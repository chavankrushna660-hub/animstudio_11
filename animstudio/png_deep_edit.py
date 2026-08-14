"""
PNG Deep Edit Processing Engine for AnimStudio 7.
Performs background removal, threshold alpha masks, color replacement, and edge detection.
"""

from typing import List, Tuple, Optional


class PNGDeepEditProcessor:
    @staticmethod
    def process_threshold_alpha(pixels: List[List[Tuple[int, int, int, int]]], threshold: int = 128) -> List[List[Tuple[int, int, int, int]]]:
        """Applies luminance thresholding to convert near-white/light pixels to transparent."""
        height = len(pixels)
        if height == 0:
            return pixels
        width = len(pixels[0])

        processed = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b, a = pixels[y][x]
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                if luminance >= threshold:
                    row.append((r, g, b, 0))  # Transparent
                else:
                    row.append((r, g, b, a))
            processed.append(row)
        return processed

    @staticmethod
    def replace_color(pixels: List[List[Tuple[int, int, int, int]]], target_rgb: Tuple[int, int, int], new_rgb: Tuple[int, int, int], tolerance: int = 30) -> List[List[Tuple[int, int, int, int]]]:
        """Replaces matching RGB colors within tolerance with new RGB values."""
        height = len(pixels)
        if height == 0:
            return pixels
        width = len(pixels[0])

        tr, tg, tb = target_rgb
        nr, ng, nb = new_rgb

        processed = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b, a = pixels[y][x]
                if abs(r - tr) <= tolerance and abs(g - tg) <= tolerance and abs(b - tb) <= tolerance:
                    row.append((nr, ng, nb, a))
                else:
                    row.append((r, g, b, a))
            processed.append(row)
        return processed
