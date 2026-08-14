import React from 'react';
import { 
  Pointer, 
  Paintbrush, 
  Trash2, 
  Scissors, 
  PenTool, 
  MapPin, 
  CircleDot, 
  GitFork, 
  Layers, 
  Maximize2, 
  Minimize2, 
  Crop, 
  Compass, 
  Pipette, 
  Palette, 
  Zap, 
  GitCommit,
  LayoutGrid,
  Sparkles,
  Box,
  ZoomIn,
  Share2,
  Sliders,
  Activity,
  Move,
  Spline,
  EyeOff
} from 'lucide-react';

interface ToolbarProps {
  activeTool: string;
  setActiveTool: (tool: string) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

export default function Toolbar({
  activeTool,
  setActiveTool,
  collapsed,
  setCollapsed,
}: ToolbarProps) {
  const tools = [
    { id: 'SEL', label: 'Select (SEL)', icon: PointerIcon, desc: 'Select / transform drawings' },
    { id: 'LIN', name: 'Line Tool', label: 'Line Tool (LIN)', icon: SplineIcon, desc: 'Shape & stroke editing line: Overlays exact stroke path on selected drawing. Drag line to reshape and curve strokes in real-time.' },
    { id: 'PEN', label: 'Vector Pen (PEN)', icon: FeatherIcon, desc: 'Draw precise bezier curve paths' },
    { id: 'BRS', name: 'Brush', label: 'Brush Tool (BRS)', icon: PaintbrushIcon },
    { id: 'ERS', name: 'Eraser', label: 'Eraser Tool (ERS)', icon: EraserIcon },
    { id: 'PVT', name: 'Pivot', label: 'Pivot Tool (PVT)', icon: AnchorIcon },
    { id: "KNF", name: "Knife", label: "Knife Tool (KNF)", icon: ScissorsIcon },
    { id: "PIN", name: "Puppet Pin", label: "Puppet Pin (PIN)", icon: PinIcon },
    { id: 'FIL', name: 'Fill', label: 'Fill Bucket (FIL)', icon: PaintBucketIcon },
    { id: 'LSO', name: 'Lasso Selection', label: 'Lasso Area & Fill (LSO)', icon: SparklesIcon, desc: 'Draw a lasso region to transform specific sub-areas or color fill them' },
    { id: 'FSL', name: 'Free Selection', label: 'Adjustable Selection (FSL)', icon: SlidersIcon, desc: 'Draw or edit a selection area. Drag, double-click, or insert vertices to customize the region.' },
    { id: 'VEX', name: 'Vector Part Isolator', label: 'Vector Part Isolator (VEX)', icon: ScissorsIcon, desc: 'Draw vector selection around PNG or drawing part to isolate, extract as layer, and auto-infill empty background' },
    { id: 'PSE', name: 'Pose Studio', label: 'Mouth & Eye Pose Studio (PSE)', icon: SparklesIcon, desc: 'Deep mouth opening, eye blinking, pupil movement and 3D posing for PNG characters and drawings' },
    { id: '360', name: '360° Studio', label: '360° Pseudo-3D (360)', icon: CompassIcon, desc: 'Create and animate 360-degree pseudo-3D objects' },
    { id: 'WSC', name: '3D Wire Sculpt', label: '3D Wire Sculpt (WSC)', icon: SparklesIcon, desc: 'Convert 2D stroke to editable 3D wireframe mesh with vertices, extrude, bevel, inner space depth and saved selections.' },
    { id: 'SHP', name: 'Shape', label: 'Shapes Tool (SHP)', icon: ShapesIcon },
    { id: 'MSH', name: 'Mesh Wrap', label: 'Geometry Deform (MSH)', icon: CropIcon, desc: 'Deform drawing geometry by dragging individual vertices deeply' },
    { id: 'SPL', name: 'Spline Reshape', label: 'Spline Reshape (SPL)', icon: Share2Icon, desc: 'Fit stroke to a cubic bezier path and deform or stretch smoothly' },
    { id: 'MCL', name: 'Mesh Coloring', label: 'Smart Mesh Color (MCL)', icon: PaletteIcon, desc: 'Paint directly on simplified mesh cells or points to color your drawing' },
    { id: 'SWP', name: 'Smart Warp', label: 'Smart Pin Warp (SWP)', icon: PinIcon, desc: 'Add large clickable pins to easily deform drawing geometry' },
    { id: 'CAG', name: 'Cage Deform', label: 'Cage Deform (CAG)', icon: BoxIcon, desc: 'Deform the drawing boundary cage to warp the shape smoothly' },
    { id: 'LQB', name: 'Liquify Brush', label: 'Liquify Brush (LQB)', icon: SparklesIcon, desc: 'Push, pinch, bulge, or twist drawing geometry with a brush' },
    { id: 'SPD', name: 'Stroke Touch Pull', label: 'Direct Stroke Pull (SPD)', icon: Sparkles, desc: 'Touch and drag drawing strokes directly to pull and deform locally with auto-smoothing' },
    { id: 'SPT', name: 'Stroke Direct Move', label: 'Direct Stroke Position Move (SPT)', icon: Move, desc: 'Touch and drag any stroke directly to shift strictly its position without bending, blending or warping shape' },
    { id: 'S3D', name: '3D Stroke Extruder', label: '2D-to-3D Stroke & Limb Generator (S3D)', icon: Box, desc: 'Project 2D strokes into 3D volumetric models, rotate in 360°, bevel, extrude, and auto-generate 3D character limbs (legs & hands) from a single stroke' },
    { id: 'CON', name: 'Constraint', label: 'Constraints (CON)', icon: AlignCenterIcon },
    { id: 'MOT', name: 'Motion Path', label: 'Motion Path (MOT)', icon: TrendingUpIcon },
    { id: 'CPT', name: 'Curve Path', label: 'Curve Path Tool (CPT)', icon: GitForkIcon, desc: 'Warp and blend drawing along interactive horizontal and vertical spine lines' },
    { id: 'VDF', name: 'Vector Curve Deformer', label: 'Vector Deformer (VDF)', icon: GitCommit, desc: 'Draw custom vector points by hand across drawing and drag points to deform and blend' },
    { id: 'VPR', name: 'Vector Pen Reshape', label: 'Vector Pen Reshape (VPR)', icon: FeatherIcon, desc: 'Place custom vector pen points on drawing strokes to capture local stroke areas and bend straight lines into circles or curves' },
    { id: 'PBM', name: 'Points Movement', label: 'Points Movement (PBM)', icon: PinIcon, desc: 'Points-Based Movement (PBM): Place custom joint points on drawing and drag to move rigid sections strictly as-is without distortion' },
    { id: 'RPD', name: 'Rigid Point Deform', label: 'Rigid Point Deform (RPD)', icon: PinIcon, desc: 'Place custom points on drawing and drag to move rigid sections in a straight line without stretching or curving' },
    { id: 'CRV', name: 'Curve Line Deformer', label: 'Curve Line Deformer (CRV)', icon: ActivityIcon, desc: 'Flexible curve line overlay to bend and attach to specific drawing parts like tail, arm, leg seamlessly' },
    { id: 'EYE', name: 'Eyedropper', label: 'Eyedropper (EYE)', icon: EyedropperIcon },
    { id: 'ZOM', name: 'Zoom & Pan', label: 'Zoom & Pan (ZOM)', icon: ZoomInIcon, desc: 'Pinch with two fingers to zoom, or drag with single touch/pointer to pan smoothly in any direction.' },
    { id: 'CONTOUR_EDITOR', shortId: 'CNE', name: 'Contour Editor', label: 'Contour Editor (Bezier & Points)', icon: PointerIcon, desc: 'Directly select anchor points, edit Bezier handles and directional control arms' },
    { id: 'CUTTER', shortId: 'CTR', name: 'Cutter', label: 'Cutter Tool (Line Trim)', icon: ScissorsIcon, desc: 'Slice and trim intersecting stroke ends without damaging artwork or fills' },
    { id: 'MASTER_CONTROLLER', shortId: 'MCT', name: 'Master Controller', label: 'Master Controllers (Widgets)', icon: SlidersIcon, desc: 'On-screen 2D Joysticks and Sliders to drive multi-layer puppet rigs' },
    { id: 'PEG_HIERARCHY', shortId: 'PEG', name: 'Peg Hierarchy', label: 'Peg Hierarchy & Rigging', icon: GitForkIcon, desc: 'Parent-child peg linking and pivot offsets for body mechanics' },
    { id: 'BONE_CURVE', shortId: 'BNC', name: 'Bone Deformer', label: 'Bone & Curve Deformer', icon: ActivityIcon, desc: 'Organic bending and stretching along spline curves for limbs' },
    { id: 'PTS', shortId: 'PTS', name: 'Point Shape Sculptor', label: 'Point Shape Sculptor (PTS)', icon: CircleDot, desc: 'Place points to draw custom shapes, drag points to edit/reshape, and merge vertices.' },
    { id: 'SHS', shortId: 'SHS', name: 'Shape Studio', label: 'Shape Studio (SHS)', icon: Layers, desc: 'Add and attach custom shapes, drawings, and PNG parts (mouth, eyes, limbs) permanently to character drawings. Swap poses and expressions with 1 click.' },
    { id: 'SCB', shortId: 'SCB', name: 'Sculpt & Correct Brush', label: 'Sculpt & Correct Brush (SCB)', icon: Sparkles, desc: 'Drag brush over any drawing to expand, collapse, smooth, push, or auto-correct strokes and contours.' },
    { id: 'MSK', shortId: 'MSK', name: 'Area Mask & Hide', label: 'Custom Shape Hide/Show Area (MSK)', icon: EyeOffIcon, desc: 'Draw a custom shape or area on any single individual drawing to hide that specific part. Toggle hide/show or invert masked areas.' },
  ];

  return (
    <div
      className={`bg-neutral-900 border-r border-neutral-800 flex flex-col h-full transition-all duration-200 ${
        collapsed ? 'w-14' : 'w-56'
      }`}
    >
      {/* Brand Header */}
      <div className="h-14 border-b border-neutral-800 flex items-center justify-between px-3 shrink-0">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors ml-auto"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
        </button>
      </div>

      {/* Tools List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin select-none">
        {tools.map((t) => {
          const isActive = activeTool === t.id;
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTool(t.id)}
              className={`w-full flex items-center gap-3 p-2.5 rounded-xl transition-all relative group text-left ${
                isActive
                  ? 'bg-amber-500/20 border border-amber-400/40 text-amber-300 shadow-[0_0_15px_rgba(245,158,11,0.15)] font-black'
                  : 'border border-transparent text-neutral-400 hover:text-white hover:bg-neutral-800/60 font-semibold'
              }`}
              title={t.label}
            >
              <div className={`shrink-0 ${isActive ? 'scale-110' : ''} transition-transform`}>
                <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-neutral-400 group-hover:text-white'}`} />
              </div>
              {!collapsed && (
                <div className="overflow-hidden truncate">
                  <span className="text-xs uppercase tracking-wider block font-bold leading-tight">
                    {(t as any).shortId || t.id}
                  </span>
                  <span className="text-[10px] text-neutral-500 font-semibold block leading-none truncate group-hover:text-neutral-400 transition-colors">
                    {t.name || t.label.split('(')[0].trim()}
                  </span>
                </div>
              )}

              {/* Collapsed Tooltip Overlay */}
              {collapsed && (
                <div className="absolute left-16 bg-neutral-950 border border-neutral-800 text-white text-[11px] font-bold px-3 py-2 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl shadow-black/50">
                  <div className="text-amber-400 font-black">{t.label}</div>
                  <div className="text-neutral-400 text-[10px] font-medium mt-0.5">{t.desc}</div>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// Wrapper local components with correct typing for simpler implementation
function PointerIcon(props: any) { return <Pointer {...props} /> }
function PaintbrushIcon(props: any) { return <Paintbrush {...props} /> }
function ScissorsIcon(props: any) { return <Scissors {...props} /> }
function FeatherIcon(props: any) { return <PenTool {...props} /> }
function PinIcon(props: any) { return <MapPin {...props} /> }
function AnchorIcon(props: any) { return <CircleDot {...props} /> }
function BoneIcon(props: any) { return <GitFork {...props} /> }
function GitForkIcon(props: any) { return <GitFork {...props} /> }
function ZapIcon(props: any) { return <Zap {...props} /> }
function PaintBucketIcon(props: any) { return <Palette {...props} /> }
function PaletteIcon(props: any) { return <Palette {...props} /> }
function ShapesIcon(props: any) { return <LayoutGrid {...props} /> }
function LayoutGridIcon(props: any) { return <LayoutGrid {...props} /> }
function CropIcon(props: any) { return <Crop {...props} /> }
function AlignCenterIcon(props: any) { return <GitCommit {...props} /> }
function TrendingUpIcon(props: any) { return <Compass {...props} /> }
function EyedropperIcon(props: any) { return <Pipette {...props} /> }
function EraserIcon(props: any) { return <Trash2 {...props} /> }
function SparklesIcon(props: any) { return <Sparkles {...props} /> }
function BoxIcon(props: any) { return <Box {...props} /> }
function CompassIcon(props: any) { return <Compass {...props} /> }
function ActivityIcon(props: any) { return <Activity {...props} /> }
function ZoomInIcon(props: any) { return <ZoomIn {...props} /> }
function Share2Icon(props: any) { return <Share2 {...props} /> }
function SlidersIcon(props: any) { return <Sliders {...props} /> }
function SplineIcon(props: any) { return <Spline {...props} /> }
function EyeOffIcon(props: any) { return <EyeOff {...props} /> }
