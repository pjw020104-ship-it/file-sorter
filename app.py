"""sort_files.py의 분류 기능을 웹 화면으로 쓰는 Streamlit 앱.

파일을 여러 개 올리면 확장자별 폴더로 나눈 zip 파일을 내려받을 수 있다.
(폴더 경로로 분류하는 로컬 버전은 app_local.py)

실행:
    streamlit run app.py
"""

import io
import zipfile
from collections import Counter
from pathlib import PurePath

import streamlit as st

from sort_files import CATEGORIES, OTHER, categorize


def unique_name(name: str, used: set[str]) -> str:
    # 같은 폴더에 같은 이름이 오면 "보고서 (2).pdf"처럼 번호를 붙여 둘 다 남긴다
    if name.lower() not in used:
        return name
    stem, suffix = PurePath(name).stem, PurePath(name).suffix
    n = 2
    while f"{stem} ({n}){suffix}".lower() in used:
        n += 1
    return f"{stem} ({n}){suffix}"


def make_plan(files) -> list[dict]:
    plan = []
    used: dict[str, set[str]] = {}
    for f in sorted(files, key=lambda f: f.name):
        folder = categorize(PurePath(f.name), CATEGORIES)
        names = used.setdefault(folder, set())
        new_name = unique_name(f.name, names)
        names.add(new_name.lower())
        plan.append({
            "파일 이름": f.name,
            "들어갈 폴더": folder,
            "비고": f"이름이 겹쳐 '{new_name}'(으)로 저장" if new_name != f.name else "",
            "_file": f,
            "_name": new_name,
        })
    return plan


def make_zip(plan: list[dict]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in plan:
            zf.writestr(f"{p['들어갈 폴더']}/{p['_name']}", p["_file"].getvalue())
    return buffer.getvalue()


def count_table(counts: Counter) -> list[dict]:
    order = list(CATEGORIES) + [OTHER]
    rows = [{"폴더": k, "파일 수": counts[k]} for k in order if counts[k]]
    rows.append({"폴더": "합계", "파일 수": sum(counts.values())})
    return rows


st.set_page_config(page_title="파일 자동 분류", page_icon="📂")
st.title("📂 파일 자동 분류")
st.write(
    "파일을 올리면 종류별(문서 / 엑셀 / 이미지 / 압축 / 기타) 폴더로 나눠 "
    "**zip 파일 하나**로 만들어 드립니다. 올린 파일은 서버에 저장되지 않습니다."
)

st.subheader("1. 분류할 파일 올리기")
files = st.file_uploader(
    "파일을 끌어다 놓거나 'Browse files'를 눌러 여러 개를 한꺼번에 선택하세요.",
    accept_multiple_files=True,
)
with st.expander("어떤 확장자가 어느 폴더로 가나요?"):
    st.table([{"폴더": c, "확장자": ", ".join(sorted(e))} for c, e in CATEGORIES.items()]
             + [{"폴더": OTHER, "확장자": "위에 없는 나머지 모두"}])

if not files:
    st.info("파일을 올리면 분류 결과와 내려받기 버튼이 나타납니다.")
    st.stop()

plan = make_plan(files)
counts = Counter(p["들어갈 폴더"] for p in plan)

st.subheader("2. 분류 결과 확인")
st.success(f"파일 **{len(plan)}개**를 아래처럼 나눴습니다.")
st.dataframe(count_table(counts), hide_index=True)
renamed = sum(1 for p in plan if p["비고"])
if renamed:
    st.warning(f"같은 이름의 파일이 {renamed}개 있어 이름 뒤에 번호를 붙였습니다. 아래 표의 '비고'를 확인하세요.")
with st.expander("파일별 결과 보기", expanded=bool(renamed)):
    st.dataframe([{k: v for k, v in p.items() if not k.startswith("_")} for p in plan],
                 width="stretch", hide_index=True)

st.subheader("3. 내려받기")
st.download_button(
    "⬇ 분류 결과 zip 내려받기",
    data=make_zip(plan),
    file_name="분류결과.zip",
    mime="application/zip",
    type="primary",
    width="stretch",
)
st.caption("zip을 풀면 종류별 폴더 안에 파일이 들어 있습니다.")
