import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
import hashlib

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# دالة التشفير
def make_hash(password): return hashlib.sha256(str.encode(password)).hexdigest()

# قاعدة البيانات (بدون سعر التكلفة)
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
conn.commit()

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

if not st.session_state.logged_in:
    st.title("🔐 بوابة المبرمج ياسر")
    choice = st.radio("العملية:", ["دخول", "إنشاء حساب جديد"], horizontal=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    
    if choice == "دخول":
        if st.button("دخول"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, make_hash(p)))
            if c.fetchone(): st.session_state.logged_in = True; st.session_state.username = u; st.rerun()
            else: st.error("اسم المستخدم أو كلمة المرور خطأ")
    else:
        if st.button("إنشاء حساب"):
            try:
                c.execute("INSERT INTO users VALUES (?,?)", (u, make_hash(p)))
                conn.commit(); st.success("تم إنشاء الحساب! يمكنك الدخول الآن.")
            except: st.error("اسم المستخدم موجود مسبقاً.")
    st.stop()

# --- القوائم الرئيسية ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 البيع", "🧾 الفواتير", "👥 العملاء", "📦 المخزن"])

with tab1:
    st.header("🛒 شاشة البيع")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_options = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_options)
    
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    item_select = st.selectbox("اختر المادة", prods['name'].tolist())
    qty_input = st.text_input("الكمية") # مدخل نصي بدون أزرار +/-
    
    if st.button("➕ أضف للسلة"):
        if qty_input.isdigit():
            # جلب سعر المادة
            item_data = prods[prods['name'] == item_select]
            price = item_data['price'].values[0]
            st.session_state.cart[item_select] = {'price': price, 'qty': int(qty_input)}
        else: st.error("يرجى إدخال رقم صحيح للكمية")
    
    if st.session_state.cart:
        st.write("--- السلة ---")
        st.table(pd.DataFrame(st.session_state.cart).T)
        
        # زر إتمام البيع مع التحقق من العميل
        if st.button("✅ إتمام البيع"):
            if selected_customer == "اختر عميل...":
                st.error("⚠️ تنبيه: لا يمكن إتمام الفاتورة بدون اختيار عميل!")
            else:
                total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), "نقد"))
                conn.commit(); st.session_state.cart = {}; st.success("تم البيع بنجاح!"); st.rerun()

with tab2:
    st.header("🧾 سجل الفواتير")
    for _, row in pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn).iterrows():
        with st.expander(f"📄 فاتورة #{row['rowid']} | العميل: {row['customer_name']} | المجموع: {row['total']}"):
            try:
                items = ast.literal_eval(row['items'])
                for n, d in items.items(): st.write(f"🔹 {n} | {d['qty']} قطعة")
            except: st.error("خطأ في قراءة بيانات الفاتورة.")
            
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
        p_name = st.text_input("اسم المادة")
        p_price = st.text_input("سعر البيع")
        p_qty = st.text_input("الكمية")
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (p_name, int(p_price), int(p_qty))); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM products", conn))

if st.sidebar.button("🚪 تسجيل خروج"): st.session_state.logged_in = False; st.rerun()
