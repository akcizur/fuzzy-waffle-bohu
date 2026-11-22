#!/usr/bin/env python3
"""Structural QA for the house OBJ before GitHub Pages deployment."""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJ = ROOT / "house.obj"
TXT = ROOT / "house.txt"
MTL = ROOT / "house.mtl"

EXPECTED = {"vertices": 9455, "uvs": 2795, "normals": 1370, "faces": 6891}
REVEAL_OBJECT_MARKER = "_opening_reveal"


def cross(a, b, c):
    u = tuple(b[i] - a[i] for i in range(3))
    v = tuple(c[i] - a[i] for i in range(3))
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def length(v):
    return math.sqrt(sum(x * x for x in v))


def main():
    lines = OBJ.read_text(encoding="utf-8").splitlines()
    vertices = []
    uvs = []
    normals = []
    faces = []
    object_name = ""
    material = ""
    object_faces = Counter()
    reveal_face_count = 0
    reveal_normal_errors = 0
    degenerate_faces = 0
    invalid_refs = 0
    missing_uv_or_normal = 0

    for line_number, line in enumerate(lines, start=1):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        parts = value.split()
        tag = parts[0]

        if tag == "v":
            if len(parts) < 4:
                raise SystemExit(f"Malformed vertex at line {line_number}")
            vertices.append(tuple(float(x) for x in parts[1:4]))
        elif tag == "vt":
            if len(parts) < 3:
                raise SystemExit(f"Malformed UV at line {line_number}")
            uvs.append(tuple(float(x) for x in parts[1:3]))
        elif tag == "vn":
            if len(parts) < 4:
                raise SystemExit(f"Malformed normal at line {line_number}")
            normals.append(tuple(float(x) for x in parts[1:4]))
        elif tag == "o":
            object_name = " ".join(parts[1:])
        elif tag == "usemtl":
            material = " ".join(parts[1:])
        elif tag == "f":
            refs = []
            for token in parts[1:]:
                fields = token.split("/")
                if len(fields) != 3 or not all(fields):
                    missing_uv_or_normal += 1
                    continue
                try:
                    vi, ti, ni = (int(x) for x in fields)
                except ValueError:
                    invalid_refs += 1
                    continue
                if not (1 <= vi <= len(vertices)):
                    invalid_refs += 1
                if not (1 <= ti <= len(uvs)):
                    invalid_refs += 1
                if not (1 <= ni <= len(normals)):
                    invalid_refs += 1
                refs.append((vi, ti, ni))

            if len(refs) < 3:
                continue

            faces.append((object_name, material, refs))
            object_faces[object_name] += 1
            points = [vertices[ref[0] - 1] for ref in refs]
            area_vector = (0.0, 0.0, 0.0)
            for i in range(1, len(points) - 1):
                area_vector = add(area_vector, cross(points[0], points[i], points[i + 1]))
            area_size = length(area_vector) * 0.5
            if area_size < 1e-9:
                degenerate_faces += 1

            if REVEAL_OBJECT_MARKER in object_name:
                reveal_face_count += 1
                normal = normals[refs[0][2] - 1]
                n_len = length(area_vector)
                r_len = length(normal)
                alignment = sum(area_vector[i] * normal[i] for i in range(3)) / (n_len * r_len)
                if alignment < 0.999:
                    reveal_normal_errors += 1
                if material != "OpeningReveal":
                    raise SystemExit(f"Reveal object has wrong material: {object_name}")

    actual = {
        "vertices": len(vertices),
        "uvs": len(uvs),
        "normals": len(normals),
        "faces": len(faces),
    }
    if actual != EXPECTED:
        raise SystemExit(f"Unexpected OBJ counts: {actual}; expected {EXPECTED}")
    if invalid_refs or missing_uv_or_normal:
        raise SystemExit(f"Invalid OBJ references: {invalid_refs}; missing UV/normal refs: {missing_uv_or_normal}")
    if degenerate_faces:
        raise SystemExit(f"Degenerate faces found: {degenerate_faces}")
    if reveal_face_count != 78 or reveal_normal_errors:
        raise SystemExit(f"Reveal QA failed: {reveal_face_count} faces, {reveal_normal_errors} normal errors")

    floor_face_counts = {
        "apartment_column_floor_01": 350,
        "apartment_column_floor_02": 352,
        "apartment_column_floor_03": 351,
        "apartment_column_floor_04": 341,
        "apartment_column_floor_05": 321,
        "apartment_column_floor_06": 355,
        "apartment_column_floor_07": 343,
        "apartment_column_floor_08": 342,
        "apartment_column_floor_09": 342,
        "apartment_column_floor_10": 332,
        "apartment_column_floor_11": 346,
    }
    for name, expected_count in floor_face_counts.items():
        if object_faces[name] != expected_count:
            raise SystemExit(
                f"{name} has {object_faces[name]} faces; expected {expected_count}"
            )

    reveal_objects = {
        name for name in object_faces if REVEAL_OBJECT_MARKER in name
    }
    if len(reveal_objects) != 21:
        raise SystemExit(f"Expected 21 reveal objects, found {len(reveal_objects)}")
    retained_source_sides = {
        "apartment_column_floor_05_window_opening_reveal": 2,
        "apartment_column_floor_06_window_opening_reveal": 2,
        "apartment_column_floor_06_door_opening_reveal": 2,
    }
    for name in reveal_objects:
        expected_faces = retained_source_sides.get(name, 4)
        if object_faces[name] != expected_faces:
            raise SystemExit(f"{name} has {object_faces[name]} faces; expected {expected_faces}")
    if sum(1 for _, material, _ in faces if material == "OpeningReveal") != 78:
        raise SystemExit("OpeningReveal material face count does not match")

    mtl = MTL.read_text(encoding="utf-8")
    if "newmtl OpeningReveal" not in mtl:
        raise SystemExit("OpeningReveal material is missing from house.mtl")

    obj_text = OBJ.read_text(encoding="utf-8")
    txt_text = TXT.read_text(encoding="utf-8")
    expected_txt = obj_text.replace(
        "# 3ds Max Wavefront OBJ Exporter v0.97b - (c)2007 guruware",
        "# building - (c)2026 5110",
        1,
    )
    if txt_text != expected_txt:
        raise SystemExit("house.txt is not synchronized with house.obj")

    if "# REAL OPENINGS: WINDOW A + BALCONY DOOR THROUGH-WALL CUTS v1" not in obj_text:
        raise SystemExit("Through-wall opening marker is missing")
    if "# GENERATED: REDUNDANT SHELL SURFACES REMOVED v1" not in obj_text:
        raise SystemExit("Redundant shell surface cleanup marker is missing")
    if "# GENERATED: OPENING REVEALS v1" not in obj_text:
        raise SystemExit("Opening reveal marker is missing")

    print(
        "Model QA passed: "
        f"{len(vertices)} vertices, {len(uvs)} UVs, {len(normals)} normals, "
        f"{len(faces)} faces, 11 apartment modules, "
        f"{len(reveal_objects)} reveal objects / {reveal_face_count} quads."
    )


if __name__ == "__main__":
    main()
