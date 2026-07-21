import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import ast
import os
from datetime import date
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# إعدادات الصفحة
st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- دالة تحويل وتعديل النص العربي للـ PDF ---
def render_arabic(text):
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    except:
        return str(text)

# --- إعداد قاعدة البيانات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')

# --- دالة توليد الفاتورة باللغة العربية الآمنة ---
def generate_pdf(row, items):
    pdf = FPDF()
    pdf.add_page()
    
    # التحقق من وجود الخط العربي
    font_path = 'DejaVuSans.ttf'
    if not os.path.exists(font_path):
        raise Exception(f"ملف الخط {font_path} غير موجود في المجلد! تأكد من رفعه إلى GitHub.")
    
    # إضافة الخط العربي بنجاح
    pdf.add_font("ArabicFont", "", font_path, uni=True)
    pdf.set_font("ArabicFont", size=16)
    
    # العنوان الرئيسي
    pdf.cell(200, 10, render_arabic("فاتورة مبيعات رسمية"), ln=True, align='C')
    pdf.ln(10)
    
    # بيانات العميل والتاريخ
    pdf.set_font("ArabicFont", size=12)
    pdf.cell(200, 10, render_arabic(f"اسم العميل: {row['customer_name']}"), ln=True)
    pdf.cell(200, 10, render_arabic(f"تاريخ الفاتورة: {row['date']}"), ln=True)
    pdf.ln(10)
    
    # رأس جدول المنتجات
    pdf.cell(80, 10, render_arabic("المادة"), 1, 0, 'C')
    pdf.cell(30, 10, render_arabic("الكمية"), 1, 0, 'C')
    pdf.cell(40, 10, render_arabic("السعر"), 1, 0, 'C')
    pdf.cell(40, 10, render_arabic("الإجمالي"), 1, 1, 'C')
    
    # محتوى الجدول
    for item, data in items.items():
        pdf.cell(80, 10, render_arabic(str(item)), 1)
        pdf.cell(30, 10, str(data['qty']), 1, 0, 'C')
        pdf.cell(40, 10, str(data['price']), 1, 0, 'C')
        pdf.cell(40, 10, str(data['qty'] * data['price']), 1, 1, 'C')
        
    # المجموع الكلي
    pdf.ln(10)
    pdf.set_font("ArabicFont", size=14)
    pdf.cell(200, 10, render_arabic(f"المجموع الكلي: {row['total']} دينار"), ln=True, align='R')
        
    return pdf.output(dest='S')

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول للنظام")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("دخول كمسؤول"): 
            st.session_state.logged_in = True
            st.rerun()
    with col2:
        if st.button("🚀 دخول الضيف"): 
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- أقسام النظام الأساسية (Tabs) ---
tabs = st.tabs(["🛒 البيع والطلبات", "🧾 الفواتير والتحميل", "📦 إدارة المخزن", "👥 إدارة العملاء"])

with tabs[0]: # البيع
    st.header("إدارة المبيعات والطلب الجديد")
    custs = pd.read_sql("SELECT name FROM customers", conn)
    cust_list = ["اختر العميل..."] + custs['name'].tolist() if not custs.empty else ["اختر العميل..."]
    sel = st.selectbox("اختر العميل", cust_list)
    
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    cart = {}
    if not prods.empty:
        for idx, row in prods.iterrows():
            q = st.number_input(f"{row['name']} (السعر: {row['price_carton']})", min_value=0, key=f"q_{idx}")
            if q > 0: 
                cart[row['name']] = {'price': row['price_carton'], 'qty': q}
                
    if cart and sel != "اختر العميل..." and st.button("إتمام البيع وحفظ الفاتورة"):
        total_amt = sum(d['price'] * d['qty'] for d in cart.values())
        c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (sel, str(cart), total_amt, str(date.today()), "نقد"))
        conn.commit()
        st.success("تم حفظ الفاتورة بنجاح!")
        st.rerun()

with tabs[1]: # الفواتير
    st.header("سجل الفواتير وطباعتها")
    inv_df = pd.read_sql("SELECT rowid, * FROM invoices", conn)
    if inv_df.empty:
        st.info("لا توجد فواتير مسجلة حتى الآن.")
    else:
        for _, row in inv_df.iterrows():
            with st.expander(f"فاتورة رقم #{row['rowid']} - العميل: {row['customer_name']} - المجموع: {row['total']}"):
                items = ast.literal_eval(row['items'])
                st.table(pd.DataFrame(items).T)
                
                # زر التحميل الآمن مع معالجة الأخطاء
                try:
                    pdf_data = generate_pdf(row, items)
                    st.download_button(
                        label="📥 تحميل الفاتورة PDF (عربي)", 
                        data=pdf_data, 
                        file_name=f"invoice_{row['rowid']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{row['rowid']}"
                    )
                except Exception as e:
                    st.error(f"خطأ في توليد الملف: {e}")

with tabs[2]: # المخزن
    st.header("إدارة المخزن والمواد")
    p_name = st.text_input("اسم المادة الجديدة")
    p_price = st.number_input("سعر الكارتون", min_value=0)
    p_qty = st.number_input("الكمية المتوفرة", min_value=0)
    if st.button("إضافة مادة للمخزن"):
        if p_name:
            c.execute("INSERT INTO products VALUES (?,?,?)", (p_name, p_price, p_qty))
            conn.commit()
            st.success("تمت إضافة المادة بنجاح!")
            st.rerun()
            
    st.subheader("المواد الحالية في المخزن:")
    st.dataframe(pd.read_sql("SELECT rowid, * FROM products", conn))

with tabs[3]: # العملاء
    st.header("إدارة العملاء")
    c_name = st.text_input("اسم العميل الجديد")
    c_phone = st.text_input("رقم هاتف العميل")
    if st.button("إضافة عميل جديد"):
        if c_name:
            c.execute("INSERT INTO customers VALUES (?,?)", (c_name, c_phone))
            conn.commit()
            st.success("تم إضافة العميل بنجاح!")
            st.rerun()
            
    st.subheader("قائمة العملاء المسجلين:")
    st.dataframe(pd.read_sql("SELECT rowid, * FROM customers", conn))
