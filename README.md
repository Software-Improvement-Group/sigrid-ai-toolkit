# Sigrid AI Toolkit

A Claude Code plugin marketplace for Sigrid integrations ([documentation](https://docs.sigrid-says.com/integrations/integration-sigrid-mcp.html)).

Sigrid MCP integrations can be used to leverage Sigrid's capabilities from AI Coding Assistants, Agents and other MCP-based LLM tools.

- *Guardrail agents*: Leverage Sigrid's code analysis to prevent AI Coding Assistants from introducing security and other quality issues
- *Auto-fix agents*: Use data from Sigrid to let AI Coding Agents auto-fix and improve existing quality issues at scale

## Plugins

| Plugin | Description                                                                 |
|--------|-----------------------------------------------------------------------------|
| `sigrid` | Autoconfigures the Sigrid MCP server for guardrail and auto-fix agents |
| `sigrid-experimental` | Experimental skills for auto-fix agents                          |

## Prerequisites

- [Claude Code](https://claude.ai/code)
- A Sigrid API token ([sigrid-says.com](https://sigrid-says.com))

## Install
   
1. Install the Sigrid plugin marketplace
    ```
    /plugin marketplace add Software-Improvement-Group/sigrid-ai-toolkit
    ```

2. Install a plugin
    ```
    /plugin install sigrid@sigrid-ai-toolkit
    ```
    You'll be prompted for your Sigrid API token on first use. The token is stored securely in your system keychain.

3. Enable auto-update (recommended)

### How to: Enable auto-update

We regularly add improvements and new features. To ensure you get these updates automatically:

- `/plugin` to enter the plugin overview
- Navigate to `Marketplaces`
- Navigate to `sigrid-ai-toolkit` and press enter to select
- Navigate to `Enable auto-update` and press enter to enable

Claude Code will now automatically update the Sigrid plugin for you.

### Troubleshooting: I did not get prompted for the Sigrid token

This may happen due to a bug in at least Claude Code 2.1.84. Enter the token as follows:

- `/plugin` to enter the plugin overview
- Navigate to `Installed`
- Navigate to `sigrid` and press enter to select
- Navigate to `Configure options`
- Enter your Sigrid token and press enter
- `/reload-plugins` for changes to take effect

## Usage

See the [Sigrid MCP documentation](https://docs.sigrid-says.com/integrations/integration-sigrid-mcp.html#using-sigrid-quality-gates-with-ai-coding-agents) for usage instructions.

## Experimental skills

The `sigrid-experimental` plugin contains skills for auto-fix agents.

```
/plugin install sigrid-experimental@sigrid-ai-toolkit
```

These skills are under active development and will change. We recommend browsing the individual skills in [`sigrid-experimental/skills/`](sigrid-experimental/skills/), reading their READMEs, and adapting them to your own workflow.

| Skill | What it does |
|-------|--------------|
| `sigrid-diagnose` | Identifies your weakest maintainability property and surfaces high-leverage refactoring candidates |
| `sigrid-improve` | Executes refactoring candidates with guardrail verification |
| `sigrid-ci-feedback` | Runs Sigrid CI locally and returns structured quality feedback |
| `fix-osh-risk` | Remediates open source health findings — creates merge requests or researched issues |
