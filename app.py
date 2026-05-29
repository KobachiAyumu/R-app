import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

from scipy import stats
import statsmodels.api as sm

sns.set()

st.title("データ解析ツール")

# -------------------------
# state
# -------------------------
for key in ["df","mode","analysis","graphs"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.mode is None:
    st.session_state.mode = "input"

# =========================
# ✅ 入力画面
# =========================
if st.session_state.mode == "input":

    st.subheader("出力設定")

    # ✅ 分析選択
    analysis_options = st.multiselect(
        "出力する分析",
        ["基本統計", "t検定", "相関", "回帰分析"],
        default=["基本統計"]
    )

    # ✅ グラフ選択
    graph_options = st.multiselect(
        "出力するグラフ",
        ["箱ひげ図", "散布図", "ヒストグラム"],
        default=["箱ひげ図"]
    )

    st.session_state.analysis = analysis_options
    st.session_state.graphs = graph_options

    method = st.radio("入力方法", ["手入力", "CSVアップロード"], index=0)

    # -------------------------
    # ✅ 手入力（全部固定）
    # -------------------------
    if method == "手入力":

        n = st.number_input("データ数",1,50,2)

        data = []
        for i in range(n):
            st.write(f"データ{i+1}")

            idv = st.number_input(f"ID{i+1}", value=i+1)
            sex = st.selectbox(f"性別{i+1}", ["M","F"])
            ktv = st.number_input(f"Kt/V{i+1}", value=1.0)
            pre = st.number_input(f"Cr_pre{i+1}", value=0.0)
            post = st.number_input(f"Cr_post{i+1}", value=0.0)

            data.append([idv,sex,ktv,pre,post])

        if st.button("解析実行"):
            st.session_state.df = pd.DataFrame(
                data, columns=["ID","Sex","Kt_V","Cr_pre","Cr_post"]
            )
            st.session_state.mode = "result"

    # -------------------------
    # ✅ CSV
    # -------------------------
    else:
        file = st.file_uploader("CSVファイル")
        if file:
            st.session_state.df = pd.read_csv(file)
            st.session_state.mode = "result"


# =========================
# ✅ 解析画面
# =========================
else:

    df = st.session_state.df.copy()

    st.subheader("データ")
    st.write(df)

    # 前処理
    df["Difference"] = df["Cr_post"] - df["Cr_pre"]

    analysis_options = st.session_state.analysis
    graph_options = st.session_state.graphs

    # -------------------------
    # ✅ 分析
    # -------------------------

    if "基本統計" in analysis_options:
        st.subheader("基本統計")
        st.write(df.describe())

    if "t検定" in analysis_options:
        st.subheader("t検定")

        g1 = df[df["Sex"]=="M"]["Kt_V"]
        g2 = df[df["Sex"]=="F"]["Kt_V"]

        if len(g1) > 1 and len(g2) > 1:
            t,p = stats.ttest_ind(g1,g2)

            st.write(f"t値 = {t:.3f}")
            st.write(f"p値 = {p:.4f}")

    if "相関" in analysis_options:
        st.subheader("相関")

        r = df["Cr_pre"].corr(df["Kt_V"])
        st.write(f"r = {r:.3f}")

    if "回帰分析" in analysis_options:
        st.subheader("回帰分析")

        X = df[["Cr_pre"]]
        X = sm.add_constant(X)
        y = df["Kt_V"]

        model = sm.OLS(y, X).fit()
        st.text(model.summary())

    # -------------------------
    # ✅ グラフ
    # -------------------------
    st.subheader("グラフ")

    if "箱ひげ図" in graph_options:
        fig, ax = plt.subplots()
        sns.boxplot(x="Sex", y="Kt_V", data=df, ax=ax)
        ax.set_title("Boxplot")
        st.pyplot(fig)

    if "散布図" in graph_options:
        fig, ax = plt.subplots()
        sns.scatterplot(x="Cr_pre", y="Kt_V", data=df, ax=ax)
        sns.regplot(x="Cr_pre", y="Kt_V", data=df, ax=ax, scatter=False)
        ax.set_title("Scatter Plot")
        st.pyplot(fig)

    if "ヒストグラム" in graph_options:
        fig, ax = plt.subplots()
        ax.hist(df["Kt_V"])
        ax.set_title("Histogram")
        st.pyplot(fig)

    # -------------------------
    # ✅ CSV
    # -------------------------
    csv = df.to_csv(index=False).encode()
    st.download_button("CSVダウンロード", csv, "data.csv")

    # -------------------------
    # ✅ 戻る
    # -------------------------
    if st.button("入力画面に戻る"):
        st.session_state.mode = "input"
        st.rerun()