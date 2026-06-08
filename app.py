import streamlit as st
import feedparser
import requests

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="رادار الترند الذكي | Trend Radar", page_icon="🧠", layout="wide")

st.title("🧠 غرفة الأخبار الآلية (تحليل الترند بالذكاء الاصطناعي)")
st.markdown("نظام مستقل لا يعتمد على جوجل. يقوم بمسح 24 مصدراً واستنتاج الترندات المشتعلة حالياً.")
st.divider()

GROQ_API_KEY = "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"

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

# 3. القائمة الجانبية للتوجيه الجغرافي
st.sidebar.header("🌍 نطاق الرادار")
country_list = ["مصر 🇪🇬", "العالم العربي 🌍", "عالمياً 🌐"]
selected_scope = st.sidebar.radio("ركز استنتاج الترند على:", country_list)

# 4. دالة جلب العناوين من كل المصادر (مخففة لتناسب الذكاء الاصطناعي)
@st.cache_data(ttl=1800)
def fetch_all_headlines():
    headlines = []
    # سحب أهم 3 أخبار فقط من كل مصدر لتجنب الضغط على السيرفر
    for source in ALL_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:3]:
                headlines.append(f"- {entry.title} (المصدر: {source['name']})")
        except:
            continue
    return headlines

# 5. دالة الذكاء الاصطناعي لاستنتاج الترند (مع كاشف أخطاء دقيق)
def extract_trends_with_groq(headlines_list, scope):
    text_block = "\n".join(headlines_list)
    
    prompt = f"""
    أنت محلل ترندات وصحفي خبير.
    قمت بجمع هذه العناوين الإخبارية والمنشورات من 24 مصدراً مختلفاً في هذه اللحظة:
    
    {text_block}
    
    المهمة:
    بناءً على التكرار والمواضيع المشتركة في هذه العناوين، استنتج أهم 6 "ترندات" مشتعلة الآن، مع التركيز على نطاق: {scope}.
    
    أخرج النتيجة باللغة العربية بتنسيق منظم كالتالي لكل ترند:
    ## 🎯 [اسم الترند أو الحدث]
    * **القصة باختصار:** [سطرين يشرحان ما الذي يحدث ولماذا هو ترند]
    * **المصادر التي تتحدث عنه:** [اذكر أمثلة للمصادر التي تناولته من العناوين المرفقة]
    ---
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        # إضافة مهلة 30 ثانية للاتصال حتى لا يفصل الموقع
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # إذا كان الرد ناجحاً
        if res.status_code == 200:
            data = res.json()
            return data['choices'][0]['message']['content'].strip()
        # إذا رفض السيرفر الطلب (نطبع السبب لنعرفه)
        else:
            error_details = res.json().get('error', {}).get('message', res.text)
            return f"⚠️ رفض خادم Groq الطلب. السبب الحقيقي: {error_details}"
            
    except Exception as e:
        return f"⚠️ حدث خطأ في الاتصال بالإنترنت أو الخادم: {str(e)}"

# --- واجهة المستخدم ---
st.subheader(f"📡 رادار الذكاء الاصطناعي: {selected_scope}")

if st.button("🚀 تشغيل الرادار ومسح المصادر الآن", type="primary", use_container_width=True):
    with st.spinner('⏳ جاري جمع أحدث الأخبار من المصادر...'):
        all_news = fetch_all_headlines()
        
    if all_news:
        st.success(f"✅ تم جمع {len(all_news)} خبراً وتغريدة بنجاح لتغذية الرادار! جاري تحليلها الآن...")
        
        with st.spinner('🧠 المحلل الآلي يقرأ الأخبار ويستنتج الترندات... (قد يستغرق 10 ثوانٍ)'):
            trends_report = extract_trends_with_groq(all_news, selected_scope)
            
        st.divider()
        if "⚠️" in trends_report:
            st.error(trends_report)
        else:
            st.markdown(trends_report)
    else:
        st.error("⚠️ لم نتمكن من جلب الأخبار. يرجى التحقق من المصادر.")
