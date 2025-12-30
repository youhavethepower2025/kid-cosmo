# Underwater Domain

MCP-native Kid Cosmo for AUVs and ROVs operating in acoustic blackout conditions.

---

## The Problem

Underwater vehicles face unique "Dark Window" scenarios:
- **Acoustic link loss** — Surface vessel communication severed
- **Depth sensor spikes** — Rapid pressure changes from currents or thermoclines
- **Sediment clogging** — Sensor degradation in turbid water

Standard autopilots abort or surface when these conditions occur. Kid Cosmo reasons through them.

---

## What's Included

### Physics Abstractions (`physics/`)
- Buoyancy and drag calculations for AUV dynamics
- Sensor models: Pressure (Depth), DVL (Velocity), IMU (Attitude)
- Dark Window scenario simulation

### MCP Data Server (`data_interface/`)
Query decision manifests programmatically:

```python
# Available MCP tools:
list_domains()                    # → ["underwater", "ardupilot"]
search_manifests("underwater")    # → List of decision traces
get_decision_trace("underwater", "mission_id")
verify_trajectory("underwater", "mission_id")
```

### Sample Manifests (`../../samples/underwater/`)
Example reasoning traces from acoustic blackout scenarios.

---

## Running the MCP Server

```bash
cd domains/underwater/data_interface
python mcp_server.py
```

The server exposes Kid Cosmo decision data to any MCP-compatible client.
