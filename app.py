import streamlit as st
import feedparser
import re
import requests
import urllib.parse
from collections import Counter
from PIL import Image

# 1. إعدادات الصفحة
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

# --- التنسيق العلوي ---
col_text, col_logo = st.columns([6, 1]) 
with col_logo:
    logo_img = get_resized_logo(width_size=100)
    if logo_img: st.image(logo_img)
with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("الرادار المستقل للأخبار العاجلة وترندات الساعة.")
st.divider()

# 2. بنك المصادر
ALL_SOURCES = [
    {"name": "المصري اليوم Page", "url": "https://rss.app/feeds/0qilsswhtljm7TpX.xml"},
    {"name": "القاهرة 24 Page", "url": "https://rss.app/feeds/fSxYHaCDdTtQnPcc.xml"},
    {"name": "اليوم السابع Page", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "صدى البلد Page", "url": "https://rss.app/feeds/QmEgZe5stNIFBrub.xml"},
    {"name": "العربية مصر Page", "url": "https://rss.app/feeds/hoc4wHdnB7ZkJIun.xml"},
    {"name": "حدث بالفعل Page", "url": "https://rss.app/feeds/sUfKUXNv3LLJjC8X.xml"},
    {"name": "تليجراف مصر Page", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "صحيفة الشرق الأوسط Page", "url": "https://rss.app/feeds/WrrcuX75FOhb3MyZ.xml"},
    {"name": "Arabi21 - عربي21 Page", "url": "https://rss.app/feeds/IELo97hFudhqzc3b.xml"},
    {"name": "Eekad - إيكاد Page", "url": "https://rss.app/feeds/dIksWt06BYI9wq9h.xml"},
    {"name": "شبكة رصد Page", "url": "https://rss.app/feeds/UY9b0tCrWqLlDUS2.xml"},
    {"name": "Mada Page", "url": "https://rss.app/feeds/aZtPJd9x1TdXhpbc.xml"},
    {"name": "مزيد Page", "url": "https://rss.app/feeds/EKNJ1yBhz9dYQesm.xml"},
    {"name": "عربي بوست Page", "url": "https://rss.app/feeds/LzcCUDjvwsYkxeJb.xml"},
    {"name": "العربي الجديد Page", "url": "https://rss.app/feeds/UitAtgEww18TWQag.xml"},
    {"name": "حقوق الإنسان Page", "url": "https://rss.app/feeds/KQOHigY4eHs2OXV0.xml"},
    {"name": "تكنوقراط Page", "url": "https://rss.app/feeds/ITEpCccZdY1r0M4P.xml"},
    {"name": "المصري اليوم إكس Page", "url": "https://rss.app/feeds/idlogJBSLTtWCMLm.xml"},
    {"name": "مزيد ستوريز Page", "url": "https://rss.app/feeds/n5ZkHXC4f0Zx7tzt.xml"},
    {"name": "الشرق الأوسط منشنز Page", "url": "https://rss.app/feeds/GsU4dAB2KkXc8ctB.xml"},
    {"name": "عربي نيوز Page", "url": "https://rss.app/feeds/IELo97hFudhqzc3b.xml"},
    {"name": "The Guardian Page", "url": "https://www.theguardian.com/world/rss"},
    {"name": "The Economist Page", "url": "https://www.economist.com/the-world-this-week/rss.xml"},
    {"name": "BBC News Page", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"}
]

def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0: return entry.media_content[0]['url']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0: return entry.enclosures[0]['href']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if match: return match.group(1)
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=500&q=80"

# --- شبكة البروكسي الثقيلة لاختراق حظر rss.app ---
def fetch_feed_robust(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    encoded_url = urllib.parse.quote(url, safe='')
    
    # 1. الاتصال المباشر
    try:
        f = feedparser.parse(url, agent=headers['User-Agent'])
        if f.entries: return f
    except: pass
    # 2. نفق Codetabs
    try:
        f = feedparser.parse(f"https://api.codetabs.com/v1/proxy?quest={url}")
        if f.entries: return f
    except: pass
    # 3. نفق Corsproxy
    try:
        f = feedparser.parse(f"https://corsproxy.io/?{encoded_url}")
        if f.entries: return f
    except: pass
    
    return None

@st.cache_data(ttl=600)
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    for source in ALL_SOURCES:
        feed = fetch_feed_robust(source['url'])
        if feed and feed.entries:
            for entry in feed.entries[:30]:
                item = {
                    "title": entry.title, "link": entry.link,
                    "source": source['name'], "image": extract_image_url(entry)
                }
                all_news.append(item)
                source_news_dict[source['name']].append(item)
    return all_news, source_news_dict

# --- Groq مع التحديث الذكي لتقطيع الكلمات (حل الفاصلة العربية) ---
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:50]
        prompt = f"""
        استخرج أهم 6 مواضيع أو أحداث (ترند) من هذه العناوين:
        {" | ".join(sample_titles)}
        
        شروط:
        1. النتيجة كلمات فقط مفصولة بفاصلة.
        2. عربية حصراً.
        3. بدون أي شرح.
        """
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}, 
                            headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
        if res.status_code == 200:
            content = res.json()['choices'][0]['message']['content'].strip()
            # هنا السحر: القص باستخدام الفاصلة الإنجليزية (,) أو العربية (،) أو الخط (-)
            trends = [t.strip() for t in re.split(r'[,،\-]', content) if len(t.strip()) > 2]
            return trends[:6] if trends else None
    except: pass
    return None

def get_trends_fallback(news_list):
    STOP_WORDS = set(["على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "بسبب", "حول", "وقد", "أنه", "كما", "ذلك", "فقط", "اليوم", "صور", "فيديو", "عاجل", "تفاصيل", "أكثر"])
    words = []
    for item in news_list:
        for word in re.findall(r'[\u0600-\u06FF]+', item['title']):
            if len(word) > 3 and word not in STOP_WORDS: words.append(word)
    return [word for word, count in Counter(words).most_common(6) if count > 1]

with st.spinner('⏳ جاري تخطي الحماية ومسح المصادر...'):
    news_data, source_data_dict = fetch_trending_data()
    dominating_trends = get_trends_from_groq(news_data) or get_trends_fallback(news_data)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if sidebar_logo := get_resized_logo(width_size=80):
    st.sidebar.columns([1, 2, 1])[1].image(sidebar_logo)
st.sidebar.markdown("<h3 style='text-align: center; margin-top: -5px;'>SherifOsmanClub</h3>", unsafe_allow_html=True)
st.sidebar.divider()

if 'view_mode' not in st.session_state: st.session_state.update({'view_mode': 'trend', 'selected_value': ""})

if dominating_trends:
    st.sidebar.subheader("🚨 ترند الساعة (AI)")
    for trend in dominating_trends:
        if st.sidebar.button(f"🔥 {trend}", key=f"tr_{trend}", use_container_width=True):
            st.session_state.update({'view_mode': 'trend', 'selected_value': trend})
st.sidebar.divider()

st.sidebar.subheader("🟢 غرف المصادر المباشرة")
for source in ALL_SOURCES:
    news_count = len(source_data_dict.get(source['name'], []))
    if st.sidebar.button(f"{'🟢' if news_count > 0 else '🔴'} {source['name']} ({news_count})", key=f"src_{source['name']}", use_container_width=True):
        st.session_state.update({'view_mode': 'source', 'selected_value': source['name']})

if st.session_state.selected_value == "" and dominating_trends: st.session_state.selected_value = dominating_trends[0]

if st.session_state.view_mode == 'trend':
    st.subheader(f"🔍 تغطية حية لترند الساعة: 【 {st.session_state.selected_value} 】")
    related_items = [item for item in news_data if st.session_state.selected_value.lower() in item['title'].lower()]
else:
    st.subheader(f"📡 بث مباشر من غرفة أخبار: 【 {st.session_state.selected_value} 】")
    related_items = source_data_dict.get(st.session_state.selected_value, [])

if related_items:
    if st.session_state.view_mode == 'source': st.write(f"إجمالي الأخبار: **{len(related_items)} خبر**")
    cols = st.columns(3)
    for i, item in enumerate(related_items):
        with cols[i % 3]:
            st.image(item['image'], use_container_width=True)
            st.markdown(f"**{item['source']}**\n[{item['title']}]({item['link']})\n---")
else:
    st.info("لا توجد أخبار منشورة حالياً تحت هذا التبويب. إذا كان العداد (0)، فالمصدر محجوب من السيرفر الأصلي.")
