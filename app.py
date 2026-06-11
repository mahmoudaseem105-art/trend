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
    st.markdown("الرادار المستقل للأخبار العاجلة (نظام المحركات الثلاثة المنيع).")
st.divider()

# 2. بنك المصادر (نظام المحركات الثلاثة الموزع بدقة)
ALL_SOURCES = [
    # --- المحرك الأول: السوشيال ميديا (تليجرام مباشر - المصادر الخضراء المؤكدة) ---
    {"name": "عربي 21", "type": "telegram", "val": "Arabi21News"},
    {"name": "بي بي سي عربي", "type": "telegram", "val": "bbcarabic"},
    {"name": "روسيا اليوم", "type": "telegram", "val": "RTarabic_News"},
    {"name": "تغطية غزة", "type": "telegram", "val": "GazaNewsNow"},
    {"name": "الحدث", "type": "telegram", "val": "alhadath"},
    
    # --- المحرك الثاني: الروابط الرسمية (RSS عبر بروكسي قوي لتخطي حظر Streamlit) ---
    {"name": "القاهرة 24", "type": "rss", "val": "https://www.cairo24.com/rss"},
    {"name": "اليوم السابع", "type": "rss", "val": "https://www.youm7.com/rss/SectionRss?SectionID=65"},
    {"name": "المصري اليوم", "type": "rss", "val": "https://www.almasryalyoum.com/rss/rss"},
    {"name": "صدى البلد", "type": "rss", "val": "https://www.elbalad.news/rss.aspx"},
    {"name": "الشرق الأوسط", "type": "rss", "val": "https://aawsat.com/feed"},
    {"name": "شبكة رصد", "type": "rss", "val": "https://rassd.com/feed"},
    {"name": "إيكاد Eekad", "type": "rss", "val": "https://eekad.net/feed"},
    {"name": "مدى مصر", "type": "rss", "val": "https://www.madamasr.com/ar/feed/"},
    {"name": "عربي بوست", "type": "rss", "val": "https://arabicpost.net/feed/"},
    {"name": "تليجراف مصر", "type": "rss", "val": "https://telegraphmisr.com/rss"},
    {"name": "العربي الجديد", "type": "rss", "val": "https://www.alaraby.co.uk/rss"},
    {"name": "قناة الشرق", "type": "rss", "val": "https://elsharq.tv/feed"},
    {"name": "مكملين", "type": "rss", "val": "https://mekameleen.tv/feed"},
    {"name": "الجزيرة مصر", "type": "rss", "val": "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"},
    {"name": "الجزيرة عاجل", "type": "rss", "val": "https://www.aljazeera.net/xml/rss/all.xml"},
    {"name": "العربية عاجل", "type": "rss", "val": "https://www.alarabiya.net/.mrss/ar/latest-news.xml"},
    {"name": "سكاي نيوز", "type": "rss", "val": "https://www.skynewsarabia.com/web/rss.xml"},
    
    # --- المحرك الثالث: محرك بحث جوجل (للمصادر العنيدة جداً) ---
    {"name": "مزيد", "type": "google", "val": "مزيد أخبار"},
    {"name": "حقوق الإنسان", "type": "google", "val": "منظمة العفو الدولية حقوق الإنسان"}
]

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=500&q=80"

# --- 3. محركات السحب الثلاثة ---

def fetch_telegram_direct(handle, source_name):
    url = f"https://t.me/s/{handle}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    items = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
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

def fetch_rss_direct(url, source_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    items = []
    # شبكة بروكسيات للضرب بيد من حديد لتخطي أي حظر من المواقع الكبرى
    proxy_urls = [
        url,
        f"https://api.allorigins.win/raw?url={urllib.parse.quote(url, safe='')}",
        f"https://api.codetabs.com/v1/proxy?quest={urllib.parse.quote(url, safe='')}"
    ]
    for purl in proxy_urls:
        try:
            res = requests.get(purl, headers=headers, timeout=12)
            feed = feedparser.parse(res.content)
            if not feed.entries: continue
            for entry in feed.entries[:20]:
                img_url = DEFAULT_IMAGE
                if hasattr(entry, 'media_content') and len(entry.media_content) > 0: img_url = entry.media_content[0]['url']
                elif hasattr(entry, 'enclosures') and len(entry.enclosures) > 0: img_url = entry.enclosures[0]['href']
                elif hasattr(entry, 'summary'):
                    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary)
                    if m: img_url = m.group(1)
                
                title = entry.title.strip()
                title = re.sub(r' - [^-]+$', '', title).strip() # تنظيف هوامش جوجل إن وجدت
                items.append({
                    "title": title, "link": entry.link, "source": source_name, "image": img_url
                })
            if items: return items
        except: continue
    return items

def fetch_google_news(query, source_name):
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ar&gl=EG&ceid=EG:ar"
    return fetch_rss_direct(url, source_name)

@st.cache_data(ttl=300) 
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    for source in ALL_SOURCES:
        # توجيه المهمة للمحرك المخصص بذكاء
        if source['type'] == 'telegram':
            channel_items = fetch_telegram_direct(source['val'], source['name'])
        elif source['type'] == 'rss':
            channel_items = fetch_rss_direct(source['val'], source['name'])
        else:
            channel_items = fetch_google_news(source['val'], source['name'])
            
        if channel_items:
            all_news.extend(channel_items)
            source_news_dict[source['name']] = channel_items
    return all_news, source_news_dict

# --- 4. Groq الذكي ---
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:60]
        prompt = f"""
        اقرأ هذه العناوين الإخبارية:
        {" | ".join(sample_titles)}
        
        استخرج أهم 6 ترندات حالية. 
        شروط عسكرية صارمة جداً:
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
    STOP_WORDS = set(["على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "بسبب", "حول", "وقد", "أنه", "كما", "ذلك", "فقط", "اليوم", "صور", "فيديو", "عاجل", "تفاصيل"])
    words = []
    for item in news_list:
        for word in re.findall(r'[\u0600-\u06FF]+', item['title']):
            if len(word) > 3 and word not in STOP_WORDS: words.append(word)
    return [word for word, count in Counter(words).most_common(6) if count > 1]

# --- 5. تشغيل النظام ---
with st.spinner('⏳ جاري تشغيل المحركات الثلاثية واختراق الحظر...'):
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
    if st.session_state.view_mode == 'source': st.write(f"إجمالي الأخبار المتاحة: **{len(related_items)} خبر**")
    cols = st.columns(3)
    for i, item in enumerate(related_items):
        with cols[i % 3]:
            # درع الحماية ضد الصور المعطوبة لكي لا ينهار الموقع
            try:
                st.image(item['image'], use_container_width=True)
            except:
                st.image(DEFAULT_IMAGE, use_container_width=True)
            st.markdown(f"**{item['source']}**\n\n[{item['title']}]({item['link']})\n---")
else:
    st.info("الرادار يجمع الأخبار الآن، أو أن المصدر لم ينشر جديداً.")
