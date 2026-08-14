#include "extrusion_engine.hpp"
#include <cmath>

namespace AnimStudio {

ExtrudedMeshData ExtrusionEngine::extrudePolygon(
    const std::vector<Vec2>& polygon2D,
    double depth,
    double bevelSize,
    int bevelSegments
) {
    ExtrudedMeshData mesh;
    if (polygon2D.size() < 3) return mesh;

    size_t n = polygon2D.size();
    double halfDepth = depth / 2.0;

    // Front Cap Vertices (z = +halfDepth)
    for (size_t i = 0; i < n; ++i) {
        MeshVertex v;
        v.position = Vec3(polygon2D[i].x, polygon2D[i].y, halfDepth);
        v.normal = Vec3(0, 0, 1);
        v.uv = Vec2(polygon2D[i].x, polygon2D[i].y);
        v.color = {220, 220, 240, 255};
        mesh.vertices.push_back(v);
    }

    // Back Cap Vertices (z = -halfDepth)
    for (size_t i = 0; i < n; ++i) {
        MeshVertex v;
        v.position = Vec3(polygon2D[i].x, polygon2D[i].y, -halfDepth);
        v.normal = Vec3(0, 0, -1);
        v.uv = Vec2(polygon2D[i].x, polygon2D[i].y);
        v.color = {160, 160, 180, 255};
        mesh.vertices.push_back(v);
    }

    // Front Cap Triangles
    for (size_t i = 1; i < n - 1; ++i) {
        mesh.triangles.push_back({0, static_cast<int>(i), static_cast<int>(i + 1)});
    }

    // Back Cap Triangles (reverse winding)
    int backOffset = static_cast<int>(n);
    for (size_t i = 1; i < n - 1; ++i) {
        mesh.triangles.push_back({backOffset, backOffset + static_cast<int>(i + 1), backOffset + static_cast<int>(i)});
    }

    // Side Walls
    for (size_t i = 0; i < n; ++i) {
        size_t nextIdx = (i + 1) % n;

        Vec2 p1 = polygon2D[i];
        Vec2 p2 = polygon2D[nextIdx];
        Vec2 edge = p2 - p1;
        Vec3 sideNormal = Vec3::cross(Vec3(edge.x, edge.y, 0), Vec3(0, 0, 1)).normalized();

        int v0_idx = static_cast<int>(mesh.vertices.size());
        MeshVertex v0{Vec3(p1.x, p1.y, halfDepth), sideNormal, Vec2(0, 0), {180, 180, 200, 255}};
        MeshVertex v1{Vec3(p2.x, p2.y, halfDepth), sideNormal, Vec2(1, 0), {180, 180, 200, 255}};
        MeshVertex v2{Vec3(p2.x, p2.y, -halfDepth), sideNormal, Vec2(1, 1), {120, 120, 140, 255}};
        MeshVertex v3{Vec3(p1.x, p1.y, -halfDepth), sideNormal, Vec2(0, 1), {120, 120, 140, 255}};

        mesh.vertices.push_back(v0);
        mesh.vertices.push_back(v1);
        mesh.vertices.push_back(v2);
        mesh.vertices.push_back(v3);

        mesh.triangles.push_back({v0_idx, v0_idx + 1, v0_idx + 2});
        mesh.triangles.push_back({v0_idx, v0_idx + 2, v0_idx + 3});
    }

    return mesh;
}

} // namespace AnimStudio
