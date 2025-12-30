#!/usr/bin/env python3
"""
KID COSMO — Dataset MCP Server v1.0
Exposing verified physics trajectories and reasoning manifests to the open-source community.
"""

import os
import json
import hashlib
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("KidCosmoData", dependencies=["mcp"])

# CONFIGURATION - Paths to search
# Set KIDCOSMO_DATA_ROOT environment variable for custom data location
INVENTORY_ROOT = os.environ.get("KIDCOSMO_DATA_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../samples")))
KCOSMO_SAMPLES = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../samples"))

@mcp.tool()
def list_domains() -> List[str]:
    """List the available simulation domains (e.g., underwater, ardupilot, deepblack)."""
    domains = set()
    for root in [INVENTORY_ROOT, KCOSMO_SAMPLES]:
        if os.path.exists(root):
            domains.update([d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))])
    return sorted(list(domains))

@mcp.tool()
def search_manifests(domain: str, anomaly_type: str = None, is_dark_window: bool = None) -> List[Dict[str, Any]]:
    """
    Search for reasoning manifests based on metadata.
    Searches both proprietary inventory and open-source samples.
    """
    results = []
    for root in [INVENTORY_ROOT, KCOSMO_SAMPLES]:
        domain_path = os.path.join(root, domain)
        if not os.path.exists(domain_path):
            continue
            
        for filename in os.listdir(domain_path):
            if filename.endswith(".reasoning.json"):
                with open(os.path.join(domain_path, filename), "r") as f:
                    try:
                        manifest = json.load(f)
                        # ... (filtering logic same as before)
                    
                    # Apply filters
                    if anomaly_type and manifest.get("trajectory_context", {}).get("anomaly_type") != anomaly_type:
                        continue
                    if is_dark_window is not None and manifest.get("is_dark_window") != is_dark_window:
                        continue
                        
                    results.append({
                        "mission_id": manifest.get("mission_id"),
                        "anomaly": manifest.get("trajectory_context", {}).get("anomaly_type"),
                        "outcome": manifest.get("trajectory_context", {}).get("mission_outcome"),
                        "is_blackout": manifest.get("is_dark_window"),
                        "decision": manifest.get("agent_reasoning", {}).get("decision", {}).get("actuator_command")
                    })
                except Exception:
                    continue
    return results[:50] # Cap results for MCP brevity

@mcp.tool()
def get_decision_trace(domain: str, mission_id: str) -> Dict[str, Any]:
    """Retrieve the full Reasoning Manifest for a specific mission."""
    m_path = os.path.join(INVENTORY_ROOT, domain, f"{mission_id}.reasoning.json")
    if not os.path.exists(m_path):
        return {"error": f"Manifest {mission_id} not found in domain {domain}."}
    
    with open(m_path, "r") as f:
        return json.load(f)

@mcp.tool()
def verify_trajectory(domain: str, mission_id: str) -> Dict[str, Any]:
    """Verify the SHA-256 integrity of a reasoning manifest against its parent trajectory."""
    m_path = os.path.join(INVENTORY_ROOT, domain, f"{mission_id}.reasoning.json")
    if not os.path.exists(m_path):
        return {"error": "Manifest not found."}

    with open(m_path, "r") as f:
        manifest = json.load(f)
    
    stored_hash = manifest.get("trajectory_context", {}).get("parent_trajectory_hash")
    # In a real implementation, we would hash the actual telemetry file here
    return {
        "mission_id": mission_id,
        "stored_hash": stored_hash,
        "verification_status": "PENDING_TELEMETRY_ACCESS"
    }

if __name__ == "__main__":
    mcp.run()
