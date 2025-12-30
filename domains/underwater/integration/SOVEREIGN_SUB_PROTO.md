# Sovereign Sub — The Underwater Standard

Kid Cosmo's **Sovereign Sub** protocol is the first open-source, physics-grounded autopilot bridge for AUVs and ROVs. It is designed to be the "Safe Brain" that takes command when sensors degrade or communication is severed.

---

## Hardware Targets

### 1. BlueOS / ArduSub (Direct Integration)
Since ArduSub is built on the ArduPilot stack, Kid Cosmo provides a native MAVLink bridge for:
- BlueROV2
- Custom ArduSub-powered AUVs
- Payload-based companion computers (Jetson Orin, RPi 4)

### 2. ROS2 (Planned)
A ROS2 node that subscribes to `/odom` and `/depth` and publishes `twist` commands based on Kid Cosmo reasoning.

---

## Somatic Logic: The Depth Recovery Loop

Underwater autonomy differs from flight in three ways:

1. **Buoyancy is Life**: In a "Dark Window," maintaining neutral or slightly positive buoyancy is the primary safety heuristic.

2. **Acoustic Pinging**: Communication isn't just "on/off"; it's low-bandwidth. Kid Cosmo includes a "Sparse Reasoner" that can compress its thoughts into 32-byte acoustic pings.

3. **Hydrostatic Reality**: Every decision is validated against the `physics/marine_dynamics.py` module to ensure thruster commands don't exceed current or pressure limits.

---

## Usage

```bash
# Start the submarine simulation
python domains/underwater/scripts/SITL_SUB_MOCK.py

# In another terminal, run the Somatic Sub brain
python domains/underwater/scripts/somatic_sub.py
```

The Somatic Sub will detect acoustic blackouts and generate reasoning manifests for each decision.

---

## Output

When an acoustic link loss is detected, Sovereign Sub:
1. Generates a reasoning manifest (e.g., `sub_abc123.reasoning.json`)
2. Executes the safest actuation (STABILIZE, DEPTH_HOLD, or SURFACE)
3. Logs the decision for post-mission analysis
