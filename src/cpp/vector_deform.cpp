#include "vector_deform.hpp"
#include <cmath>
#include <algorithm>

namespace AnimStudio {

std::vector<Vec2> VectorDeformer::deformMeshGrid(
    const std::vector<Vec2>& vertices,
    const Vec2& handleStart,
    const Vec2& handleTarget,
    double radius,
    double intensity
) {
    std::vector<Vec2> result;
    result.reserve(vertices.size());

    Vec2 delta = handleTarget - handleStart;

    for (const auto& v : vertices) {
        double dist = (v - handleStart).length();
        if (dist < radius) {
            double factor = (1.0 - (dist / radius));
            // Smooth step falloff (3*f^2 - 2*f^3)
            double smoothFactor = factor * factor * (3.0 - 2.0 * factor) * intensity;
            result.push_back(v + delta * smoothFactor);
        } else {
            result.push_back(v);
        }
    }

    return result;
}

std::vector<Bone> VectorDeformer::solveCCDInverseKinematics(
    std::vector<Bone> bones,
    Vec2 targetPos,
    int maxIterations,
    double tolerance
) {
    if (bones.empty()) return bones;

    for (int iter = 0; iter < maxIterations; ++iter) {
        Vec2 endEffector = bones.back().endPos;
        if ((endEffector - targetPos).length() < tolerance) {
            break;
        }

        for (int i = static_cast<int>(bones.size()) - 1; i >= 0; --i) {
            Vec2 pivot = bones[i].startPos;
            Vec2 curEffector = bones.back().endPos;

            Vec2 toEffector = (curEffector - pivot).normalized();
            Vec2 toTarget = (targetPos - pivot).normalized();

            double cosAngle = toEffector.x * toTarget.x + toEffector.y * toTarget.y;
            double sinAngle = toEffector.x * toTarget.y - toEffector.y * toTarget.x;
            double rotAngle = std::atan2(sinAngle, cosAngle);

            bones[i].angle += rotAngle;

            // Recalculate positions down the chain
            for (size_t j = i; j < bones.size(); ++j) {
                double length = bones[j].length;
                double currentAngle = bones[j].angle;
                Vec2 start = (j == 0) ? bones[0].startPos : bones[j - 1].endPos;
                bones[j].startPos = start;
                bones[j].endPos = Vec2(
                    start.x + std::cos(currentAngle) * length,
                    start.y + std::sin(currentAngle) * length
                );
            }
        }
    }

    return bones;
}

std::vector<Vec2> VectorDeformer::applySkinning(
    const std::vector<Vec2>& originalVertices,
    const std::vector<Bone>& initialBones,
    const std::vector<Bone>& poseBones,
    const std::vector<std::vector<double>>& weights
) {
    std::vector<Vec2> skinned;
    skinned.reserve(originalVertices.size());

    for (size_t vIdx = 0; vIdx < originalVertices.size(); ++vIdx) {
        Vec2 orig = originalVertices[vIdx];
        Vec2 newPos(0.0, 0.0);

        for (size_t bIdx = 0; bIdx < initialBones.size(); ++bIdx) {
            double w = (vIdx < weights.size() && bIdx < weights[vIdx].size()) ? weights[vIdx][bIdx] : 0.0;
            if (w < 1e-4) continue;

            const auto& initBone = initialBones[bIdx];
            const auto& poseBone = poseBones[bIdx];

            // Local coordinates relative to initial bone start
            Vec2 local = orig - initBone.startPos;
            double dAngle = poseBone.angle - initBone.angle;

            double cosA = std::cos(dAngle);
            double sinA = std::sin(dAngle);

            Vec2 rotated(
                local.x * cosA - local.y * sinA,
                local.x * sinA + local.y * cosA
            );

            Vec2 transformed = poseBone.startPos + rotated;
            newPos = newPos + transformed * w;
        }

        skinned.push_back(newPos);
    }

    return skinned;
}

} // namespace AnimStudio
