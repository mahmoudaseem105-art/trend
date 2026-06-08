import streamlit as st
import feedparser
import re
from collections import Counter

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="معرض الترند البصري | Trend Hub", page_icon="🔥", layout="wide")

st.title("🔥 معرض الترندات البصري (Trend Link Hub)")
st.markdown("يصطاد المواضيع الأكثر اشتعالاً على الساحة ويعرضها لك بصرياً لتلهم محتواك.")
st.divider()

# 2. بنك المصادر (المختص بالسوشيال ميديا والأخبار السريعة)
ALL_SOURCES = [
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"},
    {"name": "عربي 21", "url": "https://rss.app/feeds/IELo97hFudhqzc3b.xml"},
    {"name": "منصة إيكاد", "url": "https://rss.app/feeds/dIksWt06BYI9wq9h.xml"},
    {"name": "شبكة رصد", "url": "https://rss.app/feeds/UY9b0tCrWqLlDUS2.xml"},
    {"name": "عربي بوست", "url": "https://rss.app/feeds/LzcCUDjvwsYkxeJb.xml"},
    {"name": "المصري اليوم (إكس)", "url": "https://rss.app/feeds/idlogJBSLTtWCMLm.xml"},
    {"name": "الشرق الأوسط (منشنز)", "url": "https://rss.app/feeds/GsU4dAB2KkXc8ctB.xml"}
]

# 3. كلمات التوقف (لإبعاد الكلمات العادية والتركيز على الترند الحقيقي)
STOP_WORDS = set([
    "على", "إلى", "هذا", "هذه", "التي", "الذي", "عبر", "خلال", "بسبب", "حول", "عاجل",
    "وقد", "أنه", "كما", "ذلك", "وهي", "وهو", "بين", "فقط", "فيديو", "صور", "شاهد",
    "منها", "وإن", "وأن", "اليوم", "أمس", "غدا", "تفاصيل", "أكثر", "كيف", "لماذا"
])

# 4. دالة استخراج الصور من الـ RSS
def extract_image_url(entry):
    # محاولة سحب الصورة من الميديا
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
        return entry.enclosures[0]['href']
    # محاولة سحب الصورة من الوصف (HTML)
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if match:
            return match.group(1)
    # صورة افتراضية في حال لم يوجد صورة
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=500&q=80"

# 5. دالة جلب البيانات مع الصور
@st.cache_data(ttl=1800)
def fetch_trending_data():
    all_news = []
    for source in ALL_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:8]: # نركز على أهم الأخبار فقط
                image_url = extract_image_url(entry)
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": source['name'],
                    "image": image_url
                })
        except:
            continue
    return all_news

# 6. خوارزمية صيد الترندات القوية فقط
def extract_dominating_trends(news_list, top_n=6):
    words = []
    for item in news_list:
        clean_text = re.sub(r'[^\w\s]', '', item['title'])
        for word in clean_text.split():
            if len(word) > 4 and word not in STOP_WORDS: # الكلمات الأطول غالباً هي أسماء وأحداث
                words.append(word)
                
    freq = Counter(words)
    # نرجع أهم الكلمات التي تكررت كثيراً فقط
    return [word for word, count in freq.most_common(top_n) if count > 1]

# --- واجهة المستخدم (الـ Visual Hub) ---
with st.spinner('⏳ جاري مسح شبكات السوشيال ميديا وتجهيز معرض الترندات...'):
    news_data = fetch_trending_data()

if news_data:
    dominating_trends = extract_dominating_trends(news_data)
    
    if dominating_trends:
        st.sidebar.header("🔥 الترندات المسيطرة الآن")
        selected_trend = st.sidebar.radio("اختر الترند لعرض الميديا الخاصة به:", dominating_trends)
        
        st.subheader(f"📸 معرض الترند: 【 {selected_trend} 】")
        
        # جلب الكروت (التي تحتوي على الكلمة) بحد أقصى 6 كروت لعدم الازدحام
        related_items = [item for item in news_data if selected_trend in item['title']][:6]
        
        # إنشاء شبكة عرض (Grid) بـ 3 أعمدة مثل انستجرام
        cols = st.columns(3)
        
        for index, item in enumerate(related_items):
            with cols[index % 3]:
                # عرض الكارت البصري
                st.image(item['image'], use_container_width=True)
                st.markdown(f"**{item['source']}**")
                st.markdown(f"[{item['title']}]({item['link']})")
                st.write("---")
    else:
        st.info("لم يتم رصد ترند قوي يسيطر على الساحة في هذه اللحظة، حاول بعد قليل.")
else:
    st.error("⚠️ لم نتمكن من جلب البيانات، يرجى تحديث الصفحة.")
