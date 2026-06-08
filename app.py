import streamlit as st
import feedparser
import requests

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="رادار الترند العالمي | Trend Radar", page_icon="🌍", layout="wide")

st.title("🌍 غرفة الأخبار الآلية ورادار الترند")
st.markdown("راقب الكلمات المشتعلة، ودع الذكاء الاصطناعي يحللها لك من أقوى المصادر المحلية والعالمية.")
st.divider()

GROQ_API_KEY = "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"

ALL_SOURCES = [
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "The Economist", "url": "https://www.economist.com/the-world-this-week/rss.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera Arabic", "url": "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"},
    {"name": "التلفزيون العربي", "url": "https://rss.app/feeds/kT7C8wffs4FlVogb.xml"},
    {"name": "عربي 21", "url": "https://rss.app/feeds/IELo97hFudhqzc3b.xml"},
    {"name": "الشرق الأوسط", "url": "https://rss.app/feeds/WrrcuX75FOhb3MyZ.xml"},
    {"name": "المصري اليوم", "url": "https://rss.app/feeds/0qilsswhtljm7TpX.xml"}
]

# 2. القائمة الجانبية (Sidebar)
st.sidebar.header("⚙️ إعدادات الرادار")
# استخدمنا الرموز الرسمية لجوجل ترندز (EG, SA, US, GB)
country_dict = {
    "مصر 🇪🇬": "EG",
    "السعودية 🇸🇦": "SA",
    "الولايات المتحدة 🇺🇸": "US",
    "المملكة المتحدة 🇬🇧": "GB"
}
selected_country_name = st.sidebar.selectbox("حدد الدولة التي تريد مراقبتها:", list(country_dict.keys()))
selected_country_code = country_dict[selected_country_name]

# 3. دالة جلب الترندات الرسمية والمستقرة 100% (Google Trends RSS)
@st.cache_data(ttl=1800)
def get_daily_trends(geo_code):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo_code}"
    try:
        feed = feedparser.parse(url)
        trends = [entry.title for entry in feed.entries]
        return trends
    except Exception as e:
        return []

# 4. دالة التحليل بواسطة Groq
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
    الكلمة الأكثر بحثاً (الترند) اليوم هي: "{trend_word}"
    
    هذه أحدث العناوين من كبرى الصحف:
    {context_text}
    
    بناءً على العناوين، اكتب تقريراً صحفياً مختصراً باللغة العربية يشرح:
    1. لماذا هذه الكلمة ترند اليوم؟
    2. ما هو السياق المحلي أو العالمي لهذا الحدث؟
    ضع التقرير في فقرتين احترافيتين بدون مقدمات طويلة.
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
st.subheader(f"🔥 الكلمات المشتعلة في {selected_country_name.split(' ')[0]}")

with st.spinner('جاري مسح شبكة الإنترنت...'):
    trends_list = get_daily_trends(selected_country_code)

if trends_list:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**قائمة الترند اليوم:**")
        for i, trend in enumerate(trends_list[:10], 1):
            st.write(f"{i}. **{trend}**")
            
    with col2:
        st.write("**🤖 تحليل الترند بالذكاء الاصطناعي:**")
        selected_trend = st.selectbox("اختر موضوعاً لمعرفة سبب صعوده:", trends_list[:10])
        
        if st.button("حلل هذا الترند الآن", type="primary"):
            with st.spinner(f"جاري جمع الأخبار وتحليل '{selected_trend}'..."):
                analysis_report = analyze_trend_with_groq(selected_trend)
                st.success("تم الانتهاء من التحليل!")
                st.info(analysis_report)
else:
    st.error("⚠️ لم نتمكن من جلب الترندات حالياً، يرجى المحاولة بعد قليل.")
