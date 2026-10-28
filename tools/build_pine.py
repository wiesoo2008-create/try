"""스승님 지표/전략 빌드: pine/src/*.src.pine → pine/ 아래 지표판, 전략판, 통합판.

통합판(*_통합.pine)은 지표판 + 거래량 보조지표를 한 스크립트로 묶는다.
스크립트는 아래 창(거래량)에 붙고, 매물대·라벨·선·표는 force_overlay로 가격 차트에 그린다.

줄 끝 태그
  //#IND  지표판에만 남김
  //#STR  전략판에만 남김
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAG = re.compile(r"\s*//#(IND|STR)\s*$")


def build(src: pathlib.Path, want: str) -> str:
    out = []
    for line in src.read_text(encoding="utf-8").split("\n"):
        m = TAG.search(line)
        if m:
            if m.group(1) != want:
                continue
            line = line[: m.start()]
        out.append(line)
    return "\n".join(out)


DRAW = re.compile(r"\b(label\.new|line\.new|box\.new|table\.new|plot)\(")


def close_paren(text: str, i: int) -> int:
    """text[i] == '(' 의 짝 괄호 위치 (문자열 안 괄호는 무시)."""
    depth, q = 0, None
    while i < len(text):
        c = text[i]
        if q:
            if c == "\\":
                i += 1
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced")


def merged(ind: str) -> str:
    out, pos = [], 0
    for m in DRAW.finditer(ind):
        if m.start() < pos:
            continue
        end = close_paren(ind, m.end() - 1)
        out.append(ind[pos:end] + ", force_overlay = true")
        pos = end
    text = "".join(out) + ind[pos:]
    head = 'indicator("불기둥 스승님 [일봉심리 · 매물대 · 매매]", shorttitle = "불기둥 스승님", overlay = true,'
    assert head in text
    text = text.replace(head, 'indicator("불기둥 스승님 통합 [일봉심리 · 매물대 · 매매 · 거래량]", shorttitle = "불기둥 스승님 통합", overlay = false, format = format.volume,')
    return text.rstrip("\n") + "\n" + (ROOT / "tools" / "volume_section.pine").read_text(encoding="utf-8")


for src in sorted((ROOT / "pine" / "src").glob("*.src.pine")):
    name = src.name[: -len(".src.pine")]
    (ROOT / "pine" / f"{name}.pine").write_text(build(src, "IND"), encoding="utf-8")
    (ROOT / "pine" / f"{name}_통합.pine").write_text(merged(build(src, "IND")), encoding="utf-8")
    (ROOT / "pine" / f"{name}_전략.pine").write_text(build(src, "STR"), encoding="utf-8")
    print("built", name)
