"""
3D Engine and Extrusion Pipeline for AnimStudio 7.
Handles 2D profile extrusion into 3D polygon meshes, matrix transformations,
lighting & surface normal shading, and wireframe/shaded rendering.
"""

import math
from typing import List, Tuple, Dict, Optional
from .types import Point, VectorObject


class Face3D:
    def __init__(self, indices: List[int], color: str = "#93c5fd", normal: Tuple[float, float, float] = (0, 0, 1)):
        self.indices = indices
        self.color = color
        self.normal = normal


class Mesh3D:
    def __init__(self):
        self.vertices: List[Tuple[float, float, float]] = []
        self.faces: List[Face3D] = []


def extrude_profile_to_3d(points: List[Point], depth: float = 30.0, bevel: float = 0.0) -> Mesh3D:
    """Extrudes a 2D polyline profile into a 3D polygonal mesh with front, back, and side quad faces."""
    mesh = Mesh3D()
    if len(points) < 2:
        return mesh

    n = len(points)
    # Front vertices (z = -depth / 2)
    for p in points:
        mesh.vertices.append((p.x, p.y, -depth / 2.0))

    # Back vertices (z = depth / 2)
    for p in points:
        mesh.vertices.append((p.x, p.y, depth / 2.0))

    # Side quad faces connecting front and back loops
    for i in range(n - 1):
        idx_f1 = i
        idx_f2 = i + 1
        idx_b1 = i + n
        idx_b2 = i + 1 + n

        # Side face quads
        face = Face3D(indices=[idx_f1, idx_f2, idx_b2, idx_b1], color="#3b82f6")
        mesh.faces.append(face)

    # Front cap face
    front_indices = list(range(n))
    mesh.faces.append(Face3D(indices=front_indices, color="#60a5fa", normal=(0, 0, -1)))

    # Back cap face
    back_indices = list(range(n, 2 * n))
    back_indices.reverse()
    mesh.faces.append(Face3D(indices=back_indices, color="#2563eb", normal=(0, 0, 1)))

    return mesh


def rotate_vertex_3d(v: Tuple[float, float, float], rotX: float, rotY: float, rotZ: float) -> Tuple[float, float, float]:
    """Applies Euler angle 3D rotations (in degrees) to a 3D vertex (x, y, z)."""
    rx = math.radians(rotX)
    ry = math.radians(rotY)
    rz = math.radians(rotZ)

    x, y, z = v

    # Rotate X
    y1 = y * math.cos(rx) - z * math.sin(rx)
    z1 = y * math.sin(rx) + z * math.cos(rx)
    x1 = x

    # Rotate Y
    x2 = x1 * math.cos(ry) + z1 * math.sin(ry)
    z2 = -x1 * math.sin(ry) + z1 * math.cos(ry)
    y2 = y1

    # Rotate Z
    x3 = x2 * math.cos(rz) - y2 * math.sin(rz)
    y3 = x2 * math.sin(rz) + y2 * math.cos(rz)
    z3 = z2

    return (x3, y3, z3)


def project_3d_point(v: Tuple[float, float, float], perspective: float = 800.0, center_x: float = 640.0, center_y: float = 360.0) -> Tuple[float, float]:
    """Projects a 3D point (x, y, z) to 2D screen coordinates using perspective projection."""
    x, y, z = v
    factor = perspective / (perspective + z) if (perspective + z) != 0 else 1.0
    proj_x = center_x + (x - center_x) * factor
    proj_y = center_y + (y - center_y) * factor
    return (proj_x, proj_y)
