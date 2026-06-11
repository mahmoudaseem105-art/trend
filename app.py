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

col_text, col_logo = st.columns([6, 1]) 
with col_logo:
    logo_img = get_resized_logo(width_size=100)
    if logo_img: st.image(logo_img)
with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("الرادار المستقل للأخبار العاجلة والنبض الحقيقي للسوشيال ميديا.")
st.divider()

# 2. مصادرك الخاصة (مربوطة بقنوات السوشيال ميديا/تليجرام الرسمية لتحديثات لحظية)
ALL_SOURCES = [
    {"name": "شبكة رصد (سوشيال)", "url": "https://rsshub.app/telegram/channel/rassd_egypt"},
    {"name": "القاهرة 24 (سوشيال)", "url": "https://rsshub.app/telegram/channel/cairo24_news"},
    {"name": "اليوم السابع (سوشيال)", "url": "https://rsshub.app/telegram/channel/Youm7"},
    {"name": "المصري اليوم (سوشيال)", "url": "https://rsshub.app/telegram/channel/almasryalyoum"},
    {"name": "إيكاد Eekad (سوشيال)", "url": "https://rsshub.app/telegram/channel/EekadFacts"},
    {"name": "عربي 21 (سوشيال)", "url": "https://rsshub.app/telegram/channel/Arabi21News"},
    {"name": "مدى مصر (سوشيال)", "url": "https://rsshub.app/telegram/channel/MadaMasr"},
    {"name": "عربي بوست (سوشيال)", "url": "https://rsshub.app/telegram/channel/Arabic_Post"},
    {"name": "مزيد (سوشيال)", "url": "https://rsshub.app/telegram/channel/Mazeeed"},
    {"name": "تليجراف مصر (سوشيال)", "url": "https://rsshub.app/telegram/channel/telegraph_egypt"},
    {"name": "صدى البلد (سوشيال)", "url": "https://rsshub.app/telegram/channel/ElBaladOfficial"},
    {"name": "الجزيرة مصر (سوشيال)", "url": "https://rsshub.app/telegram/channel/AJA_Egypt"},
    {"name": "الجزيرة عاجل (سوشيال)", "url": "https://rsshub.app/telegram/channel/AJA_News"},
    {"name": "الشرق الأوسط (سوشيال)", "url": "https://rsshub.app/telegram/channel/aawsat_news"},
    {"name": "حقوق الإنسان (سوشيال)", "url": "https://rsshub.app/telegram/channel/AmnestyAR"},
    {"name": "العربية عاجل (سوشيال)", "url": "https://rsshub.app/telegram/channel/Alarabiya_Brk"},
    {"name": "سكاي نيوز (سوشيال)", "url": "https://rsshub.app/telegram/channel/SkyNewsArabia_B"},
    {"name": "بي بي سي عربي (سوشيال)", "url": "https://rsshub.app/telegram/channel/bbcarabic"},
    {"name": "روسيا اليوم (سوشيال)", "url": "https://rsshub.app/telegram/channel/RTarabic_News"},
    {"name": "العربي الجديد (سوشيال)", "url": "https://rsshub.app/telegram/channel/alaraby_ar"},
    {"name": "قناة الشرق (سوشيال)", "url": "https://rsshub.app/telegram/channel/ElsharqTV"},
    {"name": "مكملين (سوشيال)", "url": "https://rsshub.app/telegram/channel/mekameeleen"},
    {"name": "The Guardian (Social)", "url": "https://rsshub.app/telegram/channel/guardian"},
    {"name": "حدث بالفعل", "url": "https://news.google.com/rss/search?q=site:hadathbelfael.com"}
]

def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0: return entry.media_content[0]['url']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary)
        if match: return match.group(1)
    if hasattr(entry, 'description'):
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.description)
        if match: return match.group(1)
    return "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=500&q=80"

# --- جلب البيانات مع نفق بروكسي للحماية ---
def fetch_feed_robust(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        f = feedparser.parse(res.content)
        if f.entries: return f
    except: pass
    
    # نفق بديل لضمان عدم توقف السوشيال ميديا
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        proxy_url = f"https://api.allorigins.win/raw?url={encoded_url}"
        res = requests.get(proxy_url, headers=headers, timeout=15)
        f = feedparser.parse(res.content)
        if f.entries: return f
    except: pass
    return None

@st.cache_data(ttl=300) # التحديث كل 5 دقائق لسرعة السوشيال ميديا
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    for source in ALL_SOURCES:
        feed = fetch_feed_robust(source['url'])
        if feed and feed.entries:
            for entry in feed.entries[:25]:
                # تنظيف نصوص التليجرام لتبدو كعناوين أنيقة
                clean_title = re.sub(r'<[^>]+>', '', entry.title).strip()
                if len(clean_title) > 100: clean_title = clean_title[:100] + "..."
                
                item = {
                    "title": clean_title, "link": entry.link,
                    "source": source['name'], "image": extract_image_url(entry)
                }
                all_news.append(item)
                source_news_dict[source['name']].append(item)
    return all_news, source_news_dict

# --- Groq الذكي بأوامر عسكرية صارمة للترند ---
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:60]
        prompt = f"""
        اقرأ هذه العناوين الإخبارية من السوشيال ميديا:
        {" | ".join(sample_titles)}
        
        استخرج أهم 6 ترندات حالية. 
        شروط التنفيذ عسكرية:
        1. كل ترند يجب أن يكون (كلمة واحدة فقط)، إما اسم شخص (مثل: بايدن)، دولة (مثل: مصر)، أو حدث (مثل: الدولار).
        2. ممنوع منعاً باتاً استخدام أي أفعال أو جمل طويلة.
        3. النتائج مفصولة بفاصلة عربية (،) فقط.
        """
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}, 
                            headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
        if res.status_code == 200:
            content = res.json()['choices'][0]['message']['content'].strip()
            # استخراج الكلمات المفردة فقط بدقة
            trends = [t.strip() for t in re.split(r'[,،\-]', content) if len(t.strip()) > 2 and len(t.split()) <= 2]
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

with st.spinner('⏳ جاري مسح قنوات السوشيال ميديا وتفريغ البيانات...'):
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
            st.markdown(f"**{item['source']}**\n\n[{item['title']}]({item['link']})\n---")
else:
    st.info("لا توجد ميديا مطابقة. الرادار يقوم بالتحديث المستمر لشبكات السوشيال ميديا.")
