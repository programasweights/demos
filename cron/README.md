# English to cron

[Interactive demo](https://programasweights.com/cron) · [Neural program](https://programasweights.com/hub/c073ac964bf9c643a67d) · [Exact spec](spec.txt)

The output is a five-field cron expression. Interpret it in your chosen timezone using a cron library. This example only prints the expression; it does not schedule jobs.

From the repository root:

```bash
python cron/example.py
```

Example output:

```json
{"cron":"30 9 * * 1-5"}
```

Pass your own text as the first argument. Add `--local` to run on your computer, or `--program ID` to use your own program.

## Compile your own

Edit [spec.txt](spec.txt), then run:

```bash
python compile.py cron
```

Use the printed ID with `python cron/example.py --program ID`.
