# 📂 파일 자동 분류 (file-sorter)

파일을 여러 개 올리면 확장자에 따라 **문서 / 엑셀 / 이미지 / 압축 / 기타** 폴더로 나눈 zip 파일을 내려받는 Streamlit 앱입니다.

| 폴더 | 확장자 |
|---|---|
| 문서 | docx, hwp, pdf, pptx, txt |
| 엑셀 | csv, xls, xlsx |
| 이미지 | gif, jpeg, jpg, png |
| 압축 | 7z, zip |
| 기타 | 위에 없는 나머지 |

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

- `sort_files.py`: 분류 규칙과 명령줄 버전 (`python sort_files.py 폴더경로`)
- 올린 파일은 메모리에서만 처리하고 서버에 저장하지 않습니다.
