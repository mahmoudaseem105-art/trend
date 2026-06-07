import streamlit as st
from pytrends.request import TrendReq
import pandas as pd

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="رادار الترند | Trend Radar", page_icon="📈", layout="wide")

st.title("📈 رادار الترندات اليومية")
st.markdown("لوحة تحكم حية لمراقبة الأخبار والمواضيع الأكثر تداولاً في الوقت الفعلي.")
st.divider()

# 2. دالة ذكية لجلب الترندات (تتحدث كل ساعة لتخفيف الضغط)
@st.cache_data(ttl=3600) 
def get_daily_trends(country='egypt'):
    pytrends = TrendReq(hl='ar', tz=120)
    try:
        df = pytrends.trending_searches(pn=country)
        df.columns = ['🔥 الموضوع الرائج']
        df.index += 1 # ليبدأ الترقيم من 1 بدلاً من 0
        return df
    except Exception as e:
        return None

# 3. عرض البيانات في الموقع
st.subheader("أكثر عمليات البحث المشتعلة الآن")

with st.spinner('جاري مسح شبكة الإنترنت وجلب الترند...'):
    trends_data = get_daily_trends('egypt')

if trends_data is not None:
    st.dataframe(trends_data, use_container_width=True)
else:
    st.error("⚠️ حدث ضغط على سيرفرات جوجل، يرجى المحاولة بعد قليل.")
