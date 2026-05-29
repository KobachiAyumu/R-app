import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from scipy import stats
import statsmodels.api as sm

sns.set()

st.title("データ解析ツール（統計完全版）")

# -------------------------
# ✅ state初期化
# -------------------------
for key in ["df", "analysis_options", "graph_styles", "input_data", "mode"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.mode is None:
    st.session_state.mode = "input"

# =========================
# ✅ 入力画面
# =========================
if st.session_state.mode == "input":

    input_method = st.radio(
        "データ入力方法",
        ["CSVアップロード", "手入力"],
        index=1
    )

    analysis_options = st.multiselect(
        "分析内容",
        ["Kt/V", "前後差", "グループ比較", "相関", "t検定", "回帰分析"],
        default=["Kt/V"]
    )

    graph_styles = st.multiselect(
        "グラフ形式",
        ["折れ線", "棒グラフ", "ヒストグラム", "散布図", "箱ひげ図"],
        default=["折れ線"]
    )

    # CSV
    if input_method == "CSVアップロード":
        file = st.file_uploader("CSV選択", type="csv")

        if file:
            df = pd.read_csv(file)
            st.session_state.df = df
            st.session_state.analysis_options = analysis_options
            st.session_state.graph_styles = graph_styles
            st.session_state.mode = "result"

    # 手入力
    else:
        n = st.number_input("データ数", 1, 50, 2)

        data = []
        for i in range(n):
            st.write(f"データ{i+1}")

            saved = None
            if st.session_state.input_data and i < len(st.session_state.input_data):
                saved = st.session_state.input_data[i]

            id_val = st.number_input(f"ID{i+1}", value=saved[0] if saved else i+1, key=f"id{i+1}")
            sex = st.selectbox(f"Sex{i+1}", ["M","F"],
                               index=["M","F"].index(saved[1]) if saved else 0,
                               key=f"sex{i+1}")
            ktv = st.number_input(f"Kt_V{i+1}", value=saved[2] if saved else 1.0, key=f"ktv{i+1}")
            pre = st.number_input(f"Cr_pre{i+1}", value=saved[3] if saved else 0.0, key=f"pre{i+1}")
            post = st.number_input(f"Cr_post{i+1}", value=saved[4] if saved else 0.0, key=f"post{i+1}")

            data.append([id_val, sex, ktv, pre, post])

        if st.button("データ確定"):
            st.session_state.df = pd.DataFrame(
                data, columns=["ID","Sex","Kt_V","Cr_pre","Cr_post"]
            )
            st.session_state.analysis_options = analysis_options
            st.session_state.graph_styles = graph_styles
            st.session_state.input_data = data
            st.session_state.mode = "result"

# =========================
# ✅ 解析画面
# =========================
else:

    df = st.session_state.df.copy()
    analysis_options = st.session_state.analysis_options
    graph_styles = st.session_state.graph_styles

    st.subheader("データ")
    st.write(df)

    # 基本統計
    st.subheader("基本統計")
    st.write(df.describe())

    # 戻る
    back_option = st.radio("戻るとき", ["データ保持", "データをリセット"])
    if st.button("データ入力に戻る"):
        if back_option == "データをリセット":
            st.session_state.df = None
            st.session_state.input_data = None
        st.session_state.mode = "input"
        st.rerun()

    # 前処理
    if "Cr_pre" in df.columns and "Cr_post" in df.columns:
        df["差"] = df["Cr_post"] - df["Cr_pre"]

    # =========================
    # ✅ t検定
    # =========================
    if "t検定" in analysis_options and "Sex" in df.columns:

        st.subheader("t検定（Sex別 Kt/V）")

        group1 = df[df["Sex"]=="M"]["Kt_V"]
        group2 = df[df["Sex"]=="F"]["Kt_V"]

        if len(group1) > 1 and len(group2) > 1:
            t_stat, p_val = stats.ttest_ind(group1, group2)

            st.write(f"t値: {t_stat:.3f}")
            st.write(f"p値: {p_val:.4f}")

            if p_val < 0.05:
                st.success("✅ 有意差あり（p < 0.05）")
            else:
                st.info("有意差なし")

    # =========================
    # ✅ 回帰分析
    # =========================
    if "回帰分析" in analysis_options:

        st.subheader("回帰分析（Cr_pre → Kt/V）")

        if "Cr_pre" in df.columns:

            X = df["Cr_pre"]
            Y = df["Kt_V"]

            X = sm.add_constant(X)
            model = sm.OLS(Y, X).fit()

            st.text(model.summary())

    # =========================
    # ✅ 相関
    # =========================
    if "相関" in analysis_options:

        corr = df["Cr_pre"].corr(df["Kt_V"])
        st.write(f"相関係数 r = {corr:.3f}")

    # =========================
    # ✅ グラフ
    # =========================
    for analysis in analysis_options:
        for style in graph_styles:

            fig, ax = plt.subplots()

            if analysis == "Kt/V":

                if style == "折れ線":
                    ax.plot(df["ID"], df["Kt_V"], marker='o')
                elif style == "棒グラフ":
                    ax.bar(df["ID"], df["Kt_V"])
                elif style == "ヒストグラム":
                    ax.hist(df["Kt_V"])
                elif style == "散布図":
                    ax.scatter(df["ID"], df["Kt_V"])
                elif style == "箱ひげ図":
                    sns.boxplot(y=df["Kt_V"], ax=ax)

                ax.axhline(1.2, color="red", linestyle="--")

                ax.set_title(f"Kt/V ({style})")

            elif analysis == "相関":

                if style in ["散布図","折れ線"]:
                    sns.regplot(x="Cr_pre", y="Kt_V", data=df, ax=ax)

                    corr = df["Cr_pre"].corr(df["Kt_V"])
                    ax.set_title(f"相関 r={corr:.2f}")

            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300)
            buf.seek(0)

            st.download_button(
                f"{analysis}_{style} 保存",
                buf,
                f"{analysis}_{style}.png",
                "image/png"
            )

    # CSV
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button("CSVダウンロード", csv, "data.csv", "text/csv")