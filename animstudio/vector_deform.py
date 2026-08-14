"""
Vector Deform and Mesh Deformer Engine for AnimStudio 7.
Handles lattice warp, puppet deformation, radial twist/bend, and spline curve smoothing.
"""

import math
from typing import List, Tuple
from .types import Point, PuppetPin, VectorObject


def smooth_path(points: List[Point], smoothing_factor: float = 0.5) -> List[Point]:
    """Applies Catmull-Rom or Laplacian curve smoothing to vector control points."""
    if len(points) < 3:
        return points

    smoothed = [points[0]]
    for i in range(1, len(points) - 1):
        prev_p = points[i - 1]
        curr_p = points[i]
        next_p = points[i + 1]

        nx = curr_p.x + smoothing_factor * ((prev_p.x + next_p.x) / 2.0 - curr_p.x)
        ny = curr_p.y + smoothing_factor * ((prev_p.y + next_p.y) / 2.0 - curr_p.y)
        smoothed.append(Point(x=nx, y=ny, z=curr_p.z, color=curr_p.color, thickness=curr_p.thickness))

    smoothed.append(points[-1])
    return smoothed


def apply_puppet_warp(points: List[Point], pins: List[PuppetPin]) -> List[Point]:
    """Deforms vector points based on Inverse Distance Weighting (IDW) from puppet pins."""
    if not pins or not points:
        return points

    deformed = []
    for pt in points:
        total_weight = 0.0
        dx_acc = 0.0
        dy_acc = 0.0

        for pin in pins:
            # Distance from point to pin's base local position
            dist = math.hypot(pt.x - pin.localX, pt.y - pin.localY)
            if dist < 0.001:
                dist = 0.001
            weight = 1.0 / math.pow(dist, 2.0)
            
            displacement_x = pin.currentLocalX - pin.localX
            displacement_y = pin.currentLocalY - pin.localY

            dx_acc += displacement_x * weight
            dy_acc += displacement_y * weight
            total_weight += weight

        if total_weight > 0:
            final_dx = dx_acc / total_weight
            final_dy = dy_acc / total_weight
            deformed.append(Point(x=pt.x + final_dx, y=pt.y + final_dy, z=pt.z, color=pt.color, thickness=pt.thickness))
        else:
            deformed.append(pt)

    return deformed


def apply_radial_bend(points: List[Point], center_x: float, center_y: float, angle_degrees: float, radius: float = 200.0) -> List[Point]:
    """Applies a radial twist or bend deformation around a center point."""
    angle_rad = math.radians(angle_degrees)
    res = []
    for pt in points:
        dist = math.hypot(pt.x - center_x, pt.y - center_y)
        if dist < radius:
            factor = (1.0 - dist / radius) * angle_rad
            curr_angle = math.atan2(pt.y - center_y, pt.x - center_x)
            new_angle = curr_angle + factor
            nx = center_x + dist * math.cos(new_angle)
            ny = center_y + dist * math.sin(new_angle)
            res.append(Point(x=nx, y=ny, z=pt.z, color=pt.color, thickness=pt.thickness))
        else:
            res.append(pt)
    return res
