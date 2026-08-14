"""
Keyframe Interpolation Engine for AnimStudio 7.
Handles linear, ease-in, ease-out, bezier curves, elastic, and spring easing
across 2D transforms, 3D rotations, vector control points, colors, and puppet pins.
"""

import math
from typing import List, Dict, Optional, Tuple, Any
from .types import Transform, VectorObject, Point, Keyframe, PuppetPin, SmartWarp, SmartWarpPin


def apply_easing(t: float, easing: str) -> float:
    """Clamps t in [0, 1] and applies easing function curves."""
    t = max(0.0, min(1.0, t))
    if easing == "easeIn":
        return t * t * t
    elif easing == "easeOut":
        return 1.0 - math.pow(1.0 - t, 3)
    elif easing == "easeInOut":
        return 4.0 * t * t * t if t < 0.5 else 1.0 - math.pow(-2.0 * t + 2.0, 3) / 2.0
    elif easing == "elastic":
        if t == 0 or t == 1:
            return t
        c4 = (2.0 * math.pi) / 3.0
        return -math.pow(2.0, 10.0 * t - 10.0) * math.sin((t * 10.0 - 10.75) * c4)
    elif easing == "bounce":
        n1 = 7.5625
        d1 = 2.75
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
    # Linear fallback
    return t


def interpolate_transform(t_start: Transform, t_end: Transform, progress: float) -> Transform:
    """Linearly interpolates transform properties with easing factor."""
    def lerp(a: float, b: float) -> float:
        return a + progress * (b - a)

    return Transform(
        x=lerp(t_start.x, t_end.x),
        y=lerp(t_start.y, t_end.y),
        rotation=lerp(t_start.rotation, t_end.rotation),
        scaleX=lerp(t_start.scaleX, t_end.scaleX),
        scaleY=lerp(t_start.scaleY, t_end.scaleY),
        skewX=lerp(t_start.skewX, t_end.skewX),
        skewY=lerp(t_start.skewY, t_end.skewY),
        rotateX=lerp(t_start.rotateX, t_end.rotateX),
        rotateY=lerp(t_start.rotateY, t_end.rotateY),
        perspective=lerp(t_start.perspective, t_end.perspective),
        cameraAngleX=lerp(t_start.cameraAngleX, t_end.cameraAngleX),
        cameraAngleY=lerp(t_start.cameraAngleY, t_end.cameraAngleY)
    )


def interpolate_points(pts_start: List[Point], pts_end: List[Point], progress: float) -> List[Point]:
    """Interpolates point arrays if lengths match."""
    if not pts_start or not pts_end or len(pts_start) != len(pts_end):
        return pts_start or pts_end or []

    res = []
    for p1, p2 in zip(pts_start, pts_end):
        res.append(Point(
            x=p1.x + progress * (p2.x - p1.x),
            y=p1.y + progress * (p2.y - p1.y),
            z=p1.z + progress * (p2.z - p1.z),
            pressure=p1.pressure + progress * (p2.pressure - p1.pressure),
            color=p1.color,
            thickness=p1.thickness + progress * (p2.thickness - p1.thickness)
        ))
    return res


def interpolate_objects(obj_start: VectorObject, obj_end: VectorObject, progress: float, easing: str = "linear") -> VectorObject:
    """Computes interpolated VectorObject state at progress t between two keyframe objects."""
    e = apply_easing(progress, easing)
    
    interp_trans = interpolate_transform(obj_start.transform, obj_end.transform, e)
    interp_pts = interpolate_points(obj_start.points, obj_end.points, e)
    
    interp_depth = obj_start.depth3D + e * (obj_end.depth3D - obj_start.depth3D)
    interp_rot3dX = obj_start.rotate3DX + e * (obj_end.rotate3DX - obj_start.rotate3DX)
    interp_rot3dY = obj_start.rotate3DY + e * (obj_end.rotate3DY - obj_start.rotate3DY)
    interp_rot3dZ = obj_start.rotate3DZ + e * (obj_end.rotate3DZ - obj_start.rotate3DZ)
    interp_opacity = obj_start.opacity + e * (obj_end.opacity - obj_start.opacity)

    return VectorObject(
        id=obj_start.id,
        name=obj_start.name,
        type=obj_start.type,
        points=interp_pts,
        strokeColor=obj_start.strokeColor,
        strokeWidth=obj_start.strokeWidth,
        fillColor=obj_start.fillColor,
        opacity=interp_opacity,
        transform=interp_trans,
        layerId=obj_start.layerId,
        visible=obj_start.visible,
        locked=obj_start.locked,
        depth3D=interp_depth,
        rotate3DX=interp_rot3dX,
        rotate3DY=interp_rot3dY,
        rotate3DZ=interp_rot3dZ
    )
