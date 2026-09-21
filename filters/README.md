# English to search filters

[Interactive demo](https://programasweights.com/filters) · [Neural program](https://programasweights.com/hub/2ba29151520ed1bd0956) · [Exact spec](spec.txt)

The neural program produces AND-combined filters and an optional sort order. Apply these to your catalog with ordinary code; the model does not generate or execute SQL.

From the repository root:

```bash
python filters/example.py
```

Example output:

```json
{"filters":[["category","eq","headphones"],["wireless","eq",true],["price","lt",150]],"sort":["price","asc"]}
```

Pass your own text as the first argument. Add `--local` to run on your computer, or `--program ID` to use your own program.

## Compile your own

Edit [spec.txt](spec.txt), then run:

```bash
python compile.py filters
```

Use the printed ID with `python filters/example.py --program ID`.
