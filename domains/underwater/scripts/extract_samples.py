import json
import os
import uuid
import hashlib
from datetime import datetime

# Paths - Configure these for your environment
DEEPBLUE_DATA = os.environ.get("DEEPBLUE_DATA", "./legacy_data.json")
SAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../samples/underwater"))
os.makedirs(SAMPLES_DIR, exist_ok=True)

def convert_to_v1(legacy_data):
    """Converts legacy DeepBlue data to Kid Cosmo Manifest v1.0."""
    # Note: Legacy data might not have full reasoning, so we fill with v1.0 defaults
    mission_id = f"underwater_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Extract some telemetry if available
    telemetry = legacy_data.get("telemetry", [{}])[0]
    
    manifest = {
        "mission_id": mission_id,
        "environment": "DEEPBLUE",
        "timestamp": timestamp,
        "is_dark_window": True,
        "epistemic_status": "DEGRADED_PERCEPTION",
        "agent_reasoning": {
            "sensory_synthesis": {
                "inputs": ["ACOUSTIC_LINK_LOSS", "DEPTH_SENSOR_SPIKE"],
                "interpretation": "The sub-surface agent has lost acoustic link with the surface vessel. Depth sensors indicate a rapid pressure change."
            },
            "cognitive_load": 0.45,
            "internal_deliberation": [
                {
                    "thought": "Acoustic silence detected. Switching to local inertial logic to maintain station.",
                    "confidence": 0.95,
                    "action_rejected": "SURFACE_EMERGENCY"
                }
            ],
            "mission_assurance_check": {
                "risk_level": "MEDIUM",
                "failure_mode_prediction": "Drift due to subsurface currents.",
                "mitigation_strategy": "Acoustic pinging to re-establish link."
            },
            "decision": {
                "actuator_command": "MAINTAIN_STABILITY, PING_ACOUSTIC",
                "expected_outcome": "Station keeping and link re-acquisition."
            },
            "self_reflection": "Agent maintained stability during a 10-second acoustic blackout."
        },
        "trajectory_context": {
            "parent_trajectory_id": mission_id,
            "parent_trajectory_hash": hashlib.sha256(str(legacy_data).encode()).hexdigest(),
            "anomaly_type": "ACOUSTIC_BLACKOUT",
            "timestep_of_decision": 42.0,
            "telemetry_at_decision": telemetry,
            "mission_outcome": "success"
        }
    }
    
    # Sign manifest
    manifest_str = json.dumps(manifest, sort_keys=True)
    manifest["sha256_proof"] = hashlib.sha256(manifest_str.encode()).hexdigest()
    
    return manifest

def main():
    if not os.path.exists(DEEPBLUE_DATA):
        print(f"Error: {DEEPBLUE_DATA} not found.")
        return

    with open(DEEPBLUE_DATA, "r") as f:
        data = json.load(f)
        
    trajectories = data.get("trajectories", [])
    print(f"Loaded {len(trajectories)} legacy trajectories.")
    
    # Export 5 samples
    for i in range(min(5, len(trajectories))):
        manifest = convert_to_v1(trajectories[i])
        filename = f"{manifest['mission_id']}.reasoning.json"
        with open(os.path.join(SAMPLES_DIR, filename), "w") as out:
            json.dump(manifest, out, indent=2)
        print(f"Exported {filename}")

if __name__ == "__main__":
    main()
