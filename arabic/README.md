# Arabic morphology

[Interactive demo](https://programasweights.com/arabic) · [Neural program](https://programasweights.com/hub/4185aac0cf28915ce61e) · [Exact spec](spec.txt)

Analyze one Modern Standard Arabic word. The program returns its segments, consonantal root, part of speech, and a short English meaning.

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

Edit [spec.txt](spec.txt), then run:

```bash
python compile.py arabic
```

Use the printed ID with `python arabic/example.py --program ID`.
