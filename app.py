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

# --- التنسيق العلوي ---
col_text, col_logo = st.columns([6, 1]) 
with col_logo:
    logo_img = get_resized_logo(width_size=100)
    if logo_img: st.image(logo_img)
with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("الرادار المستقل للأخبار العاجلة وترندات الساعة من المصادر الرسمية.")
st.divider()

# 2. بنك المصادر الرسمية 100% (24 مصدر قوي ومباشر)
ALL_SOURCES = [
    {"name": "المصري اليوم", "url": "https://www.almasryalyoum.com/rss/rss"},
    {"name": "اليوم السابع", "url": "https://www.youm7.com/rss/SectionRss?SectionID=65"},
    {"name": "القاهرة 24", "url": "https://www.cairo24.com/rss"},
    {"name": "صدى البلد", "url": "https://www.elbalad.news/rss.aspx"},
    {"name": "الشروق", "url": "https://www.shorouknews.com/rss/home.aspx"},
    {"name": "الوفد", "url": "https://alwafd.news/rss"},
    {"name": "الوطن", "url": "https://www.elwatannews.com/home/rss"},
    {"name": "بوابة الأهرام", "url": "https://gate.ahram.org.eg/NewsRss.aspx"},
    {"name": "الدستور", "url": "https://www.dostor.org/rss.aspx"},
    {"name": "فيتو", "url": "https://www.vetogate.com/rss.aspx"},
    {"name": "أخبار اليوم", "url": "https://akhbarelyom.com/rss/home"},
    {"name": "مصراوي", "url": "https://www.masrawy.com/CrossDomain/Public/RSS/HomePage"},
    {"name": "عربي 21", "url": "https://arabi21.com/rss"},
    {"name": "عربي بوست", "url": "https://arabicpost.net/feed/"},
    {"name": "الشرق الأوسط", "url": "https://aawsat.com/feed"},
    {"name": "الجزيرة", "url": "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"},
    {"name": "BBC عربي", "url": "http://feeds.bbci.co.uk/arabic/rss.xml"},
    {"name": "روسيا اليوم", "url": "https://arabic.rt.com/rss/"},
    {"name": "سكاي نيوز", "url": "https://www.skynewsarabia.com/web/rss.xml"},
    {"name": "CNN بالعربية", "url": "https://arabic.cnn.com/api/v1/rss/middle_east/rss.xml"},
    {"name": "العربية نت", "url": "https://www.alarabiya.net/.mrss/ar/latest-news.xml"},
    {"name": "القدس العربي", "url": "https://www.alquds.co.uk/feed/"},
    {"name": "اندبندنت عربية", "url": "https://www.independentarabia.com/rss"},
    {"name": "فرانس 24", "url": "https://www.france24.com/ar/rss"}
]

# 3. دالة استخراج الصور المتطورة للمواقع الرسمية
def extract_image_url(entry):
    if hasattr(entry, 'media_thumbnail') and len(entry.media_thumbnail) > 0: 
        return entry.media_thumbnail[0]['url']
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0: 
        return entry.media_content[0]['url']
    if hasattr(entry, 'links'):
        for link in entry.links:
            if link.get('type', '').startswith('image/'): return link['href']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'): return enc['href']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary)
        if match: return match.group(1)
    # صورة افتراضية أنيقة في حال غياب الصورة تماماً من المصدر الرسمي
    return "https://images.unsplash.com/photo-1495020689067-958852a7765e?q=80&w=500"

# --- جلب البيانات ---
@st.cache_data(ttl=600)
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    for source in ALL_SOURCES:
        try:
            res = requests.get(source['url'], headers=headers, timeout=10)
            feed = feedparser.parse(res.content)
            if feed.entries:
                for entry in feed.entries[:30]:
                    item = {
                        "title": entry.title.strip(),
                        "link": entry.link,
                        "source": source['name'],
                        "image": extract_image_url(entry)
                    }
                    all_news.append(item)
                    source_news_dict[source['name']].append(item)
        except: continue
    return all_news, source_news_dict

# --- Groq الذكي (بأوامر صارمة لقص الترندات ككلمات مفردة) ---
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:50]
        prompt = f"""
        استخرج أهم 6 مواضيع أو أسماء شخصيات (ترند) من هذه العناوين:
        {" | ".join(sample_titles)}
        
        شروط عسكرية صارمة:
        1. النتيجة يجب أن تكون كلمات مفردة فقط (كلمة واحدة لكل ترند).
        2. مفصولة بفاصلة عربية (،).
        3. ممنوع كتابة أي جمل أو أفعال أو شرح.
        مثال للرد الصحيح: الأهلي، غزة، الدولار، ترامب، الذهب، الطقس
        """
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}, 
                            headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
        if res.status_code == 200:
            content = res.json()['choices'][0]['message']['content'].strip()
            # تقسيم دقيق لضمان خروج الكلمات مفردة
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

with st.spinner('⏳ جاري جلب الأخبار من المواقع الرسمية مباشرة...'):
    news_data, source_data_dict = fetch_trending_data()
    dominating_trends = get_trends_from_groq(news_data) or get_trends_fallback(news_data)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if sidebar_logo := get_resized_logo(width_size=80):
    st.sidebar.columns([1, 2, 1])[1].image(sidebar_logo)
st.sidebar.markdown("<h3 style='text-align: center; margin-top: -5px;'>SherifOsmanClub</h3>", unsafe_allow_html=True)
st.sidebar.divider()

if 'view_mode' not in st.session_state: st.session_state.update({'view_mode': 'trend', 'selected_value': ""})

# --- قائمة الترند ---
if dominating_trends:
    st.sidebar.subheader("🚨 ترند الساعة (AI)")
    for trend in dominating_trends:
        # إزالة أي مسافات زائدة لضمان عمل زر البحث بشكل مثالي
        clean_trend = trend.replace(".", "").strip()
        if st.sidebar.button(f"🔥 {clean_trend}", key=f"tr_{clean_trend}", use_container_width=True):
            st.session_state.update({'view_mode': 'trend', 'selected_value': clean_trend})
st.sidebar.divider()

# --- قائمة المصادر الـ 24 ---
st.sidebar.subheader("🟢 غرف المصادر المباشرة")
for source in ALL_SOURCES:
    news_count = len(source_data_dict.get(source['name'], []))
    if st.sidebar.button(f"{'🟢' if news_count > 0 else '🔴'} {source['name']} ({news_count})", key=f"src_{source['name']}", use_container_width=True):
        st.session_state.update({'view_mode': 'source', 'selected_value': source['name']})

if st.session_state.selected_value == "" and dominating_trends: st.session_state.selected_value = dominating_trends[0]

# --- الشاشة الرئيسية ---
if st.session_state.view_mode == 'trend':
    st.subheader(f"🔍 تغطية حية لترند الساعة: 【 {st.session_state.selected_value} 】")
    # البحث بمرونة داخل العناوين
    related_items = [item for item in news_data if st.session_state.selected_value.lower() in item['title'].lower()]
else:
    st.subheader(f"📡 بث مباشر من غرفة أخبار: 【 {st.session_state.selected_value} 】")
    related_items = source_data_dict.get(st.session_state.selected_value, [])

if related_items:
    if st.session_state.view_mode == 'source': st.write(f"إجمالي الأخبار: **{len(related_items)} خبر**")
    cols = st.columns(3)
    for i, item in enumerate(related_items):
        with cols[i % 3]:
            # عرض الصورة الأصلية بشكل مرتب
            st.image(item['image'], use_container_width=True)
            st.markdown(f"**{item['source']}**\n\n[{item['title']}]({item['link']})\n---")
else:
    st.info("لا توجد أخبار مطابقة حالياً. إذا كنت في قسم الترند، قد يكون الحدث منقضياً أو تم ذكره بكلمة مختلفة في العناوين.")
