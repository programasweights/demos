# English to calendar

[Interactive demo](https://programasweights.com/time) · [Neural program](https://programasweights.com/hub/94cae81a182723b85cdf) · [Exact spec](spec.txt)

The neural program extracts a schedule. Your code chooses the reference date and timezone, then expands that schedule into calendar events.

From the repository root:

```bash
python time/example.py
```

Example output:

```json
{"kind":"weekly","days":[6,7],"start":"14:00","end":"16:00"}
```

Pass your own text as the first argument. Add `--local` to run on your computer, or `--program ID` to use your own program.

## Compile your own

Edit [spec.txt](spec.txt), then run:

```bash
python compile.py time
```

Use the printed ID with `python time/example.py --program ID`.
