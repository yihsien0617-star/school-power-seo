# 檔案名稱：2_dashboard.py (免 Key 免費版)
import streamlit as st
import pandas as pd
import plotly.express as px
from duckduckgo_search import DDGS
import time
import random

st.set_page_config(page_title="學校招生 SEO 戰情室", layout="wide")

try:
    df = pd.read_csv('school_data.csv')
except FileNotFoundError:
    st.error("找不到資料！請確認你有先執行 'python 1_generate_data.py'")
    st.stop()

st.sidebar.title("🏫 招生策略控制台")
dept_list = ["全校總覽"] + list(df['Department'].unique())
selected_dept = st.sidebar.selectbox("選擇分析視角", dept_list)

# --- 函數：DuckDuckGo 搜尋 (使用 html 模式最穩定) ---
def get_search_results(keyword):
    try:
        # backend='html' 是避開被擋的關鍵
        results = DDGS().text(keyword, max_results=3, backend="html")
        if results:
            return list(results), "DuckDuckGo (真實數據)"
    except Exception as e:
        print(f"搜尋錯誤: {e}")
        pass
        
    # 失敗時的備案
    templates = [
        {"title": f"【Dcard】{keyword} 評價好嗎？", "href": "https://www.dcard.tw/", "body": "學長姐真實評價..."},
        {"title": f"PTT - {keyword} 出路討論", "href": "https://www.ptt.cc/", "body": "薪水行情與工作機會..."},
        {"title": f"104 人力銀行 - {keyword} 職缺", "href": "https://www.104.com.tw/", "body": "最新工作機會列表..."},
    ]
    return random.sample(templates, 3), "模擬數據 (網路忙碌)"

# --- 主畫面 ---
if selected_dept == "全校總覽":
    st.title("📊 全校科系網路聲量總覽")
    dept_traffic = df.groupby('Department')['Search_Volume'].sum().reset_index().sort_values('Search_Volume', ascending=False)
    fig_bar = px.bar(dept_traffic, x='Department', y='Search_Volume', color='Department')
    st.plotly_chart(fig_bar, width="stretch")
else:
    st.title(f"🔍 {selected_dept}：招生關鍵字分析")
    dept_df = df[df['Department'] == selected_dept]
    best_keyword = dept_df.sort_values('Opportunity_Score', ascending=False).iloc[0]
    col1, col2 = st.columns(2)
    col1.metric("🔥 必寫文章主題", best_keyword['Keyword'])
    col2.metric("平均月搜尋量", f"{int(dept_df['Search_Volume'].mean()):,}")
    st.divider()

    st.subheader("🕵️ 競爭對手分析")
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        target_kw = st.selectbox("選擇關鍵字：", dept_df['Keyword'].unique())
    with col_s2:
        st.write("") 
        st.write("") 
        btn = st.button("開始分析", type="primary")

    if btn:
        with st.spinner(f"正在分析「{target_kw}」..."):
            results, status = get_search_results(target_kw)
            if "模擬" in status:
                st.warning(f"⚠️ {status}")
            else:
                st.success(f"✅ 分析完成！來源：{status}")

            for i, res in enumerate(results):
                title = res.get('title', '無標題')
                url = res.get('href', '#')
                with st.expander(f"第 {i+1} 名：{title}", expanded=True):
                    st.markdown(f"**連結：** [{url}]({url})")

    st.divider()
    st.dataframe(dept_df[['Keyword', 'Search_Volume', 'Opportunity_Score']].sort_values('Opportunity_Score', ascending=False), width="stretch")
