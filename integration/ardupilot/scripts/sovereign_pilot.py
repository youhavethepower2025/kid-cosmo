#!/usr/bin/env python3
"""
KID COSMO — Sovereign Pilot v1.0
The decision engine that flies when Earth isn't answering.
"""

import os
import json
import uuid
from datetime import datetime
from mavlink_bridge import MAVLinkBridge
# Import the Kid Cosmo reasoning engine
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../runtime")))
from reasoning_agent import ReasoningAgent

# CONFIGURATION
INVENTORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../samples/ardupilot"))
os.makedirs(INVENTORY_DIR, exist_ok=True)

class SovereignPilot:
    def __init__(self, connection_str: str = "udpin:localhost:14550"):
        self.bridge = MAVLinkBridge(connection_str)
        self.agent = ReasoningAgent()
        self.last_decision_time = 0
        self.decision_cooldown = 5.0 # Seconds between sovereign breaths

    def run(self):
        self.bridge.wait_for_heartbeat()
        print("🚀 Sovereign Pilot Active. Monitoring for Exclusion Zone...")

        while True:
            self.bridge.update()
            snapshot = self.bridge.get_snapshot()
            
            # Exclusion Zone Logic: Blackout or GPS Loss
            is_exclusion = snapshot["is_blackout"] or snapshot["perception"]["gps_fix"] < 3
            
            if is_exclusion and (time.time() - self.last_decision_time > self.decision_cooldown):
                print(f"⚠️  EXCLUSION ZONE TRIGGER: Blackout={snapshot['is_blackout']}, GPS={snapshot['perception']['gps_fix']}")
                
                anomaly_type = "503_CONJUNCTION_BLACKOUT" if snapshot["is_blackout"] else "GNSS_DENIED_NAVIGATION"
                
                # Generate Sovereign Manifest
                manifest = self.agent.generate_manifest(
                    mission_id=f"cosmo_{uuid.uuid4().hex[:8]}",
                    environment="ARDUPILOT_SITL",
                    telemetry_snapshot=snapshot,
                    anomaly_description=anomaly_type,
                    epistemic_isolation=snapshot["is_blackout"],
                    trajectory_context={
                        "parent_trajectory_id": f"sitl_{int(time.time())}",
                        "parent_trajectory_hash": "SITL_MOCK_DYNAMIC",
                        "anomaly_type": anomaly_type,
                        "timestep_of_decision": snapshot["t"],
                        "telemetry_at_decision": snapshot,
                        "mission_outcome": "indeterminate"
                    }
                )
                
                # Save Manifest to Kid Cosmo Samples
                m_filename = f"{manifest['mission_id']}.reasoning.json"
                m_path = os.path.join(INVENTORY_DIR, m_filename)
                with open(m_path, "w") as f:
                    json.dump(manifest, f, indent=2)
                
                print(f"🧠 Decision: {manifest['agent_reasoning']['decision']['actuator_command']}")
                print(f"📄 Saved Manifest: {m_filename}")
                
                # EXECUTE DECISION (Bridge to MAVLink)
                self.execute_decision(manifest["agent_reasoning"]["decision"]["actuator_command"])
                
                self.last_decision_time = time.time()

            time.sleep(0.1)

    def execute_decision(self, command: str):
        """Maps Kid Cosmo decisions to ArduPilot MAVLink commands."""
        command = command.upper()
        
        if "SWITCH_MODE" in command:
            target_mode = command.split("SWITCH_MODE")[-1].strip()
            # Handle common reasoning aliases
            if "HEADING_HOLD" in target_mode or "ALT_HOLD" in target_mode:
                self.bridge.set_mode("ALT_HOLD")
            elif "LAND" in target_mode:
                self.bridge.set_mode("LAND")
            elif "STABILIZE" in target_mode:
                self.bridge.set_mode("STABILIZE")
            else:
                print(f"🕹️  Somatic Action: Attempting to set mode {target_mode}")
                self.bridge.set_mode(target_mode)

        elif "SUN_SAFE_ATTITUDE" in command or "MAINTAIN_STABILITY" in command:
            print("🕹️  Somatic Action: Leveling aircraft (ALT_HOLD).")
            self.bridge.set_mode("ALT_HOLD")

        elif "EMERGENCY_LAND" in command:
            print("🕹️  Somatic Action: EXECUTING EMERGENCY LAND.")
            self.bridge.set_mode("LAND")

        elif "STOP" in command or "HOVER" in command or "HOLD_POSITION" in command:
            print("🕹️  Somatic Action: Entering BRAKE/LOITER.")
            # If GPS is down, LOITER might fail, fallback to ALT_HOLD
            if self.bridge.telemetry["gps_fix"] < 3:
                self.bridge.set_mode("ALT_HOLD")
            else:
                self.bridge.set_mode("LOITER")
        
        elif "RC_OVERRIDE" in command:
            # Example: "RC_OVERRIDE 1500 1500 1200 1500"
            params = [int(s) for s in command.split() if s.isdigit()]
            if len(params) == 4:
                self.bridge.send_rc_override(*params)
            else:
                print(f"⚠️  Invalid RC_OVERRIDE params: {command}")
        
        else:
            print(f"🕹️  Somatic Action: {command} (Monitoring only - No direct mapping)")

if __name__ == "__main__":
    import time
    pilot = SovereignPilot()
    pilot.run()
