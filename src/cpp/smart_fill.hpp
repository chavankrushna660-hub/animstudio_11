#ifndef ANIMSTUDIO_SMART_FILL_HPP
#define ANIMSTUDIO_SMART_FILL_HPP

#include "types.hpp"
#include <vector>

namespace AnimStudio {

class SmartFill {
public:
    static std::vector<uint8_t> floodFillMask(
        const uint8_t* imageData,
        int width,
        int height,
        int startX,
        int startY,
        ColorRGBA targetColor,
        int tolerance
    );
};

} // namespace AnimStudio

#endif // ANIMSTUDIO_SMART_FILL_HPP
