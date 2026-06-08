import streamlit as st
import feedparser
import re
from collections import Counter

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="رادار الأخبار المباشر | News Radar", page_icon="📡", layout="wide")

st.title("📡 غرفة الأخبار المباشرة ورادار الكلمات المفتاحية")
st.markdown("نظام ذكي يقوم بمسح 24 مصدراً، استخراج الكلمات المشتعلة برمجياً (بدون قيود)، وتوجيهك للمصادر مباشرة.")
st.divider()

# 2. بنك المصادر الشامل
ALL_SOURCES = [
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "The Economist", "url": "https://www.economist.com/the-world-this-week/rss.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"},
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

# 3. كلمات التوقف لفلترة الترند (الكلمات التي لا نعتبرها ترند)
STOP_WORDS = set([
    "على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "الذين", "عبر", "خلال", "بسبب", "حول",
    "وقد", "أنه", "كما", "ذلك", "وهي", "وهو", "بين", "عندما", "فقط", "وهناك", "عليها", "فيها",
    "منها", "إليها", "وإن", "وأن", "فإن", "بأن", "اليوم", "أمس", "غدا", "صور", "فيديو", "عاجل",
    "تفاصيل", "أكثر", "أقل", "أول", "آخر", "أهم", "بعض", "شاهد", "كيف", "لماذا", "متى", "أين"
])

# 4. دالة جلب الأخبار وحفظها كقاعدة بيانات مؤقتة
@st.cache_data(ttl=1800)
def fetch_news():
    all_news = []
    for source in ALL_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:5]: # نأخذ أحدث 5 أخبار من كل مكان
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": source['name']
                })
        except:
            continue
    return all_news

# 5. خوارزمية استخراج الكلمات المفتاحية
def extract_top_keywords(news_list, top_n=15):
    words = []
    for item in news_list:
        # مسح التشكيل والرموز للحصول على الكلمة الصافية
        clean_text = re.sub(r'[^\w\s]', '', item['title'])
        for word in clean_text.split():
            # نأخذ الكلمات الطويلة ونتجاهل حروف الجر
            if len(word) > 3 and word not in STOP_WORDS:
                words.append(word)
                
    freq = Counter(words)
    return [word for word, count in freq.most_common(top_n)]

# --- واجهة المستخدم والتفاعل ---
with st.spinner('⏳ جاري مسح 24 جريدة وموقع إخباري لاستخراج الترندات...'):
    news_data = fetch_news()

if news_data:
    top_keywords = extract_top_keywords(news_data)
    
    # القائمة الجانبية (الأزرار السريعة)
    st.sidebar.header("🔥 الكلمات المشتعلة الآن")
    selected_keyword = st.sidebar.radio("اختر الترند لترى أخباره الأصلية:", top_keywords)
    
    # الشاشة الرئيسية
    st.subheader(f"📰 الأخبار العاجلة المتعلقة بـ: 【 {selected_keyword} 】")
    
    # البحث الفوري عن الكلمة في العناوين
    related_news = [item for item in news_data if selected_keyword in item['title']]
    
    st.write(f"تم العثور على **{len(related_news)}** خبر/تغريدة تتحدث عن هذا الموضوع في مصادرك:")
    st.write("") # مسافة فارغة
    
    # عرض الأخبار بشكل روابط أنيقة
    for news in related_news:
        st.markdown(f"🔹 **[{news['title']}]({news['link']})** *(المصدر: {news['source']})*")
        
    st.divider()
    st.info("💡 اضغط على أي عنوان إخباري باللون الأزرق للانتقال مباشرة إلى الموقع الأصلي وقراءة التفاصيل.")
        
else:
    st.error("⚠️ لم نتمكن من جلب الأخبار. يرجى التحقق من اتصال الإنترنت أو تحديث الصفحة.")
