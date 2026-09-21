"""Optional tiny-model smoke test; runs when the training extras are installed."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("flex_train", ROOT / "flexbox/train.py")
train = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train)


@unittest.skipUnless(importlib.util.find_spec("peft") and importlib.util.find_spec("torch"), "Install flexbox training extras")
class TinyTraining(unittest.TestCase):
    def test_two_updates_and_uploadable_export(self):
        import torch
        from safetensors.torch import load_file
        from transformers import Qwen3Config, Qwen3ForCausalLM

        class Tokenizer:
            eos_token_id = 0
            def encode(self, text, **kwargs):
                return [byte + 1 for byte in text.encode()]
            def apply_chat_template(self, messages, **kwargs):
                return messages[0]["content"] + "\n"

        model = Qwen3ForCausalLM(Qwen3Config(vocab_size=257, hidden_size=16, intermediate_size=32,
                                           num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=1, head_dim=8))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            data = path / "data.jsonl"
            data.write_text(json.dumps(dict(input="x", output="y")) + "\n")
            argv = ["train.py", "--data", str(data), "--out", str(path / "run"), "--steps", "2",
                    "--batch-size", "2", "--micro-batch-size", "1", "--save-every", "1", "--rank", "2", "--device", "cpu"]
            with patch.object(sys, "argv", argv), patch("transformers.AutoTokenizer.from_pretrained", return_value=Tokenizer()), patch("transformers.AutoModelForCausalLM.from_pretrained", return_value=model):
                train.main()
            output = path / "run/checkpoint-2"
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["runtime_id"], "qwen3-0.6b-q6_k")
            self.assertEqual(manifest["prompt_template"], (output / "prompt_template.txt").read_text())
            self.assertEqual(manifest["prompt_template"].count("{INPUT_PLACEHOLDER}"), 1)
            weights = load_file(output / "adapter_model.safetensors")
            self.assertTrue(all(value.dtype == torch.float16 and torch.isfinite(value).all() for value in weights.values()))
            self.assertTrue(all("lora_" in name for name in weights))
            config = json.loads((output / "adapter_config.json").read_text())
            self.assertEqual(config["r"], 2)
            self.assertEqual(config["revision"], train.REVISION)


if __name__ == "__main__":
    unittest.main()
