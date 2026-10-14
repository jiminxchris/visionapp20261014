"""
제조 품질 현황 대시보드
- CSV를 업로드하거나, 업로드하지 않으면 샘플 데이터로 동작합니다.
- 실행: streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st

# CSV에 반드시 있어야 하는 컬럼
REQUIRED_COLUMNS = ["inspection_date", "product_id", "result", "defect_type", "confidence"]

st.set_page_config(page_title="제조 품질 현황 대시보드", page_icon="🏭", layout="wide")


# ─────────────────────────────────────────
# 1. 데이터 준비 함수
# ─────────────────────────────────────────
@st.cache_data
def make_sample_data(n_rows=300, seed=42):
    """CSV가 없을 때 사용할 샘플 데이터를 만든다. (seed 고정 → 매번 같은 데이터)"""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-10-01", periods=14, freq="D")
    products = ["P001", "P002", "P003", "P004", "P005"]
    defect_types = ["Scratch", "Crack", "Dent", "Stain"]

    df = pd.DataFrame({
        "inspection_date": rng.choice(dates, n_rows),
        "product_id": rng.choice(products, n_rows),
        "result": rng.choice(["OK", "NG"], n_rows, p=[0.88, 0.12]),
    })
    is_ng = df["result"] == "NG"
    df["defect_type"] = np.where(is_ng, rng.choice(defect_types, n_rows), "None")
    df["confidence"] = np.where(
        is_ng, rng.uniform(0.75, 0.95, n_rows), rng.uniform(0.90, 0.99, n_rows)
    ).round(2)
    return df.sort_values("inspection_date").reset_index(drop=True)


def read_csv_file(uploaded_file):
    """업로드한 CSV를 읽는다. 엑셀에서 저장한 한글 CSV(cp949)도 읽을 수 있게 처리."""
    try:
        return pd.read_csv(uploaded_file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        uploaded_file.seek(0)  # 파일을 처음부터 다시 읽기
        return pd.read_csv(uploaded_file, encoding="cp949")


def clean_data(df):
    """컬럼 확인 + 자료형 정리. (정리된 데이터, 오류 메시지)를 돌려준다."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return None, f"CSV에 필요한 컬럼이 없습니다: {', '.join(missing)}"

    df["inspection_date"] = pd.to_datetime(df["inspection_date"], errors="coerce").dt.normalize()
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["result"] = df["result"].astype(str).str.strip().str.upper()
    df["defect_type"] = df["defect_type"].fillna("None").astype(str).str.strip()
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")

    # 날짜가 잘못됐거나 결과가 OK/NG가 아닌 행은 제외
    df = df.dropna(subset=["inspection_date"])
    df = df[df["result"].isin(["OK", "NG"])]
    return df, None


# ─────────────────────────────────────────
# 2. 사이드바: CSV 업로드
# ─────────────────────────────────────────
st.sidebar.header("📁 데이터")
uploaded_file = st.sidebar.file_uploader("CSV 파일 업로드", type="csv")

if uploaded_file is None:
    raw_df = make_sample_data()
    st.sidebar.info("CSV가 없어서 샘플 데이터를 사용 중입니다.")
else:
    try:
        raw_df = read_csv_file(uploaded_file)
    except Exception as e:
        st.error(f"CSV 파일을 읽지 못했습니다: {e}")
        st.stop()

df, error = clean_data(raw_df)
if error:
    st.error(error)
    st.stop()
if df.empty:
    st.warning("사용할 수 있는 데이터가 없습니다. CSV 내용을 확인해 주세요.")
    st.stop()


# ─────────────────────────────────────────
# 3. 사이드바: 필터
# ─────────────────────────────────────────
st.sidebar.header("🔍 필터")

min_date = df["inspection_date"].min().date()
max_date = df["inspection_date"].max().date()
date_range = st.sidebar.date_input(
    "날짜 범위", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
# 날짜를 하나만 고른 상태(선택 중)일 때도 오류가 나지 않게 처리
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

all_products = sorted(df["product_id"].unique())
selected_products = st.sidebar.multiselect("제품", all_products, default=all_products)

selected_results = st.sidebar.multiselect("검사 결과", ["OK", "NG"], default=["OK", "NG"])

filtered = df[
    (df["inspection_date"].dt.date >= start_date)
    & (df["inspection_date"].dt.date <= end_date)
    & (df["product_id"].isin(selected_products))
    & (df["result"].isin(selected_results))
]


# ─────────────────────────────────────────
# 4. 제목 + 데이터 미리보기
# ─────────────────────────────────────────
st.title("🏭 제조 품질 현황 대시보드")
st.caption("AI 비전검사 PoC 준비를 위한 품질 데이터 모니터링")

with st.expander("📄 데이터 미리보기 (원본 상위 20행)"):
    st.dataframe(raw_df.head(20), hide_index=True)

if filtered.empty:
    st.warning("선택한 필터 조건에 맞는 데이터가 없습니다. 사이드바 필터를 조정해 주세요.")
    st.stop()


# ─────────────────────────────────────────
# 5. 상단: KPI 카드
# ─────────────────────────────────────────
total_count = len(filtered)
ok_count = int((filtered["result"] == "OK").sum())
ng_count = int((filtered["result"] == "NG").sum())
defect_rate = ng_count / total_count * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 검사", f"{total_count:,}건")
col2.metric("✅ 정상 (OK)", f"{ok_count:,}건")
col3.metric("❌ 불량 (NG)", f"{ng_count:,}건")
col4.metric("불량률", f"{defect_rate:.1f}%")

st.divider()


# ─────────────────────────────────────────
# 6. 중단: 그래프 2개
# ─────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("📈 날짜별 검사 현황")
    daily = (
        filtered.assign(
            검사건수=1,
            불량건수=(filtered["result"] == "NG").astype(int),
        )
        .groupby("inspection_date")[["검사건수", "불량건수"]]
        .sum()
    )
    st.line_chart(daily)

with right:
    st.subheader("📊 불량 유형별 건수")
    defect_counts = filtered.loc[filtered["result"] == "NG", "defect_type"].value_counts()
    if defect_counts.empty:
        st.info("선택한 조건에 불량(NG) 데이터가 없습니다.")
    else:
        st.bar_chart(defect_counts.rename("불량 건수"))

st.divider()


# ─────────────────────────────────────────
# 7. 하단: 최근 검사 결과 10건
# ─────────────────────────────────────────
st.subheader("🗂️ 최근 검사 결과 10건")

recent = filtered.sort_values("inspection_date", ascending=False).head(10).copy()
recent["판정"] = recent["result"].map({"OK": "✅ OK", "NG": "❌ NG"})
recent["inspection_date"] = recent["inspection_date"].dt.strftime("%Y-%m-%d")

st.dataframe(
    recent[["inspection_date", "product_id", "판정", "defect_type", "confidence"]],
    hide_index=True,
)
