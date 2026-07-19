import streamlit as st
import sqlite3
import pandas as pd
import random

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- تنسيق الواجهة (CSS) ---
st.markdown("""
    <style>
    .login-box { background-color: #f8f9fa; padding: 30px; border-radius: 15px; border: 1px solid #ddd; }
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

# --- تسجيل الدخول (معدل) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.title("🔐 Eng. Yasser System")
    st.subheader("مستمرين نحو الأفضل")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        if c.fetchone(): st.session_state.logged_in = True; st.rerun()
        else: st.error("خطأ في البيانات!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- الواجهة ---
st.title("Eng. Yasser Pro System")
st.subheader("مستمرين نحو الأفضل")
if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 المخزن", "🧾 الفواتير", "👥 العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # البيع
    # (نفس نظام البيع السابق)
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    cols = st.columns(3)
    for idx, row in prods.iterrows():
        with cols[idx % 3]:
            st.info(f"🔹 {row['name']} (المتوفر: {row['quantity']})")
            q = st.number_input(f"الكمية لـ {row['name']}", 0, int(row['quantity']), key=f"q_{idx}")
            if q > 0 and st.button(f"أضف {row['name']}", key=f"add_{idx}"):
                if 'cart' not in st.session_state: st.session_state.cart = {}
                st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(q)}
                st.rerun()
    if 'cart' in st.session_state and st.session_state.cart:
        if st.button("✅ إتمام البيع"):
            # (نفس منطق الحفظ)
            st.success("تم البيع!")
            st.session_state.cart = {}
            st.rerun()

with tabs[1]: # المخزن
    st.header("📦 جرد المخزن")
    data = pd.read_sql("SELECT rowid, * FROM products", conn)
    st.table(data)
    with st.form("new_p"):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر"); q = st.number_input("الكمية")
        if st.form_submit_button("إضافة"): c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()

with tabs[4]: # المساعد الذكي (الجديد)
    st.header("🤖 المساعد الذكي")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ تنبيهات المخزن")
        stock = pd.read_sql("SELECT * FROM products", conn)
        low_stock = stock[stock['quantity'] < 5]
        if not low_stock.empty:
            st.warning("المواد التي شارفت على النفاذ:")
            st.table(low_stock[['name', 'quantity']])
        else:
            st.success("المخزن مكتمل، لا توجد مواد ناقصة!")

    with col2:
        st.subheader("💡 أدوات التخطيط")
        if st.button("اقتراح اسم محل جديد"):
            names = ["مؤسسة ياسر للتقنية", "مخازن الابتكار", "ياسر برو للتجارة", "مستقبل الحاسبات"]
            st.info(f"الاسم المقترح: {random.choice(names)}")
        
        if st.button("تنظيف قاعدة البيانات (حذف الصفرية)"):
            c.execute("DELETE FROM products WHERE quantity <= 0")
            conn.commit(); st.rerun()
