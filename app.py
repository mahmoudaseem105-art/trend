import streamlit as st
import feedparser
import re
from collections import Counter

# 1. إعدادات الصفحة والهوية الرسمية للمنصة
st.set_page_config(page_title="SherifOsmanClub الإخبارية", page_icon="🔥", layout="wide")

# اسم ملف اللوجو الشفاف الجديد
LOGO_IMAGE = "logo.png" 

# --- تنسيق احترافي: اللوجو صغير في الأعلى بجوار العنوان ---
col_text, col_logo = st.columns([5, 1])

with col_logo:
    try:
        # عرض اللوجو الشفاف بحجم احترافي
        st.image(LOGO_IMAGE, width=120)
    except:
        pass 

with col_text:
    st.title("🔥 SherifOsmanClub الإخبارية")
    st.markdown("الرادار المستقل للأخبار العاجلة والترندات الأكثر تداولاً وجدلاً على الساحة.")

st.divider()

# 2. مصادر "النبض الإخباري والسوشيال ميديا"
ALL_SOURCES = [
    {"name": "المصري اليوم", "url": "https://rss.app/feeds/0qilsswhtljm7TpX.xml"},
    {"name": "القاهرة 24", "url": "https://rss.app/feeds/fSxYHaCDdTtQnPcc.xml"},
    {"name": "اليوم السابع", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "صدى البلد", "url": "https://rss.app/feeds/QmEgZe5stNIFBrub.xml"},
    {"name": "العربية مصر", "url": "https://rss.app/feeds/hoc4wHdnB7ZkJIun.xml"},
    {"name": "حدث بالفعل", "url": "https://rss.app/feeds/sUfKUXNv3LLJjC8X.xml"},
    {"name": "تليجراف مصر", "url": "https://rss.app/feeds/yS4uMduCaejNZYj8.xml"},
    {"name": "الشرق الأوسط", "url": "https://rss.app/feeds/WrrcuX75FOhb3MyZ.xml"},
    {"name": "The Guardian", "
