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

st.title("Ultimate Data Analysis Tool")

# ------------------
# ✅ state
# ------------------
for key in ["df","input_data","mode"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.mode is None:
    st.session_state.mode = "input"

# =========================
# ✅ 入力
# =========================
if st.session_state.mode == "input":

    method = st.radio("Input Method", ["Manual","CSV"], index=0)

    if method == "Manual":

        n = st.number_input("N",1,50,5)
        data = []

        for i in range(n):
            saved = None
            if st.session_state.input_data and i < len(st.session_state.input_data):
                saved = st.session_state.input_data[i]

            idv = st.number_input(f"ID{i}", value=saved[0] if saved else i+1)
            sex = st.selectbox(f"Sex{i}", ["M","F"],
                                index=["M","F"].index(saved[1]) if saved else 0)
            ktv = st.number_input(f"KtV{i}", value=saved[2] if saved else 1.0)
            pre = st.number_input(f"Pre{i}", value=saved[3] if saved else 0.0)
            post = st.number_input(f"Post{i}", value=saved[4] if saved else 0.0)

            data.append([idv,sex,ktv,pre,post])

        if st.button("Run"):
            st.session_state.df = pd.DataFrame(
                data, columns=["ID","Sex","Kt_V","Cr_pre","Cr_post"]
            )
            st.session_state.input_data = data
            st.session_state.mode = "result"

    else:
        file = st.file_uploader("CSV")
        if file:
            st.session_state.df = pd.read_csv(file)
            st.session_state.mode = "result"

# =========================
# ✅ 解析
# =========================
else:

    df = st.session_state.df.copy()

    st.subheader("Data")
    st.write(df)

    # 差分
    df["Difference"] = df["Cr_post"] - df["Cr_pre"]

    # ------------------
    # ✅ フィルタ
    # ------------------
    if "Sex" in df.columns:
        sex_filter = st.multiselect("Sex", df["Sex"].unique(), default=df["Sex"].unique())
        df = df[df["Sex"].isin(sex_filter)]

    # ------------------
    # ✅ 記述統計
    # ------------------
    st.subheader("Statistics")
    st.write(df.describe())

    # ------------------
    # ✅ 正規性検定
    # ------------------
    st.subheader("Normality (Shapiro)")
    if len(df["Kt_V"]) > 2:
        stat, p = stats.shapiro(df["Kt_V"])
        st.write(f"p={p:.4f}")

    # ------------------
    # ✅ t検定
    # ------------------
    st.subheader("t-test")

    g1 = df[df["Sex"]=="M"]["Kt_V"]
    g2 = df[df["Sex"]=="F"]["Kt_V"]

    if len(g1)>1 and len(g2)>1:
        t,p = stats.ttest_ind(g1,g2)

        mean1,mean2 = g1.mean(),g2.mean()
        sd1,sd2 = g1.std(),g2.std()

        pooled = np.sqrt((sd1**2+sd2**2)/2)
        d = (mean1-mean2)/pooled

        st.write(f"t={t:.3f}, p={p:.4f}, d={d:.2f}")

    # ------------------
    # ✅ Mann-Whitney
    # ------------------
    st.subheader("Mann-Whitney")

    if len(g1)>1 and len(g2)>1:
        u,p = stats.mannwhitneyu(g1,g2)
        st.write(f"U={u:.3f}, p={p:.4f}")

    # ------------------
    # ✅ ANOVA
    # ------------------
    st.subheader("ANOVA")
    try:
        model = smf.ols("Kt_V ~ Sex", data=df).fit()
        anova = sm.stats.anova_lm(model)
        st.write(anova)
    except:
        st.write("ANOVA not available")

    # ------------------
    # ✅ 相関
    # ------------------
    st.subheader("Correlation")
    corr = df.corr(numeric_only=True)
    st.write(corr)

    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, ax=ax)
    st.pyplot(fig)

    # ------------------
    # ✅ 回帰
    # ------------------
    st.subheader("Regression")

    X = df[["Cr_pre","Cr_post"]]
    X = sm.add_constant(X)
    y = df["Kt_V"]

    model = sm.OLS(y,X).fit()
    st.text(model.summary())

    # ------------------
    # ✅ VIF
    # ------------------
    st.subheader("VIF")

    vif_data = pd.DataFrame()
    vif_data["feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values,i) for i in range(X.shape[1])]
    st.write(vif_data)

    # ------------------
    # ✅ グラフ
    # ------------------
    st.subheader("Plots")

    fig, ax = plt.subplots()
    sns.boxplot(x="Sex", y="Kt_V", data=df, ax=ax)
    st.pyplot(fig)

    fig, ax = plt.subplots()
    sns.scatterplot(x="Cr_pre", y="Kt_V", data=df, ax=ax)
    sns.regplot(x="Cr_pre", y="Kt_V", data=df, ax=ax, scatter=False)
    st.pyplot(fig)

    # ------------------
    # ✅ 保存
    # ------------------
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    st.download_button("Download PNG", buf, "plot.png")

    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "data.csv")

    # ------------------
    # ✅ 戻る
    # ------------------
    if st.button("Back"):
        st.session_state.mode = "input"
        st.rerun()