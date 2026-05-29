import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

sns.set()

st.title("データ解析ツール（完全版）")

# -------------------------
# ✅ state
# -------------------------
for key in ["df","input_data","mode"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.mode is None:
    st.session_state.mode = "input"

# =========================
# ✅ 入力画面
# =========================
if st.session_state.mode == "input":

    method = st.radio("入力方法", ["手入力","CSVアップロード"], index=0)

    if method == "手入力":

        n = st.number_input("データ数",1,50,5)
        data = []

        for i in range(n):
            saved = None
            if st.session_state.input_data and i < len(st.session_state.input_data):
                saved = st.session_state.input_data[i]

            idv = st.number_input(f"ID{i+1}", value=saved[0] if saved else i+1)
            sex = st.selectbox(f"性別{i+1}", ["M","F"],
                                index=["M","F"].index(saved[1]) if saved else 0)
            ktv = st.number_input(f"Kt/V{i+1}", value=saved[2] if saved else 1.0)
            pre = st.number_input(f"Cr_pre{i+1}", value=saved[3] if saved else 0.0)
            post = st.number_input(f"Cr_post{i+1}", value=saved[4] if saved else 0.0)

            data.append([idv,sex,ktv,pre,post])

        if st.button("解析実行"):
            st.session_state.df = pd.DataFrame(
                data, columns=["ID","Sex","Kt_V","Cr_pre","Cr_post"]
            )
            st.session_state.input_data = data
            st.session_state.mode = "result"

    else:
        file = st.file_uploader("CSVファイルを選択")
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

    # 差分
    df["Difference"] = df["Cr_post"] - df["Cr_pre"]

    # -------------------------
    # ✅ フィルタ
    # -------------------------
    if "Sex" in df.columns:
        sex_filter = st.multiselect("性別フィルタ", df["Sex"].unique(), default=df["Sex"].unique())
        df = df[df["Sex"].isin(sex_filter)]

    # -------------------------
    # ✅ 記述統計
    # -------------------------
    st.subheader("基本統計量")
    st.write(df.describe())

    # -------------------------
    # ✅ 正規性検定
    # -------------------------
    st.subheader("正規性検定（Shapiro-Wilk）")

    if len(df["Kt_V"]) > 2:
        stat, p = stats.shapiro(df["Kt_V"])
        st.write(f"p値 = {p:.4f}")

    # -------------------------
    # ✅ t検定
    # -------------------------
    st.subheader("t検定")

    g1 = df[df["Sex"]=="M"]["Kt_V"]
    g2 = df[df["Sex"]=="F"]["Kt_V"]

    if len(g1)>1 and len(g2)>1:
        t,p = stats.ttest_ind(g1,g2)

        st.write(f"t値 = {t:.3f}")
        st.write(f"p値 = {p:.4f}")

        if p < 0.05:
            st.success("有意差あり")
        else:
            st.info("有意差なし")

    # -------------------------
    # ✅ Mann-Whitney
    # -------------------------
    st.subheader("Mann-Whitney検定")

    if len(g1)>1 and len(g2)>1:
        u,p = stats.mannwhitneyu(g1,g2)
        st.write(f"U = {u:.3f}, p = {p:.4f}")

    # -------------------------
    # ✅ ANOVA
    # -------------------------
    st.subheader("分散分析（ANOVA）")

    try:
        model = smf.ols("Kt_V ~ Sex", data=df).fit()
        anova = sm.stats.anova_lm(model)
        st.write(anova)
    except:
        st.write("実行不可")

    # -------------------------
    # ✅ 相関
    # -------------------------
    st.subheader("相関分析")

    corr = df.corr(numeric_only=True)
    st.write(corr)

    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, ax=ax)
    ax.set_title("Correlation Heatmap")  # ✅ 英語
    st.pyplot(fig)

    # -------------------------
    # ✅ 多変量回帰
    # -------------------------
    st.subheader("多変量回帰")

    X = df[["Cr_pre","Cr_post"]]
    X = sm.add_constant(X)
    y = df["Kt_V"]

    model = sm.OLS(y,X).fit()
    st.text(model.summary())

    # -------------------------
    # ✅ VIF
    # -------------------------
    st.subheader("VIF（多重共線性）")

    vif_data = pd.DataFrame()
    vif_data["変数"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values,i) for i in range(X.shape[1])]
    st.write(vif_data)

    # -------------------------
    # ✅ グラフ選択
    # -------------------------
    st.subheader("グラフ")

    selected_graphs = st.multiselect(
        "表示するグラフ",
        ["箱ひげ図","散布図","ヒストグラム"],
        default=["箱ひげ図"]
    )

    # ✅ 箱ひげ
    if "箱ひげ図" in selected_graphs:
        fig, ax = plt.subplots()
        sns.boxplot(x="Sex", y="Kt_V", data=df, ax=ax)
        ax.set_title("Boxplot (Kt/V)")  # 英語
        st.pyplot(fig)

    # ✅ 散布図
    if "散布図" in selected_graphs:
        fig, ax = plt.subplots()
        sns.scatterplot(x="Cr_pre", y="Kt_V", data=df, ax=ax)
        sns.regplot(x="Cr_pre", y="Kt_V", data=df, ax=ax, scatter=False)
        ax.set_title("Scatter Plot (Regression)")  # 英語
        st.pyplot(fig)

    # ✅ ヒストグラム
    if "ヒストグラム" in selected_graphs:
        fig, ax = plt.subplots()
        ax.hist(df["Kt_V"])
        ax.set_title("Histogram")  # 英語
        st.pyplot(fig)

    # -------------------------
    # ✅ 保存
    # -------------------------
    st.subheader("データ保存")

    csv = df.to_csv(index=False).encode()
    st.download_button("CSVダウンロード", csv, "data.csv")

    # -------------------------
    # ✅ 戻る
    # -------------------------
    if st.button("入力画面へ戻る"):
        st.session_state.mode = "input"
        st.rerun()