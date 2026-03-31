import re
from typing import Iterable, List, Optional


def extract_option_letters_from_options_text(options_text: str) -> List[str]:
    """
    Extract option letters (e.g., A, B, C, D) from an options text block.
    Common formats supported:
      - "A. xxx\nB. yyy"
      - "A) xxx\nB) yyy"
      - "A：xxx\nB：yyy"
    """
    if not options_text:
        return []

    letters = []
    for line in options_text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^([A-Z])\s*[\.\)\]】）:：\-、]\s*", line.upper())
        if m:
            letters.append(m.group(1))

    seen = set()
    unique_letters = []
    for x in letters:
        if x not in seen:
            seen.add(x)
            unique_letters.append(x)
    return unique_letters


def _normalize_text(text: str) -> str:
    if text is None:
        return ""
    return str(text).strip()


def parse_mcq_prediction(raw_response: str, valid_options: Optional[Iterable[str]] = None) -> str:
    """
    Parse a model's free-form response into a single multiple-choice option letter.

    Parsing strategy (in priority order):
    1) Match explicit answer patterns: "Answer: A", "答案：A", "Final: A".
    2) Match bracketed forms: "(A)", "（A）", "[A]".
    3) Match a leading option letter in the first non-empty line: "A", "A.", "A)".
    4) Match the first standalone letter token in the text.

    Args:
        raw_response: Model output string.
        valid_options: Optional iterable of valid option letters (e.g., ["A","B","C","D"]).

    Returns:
        A single uppercase option letter, or empty string if not found.
    """
    text = _normalize_text(raw_response)
    if not text:
        return ""

    valid_set = None
    if valid_options:
        valid_set = {str(x).strip().upper() for x in valid_options if str(x).strip()}

    upper_text = text.upper()

    patterns = [
        r"(?:^|\n)\s*(?:ANSWER|FINAL ANSWER|FINAL|OUTPUT|CHOICE)\s*[:：\-]\s*([A-Z])\b",
        r"(?:^|\n)\s*(?:答案|最终答案|最终|输出|选项)\s*[:：\-]\s*([A-Z])\b",
        r"[\(\[（【]\s*([A-Z])\s*[\)\]）】]",
        r"^(?:\s*[\*\-•]\s*)?([A-Z])\s*(?:[\.\)\]】）:：\-、]\s*|$)",
        r"\b([A-Z])\b",
    ]

    for pat in patterns:
        m = re.search(pat, upper_text, flags=re.MULTILINE)
        if not m:
            continue
        cand = m.group(1).strip().upper()
        if valid_set is None or cand in valid_set:
            return cand

    if valid_set:
        for c in valid_set:
            if c in upper_text:
                return c

    return ""

