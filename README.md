# ProgramAsWeights demos

Small neural programs you can use in a few lines of Python.

[Try the interactive demos](https://programasweights.com/demos) · [Python SDK](https://github.com/programasweights/programasweights-python)

## Run a neural program

Load a published program and call it like a Python function.

```bash
pip install programasweights --extra-index-url https://pypi.programasweights.com/simple/
```

```python
import json
import programasweights as paw

calendar = paw.function("94cae81a182723b85cdf", remote=True)
print(json.loads(calendar(json.dumps({
    "text": "Every weekend from 2pm to 4pm",
    "today": "2026-09-21",
}))))
```

```json
{"kind":"weekly","days":[6,7],"start":"14:00","end":"16:00"}
```

Use `remote=False` to download the program and run locally. All six use the same Qwen3 0.6B interpreter. No API key is needed to run these public programs.

## Compile an English description

Clone this repository and edit the English description in [`time/spec.txt`](time/spec.txt):

```bash
git clone https://github.com/programasweights/demos.git
cd demos
```

Then compile it into a reusable neural program:

```python
from pathlib import Path
import programasweights as paw

spec = Path("time/spec.txt").read_text(encoding="utf-8").strip()
program = paw.compile(spec, compiler="paw-ft-bs48")

print(program.id)
calendar = paw.function(program.id, remote=True)
```

This uses the Finetune compiler. Save the resulting program ID to reuse it without recompiling. Use `compiler="paw-4b-qwen3-0.6b"` for the fast compiler. An optional `PAW_API_KEY` gives access to your account's compile quota.

Shortcut: [`python compile.py time`](compile.py).

## Explore the demos

Each example includes a runnable script, its exact task specification, and instructions for building your own.

- [Calendar](time): English → a structured schedule.
- [Syntax highlighting](syntax): source code → labeled tokens, with original spacing preserved.
- [Flexbox](flexbox): layout properties → predicted box positions and widths, with a [custom-training recipe](flexbox#train-your-own).
- [Arabic morphology](arabic): a word → segments, root, part of speech, and meaning.
- [Search filters](filters): English → filters and sorting for a product catalog.
- [Cron](cron): English → a five-field cron expression.

```bash
python time/example.py
python filters/example.py 'Wireless headphones under $150, cheapest first'
python syntax/example.py --local
```

Requires Python 3.10+. Examples use hosted inference by default; add `--local` to run on your computer, or `--program YOUR_PROGRAM_ID` to use your own program.

## More examples

[PII detection](https://github.com/programasweights/pii) · [Claudish translation](https://github.com/programasweights/claudish) · [Avatar Director](https://github.com/programasweights/avatar)

## Citation

If you use these demos in research, cite Program-as-Weights for the programming paradigm and Compile by Training for the training compiler used in the examples.

**[Program-as-Weights: A Programming Paradigm for Fuzzy Functions](https://arxiv.org/abs/2607.02512)**

NeurIPS 2026 · [Preprint](https://arxiv.org/abs/2607.02512)

```bibtex
@inproceedings{zhang2026programasweights,
  title = {{Program-as-Weights: A Programming Paradigm for Fuzzy Functions}},
  author = {Zhang, Wentao and Hotsko, Liliana and Kim, Woojeong and Nie, Pengyu and Shieber, Stuart and Deng, Yuntian},
  booktitle = {The Fortieth Annual Conference on Neural Information Processing Systems},
  year = {2026},
  url = {https://arxiv.org/abs/2607.02512}
}
```

**[Compile by Training: Turning Natural-Language Specifications into Local Neural Functions](https://arxiv.org/abs/2609.04199)**

```bibtex
@inproceedings{paw_2609_04199,
  title = {{Compile by Training: Turning Natural-Language Specifications into Local Neural Functions}},
  author = {Deng, Yuntian and Nie, Pengyu and Shieber, Stuart},
  booktitle = {EMNLP 2026 System Demonstrations},
  year = {2026},
  url = {https://arxiv.org/abs/2609.04199}
}
```

## Credits

Inspired by [Shu's small-model roundup](https://x.com/shuding/status/2100131151709171944): [gpu-time](https://github.com/arikchakma/gpu-time), [gpu-lexer](https://github.com/vercel-labs/gpu-lexer), [neural-flexbox](https://github.com/aaronvanston/neural-flexbox), [TinySarf](https://github.com/AhmedAbdel-Aal/tinySarf), [gpu-query](https://github.com/safzanpirani/gpu-query), and [gpu-cron](https://github.com/manuschillerdev/gpu-cron).
