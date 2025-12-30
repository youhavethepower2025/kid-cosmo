#!/usr/bin/env python3
"""
KID COSMO — SITL Mock v1.0
Simulates an ArduPilot vehicle state and broadcasts MAVLink heartbeat/telemetry.
Used for Kid Cosmo integration testing without a full SITL environment.
"""

import time
import socket
from pymavlink import mavutil

def run_mock(target_ip="127.0.0.1", target_port=14550):
    print(f"📡 Starting ArduPilot Mock: {target_ip}:{target_port}")
    
    # Broadcast on UDP
    master = mavutil.mavlink_connection(f"udpout:{target_ip}:{target_port}")
    
    boot_time = time.time()
    step = 0
    
    # Simulation State
    is_gps_loss = False
    is_blackout = False

    while True:
        current_time = time.time() - boot_time
        
        # 1. Heartbeat
        master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED,
            0,
            mavutil.mavlink.MAV_STATE_ACTIVE
        )

        # 2. System Status (Battery)
        master.mav.sys_status_send(
            0, 0, 0, 500, 12400, -1, 85, 0, 0, 0, 0, 0, 0
        )

        # 3. Attitude (Gentle Tumble)
        master.mav.attitude_send(
            int(current_time * 1000),
            0.1 * (step % 10),  # roll
            0.05 * (step % 5),  # pitch
            1.5,                # yaw
            0, 0, 0
        )

        # 4. GPS (Simulate failure at T=15)
        gps_fix = 3 if current_time < 15 or current_time > 45 else 0
        sat_count = 12 if current_time < 15 or current_time > 45 else 2
        
        master.mav.gps_raw_int_send(
            int(current_time * 1000),
            gps_fix,           # fix_type
            378716580,         # lat
            -1224523000,       # lon
            10000,             # alt
            65535, 65535, 0, 65535,
            sat_count          # satellites_visible
        )

        # 5. VFR_HUD (Alt)
        master.mav.vfr_hud_send(15.0, 12.0, 180, 50, 25.0, 0.1)

        if step % 10 == 0:
            status = "NOMINAL" if gps_fix == 3 else "⚠️ GPS_LOSS"
            print(f"🚀 T={current_time:.1f}s | Status: {status}")

        step += 1
        time.sleep(1.0) # 1Hz broadcast

if __name__ == "__main__":
    run_mock()
