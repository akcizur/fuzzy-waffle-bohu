#!/usr/bin/env python3
"""Compare the repeated apartment geometry against the original sixth-floor source."""
from __future__ import annotations

import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from remove_duplicate_shell_faces import build_shell_triangles, shell_coverage

ROOT = Path(__file__).resolve().parents[1]
CURRENT_OBJ = ROOT / "house.obj"

SOURCE_COMMIT = "544d67f6cbcaa963f1dde9949694e3aa2878af42"
SOURCE_PATH = "house.obj"
FLOOR_LEVELS = [
    5.766, 19.221, 32.051, 44.254, 57.083, 69.912,
    82.741, 95.572, 108.402, 121.231, 134.060, 147.516,
]
SOURCE_FLOOR = 5
EXPECTED_SOURCE_FACES = 357
EXPECTED_REMOVED_INFILL_FACES = 2
EXPECTED_RETAINED_FLOOR_FACES = {
    1: 350, 2: 352, 3: 351, 4: 341, 5: 321, 6: 355,
    7: 343, 8: 342, 9: 342, 10: 332, 11: 346,
}


def parse_obj(text: str):
    vertices = []
    faces = []
    object_name = ""
    group = "default"
    material = None
    smoothing = "off"

    for line_number, line in enumerate(text.splitlines(), start=1):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        if value.startswith("v "):
            parts = value.split()
            if len(parts) < 4:
                raise SystemExit(f"Malformed vertex at line {line_number}")
            vertices.append(tuple(float(x) for x in parts[1:4]))
        elif value.startswith("o "):
            object_name = value[2:].strip()
        elif value.startswith("g "):
            group = value[2:].strip()
        elif value.startswith("usemtl "):
            material = value[7:].strip()
        elif value.startswith("s "):
            smoothing = value[2:].strip()
        elif value.startswith("f "):
            refs = []
            for token in value.split()[1:]:
                fields = token.split("/")
                try:
                    vertex_index = int(fields[0])
                except (ValueError, IndexError):
                    raise SystemExit(f"Bad OBJ face reference at line {line_number}")
                if not 1 <= vertex_index <= len(vertices):
                    raise SystemExit(f"Out-of-range vertex at line {line_number}")
                refs.append(vertex_index)
            if len(refs) < 3:
                raise SystemExit(f"Face with fewer than 3 vertices at line {line_number}")
            faces.append({
                "line": line_number,
                "object": object_name,
                "group": group,
                "material": material,
                "smoothing": smoothing,
                "points": [vertices[index - 1] for index in refs],
            })

    return faces


def find_floor(face) -> int:
    ys = [point[1] for point in face["points"]]
    average = sum(ys) / len(ys)
    for index in range(len(FLOOR_LEVELS) - 1):
        lower, upper = FLOOR_LEVELS[index:index + 2]
        if (
            lower <= average < upper
            and min(ys) >= lower - 0.05
            and max(ys) <= upper + 0.05
        ):
            return index
    return -1


def quantize(value: float) -> int:
    return round(value * 100)


def geometry_signature(face, map_y) -> tuple:
    return tuple(sorted(
        (
            quantize(point[0]),
            quantize(point[2]),
            quantize(map_y(point[1])),
        )
        for point in face["points"]
    ))


def full_signature(face, map_y) -> tuple:
    return (
        face["group"],
        face["material"],
        face["smoothing"],
        geometry_signature(face, map_y),
    )


def is_original_opening_infill(face) -> bool:
    points = face["points"]
    if len(points) != 4:
        return False
    xs = [point[0] for point in points]
    zs = [point[2] for point in points]
    x0, x1 = min(xs), max(xs)
    z_span = max(zs) - min(zs)
    z_average = sum(zs) / 4

    window_a = (
        10.20 <= x0 <= 10.34
        and 16.50 <= x1 <= 16.63
        and z_span < 0.02
        and abs(z_average + 29.3162) < 0.02
    )
    balcony_door = (
        35.50 <= x0 <= 35.70
        and 39.08 <= x1 <= 39.26
        and z_span < 0.02
        and abs(z_average + 19.6465) < 0.02
    )
    return window_a or balcony_door


def load_original_source() -> str:
    result = subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise SystemExit(
            "Cannot read original source commit. "
            "The Pages workflow must checkout full Git history.\n"
            + result.stderr.strip()
        )
    return result.stdout


def main() -> None:
    source_faces = parse_obj(load_original_source())
    current_faces = parse_obj(CURRENT_OBJ.read_text(encoding="utf-8"))

    by_floor = defaultdict(list)
    for face in source_faces:
        floor = find_floor(face)
        if floor >= 0:
            by_floor[floor].append(face)

    if len(by_floor[SOURCE_FLOOR]) < EXPECTED_SOURCE_FACES:
        raise SystemExit("Original sixth-floor source geometry is incomplete.")

    other_signatures = {
        geometry_signature(face, lambda y, lower=FLOOR_LEVELS[floor]: y - lower)
        for floor, records in by_floor.items()
        if floor != SOURCE_FLOOR
        for face in records
    }

    reference = [
        face for face in by_floor[SOURCE_FLOOR]
        if geometry_signature(face, lambda y: y - FLOOR_LEVELS[SOURCE_FLOOR])
        not in other_signatures
    ]
    if len(reference) != EXPECTED_SOURCE_FACES:
        raise SystemExit(
            f"Reference apartment has {len(reference)} faces; "
            f"expected {EXPECTED_SOURCE_FACES}."
        )

    removed = [face for face in reference if is_original_opening_infill(face)]
    if len(removed) != EXPECTED_REMOVED_INFILL_FACES:
        raise SystemExit(
            f"Expected {EXPECTED_REMOVED_INFILL_FACES} removed glass/infill faces, "
            f"found {len(removed)}."
        )

    removed_signatures = {
        full_signature(face, lambda y: y - FLOOR_LEVELS[SOURCE_FLOOR])
        for face in removed
    }

    shell_faces = [
        face for face in current_faces
        if not face["object"].startswith("apartment_column_floor_")
    ]
    shell_triangles = build_shell_triangles(shell_faces)

    results = []
    for floor in range(len(FLOOR_LEVELS) - 1):
        floor_number = floor + 1
        name = f"apartment_column_floor_{floor_number:02d}"
        lower, upper = FLOOR_LEVELS[floor:floor + 2]
        source_lower = FLOOR_LEVELS[SOURCE_FLOOR]
        scale = (upper - lower) / (
            FLOOR_LEVELS[SOURCE_FLOOR + 1] - source_lower
        )

        expected = []
        shell_covered = 0
        for face in reference:
            source_signature = full_signature(
                face, lambda y: y - source_lower
            )
            if source_signature in removed_signatures:
                continue

            mapped_face = dict(face)
            mapped_face["points"] = [
                (x, lower + (y - source_lower) * scale, z)
                for x, y, z in face["points"]
            ]
            if shell_coverage(mapped_face, shell_triangles) >= 0.99:
                shell_covered += 1
            else:
                expected.append(source_signature)

        expected_counts = Counter(expected)
        records = [
            face for face in current_faces
            if face["object"] == name
        ]
        actual = [
            full_signature(
                face,
                lambda y, base=lower, factor=scale:
                    (y - base) / factor,
            )
            for face in records
        ]
        actual_counts = Counter(actual)

        missing = sum((expected_counts - actual_counts).values())
        extra = sum((actual_counts - expected_counts).values())
        expected_count = EXPECTED_RETAINED_FLOOR_FACES[floor_number]
        if (
            len(expected) != expected_count
            or len(records) != expected_count
            or missing
            or extra
        ):
            raise SystemExit(
                f"{name} does not match the source after shell deduplication: "
                f"{len(records)} faces, expected {expected_count}, "
                f"{missing} missing, {extra} extra; "
                f"{shell_covered} shell-covered faces omitted."
            )

        group_counts = Counter(face["group"] for face in records)
        results.append({
            "floor": floor_number,
            "scale": scale,
            "faces": len(records),
            "omitted": shell_covered,
            "groups": group_counts,
        })

    omitted_total = sum(row["omitted"] for row in results)
    if omitted_total != 130:
        raise SystemExit(
            f"Expected 130 shell-covered source faces omitted from the copies, "
            f"found {omitted_total}."
        )

    print(
        f"Apartment comparison passed: {EXPECTED_SOURCE_FACES} original unique faces, "
        f"{EXPECTED_REMOVED_INFILL_FACES} infill faces removed, "
        f"{omitted_total} already-present shell surfaces not duplicated, "
        "remaining geometry matches on all 11 floors."
    )
    print("Floor | retained | shell copy omitted | Y fit | delta | house | kv")
    for row in results:
        scale = row["scale"]
        delta = (scale - 1) * 100
        print(
            f"{row['floor']:>5} | {row['faces']:>8} | {row['omitted']:>18} | "
            f"{scale:>5.4f} | {delta:+6.2f}% | "
            f"{row['groups'].get('house', 0):>5} | {row['groups'].get('kv', 0):>3}"
        )


if __name__ == "__main__":
    main()
