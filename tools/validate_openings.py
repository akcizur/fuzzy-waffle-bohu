#!/usr/bin/env python3
"""Check that every designated exterior opening is clear through its wall depth.

The test uses the measured opening polygons from add_opening_reveals.py and
checks the top-floor balcony door from its original apartment-module boundary.
Reveal side faces are excluded intentionally: they bound the opening rather
than obstruct its interior.
"""
from __future__ import annotations

from pathlib import Path

from add_opening_reveals import REVEALS

ROOT = Path(__file__).resolve().parents[1]
OBJ_PATH = ROOT / "house.obj"
GRID_STEPS = 12
RAY_EPSILON = 0.02

# The original OBJ contains the 11th-floor door opening in the apartment
# module, but no matching outer shell panel. Its two wall-depth planes are
# retained from the source model, so this is a measured, not invented, extent.
TOP_FLOOR_DOOR = {
    "floor": 11,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7433,
    "points": [
        [35.582, 139.1002],
        [39.1602, 135.6153],
        [39.1602, 145.8706],
        [35.582, 145.8706],
    ],
}


def parse_model(text: str):
    vertices: list[tuple[float, float, float]] = []
    triangles = []
    object_name = ""
    material = ""

    for line_number, line in enumerate(text.splitlines(), start=1):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        parts = value.split()
        tag = parts[0]

        if tag == "v":
            if len(parts) < 4:
                raise SystemExit(f"Malformed vertex at line {line_number}")
            vertices.append(tuple(float(x) for x in parts[1:4]))
        elif tag == "o":
            object_name = " ".join(parts[1:])
        elif tag == "usemtl":
            material = " ".join(parts[1:])
        elif tag == "f":
            ids = []
            for token in parts[1:]:
                fields = token.split("/")
                try:
                    index = int(fields[0])
                except (ValueError, IndexError):
                    raise SystemExit(f"Malformed face index at line {line_number}")
                if not 1 <= index <= len(vertices):
                    raise SystemExit(f"Out-of-range vertex at line {line_number}")
                ids.append(index - 1)
            if len(ids) < 3:
                raise SystemExit(f"Face with fewer than 3 vertices at line {line_number}")

            if material == "OpeningReveal" or "_opening_reveal" in object_name:
                continue

            points = [vertices[index] for index in ids]
            # Cache each triangle with its spatial bounds to keep ray checks cheap.
            for index in range(1, len(points) - 1):
                triangle = (points[0], points[index], points[index + 1])
                bounds = tuple(
                    (min(point[axis] for point in triangle), max(point[axis] for point in triangle))
                    for axis in range(3)
                )
                triangles.append((object_name, line_number, triangle, bounds))

    return triangles


def point_in_polygon(polygon, x: float, y: float) -> bool:
    inside = False
    for index, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[(index + 1) % len(polygon)]
        if (y1 > y) != (y2 > y):
            crossing = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing:
                inside = not inside
    return inside


def ray_triangle_distance(origin, triangle):
    """Return the positive +Z ray distance to a triangle, if it intersects."""
    direction = (0.0, 0.0, 1.0)
    p0, p1, p2 = triangle
    edge1 = tuple(p1[i] - p0[i] for i in range(3))
    edge2 = tuple(p2[i] - p0[i] for i in range(3))
    h = (
        direction[1] * edge2[2] - direction[2] * edge2[1],
        direction[2] * edge2[0] - direction[0] * edge2[2],
        direction[0] * edge2[1] - direction[1] * edge2[0],
    )
    determinant = sum(edge1[i] * h[i] for i in range(3))
    if abs(determinant) < 1e-10:
        return None

    inverse = 1.0 / determinant
    offset = tuple(origin[i] - p0[i] for i in range(3))
    u = inverse * sum(offset[i] * h[i] for i in range(3))
    if u < -1e-8 or u > 1.0 + 1e-8:
        return None

    q = (
        offset[1] * edge1[2] - offset[2] * edge1[1],
        offset[2] * edge1[0] - offset[0] * edge1[2],
        offset[0] * edge1[1] - offset[1] * edge1[0],
    )
    v = inverse * q[2]
    if v < -1e-8 or u + v > 1.0 + 1e-8:
        return None

    distance = inverse * sum(edge2[i] * q[i] for i in range(3))
    return distance if distance > 1e-7 else None


def check_opening(triangles, opening):
    polygon = [tuple(point) for point in opening["points"]]
    min_x = min(point[0] for point in polygon)
    max_x = max(point[0] for point in polygon)
    min_y = min(point[1] for point in polygon)
    max_y = max(point[1] for point in polygon)
    wall_low = min(opening["inner_z"], opening["outer_z"])
    wall_high = max(opening["inner_z"], opening["outer_z"])
    ray_start = wall_low - RAY_EPSILON
    ray_end = wall_high + RAY_EPSILON

    candidates = [
        item for item in triangles
        if item[3][0][0] <= max_x and item[3][0][1] >= min_x
        and item[3][1][0] <= max_y and item[3][1][1] >= min_y
        and item[3][2][0] <= ray_end and item[3][2][1] >= ray_start
    ]

    tested = 0
    for y_index in range(1, GRID_STEPS + 1):
        y = min_y + (max_y - min_y) * y_index / (GRID_STEPS + 1)
        for x_index in range(1, GRID_STEPS + 1):
            x = min_x + (max_x - min_x) * x_index / (GRID_STEPS + 1)
            if not point_in_polygon(polygon, x, y):
                continue
            tested += 1
            origin = (x, y, ray_start)
            for object_name, line_number, triangle, bounds in candidates:
                if not (bounds[0][0] <= x <= bounds[0][1]):
                    continue
                if not (bounds[1][0] <= y <= bounds[1][1]):
                    continue
                distance = ray_triangle_distance(origin, triangle)
                if distance is None:
                    continue
                hit_z = ray_start + distance
                if hit_z <= ray_end + 1e-8:
                    raise SystemExit(
                        f"Blocked opening: floor {opening['floor']:02d} {opening['kind']}, "
                        f"sample ({x:.4f}, {y:.4f}), hit z={hit_z:.4f} "
                        f"in object {object_name!r}, OBJ line {line_number}."
                    )

    if tested < 20:
        raise SystemExit(
            f"Insufficient interior samples for floor {opening['floor']:02d} {opening['kind']}: {tested}."
        )
    return tested


def main() -> None:
    openings = [dict(item) for item in REVEALS] + [TOP_FLOOR_DOOR]
    keys = [(item["floor"], item["kind"]) for item in openings]
    if len(openings) != 22 or len(set(keys)) != 22:
        raise SystemExit("Expected exactly one window and one door opening on each of 11 floors.")

    counts = {kind: sum(item["kind"] == kind for item in openings) for kind in ("window", "door")}
    if counts != {"window": 11, "door": 11}:
        raise SystemExit(f"Unexpected opening distribution: {counts}")

    triangles = parse_model(OBJ_PATH.read_text(encoding="utf-8"))
    tested_samples = 0
    for opening in openings:
        count = check_opening(triangles, opening)
        tested_samples += count
        print(f"Floor {opening['floor']:02d} {opening['kind']}: {count} clear interior samples")

    print(
        f"Opening QA passed: 22 clear through-wall openings, "
        f"{tested_samples} interior ray samples, no obstructing faces."
    )


if __name__ == "__main__":
    main()
