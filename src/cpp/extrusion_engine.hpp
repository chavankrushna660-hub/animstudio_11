#ifndef ANIMSTUDIO_EXTRUSION_ENGINE_HPP
#define ANIMSTUDIO_EXTRUSION_ENGINE_HPP

#include "types.hpp"
#include <vector>

namespace AnimStudio {

class ExtrusionEngine {
public:
    static ExtrudedMeshData extrudePolygon(
        const std::vector<Vec2>& polygon2D,
        double depth,
        double bevelSize = 0.0,
        int bevelSegments = 1
    );

private:
    static std::vector<MeshTriangle> triangulateConvexPolygon(int startIdx, int count);
};

} // namespace AnimStudio

#endif // ANIMSTUDIO_EXTRUSION_ENGINE_HPP
