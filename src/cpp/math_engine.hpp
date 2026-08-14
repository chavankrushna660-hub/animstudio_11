#ifndef ANIMSTUDIO_MATH_ENGINE_HPP
#define ANIMSTUDIO_MATH_ENGINE_HPP

#include "types.hpp"
#include <vector>
#include <string>

namespace AnimStudio {

class MathEngine {
public:
    // Interpolation & Easing
    static double interpolateLinear(double a, double b, double t);
    static double interpolateEaseIn(double a, double b, double t);
    static double interpolateEaseOut(double a, double b, double t);
    static double interpolateEaseInOut(double a, double b, double t);
    static double interpolateElastic(double a, double b, double t);
    static double interpolateBounce(double a, double b, double t);
    static double interpolateCubicBezier(double a, double b, double p1x, double p1y, double p2x, double p2y, double t);

    // Spline computations
    static Vec2 evaluateCubicBezier(const Vec2& p0, const Vec2& p1, const Vec2& p2, const Vec2& p3, double t);
    static Vec2 evaluateCatmullRom(const Vec2& p0, const Vec2& p1, const Vec2& p2, const Vec2& p3, double t, double alpha = 0.5);

    // 3D Transformations
    static std::vector<double> createIdentityMatrix();
    static std::vector<double> createTranslationMatrix(double tx, double ty, double tz);
    static std::vector<double> createScaleMatrix(double sx, double sy, double sz);
    static std::vector<double> createRotationMatrixXYZ(double rxDeg, double ryDeg, double rzDeg);
    static std::vector<double> multiplyMatrices(const std::vector<double>& a, const std::vector<double>& b);
    static Vec3 transformPoint(const std::vector<double>& mat, const Vec3& pt);
    static Vec2 project3Dto2D(const Vec3& pt3d, double focalLength, double canvasWidth, double canvasHeight);
};

} // namespace AnimStudio

#endif // ANIMSTUDIO_MATH_ENGINE_HPP
