"""
Smart Fill and Flood-Fill Engine for AnimStudio 7.
Computes region fills, encloses open vector paths, and generates fill polygon shapes.
"""

from typing import List, Tuple, Set
from .types import Point, VectorObject


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return (0, 0, 0)


def smart_flood_fill(image_data: List[List[Tuple[int, int, int, int]]], start_x: int, start_y: int, fill_color: Tuple[int, int, int, int], tolerance: int = 32) -> Set[Tuple[int, int]]:
    """Performs 4-way BFS flood fill algorithm on a 2D pixel buffer with color tolerance."""
    height = len(image_data)
    if height == 0:
        return set()
    width = len(image_data[0])

    if start_x < 0 or start_x >= width or start_y < 0 or start_y >= height:
        return set()

    target_color = image_data[start_y][start_x]
    
    def color_match(c1, c2):
        return sum(abs(a - b) for a, b in zip(c1, c2)) <= tolerance * 4

    visited = set()
    queue = [(start_x, start_y)]
    filled_pixels = set()

    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited:
            continue
        visited.add((x, y))

        if color_match(image_data[y][x], target_color):
            filled_pixels.add((x, y))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    queue.append((nx, ny))

    return filled_pixels


def close_path_for_fill(points: List[Point]) -> List[Point]:
    """Ensures a vector path forms a closed polygon for fill rendering."""
    if not points:
        return []
    res = list(points)
    if res[0].x != res[-1].x or res[0].y != res[-1].y:
        res.append(Point(x=res[0].x, y=res[0].y, z=res[0].z, color=res[0].color, thickness=res[0].thickness))
    return res
