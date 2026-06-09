import streamlit as st
import feedparser
import re
from collections import Counter
from PIL import Image

# 1. إعدادات الصفحة والهوية الرسمية للمنصة
st.set_page_config(page_title="SherifOsmanClub الإخبارية", page_icon="🔥", layout="wide")

# اسم ملف اللوجو المستضاف في جيت هاب
LOGO_IMAGE_PATH = "channels4_profile.png" 

# دالة ذكية لفتح وتصغير اللوجو برمجياً لضمان ظهوره بشكل احترافي
def get_resized_logo(width_size=120):
    try:
        img = Image.open(LOGO_IMAGE_PATH)
        # الحفاظ على تناسق أبعاد الصورة أثناء التصغير
        w_percent = (width_size / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        return img.resize((width_size, h_size), Image.Resampling.LANCZOS)
    except:
        return None

# --- تنسيق احترافي: اللوجو صغير في الأعلى بجوار العنوان ---
col_text, col_logo = st.columns([6, 1]) 

with col_logo:
    logo_img = get_resized_logo(width_size=100) # حجم صغير ومناسب لأعلى اليمين
    if logo_img:
        st.image(logo_img)

with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("الرادار المستقل للأخبار العاجلة وترندات الساعة الأكثر تداولاً وجدلاً على الساحة.")

st.divider()

# 2. بنك المصادر الشامل والكامل (24 مصدراً لجمع الترند من كل مكان)
ALL_SOURCES = [
    # المصادر العالمية
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "The Economist", "url": "https://www.economist.com/the-world-this-week/rss.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"},
    # مصادرك المحلية والخاصة كاملة
    {"name": "التلفزيون العربي", "url": "https://rss.app/feeds/kT7C8wffs4FlVogb.xml"},
    {"name": "عربي 21", "url": "https://rss.app/feeds/IELo97hFudhqzc3b.xml"},
    {"name": "منصة إيكاد", "url": "https://rss.app/feeds/dIksWt06BYI9wq9h.xml"},
    {"name": "شبكة رصد", "url": "https://rss.app/feeds/UY9b0tCrWqLlDUS2.xml"},
    {"name": "الشرق الأوسط", "url": "https://rss.app/feeds/WrrcuX75FOhb3MyZ.xml"},
    {"name": "مدى مصر", "url": "https://rss.app/feeds/aZtPJd9x1TdXhpbc.xml"},
    {"name": "شبكة مزيد", "url": "https://rss.app/feeds/EKNJ1yBhz9dYQesm.xml"},
    {"name": "عربي بوست", "url": "https://rss.app/feeds/LzcCUDjvwsYkxeJb.xml"},
    {"name": "المصري اليوم", "url": "https://rss.app/feeds/0qilsswhtljm7TpX.xml"},
    {"name": "حقوق الإنسان", "url": "https://rss.app/feeds/KQOHigY4eHs2OXV0.xml"},
    {"name": "العشرين أونلاين", "url": "https://rss.app/feeds/UitAtgEww18TWQag.xml"},
    {"name": "العربية مصر", "url": "https://rss.app/feeds/hoc4wHdnB7ZkJIun.xml"},
    {"name": "صدى مصر", "url": "https://rss.app/feeds/QmEgZe5stNIFBrub.xml"},
    {"name": "تكنوقراط", "url": "https://rss.app/feeds/ITEpCccZdY1r0M4P.xml"},
    {"name": "المصري اليوم (إكس)", "url": "https://rss.app/feeds/idlogJBSLTtWCMLm.xml"},
    {"name": "تليجراف مصر", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "مزيد ستوريز", "url": "https://rss.app/feeds/n5ZkHXC4f0Zx7tzt.xml"},
    {"name": "القاهرة 24", "url": "https://rss.app/feeds/fSxYHaCDdTtQnPcc.xml"},
    {"name": "حدث بالفعل", "url": "https://rss.app/feeds/sUfKUXNv3LLJjC8X.xml"},
    {"name": "الشرق الأوسط (منشنز)", "url": "https://rss.app/feeds/GsU4dAB2KkXc8ctB.xml"}
]

# 3. كلمات التوقف المتطورة لفلترة الشوائب والتركيز على الترند الجدلي الصافي
STOP_WORDS = set([
    "على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "الذين", "عبر", "خلال", "بسبب", "حول",
    "وقد", "أنه", "كما", "ذلك", "وهي", "وهو", "بين", "عندما", "فقط", "وهناك", "عليها", "فيها",
    "منها", "إليها", "وإن", "وأن", "فإن", "بأن", "اليوم", "أمس", "غدا", "صور", "فيديو", "عاجل",
    "تفاصيل", "أكثر", "أقل", "أول", "آخر", "أهم", "بعض", "شاهد", "كيف", "لماذا", "متى", "أين"
])

# 4. دالة استخراج الروابط والصور من الـ RSS
def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
        return entry.enclosures[0]['href']
    if hasattr(entry, 'summary'):
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if match: return match.group(1)
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=500&q=80"

# 5. جلب البيانات من الـ 24 مصدراً دفعة واحدة
@st.cache_data(ttl=600) # التحديث كل 10 دقائق لمواكبة قضايا الساعة والفضائح الساخنة
def fetch_trending_data():
    all_news = []
    for source in ALL_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:6]: # نأخذ أحدث 6 أخبار من كل مصدر
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": source['name'],
                    "image": extract_image_url(entry)
                })
        except: continue
    return all_news

# 6. خوارزمية ذكية لصيد الكلمات المفتاحية الأكثر تكراراً (ترند الساعة)
def extract_dominating_trends(news_list, top_n=8):
    words = []
    for item in news_list:
        clean_text = re.sub(r'[^\w\s]', '', item['title'])
        for word in clean_text.split():
            # قضايا الرأي العام والأسماء المشتعلة تتكون غالباً من 4 أحرف فأكثر
            if len(word) > 3 and word not in STOP_WORDS: 
                words.append(word)
                
    freq = Counter(words)
    return [word for word, count in freq.most_common(top_n) if count > 1]

# --- تشغيل الواجهة والتفاعل ---
with st.spinner('⏳ جاري مسح الـ 24 مصدراً بالكامل واصطياد ترند الساعة...'):
    news_data = fetch_trending_data()

# --- إعدادات القائمة الجانبية (Sidebar) مع اللوجو المصغر الاحترافي ---
st.sidebar.markdown("<br>", unsafe_allow_html=True)
sidebar_logo = get_resized_logo(width_size=80) # حجم صغير وأنيق جداً للسحاب الجانبي
if sidebar_logo:
    # وضع اللوجو في منتصف الشريط الجانبي
    side_col1, side_col2, side_col3 = st.sidebar.columns([1, 2, 1])
    with side_col2:
        st.image(sidebar_logo)

st.sidebar.markdown("<h3 style='text-align: center; margin-top: -5px;'>SherifOsmanClub</h3>", unsafe_allow_html=True)
st.sidebar.divider()

if news_data:
    dominating_trends = extract_dominating_trends(news_data)
    
    if dominating_trends:
        st.sidebar.header("🚨 ترند الساعة")
        selected_trend = st.sidebar.radio("اختر القضية المشتعلة الآن:", dominating_trends)
        
        st.subheader(f"📸 تغطية حية لترند الساعة: 【 {selected_trend} 】")
        
        # تصفية الأخبار التي تحتوي على كلمة الترند المختار
        related_items = [item for item in news_data if selected_trend in item['title']][:6]
        
        # عرض الكروت البصرية على شكل Grid (3 أعمدة)
        cols = st.columns(3)
        for index, item in enumerate(related_items):
            with cols[index % 3]:
                st.image(item['image'], use_container_width=True)
                st.markdown(f"**{item['source']}**")
                st.markdown(f"[{item['title']}]({item['link']})")
                st.write("---")
    else:
        st.info("الرادار يحلل البيانات الآن، لم يتم رصد كلمة مكررة بكثافة في هذه اللحظة.")
else:
    st.error("⚠️ لم نتمكن من جلب البيانات، يرجى تحديث الصفحة.")
