# 🏭 제조 품질 현황 대시보드

AI 비전검사 PoC 준비를 위한 품질 데이터 모니터링용 Streamlit 대시보드입니다.
CSV를 업로드하지 않아도 샘플 데이터로 바로 동작합니다.

## 주요 기능

- CSV 업로드 (없으면 코드에서 샘플 데이터 300건 자동 생성)
- 데이터 미리보기
- KPI 카드: 전체 검사 / 정상 / 불량 / 불량률
- 날짜별 검사·불량 건수 선그래프
- 불량 유형별 건수 막대그래프
- 최근 검사 결과 10건 표 (✅ OK / ❌ NG 표시)
- 사이드바 필터: 날짜, 제품, 검사 결과

## 파일 구조

```
quality-dashboard/
├── app.py              # 대시보드 코드 (이 파일 하나가 앱 전체)
├── requirements.txt    # 필요한 파이썬 패키지 목록
├── sample_data.csv     # 업로드 테스트용 예시 CSV
└── README.md           # 이 문서
```

## CSV 형식

아래 5개 컬럼이 반드시 있어야 합니다. (순서는 상관없음)

| 컬럼 | 설명 | 예시 |
|---|---|---|
| inspection_date | 검사 날짜 | 2026-10-01 |
| product_id | 제품 ID | P001 |
| result | 검사 결과 (OK 또는 NG) | NG |
| defect_type | 불량 유형 (정상이면 None) | Scratch |
| confidence | 판정 신뢰도 (0~1) | 0.91 |

엑셀에서 저장한 한글 CSV(CP949)도 읽을 수 있습니다.

---

## 1. 로컬에서 실행하기 (Windows 11 + VS Code)

1. VS Code에서 프로젝트 폴더를 엽니다. (`파일 → 폴더 열기`)
2. 터미널을 엽니다. (`` Ctrl + ` ``)
3. 가상환경을 만들고 켭니다.

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

   > ⚠️ "스크립트를 실행할 수 없으므로…" 오류가 나면 아래 명령을 한 번 실행한 뒤 다시 activate 하세요.
   > ```powershell
   > Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   > ```

4. 패키지를 설치합니다.

   ```powershell
   pip install -r requirements.txt
   ```

5. 앱을 실행합니다.

   ```powershell
   streamlit run app.py
   ```

   브라우저에서 `http://localhost:8501` 이 자동으로 열립니다. 종료는 터미널에서 `Ctrl + C`.

---

## 2. GitHub에 올리기

### 방법 A — 웹 화면으로 업로드 (가장 쉬움)

1. https://github.com 로그인 → 오른쪽 위 `+` → **New repository**
2. 이름 입력 (예: `quality-dashboard`), **Public** 선택 → **Create repository**
3. **uploading an existing file** 클릭 → `app.py`, `requirements.txt`, `README.md`, `sample_data.csv` 를 끌어다 놓기
4. **Commit changes** 클릭

> `.venv` 폴더는 올리지 마세요. (용량이 크고 배포에 필요 없음)

### 방법 B — Git 명령어로 업로드

Git이 설치되어 있어야 합니다. (https://git-scm.com)

```powershell
# .venv 폴더가 GitHub에 올라가지 않도록 설정
echo .venv/ > .gitignore

git init
git add .
git commit -m "제조 품질 현황 대시보드 첫 버전"
git branch -M main
git remote add origin https://github.com/<내아이디>/quality-dashboard.git
git push -u origin main
```

---

## 3. Streamlit Community Cloud에 배포하기

1. https://share.streamlit.io 접속 → **GitHub 계정으로 로그인**
2. **Create app** (또는 New app) 클릭 → "Deploy a public app from GitHub" 선택
3. 다음 항목 입력
   - **Repository**: `<내아이디>/quality-dashboard`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - (선택) **App URL**: 원하는 주소
   - (선택) Advanced settings에서 Python 버전 선택 — 기본값을 그대로 써도 됩니다
4. **Deploy** 클릭 → 1~3분 뒤 `https://<앱이름>.streamlit.app` 주소로 접속 가능

이후 GitHub에 코드를 수정해서 올리면 앱이 자동으로 다시 배포됩니다.

---

## 자주 발생하는 문제

| 증상 | 원인 / 해결 |
|---|---|
| `'streamlit'은(는) 내부 또는 외부 명령…이 아닙니다` | 가상환경이 꺼져 있음 → `.venv\Scripts\activate` 후 다시 실행, 또는 `python -m streamlit run app.py` |
| `ModuleNotFoundError: No module named 'pandas'` | `pip install -r requirements.txt` 를 실행하지 않음 |
| "CSV에 필요한 컬럼이 없습니다" | CSV 첫 줄(헤더)의 컬럼 이름 확인 |
| 그래프나 KPI가 비어 있음 | 사이드바 필터에서 제품/결과가 모두 해제되었는지 확인 |
| Cloud 배포 시 `ModuleNotFoundError` | `requirements.txt` 가 저장소 최상위 폴더(app.py와 같은 위치)에 있는지 확인 |
| Cloud에서 파일을 못 찾음 | Main file path 가 `app.py` 로 정확히 입력됐는지 확인 |
