---
name: explore-codebase
user-invocable: true
description: >
  Explore the codebase using the explore-codebase agent. Use when the user
  wants to understand the codebase structure, "what does this codebase look
  like architecturally", "where are the hotspots", "what are the
  dependencies", "show me the architecture", "explore this codebase", or
  "I need to understand this codebase".
---

# Explore Codebase

> **Adapting this skill.** Configure it by running `/sigrid:setup` to set your customer, system, and conventions in the profile — these survive plugin updates.

Use the `explore-codebase` agent to explore the codebase architecture. It leverages Sigrid's measured dependency graph combined with agentic file reading.

## Usage

```
/sigrid:explore-codebase
```

Trigger phrases: "explore this codebase", "what does this codebase look like architecturally",
"where are the hotspots", "what are the dependencies", "show me the architecture",
"understand the structure", "codebase architecture overview".

## What it does

The explore-codebase agent uses Sigrid MCP tools (`architecture:get_internal`,
`architecture:get_external_dependencies`) and agentic file reading to understand
the codebase structure. You can ask it questions like:

- Where is xyz used?
- How is communication organized within this/these directories?
- What are the external dependencies of a given module?

Just ask the agent to explore and it will figure out what it needs to know.
