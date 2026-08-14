#include "png_deep_edit.hpp"
#include <cmath>

namespace AnimStudio {

SilhouetteResult PNGDeepEdit::extractSilhouetteAndDepth(
    const uint8_t* rgbaPixels,
    int width,
    int height,
    uint8_t alphaThreshold
) {
    SilhouetteResult result;
    result.width = width;
    result.height = height;
    result.depthMap.resize(width * height, 0);

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int idx = (y * width + x) * 4;
            uint8_t r = rgbaPixels[idx];
            uint8_t g = rgbaPixels[idx + 1];
            uint8_t b = rgbaPixels[idx + 2];
            uint8_t a = rgbaPixels[idx + 3];

            if (a > alphaThreshold) {
                // Calculate pseudo-depth based on luminance & distance to center
                double luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0;
                double cx = width / 2.0;
                double cy = height / 2.0;
                double dist = std::sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy)) / std::max(cx, cy);
                double depth = (luminance * 0.7 + (1.0 - dist) * 0.3) * 255.0;
                result.depthMap[y * width + x] = static_cast<uint8_t>(std::clamp(depth, 0.0, 255.0));

                // Border contour detection
                bool isBorder = (x == 0 || x == width - 1 || y == 0 || y == height - 1);
                if (!isBorder) {
                    uint8_t aUp = rgbaPixels[((y - 1) * width + x) * 4 + 3];
                    uint8_t aDown = rgbaPixels[((y + 1) * width + x) * 4 + 3];
                    uint8_t aLeft = rgbaPixels[(y * width + (x - 1)) * 4 + 3];
                    uint8_t aRight = rgbaPixels[(y * width + (x + 1)) * 4 + 3];
                    if (aUp <= alphaThreshold || aDown <= alphaThreshold || aLeft <= alphaThreshold || aRight <= alphaThreshold) {
                        isBorder = true;
                    }
                }

                if (isBorder) {
                    result.contourPoints.push_back(Vec2(static_cast<double>(x), static_cast<double>(y)));
                }
            }
        }
    }

    return result;
}

} // namespace AnimStudio
