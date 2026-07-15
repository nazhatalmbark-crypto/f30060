import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import random

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# --- دالة التحديث الذكي ---
def update_db_schema():
    c.execute("PRAGMA table_info(invoices)")
    cols = [info[1] for info in c.fetchall()]
    if 'payment_method' not in cols:
        c.execute("ALTER TABLE invoices ADD COLUMN payment_method TEXT")
        conn.commit()

c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, color TEXT)')
update_db_schema()

# --- إدارة الجلسة (Session State) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- [نظام الدخول] ---
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.username = u
            st.rerun()
        else: st.error("خطأ في البيانات")
    st.stop()

# --- [شاشة البيع الرئيسية] ---
st.header("🛒 شاشة البيع")

# 1. البحث عن العميل (Searchable Selectbox)
cust_df = pd.read_sql("SELECT * FROM customers", conn)
cust_options = ["اختر عميل..."] + cust_df['name'].tolist()
selected_customer = st.selectbox("🔎 ابحث عن العميل", cust_options)

# عرض بيانات العميل تلقائياً
customer_data = None
if selected_customer != "اختر عميل...":
    customer_data = cust_df[cust_df['name'] == selected_customer].iloc[0]
    st.success(f"العميل: {customer_data['name']} | المحل: {customer_data['shop_name']} | العنوان: {customer_data['shop_address']}")

# 2. عرض المنتجات (المخزون المتجدد)
st.divider()
products = pd.read_sql("SELECT rowid, * FROM products", conn)
cols = st.columns(3)

for i, row in products.iterrows():
    with cols[i % 3]:
        # عرض الكمية المتوفرة حالياً من قاعدة البيانات
        st.write(f"**{row['name']}**")
        st.caption(f"المتوفر: {row['quantity']} | السعر: {row['price']}")
        
        qty_input = st.number_input(f"الكمية", min_value=1, max_value=int(row['quantity']), key=f"inp_{row['rowid']}")
        if st.button(f"➕ أضف {row['name']}", key=f"btn_{row['rowid']}"):
            st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty_input}
            st.rerun()

# 3. الفاتورة (قائمة المشتريات)
if st.session_state.cart:
    st.divider()
    st.subheader("📝 الفاتورة")
    for item, data in list(st.session_state.cart.items()):
        c1, c2 = st.columns([4, 1])
        c1.write(f"🔹 {item} | {data['qty']} × {data['price']} = {data['qty']*data['price']} د.ع")
        if c2.button("❌", key=f"del_{item}"):
            del st.session_state.cart[item]
            st.rerun()

    total = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
    st.write(f"### المجموع الكلي: {total} د.ع")
    pay_method = st.radio("طريقة الدفع", ["نقد", "دين"], horizontal=True)

    # التحقق من اختيار العميل قبل الإتمام
    if st.button("✅ إتمام البيع"):
        if selected_customer == "اختر عميل...":
            st.error("⚠️ يرجى اختيار العميل أولاً لإتمام البيع!")
        else:
            # إضافة للفواتير
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", 
                      (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), pay_method))
            # خصم الكمية من المخزن
            for name, data in st.session_state.cart.items():
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(data['qty']), name))
            conn.commit()
            st.session_state.cart = {}
            st.success("تم البيع بنجاح!")
            st.rerun()

# --- قوائم أخرى ---
with st.sidebar:
    st.subheader(f"مرحباً {st.session_state.username}")
    menu = st.radio("القائمة", ["شاشة البيع", "إضافة مواد", "العملاء", "جرد المخزن", "الفواتير"])
    
if menu == "إضافة مواد":
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر", 0); q = st.number_input("الكمية", 0)
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, p, q, 0)); conn.commit(); st.success("تم!")

elif menu == "العملاء":
    with st.form("add_c"):
        n = st.text_input("اسم العميل"); s = st.text_input("اسم المحل"); a = st.text_input("العنوان")
        if st.form_submit_button("إضافة عميل"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (n, "0", s, a, "البصرة")); conn.commit(); st.success("تم!")
    st.table(pd.read_sql("SELECT * FROM customers", conn))

elif menu == "جرد المخزن":
    st.table(pd.read_sql("SELECT * FROM products", conn))

elif menu == "الفواتير":
    df = pd.read_sql("SELECT * FROM invoices ORDER BY date DESC", conn)
    st.dataframe(df)
