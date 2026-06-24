# Sigrid AI Toolkit

A Claude Code plugin marketplace for Sigrid integrations ([documentation](https://docs.sigrid-says.com/integrations/integration-sigrid-mcp.html)).

Sigrid MCP integrations can be used to leverage Sigrid's capabilities from AI Coding Assistants, Agents and other MCP-based LLM tools.

- *Sigrid Guardrails MCP*: Leverage Sigrid's code analysis to safeguard AI Coding Assistants from introducing security and other quality issues
- *Sigrid Modernization Recipes MCP*: Use data from Sigrid to let AI Coding Agents perform large scale modernization tasks (coming soon)

## Plugins

| Plugin | Description |
|--------|-------------|
| `sigrid` | Autoconfigures the Sigrid MCP server for code quality guardrails |
| `sigrid-experimental` | Experimental recipes for AI-assisted modernization |

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
