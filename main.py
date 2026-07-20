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

# إنشاء الجداول والتأكد من وجود الأعمدة
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- دالة حماية النصوص للـ PDF ---
def safe_pdf_text(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔐 Eng. Yasser Pro System")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "admin" and pw == "1234":
            st.session_state.logged_in = True; st.rerun()
        else: st.error("خطأ!")
    st.stop()

# --- الواجهة ---
st.title("Eng. Yasser Pro System ✨")
if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 عرض المخزن", "🧾 الفواتير", "👥 العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # البيع
    st.header("🛒 البيع والطلب")
    custs = pd.read_sql("SELECT name FROM customers", conn)
    selected_c = st.selectbox("اختر العميل", ["اختر..."] + custs['name'].tolist())
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    
    current_cart = {}
    for idx, row in prods.iterrows():
        qty = st.number_input(f"{row['name']} (المتوفر: {row['quantity']})", min_value=0, step=1, key=f"q_{idx}")
        if qty > 0: current_cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
    
    if current_cart and st.button("✅ إتمام البيع"):
        total = sum(d['price'] * d['qty'] for d in current_cart.values())
        c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_c, str(current_cart), int(total), str(date.today()), "نقد"))
        for n, d in current_cart.items(): c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
        conn.commit(); st.success("تم البيع!"); st.rerun()

with tabs[1]: # المخزن
    st.header("📦 عرض المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

with tabs[2]: # الفواتير
    st.header("🧾 سجل الفواتير")
    for _, row in pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn).iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']}"):
            items = ast.literal_eval(row['items'])
            st.table(pd.DataFrame(items).T)
            
            # PDF مرتب
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="INVOICE", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Customer: {safe_pdf_text(row['customer_name'])}", ln=True)
            pdf.ln(5)
            # الجدول
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(80, 10, "Item", 1, 0, 'C', True)
            pdf.cell(30, 10, "Qty", 1, 0, 'C', True)
            pdf.cell(40, 10, "Price", 1, 0, 'C', True)
            pdf.cell(40, 10, "Total", 1, 1, 'C', True)
            for item, data in items.items():
                pdf.cell(80, 10, safe_pdf_text(item), 1)
                pdf.cell(30, 10, str(data['qty']), 1)
                pdf.cell(40, 10, str(data['price']), 1)
                pdf.cell(40, 10, str(data['qty']*data['price']), 1, 1)
            pdf.cell(190, 10, txt=f"GRAND TOTAL: {row['total']} IQD", border=1, align='R')
            st.download_button("📥 تحميل PDF", pdf.output(dest='S').encode('latin-1'), f"inv_{row['rowid']}.pdf")

with tabs[3]: # العملاء
    st.header("👥 العملاء")
    with st.form("add_c", clear_on_submit=True):
        n = st.text_input("اسم العميل"); p = st.text_input("هاتف")
        if st.form_submit_button("إضافة"): c.execute("INSERT INTO customers VALUES (?,?)", (n, p)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tabs[4]: # المساعد الذكي (الجرد)
    st.header("🤖 المساعد الذكي - جرد المخزن")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ إضافة مادة")
        with st.form("add_p", clear_on_submit=True):
            n = st.text_input("اسم المادة"); p = st.number_input("السعر"); q = st.number_input("الكمية")
            if st.form_submit_button("حفظ"): c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()
    with col2:
        st.subheader("📊 جرد المخزن")
        st.table(pd.read_sql("SELECT * FROM products", conn))
        if st.button("فحص النواقص"):
            st.table(pd.read_sql("SELECT * FROM products WHERE quantity < 5", conn))
