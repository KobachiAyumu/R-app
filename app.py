import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'IPAexGothic'
sns.set()

st.title("データ解析ツール")

# -------------------------
# ✅ グラフ選択（先に置く！）
# -------------------------
selected_graphs = st.multiselect(
    "表示するグラフを選択（複数可）",
    ["Kt/V", "前後差", "グループ比較"],
    default=["Kt/V"]
)

# -------------------------
# ✅ 入力方法
# -------------------------
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
# ✅ 解析
# -------------------------
if df is not None:

    st.subheader("データ表示")
    st.write(df)

    st.subheader("基本統計")
    st.write(df.describe())

    # -------------------------
    # ✅ 選択されたグラフを全部表示
    # -------------------------
    for graph_type in selected_graphs:

        # -------------------------
        # ✅ Kt/V
        # -------------------------
        if graph_type == "Kt/V" and "Kt_V" in df.columns:

            st.subheader("Kt/V 分布")

            fig, ax = plt.subplots()
            ax.plot(df.index, df["Kt_V"], marker='o')

            ax.axhline(1.2, color="red", linestyle="--")
            ax.set_title("Kt/V Distribution")

            st.pyplot(fig)

        # -------------------------
        # ✅ 前後差
        # -------------------------
        if graph_type == "前後差" and "Cr_pre" in df.columns:

            st.subheader("前後差分布")

            df["差"] = df["Cr_post"] - df["Cr_pre"]

            fig, ax = plt.subplots()
            ax.plot(df.index, df["差"], marker='o')

            ax.set_title("Distribution of Pre-Post Differences")

            st.pyplot(fig)

        # -------------------------
        # ✅ グループ比較
        # -------------------------
        if graph_type == "グループ比較" and "Sex" in df.columns:

            st.subheader("グループ比較")

            result = df.groupby("Sex")["Kt_V"].mean()

            fig, ax = plt.subplots()
            ax.plot(result.index, result.values, marker='o')

            ax.set_title("Group Comparison")

            st.pyplot(fig)
