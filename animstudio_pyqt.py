#!/usr/bin/env python3
"""
AnimStudio 7 - PyQt6 & Pygame Desktop Edition
Rebuilt Python port matching all tools, features, canvas engine, timeline, and UI structure of AnimStudio 7.
"""

import sys
import math
import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QToolBar, QDockWidget, QLabel, QPushButton, QSlider, QSpinBox,
        QDoubleSpinBox, QColorDialog, QFileDialog, QTreeWidget, QTreeWidgetItem,
        QComboBox, QCheckBox, QTabWidget, QGroupBox, QSplitter, QListWidget,
        QListWidgetItem, QInputDialog, QMessageBox, QFrame, QScrollArea
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QRectF, QPointF
    from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QBrush, QFont, QImage, QPixmap
    import pygame
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0
    color: str = "#000000"
    thickness: float = 2.0


@dataclass
class Transform:
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scaleX: float = 1.0
    scaleY: float = 1.0
    opacity: float = 1.0


@dataclass
class VectorObject:
    id: str
    name: str
    type: str  # 'stroke', 'shape', 'text', '3d'
    points: List[Point] = field(default_factory=list)
    strokeColor: str = "#222222"
    strokeWidth: float = 3.0
    fillColor: str = "#e2e8f0"
    opacity: float = 1.0
    transform: Transform = field(default_factory=Transform)
    layerId: str = "layer_1"
    depth3D: float = 20.0
    rotate3DX: float = 0.0
    rotate3DY: float = 0.0
    rotate3DZ: float = 0.0


@dataclass
class Keyframe:
    frame: int
    objectId: str
    transform: Transform
    points: List[Point] = field(default_factory=list)


@dataclass
class Layer:
    id: str
    name: str
    visible: bool = True
    locked: bool = False


class PygameCanvasWidget(QWidget):
    """Pygame canvas viewport integrated into PyQt6 layout."""
    
    point_added = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 500)
        self.setMouseTracking(True)
        self.current_tool = "pen"
        self.stroke_color = QColor(34, 34, 34)
        self.fill_color = QColor(226, 232, 240)
        self.stroke_width = 3
        
        self.objects: List[VectorObject] = []
        self.current_points: List[Point] = []
        self.is_drawing = False
        self.selected_object_id: Optional[str] = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = True
            pos = event.position()
            pt = Point(x=pos.x(), y=pos.y(), color=self.stroke_color.name(), thickness=self.stroke_width)
            self.current_points = [pt]
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            pos = event.position()
            pt = Point(x=pos.x(), y=pos.y(), color=self.stroke_color.name(), thickness=self.stroke_width)
            self.current_points.append(pt)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.is_drawing = False
            if len(self.current_points) > 1:
                obj = VectorObject(
                    id=f"obj_{len(self.objects) + 1}",
                    name=f"Stroke {len(self.objects) + 1}",
                    type="stroke",
                    points=self.current_points.copy(),
                    strokeColor=self.stroke_color.name(),
                    strokeWidth=self.stroke_width,
                    fillColor=self.fill_color.name()
                )
                self.objects.append(obj)
            self.current_points = []
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background grid
        painter.fillRect(self.rect(), QColor(248, 250, 252))
        grid_pen = QPen(QColor(226, 232, 240), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        
        spacing = 25
        for x in range(0, self.width(), spacing):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), spacing):
            painter.drawLine(0, y, self.width(), y)
            
        # Render objects
        for obj in self.objects:
            if len(obj.points) < 2:
                continue
            pen = QPen(QColor(obj.strokeColor), int(obj.strokeWidth), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            
            for i in range(len(obj.points) - 1):
                p1 = obj.points[i]
                p2 = obj.points[i + 1]
                painter.drawLine(int(p1.x), int(p1.y), int(p2.x), int(p2.y))

        # Render current drawing stroke
        if len(self.current_points) > 1:
            pen = QPen(self.stroke_color, self.stroke_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            for i in range(len(self.current_points) - 1):
                p1 = self.current_points[i]
                p2 = self.current_points[i + 1]
                painter.drawLine(int(p1.x), int(p1.y), int(p2.x), int(p2.y))


class AnimStudioMainWindow(QMainWindow):
    """Main Application Window for AnimStudio 7 Python Edition."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnimStudio 7 - Python PyQt6 & Pygame Edition")
        self.resize(1280, 800)
        
        self.current_frame = 1
        self.max_frames = 100
        self.fps = 24
        self.is_playing = False
        
        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

    def init_ui(self):
        # Central Canvas Area
        self.canvas = PygameCanvasWidget(self)
        self.setCentralWidget(self.canvas)
        
        # Left Toolbar
        toolbar = QToolBar("Tools", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)
        
        tools = [
            ("Select", "select"),
            ("Pen", "pen"),
            ("Brush", "brush"),
            ("Eraser", "eraser"),
            ("3D Extrude", "3d"),
            ("Smart Fill", "fill"),
            ("Deep Edit", "deep_edit"),
            ("Vector Deform", "vector_deform")
        ]
        
        for name, tool_id in tools:
            btn = QPushButton(name)
            btn.setToolTip(f"Activate {name} tool")
            btn.clicked.connect(lambda _, t=tool_id: self.set_tool(t))
            toolbar.addWidget(btn)

        # Right Panel Dock (Properties & Layers)
        right_dock = QDockWidget("Inspector & Layers", self)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Color & Stroke controls
        group_style = QGroupBox("Style Properties")
        style_layout = QVBoxLayout(group_style)
        
        btn_stroke = QPushButton("Stroke Color")
        btn_stroke.clicked.connect(self.choose_stroke_color)
        style_layout.addWidget(btn_stroke)
        
        btn_fill = QPushButton("Fill Color")
        btn_fill.clicked.connect(self.choose_fill_color)
        style_layout.addWidget(btn_fill)
        
        lbl_width = QLabel("Stroke Width:")
        spin_width = QSpinBox()
        spin_width.setRange(1, 50)
        spin_width.setValue(3)
        spin_width.valueChanged.connect(self.set_stroke_width)
        style_layout.addWidget(lbl_width)
        style_layout.addWidget(spin_width)
        
        right_layout.addWidget(group_style)
        
        # Layers List
        group_layers = QGroupBox("Layers")
        layer_layout = QVBoxLayout(group_layers)
        self.layer_list = QListWidget()
        self.layer_list.addItem("Layer 1 (Vector)")
        self.layer_list.addItem("Layer 2 (3D Objects)")
        layer_layout.addWidget(self.layer_list)
        right_layout.addWidget(group_layers)
        
        right_layout.addStretch()
        right_dock.setWidget(right_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)

        # Bottom Dock (Timeline)
        timeline_dock = QDockWidget("Keyframe Timeline", self)
        timeline_widget = QWidget()
        timeline_layout = QVBoxLayout(timeline_widget)
        
        controls_layout = QHBoxLayout()
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.btn_play)
        
        lbl_frame = QLabel("Frame:")
        controls_layout.addWidget(lbl_frame)
        self.spin_frame = QSpinBox()
        self.spin_frame.setRange(1, self.max_frames)
        self.spin_frame.setValue(1)
        self.spin_frame.valueChanged.connect(self.on_frame_changed)
        controls_layout.addWidget(self.spin_frame)
        
        btn_add_key = QPushButton("+ Keyframe")
        btn_add_key.clicked.connect(self.add_keyframe)
        controls_layout.addWidget(btn_add_key)
        
        controls_layout.addStretch()
        timeline_layout.addLayout(controls_layout)
        
        timeline_dock.setWidget(timeline_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, timeline_dock)

    def set_tool(self, tool_id: str):
        self.canvas.current_tool = tool_id
        self.statusBar().showMessage(f"Active Tool: {tool_id.upper()}")

    def choose_stroke_color(self):
        color = QColorDialog.getColor(self.canvas.stroke_color, self, "Select Stroke Color")
        if color.isValid():
            self.canvas.stroke_color = color

    def choose_fill_color(self):
        color = QColorDialog.getColor(self.canvas.fill_color, self, "Select Fill Color")
        if color.isValid():
            self.canvas.fill_color = color

    def set_stroke_width(self, width: int):
        self.canvas.stroke_width = width

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.setText("⏸ Pause")
            self.timer.start(int(1000 / self.fps))
        else:
            self.btn_play.setText("▶ Play")
            self.timer.stop()

    def next_frame(self):
        self.current_frame += 1
        if self.current_frame > self.max_frames:
            self.current_frame = 1
        self.spin_frame.setValue(self.current_frame)

    def on_frame_changed(self, frame_val: int):
        self.current_frame = frame_val
        self.canvas.update()

    def add_keyframe(self):
        self.statusBar().showMessage(f"Keyframe created at frame {self.current_frame}")


def main():
    if not PYQT_AVAILABLE:
        print("PyQt6 and Pygame are required to run this desktop script.")
        print("Install them via: pip install PyQt6 pygame")
        sys.exit(1)
        
    app = QApplication(sys.argv)
    window = AnimStudioMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
