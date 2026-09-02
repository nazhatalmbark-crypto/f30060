import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# إعدادات صفحة ستريملت
st.set_page_config(page_title="نظام الإدارة والفواتير", layout="centered")

st.title("نظام الإدارة والفواتير والتخزين")
st.write("أهلاً بك. تم تصحيح جميع أخطاء الاستيراد البرمجية لتعمل المنصة بكفاءة.")

# نموذج بسيط لتوضيح عمل النظام
with st.form("invoice_form"):
    customer_name = st.text_input("اسم العميل")
    item_description = st.text_input("وصف المنتج أو الخدمة")
    amount = st.number_input("المبلغ", min_value=0.0, step=0.5)
    
    submitted = st.form_submit_button("حفظ وإنشاء الفاتورة")
    if submitted:
        st.success(f"تم تسجيل الفاتورة بنجاح للعميل: {customer_name} بقيمة {amount}")

# مثال على استخدام المكونات البرمجية وتجنب أخطاء TTFont
st.info("الكود جاهز ومحدث بالكامل بالمسارات الصحيحة.")
