"""Split source mechanically; all syntax labels come from the neural program."""
import json
import unicodedata

LABELS = ["plain", "comment", "string", "number", "keyword", "type", "function", "constant", "operator"]
COLORS = ["", "90", "32", "33", "35", "36", "34", "33", "36"]


def tokens(code):
    result, i = [], 0
    while i < len(code):
        start, char = i, code[i]
        i += 1
        if char.isspace():
            continue
        if char in "_$" or unicodedata.category(char).startswith("L"):
            while i < len(code) and (code[i] in "_$" or unicodedata.category(code[i])[0] in "LN"):
                i += 1
        elif char in "0123456789":
            while i < len(code) and code[i] in "0123456789":
                i += 1
            if i + 1 < len(code) and code[i] == "." and code[i + 1] in "0123456789":
                i += 1
                while i < len(code) and code[i] in "0123456789":
                    i += 1
        result.append((code[start:i], start, i))
    return result


def encode(code):
    pieces = [text for text, _, _ in tokens(code)]
    if not 1 <= len(pieces) <= 80:
        raise ValueError("Use a short snippet with 1–80 non-whitespace tokens.")
    return json.dumps(dict(code=code, tokens=pieces, count=len(pieces)), ensure_ascii=False, separators=(",", ":"))


def decode(raw, code):
    pairs = json.loads(raw)
    pieces = tokens(code)
    if not isinstance(pairs, list) or len(pairs) != len(pieces):
        raise ValueError("The program did not label every source token.")
    for pair, (text, _, _) in zip(pairs, pieces):
        if (not isinstance(pair, list) or len(pair) != 2 or pair[1] != text
                or type(pair[0]) is not int or not 0 <= pair[0] < len(LABELS)):
            raise ValueError("The program changed a token or returned an invalid label.")
    return pairs


def highlight(code, pairs):
    parts, end = [], 0
    for (label, text), (_, start, stop) in zip(pairs, tokens(code)):
        color = COLORS[label]
        parts.extend([code[end:start], f"\033[{color}m{text}\033[0m" if color else text])
        end = stop
    return "".join(parts) + code[end:]
