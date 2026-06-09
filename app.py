import streamlit as st
import feedparser
import re
from collections import Counter

# 1. إعدادات الصفحة والهوية الرسمية للمنصة
st.set_page_config(page_title="SherifOsmanClub الإخبارية", page_icon="🔥", layout="wide")

# اسم ملف اللوجو الذي سيتم قراءته من جيت هاب
LOGO_IMAGE = "channels4_profile.jpg" 

# --- عرض اللوجو الكبير في الشاشة الرئيسية ---
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    try:
        st.image(LOGO_IMAGE, caption="المنصة الرسمية - SherifOsmanClub", use_container_width=True)
    except:
        st.warning("جاري تحميل اللوجو... يرجى التأكد من رفع صورة channels4_profile.jpg إلى جيت هاب.")

st.title("🔥 SherifOsmanClub الإخبارية")
st.markdown("الرادار المستقل للأخبار العاجلة والترندات الأكثر تداولاً وجدلاً على الساحة.")
st.divider()

# 2. مصادر "النبض الإخباري والسوشيال ميديا"
ALL_SOURCES = [
    {"name": "المصري اليوم", "url": "https://rss.app/feeds/0qilsswhtljm7TpX.xml"},
    {"name": "القاهرة 24", "url": "https://rss.app/feeds/fSxYHaCDdTtQnPcc.xml"},
    {"name": "اليوم السابع", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "صدى البلد", "url": "https://rss.app/feeds/QmEgZe5stNIFBrub.xml"},
    {"name": "العربية مصر", "url": "https://rss.app/feeds/hoc4wHdnB7ZkJIun.xml"},
    {"name": "حدث بالفعل", "url": "https://rss.app/feeds/sUfKUXNv3LLJjC8X.xml"},
    {"name": "تليجراف مصر", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "الشرق الأوسط", "url": "https://rss.app/feeds/WrrcuX75FOhb3MyZ.xml"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"}
]

# 3. كلمات التوقف لفلترة العناوين
STOP_WORDS = set(["على", "إلى", "هذا", "هذه", "التي", "الذي", "بسبب", "عاجل", "اليوم", "أمس", "صور", "فيديو", "شاهد", "تفاصيل"])

# 4. دالة استخراج الصور
def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if match: return match.group(1)
    return "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=500"

# 5. جلب البيانات
@st.cache_data(ttl=600) # تحديث كل 10 دقائق
def fetch_trending_data():
    all_news = []
    for source in ALL_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:10]:
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": source['name'],
                    "image": extract_image_url(entry)
                })
        except: continue
    return all_news

# 6. صيد ترند الساعة
def extract_dominating_trends(news_list):
    words = []
    for item in news_list:
        clean_text = re.sub(r'[^\w\s]', '', item['title'])
        for word in clean_text.split():
            if len(word) > 3 and word not in STOP_WORDS: 
                words.append(word)
    freq = Counter(words)
    return [word for word, count in freq.most_common(8) if count > 1]

# --- تشغيل الواجهة والتفاعل ---
news_data = fetch_trending_data()
dominating_trends = extract_dominating_trends(news_data)

# إعدادات القائمة الجانبية (Sidebar) مع اللوجو
try:
    st.sidebar.image(LOGO_IMAGE, use_container_width=True)
except:
    pass # في حالة تأخر تحميل الصورة لا يظهر خطأ يزعج الزائر
    
st.sidebar.markdown("<h3 style='text-align: center;'>SherifOsmanClub</h3>", unsafe_allow_html=True)
st.sidebar.divider()

if dominating_trends:
    st.sidebar.header("🚨 ترند الساعة")
    selected_trend = st.sidebar.radio("اختر الحدث الساخن لمتابعته:", dominating_trends)
    
    st.subheader(f"🔍 تغطية حية لترند الساعة: 【 {selected_trend} 】")
    
    related_items = [item for item in news_data if selected_trend in item['title']]
    
    cols = st.columns(3)
    for index, item in enumerate(related_items[:6]):
        with cols[index % 3]:
            st.image(item['image'], use_container_width=True)
            st.markdown(f"**{item['source']}**")
            st.markdown(f"[{item['title']}]({item['link']})")
            st.write("---")
else:
    st.info("الرادار يمسح الأخبار والمنصات الآن... انتظر لحظات.")
