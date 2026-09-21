# English to calendar

Turn an English description into a structured schedule for calendar events.

[Interactive demo](https://programasweights.com/time) · [Neural program](https://programasweights.com/hub/94cae81a182723b85cdf) · [Exact spec](spec.txt)

## Run it

From the repository root:

```bash
python time/example.py
```

Example output:

```json
{"kind":"weekly","days":[6,7],"start":"14:00","end":"16:00"}
```

Your code chooses the reference date and timezone, then expands the schedule into calendar events.

Pass your own text as the first argument. Add `--local` to run on your computer, or `--program ID` to use your own program.

## Compile your own

Edit [spec.txt](spec.txt), then run this Python from the repository root:

```python
from pathlib import Path
import programasweights as paw

spec = Path("time/spec.txt").read_text(encoding="utf-8").strip()
program = paw.compile(spec, compiler="paw-ft-bs48")
print(program.id)
```

Use the printed ID with `python time/example.py --program ID`. Save it to reuse the program without recompiling.

Shortcut: [`python compile.py time`](../compile.py).
