# ArduPilot Integration

MCP-native Kid Cosmo as a companion brain for ArduPilot vehicles.

---

## Architecture

We don't modify ArduPilot's safety-critical C++ core. Instead, Kid Cosmo runs as a **companion computer** (Jetson, Raspberry Pi, or Apple Silicon) communicating via MAVLink.

```
┌─────────────────┐     MAVLink      ┌─────────────────┐
│   ArduPilot     │ ◄──────────────► │   Kid Cosmo     │
│   Flight Core   │                  │   Reasoning     │
└─────────────────┘                  └─────────────────┘
        │                                    │
        ▼                                    ▼
   Hardware I/O                      Local LLM (Qwen)
   (Motors, GPS)                     Decision Manifests
```

---

## Components

### MAVLink Bridge (`scripts/mavlink_bridge.py`)
Listens to ArduPilot telemetry:
- `SYS_STATUS` — System health
- `GPS_RAW_INT` — GPS fix quality
- `ATTITUDE` — Roll, pitch, yaw
- `BATTERY_STATUS` — Power state

Detects "Dark Window" triggers:
- GPS fix drops below 3D lock
- Ground control heartbeat lost
- Rapid sensor divergence

### Sovereign Pilot (`scripts/sovereign_pilot.py`)
The reasoning loop:
1. Receives telemetry snapshot from bridge
2. Detects exclusion zone conditions
3. Runs local Qwen inference
4. Generates Reasoning Manifest
5. Sends MAVLink commands back to ArduPilot

### Supported Commands
- `SET_MODE` — Switch flight modes (ALT_HOLD, LAND, LOITER)
- `RC_CHANNELS_OVERRIDE` — Direct actuator control

---

## Usage

```bash
# Start ArduPilot SITL
sim_vehicle.py -v ArduCopter --console --map

# In another terminal, run Kid Cosmo
cd integration/ardupilot/scripts
python sovereign_pilot.py
```

The Sovereign Pilot will monitor for GPS loss or comms blackout and generate local decisions.

---

## Testing Without Hardware

Use `SITL_MOCK.py` to simulate telemetry without a full ArduPilot SITL setup:

```bash
python SITL_MOCK.py
```
