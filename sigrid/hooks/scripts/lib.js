const fs = require("fs");
const path = require("path");

const SUPPORTED_EXT_REGEX = /\.(java|py|c|h|cc|cpp|cxx|hpp|hxx|cs|js|jsx|mjs|cjs|ts|tsx|kt|kts|p|w|cls|i|php)$/i;
const TEST_PATH_REGEX = /(^|[\\/])(tests?|__tests__|spec|specs)[\\/]|(^|[\\/])test_[^\\/]*$|_test\.[^\\/]*$|\.test\.[^\\/]*$|_spec\.[^\\/]*$|\.spec\.[^\\/]*$/i;

function hooksEnabled() {
  return process.env.CLAUDE_PLUGIN_OPTION_ENABLE_AUTO_GUARDRAILS_HOOK !== "false";
}

function isRelevantFile(filePath) {
  if (!filePath) return false;
  if (!SUPPORTED_EXT_REGEX.test(filePath)) return false;
  if (TEST_PATH_REGEX.test(filePath)) return false;
  if (!isUnderProjectDir(filePath)) return false;
  return true;
}

function isUnderProjectDir(filePath) {
  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const relative = path.relative(path.resolve(projectDir), path.resolve(filePath));
  return relative !== "" && !relative.startsWith("..") && !path.isAbsolute(relative);
}

function markerPath() {
  return path.join(process.env.CLAUDE_PROJECT_DIR || process.cwd(), ".claude", "sigrid-turn-edited-files.txt");
}

function readStdin() {
  try {
    return fs.readFileSync(0, "utf8");
  } catch (err) {
    process.stderr.write(`sigrid guardrails hook: failed to read stdin (${err.code || err.message}) — skipping.\n`);
    return "";
  }
}

function writeStdout(obj) {
  fs.writeSync(1, JSON.stringify(obj) + "\n");
}

module.exports = { hooksEnabled, isRelevantFile, markerPath, readStdin, writeStdout };
