import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import ast
from datetime import date
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- قاعدة البيانات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')

# تحديث الجدول إذا كان ناقصاً
try:
    c.execute("ALTER TABLE invoices ADD COLUMN payment_type TEXT")
    conn.commit()
except:
    pass

# --- دالة حماية النصوص ---
def safe_pdf_text(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def hash_pw(pw): 
    return hashlib.sha256(pw.encode()).hexdigest()

c.execute("SELECT COUNT(*) FROM users")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users VALUES (?, ?)", ("admin", hash_pw("1234")))
    conn.commit()

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_guest' not in st.session_state: st.session_state.is_guest = False

if not st.session_state.logged_in:
    st.title("🔐 Eng. Yasser Pro System - تسجيل الدخول")
    tab1, tab2 = st.tabs(["🔑 تسجيل دخول المسؤول", "👤 دخول الضيف"])
    with tab1:
        user = st.text_input("اسم المستخدم", key="u1")
        pw = st.text_input("كلمة المرور", type="password", key="p1")
        if st.button("دخول كمسؤول"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, hash_pw(pw)))
            if c.fetchone(): 
                st.session_state.logged_in = True
                st.session_state.is_guest = False
                st.rerun()
            else: st.error("خطأ!")
    with tab2:
        if st.button("🚀 الدخول السريع كضيف"):
            st.session_state.logged_in = True
            st.session_state.is_guest = True
            st.rerun()
    st.stop()

# --- الواجهة ---
st.title("Eng. Yasser Pro System ✨")
if st.button("تسجيل الخروج"): 
    st.session_state.logged_in = False
    st.session_state.is_guest = False
    st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 المخزن", "🧾 الفواتير", "👥 العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # البيع
    st.header("🛒 نقطة البيع")
    custs = pd.read_sql("SELECT name FROM customers", conn)
    if custs.empty: st.warning("أضف عملاء أولاً!")
    else:
        selected_c = st.selectbox("اختر العميل", ["اختر..."] + custs['name'].tolist())
        prods = pd.read_sql("SELECT rowid, * FROM products", conn)
        cart = {}
        for idx, row in prods.iterrows():
            qty = st.number_input(f"{row['name']} (متوفر: {row['quantity']})", min_value=0, step=1, key=f"q_{idx}")
            if qty > 0: cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
        if cart and st.button("✅ إتمام البيع"):
            total = sum(d['price'] * d['qty'] for d in cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_c, str(cart), int(total), str(date.today()), "نقد"))
            for n, d in cart.items(): c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
            conn.commit(); st.success("تم الحفظ!"); st.rerun()

with tabs[1]: # المخزن
    st.header("📦 عرض المخزن")
    st.dataframe(pd.read_sql("SELECT * FROM products", conn), use_container_width=True)

with tabs[2]: # الفواتير
    st.header("🧾 سجل الفواتير")
    for _, row in pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn).iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']}"):
            items = ast.literal_eval(row['items'])
            st.table(pd.DataFrame(items).T)
            
            # PDF (تم إصلاح الطريقة هنا)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, "INVOICE", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, f"Customer: {safe_pdf_text(row['customer_name'])}", ln=True)
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
            pdf.cell(190, 10, f"TOTAL: {row['total']} IQD", 1, 1, 'R')
            
            # طريقة تحميل حديثة تمنع الـ AttributeError
            st.download_button("📥 تحميل PDF", data=pdf.output(), file_name=f"inv_{row['rowid']}.pdf")

with tabs[3]: # العملاء
    st.header("👥 العملاء")
    with st.form("add_c", clear_on_submit=True):
        n = st.text_input("اسم العميل"); p = st.text_input("هاتف")
        if st.form_submit_button("إضافة"): c.execute("INSERT INTO customers VALUES (?,?)", (n, p)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tabs[4]: # المساعد
    st.header("🤖 المساعد الذكي - جرد المخزن")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("➕ إضافة مادة")
        with st.form("add_p", clear_on_submit=True):
            n = st.text_input("اسم المادة"); p = st.number_input("السعر"); q = st.number_input("الكمية")
            if st.form_submit_button("حفظ"): c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()
    with c2:
        st.subheader("📊 جرد المخزن")
        st.table(pd.read_sql("SELECT * FROM products", conn))
        if st.button("فحص النواقص"):
            st.table(pd.read_sql("SELECT * FROM products WHERE quantity < 5", conn))
