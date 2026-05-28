import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

plt.rcParams['font.family'] = 'IPAexGothic'

st.title("データ解析ツール")

input_method = st.radio(
    "データ入力方法を選択",
    ["CSVアップロード", "手入力"]
)

df = None

# -------------------------
# CSV入力
# -------------------------
if input_method == "CSVアップロード":
    uploaded_file = st.file_uploader("CSVファイルを選択", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding="utf-8")

# -------------------------
# 手入力
# -------------------------
elif input_method == "手入力":
    st.subheader("データ入力")

    num_rows = st.number_input("データ数", 1, 50, 5)

    data = []

    for i in range(num_rows):
        st.write(f"データ {i+1}")

        id_val = st.number_input(f"ID_{i+1}", min_value=1, step=1, format="%d", key=f"id{i}")
        sex = st.selectbox(f"Sex_{i+1}", ["M", "F"], key=f"sex{i}")
        ktv = st.number_input(f"Kt_V_{i+1}", key=f"ktv{i}")
        pre = st.number_input(f"Cr_pre_{i+1}", key=f"pre{i}")
        post = st.number_input(f"Cr_post_{i+1}", key=f"post{i}")

        data.append([id_val, sex, ktv, pre, post])

    if st.button("データ確定"):
        df = pd.DataFrame(
            data,
            columns=["ID", "Sex", "Kt_V", "Cr_pre", "Cr_post"]
        )

# -------------------------
# 解析処理
# -------------------------
if df is not None:
    st.subheader("データ表示")
    st.write(df)

    st.subheader("基本統計")
    st.write(df.describe())

    # -------------------------
    # ✅ Kt/V（折れ線）
    # -------------------------
    if "Kt_V" in df.columns:
        st.subheader("Kt/V 分布")

        fig, ax = plt.subplots()
        ax.plot(df.index, df["Kt_V"], marker='o', color="#4472C4")
        ax.axhline(1.2, color="red", linestyle="--")
        ax.set_title("Kt/V Distribution")
        ax.set_xlabel("Index")
        ax.set_ylabel("Kt/V")

        st.pyplot(fig)

    # -------------------------
    # ✅ 前後差（折れ線）
    # -------------------------
    if "Cr_pre" in df.columns and "Cr_post" in df.columns:
        st.subheader("前後差分布")

        df["差"] = df["Cr_post"] - df["Cr_pre"]

        fig, ax = plt.subplots()
        ax.plot(df.index, df["差"], marker='o', color="#70AD47")
        ax.set_title("Distribution of Pre-Post Differences")
        ax.set_xlabel("Index")
        ax.set_ylabel("Difference")

        st.pyplot(fig)

    # -------------------------
    # ✅ グループ比較（折れ線）
    # -------------------------
    if "Sex" in df.columns and "Kt_V" in df.columns:
        st.subheader("グループ比較")

        result = df.groupby("Sex")["Kt_V"].mean()

        fig, ax = plt.subplots()
        ax.plot(result.index, result.values, marker='o', color="#5B9BD5")
        ax.set_title("Group Comparison")
        ax.set_xlabel("Sex")
        ax.set_ylabel("Mean")

        st.pyplot(fig)
