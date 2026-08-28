#!/usr/bin/env node
// PostToolUse hook (Edit|Write|MultiEdit): records production-code files
// touched this turn, for the paired Stop hook to act on once per turn.
const fs = require("fs");
const path = require("path");
const { hooksEnabled, isRelevantFile, markerPath, readStdin } = require("./lib.js");

function parseFilePath(raw) {
  let input;
  try {
    input = JSON.parse(raw || "{}");
  } catch {
    input = {};
  }
  return input.tool_input && input.tool_input.file_path;
}

function recordFile(filePath) {
  const marker = markerPath();
  fs.mkdirSync(path.dirname(marker), { recursive: true });
  fs.appendFileSync(marker, filePath + "\n");
}

function main() {
  if (!hooksEnabled()) return;

  const filePath = parseFilePath(readStdin());
  if (isRelevantFile(filePath)) recordFile(filePath);
}

main();
