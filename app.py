import streamlit as st
import feedparser
import re
import requests
import urllib.parse
from collections import Counter
import concurrent.futures
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

col_text, col_logo = st.columns([6, 1]) 
with col_logo:
    logo_img = get_resized_logo(width_size=100)
    if logo_img: st.image(logo_img)
with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("الرادار المستقل للأخبار العاجلة (مدعوم بتقنية السحب المتوازي فائقة السرعة).")
st.divider()

# 2. مصادرك الـ 24 الأصلية 
# (تمت معالجة القنوات المغلقة لتعمل عبر بروكسي RSS، والقنوات المفتوحة تعمل عبر RSSHub)
ALL_SOURCES = [
    # المصادر التي تدعم RSSHub (تليجرام) بامتياز
    {"name": "عربي 21", "url": "https://rsshub.app/telegram/channel/Arabi21News"},
    {"name": "بي بي سي عربي", "url": "https://rsshub.app/telegram/channel/bbcarabic"},
    {"name": "روسيا اليوم", "url": "https://rsshub.app/telegram/channel/RTarabic_News"},
    {"name": "تغطية غزة", "url": "https://rsshub.app/telegram/channel/GazaNewsNow"},
    {"name": "الحدث", "url": "https://rsshub.app/telegram/channel/alhadath"},
    {"name": "اليوم السابع", "url": "https://rsshub.app/telegram/channel/Youm7"},
    {"name": "صدى البلد", "url": "https://rsshub.app/telegram/channel/ElBaladOfficial"},
    {"name": "الشرق الأوسط", "url": "https://rsshub.app/telegram/channel/aawsat_news"},
    {"name": "مدى مصر", "url": "https://rsshub.app/telegram/channel/MadaMasr"},
    {"name": "عربي بوست", "url": "https://rsshub.app/telegram/channel/Arabic_Post"},
    {"name": "الجزيرة مصر", "url": "https://rsshub.app/telegram/channel/AJA_Egypt"},
    {"name": "سكاي نيوز", "url": "https://rsshub.app/telegram/channel/SkyNewsArabia_B"},
    {"name": "مزيد", "url": "https://rsshub.app/telegram/channel/Mazeeed"},
    {"name": "حقوق الإنسان", "url": "https://rsshub.app/telegram/channel/AmnestyAR"},

    # المصادر التي أغلقت التليجرام (تم إجبارها على العمل عبر RSS سريع مخفي)
    {"name": "شبكة رصد", "url": "https://api.allorigins.win/raw?url=https://rassd.com/feed"},
    {"name": "القاهرة 24", "url": "https://api.allorigins.win/raw?url=https://www.cairo24.com/rss"},
    {"name": "المصري اليوم", "url": "https://api.allorigins.win/raw?url=https://www.almasryalyoum.com/rss/rss"},
    {"name": "إيكاد Eekad", "url": "https://api.allorigins.win/raw?url=https://eekad.net/feed"},
    {"name": "تليجراف مصر", "url": "https://api.allorigins.win/raw?url=https://telegraphmisr.com/rss"},
    {"name": "العربي الجديد", "url": "https://api.allorigins.win/raw?url=https://www.alaraby.co.uk/rss"},
    {"name": "قناة الشرق", "url": "https://api.allorigins.win/raw?url=https://elsharq.tv/feed"},
    {"name": "مكملين", "url": "https://api.allorigins.win/raw?url=https://mekameleen.tv/feed"},
    {"name": "الجزيرة عاجل", "url": "https://api.allorigins.win/raw?url=https://www.aljazeera.net/xml/rss/all.xml"},
    {"name": "العربية عاجل", "url": "https://api.allorigins.win/raw?url=https://www.alarabiya.net/.mrss/ar/latest-news.xml"}
]

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=500&q=80"

def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0: return entry.media_content[0]['url']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0: return entry.enclosures[0]['href']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary)
        if match: return match.group(1)
    return DEFAULT_IMAGE

# --- دالة سحب بيانات لمصدر واحد بمهلة قصيرة جداً لمنع البطء ---
def fetch_single_source(source):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    items = []
    try:
        # مهلة 5 ثوانٍ فقط، إذا لم يرد المصدر يتجاوزه فوراً لكي لا يُبطئ الموقع
        res = requests.get(source['url'], headers=headers, timeout=5)
        feed = feedparser.parse(res.content)
        if feed.entries:
            for entry in feed.entries[:20]:
                clean_title = re.sub(r'<[^>]+>', '', entry.title).strip()
                if len(clean_title) > 130: clean_title = clean_title[:130] + "..."
                items.append({
                    "title": clean_title,
                    "link": entry.link,
                    "source": source['name'],
                    "image": extract_image_url(entry)
                })
        return source['name'], items
    except:
        return source['name'], []

# --- تقنية الخيوط المتوازية (Threading) لسرعة صاروخية ---
@st.cache_data(ttl=300) 
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    
    # الهجوم على الـ 24 مصدراً في نفس اللحظة عبر 15 خيط برمجي
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        results = executor.map(fetch_single_source, ALL_SOURCES)
        
    for source_name, items in results:
        if items:
            all_news.extend(items)
            source_news_dict[source_name] = items
            
    return all_news, source_news_dict

# --- Groq الذكي للترند ---
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:60]
        prompt = f"""
        اقرأ هذه العناوين:
        {" | ".join(sample_titles)}
        استخرج أهم 6 ترندات حالية. 
        شروط عسكرية صارمة:
        1. كل ترند يجب أن يكون (كلمة واحدة فقط)، إما اسم شخص، دولة، أو حدث.
        2. ممنوع استخدام أي أفعال أو جمل.
        3. النتائج مفصولة بفاصلة عربية (،) فقط.
        """
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}, 
                            headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
        if res.status_code == 200:
            content = res.json()['choices'][0]['message']['content'].strip()
            trends = [t.strip() for t in re.split(r'[,،\-]', content) if len(t.strip()) > 2 and len(t.split()) <= 2]
            return trends[:6] if trends else None
    except: pass
    return None

def get_trends_fallback(news_list):
    STOP_WORDS = set(["على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "بسبب", "حول", "وقد", "أنه", "كما", "ذلك", "فقط", "اليوم"])
    words = []
    for item in news_list:
        for word in re.findall(r'[\u0600-\u06FF]+', item['title']):
            if len(word) > 3 and word not in STOP_WORDS: words.append(word)
    return [word for word, count in Counter(words).most_common(6) if count > 1]

# --- تشغيل الواجهة ---
with st.spinner('⏳ جاري مسح الـ 24 مصدراً بسرعة البرق...'):
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
        clean_trend = trend.replace(".", "").strip()
        if st.sidebar.button(f"🔥 {clean_trend}", key=f"tr_{clean_trend}", use_container_width=True):
            st.session_state.update({'view_mode': 'trend', 'selected_value': clean_trend})
st.sidebar.divider()

st.sidebar.subheader("🟢 غرف المصادر المباشرة")
for source in ALL_SOURCES:
    news_count = len(source_data_dict.get(source['name'], []))
    status_icon = "🟢" if news_count > 0 else "🔴"
    if st.sidebar.button(f"{status_icon} {source['name']} ({news_count})", key=f"src_{source['name']}", use_container_width=True):
        st.session_state.update({'view_mode': 'source', 'selected_value': source['name']})

if st.session_state.selected_value == "" and dominating_trends: st.session_state.selected_value = dominating_trends[0]

if st.session_state.view_mode == 'trend':
    st.subheader(f"🔍 تغطية حية لترند الساعة: 【 {st.session_state.selected_value} 】")
    related_items = [item for item in news_data if st.session_state.selected_value.lower() in item['title'].lower()]
else:
    st.subheader(f"📡 بث مباشر من غرفة أخبار: 【 {st.session_state.selected_value} 】")
    related_items = source_data_dict.get(st.session_state.selected_value, [])

if related_items:
    if st.session_state.view_mode == 'source': st.write(f"إجمالي الأخبار المتاحة: **{len(related_items)} خبر**")
    cols = st.columns(3)
    for i, item in enumerate(related_items):
        with cols[i % 3]:
            try: st.image(item['image'], use_container_width=True)
            except: st.image(DEFAULT_IMAGE, use_container_width=True)
            st.markdown(f"**{item['source']}**\n\n[{item['title']}]({item['link']})\n---")
else:
    st.info("لا توجد أخبار حالياً في هذا القسم.")
