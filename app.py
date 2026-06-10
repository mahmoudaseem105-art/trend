import streamlit as st
import feedparser
import re
import requests
from collections import Counter
from PIL import Image

# 1. إعدادات الصفحة والهوية الرسمية
st.set_page_config(page_title="SherifOsmanClub الإخبارية", page_icon="🔥", layout="wide")

GROQ_API_KEY = "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"
LOGO_IMAGE_PATH = "channels4_profile.png" 

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
    st.markdown("الرادار المستقل للأخبار العاجلة وترندات الساعة بالذكاء الاصطناعي.")
st.divider()

# 2. بنك المصادر (24 مصدراً)
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

# 3. دالة استخراج الصور
def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
        return entry.enclosures[0]['href']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if match: return match.group(1)
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=500&q=80"

# 4. جلب البيانات (مع كاسر الحماية المتطور)
@st.cache_data(ttl=600)
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    
    # رأس اتصال متقدم يحاكي متصفحاً حقيقياً لاختراق حظر rss.app
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Referer': 'https://google.com/'
    }
    
    for source in ALL_SOURCES:
        try:
            # نحاول أولاً باستخدام feedparser مع القناع
            feed = feedparser.parse(source['url'], agent=headers['User-Agent'])
            if not feed.entries:
                # إذا فشل، نستخدم requests كبديل هجومي
                res = requests.get(source['url'], headers=headers, timeout=10)
                feed = feedparser.parse(res.content)
                
            for entry in feed.entries:
                item = {
                    "title": entry.title,
                    "link": entry.link,
                    "source": source['name'],
                    "image": extract_image_url(entry)
                }
                all_news.append(item)
                source_news_dict[source['name']].append(item)
        except: continue
    return all_news, source_news_dict

# 5. استنتاج الترند بواسطة Groq (مع أوامر صارمة بعدم الترجمة)
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:50]
        text_block = "\n".join(sample_titles)
        
        prompt = f"""
        أنت محلل بيانات إخبارية خبير. اقرأ هذه العناوين:
        {text_block}
        
        استخرج أهم 6 مواضيع أو أسماء شخصيات تتكرر فيها.
        شروط هامة جداً:
        1. أريد النتيجة كقائمة كلمات فقط مفصولة بفاصلة.
        2. استخرج الكلمة بنفس اللغة المكتوبة بها في العناوين (لا تترجم الكلمات الإنجليزية إلى العربية).
        3. بدون أي نص إضافي أو شرح.
        """
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        api_headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        
        res = requests.post(url, json=payload, headers=api_headers, timeout=15)
        if res.status_code == 200:
            content = res.json()['choices'][0]['message']['content'].strip()
            trends = [t.strip() for t in content.split(',') if len(t.strip()) > 2]
            return trends[:6] if trends else None
    except: pass
    return None

# 6. نظام الطوارئ
def get_trends_fallback(news_list):
    STOP_WORDS = set(["على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "بسبب", "حول", "وقد", "أنه", "كما", "ذلك", "فقط", "اليوم", "صور", "فيديو", "عاجل", "تفاصيل", "أكثر"])
    words = []
    for item in news_list:
        arabic_words = re.findall(r'[\u0600-\u06FF]+', item['title'])
        for word in arabic_words:
            if len(word) > 3 and word not in STOP_WORDS: words.append(word)
    freq = Counter(words)
    return [word for word, count in freq.most_common(6) if count > 1]

# --- تشغيل الواجهة ---
with st.spinner('⏳ جاري مسح المصادر واصطياد الترندات...'):
    news_data, source_data_dict = fetch_trending_data()
    
    dominating_trends = get_trends_from_groq(news_data)
    if not dominating_trends:
        dominating_trends = get_trends_fallback(news_data)

# --- إعدادات السحاب الجانبي (Sidebar) ---
st.sidebar.markdown("<br>", unsafe_allow_html=True)
sidebar_logo = get_resized_logo(width_size=80)
if sidebar_logo:
    side_col1, side_col2, side_col3 = st.sidebar.columns([1, 2, 1])
    with side_col2: st.image(sidebar_logo)

st.sidebar.markdown("<h3 style='text-align: center; margin-top: -5px;'>SherifOsmanClub</h3>", unsafe_allow_html=True)
st.sidebar.divider()

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'trend'
if 'selected_value' not in st.session_state:
    st.session_state.selected_value = ""

# --- القائمة الأولى: ترند الساعة ---
if dominating_trends:
    st.sidebar.subheader("🚨 ترند الساعة (AI)")
    for trend in dominating_trends:
        if st.sidebar.button(f"🔥 {trend}", key=f"tr_{trend}", use_container_width=True):
            st.session_state.view_mode = 'trend'
            st.session_state.selected_value = trend

st.sidebar.divider()

# --- القائمة الثانية: غرف المصادر (مع العداد الحي) ---
st.sidebar.subheader("🟢 غرف المصادر المباشرة")
for source in ALL_SOURCES:
    # جلب عدد الأخبار في كل مصدر لعرضه للمستخدم
    news_count = len(source_data_dict.get(source['name'], []))
    status_icon = "🟢" if news_count > 0 else "🔴"
    
    display_name = f"{status_icon} {source['name']} ({news_count})"
    if st.sidebar.button(display_name, key=f"src_{source['name']}", use_container_width=True):
        st.session_state.view_mode = 'source'
        st.session_state.selected_value = source['name']

if st.session_state.selected_value == "" and dominating_trends:
    st.session_state.selected_value = dominating_trends[0]

# --- الشاشة الرئيسية للعرض ---
if st.session_state.view_mode == 'trend':
    current_trend = st.session_state.selected_value
    st.subheader(f"🔍 تغطية حية لترند الساعة: 【 {current_trend} 】")
    # بحث مرن (يتجاهل الحروف الكبيرة والصغيرة ليتوافق مع الإنجليزي والعربي)
    related_items = [item for item in news_data if current_trend.lower() in item['title'].lower()]
else:
    current_source = st.session_state.selected_value
    st.subheader(f"📡 بث مباشر من غرفة أخبار: 【 {current_source} 】")
    related_items = source_data_dict.get(current_source, [])

if related_items:
    if st.session_state.view_mode == 'source':
        st.write(f"إجمالي الأخبار المتاحة من المصدر حالياً: **{len(related_items)} خبر**")
    cols = st.columns(3)
    for index, item in enumerate(related_items):
        with cols[index % 3]:
            st.image(item['image'], use_container_width=True)
            st.markdown(f"**{item['source']}**")
            st.markdown(f"[{item['title']}]({item['link']})")
            st.write("---")
else:
    st.info("لا توجد أخبار منشورة حالياً تحت هذا التبويب. إذا كان العداد بجانب المصدر (0)، فهذا يعني أن المصدر الرئيسي متوقف مؤقتاً.")
