# Agentic FP&A Analytics — Governed Application Blueprint

[Control contracts](app/config.py) · [Lessons learned](docs/lessons-learned.md) · [Portfolio](https://github.com/daetan999/technical_resume)

## Overview

This repository is a sanitized reference design for a Google ADK agent that performs natural-language finance and operational analysis over governed BigQuery data.

The design covers questions across P&L measures, budget variance, occupancy, ADR, RevPAR, and property performance. It defines a Next.js-to-ADK request boundary and a single guarded SQL path to approved BigQuery tables.

The governing principle is simple: the model plans and narrates; SQL calculates the numbers. The model cannot issue direct warehouse requests, although approved query results would still enter model context for synthesis.

## Portfolio Role

This is the governed enterprise-application layer of the [Enterprise AI Infrastructure Portfolio](https://github.com/daetan999/technical_resume). It demonstrates how application controls, warehouse semantics, cost limits, data quality, and identity boundaries constrain an agentic workflow before infrastructure and commercial recommendations can be trusted.

## Published Artifact Status

This repository is a **control blueprint**, not a runnable end-to-end application.

| Available here | Not implemented in the public tree |
|---|---|
| Approved-table, KPI, calendar, and lookup contracts | BigQuery execution and structural SQL enforcement |
| ADK agent/tool interface shapes | Complete agent instruction and runnable ADK workflow |
| Server-side Next.js proxy boundary | Page, chart renderer, package manifest, and working client response parser |
| Synthetic property-master example and architecture diagrams | Authentication, session ownership, deployment, and evaluation harness |

Source paths marked as blueprint stubs are intentionally non-runnable. The controls below are design requirements unless a linked public function implements them directly.

## Public-Portfolio Boundary

- Project IDs, datasets, tables, columns, property names, and codes are placeholders.
- Sample data and numeric examples are synthetic.
- Proprietary prompts, integrations, credentials, and internal endpoints are excluded.
- Current development implementation and proposed production deployment are labelled separately.
- Representative code preserves validation, control, and interface patterns without publishing production logic.

## Reference System Topology

![Agent topology](docs/assets/agent-topology.svg)

The target request path consists of:

1. Next.js chat interface and server-side API route
2. Google ADK API server and session state
3. Gemini planning and tool invocation
4. One guarded SQL execution path
5. Approved BigQuery views and reference tables
6. Structured answer and chart output

## Request Lifecycle

![Agent request lifecycle](docs/assets/request-lifecycle.svg)

A complete implementation would use these controlled steps:

1. Resolve the requested property against an approved master table.
2. Retrieve the source-specific identifier required by finance or property-management data.
3. Generate a fact query using the resolved identifier as a filter.
4. Validate and execute the query through the guarded tool.
5. Return rows and raw KPI components to the agent.
6. Produce a grounded answer and declarative chart specification.

## Guarded SQL Execution

The public contracts require every query to pass through one validation pipeline. Enforcement is not implemented in this repository.

| Control contract | Required behavior | Public status |
|---|---|---|
| Statement restriction | Exactly one SQL statement and `SELECT` only | Documented; validator stub |
| Table access | Frozen allowlist of approved BigQuery objects | Allowlist declared; enforcement stub |
| Lookup discipline | Restricted metadata queries for property resolution | Rules declared; enforcement stub |
| Cost control | Per-query `MAX_BYTES_BILLED` cap | Constant declared; job configuration omitted |
| Result volume | Row limits injected for unrestricted detail queries | Documented; injection omitted |
| KPI semantics | Warn on non-additive rates such as ADR, RevPAR, and occupancy | Measure sets declared; warnings omitted |
| Data quality | Surface impossible outputs with raw components | Documented; sanity gate omitted |

## Multi-System Property Resolution

Finance, asset-management, and property-management systems can use different identifiers for the same asset. The agent therefore avoids joining alias-rich master tables directly to facts.

- **Step 1:** resolve all approved identifiers from the relevant master.
- **Step 1b:** resolve the separate property-management code when operational metrics are requested.
- **Step 2:** query the fact table using the source-appropriate identifier as a literal filter.

This pattern prevents duplicate-row inflation, incorrect source selection, and zero-row answers caused by code-system mismatches.

## Public Artifact and Target Deployment

![Deployment view](docs/assets/deployment-view.svg)

### Published public artifact

- Python configuration and interface skeletons
- Partial Next.js server-side proxy and client boundary
- Synthetic property-master data
- Architecture and request-lifecycle documentation

### Target production design

- Managed ADK or agent hosting
- Cloud Run frontend
- Enterprise authentication and authorization
- Dedicated least-privilege service identity
- Central monitoring and evaluation harness

The target state is an architecture design and is not represented as already deployed. The public tree also does not constitute a runnable development deployment.

## Development Lessons Converted into Controls

| Failure class | Blueprint response |
|---|---|
| Alias-rich joins duplicate room counts | Require two-step property resolution and avoid master-to-fact joins |
| Reservation expansion exceeds the byte cap | Require date-filter pushdown before expansion |
| Finance identifiers are used against operational tables | Resolve source-specific codes first |
| Rate measures are summed | Separate additive and non-additive measure semantics |
| Operational questions fall back to finance data | Require source-selection rules and approved operational tables |
| Duplicate reservations produce impossible occupancy | Require deduplication before stay-night expansion |
| Genuine source gaps still produce impossible values | Return raw components and data-quality flags |

The longer engineering log is available in [`docs/lessons-learned.md`](docs/lessons-learned.md).

## Technology Stack

| Layer | Technology |
|---|---|
| Agent framework | Google ADK |
| Model | Gemini on Vertex AI |
| Warehouse | BigQuery |
| SQL parsing | sqlparse |
| Frontend | Next.js |
| API | ADK API server |
| Cost guardrail | `MAX_BYTES_BILLED` |

## Repository Map

```text
app/agent.py                         Root-agent interface and placeholder instruction
app/bq_tool.py                       Guarded SQL interface with explicit execution stubs
app/config.py                        Approved tables, measure semantics, and calendar rules
frontend/src/app/api/chat/route.ts   Development proxy boundary
frontend/src/lib/adkClient.ts        Partial ADK session/response client
data/                                Synthetic property-master example
docs/                                Reference diagrams and lessons-learned log
```

## Repository Verification

The published Python syntax, synthetic fixture, and SVG assets can be checked without cloud credentials:

```bash
python -m compileall app
python - <<'PY'
from pathlib import Path
import csv
import xml.etree.ElementTree as ET

rows = list(csv.DictReader(Path("data/sample_property_master.csv").open()))
assert rows and all(row["property_name"] for row in rows)
for diagram in Path("docs/assets").glob("*.svg"):
    ET.parse(diagram)
print("Published blueprint assets verified")
PY
```

These checks do not validate ADK, Next.js, BigQuery, authentication, or the guarded execution path because the required implementations and manifests are not present.

## Limitations

- The public repository cannot currently be installed or run as an application.
- SQL parsing comments and regex extraction are not sufficient security boundaries for BigQuery.
- Client-supplied user and session identifiers require authentication, ownership checks, validation, encoding, timeouts, and safe error handling in a real deployment.
- The reference design requires executable guardrail tests before any finance or operational use.

## Extension Paths

- Managed agent deployment
- Planner and executor separation for larger query families
- Shared semantic layer for BI and agent use
- Regression evaluation for groundedness, source selection, and KPI correctness

## License

Released under the MIT License.

---

[Part of the Enterprise AI Infrastructure Portfolio](https://github.com/daetan999/technical_resume)
