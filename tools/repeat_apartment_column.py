#!/usr/bin/env python3
"""Repeat the reference apartment through all storeys of house.obj.

Run once on the untouched source model:
    python tools/repeat_apartment_column.py

The script edits house.obj and synchronizes house.txt. It intentionally refuses
to run on an already-generated model, preventing accidental duplicate geometry.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJ_PATH = ROOT / "house.obj"
TXT_PATH = ROOT / "house.txt"

FLOOR_LEVELS = [
    5.766, 19.221, 32.051, 44.254, 57.083, 69.912,
    82.741, 95.572, 108.402, 121.231, 134.060, 147.516,
]
SOURCE_FLOOR = 5  # sixth floor
MARKER = "# GENERATED: APARTMENT COLUMN REPEAT v1"


def parse_obj(text: str):
    lines = text.splitlines()
    vertices = []
    faces = []
    group = "default"
    material = None
    smoothing = "off"
    last_vertex_line = -1

    for line_index, line in enumerate(lines):
        value = line.strip()
        if value.startswith("v "):
            vertices.append(tuple(float(x) for x in value.split()[1:4]))
            last_vertex_line = line_index
        elif value.startswith("g "):
            group = value[2:].strip()
        elif value.startswith("usemtl "):
            material = value[7:].strip()
        elif value.startswith("s "):
            smoothing = value[2:].strip()
        elif value.startswith("f "):
            tokens = value.split()[1:]
            faces.append({
                "line_index": line_index,
                "tokens": tokens,
                "ids": [int(token.split("/")[0]) for token in tokens],
                "group": group,
                "material": material,
                "smoothing": smoothing,
            })

    return lines, vertices, faces, last_vertex_line


def quantize(value: float) -> int:
    # Python round is ties-to-even; multiplying first matches the source
    # export's 0.01-unit comparison grid.
    return round(value * 100)


def signature(face, vertices, floor_base):
    points = [vertices[index - 1] for index in face["ids"]]
    return tuple(sorted(
        (quantize(x), quantize(z), quantize(y - floor_base))
        for x, y, z in points
    ))


def find_floor(y: float) -> int:
    for index in range(len(FLOOR_LEVELS) - 1):
        if FLOOR_LEVELS[index] <= y < FLOOR_LEVELS[index + 1]:
            return index
    return -1


def main() -> None:
    source = OBJ_PATH.read_text(encoding="utf-8")
    if MARKER in source:
        raise SystemExit("Generated apartment geometry already exists; restore the clean source before rerunning.")

    lines, vertices, faces, last_vertex_line = parse_obj(source)
    by_floor = defaultdict(list)

    for face in faces:
        points = [vertices[index - 1] for index in face["ids"]]
        ys = [point[1] for point in points]
        floor = find_floor(sum(ys) / len(ys))
        if floor < 0:
            continue

        lower, upper = FLOOR_LEVELS[floor:floor + 2]
        if min(ys) < lower - 0.05 or max(ys) > upper + 0.05:
            continue

        face["floor"] = floor
        face["signature"] = signature(face, vertices, lower)
        by_floor[floor].append(face)

    other_signatures = {
        face["signature"]
        for floor, records in by_floor.items()
        if floor != SOURCE_FLOOR
        for face in records
    }
    apartment = [
        face for face in by_floor[SOURCE_FLOOR]
        if face["signature"] not in other_signatures
    ]

    if len(apartment) != 357:
        raise SystemExit(
            f"Unexpected reference apartment size: {len(apartment)} faces; expected 357."
        )

    moved_lines = {face["line_index"] for face in apartment}
    used_ids = sorted({index for face in apartment for index in face["ids"]})
    extra_vertices = []
    appended = [
        "",
        MARKER,
        "# Reference: original sixth-floor apartment; unique interior geometry only.",
        "# Repeated across all 11 storeys; Y is fitted to each measured floor height.",
    ]

    for floor in range(len(FLOOR_LEVELS) - 1):
        lower, upper = FLOOR_LEVELS[floor:floor + 2]
        source_lower, source_upper = FLOOR_LEVELS[SOURCE_FLOOR:SOURCE_FLOOR + 2]
        y_scale = (upper - lower) / (source_upper - source_lower)
        vertex_map = {}

        if floor == SOURCE_FLOOR:
            vertex_map = {index: index for index in used_ids}
        else:
            for old_index in used_ids:
                x, y, z = vertices[old_index - 1]
                new_index = len(vertices) + len(extra_vertices) + 1
                vertex_map[old_index] = new_index
                new_y = lower + (y - source_lower) * y_scale
                extra_vertices.append(f"v {x:.6f} {new_y:.6f} {z:.6f}")

        appended.extend(["", f"o apartment_column_floor_{floor + 1:02d}"])
        previous_state = None

        for face in apartment:
            state = (face["group"], face["material"], face["smoothing"])
            if state != previous_state:
                group_name, material_name, smoothing = state
                appended.append(f"g {group_name}")
                if material_name:
                    appended.append(f"usemtl {material_name}")
                if smoothing:
                    appended.append(f"s {smoothing}")
                previous_state = state

            tokens = []
            for token in face["tokens"]:
                parts = token.split("/")
                parts[0] = str(vertex_map[int(parts[0])])
                tokens.append("/".join(parts))
            appended.append("f " + " ".join(tokens))

    kept_lines = [line for index, line in enumerate(lines) if index not in moved_lines]
    output_lines = (
        kept_lines[:last_vertex_line + 1]
        + extra_vertices
        + kept_lines[last_vertex_line + 1:]
        + appended
    )
    output = "\n".join(output_lines) + "\n"

    # Validate the generated result before replacing either source file.
    _, final_vertices, final_faces, _ = parse_obj(output)
    if len(final_vertices) != 8732 or len(final_faces) != 6859:
        raise SystemExit(
            f"Validation failed: {len(final_vertices)} vertices, {len(final_faces)} faces."
        )
    if any(index < 1 or index > len(final_vertices)
           for face in final_faces for index in face["ids"]):
        raise SystemExit("Generated OBJ contains an out-of-range vertex index.")

    original_txt = TXT_PATH.read_text(encoding="utf-8")
    if MARKER in original_txt:
        raise SystemExit("house.txt already contains generated apartment geometry.")

    text_output = output.replace(
        "# 3ds Max Wavefront OBJ Exporter v0.97b - (c)2007 guruware",
        "# building - (c)2026 5110",
        1,
    )

    OBJ_PATH.write_text(output, encoding="utf-8", newline="\n")
    TXT_PATH.write_text(text_output, encoding="utf-8", newline="\n")
    print("Apartment column generated: 11 floors × 357 faces.")
    print(f"Final geometry: {len(final_vertices)} vertices, {len(final_faces)} polygons.")


if __name__ == "__main__":
    main()
