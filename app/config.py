"""Configuration contract for the FP&A agent — sanitized blueprint.

Everything the validator enforces lives here: the table allowlist, lookup
column sets, measure semantics, and the fiscal/freshness calendar. The
instruction template injects these values, so config.py is the single
source of truth for both the guardrails and the agent's own knowledge.
"""
from __future__ import annotations

from datetime import date
import os

# --- GCP / BigQuery -----------------------------------------------------------

PROJECT_ID = os.getenv("BQ_PROJECT", "<DATA_PLATFORM_PROJECT_ID>")

# Official monthly finance / P&L answers come from this view, always.
SOURCE_TABLE = f"{PROJECT_ID}.finance_gold.vw_pnl_main"

# Property master: metadata + geography clustering. Standalone lookups only —
# JOINs to fact tables are rejected (alias codes cause row explosion).
PROPERTY_MASTER_TABLE = f"{PROJECT_ID}.operations_silver.dim_property_master"

# The PMS property code exists ONLY in this separate gold view — proven by
# diagnostics; dim_property_master has no PMS code column at all.
PMS_PROPERTY_MASTER_TABLE = f"{PROJECT_ID}.operations_gold.vw_property_master"

# PMS operational tables (daily freshness, vs the monthly finance cycle).
PMS_HISTORICAL_TABLE = f"{PROJECT_ID}.operations_gold.vw_reservations"
PMS_OTB_RESERVATIONS_TABLE = f"{PROJECT_ID}.operations_gold.vw_otb_reservations"
PMS_OTB_GROUPS_TABLE = f"{PROJECT_ID}.operations_gold.vw_otb_groups"

# Available-rooms (AAN) inventory — three source-specific silver tables, each
# with its own date/property/count columns; unioned by the availability CTE.
PMS_INVENTORY_A_TABLE = f"{PROJECT_ID}.operations_silver.fact_pms_a_room_inventory"
PMS_INVENTORY_B_TABLE = f"{PROJECT_ID}.operations_silver.fact_pms_b_room_inventory"
PMS_INVENTORY_C_TABLE = f"{PROJECT_ID}.operations_silver.fact_pms_c_room_inventory"

# The allowlist is a frozenset on purpose: membership is the security gate,
# not a naming convention.
APPROVED_TABLES = frozenset({
    SOURCE_TABLE,
    PROPERTY_MASTER_TABLE,
    PMS_PROPERTY_MASTER_TABLE,
    PMS_HISTORICAL_TABLE,
    PMS_OTB_RESERVATIONS_TABLE,
    PMS_OTB_GROUPS_TABLE,
    PMS_INVENTORY_A_TABLE,
    PMS_INVENTORY_B_TABLE,
    PMS_INVENTORY_C_TABLE,
})

# A valid finance/operations query must reference at least one fact table;
# standalone property-master lookups are the deliberate exception.
PRIMARY_FACT_TABLES = frozenset({
    SOURCE_TABLE,
    PMS_HISTORICAL_TABLE,
    PMS_OTB_RESERVATIONS_TABLE,
    PMS_OTB_GROUPS_TABLE,
})

# --- Property-master lookup columns --------------------------------------------

# Property codes are source-specific. Resolve names → codes via the master,
# then use the code matching the target source. Never assume one code system.
PROPERTY_MASTER_LOOKUP_COLUMNS = frozenset({
    "property_code_epm",
    "property_code_epm_historical",
    "property_code_am",
    "display_name",
    "property_group",
    "region", "country", "city",
    "brand", "ownership", "operator",
    "currency", "property_status", "asset_class",
})

# Allowed metadata columns on the PMS master view. `pms_property_code` is the
# ONLY field that matches `propertycode` in the PMS reservation/inventory tables.
PMS_PROPERTY_MASTER_LOOKUP_COLUMNS = frozenset({
    "property_code_epm",
    "property_code_am",
    "pms_property_code",
    "display_name",
    "currency",
})

# Fictional illustrative alias — the shape, not the data.
KNOWN_PROPERTY_ALIASES = {
    "property alpha": {
        "canonical_name": "Harborview Suites Alpha",
        "known_codes": ("XX001", "HSALP"),
        "notes": "Master may carry a current EPM code and a legacy AM code; "
                 "use the code appropriate to the target source table.",
    }
}

# --- Model / guardrails ---------------------------------------------------------

GEMINI_MODEL = os.getenv("NARRATIVE_MODEL", "gemini-flash-class")

# Hard per-query cost cap. Sized to allow daily-grain PMS queries that use the
# date-pushdown pattern; a query that needs more is a wrong query.
MAX_BYTES_BILLED = 10 * 1024 * 1024 * 1024

# Row cap injected into detail (non-aggregate) queries lacking a LIMIT.
DEFAULT_LIMIT = 1000

# --- Business calendar ----------------------------------------------------------

DEFAULT_BUDGET_VERSION = "Budget"

# Configurable fiscal year start (month number).
FISCAL_YEAR_START_MONTH = int(os.getenv("FISCAL_YEAR_START_MONTH", "10"))

# The finance cube is not fully refreshed for all properties until day N of
# the month; the previous month counts as a confirmed actual only after that.
DATA_FULL_REFRESH_DAY = int(os.getenv("DATA_FULL_REFRESH_DAY", "17"))
FIRST_CONFIRMED_DAY = DATA_FULL_REFRESH_DAY + 1

# --- Measure semantics -----------------------------------------------------------

# Additive line items may be summed across properties/periods.
ADDITIVE_MEASURES = frozenset({
    "GOP", "EBITDA", "Rooms Revenue", "F&B Revenue", "Revenue - Primary",
    "NPI", "PBIT",
})

# Rates/percentages must NEVER be summed — summing an ADR of 200 over 30 days
# yields a nonsense "6,000". Recompute from raw components instead.
NON_ADDITIVE_MEASURES = frozenset({
    "Occ%", "GOP%", "ADR", "RevPAR",
})

PERCENTAGE_MEASURES = frozenset({"Occ%", "GOP%"})


def is_additive(measure: str) -> bool:
    return measure not in NON_ADDITIVE_MEASURES


def default_aggregation(measure: str) -> str:
    return "SUM" if is_additive(measure) else "AVG"


def get_latest_fully_confirmed_actual_month(today: date | None = None) -> date:
    """First day of the latest month whose actuals are confirmed for ALL
    properties (before day FIRST_CONFIRMED_DAY, that's two months back)."""
    if today is None:
        today = date.today()
    months_back = 1 if today.day >= FIRST_CONFIRMED_DAY else 2
    month_index = (today.year * 12 + (today.month - 1)) - months_back
    year, month0 = divmod(month_index, 12)
    return date(year, month0 + 1, 1)
