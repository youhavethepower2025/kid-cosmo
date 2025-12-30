# Kid Cosmo

**MCP-native autonomy for when Earth isn't answering.**

Kid Cosmo is an MCP-native reasoning engine for autonomous vehicles operating in denied environments — GPS blackouts, communication loss, sensor degradation. Instead of failing when the cloud link dies, Kid Cosmo runs a small language model (Qwen 2.5 7B) directly on the vehicle to make physics-grounded decisions.

Every decision is exposed as an MCP tool, making Kid Cosmo's reasoning queryable by any MCP-compatible AI agent.

---

## What It Does

1. **Monitors for "Dark Window" conditions** — GPS loss, comms blackout, sensor anomalies
2. **Triggers local reasoning** — A small LLM generates structured decisions without network dependency
3. **Outputs Decision Manifests** — Every choice is documented with sensor inputs, deliberation, and expected outcomes
4. **Exposes via MCP** — All decisions and telemetry are queryable through the Model Context Protocol
5. **Bridges to hardware** — MAVLink integration for ArduPilot drones, extensible to ROS2 and others

---

## Quick Start

```bash
# Clone
git clone https://github.com/youhavethepower2025/kid-cosmo.git
cd kid-cosmo

# Install dependencies (Apple Silicon recommended for MLX)
pip install -r requirements.txt

# Run the MCP data server
python domains/underwater/data_interface/mcp_server.py

# Or run the ArduPilot integration (requires SITL)
python integration/ardupilot/scripts/sovereign_pilot.py
```

---

## Project Structure

```
kid-cosmo/
├── spec/                 # Reasoning Manifest v1.0 specification
├── runtime/              # Local reasoning engine (MLX + Qwen)
├── integration/          # ArduPilot MAVLink bridge
│   └── ardupilot/
├── domains/              # Domain-specific physics + data
│   └── underwater/       # AUV/ROV autonomy
└── samples/              # Example decision manifests
```

---

## The Reasoning Manifest

Every decision Kid Cosmo makes is captured in a structured JSON manifest:

```json
{
  "mission_id": "cosmo_abc123",
  "is_dark_window": true,
  "agent_reasoning": {
    "sensory_synthesis": {
      "inputs": ["GPS_LOSS", "ALTITUDE_HOLD"],
      "interpretation": "GPS signal lost. Switching to barometric altitude hold."
    },
    "decision": {
      "actuator_command": "SET_MODE ALT_HOLD",
      "expected_outcome": "Maintain altitude until GPS recovery"
    }
  }
}
```

See [spec/REASONING_MANIFEST_v1.md](spec/REASONING_MANIFEST_v1.md) for the full specification.

---

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| ArduPilot (Copter/Plane) | Working | MAVLink bridge included |
| Underwater (AUV/ROV) | Samples | Physics abstractions + manifests |
| ROS2 | Planned | — |
| CARLA | Planned | — |

---

## Requirements

- Python 3.10+
- Apple Silicon recommended (for MLX local inference)
- ArduPilot SITL for drone testing

---

## License

MIT — See [LICENSE](LICENSE)
