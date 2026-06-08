import streamlit as st
import feedparser
import requests
import urllib.parse
import json

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="رادار الترند العالمي | Trend Radar", page_icon="🌍", layout="wide")

st.title("🌍 غرفة الأخبار الآلية ورادار الترند")
st.markdown("راقب الكلمات المشتعلة من (Google Trends) مباشرة، مع تحليل ذكي لأكثر من 24 مصدراً محلياً وعالمياً.")
st.divider()

GROQ_API_KEY = "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"

# 2. بنك المصادر الشامل
ALL_SOURCES = [
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "The Economist", "url": "https://www.economist.com/the-world-this-week/rss.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera Arabic", "url": "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"},
    {"name": "التلفزيون العربي", "url": "https://rss.app/feeds/kT7C8wffs4FlVogb.xml"},
    {"name": "عربي 21", "url": "https://rss.app/feeds/IELo97hFudhqzc3b.xml"},
    {"name": "منصة إيكاد", "url": "https://rss.app/feeds/dIksWt06BYI9wq9h.xml"},
    {"name": "شبكة رصد", "url": "https://rss.app/feeds/UY9b0tCrWqLlDUS2.xml"},
    {"name": "الشرق الأوسط", "url": "https://rss.app/feeds/WrrcuX75FOhb3MyZ.xml"},
    {"name": "مدى مصر", "url": "https://rss.app/feeds/aZtPJd9x1TdXhpbc.xml"},
    {"name": "شبكة مزيد", "url": "https://rss.app/feeds/EKNJ1yBhz9dYQesm.xml"},
    {"name": "عربي بوست", "url": "https://rss.app/feeds/LzcCUDjvwsYkxeJb.xml"},
    {"name": "المصري اليوم", "url": "https://rss.app/feeds/0qilsswhtljm7TpX.xml"},
    {"name": "حقوق الإنسان", "url": "https://rss.app/feeds/KQOHigY4eHs2OXV0.xml"},
    {"name": "العشرين أونلاين", "url": "https://rss.app/feeds/UitAtgEww18TWQag.xml"},
    {"name": "العربية مصر", "url": "https://rss.app/feeds/hoc4wHdnB7ZkJIun.xml"},
    {"name": "صدى مصر", "url": "https://rss.app/feeds/QmEgZe5stNIFBrub.xml"},
    {"name": "تكنوقراط", "url": "https://rss.app/feeds/ITEpCccZdY1r0M4P.xml"},
    {"name": "المصري اليوم (إكس)", "url": "https://rss.app/feeds/idlogJBSLTtWCMLm.xml"},
    {"name": "تليجراف مصر", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "مزيد ستوريز", "url": "https://rss.app/feeds/n5ZkHXC4f0Zx7tzt.xml"},
    {"name": "القاهرة 24", "url": "https://rss.app/feeds/fSxYHaCDdTtQnPcc.xml"},
    {"name": "حدث بالفعل", "url": "https://rss.app/feeds/sUfKUXNv3LLJjC8X.xml"},
    {"name": "الشرق الأوسط (منشنز)", "url": "https://rss.app/feeds/GsU4dAB2KkXc8ctB.xml"}
]

# 3. القائمة الجانبية (Sidebar)
st.sidebar.header("🌍 اختر الدولة")
country_dict = {
    "مصر 🇪🇬": "EG",
    "السعودية 🇸🇦": "SA",
    "الولايات المتحدة 🇺🇸": "US",
    "المملكة المتحدة 🇬🇧": "GB",
    "الإمارات 🇦🇪": "AE"
}

selected_country_name = st.sidebar.radio("اضغط على الدولة لجلب الترند:", list(country_dict.keys()))
selected_country_code = country_dict[selected_country_name]

# 4. خوارزمية "الباب السري" لجلب البيانات من Google Trends API مباشرة
@st.cache_data(ttl=1800)
def get_daily_trends(geo_code):
    # الرابط السري المخفي الذي تستخدمه جوجل داخلياً (ليس RSS)
    target_url = f"https://trends.google.com/trends/api/dailytrends?hl=ar&tz=-120&geo={geo_code}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    
    trends_data = []
    
    def process_json(raw_text):
        # جوجل تضع 5 أحرف غريبة )]}', في بداية الملف لحمايته، نقوم بإزالتها لنتمكن من القراءة
        clean_text = raw_text[5:] if raw_text.startswith(")]}'") else raw_text
        try:
            data = json.loads(clean_text)
            days = data.get('default', {}).get('trendingSearchesDays', [])
            if days:
                for search in days[0].get('trendingSearches', []):
                    title = search.get('title', {}).get('query', '')
                    traffic = search.get('formattedTraffic', '+10K')
                    if title:
                        trends_data.append({"title": title, "traffic": traffic})
            return trends_data
        except:
            return []

    # المحاولة الأولى: الدخول المباشر
    try:
        res = requests.get(target_url, headers=headers, timeout=10)
        if res.status_code == 200:
            result = process_json(res.text)
            if result: return result
    except: pass

    # المحاولة الثانية: الدخول السري عبر وسيط AllOrigins
    try:
        proxy_url = f"https://api.allorigins.win/raw?url={urllib.parse.quote(target_url)}"
        res = requests.get(proxy_url, headers=headers, timeout=15)
        if res.status_code == 200:
            result = process_json(res.text)
            if result: return result
    except: pass

    return trends_data

# 5. دالة التحليل بواسطة Groq
def analyze_trend_with_groq(trend_word):
    context_headlines = []
    for source in ALL_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:2]:
                context_headlines.append(f"- {entry.title}")
        except:
            continue
            
    context_text = "\n".join(context_headlines)
    
    prompt = f"""
    أنت رئيس تحرير صحفي خبير ومحلل سياسي واقتصادي.
    الكلمة الأكثر بحثاً (الترند في جوجل) اليوم هي: "{trend_word}"
    
    تم مسح 24 مصدراً إخبارياً عالمياً ومحلياً، وهذه أحدث العناوين:
    {context_text}
    
    بناءً على العناوين، اكتب تقريراً صحفياً مختصراً باللغة العربية يشرح:
    1. لماذا هذه الكلمة ترند اليوم في جوجل؟
    2. ما هو السياق المحلي أو العالمي لهذا الحدث؟
    ضع التقرير في فقرتين احترافيتين بدون مقدمات.
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        data = res.json()
        return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "⚠️ تعذر الاتصال بمحرك الذكاء الاصطناعي حالياً."

# --- واجهة المستخدم ---
st.subheader(f"🔥 الكلمات المشتعلة من جوجل ترند: {selected_country_name.split(' ')[0]}")

with st.spinner('جاري اختراق واجهة جوجل الداخلية وجلب البيانات...'):
    trends_list = get_daily_trends(selected_country_code)

if trends_list:
    st.write("**مؤشرات التداول على الأخبار (أكثر الكلمات بحثاً):**")
    
    cols = st.columns(3)
    
    trend_titles_only = []
    for i, trend in enumerate(trends_list[:9]): 
        trend_titles_only.append(trend['title'])
        with cols[i % 3]:
            st.metric(label=f"#{i+1} {trend['title']}", value=f"{trend['traffic']}", delta="صاعد الآن")
            
    st.divider()
            
    st.write("**🤖 الغوص في عمق الترند بالذكاء الاصطناعي:**")
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        selected_trend = st.selectbox("اختر موضوعاً لتكليف المحرر الآلي بتحليله:", trend_titles_only)
        analyze_btn = st.button("حلل هذا الترند الآن", type="primary", use_container_width=True)
        
    with col_b:
        if analyze_btn:
            with st.spinner(f"جاري مسح 24 مصدراً إخبارياً لتحليل '{selected_trend}'... قد يستغرق بضع ثوانٍ"):
                analysis_report = analyze_trend_with_groq(selected_trend)
                st.success("تم الانتهاء من التحليل الشامل!")
                st.info(analysis_report)
else:
    st.error("⚠️ لم نتمكن من جلب الترندات. سيرفرات Streamlit المجانية محظورة بالكامل من جوجل حالياً.")
