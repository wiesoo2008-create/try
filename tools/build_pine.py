"""스승님 지표/전략 빌드: pine/src/*.src.pine → pine/ 아래 지표판과 전략판.

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


for src in sorted((ROOT / "pine" / "src").glob("*.src.pine")):
    name = src.name[: -len(".src.pine")]
    (ROOT / "pine" / f"{name}.pine").write_text(build(src, "IND"), encoding="utf-8")
    (ROOT / "pine" / f"{name}_전략.pine").write_text(build(src, "STR"), encoding="utf-8")
    print("built", name)
