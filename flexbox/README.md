# Predicting flexbox layout

Predict the positions and widths of boxes in a horizontal flex row from its layout properties.

[Interactive demo](https://programasweights.com/flexbox) · [Neural program](https://programasweights.com/hub/3c09d7b6e31063797825) · [Task spec](spec.txt)

## Run it

From the repository root:

```bash
python flexbox/example.py
python flexbox/example.py --width 400
python flexbox/example.py --file layout.json --local
```

Each output pair is `[left, width]` in pixels. Change the container width, gap, alignment, or each box's `basis`, `grow`, and `shrink` in a `layout.json` file:

```json
{"width":640,"gap":16,"justify":"space-between","items":[{"basis":120,"grow":1,"shrink":1},{"basis":160,"grow":0,"shrink":1},{"basis":200,"grow":2,"shrink":1}]}
```

## How it works

1. [`codec.py`](codec.py) normalizes the input to a 1,000-unit row and adds sums and prefix sums.
2. The program predicts an integer starting offset, total extra spacing, and box widths.
3. The decoder rescales those predictions into pixels.

The model supports 1–4 boxes with `min-width: 0` and no wrapping. Inputs use integer width 240–960, gap 0–40, basis 20–400, grow 0–3, and shrink 0/1. Chromium supplies the training targets; inference uses only the model and codec.

## Train your own

Flexbox uses a custom LoRA trained on browser-generated examples. The other five demos use PAW's English-spec compiler.

Install training dependencies and Chromium:

```bash
pip install -r flexbox/requirements-train.txt
python -m playwright install chromium
```

### Generate training data

Use Chromium to generate disjoint training, validation, and test sets:

```bash
python flexbox/generate.py
```

### Train

Train a LoRA on a CUDA GPU:

```bash
python flexbox/train.py
```

The compact training script uses rank 64, alpha 16, batch size 64, and the released program's learning-rate stages: `2e-4` through step 4,000, `5e-5` through 5,000, then `1e-5` through 9,500. It keeps the interpreter frozen and learns adapters for its attention and MLP projections. Adjust `--steps`, `--lr-schedule`, `--rank`, `--alpha`, or `--micro-batch-size` to experiment.

### Evaluate

Check a saved adapter against Chromium:

```bash
python flexbox/evaluate.py --checkpoint runs/flexbox/checkpoint-9500 --limit 0
```

This reports whole-layout accuracy within 2 pixels and coordinate mean absolute error. Use validation to compare checkpoints; use `--data data/flexbox/test.jsonl` for your final evaluation.

### Upload your program

Upload the selected adapter as a public PAW program:

```bash
paw login
python flexbox/upload.py runs/flexbox/checkpoint-9500
python flexbox/example.py --program YOUR_PROGRAM_ID
```

The upload contains the LoRA weights, adapter configuration, and a manifest with the exact prompt template and interpreter ID. Keep the prompt template unchanged between training and inference. Uploading requires a PAW account; running the public program does not.

The released program is the selected step-9,500 checkpoint. These scripts provide a standalone version of the data-generation and training pipeline; they generate a fresh dataset and adapter rather than recreating identical weights.
