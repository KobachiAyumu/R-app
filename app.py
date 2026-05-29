import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import japanize_matplotlib  # 日本語対応

sns.set()

st.title("データ解析ツール")

# -------------------------
# ✅ session_state 初期化
# -------------------------
if "df" not in st.session_state:
    st.session_state.df = None

# -------------------------
# ✅ データ未確定 → 入力画面
# -------------------------
if st.session_state.df is None:

    # 分析選択
    analysis_options = st.multiselect(
        "分析内容を選択",
        ["Kt/V", "前後差", "グループ比較", "相関"],
        default=["Kt/V"]
    )

    # グラフ形式
    graph_style = st.selectbox(
        "グラフ形式",
        ["折れ線", "棒グラフ", "ヒストグラム", "散布図"]
    )

    # 入力方法
    input_method = st.radio(
        "データ入力方法",
        ["CSVアップロード", "手入力"]
    )

    # -------------------------
    # CSVアップロード
    # -------------------------
    if input_method == "CSVアップロード":
        file = st.file_uploader("CSV選択", type="csv")
        if file:
            df = pd.read_csv(file, encoding="utf-8")
            st.session_state.df = df
            st.session_state.analysis_options = analysis_options
            st.session_state.graph_style = graph_style

    # -------------------------
    # 手入力
    # -------------------------
    else:
        n = st.number_input("データ数", 1, 50, 2)

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
            st.session_state.df = pd.DataFrame(
                data, columns=["ID", "Sex", "Kt_V", "Cr_pre", "Cr_post"]
            )
            st.session_state.analysis_options = analysis_options
            st.session_state.graph_style = graph_style

# -------------------------
# ✅ データ確定 → 解析画面
# -------------------------
else:
    df = st.session_state.df
    analysis_options = st.session_state.analysis_options
    graph_style = st.session_state.graph_style

    st.subheader("データ")
    st.write(df)

    # 戻るボタン
    if st.button("データ入力に戻る"):
        st.session_state.df = None
        st.rerun()

    # 前処理
    if "Cr_pre" in df.columns:
        df["差"] = df["Cr_post"] - df["Cr_pre"]

    # -------------------------
    # ✅ グラフ作成
    # -------------------------
    for analysis in analysis_options:

        fig, ax = plt.subplots()

        # ===== Kt/V =====
        if analysis == "Kt/V" and "Kt_V" in df.columns:

            if graph_style == "折れ線":
                ax.plot(df["ID"], df["Kt_V"], marker='o')

            elif graph_style == "棒グラフ":
                ax.bar(df["ID"], df["Kt_V"])

            elif graph_style == "ヒストグラム":
                ax.hist(df["Kt_V"])

            elif graph_style == "散布図":
                ax.scatter(df["ID"], df["Kt_V"])

            # 基準ライン
            ax.axhline(1.2, color="red", linestyle="--")

            # 平均値ライン
            mean_val = df["Kt_V"].mean()
            ax.axhline(mean_val, color="green", linestyle="--", label=f"Mean={mean_val:.2f}")
            ax.legend()

            ax.set_title("Kt/V")

        # ===== 前後差 =====
        elif analysis == "前後差":

            if graph_style == "折れ線":
                ax.plot(df["ID"], df["差"], marker='o')

            elif graph_style == "棒グラフ":
                ax.bar(df["ID"], df["差"])

            elif graph_style == "ヒストグラム":
                ax.hist(df["差"])

            elif graph_style == "散布図":
                ax.scatter(df["ID"], df["差"])

            ax.set_title("Pre-Post Difference")

        # ===== グループ比較 =====
        elif analysis == "グループ比較":

            result = df.groupby("Sex")["Kt_V"].mean()

            if graph_style == "折れ線":
                ax.plot(result.index, result.values, marker='o')

            elif graph_style == "棒グラフ":
                ax.bar(result.index, result.values)

            ax.set_title("Group Comparison")

        # ===== 相関 =====
        elif analysis == "相関":

            sns.regplot(x="Cr_pre", y="Kt_V", data=df, ax=ax)

            corr = df["Cr_pre"].corr(df["Kt_V"])

            ax.set_title(f"Correlation (r={corr:.2f})")
            ax.set_xlabel("Cr_pre")
            ax.set_ylabel("Kt/V")

        # -------------------------
        # ✅ 表示
        # -------------------------
        st.pyplot(fig)

        # -------------------------
        # ✅ PNG保存
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

    # -------------------------
    # ✅ CSV保存
    # -------------------------
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "加工データCSVダウンロード",
        csv,
        "processed_data.csv",
        "text/csv"
    )
