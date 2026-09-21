# Neural syntax highlighting

[Interactive demo](https://programasweights.com/syntax) · [Neural program](https://programasweights.com/hub/8cc17c494a1c1f81a50d) · [Exact spec](spec.txt)

Give the program source code and mechanically split tokens. It predicts a label for each token: keyword, string, comment, function, and so on. The renderer preserves the original text and whitespace.

From the repository root:

```bash
python syntax/example.py
python syntax/example.py 'def greet(name): return "Hello " + name'
python syntax/example.py --file my_snippet.py --local
```

The script prints colored source and the raw `[label, token]` pairs. It accepts short snippets up to 80 tokens. The website additionally chunks longer files.

[`codec.py`](codec.py) contains the mechanical tokenization and rendering; it never assigns syntax labels. For example, `const n = 42;` becomes:

```json
[[4,"const"],[0,"n"],[8,"="],[3,"42"],[0,";"]]
```

## Compile your own

Edit [spec.txt](spec.txt), then run `python compile.py syntax`. Pass the printed ID to `python syntax/example.py --program ID`.
