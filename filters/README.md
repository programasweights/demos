# English to search filters

Turn an English search request into structured filters and a sort order for a product catalog.

[Interactive demo](https://programasweights.com/filters) · [Neural program](https://programasweights.com/hub/2ba29151520ed1bd0956) · [Exact spec](spec.txt)

## Run it

From the repository root:

```bash
python filters/example.py
```

Example output:

```json
{"filters":[["category","eq","headphones"],["wireless","eq",true],["price","lt",150]],"sort":["price","asc"]}
```

Apply the AND-combined filters and optional sort order to your catalog with ordinary code.

Pass your own text as the first argument. Add `--local` to run on your computer, or `--program ID` to use your own program.

## Compile your own

Edit [spec.txt](spec.txt), then run this Python from the repository root:

```python
from pathlib import Path
import programasweights as paw

spec = Path("filters/spec.txt").read_text(encoding="utf-8").strip()
program = paw.compile(spec, compiler="paw-ft-bs48")
print(program.id)
```

Use the printed ID with `python filters/example.py --program ID`. Save it to reuse the program without recompiling.

Shortcut: [`python compile.py filters`](../compile.py).
