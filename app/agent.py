"""Root agent definition — sanitized blueprint skeleton.

One agent, one tool. The instruction is a token-templated playbook so the
model's knowledge of table ids, budget versions, and freshness rules comes
from config.py — never from prompt drift.
"""
from __future__ import annotations

from google.adk.agents import Agent

from . import config
from .bq_tool import run_finance_sql

# The production instruction template is proprietary; its structure is:
#
#   ROLE            finance/operations analyst for a hospitality portfolio
#   SOURCES         [[PNL_VIEW]] for official monthly finance answers;
#                   [[PMS_TABLES]] for daily-freshness operational metrics —
#                   always STATE which source an answer used
#   RESOLUTION      Step 1: resolve property via [[PROPERTY_MASTER]]
#                   (standalone lookup, approved columns only);
#                   Step 1b: resolve the PMS code via [[PMS_MASTER]];
#                   Step 2: inject resolved codes as WHERE literals
#   MEASURE RULES   additive vs rate semantics; SAFE_DIVIDE on raw
#                   components; dual-currency output (local + group)
#   FRESHNESS       latest confirmed actual month from config; forecast
#                   months read the [[BUDGET]] snapshot rules
#   HONESTY         impossible values (Occ% > 100) are flagged findings with
#                   raw components — never confirmed answers; empty results
#                   are stated as data gaps, never filled in
#   OUTPUT          concise narrative + chart-ready JSON spec
_INSTRUCTION_TEMPLATE = """
[Blueprint stub — proprietary playbook omitted. Structure documented above.]
"""


def _build_instruction() -> str:
    replacements = {
        "[[PNL_VIEW]]": config.SOURCE_TABLE,
        "[[PROPERTY_MASTER]]": config.PROPERTY_MASTER_TABLE,
        "[[PMS_MASTER]]": config.PMS_PROPERTY_MASTER_TABLE,
        "[[BUDGET]]": config.DEFAULT_BUDGET_VERSION,
    }
    instruction = _INSTRUCTION_TEMPLATE
    for token, value in replacements.items():
        instruction = instruction.replace(token, value)
    return instruction.strip()


root_agent = Agent(
    name="fpa_finance_agent",
    model=config.GEMINI_MODEL,
    description=(
        "Answers portfolio finance (P&L) and operational (PMS) questions by "
        "generating guarded BigQuery SQL against approved tables, with "
        "freshness, forecast-snapshot, KPI-aggregation, and dynamic "
        "property-code safeguards."
    ),
    instruction=_build_instruction(),
    tools=[run_finance_sql],
)
