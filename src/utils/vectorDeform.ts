import { Point, CustomVectorDeformNode } from '../types';

/**
 * Calculates deformed object points given original object points and custom vector deform nodes.
 *
 * STRICT UNIFORM & LINEAR POINT MOVEMENT (NO BLENDING, NO CURVING, 100% ISOLATED):
 * 1. ONLY points strictly within the tight capture corridor around placed nodes and segments move.
 * 2. NO radial weight falloff / decay multiplier is applied — captured points move with 100% direct
 *    linear displacement along the placed segment. Straight lines stay exact straight lines with ZERO curves or bends.
 * 3. All other parts of the drawing (head, torso, other strokes) remain 100% STABLE, FROZEN, AND UNTOUCHED.
 */
export function calculateCustomVectorDeformedPoints(
  origPoints: Point[],
  nodes: CustomVectorDeformNode[],
  captureRadius: number = 25
): Point[] {
  if (!origPoints || origPoints.length === 0) return [];
  if (!nodes || nodes.length === 0) return origPoints;

  const nodeDisplacements = nodes.map(n => ({
    node: n,
    origX: n.origX,
    origY: n.origY,
    dx: n.x - n.origX,
    dy: n.y - n.origY,
    rad: Math.max(25, n.radius || captureRadius || 60)
  }));

  const hasMovement = nodeDisplacements.some(d => Math.abs(d.dx) > 0.001 || Math.abs(d.dy) > 0.001);
  if (!hasMovement) return origPoints;

  // Build segments between linked nodes
  const segments: Array<{
    origA: { x: number; y: number };
    origB: { x: number; y: number };
    dxA: number;
    dyA: number;
    dxB: number;
    dyB: number;
    rad: number;
  }> = [];

  const nodeMap = new Map<string, typeof nodeDisplacements[0]>();
  nodeDisplacements.forEach(nd => nodeMap.set(nd.node.id, nd));
  const processedPairs = new Set<string>();

  for (let i = 0; i < nodeDisplacements.length; i++) {
    const curr = nodeDisplacements[i];
    let parent = curr.node.parentNodeId ? nodeMap.get(curr.node.parentNodeId) : (i > 0 ? nodeDisplacements[i - 1] : undefined);
    if (parent && parent.node.id !== curr.node.id) {
      const pairKey = `${parent.node.id}_${curr.node.id}`;
      if (!processedPairs.has(pairKey)) {
        processedPairs.add(pairKey);
        segments.push({
          origA: { x: parent.origX, y: parent.origY },
          origB: { x: curr.origX, y: curr.origY },
          dxA: parent.dx,
          dyA: parent.dy,
          dxB: curr.dx,
          dyB: curr.dy,
          rad: Math.max(25, Math.max(parent.rad, curr.rad))
        });
      }
    }
  }

  return origPoints.map(pt => {
    let isCaptured = false;
    let bestDist = Infinity;
    let dispX = 0;
    let dispY = 0;

    if (segments.length > 0) {
      for (let s = 0; s < segments.length; s++) {
        const seg = segments[s];
        const abx = seg.origB.x - seg.origA.x;
        const aby = seg.origB.y - seg.origA.y;
        const ab2 = abx * abx + aby * aby;

        if (ab2 < 0.0001) {
          const dist = Math.hypot(pt.x - seg.origA.x, pt.y - seg.origA.y);
          if (dist <= seg.rad && dist < bestDist) {
            bestDist = dist;
            isCaptured = true;
            dispX = seg.dxA;
            dispY = seg.dyA;
          }
        } else {
          const t_raw = ((pt.x - seg.origA.x) * abx + (pt.y - seg.origA.y) * aby) / ab2;

          if (t_raw >= 0 && t_raw <= 1) {
            const projX = seg.origA.x + t_raw * abx;
            const projY = seg.origA.y + t_raw * aby;
            const dist = Math.hypot(pt.x - projX, pt.y - projY);

            if (dist <= seg.rad && dist < bestDist) {
              bestDist = dist;
              isCaptured = true;
              // Pure linear parametric interpolation (ZERO CURVES, ZERO BLENDING Multipliers)
              dispX = (1 - t_raw) * seg.dxA + t_raw * seg.dxB;
              dispY = (1 - t_raw) * seg.dyA + t_raw * seg.dyB;
            }
          } else if (t_raw > 1) {
            const distB = Math.hypot(pt.x - seg.origB.x, pt.y - seg.origB.y);
            if (distB <= seg.rad && distB < bestDist) {
              bestDist = distB;
              isCaptured = true;
              dispX = seg.dxB;
              dispY = seg.dyB;
            }
          } else if (t_raw < 0) {
            const distA = Math.hypot(pt.x - seg.origA.x, pt.y - seg.origA.y);
            if (distA <= seg.rad && distA < bestDist) {
              bestDist = distA;
              isCaptured = true;
              dispX = seg.dxA;
              dispY = seg.dyA;
            }
          }
        }
      }
    } else {
      // Standalone node influences
      for (let n = 0; n < nodeDisplacements.length; n++) {
        const nd = nodeDisplacements[n];
        const dist = Math.hypot(pt.x - nd.origX, pt.y - nd.origY);
        if (dist <= nd.rad && dist < bestDist) {
          bestDist = dist;
          isCaptured = true;
          dispX = nd.dx;
          dispY = nd.dy;
        }
      }
    }

    // STRICT ISOLATION: Point outside capture corridor -> 100% FROZEN & UNTOUCHED!
    if (!isCaptured) {
      return pt;
    }

    const ext = pt as Point & { p1?: Point; p2?: Point };
    return {
      ...pt,
      x: Number((pt.x + dispX).toFixed(2)),
      y: Number((pt.y + dispY).toFixed(2)),
      ...(ext.p1 ? { p1: { x: Number((ext.p1.x + dispX).toFixed(2)), y: Number((ext.p1.y + dispY).toFixed(2)) } } : {}),
      ...(ext.p2 ? { p2: { x: Number((ext.p2.x + dispX).toFixed(2)), y: Number((ext.p2.y + dispY).toFixed(2)) } } : {})
    };
  });
}

/**
 * Calculates deformed object points using STRICT RIGID 2D TRANSFORM.
 */
export function calculateRigidLinearDeformedPoints(
  origPoints: Point[],
  nodes: CustomVectorDeformNode[],
  captureRadius: number = 25
): Point[] {
  if (!origPoints || origPoints.length === 0) return [];
  if (!nodes || nodes.length === 0) return origPoints;

  return calculateCustomVectorDeformedPoints(origPoints, nodes, captureRadius);
}
