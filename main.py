import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- الإعدادات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- دالة السرعة (Caching) ---
@st.cache_data(ttl=600)
def get_products_data():
    return pd.read_sql("SELECT rowid, * FROM products", conn)

@st.cache_data(ttl=600)
def get_customers_data():
    return pd.read_sql("SELECT * FROM customers", conn)

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول")
    st.subheader("مستمرين نحو الأفضل")
    choice = st.radio("العملية:", ["تسجيل دخول", "حساب جديد"])
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول / تنفيذ"):
        if choice == "حساب جديد":
            try:
                c.execute("INSERT INTO users VALUES (?,?)", (user, pw))
                conn.commit(); st.success("تم الإنشاء!"); st.cache_data.clear()
            except: st.error("المستخدم موجود مسبقاً!")
        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
            if c.fetchone(): st.session_state.logged_in = True; st.rerun()
            else: st.error("خطأ في البيانات!")
    st.stop()

# --- الواجهة الرئيسية ---
st.title("Eng. Yasser Pro System")
st.subheader("مستمرين نحو الأفضل")

if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 إضافة مواد", "📊 المخزن", "🧾 الفواتير", "👥 العملاء"])

with tabs[0]: # البيع
    st.header("🛒 البيع والطلب")
    cust_data = get_customers_data()
    cust_list = ["اختر عميل..."] + cust_data['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_list)
    p_type = st.radio("نوع الدفع", ["نقد", "أقساط"])
    
    prods = get_products_data()
    cols = st.columns(3)
    for idx, row in prods.iterrows():
        with cols[idx % 3]:
            st.info(f"🔹 **{row['name']}**\nالسعر: {row['price_carton']} | المتوفر: {row['quantity']}")
            q = st.number_input(f"الكمية لـ {row['name']}", 0, int(row['quantity']), key=f"q_{idx}")
            if q > 0:
                if st.button(f"➕ إضافة {row['name']}", key=f"add_{idx}"):
                    if 'cart' not in st.session_state: st.session_state.cart = {}
                    st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(q)}
                    st.rerun()

    if 'cart' in st.session_state and st.session_state.cart:
        st.subheader("🛒 السلة")
        st.write(pd.DataFrame(st.session_state.cart).T)
        if st.button("✅ إتمام البيع"):
            if selected_customer == "اختر عميل...": st.error("يجب اختيار عميل!")
            else:
                total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), p_type))
                for n, d in st.session_state.cart.items():
                    c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
                conn.commit(); st.session_state.cart = {}; st.cache_data.clear(); st.success("تم البيع بنجاح!"); st.rerun()

with tabs[1]: # إضافة مواد
    st.header("📦 إضافة مادة جديدة للمخزن")
    with st.form("add_prod", clear_on_submit=True):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر", 0); q = st.number_input("الكمية", 0)
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.cache_data.clear(); st.success("تم الإضافة!")

with tabs[2]: # المخزن
    st.header("📊 جرد المخزن")
    data = get_products_data()
    cols = st.columns(3)
    for i, row in data.iterrows():
        with cols[i % 3]:
            st.warning(f"🔹 **{row['name']}**\nالسعر: {row['price_carton']} | المتوفر: {row['quantity']}")
            if st.button("🗑️ حذف", key=f"d_{row['rowid']}"):
                c.execute("DELETE FROM products WHERE rowid=?", (row['rowid'],)); conn.commit(); st.cache_data.clear(); st.rerun()

with tabs[3]: # الفواتير
    st.header("🧾 سجل الفواتير")
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']} - {row['payment_type']}"):
            cust = c.execute("SELECT * FROM customers WHERE name=?", (row['customer_name'],)).fetchone()
            st.markdown("---")
            st.markdown(f"### 🏢 اسم المحل: {cust[2] if cust else '---'}")
            st.write(f"**العميل:** {row['customer_name']} | **الهاتف:** {cust[1] if cust else '---'}")
            st.write(f"**العنوان:** {cust[3] if cust else '---'} | **المحافظة:** {cust[4] if cust else '---'}")
            st.markdown("---")
            items = ast.literal_eval(row['items'])
            st.table(pd.DataFrame(items).T)
            st.markdown(f"### المجموع الكلي: {row['total']} دينار")
            st.warning("⚠️ بضاعة المباعة لا ترد ولا تستبدل، شكراً لتعاملكم معنا")
            st.success("✨ مستمرين نحو الأفضل")
            st.markdown("---")
            if st.button(f"🗑️ حذف الفاتورة #{row['rowid']}", key=f"del_{row['rowid']}"):
                c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tabs[4]: # العملاء
    st.header("👥 إضافة عميل جديد")
    with st.form("add_c", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n = c1.text_input("اسم العميل"); ph = c2.text_input("رقم الهاتف")
        sh = c1.text_input("اسم المحل"); ad = c2.text_input("العنوان")
        pr = c1.text_input("المحافظة")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (n, ph, sh, ad, pr)); conn.commit(); st.cache_data.clear(); st.rerun()
    st.table(get_customers_data())
