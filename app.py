import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# 日本語フォント
plt.rcParams['font.family'] = 'IPAexGothic'
sns.set()

st.title("データ解析ツール（プロ版）")

# -------------------------
# ✅ 分析選択（複数可）
# -------------------------
analysis_options = st.multiselect(
    "分析内容を選択",
    ["Kt/V", "前後差", "グループ比較", "相関"],
    default=["Kt/V"]
)

# -------------------------
# ✅ グラフ形式
# -------------------------
graph_style = st.selectbox(
    "グラフ形式",
    ["折れ線", "棒グラフ", "ヒストグラム", "散布図"]
)

# -------------------------
# ✅ 入力方法
# -------------------------
input_method = st.radio(
    "データ入力方法",
    ["CSVアップロード", "手入力"]
)

df = None

# -------------------------
# CSV
# -------------------------
if input_method == "CSVアップロード":
    file = st.file_uploader("CSV選択", type="csv")
    if file:
        df = pd.read_csv(file, encoding="utf-8")

# -------------------------
# 手入力
# -------------------------
else:
    n = st.number_input("データ数", 1, 50, 5)

    data = []
    for i in range(n):
        st.write(f"データ{i+1}")

        id_val = st.number_input(f"ID{i}", 1, key=f"id{i}")
        sex = st.selectbox(f"Sex{i}", ["M", "F"], key=f"sex{i}")
        ktv = st.number_input(f"Kt_V{i}", key=f"ktv{i}")
        pre = st.number_input(f"Cr_pre{i}", key=f"pre{i}")
        post = st.number_input(f"Cr_post{i}", key=f"post{i}")

        data.append([id_val, sex, ktv, pre, post])

    if st.button("データ確定"):
        df = pd.DataFrame(data, columns=["ID","Sex","Kt_V","Cr_pre","Cr_post"])

# -------------------------
# ✅ 解析
# -------------------------
if df is not None:

    st.subheader("データ")
    st.write(df)

    # 前処理
    if "Cr_pre" in df.columns:
        df["差"] = df["Cr_post"] - df["Cr_pre"]

    # -------------------------
    # ✅ グラフ作成ループ
    # -------------------------
    for analysis in analysis_options:

        fig, ax = plt.subplots()

        # ===== Kt/V =====
        if analysis == "Kt/V" and "Kt_V" in df.columns:

            if graph_style == "折れ線":
                ax.plot(df.index, df["Kt_V"], marker='o')

            elif graph_style == "棒グラフ":
                ax.bar(df.index, df["Kt_V"])

            elif graph_style == "ヒストグラム":
                ax.hist(df["Kt_V"])

            elif graph_style == "散布図":
                ax.scatter(df.index, df["Kt_V"])

            ax.axhline(1.2, color="red", linestyle="--")
            ax.set_title("Kt/V")

        # ===== 前後差 =====
        elif analysis == "前後差":

            if graph_style == "折れ線":
                ax.plot(df.index, df["差"], marker='o')

            elif graph_style == "棒グラフ":
                ax.bar(df.index, df["差"])

            elif graph_style == "ヒストグラム":
                ax.hist(df["差"])

            elif graph_style == "散布図":
                ax.scatter(df.index, df["差"])

            ax.set_title("前後差")

        # ===== グループ比較 =====
        elif analysis == "グループ比較":

            result = df.groupby("Sex")["Kt_V"].mean()

            if graph_style == "折れ線":
                ax.plot(result.index, result.values, marker='o')

            elif graph_style == "棒グラフ":
                ax.bar(result.index, result.values)

            ax.set_title("グループ比較")

        # ===== 相関 =====
        elif analysis == "相関":

            ax.scatter(df["Cr_pre"], df["Kt_V"])
            ax.set_xlabel("Cr_pre")
            ax.set_ylabel("Kt/V")
            ax.set_title("相関")

        # -------------------------
        # ✅ 表示
        # -------------------------
        st.pyplot(fig)

        # -------------------------
        # ✅ PNG保存（追加部分）
        # -------------------------
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        buf.seek(0)

        st.download_button(
            label=f"{analysis} をPNGで保存",
            data=buf,
            file_name=f"{analysis}_{graph_style}.png",
            mime="image/png"
        )