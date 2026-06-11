import streamlit as st
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
    st.markdown("الرادار المستقل للأخبار العاجلة والنبض الحقيقي للسوشيال ميديا (قراءة مباشرة).")
st.divider()

# 2. مصادرك الخاصة (مربوطة بمعرفات قنوات التليجرام الرسمية)
ALL_SOURCES = [
    {"name": "شبكة رصد", "handle": "rassd_egypt"},
    {"name": "القاهرة 24", "handle": "cairo24_news"},
    {"name": "اليوم السابع", "handle": "Youm7"},
    {"name": "المصري اليوم", "handle": "almasryalyoum"},
    {"name": "إيكاد Eekad", "handle": "EekadFacts"},
    {"name": "عربي 21", "handle": "Arabi21News"},
    {"name": "مدى مصر", "handle": "MadaMasr"},
    {"name": "عربي بوست", "handle": "Arabic_Post"},
    {"name": "مزيد", "handle": "Mazeeed"},
    {"name": "تليجراف مصر", "handle": "telegraph_egypt"},
    {"name": "صدى البلد", "handle": "ElBaladOfficial"},
    {"name": "الجزيرة مصر", "handle": "AJA_Egypt"},
    {"name": "الجزيرة عاجل", "handle": "AJA_News"},
    {"name": "الشرق الأوسط", "handle": "aawsat_news"},
    {"name": "حقوق الإنسان", "handle": "AmnestyAR"},
    {"name": "العربية عاجل", "handle": "Alarabiya_Brk"},
    {"name": "سكاي نيوز", "handle": "SkyNewsArabia_B"},
    {"name": "بي بي سي عربي", "handle": "bbcarabic"},
    {"name": "روسيا اليوم", "handle": "RTarabic_News"},
    {"name": "العربي الجديد", "handle": "alaraby_ar"},
    {"name": "قناة الشرق", "handle": "ElsharqTV"},
    {"name": "مكملين", "handle": "mekameeleen"},
    {"name": "تغطية غزة", "handle": "GazaNewsNow"},
    {"name": "الحدث", "handle": "alhadath"}
]

# --- 3. محرك اختراق تليجرام المباشر (بديل الـ RSS) ---
# هذا الكود يقرأ من تليجرام مباشرة كأنه إنسان ويتجاهل كل الوسطاء
def fetch_telegram_direct(handle, source_name):
    url = f"https://t.me/s/{handle}" # واجهة تليجرام العامة للويب
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }
    items = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200: return []
        
        # تقسيم كود الصفحة إلى بلوكات (كل بوست في بلوك)
        blocks = res.text.split('tgme_widget_message_wrap js-widget_message_wrap')[1:]
        
        # قراءة البوستات من الأحدث للأقدم
        for block in reversed(blocks):
            # 1. استخراج النص
            text_match = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', block, re.DOTALL)
            if not text_match: continue
            
            raw_text = text_match.group(1)
            clean_text = re.sub(r'<br/?>', ' | ', raw_text) # تحويل النزول لسطر إلى فاصل
            clean_text = re.sub(r'<[^>]+>', '', clean_text).strip() # إزالة أكواد HTML
            if len(clean_text) < 15: continue # تجاهل البوستات القصيرة جداً
            
            # 2. استخراج الصورة إن وجدت
            img_match = re.search(r"background-image:url\('([^']+)'\)", block)
            image_url = img_match.group(1) if img_match else "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=500&q=80"
            
            # 3. استخراج رابط البوست الأصلي
            link_match = re.search(r'href="(https://t.me/[^"]+/\d+)"', block)
            post_link = link_match.group(1) if link_match else url
            
            items.append({
                "title": clean_text[:130] + "..." if len(clean_text) > 130 else clean_text,
                "link": post_link,
                "source": source_name,
                "image": image_url
            })
            
            if len(items) >= 20: break # جلب أحدث 20 بوست من كل قناة
        return items
    except:
        return []

@st.cache_data(ttl=300) # التحديث كل 5 دقائق
def fetch_trending_data():
    all_news = []
    source_news_dict = {src['name']: [] for src in ALL_SOURCES}
    
    for source in ALL_SOURCES:
        # استخدام المحرك المباشر بدلاً من RSSHub
        channel_items = fetch_telegram_direct(source['handle'], source['name'])
        if channel_items:
            all_news.extend(channel_items)
            source_news_dict[source['name']] = channel_items
            
    return all_news, source_news_dict

# --- 4. Groq الذكي (الترندات المفلترة بصرامة) ---
@st.cache_data(ttl=900) 
def get_trends_from_groq(news_list):
    try:
        sample_titles = list(set([item['title'] for item in news_list]))[:60]
        prompt = f"""
        اقرأ هذه المنشورات الإخبارية من السوشيال ميديا:
        {" | ".join(sample_titles)}
        
        استخرج أهم 6 ترندات حالية. 
        شروط عسكرية صارمة جداً:
        1. كل ترند يجب أن يكون (كلمة واحدة فقط)، إما اسم شخص، دولة، أو حدث.
        2. ممنوع منعاً باتاً استخدام أي أفعال أو جمل.
        3. النتائج مفصولة بفاصلة عربية (،) فقط، بدون أي شرح أو ترقيم.
        مثال للرد الصحيح: الأهلي، غزة، الدولار، ترامب، بايدن، الزمالك
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
    STOP_WORDS = set(["على", "إلى", "عن", "هذا", "هذه", "التي", "الذي", "بسبب", "حول", "وقد", "أنه", "كما", "ذلك", "فقط", "اليوم", "صور", "فيديو", "عاجل", "تفاصيل", "أكثر"])
    words = []
    for item in news_list:
        for word in re.findall(r'[\u0600-\u06FF]+', item['title']):
            if len(word) > 3 and word not in STOP_WORDS: words.append(word)
    return [word for word, count in Counter(words).most_common(6) if count > 1]

# --- 5. تشغيل واجهة المستخدم ---
with st.spinner('⏳ جاري سحب البيانات مباشرة من سيرفرات تليجرام (بدون وسطاء)...'):
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
    if st.session_state.view_mode == 'source': st.write(f"إجمالي المنشورات المتاحة: **{len(related_items)} بوست**")
    cols = st.columns(3)
    for i, item in enumerate(related_items):
        with cols[i % 3]:
            st.image(item['image'], use_container_width=True)
            st.markdown(f"**{item['source']}**\n\n[{item['title']}]({item['link']})\n---")
else:
    st.info("لم يتم العثور على بوستات. تأكد من أن القناة نشطة على تليجرام.")
