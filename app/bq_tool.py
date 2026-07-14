"""run_finance_sql — the guarded SQL tool. Sanitized blueprint skeleton.

Design rule: the model never touches BigQuery directly. Every query —
including the agent's own property-master lookups — passes this pipeline.
A rejection is returned as a structured, readable error so the model can
correct itself; nothing invalid ever reaches the warehouse.
"""
from __future__ import annotations

import re

import sqlparse

from . import config


def _referenced_tables(sql_without_backticks: str) -> set[str]:
    """Extract fully-qualified table references (project.dataset.table)."""
    return set(re.findall(r"[\w-]+\.[\w]+\.[\w]+", sql_without_backticks))


def kpi_aggregation_warnings(sql: str) -> list[str]:
    """Attach warnings when a rate measure appears under SUM() — the answer
    still executes, but the model is told its aggregation is suspect."""
    raise NotImplementedError("Blueprint stub")


def _validate_property_master_only_lookup(sql: str) -> tuple[bool, str | None]:
    """Standalone master lookups are allowed for code resolution only:
    approved lookup columns, no fact tables, no JOINs. Accepts either
    property-master table (the PMS code lives in a separate view)."""
    raise NotImplementedError("Blueprint stub")


def _validate_and_prepare(generated_sql: str):
    """The gate, in order:

    1. sqlparse: exactly one statement, and it is a SELECT.
    2. Allowlist: every referenced table ∈ config.APPROVED_TABLES.
    3. Shape: references a PRIMARY_FACT_TABLE, or qualifies as a
       property-master-only lookup (rule 3 above).
    4. LIMIT: detail queries without one get config.DEFAULT_LIMIT injected.
    5. Cost: job config carries config.MAX_BYTES_BILLED — the cap is
       enforced by BigQuery itself, not by our arithmetic.

    Returns (prepared_sql, job_config) or raises a structured rejection.
    """
    raise NotImplementedError("Blueprint stub — full rule set omitted")


def run_finance_sql(user_question: str, generated_sql: str) -> dict:
    """ADK tool entrypoint.

    Returns a dict the model can reason about:
      { status, rows, row_count, warnings[], error? }

    Rows are serialized with raw components preserved (revenue, OAN, AAN)
    so downstream sanity gates — occupancy > 100% ⇒ flagged finding —
    always have the evidence they need.
    """
    raise NotImplementedError("Blueprint stub — execution path omitted")
