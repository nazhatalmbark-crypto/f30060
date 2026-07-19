import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime, date
import ast

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- تنسيق CSS للواجهة ---
st.markdown("""
    <style>
    .login-box { background-color: #f8f9fa; padding: 40px; border-radius: 20px; border: 2px solid #e1e4e8; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- الإعدادات وقاعدة البيانات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- الدوال المساعدة ---
def get_products(): return pd.read_sql("SELECT rowid, * FROM products", conn)
def get_customers(): return pd.read_sql("SELECT * FROM customers", conn)

# --- تسجيل الدخول (النسخة النهائية) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.title("🔐 Eng. Yasser Pro System")
    st.subheader("مستمرين نحو الأفضل")
    
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("دخول النظام"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
            if c.fetchone(): st.session_state.logged_in = True; st.rerun()
            else: st.error("خطأ في البيانات!")
    with col2:
        if st.button("دخول كزائر (Guest)"):
            st.session_state.logged_in = True; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- الواجهة الرئيسية ---
st.title("Eng. Yasser Pro System")
st.subheader("مستمرين نحو الأفضل")
if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["📊 الإحصائيات", "🛒 البيع", "📦 المخزن", "🧾 الفواتير", "👥 العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # الإحصائيات
    st.header("📊 لوحة التحكم")
    inv = pd.read_sql("SELECT * FROM invoices", conn)
    if not inv.empty:
        col1, col2 = st.columns(2)
        col1.metric("إجمالي المبيعات", f"{inv['total'].sum()} د.ع")
        col2.metric("عدد الفواتير", len(inv))
        st.bar_chart(inv.groupby('payment_type')['total'].sum())
    else: st.info("لا توجد مبيعات!")

with tabs[1]: # البيع
    st.header("🛒 البيع والطلب")
    cust_list = ["اختر عميل..."] + get_customers()['name'].tolist()
    selected_customer = st.selectbox("🔎 العميل", cust_list)
    prods = get_products()
    cols = st.columns(3)
    for idx, row in prods.iterrows():
        with cols[idx % 3]:
            st.info(f"🔹 {row['name']} (متوفر: {row['quantity']})")
            q = st.number_input(f"الكمية لـ {row['name']}", 0, int(row['quantity']), key=f"q_{idx}")
            if q > 0 and st.button(f"أضف {row['name']}", key=f"add_{idx}"):
                if 'cart' not in st.session_state: st.session_state.cart = {}
                st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(q)}
                st.rerun()
    if 'cart' in st.session_state and st.session_state.cart:
        if st.button("✅ إتمام البيع"):
            total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), str(date.today()), "نقد"))
            for n, d in st.session_state.cart.items(): c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
            conn.commit(); st.session_state.cart = {}; st.success("تم البيع!"); st.rerun()

with tabs[2]: # المخزن
    st.header("📦 جرد المخزن")
    st.table(get_products())
    with st.form("new_p"):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر"); q = st.number_input("الكمية")
        if st.form_submit_button("إضافة"): c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()

with tabs[3]: # الفواتير
    st.header("🧾 سجل الفواتير")
    for _, row in pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn).iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']} - {row['total']} د.ع"):
            st.table(pd.DataFrame(ast.literal_eval(row['items'])).T)
            st.warning("⚠️ بضاعة المباعة لا ترد ولا تستبدل - مستمرين نحو الأفضل")

with tabs[4]: # العملاء
    st.header("👥 العملاء")
    st.table(get_customers())

with tabs[5]: # المساعد الذكي
    st.header("🤖 المساعد الذكي")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚠️ تنبيهات المخزن")
        low_stock = get_products()[get_products()['quantity'] < 5]
        if not low_stock.empty: st.warning("مواد ناقصة:"); st.table(low_stock[['name', 'quantity']])
        else: st.success("المخزن مكتمل!")
    with c2:
        st.subheader("💡 أدوات")
        if st.button("اقتراح اسم محل"): st.info(f"الاسم: {random.choice(['مؤسسة ياسر للتقنية', 'مخازن الابتكار', 'ياسر برو للتجارة'])}")
        if st.button("تنظيف المخزن (حذف الأصفار)"): c.execute("DELETE FROM products WHERE quantity <= 0"); conn.commit(); st.rerun()
