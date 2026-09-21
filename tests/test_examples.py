"""Offline contract checks. Run: python -m unittest discover -s tests -v"""
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


flex = load("flex_codec", "flexbox/codec.py")
syntax = load("syntax_codec", "syntax/codec.py")
train = load("flex_train", "flexbox/train.py")


class Contracts(unittest.TestCase):
    def layout(self, width=640, **item):
        return dict(width=width, gap=16, justify="center", items=[dict(basis=160, grow=0, shrink=1, **item)])

    def test_flex_center(self):
        layout = self.layout()
        self.assertEqual(flex.features(layout)["totalBasis"], 250)
        self.assertEqual(flex.decode('{"offset":375,"extra":0,"widths":[250]}', layout), [[240, 160]])
        self.assertEqual(json.loads(flex.target(layout, [[240, 160]])), dict(offset=375, extra=0, widths=[250]))

    def test_flex_overflow_and_signed_offset(self):
        layout = self.layout(width=240)
        layout["items"][0].update(basis=400, shrink=0)
        output = flex.target(layout, [[-80, 400]])
        self.assertLess(json.loads(output)["offset"], 0)
        self.assertAlmostEqual(flex.decode(output, layout)[0][0], -79.92)

    def test_spacing_and_cumulative_rounding(self):
        layout = dict(width=640, gap=16, justify="space-between", items=[dict(basis=100, grow=0, shrink=1)] * 3)
        actual = flex.decode(flex.target(layout, [[0, 100], [270, 100], [540, 100]]), layout)
        self.assertTrue(all(abs(a - b) < 1 for box, expected in zip(actual, [[0, 100], [270, 100], [540, 100]]) for a, b in zip(box, expected)))

    def test_float_spelling_matches_training(self):
        layout = dict(width=387, gap=28, justify="center", items=[dict(basis=350, grow=0, shrink=0)])
        text = flex.encode(layout)
        self.assertIn('"totalWeightedShrink":0.0', text)
        self.assertIn('"weightedShrink":0.0', text)
        self.assertIn('"prefixBasis":0,', text)

    def test_flex_invalid_inputs(self):
        for value in [0, 239, 961, True, 640.0]:
            with self.assertRaises(ValueError):
                flex.encode(self.layout(width=value))

    def test_flex_invalid_outputs(self):
        for text in ['{"offset":0.0,"extra":0,"widths":[1]}', '{"offset":0,"extra":1,"widths":[1]}',
                     '{"offset":true,"extra":0,"widths":[1]}', '{"offset":0,"extra":0,"widths":[]}',
                     '{"offset":0,"extra":0,"widths":[-1]}', '{"offset":0,"extra":0,"widths":[1],"x":1}']:
            with self.assertRaises(ValueError):
                flex.decode(text, self.layout())

    def test_syntax_whitespace_and_unicode(self):
        code = 'const café = "مرحبا";\n\t// comment 😀\n'
        pairs = [[0, text] for text, _, _ in syntax.tokens(code)]
        self.assertEqual(syntax.highlight(code, syntax.decode(json.dumps(pairs), code)), code)
        self.assertEqual(json.loads(syntax.encode(code))["tokens"], [p[1] for p in pairs])

    def test_syntax_rejects_corruption(self):
        for pairs in [[[4, "var"]], [[True, "const"]], [[9, "const"]], [], [4]]:
            with self.assertRaises(ValueError):
                syntax.decode(json.dumps(pairs), "const")
        with self.assertRaises(ValueError):
            syntax.encode("x " * 81)

    def test_syntax_label_render_preserves_source(self):
        code = 'const n = 42;\n'
        pairs = [[4, "const"], [0, "n"], [8, "="], [3, "42"], [0, ";"]]
        colored = syntax.highlight(code, syntax.decode(json.dumps(pairs), code))
        self.assertEqual(re.sub(r"\x1b\[[0-9;]*m", "", colored), code)

    def test_training_schedule(self):
        rates = train.learning_rates("0:2e-4,4000:5e-5,5000:1e-5")
        self.assertEqual(rates, [(0, 0.0002), (4000, 0.00005), (5000, 0.00001)])
        for bad in ["1:0.1", "0:-1", "0:nan", "0:0.1,0:0.2"]:
            with self.assertRaises(ValueError):
                train.learning_rates(bad)

    def test_training_masks_prompt_and_adds_eos(self):
        class Tokenizer:
            eos_token_id = 1000
            def encode(self, text, **kwargs):
                return list(text.encode())
        result = train.encode_pair(dict(input="a", output="b"), Tokenizer(), "X{INPUT_PLACEHOLDER}Y", 20)
        self.assertEqual(result["input_ids"], [88, 97, 89, 98, 1000])
        self.assertEqual(result["labels"], [-100, -100, -100, 98, 1000])
        with self.assertRaises(ValueError):
            train.encode_pair(dict(input="a", output="b"), Tokenizer(), "X{INPUT_PLACEHOLDER}Y", 4)

    def test_specs_are_paragraphs_without_soft_wraps(self):
        for path in ROOT.glob("*/spec.txt"):
            for paragraph in path.read_text().strip().split("\n\n"):
                lines = paragraph.splitlines()
                self.assertTrue(len(lines) == 1 or len(lines) == 2 and lines[0].startswith("Input:") and lines[1].startswith("Output:"), path)


if __name__ == "__main__":
    unittest.main()
