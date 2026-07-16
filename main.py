import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
import hashlib

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- دالة التشفير ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول (مع الأعمدة الجديدة)
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
conn.commit()

# --- CSS للتصميم ---
st.markdown("""
    <style>
    .invoice-card { background-color: #f8f9fa; border-radius: 15px; padding: 15px; margin-bottom: 15px; border-left: 5px solid #28a745; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .badge-price { padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- الدخول ---
if not st.session_state.logged_in:
    st.title("🔐 بوابة المبرمج ياسر")
    if st.radio("العملية:", ["دخول", "تسجيل"]) == "دخول":
        u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, make_hash(p)))
            if c.fetchone(): st.session_state.logged_in = True; st.session_state.username = u; st.rerun()
    else:
        new_u = st.text_input("اسم المستخدم الجديد"); new_p = st.text_input("كلمة المرور", type="password")
        if st.button("إنشاء حساب"):
            try: c.execute("INSERT INTO users VALUES (?,?)", (new_u, make_hash(new_p))); conn.commit(); st.success("تم!")
            except: st.error("موجود مسبقاً")
    st.stop()

# --- القوائم ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 البيع", "🧾 الفواتير", "👥 العملاء", "📦 المخزن"])

with tab1:
    st.header("🛒 شاشة البيع")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    selected_customer = st.selectbox("🔎 اختر العميل", ["اختر..."] + cust_df['name'].tolist())
    
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    cols = st.columns(3)
    for i, row in prods.iterrows():
        with cols[i % 3]:
            if st.button(f"➕ {row['name']} ({row['quantity']})"):
                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': 1}
    
    if st.session_state.cart:
        st.write("--- السلة ---")
        for item, d in st.session_state.cart.items():
            st.write(f"{item} | السعر: {d['price']}")
        if st.button("✅ إتمام البيع"):
            total = sum(d['price'] for d in st.session_state.cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), "نقد"))
            conn.commit(); st.session_state.cart = {}; st.rerun()

with tab2:
    st.header("🧾 سجل الفواتير")
    for _, row in pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn).iterrows():
        st.markdown(f'<div class="invoice-card"><b>فاتورة #{row["rowid"]} | العميل: {row["customer_name"]}</b><br>المجموع: {row["total"]} د.ع</div>', unsafe_allow_html=True)
        with st.expander("👁️ عرض تفاصيل الفاتورة"):
            items = ast.literal_eval(row['items'])
            for n, d in items.items(): st.write(f"🔹 {n} : {d['price']} د.ع")
            if st.button(f"🗑️ حذف الفاتورة {row['rowid']}", key=f"del_{row['rowid']}"):
                c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tab3:
    st.header("👥 إضافة عميل جديد")
    with st.form("add_c"):
        name = st.text_input("اسم العميل"); phone = st.text_input("رقم الهاتف")
        shop = st.text_input("اسم المحل"); addr = st.text_input("موقع المحل")
        prov = st.selectbox("المحافظة", ["البصرة", "بغداد", "الموصل", "أخرى"])
        if st.form_submit_button("حفظ العميل"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop, addr, prov)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tab4:
    st.header("📦 إضافة منتج")
    with st.form("add_p"):
        p_name = st.text_input("اسم المادة"); p_price = st.number_input("سعر البيع", 0)
        p_cost = st.number_input("سعر التكلفة", 0); p_qty = st.number_input("الكمية", 0)
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (p_name, p_price, p_qty, p_cost)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM products", conn))

if st.sidebar.button("🚪 تسجيل خروج"): st.session_state.logged_in = False; st.rerun()
