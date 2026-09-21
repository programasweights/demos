"""Generate disjoint train/validation/test layouts with Chromium as the teacher."""
import argparse
import json
from pathlib import Path
import random

from codec import JUSTIFY, encode, target

MEASURE = """layouts => layouts.map(layout => {
  const row = document.createElement('div');
  Object.assign(row.style, {display: 'flex', position: 'absolute', left: '0',
    width: `${layout.width}px`, gap: `${layout.gap}px`, justifyContent: layout.justify,
    padding: '0', border: '0', flexWrap: 'nowrap'});
  for (const item of layout.items) {
    const box = document.createElement('div');
    box.style.flex = `${item.grow} ${item.shrink} ${item.basis}px`;
    box.style.minWidth = '0'; row.append(box);
  }
  document.body.append(row);
  const origin = row.getBoundingClientRect().x;
  const boxes = [...row.children].map(box => {
    const rect = box.getBoundingClientRect(); return [rect.x - origin, rect.width];
  });
  row.remove(); return boxes;
})"""


def sample(rng, index):
    n, regime = index % 4 + 1, (index // 24) % 5
    layout = dict(width=rng.randint(240, 960), gap=rng.randint(0, 40),
                  justify=JUSTIFY[(index // 4) % 6], items=[
                      dict(basis=rng.randint(20, 400), grow=0 if regime in (0, 4) else rng.randint(0, 3),
                           shrink=0 if regime == 4 else rng.randint(0, 1)) for _ in range(n)])
    if regime == 2:
        width = sum(item["basis"] for item in layout["items"]) + layout["gap"] * (n - 1) + rng.randint(-2, 2)
        if 240 <= width <= 960:
            layout["width"] = width
    return layout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data/flexbox"))
    parser.add_argument("--train", type=int, default=50000)
    parser.add_argument("--validation", type=int, default=2000)
    parser.add_argument("--test", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=9162026)
    args = parser.parse_args()
    if min(args.train, args.validation, args.test) < 1:
        parser.error("Split sizes must be positive.")
    from playwright.sync_api import sync_playwright
    args.out.mkdir(parents=True, exist_ok=False)
    rng, seen = random.Random(args.seed), set()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_content("<html><body></body></html>")
        for split in ("train", "validation", "test"):
            done, count = 0, getattr(args, split)
            with (args.out / f"{split}.jsonl").open("x", encoding="utf-8") as stream:
                while done < count:
                    layouts = []
                    while len(layouts) < min(128, count - done):
                        layout = sample(rng, done + len(layouts))
                        text = encode(layout)
                        if text not in seen:
                            seen.add(text)
                            layouts.append(layout)
                    for layout, boxes in zip(layouts, page.evaluate(MEASURE, layouts)):
                        row = dict(input=encode(layout), output=target(layout, boxes), layout=layout, expected=boxes)
                        stream.write(json.dumps(row, separators=(",", ":")) + "\n")
                    done += len(layouts)
            print(f"{split}: {done} layouts")
        browser.close()


if __name__ == "__main__":
    main()
