import streamlit as st
import feedparser
import requests
import re
import urllib.parse
from collections import Counter
from PIL import Image

# --- 1. إعدادات الصفحة والهوية ---
st.set_page_config(page_title="SherifOsmanClub الإخبارية", page_icon="🔥", layout="wide")

GROQ_API_KEY = "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"
LOGO_IMAGE_PATH = "channels4_profile.jpg" 

def get_resized_logo(width_size=120):
    try:
        img = Image.open(LOGO_IMAGE_PATH)
        w_percent = (width_size / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        return img.resize((width_size, h_size), Image.Resampling.LANCZOS)
    except:
        return None

col_text, col_logo = st.columns([8, 1]) 
with col_logo:
    logo_img = get_resized_logo(width_size=100)
    if logo_img: st.image(logo_img)
with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("**بوابة الأخبار العاجلة والترندات الذكية. (اضغط على المصدر أو الترند للانتقال المباشر)**")
st.divider()

# --- 2. قائمتك الـ 24 الأصلية (روابط مباشرة للمواقع وقنوات التليجرام) ---
ALL_SOURCES = [
    {"name": "المصري اليوم", "url": "https://www.almasryalyoum.com/"},
    {"name": "القاهرة 24", "url": "https://www.cairo24.com/"},
    {"name": "اليوم السابع", "url": "https://www.youm7.com/"},
    {"name": "صدى البلد", "url": "https://www.elbalad.news/"},
    {"name": "العربية مصر", "url": "https://www.alarabiya.net/egypt"},
    {"name": "حدث بالفعل", "url": "https://hadathbelfael.com/"},
    {"name": "تليجراف مصر", "url": "https://telegraphmisr.com/"},
    {"name": "صحيفة الشرق الأوسط", "url": "https://aawsat.com/"},
    {"name": "عربي 21", "url": "https://arabi21.com/"},
    {"name": "إيكاد Eekad", "url": "https://eekad.net/"},
    {"name": "شبكة رصد", "url": "https://rassd.com/"},
    {"name": "مدى مصر", "url": "https://www.madamasr.com/"},
    {"name": "شبكة مزيد", "url": "https://t.me/s/Mazeeed"},
    {"name": "عربي بوست", "url": "https://arabicpost.net/"},
    {"name": "العربي الجديد", "url": "https://www.alaraby.co.uk/"},
    {"name": "حقوق الإنسان", "url": "https://www.amnesty.org/ar/"},
    {"name": "تكنوقراط", "url": "https://t.me/s/EgyTechnocrats"},
    {"name": "المصري اليوم إكس", "url": "https://twitter.com/AlMasryAlYoum"},
    {"name": "مزيد ستوريز", "url": "https://t.me/s/Mazeeed"},
    {"name": "الشرق الأوسط منشنز", "url": "https://twitter.com/aawsat_news"},
    {"name": "عربي نيوز", "url": "https://arabi21.com/"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world"},
    {"name": "The Economist", "url": "https://www.economist.com/"},
    {"name": "BBC News", "url": "https://www.bbc.com/arabic"}
]

# --- 3. تغذية الذكاء الاصطناعي (سحب خلفي آمن لا يُحظر أبداً) ---
@st.cache_data(ttl=600)
def fetch_global_headlines():
    # نستخدم روابط عالمية مفتوحة المصدر فقط لجمع العناوين لـ Groq لكي لا نتوقف أبداً
    rss_urls = [
        "https://news.google.com/rss?hl=ar&gl=EG&ceid=EG:ar",
        "https://news.google.com/rss/headlines/section/topic/WORLD?hl=ar&gl=EG&ceid=EG:ar"
    ]
    titles = []
    for u in rss_urls:
        try:
            feed = feedparser.parse(u)
            for entry in feed.entries[:30]:
                titles.append(entry.title)
        except: pass
    return titles

@st.cache_data(ttl=900) 
def get_trends_from_groq(titles):
    try:
        sample_titles = list(set(titles))[:60]
        prompt = f"""
        اقرأ هذه العناوين الإخبارية الحالية:
        {" | ".join(sample_titles)}
        
        استخرج أهم 6 مواضيع أو أسماء شخصيات (ترند) مشتعلة الآن.
        شروط:
        1. الترند كلمة واحدة فقط أو اسم علم مفرد (مثل: غزة، الدولار، بايدن).
        2. يمنع صياغة جمل.
        3. النتيجة مفصولة بفاصلة عربية (،) فقط.
        """
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}, 
                            headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=10)
        if res.status_code == 200:
            content = res.json()['choices'][0]['message']['content'].strip()
            trends = [t.strip() for t in re.split(r'[,،\-]', content) if len(t.strip()) > 2 and len(t.split()) <= 2]
            return trends[:6] if trends else None
    except: pass
    return None

def get_trends_fallback(titles):
    STOP_WORDS = set(["على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "بسبب", "حول", "وقد", "أنه", "كما", "ذلك", "فقط", "اليوم"])
    words = []
    for title in titles:
        for word in re.findall(r'[\u0600-\u06FF]+', title):
            if len(word) > 3 and word not in STOP_WORDS: words.append(word)
    return [word for word, count in Counter(words).most_common(6) if count > 1]

# --- 4. تشغيل النظام وبناء الواجهة ---
with st.spinner('⏳ جاري تحليل النبض العالمي واستخراج الترندات...'):
    global_titles = fetch_global_headlines()
    dominating_trends = get_trends_from_groq(global_titles) or get_trends_fallback(global_titles)

# قسم الترندات في أعلى الصفحة (مساحة واسعة)
if dominating_trends:
    st.subheader("🚨 الكلمات المشتعلة (ترند الساعة)")
    st.markdown("اضغط على الترند ليقوم بتحويلك لتغطية شاملة عنه في تبويب جديد:")
    
    # توزيع الأزرار في أعمدة متساوية
    cols = st.columns(len(dominating_trends))
    for i, trend in enumerate(dominating_trends):
        clean_trend = trend.replace(".", "").strip()
        # عند الضغط على الترند، يفتح بحث جوجل الإخباري لهذا الترند مباشرة
        trend_url = f"https://news.google.com/search?q={urllib.parse.quote(clean_trend)}&hl=ar&gl=EG&ceid=EG:ar"
        with cols[i]:
            st.link_button(f"🔥 {clean_trend}", url=trend_url, use_container_width=True)

st.divider()

# قسم المصادر الرسمية (كشبكة بورتال Portal Grid)
st.subheader("🟢 غرف المصادر المباشرة (الـ 24 مصدراً)")
st.markdown("بوابتك المباشرة للأخبار. اضغط على أي مصدر ليفتح لك موقعه الرسمي أو قناته فوراً:")

# عرض الـ 24 مصدراً في شبكة من 4 أعمدة ليكون التصفح مريحاً للعين
col_count = 4
source_cols = st.columns(col_count)

for index, source in enumerate(ALL_SOURCES):
    col_idx = index % col_count
    with source_cols[col_idx]:
        # زر يعمل كـ هايبر لينك (Hyperlink) يفتح في New Tab مباشرة
        st.link_button(f"📡 {source['name']}", url=source['url'], use_container_width=True)

st.markdown("<br><br><center>تم بناء هذه البوابة لتعمل بأقصى سرعة واستقرار 🚀</center>", unsafe_allow_html=True)

# وضعنا اللوجو في القائمة الجانبية كشكل جمالي فقط
if sidebar_logo := get_resized_logo(width_size=100):
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.columns([1, 2, 1])[1].image(sidebar_logo)
    st.sidebar.markdown("<h3 style='text-align: center; margin-top: -5px;'>SherifOsmanClub</h3>", unsafe_allow_html=True)
    st.sidebar.info("💡 **نصيحة:** جميع الأزرار في هذه المنصة تفتح المصادر الأصلية في نافذة جديدة (New Tab) لضمان عدم توقف الأخبار وحمايتك من حظر السيرفرات.")
