import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from scipy import stats
import statsmodels.api as sm

sns.set()

st.title("データ解析ツール")

# =========================
# state 初期化
# =========================
for key in ["df", "mode", "analysis", "graphs"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.mode is None:
    st.session_state.mode = "input"

# =========================
# 入力画面
# =========================
if st.session_state.mode == "input":

    st.subheader("出力設定")

    analysis_options = st.multiselect(
        "出力する分析",
        ["基本統計", "t検定", "相関", "回帰分析"],
        default=["基本統計"]
    )

    graph_options = st.multiselect(
        "出力するグラフ",
        ["箱ひげ図", "散布図", "ヒストグラム"],
        default=["箱ひげ図"]
    )

    st.session_state.analysis = analysis_options
    st.session_state.graphs = graph_options

    method = st.radio("入力方法", ["手入力", "CSVアップロード"], index=0)

    if method == "手入力":

        n = st.number_input("データ数", 1, 50, 2)

        data = []
        for i in range(n):
            st.markdown(f"### データ {i+1}")

            c1, c2 = st.columns(2)
            with c1:
                idv = st.number_input(f"ID {i+1}", value=i+1, key=f"id_{i}")
            with c2:
                sex = st.selectbox(f"性別 {i+1}", ["M", "F"], key=f"sex_{i}")

            c3, c4 = st.columns(2)
            with c3:
                ktv = st.number_input(f"Kt/V {i+1}", value=1.0, key=f"ktv_{i}")
            with c4:
                pre = st.number_input(f"Cr_pre {i+1}", value=0.0, key=f"pre_{i}")

            post = st.number_input(f"Cr_post {i+1}", value=0.0, key=f"post_{i}")

            data.append([idv, sex, ktv, pre, post])

        if st.button("解析実行"):
            st.session_state.df = pd.DataFrame(
                data, columns=["ID", "Sex", "Kt_V", "Cr_pre", "Cr_post"]
            )
            st.session_state.mode = "result"

    else:
        file = st.file_uploader("CSVファイルを選択")
        if file:
            st.session_state.df = pd.read_csv(file)
            st.session_state.mode = "result"

# =========================
# 解析画面
# =========================
else:

    df = st.session_state.df.copy()

    st.subheader("データ")
    st.write(df)

    analysis_options = st.session_state.analysis
    graph_options = st.session_state.graphs

    # -------------------------
    # 箱ひげ図 + t検定
    # -------------------------
    if "箱ひげ図" in graph_options:

        st.subheader("Kt/V（Sex別）")

        col_g, col_s = st.columns([2, 1])

        with col_g:
            fig, ax = plt.subplots()
            sns.boxplot(x="Sex", y="Kt_V", data=df, ax=ax)

            ax.set_title("Boxplot (Kt/V by Sex)")
            ax.set_xlabel("Sex")
            ax.set_ylabel("Kt/V")

            ax.text(
                1.02, 0.5,
                "X-axis: Sex\nY-axis: Kt/V",
                transform=ax.transAxes,
                fontsize=9,
                va="center"
            )

            st.pyplot(fig)

            # ✅ 画像保存
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300)
            buf.seek(0)

            st.download_button(
                "このグラフを保存",
                buf,
                file_name="boxplot.png",
                mime="image/png"
            )

        if "t検定" in analysis_options:
            with col_s:
                g1 = df[df["Sex"]=="M"]["Kt_V"]
                g2 = df[df["Sex"]=="F"]["Kt_V"]

                if len(g1) > 1 and len(g2) > 1:
                    t, p = stats.ttest_ind(g1, g2)
                    st.write(f"t値: {t:.3f}")
                    st.write(f"p値: {p:.4f}")

    # -------------------------
    # 散布図
    # -------------------------
    if "散布図" in graph_options:

        st.subheader("散布図")

        col_g, col_s = st.columns([2, 1])

        with col_g:
            fig, ax = plt.subplots()
            sns.scatterplot(x="Cr_pre", y="Kt_V", data=df, ax=ax)
            sns.regplot(x="Cr_pre", y="Kt_V", data=df, ax=ax, scatter=False)

            ax.set_title("Scatter Plot")
            ax.set_xlabel("Cr_pre")
            ax.set_ylabel("Kt/V")

            ax.text(
                1.02, 0.5,
                "X-axis: Cr_pre\nY-axis: Kt/V",
                transform=ax.transAxes,
                fontsize=9,
                va="center"
            )

            st.pyplot(fig)

            # ✅ 画像保存
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300)
            buf.seek(0)

            st.download_button(
                "このグラフを保存",
                buf,
                file_name="scatter.png",
                mime="image/png"
            )

        if "相関" in analysis_options:
            with col_s:
                r = df["Cr_pre"].corr(df["Kt_V"])
                st.write(f"r = {r:.3f}")

    # -------------------------
    # ヒストグラム
    # -------------------------
    if "ヒストグラム" in graph_options:

        st.subheader("ヒストグラム")

        fig, ax = plt.subplots()
        ax.hist(df["Kt_V"])

        ax.set_title("Histogram")
        ax.set_xlabel("Kt/V")
        ax.set_ylabel("Frequency")

        st.pyplot(fig)

        # ✅ 画像保存
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        buf.seek(0)

        st.download_button(
            "このグラフを保存",
            buf,
            file_name="histogram.png",
            mime="image/png"
        )

    # -------------------------
    # 戻る
    # -------------------------
    keep = st.radio(
        "データを保持しますか？",
        ["保持する", "破棄する"]
    )

    if st.button("入力画面に戻る"):
        if keep == "破棄する":
            st.session_state.df = None
        st.session_state.mode = "input"
        st.rerun()
