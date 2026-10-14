"""폴더의 파일을 확장자별로 sorted/<분류>/<YYYY-MM>/ 아래에 복사한다.

사용법:
    python sort_files.py [원본폴더] [--target 결과폴더] [--rule 분류=확장자,확장자 ...]

원본폴더를 생략하면 이 스크립트 옆의 mixed/, 결과폴더를 생략하면 원본폴더 옆의 sorted/.
--rule을 하나라도 주면 기본 CATEGORIES 대신 그 규칙만 쓴다 (주어진 순서대로 표에 표시).
"""

import argparse
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "mixed"

CATEGORIES = {
    "문서": {"docx", "hwp", "pdf", "txt", "pptx"},
    "엑셀": {"xlsx", "xls", "csv"},
    "이미지": {"jpg", "jpeg", "png", "gif"},
    "압축": {"zip", "7z"},
}
OTHER = "기타"


def parse_rule(text: str) -> tuple[str, set[str]]:
    name, sep, exts = text.partition("=")
    if not sep or not name.strip():
        raise argparse.ArgumentTypeError(f"규칙 형식은 '분류=확장자,확장자' 입니다: {text}")
    return name.strip(), {e.strip().lower().lstrip(".") for e in exts.split(",") if e.strip()}


def categorize(path: Path, categories: dict[str, set[str]]) -> str:
    ext = path.suffix.lower().lstrip(".")
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return OTHER


def month_folder(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", nargs="?", type=Path, default=SOURCE_DIR)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--rule", type=parse_rule, action="append", default=[])
    args = parser.parse_args()

    source = args.source.resolve()
    target = (args.target or source.parent / "sorted").resolve()
    categories = dict(args.rule) if args.rule else CATEGORIES
    if not source.is_dir():
        parser.error(f"원본 폴더가 없습니다: {source}")
    if target == source or source in target.parents:
        parser.error("결과 폴더는 원본 폴더 밖에 있어야 합니다")

    counts = Counter()
    overwritten = 0
    for src in sorted(source.iterdir()):
        if not src.is_file():
            continue
        dest_dir = target / categorize(src, categories) / month_folder(src)
        dest_dir.mkdir(parents=True, exist_ok=True)
        overwritten += (dest_dir / src.name).exists()
        shutil.copy2(src, dest_dir / src.name)  # copy2: 수정 날짜 유지, 원본은 건드리지 않음
        counts[dest_dir.relative_to(target).as_posix()] += 1

    print(f"원본: {source}")
    print(f"결과: {target}")
    if overwritten:
        print(f"덮어쓴 파일: {overwritten}개")
    print_table(counts, categories)


def print_table(counts: Counter, categories: dict[str, set[str]]) -> None:
    order = list(categories) + [OTHER]
    rows = sorted(counts.items(), key=lambda kv: (order.index(kv[0].split("/")[0]), kv[0]))

    print(f"{'폴더':<20}{'파일 수':>8}")
    print("-" * 28)
    for category in order:
        sub_rows = [(k, v) for k, v in rows if k.split("/")[0] == category]
        if not sub_rows:
            continue
        for folder, count in sub_rows:
            print(f"{folder:<20}{count:>8}")
        print(f"{'  └ ' + category + ' 소계':<20}{sum(v for _, v in sub_rows):>8}")
    print("-" * 28)
    print(f"{'합계':<20}{sum(counts.values()):>8}")


if __name__ == "__main__":
    main()
