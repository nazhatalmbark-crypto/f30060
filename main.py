import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# اسم قاعدة بيانات جديد تماماً لإنهاء كل المشاكل
DB_NAME = 'shop_data_final.db'

def make_hash(password): return hashlib.sha256(str.encode(password)).hexdigest()

# إنشاء الجداول
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
conn.commit()

# حالة الجلسة
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- صفحة الدخول ---
if not st.session_state.logged_in:
    st.title("🔐 بوابة المبرمج ياسر")
    choice = st.radio("العملية:", ["دخول", "إنشاء حساب جديد"], horizontal=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if choice == "دخول":
        if st.button("دخول"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, make_hash(p)))
            if c.fetchone(): st.session_state.logged_in = True; st.rerun()
            else: st.error("خطأ في بيانات الدخول")
    else:
        if st.button("إنشاء حساب"):
            try:
                c.execute("INSERT INTO users VALUES (?,?)", (u, make_hash(p)))
                conn.commit(); st.success("تم إنشاء الحساب، يمكنك الدخول الآن!")
            except: st.error("اسم المستخدم موجود مسبقاً")
    st.stop()

# --- القوائم الرئيسية ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 البيع", "🧾 الفواتير", "👥 العملاء", "📦 المخزن"])

with tab1:
    st.header("🛒 شاشة البيع")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_options = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_options)
    
    # جلب المنتجات بحذر
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    
    if not prods.empty:
        item_select = st.selectbox("المادة", prods['name'].tolist())
        qty_input = st.text_input("الكمية")
        if st.button("➕ أضف للسلة"):
            if selected_customer == "اختر عميل...": st.error("يجب اختيار عميل أولاً!")
            elif not qty_input.isdigit(): st.error("أدخل رقماً للكمية")
            else:
                price = prods[prods['name'] == item_select]['price_carton'].values[0]
                st.session_state.cart[item_select] = {'price': price, 'qty': int(qty_input)}
                st.rerun()
    else:
        st.warning("المخزن فارغ حالياً، أضف مواد أولاً.")
    
    if st.session_state.cart:
        st.write("--- السلة ---")
        st.table(pd.DataFrame(st.session_state.cart).T)
        if st.button("✅ إتمام البيع"):
            if selected_customer == "اختر عميل...":
                st.error("⚠️ لا يمكن إتمام الفاتورة بدون اختيار عميل!")
            else:
                total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
                for name, data in st.session_state.cart.items():
                    c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (data['qty'], name))
                c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d")))
                conn.commit(); st.session_state.cart = {}; st.success("تم البيع بنجاح!"); st.rerun()

with tab2:
    st.header("🧾 سجل الفواتير")
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} | العميل: {row['customer_name']}"):
            try:
                import ast
                items = ast.literal_eval(row['items'])
                for n, d in items.items(): st.write(f"🔹 {n} | {d['qty']} قطعة")
                st.write(f"المجموع: {row['total']}")
            except: st.write("بيانات الفاتورة قديمة.")

with tab3:
    st.header("👥 العملاء")
    with st.form("add_c"):
        name = st.text_input("اسم العميل"); phone = st.text_input("رقم الهاتف")
        shop = st.text_input("اسم المحل"); addr = st.text_input("موقع المحل")
        prov = st.selectbox("المحافظة", ["البصرة", "بغداد", "أخرى"])
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop, addr, prov)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tab4:
    st.header("📦 إضافة منتج")
    with st.form("add_p"):
        p_name = st.text_input("اسم المادة")
        p_price = st.text_input("سعر الكارتون")
        p_qty = st.text_input("الكمية المتوفرة")
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (p_name, int(p_price), int(p_qty))); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM products", conn))

if st.sidebar.button("🚪 خروج"): st.session_state.logged_in = False; st.rerun()
