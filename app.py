import streamlit as st
import feedparser
import re
from collections import Counter
from PIL import Image

# 1. إعدادات الصفحة والهوية الرسمية للمنصة
st.set_page_config(page_title="SherifOsmanClub الإخبارية", page_icon="🔥", layout="wide")

# اسم ملف اللوجو المستضاف في جيت هاب
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
    if logo_img:
        st.image(logo_img)

with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("الرادار المستقل للأخبار العاجلة وترندات الساعة الأكثر تداولاً وجدلاً على الساحة.")

st.divider()

# 2. بنك المصادر الشامل والكامل (24 مصدراً) مع ميزة التفعيل والأسماء المخصصة كما في الصورة
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
    {"name": "عربي نيوز Page", "url": "https://rss.app/feeds/IELo97hFudhqzc3b.xml"}, # مصدر بديل
    {"name": "The Guardian Page", "url": "https://www.theguardian.com/world/rss"},
    {"name": "The Economist Page", "url": "https://www.economist.com/the-world-this-week/rss.xml"},
    {"name": "BBC News Page", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"}
]

# 3. كلمات التوقف لفلترة الشوائب
STOP_WORDS = set([
    "على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "الذين", "عبر", "خلال", "بسبب", "حول",
    "وقد", "أنه", "كما", "ذلك", "وهي", "وهو", "بين", "عندما", "فقط", "وهناك", "عليها", "فيها",
    "منها", "إليها", "وإن", "وأن", "فإن", "بأن", "اليوم", "أمس", "غدا", "صور", "فيديو", "عاجل",
    "تفاصيل", "أكثر", "أقل", "أول", "آخر", "أهم", "بعض", "شاهد", "كيف", "لماذا", "متى", "أين"
])

# 4. دالة استخراج الصور
def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
        return entry.enclosures[0]['href']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if match: return match.group(1)
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=500&q=80"

# 5. جلب البيانات من الـ 24 مصدراً مع التخزين المؤقت
@st.cache_data(ttl=600)
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    
    for source in ALL_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:8]:
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

# 6. خوارزمية صيد ترند الساعة
def extract_dominating_trends(news_list, top_n=6):
    words = []
    for item in news_list:
        clean_text = re.sub(r'[^\w\s]', '', item['title'])
        for word in clean_text.split():
            if len(word) > 3 and word not in STOP_WORDS: 
                words.append(word)
    freq = Counter(words)
    return [word for word, count in freq.most_common(top_n) if count > 1]

# --- تشغيل الواجهة وجلب البيانات ---
with St.spinner('⏳ جاري تحديث الرادار ومسح الـ 24 منصة...'):
    news_data, source_data_dict = fetch_trending_data()

# --- إعدادات السحاب الجانبي (Sidebar) ---
st.sidebar.markdown("<br>", unsafe_allow_html=True)
sidebar_logo = get_resized_logo(width_size=80)
if sidebar_logo:
    side_col1, side_col2, side_col3 = st.sidebar.columns([1, 2, 1])
    with side_col2: st.image(sidebar_logo)

st.sidebar.markdown("<h3 style='text-align: center; margin-top: -5px;'>SherifOsmanClub</h3>", unsafe_allow_html=True)
st.sidebar.divider()

# الحفاظ على خيار التحكم لمعرفة ماذا اختار المستخدم (ترند أم مصدر محدد)
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'trend'
if 'selected_value' not in st.session_state:
    st.session_state.selected_value = ""

# --- القائمة الأولى: ترند الساعة ---
dominating_trends = extract_dominating_trends(news_data)
if dominating_trends:
    st.sidebar.subheader("🚨 ترند الساعة")
    # إذا ضغط المستخدم على ترند يحول وضع العرض لـ 'trend'
    for trend in dominating_trends:
        if st.sidebar.button(f"🔥 {trend}", key=f"tr_{trend}", use_container_width=True):
            st.session_state.view_mode = 'trend'
            st.session_state.selected_value = trend

st.sidebar.divider()

# --- القائمة الثانية الجديدة تماماً: غرف ومصادر الأخبار الحية المضيئة ---
st.sidebar.subheader("🟢 غرف المصادر المباشرة")
for source in ALL_SOURCES:
    # تنسيق الاسم بوضع لمبة خضراء مضيئة بجانبه تماماً كما في الصورة المرفقة
    display_name = f"🟢 {source['name']}"
    if st.sidebar.button(display_name, key=f"src_{source['name']}", use_container_width=True):
        st.session_state.view_mode = 'source'
        st.session_state.selected_value = source['name']

# في المرة الأولى نقوم بضبط القيمة الافتراضية لأول ترند صاعد
if st.session_state.selected_value == "" and dominating_trends:
    st.session_state.selected_value = dominating_trends[0]

# --- الشاشة الرئيسية للعرض الديناميكي ---
if st.session_state.view_mode == 'trend':
    # وضع عرض ترند الساعة المشترك
    current_trend = st.session_state.selected_value
    st.subheader(f"🔍 تغطية حية لترند الساعة: 【 {current_trend} 】")
    related_items = [item for item in news_data if current_trend in item['title']][:6]
else:
    # وضع عرض مصدر معين بجميع أخباره المستقلة
    current_source = st.session_state.selected_value
    st.subheader(f"📡 بث مباشر من غرفة أخبار: 【 {current_source} 】")
    related_items = source_data_dict.get(current_source, [])[:6]

# عرض النتائج والصور في شبكة احترافية من 3 أعمدة
if related_items:
    cols = st.columns(3)
    for index, item in enumerate(related_items):
        with cols[index % 3]:
            st.image(item['image'], use_container_width=True)
            st.markdown(f"**{item['source']}**")
            st.markdown(f"[{item['title']}]({item['link']})")
            st.write("---")
else:
    st.info("لا توجد ميديا منشورة حالياً تحت هذا التبويب، اختر مصدراً أو ترنداً آخر من القائمة.")
