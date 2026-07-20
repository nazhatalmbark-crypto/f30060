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

# --- دوال مساعدة للعربي ---
def render_arabic(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

# --- قاعدة البيانات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')

# --- دالة الفاتورة (كاملة) ---
def generate_pdf(row, items):
    pdf = FPDF()
    pdf.add_page()
    
    # تحميل الخط
    font_path = 'DejaVuSans.ttf'
    if os.path.exists(font_path):
        pdf.add_font("Arabic", "", font_path, uni=True)
        pdf.set_font("Arabic", size=16)
    else:
        pdf.set_font("Arial", size=16)

    # طباعة الفاتورة
    pdf.cell(200, 10, render_arabic("فاتورة مبيعات"), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12) # نستخدم خط عادي لبقية البيانات
    pdf.cell(200, 10, render_arabic(f"اسم العميل: {row['customer_name']}"), ln=True)
    pdf.cell(200, 10, render_arabic(f"التاريخ: {row['date']}"), ln=True)
    pdf.ln(10)
    
    # الجدول
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

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول")
    if st.button("دخول كمسؤول"): st.session_state.logged_in = True; st.rerun()
    if st.button("🚀 دخول الضيف"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- النظام الأساسي ---
tabs = st.tabs(["🛒 البيع", "🧾 الفواتير", "📦 المخزن", "👥 العملاء"])

with tabs[0]: # البيع
    custs = pd.read_sql("SELECT name FROM customers", conn)
    sel = st.selectbox("اختر العميل", ["اختر..."] + custs['name'].tolist())
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    cart = {}
    for idx, row in prods.iterrows():
        q = st.number_input(f"{row['name']}", key=f"q_{idx}")
        if q > 0: cart[row['name']] = {'price': row['price_carton'], 'qty': q}
    if cart and sel != "اختر..." and st.button("إتمام البيع"):
        total = sum(d['price']*d['qty'] for d in cart.values())
        c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (sel, str(cart), total, str(date.today()), "نقد"))
        conn.commit(); st.rerun()

with tabs[1]: # الفواتير
    for _, row in pd.read_sql("SELECT rowid, * FROM invoices", conn).iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']}"):
            items = ast.literal_eval(row['items'])
            st.table(pd.DataFrame(items).T)
            # زر التحميل
            try:
                pdf_data = generate_pdf(row, items)
                st.download_button("📥 تحميل PDF", data=pdf_data, file_name=f"inv_{row['rowid']}.pdf")
            except Exception as e:
                st.error(f"خطأ في توليد الملف: {e}")

with tabs[2]: # المخزن
    st.subheader("إضافة مادة")
    n = st.text_input("اسم المادة")
    p = st.number_input("السعر")
    q = st.number_input("الكمية")
    if st.button("حفظ"):
        c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()
    st.dataframe(pd.read_sql("SELECT * FROM products", conn))

with tabs[3]: # العملاء
    st.subheader("إضافة عميل")
    cn = st.text_input("اسم العميل")
    cp = st.text_input("الهاتف")
    if st.button("إضافة"):
        c.execute("INSERT INTO customers VALUES (?,?)", (cn, cp)); conn.commit(); st.rerun()
    st.dataframe(pd.read_sql("SELECT * FROM customers", conn))
