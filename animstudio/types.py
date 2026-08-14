"""
Data structures and type definitions for AnimStudio 7 Python Edition.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any


@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0
    pressure: float = 1.0
    color: str = "#000000"
    thickness: float = 2.0


@dataclass
class Pivot:
    id: str
    localX: float
    localY: float
    name: str = "Pivot"


@dataclass
class PuppetPin:
    id: str
    localX: float
    localY: float
    currentLocalX: float
    currentLocalY: float
    weight: float = 1.0


@dataclass
class SmartWarpPin:
    id: str
    x: float
    y: float
    targetX: float
    targetY: float
    radius: float = 50.0


@dataclass
class SmartWarp:
    pins: List[SmartWarpPin] = field(default_factory=list)
    gridRows: int = 10
    gridCols: int = 10
    meshType: str = "triangular"


@dataclass
class Transform:
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scaleX: float = 1.0
    scaleY: float = 1.0
    skewX: float = 0.0
    skewY: float = 0.0
    rotateX: float = 0.0
    rotateY: float = 0.0
    perspective: float = 1000.0
    cameraAngleX: float = 0.0
    cameraAngleY: float = 0.0


@dataclass
class VectorObject:
    id: str
    name: str
    type: str  # 'stroke', 'shape', 'text', '3d', 'image'
    points: List[Point] = field(default_factory=list)
    subPaths: List[List[Point]] = field(default_factory=list)
    strokeColor: str = "#3b82f6"
    strokeWidth: float = 3.0
    fillColor: str = "#93c5fd"
    opacity: float = 1.0
    transform: Transform = field(default_factory=Transform)
    layerId: str = "layer_1"
    visible: bool = True
    locked: bool = False
    
    # 3D Properties
    depth3D: float = 30.0
    rotate3DX: float = 0.0
    rotate3DY: float = 0.0
    rotate3DZ: float = 0.0
    bevel3D: float = 2.0
    
    # Deformation & Puppet
    pivots: List[Pivot] = field(default_factory=list)
    pins: List[PuppetPin] = field(default_factory=list)
    smartWarp: Optional[SmartWarp] = None
    
    # PNG Deep Edit
    imagePath: Optional[str] = None
    threshold: float = 128.0
    colorReplaceFrom: str = "#ffffff"
    colorReplaceTo: str = "#000000"


@dataclass
class Keyframe:
    id: str
    frame: int
    objectId: str
    transform: Transform = field(default_factory=Transform)
    points: List[Point] = field(default_factory=list)
    opacity: float = 1.0
    easing: str = "linear"  # 'linear', 'easeIn', 'easeOut', 'easeInOut', 'elastic', 'bounce'


@dataclass
class Layer:
    id: str
    name: str
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0
    blendMode: str = "normal"


@dataclass
class Project:
    id: str = "proj_1"
    title: str = "AnimStudio Project"
    width: int = 1280
    height: int = 720
    fps: int = 24
    totalFrames: int = 120
    layers: List[Layer] = field(default_factory=list)
    objects: List[VectorObject] = field(default_factory=list)
    keyframes: List[Keyframe] = field(default_factory=list)
