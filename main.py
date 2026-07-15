import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import random

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# --- دالة تحديث قاعدة البيانات التلقائية (حل جذري للخطأ) ---
def update_db_schema():
    # التأكد من وجود الأعمدة المطلوبة وتحديث الجدول إن لزم الأمر
    c.execute("PRAGMA table_info(invoices)")
    columns = [info[1] for info in c.fetchall()]
    if 'payment_method' not in columns:
        c.execute("ALTER TABLE invoices ADD COLUMN payment_method TEXT DEFAULT 'نقد'")
        conn.commit()

# إنشاء الجداول الأساسية
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, color TEXT)')
update_db_schema() # تنفيذ التحديث الذكي

# --- دالة لون عشوائي ---
def get_random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# --- نظام الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_color = get_random_color()
    st.session_state.cart = {}

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
        else: st.error("خطأ في البيانات!")
    if st.button("إنشاء حساب جديد"):
        try:
            c.execute("INSERT INTO users VALUES (?,?,?)", (u, p, get_random_color()))
            conn.commit(); st.success("تم إنشاء الحساب!")
        except: st.error("اسم المستخدم موجود!")
    st.stop()

# --- الواجهة ---
st.sidebar.markdown(f"""
    <div style="background-color: {st.session_state.user_color}; padding: 15px; border-radius: 50%; width: 50px; height: 50px; text-align: center; color: white; font-weight: bold;">
    {st.session_state.username[0].upper()}
    </div>
    <h3>مرحباً، {st.session_state.username}</h3>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "العملاء", "جرد المخزن", "الفواتير", "التقارير"])

# --- 1. شاشة البيع ---
if menu == "شاشة البيع":
    st.header("🛒 شاشة البيع")
    products = pd.read_sql("SELECT rowid, * FROM products", conn).drop_duplicates(subset=['name'])
    
    # اختيار العميل
    customers = pd.read_sql("SELECT name FROM customers", conn)
    cust_list = customers['name'].tolist() if not customers.empty else ["عام"]
    selected_customer = st.selectbox("اختر العميل", cust_list)
    
    # عرض المنتجات
    cols = st.columns(3)
    for i, row in products.iterrows():
        with cols[i % 3]:
            st.write(f"**{row['name']}** (السعر: {row['price']})")
            qty = st.number_input(f"الكمية لـ {row['name']}", min_value=1, max_value=row['quantity'], key=f"q_{row['rowid']}")
            if st.button(f"➕ أضف {row['name']}", key=f"add_{row['rowid']}"):
                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty}
                st.rerun()

    # الفاتورة
    if st.session_state.cart:
        st.divider()
        st.subheader("📝 الفاتورة الحالية")
        # عرض المنتجات مع زر حذف
        for item, data in list(st.session_state.cart.items()):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔹 {item} | {data['qty']} × {data['price']} = {data['qty']*data['price']} د.ع")
            if c2.button("❌", key=f"del_{item}"):
                del st.session_state.cart[item]
                st.rerun()
        
        total = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
        st.write(f"### المجموع الكلي: {total} د.ع")
        pay_method = st.radio("طريقة الدفع", ["نقد", "دين"])
        
        if st.button("✅ إتمام البيع"):
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d"), pay_method))
            for name, data in st.session_state.cart.items():
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(data['qty']), name))
            conn.commit(); st.session_state.cart = {}; st.success("تم البيع بنجاح!"); st.rerun()

# --- باقي الصفحات ---
elif menu == "إضافة مواد":
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر", 0); q = st.number_input("الكمية", 0)
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, p, q, 0)); conn.commit(); st.success("تم!")

elif menu == "الفواتير":
    st.header("🧾 سجل الفواتير")
    df = pd.read_sql("SELECT * FROM invoices ORDER BY date DESC", conn)
    def color_row(row):
        color = '#d4edda' if row['payment_method'] == 'نقد' else '#f8d7da'
        return [f'background-color: {color}'] * len(row)
    if not df.empty: st.dataframe(df.style.apply(color_row, axis=1))
    
elif menu == "جرد المخزن":
    st.table(pd.read_sql("SELECT * FROM products", conn))

elif menu == "التقارير":
    sales = pd.read_sql("SELECT * FROM invoices", conn)
    st.metric("إجمالي المبيعات", f"{sales['total'].sum() if not sales.empty else 0} د.ع")
