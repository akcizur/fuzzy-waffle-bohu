#!/usr/bin/env python3
"""Add source-measured reveal surfaces to the already-cut house OBJ.

Run after the apartment column and through-wall openings have been generated:
    python tools/add_opening_reveals.py

The script is idempotent. It does not invent wall depth for the top-floor door,
because the source model contains no matching backing wall plane there.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJ_PATH = ROOT / "house.obj"
TXT_PATH = ROOT / "house.txt"
MARKER = "# GENERATED: OPENING REVEALS v1"

REVEALS = [
  {
    "floor": 1,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.156398,
    "points": [
      [
        10.27,
        17.575125
      ],
      [
        10.27,
        10.819412
      ],
      [
        16.5755,
        10.819412
      ],
      [
        16.5755,
        17.575125
      ]
    ]
  },
  {
    "floor": 1,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -19.9771,
    "points": [
      [
        35.582,
        10.805673
      ],
      [
        39.1602,
        7.321154
      ],
      [
        39.1602,
        17.575754
      ],
      [
        35.582,
        17.575754
      ]
    ]
  },
  {
    "floor": 2,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1582449,
    "points": [
      [
        10.27,
        30.481578
      ],
      [
        10.27,
        24.039676
      ],
      [
        16.5755,
        24.039676
      ],
      [
        16.5755,
        30.481578
      ]
    ]
  },
  {
    "floor": 2,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7400006,
    "points": [
      [
        35.582,
        24.026575
      ],
      [
        39.1602,
        20.703916
      ],
      [
        39.1602,
        30.482178
      ],
      [
        35.582,
        30.482178
      ]
    ]
  },
  {
    "floor": 3,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1582,
    "points": [
      [
        10.27,
        42.761275
      ],
      [
        10.27,
        36.634188
      ],
      [
        16.5755,
        36.634188
      ],
      [
        16.5755,
        42.761275
      ]
    ]
  },
  {
    "floor": 3,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.74,
    "points": [
      [
        35.582,
        36.621727
      ],
      [
        39.1602,
        33.461446
      ],
      [
        39.1602,
        42.761846
      ],
      [
        35.582,
        42.761846
      ]
    ]
  },
  {
    "floor": 4,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1594,
    "points": [
      [
        10.27,
        55.5137
      ],
      [
        10.27,
        49.0723
      ],
      [
        16.5755,
        49.0723
      ],
      [
        16.5755,
        55.5137
      ]
    ]
  },
  {
    "floor": 4,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7412,
    "points": [
      [
        35.582,
        49.0592
      ],
      [
        39.1602,
        45.7368
      ],
      [
        39.1602,
        55.5143
      ],
      [
        35.582,
        55.5143
      ]
    ]
  },
  {
    "floor": 5,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1607,
    "points": [
      [
        10.27,
        68.3427
      ],
      [
        10.27,
        61.9013
      ],
      [
        16.5755,
        61.9013
      ],
      [
        16.5755,
        68.3427
      ]
    ]
  },
  {
    "floor": 5,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7425,
    "points": [
      [
        35.582,
        61.8882
      ],
      [
        39.1602,
        58.5658
      ],
      [
        39.1602,
        68.3433
      ],
      [
        35.582,
        68.3433
      ]
    ]
  },
  {
    "floor": 6,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1615,
    "points": [
      [
        10.27,
        81.1717
      ],
      [
        10.27,
        74.7303
      ],
      [
        16.5755,
        74.7303
      ],
      [
        16.5755,
        81.1717
      ]
    ]
  },
  {
    "floor": 6,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7433,
    "points": [
      [
        35.582,
        74.7172
      ],
      [
        39.1602,
        71.3948
      ],
      [
        39.1602,
        81.1723
      ],
      [
        35.582,
        81.1723
      ]
    ]
  },
  {
    "floor": 7,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1561,
    "points": [
      [
        10.27,
        94.002455
      ],
      [
        10.27,
        87.560051
      ],
      [
        16.5755,
        87.560051
      ],
      [
        16.5755,
        94.002455
      ]
    ]
  },
  {
    "floor": 7,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7379,
    "points": [
      [
        35.582,
        87.546949
      ],
      [
        39.1602,
        84.224031
      ],
      [
        39.1602,
        94.003055
      ],
      [
        35.582,
        94.003055
      ]
    ]
  },
  {
    "floor": 8,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1573,
    "points": [
      [
        10.27,
        106.832578
      ],
      [
        10.27,
        100.390676
      ],
      [
        16.5755,
        100.390676
      ],
      [
        16.5755,
        106.832578
      ]
    ]
  },
  {
    "floor": 8,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7391,
    "points": [
      [
        35.582,
        100.377575
      ],
      [
        39.1602,
        97.054916
      ],
      [
        39.1602,
        106.833178
      ],
      [
        35.582,
        106.833178
      ]
    ]
  },
  {
    "floor": 9,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1586,
    "points": [
      [
        10.27,
        119.6617
      ],
      [
        10.27,
        113.2203
      ],
      [
        16.5755,
        113.2203
      ],
      [
        16.5755,
        119.6617
      ]
    ]
  },
  {
    "floor": 9,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7404,
    "points": [
      [
        35.582,
        113.2072
      ],
      [
        39.1602,
        109.8848
      ],
      [
        39.1602,
        119.6623
      ],
      [
        35.582,
        119.6623
      ]
    ]
  },
  {
    "floor": 10,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1598,
    "points": [
      [
        10.27,
        132.4907
      ],
      [
        10.27,
        126.0493
      ],
      [
        16.5755,
        126.0493
      ],
      [
        16.5755,
        132.4907
      ]
    ]
  },
  {
    "floor": 10,
    "kind": "door",
    "inner_z": -19.6465,
    "outer_z": -20.7416,
    "points": [
      [
        35.582,
        126.0362
      ],
      [
        39.1602,
        122.7138
      ],
      [
        39.1602,
        132.4913
      ],
      [
        35.582,
        132.4913
      ]
    ]
  },
  {
    "floor": 11,
    "kind": "window",
    "inner_z": -29.3162,
    "outer_z": -30.1558263,
    "points": [
      [
        10.27,
        145.870003
      ],
      [
        10.27,
        139.113788
      ],
      [
        16.5755,
        139.113788
      ],
      [
        16.5755,
        145.870003
      ]
    ]
  }
]


def main() -> None:
    source = OBJ_PATH.read_text(encoding="utf-8")
    if "# REAL OPENINGS: WINDOW A + BALCONY DOOR THROUGH-WALL CUTS v1" not in source:
        raise SystemExit("Run the through-wall opening repair before adding reveals.")
    if MARKER in source:
        raise SystemExit("Opening reveals already exist; refusing to duplicate them.")

    # Source-aware duplicate check: some reveal sides are already modelled.
    source_vertices = []
    existing_quad_keys = set()
    for line in source.splitlines():
        value = line.strip()
        if value.startswith("v "):
            source_vertices.append(tuple(float(x) for x in value.split()[1:4]))
        elif value.startswith("f "):
            tokens = value.split()[1:]
            if len(tokens) == 4:
                points = [
                    source_vertices[int(token.split("/")[0]) - 1]
                    for token in tokens
                ]
                key = tuple(sorted(tuple(round(x, 3) for x in point) for point in points))
                existing_quad_keys.add(key)

    lines = source.splitlines()
    vertex_count = sum(line.startswith("v ") for line in lines)
    uv_count = sum(line.startswith("vt ") for line in lines)
    normal_count = sum(line.startswith("vn ") for line in lines)

    vertices: list[str] = []
    uvs: list[str] = []
    normals: list[str] = []
    blocks: list[str] = []
    next_v, next_vt, next_vn = vertex_count + 1, uv_count + 1, normal_count + 1
    face_count = 0

    for reveal in REVEALS:
        polygon = [tuple(point) for point in reveal["points"]]
        signed_area = sum(
            polygon[i][0] * polygon[(i + 1) % len(polygon)][1]
            - polygon[(i + 1) % len(polygon)][0] * polygon[i][1]
            for i in range(len(polygon))
        ) / 2
        ccw = signed_area > 0
        object_faces: list[str] = []

        for edge in range(len(polygon)):
            a, b = polygon[edge], polygon[(edge + 1) % len(polygon)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = (dx * dx + dy * dy) ** 0.5
            if length < 0.001:
                raise SystemExit("Degenerate aperture edge.")

            if ccw:
                inward = (-dy / length, dx / length)
                positions = [
                    (b[0], b[1], reveal["outer_z"]),
                    (a[0], a[1], reveal["outer_z"]),
                    (a[0], a[1], reveal["inner_z"]),
                    (b[0], b[1], reveal["inner_z"]),
                ]
                uv = [(length, 0), (0, 0), (0, reveal["inner_z"] - reveal["outer_z"]),
                      (length, reveal["inner_z"] - reveal["outer_z"])]
            else:
                inward = (dy / length, -dx / length)
                positions = [
                    (a[0], a[1], reveal["outer_z"]),
                    (b[0], b[1], reveal["outer_z"]),
                    (b[0], b[1], reveal["inner_z"]),
                    (a[0], a[1], reveal["inner_z"]),
                ]
                uv = [(0, 0), (length, 0), (length, reveal["inner_z"] - reveal["outer_z"]),
                      (0, reveal["inner_z"] - reveal["outer_z"])]

            point_key = tuple(sorted(tuple(round(float(x), 3) for x in point) for point in positions))
            if point_key in existing_quad_keys:
                continue
            existing_quad_keys.add(point_key)

            normal_index = next_vn
            normals.append(f"vn {inward[0]:.7f} {inward[1]:.7f} 0.0000000")
            next_vn += 1
            refs = []
            for point, texcoord in zip(positions, uv):
                vertices.append(f"v {point[0]:.7f} {point[1]:.7f} {point[2]:.7f}")
                uvs.append(f"vt {texcoord[0]:.7f} {texcoord[1]:.7f}")
                refs.append(f"{next_v}/{next_vt}/{normal_index}")
                next_v += 1
                next_vt += 1
            object_faces.append("f " + " ".join(refs))
            face_count += 1

        floor = int(reveal["floor"])
        kind = reveal["kind"]
        blocks.extend([
            f"o apartment_column_floor_{floor:02d}_{kind}_opening_reveal",
            "g opening_reveal",
            "usemtl OpeningReveal",
            "s off",
            *object_faces,
        ])

    if face_count != 78 or len(vertices) != 312 or len(uvs) != 312 or len(normals) != 78:
        raise SystemExit("Reveal geometry validation failed.")

    additions = [
        "",
        MARKER,
        "# 21 apertures receive only missing reveal quads; six source sides are retained.",
        "# Source-measured depths; top-floor door has no backing wall plane.",
        *vertices,
        *uvs,
        *normals,
        *blocks,
        "",
    ]
    updated = source.rstrip() + "\n" + "\n".join(additions)
    if sum(line.startswith("v ") for line in updated.splitlines()) != 9455:
        raise SystemExit("Final vertex count mismatch.")
    if sum(line.startswith("f ") for line in updated.splitlines()) != 7021:
        raise SystemExit("Final face count mismatch.")

    text_copy = updated.replace(
        "# 3ds Max Wavefront OBJ Exporter v0.97b - (c)2007 guruware",
        "# building - (c)2026 5110",
        1,
    )
    OBJ_PATH.write_text(updated, encoding="utf-8", newline="\n")
    TXT_PATH.write_text(text_copy, encoding="utf-8", newline="\n")
    print("Added 84 reveal quads to 21 source-backed openings.")


if __name__ == "__main__":
    main()
