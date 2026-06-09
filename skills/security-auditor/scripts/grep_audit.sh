#!/usr/bin/env bash
#
# grep_audit.sh — high-signal OWASP triage grep over a codebase.
#
# Surfaces candidate vulnerability patterns to manually confirm. This is a
# LEAD GENERATOR, not proof: every hit must be verified by reading the data
# flow (source -> sink -> sanitizer). Expect false positives.
#
# Usage:
#   ./grep_audit.sh <path>            # scan a directory or file
#   ./grep_audit.sh                   # scan current directory
#
# Exit code: 0 always (triage tool). Output grouped by OWASP category.
#
# Pure POSIX + grep. No dependencies.

set -u

TARGET="${1:-.}"

if [ ! -e "$TARGET" ]; then
  echo "error: path not found: $TARGET" >&2
  exit 2
fi

# Directories we never want to scan.
EXCLUDES='--exclude-dir=.git --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.venv --exclude-dir=dist --exclude-dir=build --exclude-dir=__pycache__ --exclude-dir=vendor'

GREP() {
  # $1 = label, $2 = extended regex
  local label="$1"; shift
  local pattern="$1"; shift
  # shellcheck disable=SC2086
  local hits
  hits=$(grep -rniE $EXCLUDES "$pattern" "$TARGET" 2>/dev/null)
  if [ -n "$hits" ]; then
    printf '\n### %s\n' "$label"
    printf '%s\n' "$hits"
  fi
}

echo "================================================================="
echo " OWASP grep triage  ->  $TARGET"
echo " Confirm every hit by reading the surrounding code. False"
echo " positives are expected. Absence of hits != absence of bugs."
echo "================================================================="

echo
echo "## A03 Injection ----------------------------------------------"
GREP "SQL string-building (concat / f-string / format into query)" \
  '(execute|query|cursor)\s*\(.*(\+|%|\.format|f"|f'\'').*'
GREP "OS command with shell=True / os.system / exec / popen" \
  '(os\.system|shell\s*=\s*true|subprocess\.(call|run|popen).*shell|child_process\.exec[^F]|`.*\$\{)'
GREP "eval / dynamic execution" \
  '\b(eval|exec)\s*\(|new Function\(|setTimeout\(\s*"'
GREP "XSS sinks (raw HTML render)" \
  'dangerouslySetInnerHTML|innerHTML\s*=|\|\s*safe|\{!!|v-html|document\.write'

echo
echo "## A02 Cryptographic Failures --------------------------------"
GREP "Weak hash / cipher" \
  '\b(md5|sha1|des|rc4|ecb)\b'
GREP "Disabled TLS verification" \
  'verify\s*=\s*false|rejectunauthorized\s*:\s*false|insecureskipverify\s*:\s*true|check_hostname\s*=\s*false'
GREP "Insecure randomness for tokens" \
  '(math\.random|random\.random|random\.randint|mt_rand)\s*\('

echo
echo "## A01/A05 Secrets & hardcoded credentials -------------------"
GREP "Hardcoded secret-like assignments" \
  '(password|passwd|secret|api[_-]?key|token|private[_-]?key|aws_secret)\s*[:=]\s*["'\''][^"'\'' ]{6,}'
GREP "AWS access key id" \
  'AKIA[0-9A-Z]{16}'
GREP "Private key block" \
  '-----BEGIN ([A-Z ]+ )?PRIVATE KEY-----'

echo
echo "## A08 Insecure Deserialization ------------------------------"
GREP "Dangerous deserializers" \
  'pickle\.loads|yaml\.load\s*\(|cPickle|marshal\.loads|ObjectInputStream|unserialize\s*\(|JSON\.parse\(.*eval'

echo
echo "## A10 SSRF --------------------------------------------------"
GREP "Outbound request with variable URL" \
  '(requests\.(get|post|put)|urllib\.request\.urlopen|httpx\.|axios\.|fetch\(|http\.get)\s*\(.*(url|req\.|request\.|params)'

echo
echo "## A05 Security Misconfiguration -----------------------------"
GREP "Debug mode / permissive CORS" \
  'debug\s*=\s*true|access-control-allow-origin.*\*|cors\(\)|allow_origins\s*=\s*\[?\s*["'\'']\*'

echo
echo "## A07 Auth / JWT --------------------------------------------"
GREP "JWT alg none / unverified decode" \
  'alg.*none|algorithms\s*=\s*\[\s*\]|verify\s*=\s*false|jwt\.decode\([^,]*\)'

echo
echo "================================================================="
echo " Triage complete. Now: trace each hit source->sink, build a PoC,"
echo " rate severity (references/severity-rubric.md), write the fix."
echo "================================================================="
exit 0
