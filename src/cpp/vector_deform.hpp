#ifndef ANIMSTUDIO_VECTOR_DEFORM_HPP
#define ANIMSTUDIO_VECTOR_DEFORM_HPP

#include "types.hpp"
#include <vector>

namespace AnimStudio {

struct Bone {
    int id;
    std::string name;
    Vec2 startPos;
    Vec2 endPos;
    double length;
    double angle;
    int parentId{-1};
};

class VectorDeformer {
public:
    static std::vector<Vec2> deformMeshGrid(
        const std::vector<Vec2>& vertices,
        const Vec2& handleStart,
        const Vec2& handleTarget,
        double radius,
        double intensity
    );

    static std::vector<Bone> solveCCDInverseKinematics(
        std::vector<Bone> bones,
        Vec2 targetPos,
        int maxIterations = 10,
        double tolerance = 1e-3
    );

    static std::vector<Vec2> applySkinning(
        const std::vector<Vec2>& originalVertices,
        const std::vector<Bone>& initialBones,
        const std::vector<Bone>& poseBones,
        const std::vector<std::vector<double>>& weights
    );
};

} // namespace AnimStudio

#endif // ANIMSTUDIO_VECTOR_DEFORM_HPP
