#!/usr/bin/env bash
# Dev Container: register Salesforce CA from qbrix/certs and align Node / Claude Code for bind-mounted ~/.claude (SSO + tokens).
# Run from container_poststart.sh (typically as root). Idempotent where possible.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CERT_SRC="${WORKSPACE_ROOT}/qbrix/certs/salesforce-ca-bundle.pem"
CERT_DEST="/usr/local/share/ca-certificates/salesforce-ca-bundle.crt"
CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
PROFILE_NODE_CA="/etc/profile.d/qbrix-node-extra-ca.sh"
SETTINGS="${HOME}/.claude/settings.json"
# PEM inside the container workspace — stable path for editors and Node tooling
CONTAINER_CERT_PEM="$CERT_SRC"

ensure_settings_node_ca() {
  [[ -f "$SETTINGS" ]] || return 0
  python3 - "$SETTINGS" "$CONTAINER_CERT_PEM" <<'PY'
import json
import os
import sys

settings_path = sys.argv[1]
pem_path = sys.argv[2]

try:
    with open(settings_path, encoding="utf-8") as f:
        data = json.load(f)
except (OSError, json.JSONDecodeError):
    sys.exit(0)

env = data.setdefault("env", {})
current = env.get("NODE_EXTRA_CA_CERTS", "")
if current and isinstance(current, str) and os.path.isfile(current):
    sys.exit(0)

env["NODE_EXTRA_CA_CERTS"] = pem_path
with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
}

write_local_bin_path() {
  local line='export PATH="$HOME/.local/bin:$PATH"'
  echo "$line" > /etc/profile.d/qbrix-local-bin.sh
  chmod +x /etc/profile.d/qbrix-local-bin.sh
}

# ── 1. Install CA into OS trust store ─────────────────────────────────────────
if [[ ! -f "$CERT_SRC" ]]; then
  echo "ERROR: Salesforce CA bundle not found at ${CERT_SRC}" >&2
  exit 1
fi

if ! cmp -s "$CERT_SRC" "$CERT_DEST" 2>/dev/null; then
  echo "--> Installing Salesforce CA cert into OS trust store..."
  cp "$CERT_SRC" "$CERT_DEST"
  update-ca-certificates
else
  echo "--> OS trust store: Salesforce CA already up to date, skipping."
fi

# ── 2. NODE_EXTRA_CA_CERTS for new shells (full system bundle) ───────────────
if [[ ! -f "$PROFILE_NODE_CA" ]]; then
  echo "--> Writing NODE_EXTRA_CA_CERTS to ${PROFILE_NODE_CA}..."
  echo "export NODE_EXTRA_CA_CERTS=${CA_BUNDLE}" >"$PROFILE_NODE_CA"
  chmod +x "$PROFILE_NODE_CA"
else
  echo "--> ${PROFILE_NODE_CA} already exists, skipping."
fi

export NODE_EXTRA_CA_CERTS="${CA_BUNDLE}"

# ── 3. Mounted ~/.claude: fix Mac-only or missing NODE_EXTRA_CA_CERTS ─────────
if [[ -f "$SETTINGS" ]]; then
  echo "--> Ensuring NODE_EXTRA_CA_CERTS in ${SETTINGS} points at container path..."
  ensure_settings_node_ca
fi

# ── 4. Claude Code binary + SSO / token paths ─────────────────────────────────
SKIP_TO_DONE=0
if [[ -f "$SETTINGS" ]] && grep -q "ANTHROPIC_AUTH_TOKEN" "$SETTINGS" 2>/dev/null; then
  if ! command -v claude &>/dev/null && [[ ! -f "$HOME/.local/bin/claude" ]]; then
    echo "--> Installing Claude Code binary (auth token present in settings; skipping full SSO installer)..."
    export NODE_EXTRA_CA_CERTS="${CONTAINER_CERT_PEM}"
    curl -fsSL https://claude.ai/install.sh | bash || true
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "--> Claude Code binary already present, skipping public installer."
  fi
  ensure_settings_node_ca
  write_local_bin_path
  if command -v claude &>/dev/null || [[ -f "$HOME/.local/bin/claude" ]]; then
    echo "--> Claude Code ready (token in ~/.claude/settings.json)."
    SKIP_TO_DONE=1
  else
    echo "--> Claude binary install failed; will try Salesforce SSO installer below." >&2
    SKIP_TO_DONE=0
  fi
fi

if [[ "${SKIP_TO_DONE}" != "1" ]]; then
  echo "--> Installing Claude Code via Salesforce SSO installer (or refreshing binary)..."
  export NODE_EXTRA_CA_CERTS="${CONTAINER_CERT_PEM}"
  curl -fsSL https://plugins.codegen.salesforceresearch.ai/claude/install.sh | bash || true
  ensure_settings_node_ca
  write_local_bin_path
  export PATH="$HOME/.local/bin:$PATH"
  if command -v claude &>/dev/null || [[ -f "$HOME/.local/bin/claude" ]]; then
    echo "--> Claude Code installed; use SSO flow if prompted on first run."
  else
    echo "--> Warning: Claude CLI not found after installers; check network and ~/.claude mount." >&2
  fi
fi

echo "--> CA + Claude environment bootstrap finished."
