#include "math_engine.hpp"
#include "vector_deform.hpp"
#include "extrusion_engine.hpp"
#include "smart_fill.hpp"
#include "png_deep_edit.hpp"
#include <iostream>
#include <sstream>
#include <string>

using namespace AnimStudio;

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << R"({"status":"ok","engine":"AnimStudio High Performance C++ Core v2.0","commands":["interpolate","catmull_rom","deform_mesh","solve_ik","extrude_3d"]})" << std::endl;
        return 0;
    }

    std::string command = argv[1];

    if (command == "interpolate") {
        // Example: animstudio_cpp_engine interpolate 0.0 100.0 0.5 easeInOut
        if (argc < 6) {
            std::cout << R"({"error":"Missing arguments for interpolate"})" << std::endl;
            return 1;
        }
        double startVal = std::stod(argv[2]);
        double endVal = std::stod(argv[3]);
        double progress = std::stod(argv[4]);
        std::string mode = argv[5];

        double result = startVal;
        if (mode == "linear") result = MathEngine::interpolateLinear(startVal, endVal, progress);
        else if (mode == "easeIn") result = MathEngine::interpolateEaseIn(startVal, endVal, progress);
        else if (mode == "easeOut") result = MathEngine::interpolateEaseOut(startVal, endVal, progress);
        else if (mode == "easeInOut") result = MathEngine::interpolateEaseInOut(startVal, endVal, progress);
        else if (mode == "elastic") result = MathEngine::interpolateElastic(startVal, endVal, progress);
        else if (mode == "bounce") result = MathEngine::interpolateBounce(startVal, endVal, progress);
        else result = MathEngine::interpolateLinear(startVal, endVal, progress);

        std::cout << R"({"status":"success","value":)" << result << R"(})" << std::endl;
        return 0;
    }
    
    if (command == "extrude_3d") {
        // Extrude a default square polygon
        std::vector<Vec2> polygon = { Vec2(0,0), Vec2(100,0), Vec2(100,100), Vec2(0,100) };
        double depth = argc > 2 ? std::stod(argv[2]) : 50.0;
        ExtrudedMeshData mesh = ExtrusionEngine::extrudePolygon(polygon, depth);

        std::cout << R"({"status":"success","vertices":)" << mesh.vertices.size() << R"(,"triangles":)" << mesh.triangles.size() << R"(})" << std::endl;
        return 0;
    }

    std::cout << R"({"status":"unknown_command"})" << std::endl;
    return 0;
}
