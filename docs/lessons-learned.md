# Lessons-Learned Engineering Log

> **Public-artifact boundary:** this retrospective records the failure modes and control requirements that shaped the reference architecture. In this repository, most validator, execution, client, and sanity-gate paths are explicit blueprint stubs. Treat the controls below as design requirements and sanitized operating lessons—not as claims that the public code enforces them end to end.

The full narrative behind the README's summary table. Every figure below is a
**fictional illustration** of the real failure shape; every fix is real and
is represented as a design or configuration contract. Enforcement code is not
published unless the referenced source path implements it directly.

## 1 · JOIN explosion (data duplication)

Joining the property master to fact tables to group by region looked obvious
and was wrong: the master carries historical and alias codes, so joins
duplicated room counts and silently *deflated* ADR/RevPAR. **Fix:** strict
two-step querying — resolve codes in a standalone lookup, inject them into
fact queries as literals. The validator now rejects master-to-fact JOINs
outright.

## 2 · Scan-limit blowups

Unnesting stay dates *before* filtering forced the warehouse to explode the
property's entire reservation history, breaching the byte cap.

```sql
-- FAILED: UNNEST first, filter later — scans full history
WITH exploded AS (
  SELECT revenue, night
  FROM `<reservations view>`,
       UNNEST(GENERATE_DATE_ARRAY(arrivaldate, departuredate)) AS night
)
SELECT ... WHERE night BETWEEN @start AND @end

-- WORKING: prune rows BEFORE unnesting (date-filter pushdown)
WITH exploded AS (
  SELECT revenue, night
  FROM `<reservations view>`,
       UNNEST(GENERATE_DATE_ARRAY(arrivaldate,
              DATE_SUB(departuredate, INTERVAL 1 DAY))) AS night
  WHERE arrivaldate <= @end AND departuredate > @start
)
```

The byte cap stayed — as a backstop, not a crutch.

## 3–4 · Code-system mismatches

The finance cube, the asset-management ledger, and the PMS each use different
property codes. Using a finance code against PMS tables returned a confident
"0 rows / data not available"; combining current and historical codes with
`IN (...)` double-counted snapshots. **Fix:** per-source code resolution, and
fact queries filter on exactly one source-appropriate code.

## 5–6 · Rate semantics and currency

`SUM(ADR)` produces nonsense (a 200 ADR over 30 days "becomes" 6,000).
Measures are now classified additive vs non-additive in config; rates are
recomputed from raw components with `SAFE_DIVIDE`, and every finance answer
carries both local and group currency from a single query.

## 7 · Silent source fallback

Asked for PMS-sourced ADR + RevPAR, the agent answered with finance-cube
numbers and claimed PMS was unavailable. Root cause: two contradictory
instruction rules — and the "restrictive" one was correct, because the
reservations view genuinely has no available-rooms column. The agent resolved
the contradiction by quietly abandoning PMS. **Fix:** the three inventory
tables joined the allowlist, the contradiction was deleted, and answers must
state their source.

## 8 · The phantom code column

The instruction told the agent to use a PMS code column that **did not
exist** — a display-name column was masquerading as a code. Filtering on it
returned zero rows for every property. A diagnostic query proved the real PMS
code lives only in a separate master view. **Fix:** the phantom columns were
deleted from config, the second master view was allowlisted for metadata-only
lookups, and "Step 1b" became mandatory for PMS questions.

## 9 · Duplicate rows, impossible occupancy

First fully-PMS answer: occupancy 187% — impossible. Line-by-line comparison
against the production reporting engine found the rewritten SQL had dropped
`SELECT DISTINCT` before the `UNNEST`; exact-duplicate reservation rows were
counted twice (illustratively: 9,412 occupied nights against 5,030 available).
**Fix:** `DISTINCT` restored to match the reference engine exactly, and raw
components (revenue, occupied nights, available nights) are always returned
alongside ratios — an impossible number must be *diagnosable*.

## 10 · The honest dead end (still open)

One property still computes occupancy slightly above 100% for one month.
The investigation ruled out availability data (all nights resolved from the
primary inventory source, no gaps, no stale carry-forward) and ruled out
agent/tool bugs (identical results pasted directly into the console). The
remaining hypothesis is stay-record duplication under distinct stay ids.
**The safeguard is the point:** the sanity gate presents the raw components
and a data-quality flag instead of a confirmed KPI, which is exactly what let
this investigation happen rather than a wrong number shipping silently.

## 11 · End-to-end validation

The same pipeline proven on a second property: sane occupancy, clean
per-night availability, PMS ADR/Occ%/RevPAR all computed from approved
tables. The failure was property-specific data, not the architecture.
