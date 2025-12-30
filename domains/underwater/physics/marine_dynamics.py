"""
KID COSMO — Marine Dynamics v1.0
Open-source physics abstractions for Sovereign Underwater robotics.
"""

import numpy as np
from dataclasses import dataclass

@dataclass
class MarinePhysics:
    gravity: float = 9.81
    rho_water: float = 1025.0 # kg/m^3
    viscosity: float = 0.001  # N*s/m^2 (Dynamic viscosity)

    def calculate_buoyancy(self, volume: float) -> float:
        """F_buoyancy = rho * g * V"""
        return self.rho_water * self.gravity * volume

    def calculate_drag(self, velocity: np.ndarray, area: float, cd: float = 0.5) -> np.ndarray:
        """F_drag = 0.5 * rho * v^2 * Cd * A"""
        speed = np.linalg.norm(velocity)
        if speed < 1e-6:
            return np.zeros_like(velocity)
        drag_mag = 0.5 * self.rho_water * (speed**2) * cd * area
        return -drag_mag * (velocity / speed)

    def hydrostatic_pressure(self, depth: float) -> float:
        """P = P_atm + rho * g * h"""
        return 101325.0 + self.rho_water * self.gravity * depth

@dataclass
class AUVModel:
    mass: float
    volume: float
    drag_area: float
    cd: float = 0.5

    def get_net_force(self, depth: float, velocity: np.ndarray, physics: MarinePhysics) -> np.ndarray:
        """Calculate net vertical/horizontal forces on the AUV."""
        buoyancy = physics.calculate_buoyancy(self.volume)
        weight = self.mass * physics.gravity
        net_vertical = buoyancy - weight # Upward is positive
        
        drag = physics.calculate_drag(velocity, self.drag_area, self.cd)
        
        # Simple resultant force
        force = drag
        force[2] += net_vertical # Assuming Z is vertical
        return force
