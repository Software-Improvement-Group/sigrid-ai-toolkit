# Setup

> **Run this first.** Every other Sigrid skill reads the profile this one writes.

Interviews you for your Sigrid customer/system, git-host conventions, and any behavior preferences,
then writes them to a **profile** the other skills read. Re-run it any time to add a system or change
conventions.

## What it does

1. Reads the plugin's profile template for the current field list
2. Interviews you (in small batches) for your Sigrid system(s), git-host conventions, and preferences
3. Writes the filled-in profile to the plugin's persistent data directory

## Where the profile lives

```
${CLAUDE_PLUGIN_DATA}/CLAUDE.md
```

i.e. `~/.claude/plugins/data/sigrid-sigrid-ai-toolkit/CLAUDE.md`. This is the officially supported
per-plugin data location — outside the version-scoped `cache/`, so your profile **survives
`/plugin update`**. You can also edit the file by hand.

## Multiple systems

A profile can hold several Sigrid systems (one per codebase). Each system records a `Repo` key
(`host/owner/repo`) so skills auto-select the right one by matching the current repository's git
remote. A single-system profile can omit the key.

## Usage

```
/sigrid:setup
```

Trigger phrases: "set up Sigrid", "configure Sigrid", "Sigrid onboarding", or
"my Sigrid customer/system is ...".

## Note

This skill only writes the profile — it never touches project code, calls the Sigrid MCP, or stores
your API token. (The MCP token lives in the OS keychain via plugin config; `change-feedback` uses a
separate `SIGRID_CI_TOKEN` environment variable.)
