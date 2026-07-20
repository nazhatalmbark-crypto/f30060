import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# دالة تحويل النص العربي
def to_arabic(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

# دالة توليد الـ PDF (بدون خطوط خارجية معقدة حالياً)
def generate_pdf(row, items):
    pdf = FPDF()
    pdf.add_page()
    
    # استخدام الخط الافتراضي (Unicode المدمج)
    # ملاحظة: في fpdf2 الخط الافتراضي يدعم اليونيكود بشكل جيد
    pdf.set_font("Helvetica", size=12)
    
    # العنوان
    pdf.cell(200, 10, to_arabic("فاتورة مبيعات"), ln=True, align='C')
    pdf.ln(10)
    
    # المعلومات
    pdf.cell(200, 10, to_arabic(f"اسم العميل: {row['customer_name']}"), ln=True)
    pdf.cell(200, 10, to_arabic(f"التاريخ: {row['date']}"), ln=True)
    pdf.ln(10)
    
    # الجدول
    pdf.cell(80, 10, to_arabic("المادة"), 1)
    pdf.cell(30, 10, to_arabic("الكمية"), 1)
    pdf.cell(40, 10, to_arabic("السعر"), 1)
    pdf.cell(40, 10, to_arabic("الإجمالي"), 1, ln=True)
    
    for item, data in items.items():
        pdf.cell(80, 10, to_arabic(str(item)), 1)
        pdf.cell(30, 10, to_arabic(str(data['qty'])), 1)
        pdf.cell(40, 10, to_arabic(str(data['price'])), 1)
        pdf.cell(40, 10, to_arabic(str(data['qty'] * data['price'])), 1, ln=True)
        
    return pdf.output() # إرجاع الملف مباشرة

# --- في منطقة عرض الفواتير في الـ UI ---
# استخدم هذه الطريقة لعرض زر التحميل:
# ... (داخل التكرار الخاص بالفواتير)
try:
    pdf_bytes = generate_pdf(row, items)
    st.download_button(
        label="📥 تحميل الفاتورة",
        data=pdf_bytes,
        file_name=f"invoice_{row['rowid']}.pdf"
    )
except Exception as e:
    st.error(f"حدث خطأ في تحميل الفاتورة: {e}")
