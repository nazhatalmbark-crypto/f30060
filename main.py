import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
import hashlib

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- دالة التشفير ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
conn.commit()

# --- التصميم (CSS) ---
st.markdown("""
    <style>
    .invoice-card { background-color: #f8f9fa; border-radius: 15px; padding: 15px; margin-bottom: 10px; border: 1px solid #e0e0e0; }
    .badge-price { padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- نظام الدخول الآمن ---
if not st.session_state.logged_in:
    st.title("🔐 بوابة الحماية - المبرمج ياسر")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        hashed_p = make_hash(p)
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hashed_p))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.username = u
            st.rerun()
        else: st.error("بيانات غير صحيحة!")
    st.stop()

# --- القوائم العلوية ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 شاشة البيع", "🧾 الفواتير والبحث", "👥 العملاء", "📦 المخزن"])

# 1. شاشة البيع
with tab1:
    st.header("🛒 شاشة البيع")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_options = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 ابحث عن العميل", cust_options)
    
    products_df = pd.read_sql("SELECT rowid, * FROM products", conn).drop_duplicates(subset=['name'])
    cols = st.columns(3)
    for i, row in products_df.iterrows():
        with cols[i % 3]:
            st.write(f"**{row['name']}**")
            qty_input = st.number_input(f"المتوفر: {row['quantity']}", min_value=1, max_value=int(row['quantity']), key=f"inp_{row['rowid']}")
            if st.button(f"➕ أضف {row['name']}", key=f"btn_{row['rowid']}"):
                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty_input}
                st.rerun()
    
    if st.session_state.cart:
        if st.button("✅ إتمام البيع"):
            if selected_customer == "اختر عميل...": st.error("اختر عميلاً أولاً!")
            else:
                total = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), "نقد"))
                for n, d in st.session_state.cart.items(): c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (d['qty'], n))
                conn.commit(); st.session_state.cart = {}; st.rerun()

# 2. الفواتير (مع ميزة البحث والفتح)
with tab2:
    st.header("🧾 سجل الفواتير")
    search_query = st.text_input("🔍 بحث باسم العميل...")
    
    query = "SELECT rowid, * FROM invoices ORDER BY rowid DESC"
    df = pd.read_sql(query, conn)
    
    if search_query:
        df = df[df['customer_name'].str.contains(search_query, case=False)]

    for i, row in df.iterrows():
        p_col = "#ffc107" if row['payment_method'] == 'نقد' else "#dc3545"
        
        # البطاقة (Card)
        st.markdown(f"""
            <div class="invoice-card">
                <b>فاتورة #{row['rowid']} | العميل: {row['customer_name']}</b>
                <br><span class="badge-price" style="background-color: {p_col};">{row['total']} دينار</span>
            </div>
        """, unsafe_allow_html=True)
        
        # ميزة الفتح (Expander)
        with st.expander("👁️ عرض تفاصيل الفاتورة"):
            items = ast.literal_eval(row['items'])
            for name, data in items.items():
                st.write(f"🔹 {name} | الكمية: {data['qty']} | السعر: {data['price']}")
            if st.button(f"🗑️ حذف الفاتورة #{row['rowid']}", key=f"del_{row['rowid']}"):
                c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

# 3. العملاء
with tab3:
    st.header("👥 إضافة عملاء")
    with st.form("add_c"):
        n = st.text_input("اسم العميل"); ph = st.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (n, ph, "", "", "")); conn.commit(); st.rerun()

# 4. المخزن
with tab4:
    st.header("📦 جرد المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

if st.sidebar.button("🚪 تسجيل خروج"):
    st.session_state.logged_in = False
    st.rerun()
