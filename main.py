import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
import hashlib

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

def make_hash(password): return hashlib.sha256(str.encode(password)).hexdigest()

# قاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
conn.commit()

# إدارة الجلسة
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

if not st.session_state.logged_in:
    st.title("🔐 بوابة المبرمج ياسر")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, make_hash(p)))
        if c.fetchone(): st.session_state.logged_in = True; st.session_state.username = u; st.rerun()
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["🛒 البيع", "🧾 الفواتير", "👥 العملاء", "📦 المخزن"])

with tab1:
    st.header("🛒 شاشة البيع")
    
    # جلب قائمة العملاء
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_options = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_options)
    
    # التحقق من اختيار العميل
    is_customer_selected = (selected_customer != "اختر عميل...")
    
    if not is_customer_selected:
        st.warning("⚠️ يرجى اختيار العميل أولاً لتتمكن من البيع.")

    # القوائم المنسدلة (Grid style)
    prods = pd.read_sql("SELECT * FROM products", conn)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        item_select = st.selectbox("المادة", prods['name'].tolist())
    with col2:
        qty_input = st.text_input("الكمية")
    with col3:
        st.write("---")
        add_btn = st.button("➕ أضف للسلة")
    
    if add_btn:
        if not is_customer_selected:
            st.error("خطأ: لا يمكنك إضافة مواد بدون اختيار عميل!")
        elif not qty_input.isdigit():
            st.error("يرجى إدخال رقم صحيح للكمية")
        else:
            price = prods[prods['name'] == item_select]['price'].values[0]
            st.session_state.cart[item_select] = {'price': price, 'qty': int(qty_input)}
            st.rerun()
    
    if st.session_state.cart:
        st.write("### 🧺 السلة")
        st.table(pd.DataFrame(st.session_state.cart).T)
        
        # تعطيل الزر إذا لم يختر عميل
        if st.button("✅ إتمام البيع", disabled=not is_customer_selected):
            total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", 
                      (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), "نقد"))
            conn.commit(); st.session_state.cart = {}; st.success("تم البيع!"); st.rerun()

with tab2:
    st.header("🧾 سجل الفواتير")
    for _, row in pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn).iterrows():
        with st.expander(f"📄 فاتورة #{row['rowid']} | العميل: {row['customer_name']}"):
            try:
                items = ast.literal_eval(row['items'])
                for n, d in items.items(): st.write(f"🔹 {n} | {d['qty']} قطعة")
                st.write(f"**المجموع: {row['total']}**")
            except: st.error("بيانات الفاتورة قديمة.")
            if st.button(f"🗑️ حذف الفاتورة {row['rowid']}", key=f"del_{row['rowid']}"):
                c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

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
        p_name = st.text_input("اسم المادة"); p_price = st.text_input("السعر"); p_qty = st.text_input("الكمية")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (p_name, int(p_price), int(p_qty))); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM products", conn))

if st.sidebar.button("🚪 خروج"): st.session_state.logged_in = False; st.rerun()
