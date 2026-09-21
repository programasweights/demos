"""Compare model-predicted boxes with held-out Chromium layouts."""
import argparse
import json
from pathlib import Path

from codec import decode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/flexbox/validation.jsonl"))
    parser.add_argument("--limit", type=int, default=128, help="0 evaluates the full file")
    parser.add_argument("--checkpoint", type=Path, help="Evaluate a local PEFT adapter before uploading")
    parser.add_argument("--program", default="3c09d7b6e31063797825")
    parser.add_argument("--local", action="store_true", help="Use local SDK inference instead of hosted inference")
    parser.add_argument("--device", choices=["cuda", "cpu", "mps"], default="cuda")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("Limit must be nonnegative.")
    rows = [json.loads(line) for line in args.data.read_text().splitlines() if line.strip()]
    if args.limit:
        rows = rows[:args.limit]
    if not rows:
        parser.error("Evaluation data is empty.")
    function = None
    if args.checkpoint:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from train import BASE, REVISION
        tokenizer = AutoTokenizer.from_pretrained(BASE, revision=REVISION)
        dtype = torch.bfloat16 if args.device == "cuda" and torch.cuda.is_bf16_supported() else torch.float32
        base = AutoModelForCausalLM.from_pretrained(BASE, revision=REVISION, torch_dtype=dtype).to(args.device)
        model = PeftModel.from_pretrained(base, args.checkpoint).eval()
        template = (args.checkpoint / "prompt_template.txt").read_text()

        def infer(text):
            ids = tokenizer(template.replace("{INPUT_PLACEHOLDER}", text), return_tensors="pt", add_special_tokens=False).to(args.device)
            with torch.inference_mode():
                output = model.generate(**ids, max_new_tokens=128, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            return tokenizer.decode(output[0, ids["input_ids"].shape[1]:], skip_special_tokens=True)
    else:
        import programasweights as paw
        function = paw.function(args.program, remote=not args.local)
        infer = lambda text: function(text, max_tokens=128)
    errors, valid, correct = [], 0, 0
    try:
        for row in rows:
            raw = infer(row["input"])
            try:
                predicted = decode(raw, row["layout"])
            except (ValueError, TypeError):
                continue
            delta = [abs(a - b) for actual, expected in zip(predicted, row["expected"]) for a, b in zip(actual, expected)]
            valid += 1
            correct += max(delta) <= 2
            errors.extend(delta)
    finally:
        if function:
            function.close()
    print(json.dumps(dict(examples=len(rows), valid=valid, within_2px=correct,
                          accuracy=correct / len(rows), coordinate_mae_px=sum(errors) / len(errors) if errors else None), indent=2))


if __name__ == "__main__":
    main()
