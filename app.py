import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

sns.set()

st.title("データ解析ツール")

# -------------------------
# ✅ session_state 初期化
# -------------------------
for key in ["df", "analysis_options", "graph_styles"]:
    if key not in st.session_state:
        st.session_state[key] = None

# -------------------------
# ✅ 入力画面
# -------------------------
if st.session_state.df is None:

    # 分析選択
    analysis_options = st.multiselect(
        "分析内容を選択",
        ["Kt/V", "前後差", "グループ比較", "相関"],
        default=["Kt/V"]
    )

    # ✅ グラフ複数選択
    graph_styles = st.multiselect(
        "グラフ形式（複数選択可）",
        ["折れ線", "棒グラフ", "ヒストグラム", "散布図", "箱ひげ図"],
        default=["折れ線"]
    )

    # 入力方法
    input_method = st.radio(
        "データ入力方法",
        ["CSVアップロード", "手入力"]
    )

    # CSV
    if input_method == "CSVアップロード":
        file = st.file_uploader("CSV選択", type="csv")
        if file:
            df = pd.read_csv(file, encoding="utf-8")
            st.session_state.df = df
            st.session_state.analysis_options = analysis_options
            st.session_state.graph_styles = graph_styles

    # 手入力
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
            st.session_state.graph_styles = graph_styles

# -------------------------
# ✅ 解析画面
# -------------------------
else:

    df = st.session_state.df
    analysis_options = st.session_state.analysis_options
    graph_styles = st.session_state.graph_styles

    st.subheader("データ")
    st.write(df)

    # -------------------------
    # ✅ 戻る処理（選択式）
    # -------------------------
    back_option = st.radio(
        "戻る時のデータ扱い",
        ["データ保持", "データをリセット"]
    )

    if st.button("データ入力に戻る"):
        if back_option == "データをリセット":
            st.session_state.df = None
        st.rerun()

    # 前処理
    if "Cr_pre" in df.columns:
        df["差"] = df["Cr_post"] - df["Cr_pre"]

    # -------------------------
    # ✅ グラフループ（二重ループ）
    # -------------------------
    for analysis in analysis_options:
        for style in graph_styles:

            fig, ax = plt.subplots()

            # ===== Kt/V =====
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

                mean_val = df["Kt_V"].mean()
                ax.axhline(mean_val, color="green", linestyle="--",
                           label=f"Mean={mean_val:.2f}")
                ax.legend()

                ax.set_title(f"Kt/V ({style})")

            # ===== 前後差 =====
            elif analysis == "前後差":

                if style == "折れ線":
                    ax.plot(df["ID"], df["差"], marker='o')

                elif style == "棒グラフ":
                    ax.bar(df["ID"], df["差"])

                elif style == "ヒストグラム":
                    ax.hist(df["差"])

                elif style == "散布図":
                    ax.scatter(df["ID"], df["差"])

                elif style == "箱ひげ図":
                    sns.boxplot(y=df["差"], ax=ax)

                ax.set_title(f"Pre-Post Difference ({style})")

            # ===== グループ比較 =====
            elif analysis == "グループ比較":

                result = df.groupby("Sex")["Kt_V"].mean()

                if style == "折れ線":
                    ax.plot(result.index, result.values, marker='o')

                elif style == "棒グラフ":
                    ax.bar(result.index, result.values)

                elif style == "箱ひげ図":
                    sns.boxplot(x="Sex", y="Kt_V", data=df, ax=ax)

                ax.set_title(f"Group Comparison ({style})")

            # ===== 相関 =====
            elif analysis == "相関":

                if style in ["散布図", "折れ線"]:
                    sns.regplot(x="Cr_pre", y="Kt_V", data=df, ax=ax)

                    corr = df["Cr_pre"].corr(df["Kt_V"])
                    ax.set_title(f"Correlation r={corr:.2f}")

                else:
                    ax.text(0.2, 0.5, "このグラフ形式は非対応")

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
                label=f"{analysis}_{style} 保存",
                data=buf,
                file_name=f"{analysis}_{style}.png",
                mime="image/png"
            )

    # -------------------------
    # ✅ CSV保存
    # -------------------------
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "CSVダウンロード",
        csv,
        "processed_data.csv",
        "text/csv"
    )