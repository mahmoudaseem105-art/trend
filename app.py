import streamlit as st
import feedparser
import requests
import re
import urllib.parse
import concurrent.futures
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
    st.markdown("الرادار المستقل للأخبار العاجلة. **(المصادر المتاحة تُعرض هنا، والمغلقة تفتح في نافذة جديدة مباشرة)**")
st.divider()

# --- 2. قائمتك الـ 24 الأصلية בדיוק (مع الروابط الخارجية للطوارئ) ---
ALL_SOURCES = [
    {"name": "المصري اليوم", "type": "rss", "val": "https://www.almasryalyoum.com/rss/rss", "ext_url": "https://www.almasryalyoum.com/"},
    {"name": "القاهرة 24", "type": "rss", "val": "https://www.cairo24.com/rss", "ext_url": "https://www.cairo24.com/"},
    {"name": "اليوم السابع", "type": "rss", "val": "https://www.youm7.com/rss/SectionRss?SectionID=65", "ext_url": "https://www.youm7.com/"},
    {"name": "صدى البلد", "type": "rss", "val": "https://www.elbalad.news/rss.aspx", "ext_url": "https://www.elbalad.news/"},
    {"name": "العربية مصر", "type": "rss", "val": "https://www.alarabiya.net/.mrss/ar/latest-news.xml", "ext_url": "https://www.alarabiya.net/egypt"},
    {"name": "حدث بالفعل", "type": "rss", "val": "https://hadathbelfael.com/feed", "ext_url": "https://hadathbelfael.com/"},
    {"name": "تليجراف مصر", "type": "rss", "val": "https://telegraphmisr.com/rss", "ext_url": "https://telegraphmisr.com/"},
    {"name": "صحيفة الشرق الأوسط", "type": "rss", "val": "https://aawsat.com/feed", "ext_url": "https://aawsat.com/"},
    {"name": "عربي 21", "type": "telegram", "val": "Arabi21News", "ext_url": "https://arabi21.com/"},
    {"name": "إيكاد Eekad", "type": "rss", "val": "https://eekad.net/feed", "ext_url": "https://eekad.net/"},
    {"name": "شبكة رصد", "type": "rss", "val": "https://rassd.com/feed", "ext_url": "https://rassd.com/"},
    {"name": "مدى مصر", "type": "rss", "val": "https://www.madamasr.com/ar/feed/", "ext_url": "https://www.madamasr.com/"},
    {"name": "شبكة مزيد", "type": "telegram", "val": "Mazeeed", "ext_url": "https://t.me/s/Mazeeed"},
    {"name": "عربي بوست", "type": "rss", "val": "https://arabicpost.net/feed/", "ext_url": "https://arabicpost.net/"},
    {"name": "العربي الجديد", "type": "rss", "val": "https://www.alaraby.co.uk/rss", "ext_url": "https://www.alaraby.co.uk/"},
    {"name": "حقوق الإنسان", "type": "rss", "val": "https://www.amnesty.org/ar/rss", "ext_url": "https://www.amnesty.org/ar/"},
    {"name": "تكنوقراط", "type": "telegram", "val": "EgyTechnocrats", "ext_url": "https://t.me/s/EgyTechnocrats"},
    {"name": "المصري اليوم إكس", "type": "none", "val": "", "ext_url": "https://twitter.com/AlMasryAlYoum"},
    {"name": "مزيد ستوريز", "type": "telegram", "val": "Mazeeed", "ext_url": "https://t.me/s/Mazeeed"},
    {"name": "الشرق الأوسط منشنز", "type": "none", "val": "", "ext_url": "https://twitter.com/aawsat_news"},
    {"name": "عربي نيوز", "type": "telegram", "val": "Arabi21News", "ext_url": "https://arabi21.com/"},
    {"name": "The Guardian", "type": "rss", "val": "https://www.theguardian.com/world/rss", "ext_url": "https://www.theguardian.com/world"},
    {"name": "The Economist", "type": "rss", "val": "https://www.economist.com/the-world-this-week/rss.xml", "ext_url": "https://www.economist.com/"},
    {"name": "BBC News", "type": "telegram", "val": "bbcarabic", "ext_url": "https://www.bbc.com/arabic"}
]

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1495020689067-958852a7765e?q=80&w=500"

# --- 3. محركات الجلب المباشرة (سريعة جداً وبدون وسطاء) ---
def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0: return entry.media_content[0]['url']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0: return entry.enclosures[0]['href']
    if hasattr(entry, 'description'):
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.description)
        if match: return match.group(1)
    return DEFAULT_IMAGE

def fetch_telegram_direct(handle, source_name):
    url = f"https://t.me/s/{handle}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}
    items = []
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code != 200: return []
        blocks = res.text.split('tgme_widget_message_wrap js-widget_message_wrap')[1:]
        for block in reversed(blocks):
            text_match = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', block, re.DOTALL)
            if not text_match: continue
            
            raw_text = text_match.group(1)
            clean_text = re.sub(r'<br/?>', ' | ', raw_text)
            clean_text = re.sub(r'<[^>]+>', '', clean_text).strip()
            if len(clean_text) < 15: continue
            
            img_match = re.search(r"background-image:\s*url\(['\"]?([^'\"]+)['\"]?\)", block)
            image_url = img_match.group(1) if img_match else DEFAULT_IMAGE
            
            link_match = re.search(r'href="(https://t.me/[^"]+/\d+)"', block)
            post_link = link_match.group(1) if link_match else url
            
            items.append({"title": clean_text[:200] + "...", "link": post_link, "source": source_name, "image": image_url})
            if len(items) >= 15: break
        return items
    except: return []

def fetch_rss_direct(url, source_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}
    items = []
    try:
        res = requests.get(url, headers=headers, timeout=4) # محاولة مباشرة سريعة
        if res.status_code == 200:
            feed = feedparser.parse(res.content)
            for entry in feed.entries[:15]:
                clean_title = re.sub(r' - [^-]+$', '', entry.title).strip()
                clean_title = re.sub(r'<[^>]+>', '', clean_title)
                items.append({
                    "title": clean_title[:200] + "...",
                    "link": entry.link, "source": source_name, "image": extract_image_url(entry)
                })
        return items
    except: return []

def fetch_single_source(source):
    if source['type'] == 'telegram':
        return source['name'], fetch_telegram_direct(source['val'], source['name'])
    elif source['type'] == 'rss':
        return source['name'], fetch_rss_direct(source['val'], source['name'])
    return source['name'], []

@st.cache_data(ttl=300) 
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    
    # خيوط متوازية للسرعة، بدون إرهاق السيرفرات لتجنب الحظر
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(fetch_single_source, ALL_SOURCES)
        
    for source_name, items in results:
        if items:
            all_news.extend(items)
            source_news_dict[source_name] = items
            
    return all_news, source_news_dict

# --- 4. Groq الذكي لترندات الساعة النقية ---
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:60]
        # إذا لم يكن هناك أخبار كافية، نسحب تغذية خلفية صامتة لضمان عمل الذكاء الاصطناعي
        if len(sample_titles) < 10:
            res_bg = requests.get("https://news.google.com/rss?hl=ar&gl=EG&ceid=EG:ar", timeout=5)
            feed_bg = feedparser.parse(res_bg.content)
            sample_titles = [entry.title for entry in feed_bg.entries[:40]]

        prompt = f"""
        اقرأ هذه العناوين الإخبارية:
        {" | ".join(sample_titles)}
        
        استخرج أهم 6 مواضيع أو أسماء شخصيات (ترند) تسيطر عليها.
        شروط:
        1. الترند كلمة واحدة فقط أو اسم علم مفرد (مثل غزة، بايدن، الأهلي).
        2. يمنع صياغة جمل تماماً.
        3. النتيجة مفصولة بفاصلة عربية (،) فقط.
        """
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}, 
                            headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=12)
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

# --- تشغيل جلب البيانات ---
with st.spinner('⏳ جاري بناء شاشة الأخبار الحية وفحص حالة المصادر...'):
    news_data, source_data_dict = fetch_trending_data()
    dominating_trends = get_trends_from_groq(news_data) or get_trends_fallback(news_data)

# --- إعدادات القائمة الجانبية (Sidebar) ---
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if sidebar_logo := get_resized_logo(width_size=80):
    st.sidebar.columns([1, 2, 1])[1].image(sidebar_logo)
st.sidebar.markdown("<h3 style='text-align: center; margin-top: -5px;'>SherifOsmanClub</h3>", unsafe_allow_html=True)

if 'selected_source' not in st.session_state: st.session_state.selected_source = "الكل"

# زر العودة للرئيسية ليعرض كل الأخبار المجمعة
if st.sidebar.button("🏠 الرئيسية (أحدث الأخبار)", use_container_width=True):
    st.session_state.selected_source = "الكل"
st.sidebar.divider()

# عرض أزرار الترند (تفتح بحث مباشر في New Tab)
if dominating_trends:
    st.sidebar.subheader("🚨 الترند (اضغط للانتقال)")
    for trend in dominating_trends:
        clean_trend = trend.replace(".", "").strip()
        trend_url = f"https://news.google.com/search?q={urllib.parse.quote(clean_trend)}&hl=ar&gl=EG&ceid=EG:ar"
        st.sidebar.link_button(f"🔥 {clean_trend}", url=trend_url, use_container_width=True)
st.sidebar.divider()

# عرض العداد الحي للمصادر الـ 24
st.sidebar.subheader("🟢 غرف المصادر")
for source in ALL_SOURCES:
    news_count = len(source_data_dict.get(source['name'], []))
    
    # 🟢 إذا كان المصدر مفتوحاً وسحبنا منه أخبار، نعرضه كزر داخل الموقع
    if news_count > 0:
        if st.sidebar.button(f"🟢 {source['name']} ({news_count})", use_container_width=True):
            st.session_state.selected_source = source['name']
    
    # 🔴 إذا كان المصدر مغلقاً أو أعطى (0)، نعرضه كزر (رابط ذكي 🔗) يفتح نافذة جديدة لموقعه
    else:
        st.sidebar.link_button(f"🔴 {source['name']} (0) - مباشر 🔗", url=source['ext_url'], use_container_width=True)

# --- شاشة العرض الرئيسية المنسقة ---
if st.session_state.selected_source == "الكل":
    st.subheader("📰 أحدث الأخبار من المصادر النشطة")
    related_items = news_data[:60] # عرض أحدث 60 خبراً من كل المصادر الخضراء لتكون الشاشة مليئة بالحياة
else:
    st.subheader(f"📡 بث مباشر من: 【 {st.session_state.selected_source} 】")
    related_items = source_data_dict.get(st.session_state.selected_source, [])

if related_items:
    cols = st.columns(3)
    for i, item in enumerate(related_items):
        with cols[i % 3]:
            try: st.image(item['image'], use_container_width=True)
            except: st.image(DEFAULT_IMAGE, use_container_width=True)
            
            st.markdown(f"**🔹 {item['source']}**")
            st.write(item['title']) 
            st.markdown(f"**[🔗 اقرأ التفاصيل من المصدر]({item['link']})**")
            st.markdown("---")
else:
    st.info("لا توجد أخبار حالياً في هذا القسم. اختر مصدراً من القائمة الجانبية.")
