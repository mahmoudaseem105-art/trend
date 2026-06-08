import streamlit as st
import feedparser
import re
from collections import Counter

# 1. إعدادات الصفحة
st.set_page_config(page_title="Trend now - مصر", page_icon="🔥", layout="wide")
st.title("🔥 Trend now | نبض الترند المصري")
st.markdown("رادار لحظي للقضايا الأكثر جدلاً في الشارع المصري ومواقع التواصل.")
st.divider()

# 2. مصادر "النبض المصري" (ركزنا على القنوات والمواقع التي يتابعها الشارع المصري)
ALL_SOURCES = [
    {"name": "المصري اليوم", "url": "https://rss.app/feeds/0qilsswhtljm7TpX.xml"},
    {"name": "القاهرة 24", "url": "https://rss.app/feeds/fSxYHaCDdTtQnPcc.xml"},
    {"name": "اليوم السابع", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "صدى البلد", "url": "https://rss.app/feeds/QmEgZe5stNIFBrub.xml"},
    {"name": "العربية مصر", "url": "https://rss.app/feeds/hoc4wHdnB7ZkJIun.xml"},
    {"name": "حدث بالفعل", "url": "https://rss.app/feeds/sUfKUXNv3LLJjC8X.xml"},
    {"name": "تليجراف مصر", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "الشرق الأوسط", "url": "https://rss.app/feeds/WrrcuX75FOhb3MyZ.xml"}
]

# 3. كلمات التوقف (لإبعاد الكلمات غير المهمة)
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
@st.cache_data(ttl=600) # تحديث كل 10 دقائق لمواكبة سرعة السوشيال ميديا
def fetch_trending_data():
    all_news = []
    for source in ALL_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:10]: # سحب أخبار أكثر لزيادة الدقة
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": source['name'],
                    "image": extract_image_url(entry)
                })
        except: continue
    return all_news

# 6. صيد الترندات (التركيز على الأسماء والأحداث)
def extract_dominating_trends(news_list):
    words = []
    for item in news_list:
        clean_text = re.sub(r'[^\w\s]', '', item['title'])
        for word in clean_text.split():
            # كلمات أكثر من 3 حروف، غالباً هي أسماء أشخاص أو قضايا
            if len(word) > 3 and word not in STOP_WORDS: 
                words.append(word)
    freq = Counter(words)
    return [word for word, count in freq.most_common(8) if count > 1]

# --- الواجهة ---
news_data = fetch_trending_data()
dominating_trends = extract_dominating_trends(news_data)

if dominating_trends:
    st.sidebar.header("🚨 ترندات الساعة في مصر")
    selected_trend = st.sidebar.radio("اختر الحدث الساخن:", dominating_trends)
    
    st.subheader(f"🔍 متابعة قضية: 【 {selected_trend} 】")
    
    related_items = [item for item in news_data if selected_trend in item['title']]
    
    cols = st.columns(3)
    for index, item in enumerate(related_items[:6]):
        with cols[index % 3]:
            st.image(item['image'], use_container_width=True)
            st.markdown(f"**{item['source']}**")
            st.markdown(f"[{item['title']}]({item['link']})")
            st.write("---")
else:
    st.info("الرادار يمسح الأخبار الآن... انتظر لحظات.")
