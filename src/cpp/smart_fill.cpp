#include "smart_fill.hpp"
#include <queue>
#include <cmath>

namespace AnimStudio {

std::vector<uint8_t> SmartFill::floodFillMask(
    const uint8_t* imageData,
    int width,
    int height,
    int startX,
    int startY,
    ColorRGBA targetColor,
    int tolerance
) {
    std::vector<uint8_t> mask(width * height, 0);

    if (startX < 0 || startX >= width || startY < 0 || startY >= height) {
        return mask;
    }

    auto colorMatch = [&](int px, int py) -> bool {
        int idx = (py * width + px) * 4;
        int dr = std::abs(static_cast<int>(imageData[idx]) - targetColor.r);
        int dg = std::abs(static_cast<int>(imageData[idx + 1]) - targetColor.g);
        int db = std::abs(static_cast<int>(imageData[idx + 2]) - targetColor.b);
        int da = std::abs(static_cast<int>(imageData[idx + 3]) - targetColor.a);
        return (dr + dg + db + da) <= (tolerance * 4);
    };

    std::queue<std::pair<int, int>> q;
    q.push({startX, startY});
    mask[startY * width + startX] = 255;

    int dx[4] = {1, -1, 0, 0};
    int dy[4] = {0, 0, 1, -1};

    while (!q.empty()) {
        auto [cx, cy] = q.front();
        q.pop();

        for (int i = 0; i < 4; ++i) {
            int nx = cx + dx[i];
            int ny = cy + dy[i];

            if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                int maskIdx = ny * width + nx;
                if (mask[maskIdx] == 0 && colorMatch(nx, ny)) {
                    mask[maskIdx] = 255;
                    q.push({nx, ny});
                }
            }
        }
    }

    return mask;
}

} // namespace AnimStudio
