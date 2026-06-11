import streamlit as st
import feedparser
import re
import requests
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
    st.markdown("الرادار المستقل للأخبار العاجلة (نسخة الاستقرار المباشر بدون وسطاء).")
st.divider()

# 2. مصادرك الـ 24 المحددة (مقسمة تقنياً لتعمل بدون بروكسيات تحظرنا)
ALL_SOURCES = [
    # المصادر التي تملك قنوات تليجرام مفتوحة (تعمل بمحرك الاختراق المباشر)
    {"name": "عربي 21", "type": "telegram", "val": "Arabi21News"},
    {"name": "بي بي سي عربي", "type": "telegram", "val": "bbcarabic"},
    {"name": "روسيا اليوم", "type": "telegram", "val": "RTarabic_News"},
    {"name": "تغطية غزة", "type": "telegram", "val": "GazaNewsNow"},
    {"name": "الحدث", "type": "telegram", "val": "alhadath"},
    {"name": "اليوم السابع", "type": "telegram", "val": "Youm7"},
    {"name": "صدى البلد", "type": "telegram", "val": "ElBaladOfficial"},
    {"name": "الشرق الأوسط", "type": "telegram", "val": "aawsat_news"},
    {"name": "مدى مصر", "type": "telegram", "val": "MadaMasr"},
    {"name": "عربي بوست", "type": "telegram", "val": "Arabic_Post"},
    {"name": "الجزيرة مصر", "type": "telegram", "val": "AJA_Egypt"},
    {"name": "سكاي نيوز", "type": "telegram", "val": "SkyNewsArabia_B"},
    {"name": "مزيد", "type": "telegram", "val": "Mazeeed"},
    {"name": "حقوق الإنسان", "type": "telegram", "val": "AmnestyAR"},

    # المصادر التي نعتمد على روابط الـ RSS الرسمية الخاصة بها
    {"name": "شبكة رصد", "type": "rss", "val": "https://rassd.com/feed"},
    {"name": "القاهرة 24", "type": "rss", "val": "https://www.cairo24.com/rss"},
    {"name": "المصري اليوم", "type": "rss", "val": "https://www.almasryalyoum.com/rss/rss"},
    {"name": "إيكاد Eekad", "type": "rss", "val": "https://eekad.net/feed"},
    {"name": "تليجراف مصر", "type": "rss", "val": "https://telegraphmisr.com/rss"},
    {"name": "العربي الجديد", "type": "rss", "val": "https://www.alaraby.co.uk/rss"},
    {"name": "قناة الشرق", "type": "rss", "val": "https://elsharq.tv/feed"},
    {"name": "مكملين", "type": "rss", "val": "https://mekameleen.tv/feed"},
    {"name": "الجزيرة عاجل", "type": "rss", "val": "https://www.aljazeera.net/xml/rss/all.xml"},
    {"name": "العربية عاجل", "type": "rss", "val": "https://www.alarabiya.net/.mrss/ar/latest-news.xml"}
]

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=500&q=80"

# إنشاء جلسة واحدة مستقرة لعدم إثارة شكوك السيرفرات (Anti-Ban)
http_session = requests.Session()
http_session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'})

def extract_rss_image(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0: return entry.media_content[0]['url']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0: return entry.enclosures[0]['href']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary)
        if match: return match.group(1)
    return DEFAULT_IMAGE

# --- محرك التليجرام المباشر (يقرأ الـ HTML بدون API وبدون حظر) ---
def fetch_telegram(handle, source_name):
    url = f"https://t.me/s/{handle}"
    items = []
    try:
        res = http_session.get(url, timeout=7)
        if res.status_code != 200: return []
        blocks = res.text.split('tgme_widget_message_wrap js-widget_message_wrap')[1:]
        for block in reversed(blocks):
            text_match = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', block, re.DOTALL)
            if not text_match: continue
            
            raw_text = text_match.group(1)
            clean_text = re.sub(r'<br/?>', ' | ', raw_text)
            clean_text = re.sub(r'<[^>]+>', '', clean_text).strip()
            if len(clean_text) < 15: continue
            
            img_match = re.search(r"background-image:url\('([^']+)'\)", block)
            image_url = img_match.group(1) if img_match else DEFAULT_IMAGE
            
            link_match = re.search(r'href="(https://t.me/[^"]+/\d+)"', block)
            post_link = link_match.group(1) if link_match else url
            
            items.append({
                "title": clean_text[:130] + "..." if len(clean_text) > 130 else clean_text,
                "link": post_link, "source": source_name, "image": image_url
            })
            if len(items) >= 20: break
        return items
    except: return []

# --- محرك الـ RSS المباشر والهادئ ---
def fetch_rss(url, source_name):
    items = []
    try:
        res = http_session.get(url, timeout=7)
        feed = feedparser.parse(res.content)
        if feed.entries:
            for entry in feed.entries[:20]:
                clean_title = entry.title.strip()
                clean_title = re.sub(r'<[^>]+>', '', clean_title) # تنظيف العناوين
                items.append({
                    "title": clean_title,
                    "link": entry.link,
                    "source": source_name,
                    "image": extract_rss_image(entry)
                })
        return items
    except: return []

# سحب متسلسل آمن (يأخذ بضع ثواني إضافية ولكنه مستقر 100%)
@st.cache_data(ttl=300) 
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    
    for source in ALL_SOURCES:
        if source['type'] == 'telegram':
            items = fetch_telegram(source['val'], source['name'])
        else:
            items = fetch_rss(source['val'], source['name'])
            
        if items:
            all_news.extend(items)
            source_news_dict[source['name']] = items
            
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
        شروط صارمة:
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
with st.spinner('⏳ جاري المسح الآمن للمصادر (يرجى الانتظار بضع ثوانٍ لضمان استقرار الاتصال)...'):
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
    st.info("لا توجد أخبار حالياً في هذا القسم. إذا كان العداد (0)، فهذا يعني أن المصدر الأصلي لم ينشر جديداً أو يمنع الوصول مؤقتاً.")
