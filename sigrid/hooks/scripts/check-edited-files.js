#!/usr/bin/env node
// Stop hook: once per turn, nudges the main thread to run the guardrails
// check on any production-code files it touched, then clears the marker
// so the nudge fires exactly once (no re-block on the next turn).
const fs = require("fs");
const { hooksEnabled, markerPath, writeStdout } = require("./lib.js");

function readMarkedFiles(marker) {
  let contents;
  try {
    contents = fs.readFileSync(marker, "utf8");
  } catch {
    contents = "";
  }
  return [...new Set(contents.split("\n").map((line) => line.trim()).filter(Boolean))].sort();
}

function buildBlockReason(files) {
  return `Files changed this turn: ${files.join(",")}. If any are production code, call the Sigrid guardrails_quality_check MCP tool on them now before finishing.`;
}

function main() {
  if (!hooksEnabled()) {
    writeStdout({ continue: true });
    return;
  }

  const marker = markerPath();
  const files = readMarkedFiles(marker);
  if (files.length === 0) {
    writeStdout({ continue: true });
    return;
  }

  fs.unlinkSync(marker);
  writeStdout({ decision: "block", reason: buildBlockReason(files) });
}

main();
