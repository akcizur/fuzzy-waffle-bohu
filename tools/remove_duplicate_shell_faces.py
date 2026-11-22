#!/usr/bin/env python3
"""Remove apartment polygons already covered by the original house shell.

Run once with:
    python tools/remove_duplicate_shell_faces.py

Verify a cleaned model with:
    python tools/remove_duplicate_shell_faces.py --check

Only a same-material, same-winding, coplanar surface covering at least 99%
of the candidate polygon is considered redundant. The original shell face
is kept; only the repeated apartment copy is removed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJ_PATH = ROOT / "house.obj"
TXT_PATH = ROOT / "house.txt"
MARKER = "# GENERATED: REDUNDANT SHELL SURFACES REMOVED v1"
COVERAGE_THRESHOLD = 0.99

EXPECTED_REMOVALS = {
    "apartment_column_floor_01": 5,
    "apartment_column_floor_02": 3,
    "apartment_column_floor_03": 4,
    "apartment_column_floor_04": 14,
    "apartment_column_floor_05": 34,
    "apartment_column_floor_06": 0,
    "apartment_column_floor_07": 12,
    "apartment_column_floor_08": 13,
    "apartment_column_floor_09": 15,
    "apartment_column_floor_10": 23,
    "apartment_column_floor_11": 9,
}


def _sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def _normal(value):
    length = sum(component * component for component in value) ** 0.5
    if length < 1e-12:
        return (0.0, 0.0, 0.0)
    return tuple(component / length for component in value)


def _bounds(points):
    return tuple(
        (min(point[axis] for point in points), max(point[axis] for point in points))
        for axis in range(3)
    )


def _triangulate_face(face):
    points = face["points"]
    triangles = []
    for index in range(1, len(points) - 1):
        triangle = (points[0], points[index], points[index + 1])
        normal = _normal(_cross(
            _sub(triangle[1], triangle[0]),
            _sub(triangle[2], triangle[0]),
        ))
        if _dot(normal, normal) < 0.5:
            continue
        triangles.append({
            "points": triangle,
            "normal": normal,
            "plane": _dot(normal, triangle[0]),
            "bounds": _bounds(triangle),
            "material": face["material"],
        })
    return triangles


def build_shell_triangles(shell_faces):
    return [
        triangle
        for face in shell_faces
        for triangle in _triangulate_face(face)
    ]


def _bounds_overlap(a, b):
    return all(
        a[axis][0] <= b[axis][1] + 0.001
        and b[axis][0] <= a[axis][1] + 0.001
        for axis in range(3)
    )


def _project(point, axis):
    if axis == 0:
        return (point[1], point[2])
    if axis == 1:
        return (point[0], point[2])
    return (point[0], point[1])


def _cross2(a, b, point):
    return (
        (b[0] - a[0]) * (point[1] - a[1])
        - (b[1] - a[1]) * (point[0] - a[0])
    )


def _polygon_area(points):
    if len(points) < 3:
        return 0.0
    total = 0.0
    for index, point in enumerate(points):
        following = points[(index + 1) % len(points)]
        total += point[0] * following[1] - following[0] * point[1]
    return abs(total) * 0.5


def _clip_triangle(subject, clipper):
    output = list(subject)
    orientation = 1.0 if _cross2(
        clipper[0], clipper[1], clipper[2]
    ) >= 0 else -1.0

    for edge in range(3):
        a = clipper[edge]
        b = clipper[(edge + 1) % 3]
        source = output
        output = []
        if not source:
            break

        for index, point in enumerate(source):
            following = source[(index + 1) % len(source)]
            inside_point = orientation * _cross2(a, b, point) >= -1e-8
            inside_following = orientation * _cross2(a, b, following) >= -1e-8

            def intersection():
                ray = (
                    following[0] - point[0],
                    following[1] - point[1],
                )
                edge_vector = (b[0] - a[0], b[1] - a[1])
                denominator = (
                    ray[0] * edge_vector[1] - ray[1] * edge_vector[0]
                )
                if abs(denominator) < 1e-12:
                    return following
                factor = (
                    (a[0] - point[0]) * edge_vector[1]
                    - (a[1] - point[1]) * edge_vector[0]
                ) / denominator
                return (
                    point[0] + factor * ray[0],
                    point[1] + factor * ray[1],
                )

            if inside_point and inside_following:
                output.append(following)
            elif inside_point and not inside_following:
                output.append(intersection())
            elif not inside_point and inside_following:
                output.extend((intersection(), following))

    return output


def shell_coverage(face, shell_triangles):
    target_triangles = _triangulate_face(face)
    total_area = 0.0
    overlap_area = 0.0

    for target in target_triangles:
        normal = target["normal"]
        axis = max(range(3), key=lambda index: abs(normal[index]))
        target_projected = [
            _project(point, axis) for point in target["points"]
        ]
        total_area += _polygon_area(target_projected)

        for shell in shell_triangles:
            if face["material"] != shell["material"]:
                continue
            if _dot(normal, shell["normal"]) < 0.9999:
                continue
            if not _bounds_overlap(target["bounds"], shell["bounds"]):
                continue
            distance = abs(
                target["plane"] - _dot(normal, shell["points"][0])
            )
            if distance > 0.005:
                continue

            shell_projected = [
                _project(point, axis) for point in shell["points"]
            ]
            overlap_area += _polygon_area(
                _clip_triangle(target_projected, shell_projected)
            )

    return overlap_area / total_area if total_area > 1e-8 else 0.0


def parse_obj(text):
    vertices = []
    faces = []
    object_name = ""
    group_name = "default"
    material = None
    smoothing = "off"

    for line_index, line in enumerate(text.splitlines()):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        parts = value.split()
        tag = parts[0]

        if tag == "v":
            vertices.append(tuple(float(component) for component in parts[1:4]))
        elif tag == "o":
            object_name = " ".join(parts[1:])
        elif tag == "g":
            group_name = " ".join(parts[1:])
        elif tag == "usemtl":
            material = " ".join(parts[1:])
        elif tag == "s":
            smoothing = " ".join(parts[1:])
        elif tag == "f":
            indices = [int(token.split("/")[0]) - 1 for token in parts[1:]]
            if len(indices) < 3 or any(
                index < 0 or index >= len(vertices) for index in indices
            ):
                raise SystemExit(f"Malformed face at OBJ line {line_index + 1}")
            faces.append({
                "line_index": line_index,
                "object": object_name,
                "group": group_name,
                "material": material,
                "smoothing": smoothing,
                "points": [vertices[index] for index in indices],
            })

    return faces


def find_redundant_faces(text):
    faces = parse_obj(text)
    shell_faces = [
        face for face in faces
        if not face["object"].startswith("apartment_column_floor_")
    ]
    shell_triangles = build_shell_triangles(shell_faces)

    redundant = []
    per_floor = Counter()
    for face in faces:
        if not face["object"].startswith("apartment_column_floor_"):
            continue
        if "_opening_reveal" in face["object"]:
            continue
        if shell_coverage(face, shell_triangles) >= COVERAGE_THRESHOLD:
            redundant.append(face["line_index"])
            per_floor[face["object"]] += 1

    return redundant, per_floor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if a redundant shell polygon remains; do not modify files",
    )
    args = parser.parse_args()

    source = OBJ_PATH.read_text(encoding="utf-8")
    redundant, per_floor = find_redundant_faces(source)

    if args.check:
        if redundant:
            detail = ", ".join(
                f"{name}: {per_floor[name]}"
                for name in sorted(per_floor)
            )
            raise SystemExit(
                f"Redundant apartment/shell surfaces remain ({len(redundant)}): {detail}"
            )
        print("Shell overlap QA passed: no redundant coplanar apartment faces.")
        return

    if MARKER in source:
        if redundant:
            raise SystemExit(
                "Cleanup marker exists but duplicate faces remain; inspect the model manually."
            )
        print("Shell cleanup already applied; no redundant surfaces found.")
        return

    observed = {name: per_floor.get(name, 0) for name in EXPECTED_REMOVALS}
    if observed != EXPECTED_REMOVALS or len(redundant) != 130:
        raise SystemExit(
            "Unexpected cleanup candidate set. "
            f"Found {len(redundant)} faces: {observed}. "
            "Expected the reviewed 130-face set; no file was changed."
        )

    lines = source.splitlines()
    remove_set = set(redundant)
    output_lines = [
        line for line_index, line in enumerate(lines)
        if line_index not in remove_set
    ]
    output_lines.insert(1, MARKER)
    output = "\n".join(output_lines) + "\n"

    text_copy = output.replace(
        "# 3ds Max Wavefront OBJ Exporter v0.97b - (c)2007 guruware",
        "# building - (c)2026 5110",
        1,
    )
    OBJ_PATH.write_text(output, encoding="utf-8", newline="\n")
    TXT_PATH.write_text(text_copy, encoding="utf-8", newline="\n")

    print(f"Removed {len(redundant)} redundant shell surfaces from apartment copies.")
    for name in sorted(EXPECTED_REMOVALS):
        print(f"{name}: removed {per_floor[name]} faces")


if __name__ == "__main__":
    main()
