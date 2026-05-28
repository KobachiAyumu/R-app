import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib  # ← これが最強対策
 
# -------------------------
# ✅ 描画設定
# -------------------------
sns.set()



# -------------------------
# ✅ Excel風スタイル
# -------------------------
plt.style.use("default")
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "font.size": 10
})

# -------------------------
# ✅ タイトル
# -------------------------
st.title("データ解析ツール")

# -------------------------
# ✅ 入力方法選択
# -------------------------
input_method = st.radio(
    "データ入力方法を選択",
    ["CSVアップロード", "手入力"]
)

df = None

# -------------------------
# ✅ CSV入力
# -------------------------
if input_method == "CSVアップロード":
    uploaded_file = st.file_uploader("CSVファイルを選択", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

# -------------------------
# ✅ 手入力
# -------------------------
elif input_method == "手入力":
    st.subheader("データ入力")

    num_rows = st.number_input("データ数", 1, 50, 5)

    data = []

    for i in range(num_rows):
        st.write(f"データ {i+1}")

        id_val = st.number_input(f"ID_{i+1}",min_value=1,step=1,format="%d",key=f"id{i+1}")
        sex = st.selectbox(f"Sex_{i+1}", ["M", "F"], key=f"sex{i+1}")
        ktv = st.number_input(f"Kt_V_{i+1}", key=f"ktv{i+1}")
        pre = st.number_input(f"Cr_pre_{i+1}", key=f"pre{i+1}")
        post = st.number_input(f"Cr_post_{i+1}", key=f"post{i+1}")

        data.append([id_val, sex, ktv, pre, post])

    if st.button("データ確定"):
        df = pd.DataFrame(
            data,
            columns=["ID", "Sex", "Kt_V", "Cr_pre", "Cr_post"]
        )

# -------------------------
# ✅ 解析処理
# -------------------------
if df is not None:

    st.subheader("データ表示")
    st.write(df)

    # -------------------------
    # 基本統計
    # -------------------------
    st.subheader("基本統計")
    st.write(df.describe())

    # -------------------------
    # ✅ Kt/V判定
    # -------------------------
    if "Kt_V" in df.columns:
        st.subheader("Kt/V判定（1.2以上）")

        df["KtV判定"] = df["Kt_V"].apply(
            lambda x: "OK" if x >= 1.2 else "低値"
        )

        st.write(df[["Kt_V", "KtV判定"]])

        fig, ax = plt.subplots()
        ax.hist(df["Kt_V"], bins=10, color="#4472C4", edgecolor="black")
        ax.axvline(1.2, color="red", linestyle="--", linewidth=2)
        ax.set_title("Kt/V 分布")
        ax.set_xlabel("Kt/V")
        ax.set_ylabel("頻度")

        st.pyplot(fig)

    # -------------------------
    # ✅ 透析前後差
    # -------------------------
    if "Cr_pre" in df.columns and "Cr_post" in df.columns:
        st.subheader("透析前後差")

        df["差"] = df["Cr_post"] - df["Cr_pre"]
        st.write(df[["Cr_pre", "Cr_post", "差"]])

        fig, ax = plt.subplots()
        ax.hist(df["差"], bins=10, color="#70AD47", edgecolor="black")
        ax.set_title("前後差分布")

        st.pyplot(fig)

    # -------------------------
    # ✅ グループ比較
    # -------------------------
    if "Sex" in df.columns and "Kt_V" in df.columns:
        st.subheader("グループ比較")

        result = df.groupby("Sex")["Kt_V"].mean()

        st.write("平均値")
        st.write(result)

        fig, ax = plt.subplots()
        sns.boxplot(
            x="Sex",
            y="Kt_V",
            data=df,
            ax=ax,
            color="#5B9BD5"
        )

        ax.set_title("グループ比較")

        st.pyplot(fig)