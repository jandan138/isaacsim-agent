#!/usr/bin/env bash
set -euo pipefail

resolve_isaac_root() {
  if [[ -n "${ISAAC_SIM_ROOT:-}" && -x "${ISAAC_SIM_ROOT}/python.sh" ]]; then
    echo "${ISAAC_SIM_ROOT}"
    return 0
  fi

  if [[ -x "/isaac-sim/python.sh" ]]; then
    echo "/isaac-sim"
    return 0
  fi

  local ov_root="${HOME}/.local/share/ov/pkg"
  if [[ -d "${ov_root}" ]]; then
    local candidate=""
    candidate="$(find "${ov_root}" -maxdepth 1 -type d -name 'isaac_sim-*' | sort -V | tail -n 1 || true)"
    if [[ -n "${candidate}" && -x "${candidate}/python.sh" ]]; then
      echo "${candidate}"
      return 0
    fi
  fi

  for base in /opt/nvidia/isaac-sim /opt/NVIDIA/isaac-sim /opt/omniverse/isaac-sim; do
    if [[ -x "${base}/python.sh" ]]; then
      echo "${base}"
      return 0
    fi
  done

  return 1
}

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <script.py|module> [args...]" >&2
  exit 2
fi

ISAAC_ROOT="$(resolve_isaac_root)" || {
  echo "EXPECTED_MISSING_DEPENDENCY: Isaac Sim installation not found." >&2
  echo "Hint: export ISAAC_SIM_ROOT=/abs/path/to/isaac_sim-<version>" >&2
  exit 3
}

export OMNI_KIT_ACCEPT_EULA="${OMNI_KIT_ACCEPT_EULA:-YES}"
exec "${ISAAC_ROOT}/python.sh" "$@"
