# Arabic morphology

Analyze a Modern Standard Arabic word to find its segments, consonantal root, part of speech, and English meaning.

[Interactive demo](https://programasweights.com/arabic) · [Neural program](https://programasweights.com/hub/4185aac0cf28915ce61e) · [Exact spec](spec.txt)

## Run it

From the repository root:

```bash
python arabic/example.py
```

Example output:

```json
{"segments":["و","ب","كتاب","هم"],"root":"كتب","pos":"noun","gloss":"and with their book"}
```

Pass your own text as the first argument. Add `--local` to run on your computer, or `--program ID` to use your own program.

## Compile your own

Edit [spec.txt](spec.txt), then run this Python from the repository root:

```python
from pathlib import Path
import programasweights as paw

spec = Path("arabic/spec.txt").read_text(encoding="utf-8").strip()
program = paw.compile(spec, compiler="paw-ft-bs48")
print(program.id)
```

Use the printed ID with `python arabic/example.py --program ID`. Save it to reuse the program without recompiling.

Shortcut: [`python compile.py arabic`](../compile.py).
