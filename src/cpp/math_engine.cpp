#include "math_engine.hpp"
#include <cmath>
#include <algorithm>

namespace AnimStudio {

double MathEngine::interpolateLinear(double a, double b, double t) {
    return a + (b - a) * t;
}

double MathEngine::interpolateEaseIn(double a, double b, double t) {
    double ease = t * t * t;
    return a + (b - a) * ease;
}

double MathEngine::interpolateEaseOut(double a, double b, double t) {
    double f = t - 1.0;
    double ease = f * f * f + 1.0;
    return a + (b - a) * ease;
}

double MathEngine::interpolateEaseInOut(double a, double b, double t) {
    double ease = t < 0.5 ? 4.0 * t * t * t : (t - 1.0) * (2.0 * t - 2.0) * (2.0 * t - 2.0) + 1.0;
    return a + (b - a) * ease;
}

double MathEngine::interpolateElastic(double a, double b, double t) {
    if (t <= 0.0) return a;
    if (t >= 1.0) return b;
    double p = 0.3;
    double s = p / 4.0;
    double ease = std::pow(2.0, -10.0 * t) * std::sin((t - s) * (2.0 * M_PI) / p) + 1.0;
    return a + (b - a) * ease;
}

double MathEngine::interpolateBounce(double a, double b, double t) {
    double ease;
    if (t < (1.0 / 2.75)) {
        ease = 7.5625 * t * t;
    } else if (t < (2.0 / 2.75)) {
        t -= (1.5 / 2.75);
        ease = 7.5625 * t * t + 0.75;
    } else if (t < (2.5 / 2.75)) {
        t -= (2.25 / 2.75);
        ease = 7.5625 * t * t + 0.9375;
    } else {
        t -= (2.625 / 2.75);
        ease = 7.5625 * t * t + 0.984375;
    }
    return a + (b - a) * ease;
}

double MathEngine::interpolateCubicBezier(double a, double b, double p1x, double p1y, double p2x, double p2y, double t) {
    double u = 1.0 - t;
    double tt = t * t;
    double uu = u * u;
    double uuu = uu * u;
    double ttt = tt * t;

    // Cubic bezier parameter calculation for y given t approximation
    double easeY = 3.0 * uu * t * p1y + 3.0 * u * tt * p2y + ttt;
    return a + (b - a) * easeY;
}

Vec2 MathEngine::evaluateCubicBezier(const Vec2& p0, const Vec2& p1, const Vec2& p2, const Vec2& p3, double t) {
    double u = 1.0 - t;
    double tt = t * t;
    double uu = u * u;
    double uuu = uu * u;
    double ttt = tt * t;

    Vec2 p;
    p.x = uuu * p0.x + 3.0 * uu * t * p1.x + 3.0 * u * tt * p2.x + ttt * p3.x;
    p.y = uuu * p0.y + 3.0 * uu * t * p1.y + 3.0 * u * tt * p2.y + ttt * p3.y;
    return p;
}

Vec2 MathEngine::evaluateCatmullRom(const Vec2& p0, const Vec2& p1, const Vec2& p2, const Vec2& p3, double t, double alpha) {
    double t0 = 0.0;
    double t1 = t0 + std::pow((p1 - p0).length(), alpha);
    double t2 = t1 + std::pow((p2 - p1).length(), alpha);
    double t3 = t2 + std::pow((p3 - p2).length(), alpha);

    if (std::abs(t1 - t0) < 1e-6) t1 = t0 + 1.0;
    if (std::abs(t2 - t1) < 1e-6) t2 = t1 + 1.0;
    if (std::abs(t3 - t2) < 1e-6) t3 = t2 + 1.0;

    double t_curr = t1 + t * (t2 - t1);

    Vec2 A1 = p0 * ((t1 - t_curr) / (t1 - t0)) + p1 * ((t_curr - t0) / (t1 - t0));
    Vec2 A2 = p1 * ((t2 - t_curr) / (t2 - t1)) + p2 * ((t_curr - t1) / (t2 - t1));
    Vec2 A3 = p2 * ((t3 - t_curr) / (t3 - t2)) + p3 * ((t_curr - t2) / (t3 - t2));

    Vec2 B1 = A1 * ((t2 - t_curr) / (t2 - t0)) + A2 * ((t_curr - t0) / (t2 - t0));
    Vec2 B2 = A2 * ((t3 - t_curr) / (t3 - t1)) + A3 * ((t_curr - t1) / (t3 - t1));

    Vec2 C = B1 * ((t2 - t_curr) / (t2 - t1)) + B2 * ((t_curr - t1) / (t2 - t1));
    return C;
}

std::vector<double> MathEngine::createIdentityMatrix() {
    return {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    };
}

std::vector<double> MathEngine::createTranslationMatrix(double tx, double ty, double tz) {
    return {
        1, 0, 0, tx,
        0, 1, 0, ty,
        0, 0, 1, tz,
        0, 0, 0, 1
    };
}

std::vector<double> MathEngine::createScaleMatrix(double sx, double sy, double sz) {
    return {
        sx, 0,  0,  0,
        0,  sy, 0,  0,
        0,  0,  sz, 0,
        0,  0,  0,  1
    };
}

std::vector<double> MathEngine::createRotationMatrixXYZ(double rxDeg, double ryDeg, double rzDeg) {
    double rx = rxDeg * M_PI / 180.0;
    double ry = ryDeg * M_PI / 180.0;
    double rz = rzDeg * M_PI / 180.0;

    double cx = std::cos(rx), sx = std::sin(rx);
    double cy = std::cos(ry), sy = std::sin(ry);
    double cz = std::cos(rz), sz = std::sin(rz);

    std::vector<double> mx = {
        1,  0,   0, 0,
        0, cx, -sx, 0,
        0, sx,  cx, 0,
        0,  0,   0, 1
    };

    std::vector<double> my = {
         cy, 0, sy, 0,
          0, 1,  0, 0,
        -sy, 0, cy, 0,
          0, 0,  0, 1
    };

    std::vector<double> mz = {
        cz, -sz, 0, 0,
        sz,  cz, 0, 0,
         0,   0, 1, 0,
         0,   0, 0, 1
    };

    return multiplyMatrices(mz, multiplyMatrices(my, mx));
}

std::vector<double> MathEngine::multiplyMatrices(const std::vector<double>& a, const std::vector<double>& b) {
    std::vector<double> res(16, 0.0);
    for (int r = 0; r < 4; ++r) {
        for (int c = 0; c < 4; ++c) {
            double sum = 0.0;
            for (int k = 0; k < 4; ++k) {
                sum += a[r * 4 + k] * b[k * 4 + c];
            }
            res[r * 4 + c] = sum;
        }
    }
    return res;
}

Vec3 MathEngine::transformPoint(const std::vector<double>& mat, const Vec3& pt) {
    double x = mat[0] * pt.x + mat[1] * pt.y + mat[2] * pt.z + mat[3];
    double y = mat[4] * pt.x + mat[5] * pt.y + mat[6] * pt.z + mat[7];
    double z = mat[8] * pt.x + mat[9] * pt.y + mat[10] * pt.z + mat[11];
    double w = mat[12] * pt.x + mat[13] * pt.y + mat[14] * pt.z + mat[15];

    if (std::abs(w) > 1e-9 && std::abs(w - 1.0) > 1e-9) {
        x /= w;
        y /= w;
        z /= w;
    }
    return Vec3(x, y, z);
}

Vec2 MathEngine::project3Dto2D(const Vec3& pt3d, double focalLength, double canvasWidth, double canvasHeight) {
    double perspectiveScale = focalLength / (focalLength + pt3d.z);
    double x2d = (pt3d.x * perspectiveScale) + (canvasWidth / 2.0);
    double y2d = (pt3d.y * perspectiveScale) + (canvasHeight / 2.0);
    return Vec2(x2d, y2d);
}

} // namespace AnimStudio
