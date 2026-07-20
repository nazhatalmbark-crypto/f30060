import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import ast
from datetime import date
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- الإعدادات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT)')
conn.commit()

# --- دالة حماية النص للـ PDF ---
def safe_pdf_text(text):
    # تحويل النص ليتناسب مع ترميز الـ PDF بدون انهيار
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# --- تسجيل الدخول (تبسيط للتركيز على الفاتورة) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    if st.button("دخول للنظام"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- الواجهة ---
st.title("Eng. Yasser Pro System ✨")
tabs = st.tabs(["🛒 البيع", "📦 المخزن", "🧾 الفواتير"])

with tabs[0]: # البيع
    st.header("🛒 تسجيل مبيعات")
    name = st.text_input("اسم العميل")
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    cart = {}
    for idx, row in prods.iterrows():
        qty = st.number_input(f"{row['name']} (السعر: {row['price_carton']})", min_value=0, key=f"q_{idx}")
        if qty > 0: cart[row['name']] = {'price': row['price_carton'], 'qty': qty}
    
    if st.button("إتمام البيع"):
        total = sum(d['price'] * d['qty'] for d in cart.values())
        c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (name, str(cart), int(total), str(date.today())))
        conn.commit(); st.success("تم الحفظ!"); st.rerun()

with tabs[1]: # المخزن
    st.header("📦 إضافة مواد")
    with st.form("add_p", clear_on_submit=True):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر"); q = st.number_input("الكمية")
        if st.form_submit_button("حفظ"): c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM products", conn))

with tabs[2]: # الفواتير
    st.header("🧾 الفواتير")
    invs = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invs.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']}"):
            items = ast.literal_eval(row['items'])
            st.table(pd.DataFrame(items).T)
            
            # زر تحميل الـ PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="INVOICE", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Customer: {safe_pdf_text(row['customer_name'])}", ln=True)
            pdf.ln(5)
            
            # جدول الفاتورة
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(80, 10, "Item", border=1, fill=True)
            pdf.cell(30, 10, "Qty", border=1, fill=True)
            pdf.cell(40, 10, "Price", border=1, fill=True)
            pdf.cell(40, 10, "Total", border=1, fill=True, ln=True)
            
            for item, data in items.items():
                pdf.cell(80, 10, safe_pdf_text(item), border=1)
                pdf.cell(30, 10, str(data['qty']), border=1)
                pdf.cell(40, 10, str(data['price']), border=1)
                pdf.cell(40, 10, str(data['qty'] * data['price']), border=1, ln=True)
            
            pdf.cell(190, 10, txt=f"GRAND TOTAL: {row['total']}", border=1, align='R')
            
            st.download_button("📥 تحميل الفاتورة PDF", pdf.output(dest='S').encode('latin-1'), file_name=f"inv_{row['rowid']}.pdf")
