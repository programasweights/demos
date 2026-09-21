# Syntax highlighting

Turn source code into labeled tokens and syntax-highlighted text.

[Interactive demo](https://programasweights.com/syntax) · [Neural program](https://programasweights.com/hub/8cc17c494a1c1f81a50d) · [Exact spec](spec.txt)

## Run it

From the repository root:

```bash
python syntax/example.py
python syntax/example.py 'def greet(name): return "Hello " + name'
python syntax/example.py --file my_snippet.py --local
```

The script prints colored source and the raw `[label, token]` pairs. It accepts short snippets up to 80 tokens. The website additionally chunks longer files.

[`codec.py`](codec.py) splits the source into tokens; the neural program labels each token as a keyword, string, comment, function, and so on. The renderer preserves the original text and whitespace. For example, `const n = 42;` becomes:

```json
[[4,"const"],[0,"n"],[8,"="],[3,"42"],[0,";"]]
```

## Compile your own

Edit [spec.txt](spec.txt), then run this Python from the repository root:

```python
from pathlib import Path
import programasweights as paw

spec = Path("syntax/spec.txt").read_text(encoding="utf-8").strip()
program = paw.compile(spec, compiler="paw-ft-bs48")
print(program.id)
```

Use the printed ID with `python syntax/example.py --program ID`. Save it to reuse the program without recompiling.

Shortcut: [`python compile.py syntax`](../compile.py).
