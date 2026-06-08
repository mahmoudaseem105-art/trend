import streamlit as st
import feedparser
import requests

# 1. إعدادات الصفحة الأساسية (يجب أن تكون في السطر الأول دائماً)
st.set_page_config(page_title="رادار الترند العالمي | Trend Radar", page_icon="🌍", layout="wide")

st.title("🌍 غرفة الأخبار الآلية ورادار الترند")
st.markdown("راقب الكلمات المشتعلة وحجم البحث الفعلي، مع تحليل ذكي للأخبار.")
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

# 2. القائمة الجانبية (Sidebar) - أزرار مباشرة للتحميل الفوري
st.sidebar.header("🌍 اختر الدولة")
country_dict = {
    "مصر 🇪🇬": "EG",
    "السعودية 🇸🇦": "SA",
    "الولايات المتحدة 🇺🇸": "US",
    "المملكة المتحدة 🇬🇧": "GB",
    "الإمارات 🇦🇪": "AE"
}

# استخدام radio لعمل قائمة مرتبة تضغط عليها فتحمل فوراً
selected_country_name = st.sidebar.radio("اضغط على الدولة لجلب الترند:", list(country_dict.keys()))
selected_country_code = country_dict[selected_country_name]

# 3. دالة جلب الترندات المتطورة (تخترق الحظر وتجلب أرقام البحث)
@st.cache_data(ttl=1800)
def get_daily_trends(geo_code):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo_code}"
    # هذا السطر هو السلاح السري لإقناع جوجل بأننا متصفح عادي
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            trends_data = []
            for entry in feed.entries:
                title = entry.title
                # جلب عدد عمليات البحث إذا كان متوفراً في جوجل
                traffic = entry.get('ht_approx_traffic', '10,000+') 
                trends_data.append({"title": title, "traffic": traffic})
            return trends_data
        else:
            return []
    except Exception as e:
        return []

# 4. دالة التحليل بواسطة Groq الصاروخي
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

# --- واجهة المستخدم (عرض بأسلوب البورصة) ---
st.subheader(f"🔥 مؤشرات البحث المشتعلة في {selected_country_name.split(' ')[0]}")

with st.spinner('جاري اختراق حماية جوجل وجلب الترندات والأرقام...'):
    trends_list = get_daily_trends(selected_country_code)

if trends_list:
    st.write("**مؤشرات التداول على الأخبار (حسب عمليات البحث):**")
    
    # تقسيم الشاشة إلى 3 أعمدة لعرض الترندات مثل شاشات البورصة
    cols = st.columns(3)
    
    trend_titles_only = []
    for i, trend in enumerate(trends_list[:9]): # نعرض أهم 9 ترندات في مربعات
        trend_titles_only.append(trend['title'])
        with cols[i % 3]:
            # st.metric هو العنصر الذي يصنع شكل سهم البورصة
            st.metric(label=f"#{i+1} {trend['title']}", value=f"{trend['traffic']} بحث", delta="🔥 صاعد بقوة")
            
    st.divider()
            
    # قسم التحليل
    st.write("**🤖 الغوص في عمق الترند بالذكاء الاصطناعي:**")
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        selected_trend = st.selectbox("اختر موضوعاً لتكليف المحرر الآلي بتحليله:", trend_titles_only)
        analyze_btn = st.button("حلل هذا الترند الآن", type="primary", use_container_width=True)
        
    with col_b:
        if analyze_btn:
            with st.spinner(f"جاري جمع الأخبار وتحليل '{selected_trend}'..."):
                analysis_report = analyze_trend_with_groq(selected_trend)
                st.success("تم الانتهاء من التحليل!")
                st.info(analysis_report)
else:
    st.error("⚠️ لم نتمكن من جلب الترندات حالياً، هناك ضغط استثنائي من سيرفرات جوجل.")
