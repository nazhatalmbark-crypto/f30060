import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import date
from fpdf import FPDF

# --- تنسيق البرنامج ---
st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# --- الإعدادات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- دالة التشفير ---
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.container()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Eng. Yasser Pro System</h1>", unsafe_allow_html=True)
        user = st.text_input("اسم المستخدم")
        pw = st.text_input("كلمة المرور", type="password")
        if st.button("دخول 🚀"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, hash_pw(pw)))
            if c.fetchone(): st.session_state.logged_in = True; st.rerun()
            else: st.error("خطأ في البيانات!")
        if st.button("دخول كضيف 👤"):
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- الواجهة بعد الدخول ---
st.markdown(f"### أهلاً بك يا مدير ✨")
if st.button("خروج 🚪"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 عرض المخزن", "🧾 الفواتير", "👥 إدارة العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # البيع (الشبكة رجعت)
    st.header("🛒 نقطة البيع")
    custs = pd.read_sql("SELECT name FROM customers", conn)
    selected_c = st.selectbox("اختر العميل", ["اختر..."] + custs['name'].tolist())
    
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    # عمل الشبكة (Grid)
    cols = st.columns(3)
    for idx, row in prods.iterrows():
        with cols[idx % 3]:
            st.markdown(f"**{row['name']}**")
            st.write(f"السعر: {row['price_carton']} IQD")
            qty = st.number_input(f"الكمية", min_value=0, step=1, format="%d", key=f"q_{idx}")
            if qty > 0:
                if 'cart' not in st.session_state: st.session_state.cart = {}
                st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
    
    st.divider()
    if 'cart' in st.session_state and st.session_state.cart:
        if st.button("✅ إتمام العملية"):
            total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_c, str(st.session_state.cart), int(total), str(date.today()), "نقد"))
            for n, d in st.session_state.cart.items(): c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
            conn.commit(); st.session_state.cart = {}; st.success("تم الحفظ بنجاح!"); st.rerun()

with tabs[1]: # عرض المخزن
    st.header("📦 إدارة المخزن")
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    for idx, row in prods.iterrows():
        cols = st.columns([3, 1, 1])
        cols[0].write(f"**{row['name']}** | السعر: {row['price_carton']} | الكمية: {row['quantity']}")
        if cols[1].button(f"❌ حذف", key=f"del_{row['rowid']}"):
            c.execute("DELETE FROM products WHERE rowid = ?", (row['rowid'],))
            conn.commit(); st.rerun()

with tabs[2]: # الفواتير
    st.header("🧾 سجل الفواتير")
    invs = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invs.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']} - {row['date']}"):
            st.markdown(f"**المجموع الكلي:** `{row['total']} IQD`")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="INVOICE - ENG. YASSER", ln=True, align='C')
            pdf.line(10, 25, 200, 25)
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Invoice ID: {row['rowid']}", ln=True)
            pdf.cell(200, 10, txt=f"Customer: {row['customer_name']}", ln=True)
            pdf.line(10, 45, 200, 45)
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt=f"TOTAL AMOUNT: {row['total']} IQD", ln=True)
            st.download_button("📥 تحميل الفاتورة", bytes(pdf.output()), f"inv_{row['rowid']}.pdf")

with tabs[3]: # العملاء
    st.header("👥 العملاء")
    with st.form("add_cust"):
        name = st.text_input("اسم العميل")
        if st.form_submit_button("إضافة"): c.execute("INSERT INTO customers (name) VALUES (?)", (name,)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT name FROM customers", conn))

with tabs[4]: # المساعد الذكي
    st.header("🤖 المساعد الذكي")
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر", step=1); q = st.number_input("الكمية", step=1)
        if st.form_submit_button("إضافة للمخزن"): c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()
