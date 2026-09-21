"""Finetune Qwen3-0.6B on Chromium input/output pairs and export an uploadable LoRA."""
import argparse
import json
import math
from pathlib import Path
import random

BASE = "Qwen/Qwen3-0.6B"
REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"
MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def learning_rates(text):
    schedule = [(int(step), float(rate)) for step, rate in (part.split(":") for part in text.split(","))]
    if (not schedule or schedule[0][0] != 0 or any(step < 0 or not math.isfinite(rate) or rate <= 0 for step, rate in schedule)
            or any(a[0] >= b[0] for a, b in zip(schedule, schedule[1:]))):
        raise ValueError("Use increasing step:rate pairs starting at 0, e.g. 0:2e-4,4000:5e-5,5000:1e-5")
    return schedule


def encode_pair(row, tokenizer, template, max_length):
    prompt = tokenizer.encode(template.replace("{INPUT_PLACEHOLDER}", row["input"]), add_special_tokens=False)
    target = tokenizer.encode(row["output"], add_special_tokens=False) + [tokenizer.eos_token_id]
    if len(prompt) + len(target) > max_length:
        raise ValueError("Example exceeds max-length; shorten the input rather than truncating its target.")
    return dict(input_ids=prompt + target, labels=[-100] * len(prompt) + target)


def batch_tensors(rows, pad, device):
    import torch
    length = max(len(row["input_ids"]) for row in rows)
    return {
        "input_ids": torch.tensor([r["input_ids"] + [pad] * (length - len(r["input_ids"])) for r in rows], device=device),
        "attention_mask": torch.tensor([[1] * len(r["input_ids"]) + [0] * (length - len(r["input_ids"])) for r in rows], device=device),
        "labels": torch.tensor([r["labels"] + [-100] * (length - len(r["labels"])) for r in rows], device=device),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/flexbox/train.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("runs/flexbox"))
    parser.add_argument("--steps", type=int, default=9500)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--micro-batch-size", type=int, default=1)
    parser.add_argument("--lr-schedule", default="0:2e-4,4000:5e-5,5000:1e-5")
    parser.add_argument("--rank", type=int, default=64)
    parser.add_argument("--alpha", type=float, default=16)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--save-every", type=int, default=500)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", choices=["cuda", "cpu", "mps"], default="cuda")
    args = parser.parse_args()
    if min(args.steps, args.batch_size, args.micro_batch_size, args.save_every) < 1 or not 1 <= args.rank <= 128:
        parser.error("Counts must be positive; rank must be 1–128.")
    if not math.isfinite(args.alpha) or not 0 < args.alpha <= 1024 or not 2 <= args.max_length <= 2048:
        parser.error("Use alpha in (0, 1024] and max-length 2–2048.")
    schedule = learning_rates(args.lr_schedule)
    if args.out.exists():
        raise FileExistsError(f"Choose a new output directory: {args.out}")
    import torch
    from peft import LoraConfig, get_peft_model, get_peft_model_state_dict
    from safetensors.torch import save_file
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(args.seed)
    rng = random.Random(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(BASE, revision=REVISION)
    spec = Path(__file__).with_name("spec.txt").read_text().strip()
    template = tokenizer.apply_chat_template([dict(role="user", content=spec + "\n\n[INPUT]\n{INPUT_PLACEHOLDER}\n[END_INPUT]")],
                                             tokenize=False, add_generation_prompt=True, enable_thinking=False)
    rows = [encode_pair(json.loads(line), tokenizer, template, args.max_length)
            for line in args.data.read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError("Training data is empty.")
    dtype = torch.bfloat16 if args.device == "cuda" and torch.cuda.is_bf16_supported() else torch.float32
    base = AutoModelForCausalLM.from_pretrained(BASE, revision=REVISION, torch_dtype=dtype).to(args.device)
    model = get_peft_model(base, LoraConfig(r=args.rank, lora_alpha=args.alpha, target_modules=MODULES,
                                          bias="none", lora_dropout=0, task_type="CAUSAL_LM", revision=REVISION))
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.config.use_cache = False
    model.train()
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=schedule[0][1], weight_decay=0)
    args.out.mkdir(parents=True)
    order, cursor = list(range(len(rows))), 0
    rng.shuffle(order)

    def save(step):
        path = args.out / f"checkpoint-{step}"
        path.mkdir()
        state = {name: value.detach().to(device="cpu", dtype=torch.float16).contiguous()
                 for name, value in get_peft_model_state_dict(model, save_embedding_layers=False).items()}
        if any(not torch.isfinite(value).all() for value in state.values()):
            raise ValueError("Non-finite adapter weights.")
        save_file(state, str(path / "adapter_model.safetensors"))
        config = model.peft_config["default"]
        config.base_model_name_or_path = BASE
        previous_mode = config.inference_mode
        config.inference_mode = True
        config.save_pretrained(path)
        config.inference_mode = previous_mode
        manifest = dict(schema_version=1, spec=spec, runtime_id="qwen3-0.6b-q6_k", producer="chromium-flex-factorized-v1", prompt_template=template)
        (path / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        (path / "prompt_template.txt").write_text(template)
        recipe = {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()}
        (path / "training.json").write_text(json.dumps(dict(recipe, step=step, base=BASE, revision=REVISION), indent=2) + "\n")
        print(f"Saved {path}", flush=True)

    for step in range(1, args.steps + 1):
        rate = next(rate for after, rate in reversed(schedule) if step > after)
        for group in optimizer.param_groups:
            group["lr"] = rate
        batch = []
        while len(batch) < args.batch_size:
            if cursor == len(order):
                rng.shuffle(order)
                cursor = 0
            batch.append(rows[order[cursor]])
            cursor += 1
        total_tokens = sum(sum(label != -100 for label in row["labels"]) for row in batch)
        optimizer.zero_grad(set_to_none=True)
        total_loss = 0.0
        for start in range(0, len(batch), args.micro_batch_size):
            tensors = batch_tensors(batch[start:start + args.micro_batch_size], tokenizer.eos_token_id, args.device)
            loss = model(**tensors, use_cache=False).loss
            if not torch.isfinite(loss):
                raise ValueError("Non-finite training loss.")
            weighted = loss * (tensors["labels"][:, 1:] != -100).sum() / total_tokens
            weighted.backward()
            total_loss += weighted.item()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        optimizer.step()
        if step == 1 or step % 10 == 0:
            print(f"step={step} loss={total_loss:.4f} lr={rate:g}", flush=True)
        if step % args.save_every == 0 or step == args.steps:
            save(step)


if __name__ == "__main__":
    main()
