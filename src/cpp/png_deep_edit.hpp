#ifndef ANIMSTUDIO_PNG_DEEP_EDIT_HPP
#define ANIMSTUDIO_PNG_DEEP_EDIT_HPP

#include "types.hpp"
#include <vector>

namespace AnimStudio {

struct SilhouetteResult {
    std::vector<Vec2> contourPoints;
    std::vector<uint8_t> depthMap;
    int width{0};
    int height{0};
};

class PNGDeepEdit {
public:
    static SilhouetteResult extractSilhouetteAndDepth(
        const uint8_t* rgbaPixels,
        int width,
        int height,
        uint8_t alphaThreshold = 20
    );
};

} // namespace AnimStudio

#endif // ANIMSTUDIO_PNG_DEEP_EDIT_HPP
