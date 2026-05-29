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
for key in ["df","input_data","mode","columns_selected"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.mode is None:
    st.session_state.mode = "input"

# =========================
# ✅ 入力画面
# =========================
if st.session_state.mode == "input":

    st.subheader("データ設定")

    # ✅ ① データ項目選択
    column_options = ["ID","Sex","Kt_V","Cr_pre","Cr_post"]

    selected_columns = st.multiselect(
        "使用するデータ項目を選択",
        column_options,
        default=st.session_state.columns_selected or ["ID","Sex","Kt_V"]
    )

    # 保存
    st.session_state.columns_selected = selected_columns

    method = st.radio("入力方法", ["手入力","CSVアップロード"], index=0)

    # -------------------------
    # ✅ 手入力
    # -------------------------
    if method == "手入力":

        # ✅ ② 初期値2
        n = st.number_input("データ数",1,50,2)

        data = []

        for i in range(n):
            row = []
            st.write(f"データ{i+1}")

            saved = None
            if st.session_state.input_data and i < len(st.session_state.input_data):
                saved = st.session_state.input_data[i]

            col_idx = 0

            if "ID" in selected_columns:
                val = st.number_input(f"ID{i+1}",
                                      value=saved[col_idx] if saved else i+1)
                row.append(val)
                col_idx += 1

            if "Sex" in selected_columns:
                val = st.selectbox(f"性別{i+1}", ["M","F"])
                row.append(val)
                col_idx += 1

            if "Kt_V" in selected_columns:
                val = st.number_input(f"Kt/V{i+1}", value=1.0)
                row.append(val)
                col_idx += 1

            if "Cr_pre" in selected_columns:
                val = st.number_input(f"Cr_pre{i+1}", value=0.0)
                row.append(val)
                col_idx += 1

            if "Cr_post" in selected_columns:
                val = st.number_input(f"Cr_post{i+1}", value=0.0)
                row.append(val)
                col_idx += 1

            data.append(row)

        if st.button("解析実行"):
            st.session_state.df = pd.DataFrame(data, columns=selected_columns)
            st.session_state.input_data = data
            st.session_state.mode = "result"

    # -------------------------
    # ✅ CSV
    # -------------------------
    else:
        file = st.file_uploader("CSVファイルを選択")
        if file:
            df = pd.read_csv(file)
            st.session_state.df = df
            st.session_state.mode = "result"

# =========================
# ✅ 解析画面
# =========================
else:

    df = st.session_state.df.copy()

    st.subheader("データ")
    st.write(df)

    # -------------------------
    # ✅ 安全処理
    # -------------------------
    if "Cr_pre" in df.columns and "Cr_post" in df.columns:
        df["Difference"] = df["Cr_post"] - df["Cr_pre"]

    # -------------------------
    # ✅ 基本統計
    # -------------------------
    st.subheader("基本統計量")
    st.write(df.describe())

    # -------------------------
    # ✅ t検定（安全版）
    # -------------------------
    if "Sex" in df.columns and "Kt_V" in df.columns:

        st.subheader("t検定")

        g1 = df[df["Sex"]=="M"]["Kt_V"]
        g2 = df[df["Sex"]=="F"]["Kt_V"]

        if len(g1)>1 and len(g2)>1:
            t,p = stats.ttest_ind(g1,g2)

            st.write(f"t値 = {t:.3f}")
            st.write(f"p値 = {p:.4f}")

    # -------------------------
    # ✅ 相関（安全）
    # -------------------------
    if "Cr_pre" in df.columns and "Kt_V" in df.columns:

        st.subheader("相関")

        r = df["Cr_pre"].corr(df["Kt_V"])
        st.write(f"相関係数 r = {r:.3f}")

    # -------------------------
    # ✅ 多変量回帰（安全）
    # -------------------------
    if all(col in df.columns for col in ["Cr_pre","Cr_post","Kt_V"]):

        st.subheader("多変量回帰")

        X = df[["Cr_pre","Cr_post"]]
        X = sm.add_constant(X)
        y = df["Kt_V"]

        model = sm.OLS(y,X).fit()
        st.text(model.summary())

    # -------------------------
    # ✅ グラフ選択（そのまま）
    # -------------------------
    st.subheader("グラフ")

    graphs = st.multiselect(
        "表示するグラフ",
        ["箱ひげ図","散布図","ヒストグラム"],
        default=["箱ひげ図"]
    )

    if "箱ひげ図" in graphs and "Sex" in df.columns:
        fig, ax = plt.subplots()
        sns.boxplot(x="Sex", y="Kt_V", data=df, ax=ax)
        ax.set_title("Boxplot")
        st.pyplot(fig)

    if "散布図" in graphs and "Cr_pre" in df.columns:
        fig, ax = plt.subplots()
        sns.scatterplot(x="Cr_pre", y="Kt_V", data=df, ax=ax)
        sns.regplot(x="Cr_pre", y="Kt_V", data=df, ax=ax, scatter=False)
        ax.set_title("Scatter Plot")
        st.pyplot(fig)

    # -------------------------
    # ✅ 保存
    # -------------------------
    csv = df.to_csv(index=False).encode()
    st.download_button("CSVダウンロード", csv, "data.csv")

    # -------------------------
    # ✅ 戻る
    # -------------------------
    if st.button("入力画面へ戻る"):
        st.session_state.mode = "input"
        st.rerun()