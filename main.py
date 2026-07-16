import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
import hashlib

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

def make_hash(password): return hashlib.sha256(str.encode(password)).hexdigest()

# --- قاعدة البيانات ---
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
conn.commit()

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

if not st.session_state.logged_in:
    st.title("🔐 بوابة المبرمج ياسر")
    if st.radio("العملية:", ["دخول", "تسجيل"], horizontal=True) == "دخول":
        u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, make_hash(p)))
            if c.fetchone(): st.session_state.logged_in = True; st.session_state.username = u; st.rerun()
    else:
        new_u = st.text_input("اسم المستخدم الجديد"); new_p = st.text_input("كلمة المرور", type="password")
        if st.button("إنشاء حساب"):
            try: c.execute("INSERT INTO users VALUES (?,?)", (new_u, make_hash(new_p))); conn.commit(); st.success("تم!")
            except: st.error("مستخدم موجود")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["🛒 البيع", "🧾 الفواتير", "👥 العملاء", "📦 المخزن"])

with tab1:
    st.header("🛒 شاشة البيع")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_options = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_options)
    
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    item_select = st.selectbox("اختر المادة", prods['name'].tolist())
    qty_select = st.number_input("الكمية", min_value=1, value=1)
    
    if st.button("➕ أضف للسلة"):
        price = prods[prods['name'] == item_select]['price'].values[0]
        st.session_state.cart[item_select] = {'price': price, 'qty': qty_select}
    
    if st.session_state.cart:
        st.write("--- السلة ---")
        st.table(pd.DataFrame(st.session_state.cart).T)
        
        if st.button("✅ إتمام البيع"):
            if selected_customer == "اختر عميل...":
                st.error("⚠️ خطأ: يجب اختيار عميل أولاً قبل إتمام الفاتورة!")
            else:
                total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), "نقد"))
                conn.commit(); st.session_state.cart = {}; st.success("تم البيع!"); st.rerun()

with tab2:
    st.header("🧾 سجل الفواتير")
    # عرض الفواتير
    for _, row in pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn).iterrows():
        with st.expander(f"📄 فاتورة #{row['rowid']} | العميل: {row['customer_name']} | المجموع: {row['total']} د.ع"):
            
            # جلب بيانات العميل كاملة من جدول العملاء
            c.execute("SELECT * FROM customers WHERE name=?", (row['customer_name'],))
            cust_info = c.fetchone()
            
            st.subheader("👤 بيانات العميل والمحل")
            if cust_info:
                st.write(f"**الاسم:** {cust_info[0]} | **الهاتف:** {cust_info[1]}")
                st.write(f"**المحل:** {cust_info[2]} | **العنوان:** {cust_info[3]} | **المحافظة:** {cust_info[4]}")
            else:
                st.write("بيانات العميل غير موجودة.")
            
            st.divider()
            st.subheader("🛒 المواد المشتراة")
            items = ast.literal_eval(row['items'])
            for n, d in items.items(): st.write(f"🔹 {n} | الكمية: {d['qty']} | السعر: {d['price']}")
            
            if st.button(f"🗑️ حذف الفاتورة {row['rowid']}", key=f"del_{row['rowid']}"):
                c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tab3:
    st.header("👥 إضافة عميل")
    with st.form("add_c"):
        c1, c2 = st.columns(2)
        with c1: name = st.text_input("اسم العميل"); phone = st.text_input("رقم الهاتف")
        with c2: shop = st.text_input("اسم المحل"); prov = st.selectbox("المحافظة", ["البصرة", "بغداد", "أخرى"])
        addr = st.text_input("موقع المحل")
        if st.form_submit_button("حفظ العميل"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop, addr, prov)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tab4:
    st.header("📦 إضافة منتج")
    with st.form("add_p"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: p_name = st.text_input("اسم المادة")
        with c2: p_price = st.number_input("سعر البيع", 0)
        with c3: p_cost = st.number_input("سعر التكلفة", 0)
        with c4: p_qty = st.number_input("الكمية", 0)
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (p_name, p_price, p_qty, p_cost)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM products", conn))

if st.sidebar.button("🚪 تسجيل خروج"): st.session_state.logged_in = False; st.rerun()
