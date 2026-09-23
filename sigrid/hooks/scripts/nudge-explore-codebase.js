#!/usr/bin/env node
// UserPromptSubmit hook: nudges Claude toward the explore-codebase skill
// instead of the generic Explorer subagent.
const { exploreCodebaseHookEnabled, writeStdout } = require("./lib.js");

function main() {
  if (!exploreCodebaseHookEnabled()) {
    writeStdout({ continue: true });
    return;
  }

  writeStdout({
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext:
        "Prefer sigrid:explore-codebase over Explorer subagent.",
    },
  });
}

main();
