# Agentic FP&A Analytics — Google ADK Agent Blueprint

[![Google ADK](https://img.shields.io/badge/Google%20ADK-agent-4285F4)](#)
[![Gemini](https://img.shields.io/badge/Gemini-Vertex%20AI-8E75B2)](#)
[![BigQuery](https://img.shields.io/badge/BigQuery-guarded%20SQL-669DF6)](#)
[![Next.js](https://img.shields.io/badge/Next.js-chat%20frontend-black)](#)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#)

> Part of the [technical project portfolio](https://github.com/daetan999/technical_resume). Supporting material: [value-engineering playbook](https://github.com/daetan999/technical_resume/blob/main/docs/value-engineering.md).

## Overview

This repository is a sanitized blueprint of a Google ADK agent for natural-language finance and operational analysis over governed BigQuery data.

The application supports questions across P&L measures, budget variance, occupancy, ADR, RevPAR, and property performance. A Next.js interface communicates with an ADK API server, while every warehouse query passes through one guarded SQL tool before reaching approved BigQuery tables.

The model plans and narrates. SQL calculates the numbers. The warehouse is never exposed directly to the model.

## Public-Portfolio Boundary

- Project IDs, datasets, tables, columns, property names, and codes are placeholders.
- Sample data and numeric examples are synthetic.
- Proprietary prompts, integrations, credentials, and internal endpoints are excluded.
- Current development implementation and proposed production deployment are labelled separately.
- Representative code preserves validation, control, and interface patterns without publishing production logic.

## System Topology

![Agent topology](docs/assets/agent-topology.svg)

The request path consists of:

1. Next.js chat interface and server-side API route
2. Google ADK API server and session state
3. Gemini planning and tool invocation
4. One guarded SQL execution path
5. Approved BigQuery views and reference tables
6. Structured answer and chart output

## Request Lifecycle

![Agent request lifecycle](docs/assets/request-lifecycle.svg)

A typical question uses multiple controlled steps:

1. Resolve the requested property against an approved master table.
2. Retrieve the source-specific identifier required by finance or property-management data.
3. Generate a fact query using the resolved identifier as a filter.
4. Validate and execute the query through the guarded tool.
5. Return rows and raw KPI components to the agent.
6. Produce a grounded answer and declarative chart specification.

## Guarded SQL Execution

All queries pass through the same validation pipeline:

| Control | Implementation |
|---|---|
| Statement restriction | Exactly one SQL statement and `SELECT` only |
| Table access | Frozen allowlist of approved BigQuery objects |
| Lookup discipline | Restricted metadata queries for property resolution |
| Cost control | Per-query `MAX_BYTES_BILLED` cap |
| Result volume | Row limits injected for unrestricted detail queries |
| KPI semantics | Warnings for non-additive rates such as ADR, RevPAR, and occupancy |
| Data quality | Impossible outputs are surfaced with raw components instead of silently corrected |

## Multi-System Property Resolution

Finance, asset-management, and property-management systems can use different identifiers for the same asset. The agent therefore avoids joining alias-rich master tables directly to facts.

- **Step 1:** resolve all approved identifiers from the relevant master.
- **Step 1b:** resolve the separate property-management code when operational metrics are requested.
- **Step 2:** query the fact table using the source-appropriate identifier as a literal filter.

This pattern prevents duplicate-row inflation, incorrect source selection, and zero-row answers caused by code-system mismatches.

## Current and Target Deployment

![Deployment view](docs/assets/deployment-view.svg)

### Current development implementation

- ADK API server in a development environment
- Next.js development frontend
- Read-only BigQuery access through application credentials
- Single guarded SQL tool shared across query families

### Target production design

- Managed ADK or agent hosting
- Cloud Run frontend
- Enterprise authentication and authorization
- Dedicated least-privilege service identity
- Central monitoring and evaluation harness

The target state is an architecture design and is not represented as already deployed.

## Development Lessons Converted into Controls

| Failure class | Structural response |
|---|---|
| Alias-rich joins duplicated room counts | Two-step property resolution; master-to-fact joins avoided |
| Reservation expansion exceeded the byte cap | Date-filter pushdown before expansion |
| Finance identifiers were used against operational tables | Source-specific code resolution |
| Rate measures were summed | Additive and non-additive measure semantics enforced |
| Operational questions fell back to finance data | Source-selection rules and approved operational tables |
| Duplicate reservations produced impossible occupancy | Deduplication before stay-night expansion |
| Genuine source gaps still produced impossible values | Sanity gate reports the finding with raw components |

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
app/agent.py          Root agent definition and tool wiring
app/bq_tool.py        Guarded SQL validation and execution structure
app/config.py         Approved tables, measure semantics, and calendar rules
frontend/             Next.js chat interface and chart renderer
data/                 Synthetic property-master examples
docs/                 Architecture diagrams and lessons-learned log
```

## Extension Paths

- Managed agent deployment
- Planner and executor separation for larger query families
- Shared semantic layer for BI and agent use
- Regression evaluation for groundedness, source selection, and KPI correctness

## License

Released under the MIT License.
