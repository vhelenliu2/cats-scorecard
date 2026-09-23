---
name: hex
description: >
  Programmatically interact with the Hex data analytics platform (https://hex.tech). Create projects,
  add python and sql cells to notebooks, write queries against data connections, build
  stakeholder-facing dashboards, and hand off dashboard and app builds to the Hex agent.
allowed-tools: Bash(hex:*) Bash(jq:*)
metadata:
  author: hex
  version: "1.2026.07.09"
---

# Hex CLI -- Agent Skill

The `hex` CLI manages Hex projects, cells, runs, data connections, and workspace resources from the command line. Use it to automate Hex workflows, create and modify notebook cells, trigger runs, and inspect workspace state.

Hex projects include notebook (draft) and app (published) views. Users can create and modify cells in a project. **Draft notebook execution** uses `hex project run` (only `--no-cache`). **Published app runs** with input parameters, timeouts, and wait/async behavior use `hex app run`. Hex uses Python and SQL to execute code and query data connections.

Always pass `--json` when you need to parse output programmatically. JSON mode returns structured data; text mode is for human display only.

## Prerequisites

Before running any command, verify the user is authenticated:

```bash
hex auth status
```

If not logged in, prompt the user to run:

```bash
hex auth login
```

In an interactive terminal, this asks which Hex instance to log in to. When run non-interactively (e.g. by an agent, with `--json`, or without a TTY) it does **not** prompt and defaults to `app.hex.tech`. For any other instance, pass the host explicitly:

```bash
hex auth login --hostname eu.hex.tech
```

All SQL cells require a data connection (usually a data warehouse or sql database). Users should already have data connections configured. Before starting a complex workflow, query for available data connections and prompt the user to ask which one they would like to use:

```bash
hex connection list
```

If a user is using this skill in a repo that defines a warehouse or database schema, clarify if the data connection matches the desired schema. Use their local schema as context in authoring notebook cells queried against that connection.

Hex project YAML exports use the public JSON Schema at `https://static.hex.site/hex-file-schema.json`. For files named `*.hex.yaml`, schema-aware editors should discover this automatically through SchemaStore. When editing exported YAML, preserve `schemaVersion` and avoid changing generated IDs unless the user intentionally wants to create new objects on import.

## Global Flags

These flags work on every command:

| Flag               | Short | Description                                |
| ------------------ | ----- | ------------------------------------------ |
| `--json`           |       | Output as JSON (for scripting and parsing) |
| `--verbose`        | `-v`  | Show verbose output for debugging          |
| `--quiet`          | `-q`  | Suppress non-essential output              |
| `--no-color`       |       | Disable colored output                     |
| `--profile <name>` |       | Use a specific profile for this command    |

## Profile Management

Profiles can be used if the user has multiple Hex accounts or workspaces. Most users just have a single `default` profile.

```bash
# List all profiles; the active profile is marked with *
hex auth status

# See ### auth for full flags (hostname, web-hostname, token-from-env, etc.)
hex auth login [profile]
hex auth switch <profile>
hex auth logout [profile] [--delete]
hex auth rename <new_name>
```

## Command Reference

### auth

```bash
hex auth login [profile]   # Log in (optional profile name). OAuth device flow by default.
  [-H, --hostname <url>]   # Hex app/API base URL for this profile (e.g. https://app.hex.tech).
                           # If omitted in an interactive shell, prompts to choose an instance
                           # (app.hex.tech / eu.hex.tech / hc.hex.tech for HIPAA / Other);
                           # defaults to app.hex.tech otherwise.
  [-u, --update]           # Overwrite existing profile hostname / storage settings
  [--insecure-storage]     # Plain-text credential storage (not keyring)
  [--no-switch]            # Do not switch active profile after login
  [--token-from-env [VAR]] # Non-interactive: token from HEX_CLI_LOGIN_TOKEN or VAR

hex auth logout [profile] [--delete]   # Log out; --delete removes the profile from config
hex auth logout --all                 # Log out of every profile

hex auth status [profile]             # Show auth status (all profiles if name omitted)

hex auth switch <profile>             # Set the active profile

hex auth rename <new_name>            # Rename the current profile
```

### projects

```bash
# Create a project
hex project create <title> [-d <description>]

# List projects (default limit 25, supports cursor pagination)
hex project list [-n <limit>] [--after <cursor>] [--before <cursor>] \
  [--sort-by <created_at|last_edited_at|last_published_at>] [--sort-direction <asc|desc>] \
  [--status <published|draft|archived>] [--category <name>] \
  [--collection-id <uuid>] [--creator-email <email>] [--owner-email <email>] \
  [--include-archived] [--include-components] [--include-sharing] [--include-trashed]

# Get project details
hex project get <project_id>

# Open project in browser
hex project open <project_id>

# Run the draft notebook (full notebook recompute). Only SQL cache control is supported.
hex project run <project_id> [--no-cache]

# Export / import project as YAML (version defaults to draft)
hex project export <project_id> [--version <draft|version_number>] [-o <path>]
hex project import <file>
```

### app

```bash
# Run the published app (parameterized runs, wait/timeout). Not the same as `hex project run`.
hex app run <project_id> \
  [-i <key=value> ...] \
  [--input-file <path>] \
  [--no-cache] \
  [--wait | --no-wait] \
  [--timeout <duration>] \
  [--poll-interval <duration>]
```

With `--json`, the CLI waits for the run to finish by default unless `--no-wait` is passed. In plain text mode, pass `--wait` to block until completion.

### cells

```bash
# List cells in a project (default limit 25, supports cursor pagination)
hex cell list <project_id> [-n <limit>] [--after <cursor>] [--before <cursor>]

# Get a single cell
hex cell get <cell_id>

# Create a cell (-t is short for --cell-type)
hex cell create <project_id> \
  -t <code|sql|markdown> \
  -s <source> \
  [-l <label>] \
  [--data-connection-id <uuid>] \
  [--output-dataframe <name>] \
  [--after-cell-id <uuid>] \
  [--parent-cell-id <uuid>] \
  [--child-position <first|last>]

# Update a cell (source / connection only; cell type is not changed via the CLI)
hex cell update <cell_id> \
  [-s <source>] \
  [--data-connection-id <uuid>] \
  [--output-dataframe <name>]

# Delete a cell
hex cell delete <cell_id>

# Run a cell and its dependencies
hex cell run <cell_id> [--dry-run]
```

### connections

```bash
# List data connections (default limit 25, supports cursor pagination). There is no CLI filter by connection type — use `--json` and filter (e.g. `jq`) on `connection_type` if needed.
hex connection list [-n <limit>] [--after <cursor>] [--before <cursor>] \
  [--sort-by <created_at|name>] [--sort-direction <asc|desc>]

# Get connection details
hex connection get <connection_id>
```

### collections

```bash
# List collections (default limit 25, supports cursor pagination)
hex collection list [-n <limit>] [--after <cursor>] [--before <cursor>] \
  [--sort-by <name>]

# Get collection details
hex collection get <collection_id>
```

### groups

IMPORTANT: stop and ask permission from a user before making any changes to groups.

```bash
# List groups (default limit 25, supports cursor pagination)
hex group list [-n <limit>] [--after <cursor>] [--before <cursor>] \
  [--sort-by <created_at|name>] [--sort-direction <asc|desc>]

# Get group details
hex group get <group_id>

# Create a group
hex group create <name>

# Delete a group
hex group delete <group_id>
```

### users

```bash
# List users (default limit 25, supports cursor pagination)
hex user list [-n <limit>] [--after <cursor>] [--before <cursor>] \
  [--sort-by <name|email>] [--sort-direction <asc|desc>] \
  [--group-id <uuid>]

# Get user details (by ID or email)
hex user get <user_id_or_email>
```

### suggestions

Suggestions are automatically generated proposed context changes that can include updates to guides, workspace context, data warehouse descriptions, or endorsements to improve agent performance in Hex. Agents and users can review these proposed changes, apply them in their preferred tool of choice, and then mark the suggestion as completed or dismissed.

```bash
# List suggestions (shows open suggestions only by default)
hex suggestion list [-n <limit>] [--after <cursor>] [--before <cursor>] \
  [--sort-by <created_date|evidence_count|last_source_added_date>] \
  [--sort-direction <asc|desc>] \
  [--status <open|completed|dismissed>]

# Get a suggestion's details, including associated warnings and proposed changes
hex suggestion get <suggestion_id>

# Trigger a review agent run on a suggestion to regenerate its proposed changes
# This is typically helpful in cases where existing proposed changes have gone stale
# due to existing workspace context that has changed since the review agent was last run.
hex suggestion run-review <suggestion_id>

# Mark a suggestion as completed or dismissed
hex suggestion update <suggestion_id> \
  --status <completed|dismissed> \
  [--dismiss-reason <reason>]

# Mark a proposed change as completed or dismissed
hex suggestion change update <suggestion_id> <change_id> \
  --status <completed|dismissed> \
  --update-target <file_update|data_warehouse_update> \
  [--dismiss-reason <reason>]
```

Typical workflow:

- List open suggestions using `hex suggestion list`
- Fetch details of an individual suggestion using `hex suggestion get` to inspect the associated warnings and proposed changes
- Review the proposed changes and, for each change, either apply it externally and mark it `completed`, or ignore it and mark as `dismissed`, using `hex suggestion change update`.
- After reviewing all proposed changes, you can close the suggestion by marking it as either `completed` or `dismissed` using `hex suggestion update`

### config

```bash
# Show all configuration
hex config list

# Get a config value
hex config get <key>

# Set a config value
hex config set <key> <value>

# Show config file path
hex config path
```

Config keys: `update_check`, `logging_enabled`, and `profiles` (read-only in `config get` / `config list`; use `hex auth` to change profiles).

### run

```bash
# List recent runs for a project
hex run list <project_id> [-n <limit>]

# Inspect a run (use --watch to poll until a terminal status)
hex run status <project_id> <run_id> [--watch] [--poll-interval <duration>]

# Cancel a run
hex run cancel <project_id> <run_id>
```

### threads

Threads send a prompt to the Hex agent, which plans and builds inside a project. Read "Prompting the Hex Agent" below before writing the prompt.

```bash
# Start a thread on an existing project, or have the agent create one
hex thread create <prompt> [--project <project_id> | --new-project]

# Threads run async; poll until status is IDLE (or ERROR)
hex thread get <thread_id>

# Gets messages for a given thread. Within a page, messages are chronological (oldest
# first). By default the most recent page is returned; use --before for older messages and --after for newer ones.
hex thread messages <thread_id> [-n <limit>] [--after <cursor>] [--before <cursor>]

# Iterate in the same thread with focused follow-ups
hex thread continue <thread_id> <prompt>

# List threads in the workspace (requires Manager role or higher)
hex thread list [-n <limit>] [--after <cursor>] [--before <cursor>] \
  [--source <hex|slack|mcp|public_api>] \
  [--user-id <id>] \
  [--type <threads|notebook|semantic_authoring>] \
  [--roles <admin,manager,editor,explorer,member,guest>] \
  [--warnings <data_limitation,user_doubt,missing_context,other>] \
  [--topic-ids <id1,id2>] \
  [--has-feedback <true|false>] \
  [--num-days <n>]
```

`--roles`, `--warnings`, and `--topic-ids` accept comma-separated values. `--has-feedback true` returns only threads with feedback, `false` only threads without. `--num-days` filters to threads created within the last N days.

`thread create` and `thread continue` require the headless agent threads feature to be enabled for the workspace; if they are missing from `hex thread --help`, the feature is not available yet.

### Other commands

`hex guide` and `hex install` are available for specialized workflows. Use `hex help` or `hex <command> --help` for the authoritative flag list.

## Prompting the Hex Agent

`hex thread` is an agent-to-agent handoff: the Hex agent is a specialist, not a code generator. It plans the app, writes the cells, and enforces Hex's house style (or the organization's styles specified in design.md Org Guide) for charts, layout, formatting, and more.

Your job in the prompt is to scope the app. The Hex agent's job is to design and build it. Over-specified prompts produce worse apps.

### Include — the agent cannot infer these

- **The user's request, in their own words** — quote it rather than translating it into a spec of your own.
- **Audience and the business question** the app answers ("for the customer success team: is our refund rate trending up?").
- **Hard constraints only**: a mandated brand color (e.g. "Read the design.md Org Guide for brand colors"), a required filter, cells it must not touch.

Optional – these are helpful if you already know them:

- **The metrics and breakdowns that matter**, roughly in priority order.
- **Data context**: which cells/dataframes feed the app, and any column semantics the agent could get wrong ("rate columns are fractions — format as percents, do not multiply by 100").

### Leave to the Hex agent — it should own these decisions

- Chart styling: colors and series color maps, heights, axis titles, gridlines, legend placement, line smoothing, data labels.
- Chart types, unless the type is itself a requirement. Describe the comparison ("monthly trend", "countries ranked by rate") and let the agent pick the encoding.
- Cell-by-cell construction steps and ordering. Describe the finished app, not the build sequence ("STEP 1… STEP 2…").
- Markdown scaffolding. Hand over the narrative; the agent writes the headers and copy, unless the user already knows the exact story to tell.

A rule of thumb: if the user said it, include it. If you inferred it, leave it out.

### Avoid the one-giant-prompt failure mode

A scoped app description one-shots well. A 60-line spec with per-chart styling does not: requirements get silently dropped when too many are packed into one prompt. If the user has many precise requirements, send the scoped build first, review, then apply them as `hex thread continue` follow-ups, one concern per message.

### Put durable preferences in guides, not prompts

If the user or their org has standing dashboard preferences, do not restate them in every prompt. Put them in a workspace guide, so every agent run inherits them — including iterations the user makes later inside Hex, where your prompt is no longer in the loop. For specific design guidance (brand palette, typography, chart conventions), suggest a `design.md` guide.

You can push guides from the CLI: `hex guide preview design.md` returns a preview link and a preview_id, and `hex guide publish <preview_id>` deploys it. Published guides apply to the whole workspace — get the user's confirmation before publishing.

### Example

Over-determined (fights the agent, gets dropped):

> STEP 3 — add a DUAL-AXIS chart: left Y total_orders as BARS colored #D9D4CF, right Y refund_rate as LINE colored #3A6EA5, smooth with visible points, remove both Y-axis titles, legend bottom-center, horizontal gridlines #88888826 only, height 300px…

Scoped (the agent owns the design):

> Build a single-page dashboard for the customer success team answering: is our refund rate trending up? At a minimum, include the latest month with MoM change (refund rate, refunded orders, total orders), then the monthly refund rate trend against order volume as the hero, then one section per breakdown. Call out the categories and sales channels with the highest refund rates. Include helpful filters.

## Workflow Examples

IMPORTANT: always open the project in a user's browser when making changes to cells:

```bash
# Opens the project in the default browser (needed for interactive review; cell execution uses the API from this CLI)
hex project open "$PROJECT_ID"
```

### Create a project and add cells

```bash
# List projects to find the target
PROJECT_ID=$(hex project list --json | jq -r '.projects[0].id')

# Create a Python code cell
hex cell create "$PROJECT_ID" -t code -s "import pandas as pd
df = pd.read_csv('data.csv')
df.head()"

# Create a SQL cell after the first one
FIRST_CELL=$(hex cell list "$PROJECT_ID" --json | jq -r '.cells[0].id')
hex cell create "$PROJECT_ID" -t sql -s "SELECT * FROM my_table LIMIT 10" \
  --after-cell-id "$FIRST_CELL" --data-connection-id "$DATA_CONNECTION_ID"

# Verify cells were created
hex cell list "$PROJECT_ID"
```

### Discover data connections and create SQL cells

```bash
# List available connections
hex connection list --json

# Ask the user which connection to use, then create a SQL cell with it
CONNECTION_ID="<selected-connection-id>"
hex cell create "$PROJECT_ID" -t sql \
  -s "SELECT count(*) FROM users" \
  --data-connection-id "$CONNECTION_ID" \
  --output-dataframe "user_count"

# Run the cell
CELL_ID=$(hex cell list "$PROJECT_ID" --json | jq -r '.cells[-1].id')
hex cell run "$CELL_ID"
```

### Open, update, and run

```bash
# Get project details
hex project get "$PROJECT_ID" --json

# Open in browser for the user to review
hex project open "$PROJECT_ID"

# List cells and update one
CELLS=$(hex cell list "$PROJECT_ID" --json)
CELL_ID=$(echo "$CELLS" | jq -r '.cells[0].id')
hex cell update "$CELL_ID" -s "print('updated code')"

# Run the updated cell
hex cell run "$CELL_ID"
```

### Hand off a dashboard build to the Hex agent

```bash
# Prerequisite: project exists with QA'd SQL cells already pushed and run
PROJECT_ID="<project with prepared query cells>"

# Send one scoped prompt (see "Prompting the Hex Agent" above for the shape)
THREAD_ID=$(hex thread create "Build a single-page dashboard for the customer success team answering: is our refund rate trending up? ..." \
  --project "$PROJECT_ID" --json | jq -r '.thread_id')

# Poll until the agent finishes (status IDLE), then open for review
hex thread get "$THREAD_ID" --json
hex project open "$PROJECT_ID"

# Iterate with focused follow-ups — one concern per message
hex thread continue "$THREAD_ID" "Show order volume behind the refund rate trend in the hero chart."
```

### Run app with parameters and monitor

```bash
# Trigger a published app run with input parameters (not supported on `hex project run`)
hex app run "$PROJECT_ID" \
  -i start_date=2024-01-01 \
  -i end_date=2024-12-31 \
  -i threshold=0.95 \
  --timeout 30m

# Or run async and monitor separately
hex app run "$PROJECT_ID" -i region=us-east-1 --no-wait --json
# Returns: {"run_id": "...", "project_id": "...", "status": "PENDING", "run_url": "..."}

RUN_ID="<run_id from above>"
hex run status "$PROJECT_ID" "$RUN_ID" --watch
```

### Workspace management

```bash
# List users and groups (JSON output includes pagination cursors)
hex user list --json
hex group list --json

# Create a new group
hex group create "Data Engineering"
```

### Troubleshooting a failed run

```bash
# Check run status
hex run status "$PROJECT_ID" "$RUN_ID" --json
# Look at the "status" field: COMPLETED, ERRORED, KILLED, UNABLE_TO_ALLOCATE_KERNEL

# If a run is stuck, cancel and retry
hex run cancel "$PROJECT_ID" "$RUN_ID"
hex project run "$PROJECT_ID" --no-cache
```
