#!/bin/bash
# Deployment Doctor — template for self-diagnosing Dockerized services
# Usage: ./doctor.sh          # diagnose only
#        ./doctor.sh --fix    # diagnose + auto-fix

set -uo pipefail
cd "$(dirname "$0")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
AUTO_FIX=false
[[ "${1:-}" == "--fix" ]] && AUTO_FIX=true
FIXES=0; ERRORS=0; WARNS=0

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; ((WARNS++)); }
fail() { echo -e "  ${RED}✗${NC} $1"; ((ERRORS++)); }
info() { echo -e "  ${CYAN}→${NC} $1"; }
fix()  { echo -e "  ${CYAN}🔧${NC} $1"; ((FIXES++)); }

# ── Auto-detect Docker host (Colima on macOS) ──
detect_docker_host() {
  if [ -z "${DOCKER_HOST:-}" ]; then
    local sock="$HOME/.colima/default/docker.sock"
    [ -S "$sock" ] && export DOCKER_HOST="unix://$sock"
  fi
}
detect_docker_host

# ── Sections ──
# 1. File integrity       — check required files exist
# 2. Docker daemon        — detect + context fallback + set DOCKER_OK flag
# 3. Docker images        — guard with ${DOCKER_OK:-false}
# 4. Port conflicts       — Docker-aware: ss/lsof for cross-platform
# 5. Environment variables— .env + API keys
# 6. Container status     — guard with ${DOCKER_OK:-false}
# 7. Backend health       — guard with ${DOCKER_OK:-false}
# 8. Frontend reachable   — guard with ${DOCKER_OK:-false}
# 9. Disk space           — df -h /
# 10. Summary             — exit $ERRORS

# Each Docker-dependent section wraps in:
#   if ${DOCKER_OK:-false}; then
#     ... section content ...
#   fi
# When Docker is down, sections silently skip (no empty headers).
# Port conflicts use 3-way logic:
#   Docker up + our container → ok
#   Docker up + other process → fail
#   Docker down + port busy  → warn (can't verify, may be SSH tunnel)
