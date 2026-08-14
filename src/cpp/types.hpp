#ifndef ANIMSTUDIO_TYPES_HPP
#define ANIMSTUDIO_TYPES_HPP

#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <memory>
#include <algorithm>

namespace AnimStudio {

struct Vec2 {
    double x{0.0};
    double y{0.0};

    Vec2() = default;
    Vec2(double x_, double y_) : x(x_), y(y_) {}

    Vec2 operator+(const Vec2& o) const { return Vec2(x + o.x, y + o.y); }
    Vec2 operator-(const Vec2& o) const { return Vec2(x - o.x, y - o.y); }
    Vec2 operator*(double s) const { return Vec2(x * s, y * s); }
    Vec2 operator/(double s) const { return Vec2(x / s, y / s); }

    double length() const { return std::sqrt(x * x + y * y); }
    Vec2 normalized() const {
        double l = length();
        if (l < 1e-9) return Vec2(0, 0);
        return Vec2(x / l, y / l);
    }
};

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    Vec3() = default;
    Vec3(double x_, double y_, double z_) : x(x_), y(y_), z(z_) {}

    Vec3 operator+(const Vec3& o) const { return Vec3(x + o.x, y + o.y, z + o.z); }
    Vec3 operator-(const Vec3& o) const { return Vec3(x - o.x, y - o.y, z - o.z); }
    Vec3 operator*(double s) const { return Vec3(x * s, y * s, z * s); }

    double length() const { return std::sqrt(x * x + y * y + z * z); }
    Vec3 normalized() const {
        double l = length();
        if (l < 1e-9) return Vec3(0, 0, 0);
        return Vec3(x / l, y / l, z / l);
    }

    static Vec3 cross(const Vec3& a, const Vec3& b) {
        return Vec3(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        );
    }

    static double dot(const Vec3& a, const Vec3& b) {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }
};

struct ColorRGBA {
    uint8_t r{0};
    uint8_t g{0};
    uint8_t b{0};
    uint8_t a{255};
};

struct PathNodeC {
    Vec2 position;
    Vec2 handleIn;
    Vec2 handleOut;
    bool isCorner{false};
};

struct KeyframeC {
    int frame{0};
    double value{0.0};
    std::string easing{"linear"};
};

struct MeshVertex {
    Vec3 position;
    Vec3 normal;
    Vec2 uv;
    ColorRGBA color;
};

struct MeshTriangle {
    int v0, v1, v2;
};

struct ExtrudedMeshData {
    std::vector<MeshVertex> vertices;
    std::vector<MeshTriangle> triangles;
};

} // namespace AnimStudio

#endif // ANIMSTUDIO_TYPES_HPP
