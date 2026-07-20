import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import os

# --- دالة تحويل النص العربي ---
def render_arabic(text):
    # ترتيب الحروف وتصحيح اتجاهها
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text

# --- دالة الـ PDF الجديدة ---
def create_safe_pdf(row, items):
    pdf = FPDF()
    pdf.add_page()
    
    # محاولة إضافة الخط العربي (تأكد أن الخط موجود في ملف المشروع)
    # إذا لم يوجد، سيستخدم الخط الافتراضي (لكن مع المكتبات الجديدة سيتعامل مع الرموز بشكل أفضل)
    font_path = 'DejaVuSans.ttf' 
    if os.path.exists(font_path):
        pdf.add_font("Arabic", "", font_path, uni=True)
        pdf.set_font("Arabic", size=12)
    else:
        # إذا لم تجد الخط، البرنامج لن ينهار، سيحاول كتابة العربية
        pdf.set_font("Arial", size=12)

    # كتابة الفاتورة
    pdf.cell(200, 10, render_arabic("فاتورة مبيعات"), ln=True, align='C')
    pdf.ln(10)
    
    pdf.cell(200, 10, render_arabic(f"اسم العميل: {row['customer_name']}"), ln=True)
    pdf.ln(5)
    
    # جدول المنتجات
    pdf.cell(80, 10, render_arabic("المادة"), 1)
    pdf.cell(30, 10, render_arabic("الكمية"), 1)
    pdf.cell(40, 10, render_arabic("السعر"), 1)
    pdf.cell(40, 10, render_arabic("الإجمالي"), 1, ln=True)
    
    for item, data in items.items():
        pdf.cell(80, 10, render_arabic(str(item)), 1)
        pdf.cell(30, 10, str(data['qty']), 1)
        pdf.cell(40, 10, str(data['price']), 1)
        pdf.cell(40, 10, str(data['qty'] * data['price']), 1, ln=True)
        
    return pdf.output(dest='S')
