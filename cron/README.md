# English to cron

Turn an English schedule into a five-field cron expression.

[Interactive demo](https://programasweights.com/cron) · [Neural program](https://programasweights.com/hub/c073ac964bf9c643a67d) · [Exact spec](spec.txt)

## Run it

From the repository root:

```bash
python cron/example.py
```

Example output:

```json
{"cron":"30 9 * * 1-5"}
```

Use the expression with a cron library in your chosen timezone to schedule jobs.

Pass your own text as the first argument. Add `--local` to run on your computer, or `--program ID` to use your own program.

## Compile your own

Edit [spec.txt](spec.txt), then run this Python from the repository root:

```python
from pathlib import Path
import programasweights as paw

spec = Path("cron/spec.txt").read_text(encoding="utf-8").strip()
program = paw.compile(spec, compiler="paw-ft-bs48")
print(program.id)
```

Use the printed ID with `python cron/example.py --program ID`. Save it to reuse the program without recompiling.

Shortcut: [`python compile.py cron`](../compile.py).
