"""
PyQt6 Main Window and GUI Layout for AnimStudio 7.
"""

import sys
import json
import math
from typing import List, Optional

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QToolBar, QDockWidget, QLabel, QPushButton, QSlider, QSpinBox,
        QDoubleSpinBox, QColorDialog, QFileDialog, QTreeWidget, QTreeWidgetItem,
        QComboBox, QCheckBox, QGroupBox, QSplitter, QListWidget, QListWidgetItem,
        QMessageBox, QStatusBar, QFrame, QMenu
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QRectF, QPointF
    from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QBrush, QFont, QAction
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .types import VectorObject, Point, Transform, Keyframe, Layer, Project
from .interpolation import interpolate_objects, apply_easing
from .engine3d import extrude_profile_to_3d, rotate_vertex_3d, project_3d_point
from .vector_deform import smooth_path, apply_puppet_warp, apply_radial_bend


class AnimStudioCanvas(QWidget):
    """Core Canvas viewport supporting 2D drawing, 3D rendering, and transform handles."""
    
    object_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        
        self.tool = "pen"
        self.stroke_color = QColor(59, 130, 246)
        self.fill_color = QColor(147, 197, 253)
        self.stroke_width = 3
        
        self.objects: List[VectorObject] = []
        self.current_points: List[Point] = []
        self.is_drawing = False
        self.selected_object_id: Optional[str] = None
        
        self.onion_skin_enabled = True
        self.current_frame = 1

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            if self.tool in ["pen", "brush"]:
                self.is_drawing = True
                self.current_points = [Point(x=pos.x(), y=pos.y(), color=self.stroke_color.name(), thickness=self.stroke_width)]
            elif self.tool == "select":
                # Hit test objects
                for obj in reversed(self.objects):
                    for p in obj.points:
                        if math.hypot(p.x - pos.x(), p.y - pos.y()) < 15:
                            self.selected_object_id = obj.id
                            self.object_selected.emit(obj.id)
                            self.update()
                            return
            self.update()

    def mouseMoveEvent(self, event):
        pos = event.position()
        if self.is_drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            self.current_points.append(Point(x=pos.x(), y=pos.y(), color=self.stroke_color.name(), thickness=self.stroke_width))
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.is_drawing = False
            if len(self.current_points) > 1:
                obj_type = "3d" if self.tool == "3d" else "stroke"
                obj = VectorObject(
                    id=f"obj_{len(self.objects) + 1}",
                    name=f"Stroke {len(self.objects) + 1}",
                    type=obj_type,
                    points=self.current_points.copy(),
                    strokeColor=self.stroke_color.name(),
                    strokeWidth=self.stroke_width,
                    fillColor=self.fill_color.name()
                )
                self.objects.append(obj)
                self.selected_object_id = obj.id
                self.object_selected.emit(obj.id)
            self.current_points = []
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background canvas styling (#1e1e2e)
        painter.fillRect(self.rect(), QColor(30, 30, 46))
        
        # Draw background grid
        grid_pen = QPen(QColor(49, 50, 68), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        spacing = 30
        for x in range(0, self.width(), spacing):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), spacing):
            painter.drawLine(0, y, self.width(), y)

        # Render objects
        for obj in self.objects:
            if not obj.visible:
                continue
                
            if obj.type == "3d" and len(obj.points) > 1:
                # 3D Extruded mesh rendering
                mesh = extrude_profile_to_3d(obj.points, depth=obj.depth3D)
                for face in mesh.faces:
                    polygon = []
                    for idx in face.indices:
                        if idx < len(mesh.vertices):
                            v = mesh.vertices[idx]
                            v_rot = rotate_vertex_3d(v, obj.rotate3DX, obj.rotate3DY, obj.rotate3DZ)
                            px, py = project_3d_point(v_rot, center_x=self.width()/2, center_y=self.height()/2)
                            polygon.append(QPointF(px, py))
                    
                    if len(polygon) >= 3:
                        painter.setBrush(QBrush(QColor(face.color)))
                        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
                        painter.drawPolygon(polygon)
            else:
                # 2D Vector Stroke rendering
                if len(obj.points) >= 2:
                    is_selected = (obj.id == self.selected_object_id)
                    pen_color = QColor("#f5e0dc") if is_selected else QColor(obj.strokeColor)
                    pen_width = obj.strokeWidth + (2 if is_selected else 0)
                    painter.setPen(QPen(pen_color, int(pen_width), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                    
                    for i in range(len(obj.points) - 1):
                        p1, p2 = obj.points[i], obj.points[i + 1]
                        painter.drawLine(int(p1.x), int(p1.y), int(p2.x), int(p2.y))

        # Render active live stroke
        if len(self.current_points) >= 2:
            painter.setPen(QPen(self.stroke_color, self.stroke_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            for i in range(len(self.current_points) - 1):
                p1, p2 = self.current_points[i], self.current_points[i + 1]
                painter.drawLine(int(p1.x), int(p1.y), int(p2.x), int(p2.y))


class MainWindow(QMainWindow):
    """Main Window UI for AnimStudio 7."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnimStudio 7 - Python PyQt6 Edition")
        self.resize(1366, 850)
        
        self.current_frame = 1
        self.fps = 24
        self.is_playing = False
        
        self.init_stylesheet()
        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

    def init_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #11111b; color: #cdd6f4; }
            QToolBar { background-color: #181825; border-right: 1px solid #313244; spacing: 6px; padding: 6px; }
            QDockWidget { titlebar-close-icon: url(close.png); color: #cdd6f4; font-weight: bold; }
            QDockWidget::title { background: #181825; padding: 8px; border-bottom: 1px solid #313244; }
            QWidget { background-color: #181825; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
            QPushButton { background-color: #313244; border: 1px solid #45475a; border-radius: 6px; padding: 6px 12px; color: #cdd6f4; font-weight: 500; }
            QPushButton:hover { background-color: #45475a; border-color: #89b4fa; }
            QPushButton:pressed { background-color: #89b4fa; color: #11111b; }
            QGroupBox { border: 1px solid #313244; border-radius: 8px; margin-top: 12px; padding-top: 14px; font-weight: bold; color: #89b4fa; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QSpinBox, QDoubleSpinBox, QComboBox { background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 4px; padding: 4px; color: #cdd6f4; }
            QListWidget { background-color: #1e1e2e; border: 1px solid #313244; border-radius: 6px; }
            QStatusBar { background-color: #11111b; color: #a6adc8; border-top: 1px solid #313244; }
        """)

    def init_ui(self):
        # Central Canvas Viewport
        self.canvas = AnimStudioCanvas(self)
        self.canvas.object_selected.connect(self.on_object_selected)
        self.setCentralWidget(self.canvas)
        
        # Left Toolbar
        toolbar = QToolBar("Tools", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)
        
        tools = [
            ("Select", "select"),
            ("Pen Tool", "pen"),
            ("Brush", "brush"),
            ("Eraser", "eraser"),
            ("3D Extrude", "3d"),
            ("Smart Fill", "fill"),
            ("PNG Deep Edit", "deep_edit"),
            ("Vector Deform", "vector_deform")
        ]
        
        for label, tool_id in tools:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, t=tool_id: self.set_tool(t))
            toolbar.addWidget(btn)

        # Right Inspector Dock
        inspector_dock = QDockWidget("Inspector & Properties", self)
        inspector_widget = QWidget()
        inspector_layout = QVBoxLayout(inspector_widget)
        
        # Style Group
        group_style = QGroupBox("Stroke & Fill")
        style_layout = QVBoxLayout(group_style)
        
        btn_stroke = QPushButton("Select Stroke Color")
        btn_stroke.clicked.connect(self.choose_stroke_color)
        style_layout.addWidget(btn_stroke)
        
        btn_fill = QPushButton("Select Fill Color")
        btn_fill.clicked.connect(self.choose_fill_color)
        style_layout.addWidget(btn_fill)
        
        lbl_width = QLabel("Stroke Width:")
        spin_width = QSpinBox()
        spin_width.setRange(1, 50)
        spin_width.setValue(3)
        spin_width.valueChanged.connect(self.set_stroke_width)
        style_layout.addWidget(lbl_width)
        style_layout.addWidget(spin_width)
        
        inspector_layout.addWidget(group_style)
        
        # 3D Extrusion Group
        group_3d = QGroupBox("3D Controls")
        layout_3d = QVBoxLayout(group_3d)
        
        lbl_depth = QLabel("Extrusion Depth:")
        spin_depth = QDoubleSpinBox()
        spin_depth.setRange(5, 200)
        spin_depth.setValue(30)
        spin_depth.valueChanged.connect(self.set_3d_depth)
        layout_3d.addWidget(lbl_depth)
        layout_3d.addWidget(spin_depth)
        
        lbl_rot_x = QLabel("Rotate X:")
        spin_rot_x = QDoubleSpinBox()
        spin_rot_x.setRange(-360, 360)
        spin_rot_x.valueChanged.connect(self.set_3d_rot_x)
        layout_3d.addWidget(lbl_rot_x)
        layout_3d.addWidget(spin_rot_x)
        
        lbl_rot_y = QLabel("Rotate Y:")
        spin_rot_y = QDoubleSpinBox()
        spin_rot_y.setRange(-360, 360)
        spin_rot_y.valueChanged.connect(self.set_3d_rot_y)
        layout_3d.addWidget(lbl_rot_y)
        layout_3d.addWidget(spin_rot_y)
        
        inspector_layout.addWidget(group_3d)
        
        # Layer Manager Group
        group_layers = QGroupBox("Layers")
        layer_layout = QVBoxLayout(group_layers)
        self.layer_list = QListWidget()
        self.layer_list.addItem("Layer 1 (Vector)")
        self.layer_list.addItem("Layer 2 (3D Mesh)")
        layer_layout.addWidget(self.layer_list)
        inspector_layout.addWidget(group_layers)
        
        inspector_layout.addStretch()
        inspector_dock.setWidget(inspector_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, inspector_dock)

        # Bottom Keyframe Timeline Dock
        timeline_dock = QDockWidget("Timeline & Keyframes", self)
        timeline_widget = QWidget()
        timeline_layout = QVBoxLayout(timeline_widget)
        
        controls = QHBoxLayout()
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.clicked.connect(self.toggle_play)
        controls.addWidget(self.btn_play)
        
        controls.addWidget(QLabel("Frame:"))
        self.spin_frame = QSpinBox()
        self.spin_frame.setRange(1, 120)
        self.spin_frame.setValue(1)
        self.spin_frame.valueChanged.connect(self.on_frame_changed)
        controls.addWidget(self.spin_frame)
        
        btn_keyframe = QPushButton("+ Keyframe")
        btn_keyframe.clicked.connect(self.add_keyframe)
        controls.addWidget(btn_keyframe)
        
        controls.addStretch()
        timeline_layout.addLayout(controls)
        
        timeline_dock.setWidget(timeline_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, timeline_dock)
        
        self.statusBar().showMessage("AnimStudio 7 Ready.")

    def set_tool(self, tool_id: str):
        self.canvas.tool = tool_id
        self.statusBar().showMessage(f"Active Tool: {tool_id.upper()}")

    def choose_stroke_color(self):
        color = QColorDialog.getColor(self.canvas.stroke_color, self, "Select Stroke Color")
        if color.isValid():
            self.canvas.stroke_color = color

    def choose_fill_color(self):
        color = QColorDialog.getColor(self.canvas.fill_color, self, "Select Fill Color")
        if color.isValid():
            self.canvas.fill_color = color

    def set_stroke_width(self, val: int):
        self.canvas.stroke_width = val

    def set_3d_depth(self, val: float):
        if self.canvas.selected_object_id:
            for obj in self.canvas.objects:
                if obj.id == self.canvas.selected_object_id:
                    obj.depth3D = val
            self.canvas.update()

    def set_3d_rot_x(self, val: float):
        if self.canvas.selected_object_id:
            for obj in self.canvas.objects:
                if obj.id == self.canvas.selected_object_id:
                    obj.rotate3DX = val
            self.canvas.update()

    def set_3d_rot_y(self, val: float):
        if self.canvas.selected_object_id:
            for obj in self.canvas.objects:
                if obj.id == self.canvas.selected_object_id:
                    obj.rotate3DY = val
            self.canvas.update()

    def on_object_selected(self, obj_id: str):
        self.statusBar().showMessage(f"Selected Object: {obj_id}")

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
        if self.current_frame > 120:
            self.current_frame = 1
        self.spin_frame.setValue(self.current_frame)

    def on_frame_changed(self, frame_val: int):
        self.current_frame = frame_val
        self.canvas.current_frame = frame_val
        self.canvas.update()

    def add_keyframe(self):
        self.statusBar().showMessage(f"Keyframe saved at frame {self.current_frame}")


def run_app():
    if not PYQT_AVAILABLE:
        print("PyQt6 is required to launch the GUI.")
        sys.exit(1)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
