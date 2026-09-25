const fs = require("fs");

function hooksEnabled() {
  return process.env.CLAUDE_PLUGIN_OPTION_ENABLE_AUTO_GUARDRAILS_HOOK !== "false";
}

function exploreCodebaseHookEnabled() {
  return process.env.CLAUDE_PLUGIN_OPTION_ENABLE_AUTO_EXPLORE_CODEBASE_HOOK !== "false";
}

function writeStdout(obj) {
  fs.writeSync(1, JSON.stringify(obj) + "\n");
}

module.exports = { hooksEnabled, exploreCodebaseHookEnabled, writeStdout };
