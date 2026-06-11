import streamlit as st
import feedparser
import re
import requests
import urllib.parse
from collections import Counter
import concurrent.futures
from PIL import Image

# 1. إعدادات الصفحة والهوية الرسمية
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

# --- التنسيق العلوي للمنصة ---
col_text, col_logo = st.columns([6, 1]) 
with col_logo:
    logo_img = get_resized_logo(width_size=100)
    if logo_img: st.image(logo_img)
with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("الرادار المستقل للأخبار العاجلة وترندات الساعة الأكثر تداولاً.")
st.divider()

# 2. قائمة مصادرك الـ 24 الأصلية بالكامل مع معرفات التليجرام ومحركات البحث الخاصة بها
ALL_SOURCES = [
    {"name": "المصري اليوم", "handle": "almasryalyoum", "query": "site:almasryalyoum.com"},
    {"name": "القاهرة 24", "handle": "cairo24_news", "query": "site:cairo24.com"},
    {"name": "اليوم السابع", "handle": "Youm7", "query": "site:youm7.com"},
    {"name": "صدى البلد", "handle": "ElBaladOfficial", "query": "site:elbalad.news"},
    {"name": "العربية مصر", "handle": "AlArabiya_Egypt", "query": "العربية مصر"},
    {"name": "حدث بالفعل", "handle": "hadathbelfael", "query": "site:hadathbelfael.com"},
    {"name": "تليجراف مصر", "handle": "telegraph_egypt", "query": "site:telegraphmisr.com"},
    {"name": "صحيفة الشرق الأوسط", "handle": "aawsat_news", "query": "site:aawsat.com"},
    {"name": "عربي 21", "handle": "Arabi21News", "query": "site:arabi21.com"},
    {"name": "إيكاد Eekad", "handle": "EekadFacts", "query": "site:eekad.net"},
    {"name": "شبكة رصد", "handle": "rassd_egypt", "query": "site:rassd.com"},
    {"name": "مدى مصر", "handle": "MadaMasr", "query": "site:madamasr.com"},
    {"name": "شبكة مزيد", "handle": "Mazeeed", "query": "منصة مزيد الإخبارية"},
    {"name": "عربي بوست", "handle": "Arabic_Post", "query": "site:arabicpost.net"},
    {"name": "العربي الجديد", "handle": "alaraby_ar", "query": "site:alaraby.co.uk"},
    {"name": "حقوق الإنسان", "handle": "AmnestyAR", "query": "منظمة العفو الدولية حقوق الإنسان"},
    {"name": "تكنوقراط", "handle": "EgyTechnocrats", "query": "التكنوقراط المصريين"},
    {"name": "المصري اليوم إكس", "handle": "almasryalyoum", "query": "المصري اليوم"},
    {"name": "مزيد ستوريز", "handle": "Mazeeed", "query": "مزيد ستوريز"},
    {"name": "الشرق الأوسط منشنز", "handle": "aawsat_news", "query": "صحيفة الشرق الأوسط"},
    {"name": "عربي نيوز", "handle": "Arabi21News", "query": "عربي نيوز إخبارية"},
    {"name": "The Guardian", "handle": "guardian", "query": "site:theguardian.com"},
    {"name": "The Economist", "handle": "TheEconomist", "query": "site:economist.com"},
    {"name": "BBC News", "handle": "bbcworld", "query": "site:bbc.com/news"}
]

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1495020689067-958852a7765e?q=80&w=500"

# --- 3. محركات جلب البيانات الفردية ---

def fetch_telegram_direct(handle, source_name):
    url = f"https://t.me/s/{handle}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    items = []
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code != 200 or "tgme_widget_message_wrap" not in res.text: return []
        
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
            if len(items) >= 15: break
        return items
    except: return []

def fetch_google_news_fallback(query, source_name):
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ar&gl=EG&ceid=EG:ar"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    items = []
    try:
        res = requests.get(url, headers=headers, timeout=4)
        feed = feedparser.parse(res.content)
        if feed.entries:
            for entry in feed.entries[:15]:
                clean_title = re.sub(r' - [^-]+$', '', entry.title).strip()
                clean_title = re.sub(r'<[^>]+>', '', clean_title)
                items.append({
                    "title": clean_title,
                    "link": entry.link,
                    "source": source_name,
                    "image": DEFAULT_IMAGE
                })
        return items
    except: return []

# دالة الفحص المزدوج لكل مصدر لمنع ظهور الصفر (0)
def fetch_single_source(source):
    # المحاولة الأولى: التليجرام المباشر لنبض السوشيال ميديا
    items = fetch_telegram_direct(source['handle'], source['name'])
    if items: 
        return source['name'], items
        
    # المحاولة الثانية (البديل التلقائي): محرك البحث المخصص لنفس المصدر عند انغلاق التليجرام
    items = fetch_google_news_fallback(source['query'], source['name'])
    return source['name'], items

# --- 4. معالج السحب الآمن والموازنة لسرعة التصفح ---
@st.cache_data(ttl=300) 
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    
    # استخدام عدد خيوط آمن (max_workers=5) لضمان السرعة وعدم التسبب في الحظر
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_single_source, ALL_SOURCES)
        
    for source_name, items in results:
        if items:
            all_news.extend(items)
            source_news_dict[source_name] = items
            
    return all_news, source_news_dict

# --- 5. Groq الذكي لترندات الساعة النقية ---
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:60]
        prompt = f"""
        اقرأ هذه العناوين الإخبارية الحالية:
        {" | ".join(sample_titles)}
        
        استخرج أهم 6 مواضيع أو أسماء شخصيات (ترند) تسيطر عليها.
        شروط التنفيذ:
        1. كل ترند يجب أن يكون كلمة واحدة فقط أو اسم علم مفرد (مثال: غزة، ترامب، الأهلي).
        2. يمنع تماماً صياغة جمل أو عبارات طويلة.
        3. النتيجة كلمات مفصولة بفاصلة عربية (،) فقط وبدون شرح أو مقدمات.
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

# --- تشغيل جلب البيانات الواجهة الرسومية ---
with st.spinner('⏳ جاري مسح وتحديث مصادرك الـ 24 المعتمدة...'):
    news_data, source_data_dict = fetch_trending_data()
    dominating_trends = get_trends_from_groq(news_data) or get_trends_fallback(news_data)

# --- إعدادات القائمة الجانبية (Sidebar) ---
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if sidebar_logo := get_resized_logo(width_size=80):
    st.sidebar.columns([1, 2, 1])[1].image(sidebar_logo)
st.sidebar.markdown("<h3 style='text-align: center; margin-top: -5px;'>SherifOsmanClub</h3>", unsafe_allow_html=True)
st.sidebar.divider()

if 'view_mode' not in st.session_state: st.session_state.update({'view_mode': 'trend', 'selected_value': ""})

# عرض أزرار الترندات المفردة
if dominating_trends:
    st.sidebar.subheader("🚨 ترند الساعة (AI)")
    for trend in dominating_trends:
        clean_trend = trend.replace(".", "").strip()
        if st.sidebar.button(f"🔥 {clean_trend}", key=f"tr_{clean_trend}", use_container_width=True):
            st.session_state.update({'view_mode': 'trend', 'selected_value': clean_trend})
st.sidebar.divider()

# عرض العداد الحي للمصادر الـ 24
st.sidebar.subheader("🟢 غرف المصادر المباشرة")
for source in ALL_SOURCES:
    news_count = len(source_data_dict.get(source['name'], []))
    status_icon = "🟢" if news_count > 0 else "🔴"
    if st.sidebar.button(f"{status_icon} {source['name']} ({news_count})", key=f"src_{source['name']}", use_container_width=True):
        st.session_state.update({'view_mode': 'source', 'selected_value': source['name']})

if st.session_state.selected_value == "" and dominating_trends: 
    st.session_state.selected_value = dominating_trends[0]

# --- شاشة العرض الرئيسية ---
if st.session_state.view_mode == 'trend':
    st.subheader(f"🔍 تغطية حية لترند الساعة: 【 {st.session_state.selected_value} 】")
    related_items = [item for item in news_data if st.session_state.selected_value.lower() in item['title'].lower()]
else:
    st.subheader(f"📡 بث مباشر من غرفة أخبار: 【 {st.session_state.selected_value} 】")
    related_items = source_data_dict.get(st.session_state.selected_value, [])

if related_items:
    if st.session_state.view_mode == 'source': st.write(f"إجمالي الأخبار المتوفرة: **{len(related_items)} خبر**")
    cols = st.columns(3)
    for i, item in enumerate(related_items):
        with cols[i % 3]:
            try: st.image(item['image'], use_container_width=True)
            except: st.image(DEFAULT_IMAGE, use_container_width=True)
            st.markdown(f"**{item['source']}**\n\n[{item['title']}]({item['link']})\n---")
else:
    st.info("لا توجد ميديا مطابقة حالياً، يرجى اختيار تبويب آخر من القائمة الجانبية.")
