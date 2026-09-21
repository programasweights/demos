"""enriched-factorized-v1: layout inputs → model text → predicted pixel boxes."""
import json
import math

JUSTIFY = ["flex-start", "center", "flex-end", "space-between", "space-around", "space-evenly"]
GRID = 1000


def validate(layout):
    def bounded(value, lo, hi):
        return type(value) is int and lo <= value <= hi

    if (not isinstance(layout, dict) or not bounded(layout.get("width"), 240, 960)
            or not bounded(layout.get("gap"), 0, 40) or layout.get("justify") not in JUSTIFY
            or not isinstance(layout.get("items"), list) or not 1 <= len(layout["items"]) <= 4
            or any(not isinstance(item, dict) or not bounded(item.get("basis"), 20, 400)
                   or not bounded(item.get("grow"), 0, 3) or not bounded(item.get("shrink"), 0, 1)
                   for item in layout["items"])):
        raise ValueError("Expected width 240–960, gap 0–40, and 1–4 boxes: basis 20–400, grow 0–3, shrink 0/1 (integers).")


def normalized(value, width):
    # Match the Chromium dataset's JavaScript Math.round, including JSON int/float spelling.
    number = math.floor((value * GRID / width) * GRID + 0.5) / GRID
    return int(number) if number.is_integer() else number


def features(layout):
    validate(layout)
    basis = grow = shrink = 0
    items = []
    gap = normalized(layout["gap"], layout["width"])
    for item in layout["items"]:
        b = normalized(item["basis"], layout["width"])
        weighted = b * item["shrink"]
        items.append(dict(basis=b, grow=item["grow"], shrink=item["shrink"],
                          weightedShrink=round(weighted, 3), prefixBasis=round(basis, 3),
                          prefixGrow=grow, prefixWeightedShrink=round(shrink, 3)))
        basis += b
        grow += item["grow"]
        shrink += weighted
    free = round(GRID - gap * (len(items) - 1) - basis, 3)
    return dict(n=len(items), gap=gap, justify=layout["justify"], totalBasis=round(basis, 3),
                free=free, totalGrow=grow, totalWeightedShrink=round(shrink, 3),
                freeSign=(free > 0) - (free < 0), canGrow=int(grow > 0), canShrink=int(shrink > 0), items=items)


def encode(layout):
    return json.dumps(features(layout), separators=(",", ":"))


def decode(raw, layout):
    validate(layout)
    value = json.loads(raw)
    if not isinstance(value, dict) or set(value) != {"offset", "extra", "widths"}:
        raise ValueError("Expected offset, extra, and widths.")
    offset, extra, widths = value["offset"], value["extra"], value["widths"]
    n = len(layout["items"])
    if (not isinstance(widths, list) or len(widths) != n
            or any(type(x) is not int or abs(x) > 100000 for x in [offset, extra, *widths])
            or extra < 0 or any(w < 0 for w in widths) or (n == 1 and extra != 0)):
        raise ValueError("Invalid integer layout predictions.")
    scale = layout["width"] / GRID
    gap = normalized(layout["gap"], layout["width"]) + (extra / (n - 1) if n > 1 else 0)
    boxes = []
    for width in widths:
        boxes.append([offset * scale, width * scale])
        offset += width + gap
    return boxes


def target(layout, boxes):
    """Encode Chromium geometry as training targets; never called during inference."""
    scale = GRID / layout["width"]
    grid_boxes = [[x * scale, width * scale] for x, width in boxes]
    widths, total, previous = [], 0.0, 0
    for _, width in grid_boxes:
        total += width
        current = math.floor(total + 0.5)
        widths.append(current - previous)
        previous = current
    spacing = sum(grid_boxes[i + 1][0] - grid_boxes[i][0] - grid_boxes[i][1] for i in range(len(boxes) - 1))
    extra = math.floor(spacing - features(layout)["gap"] * (len(boxes) - 1) + 0.5) if len(boxes) > 1 else 0
    return json.dumps(dict(offset=math.floor(grid_boxes[0][0] + 0.5), extra=extra, widths=widths), separators=(",", ":"))
