import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# إعداد قاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# تنظيف الجداول القديمة وإعادة إنشائها (لضمان عمل الكود الجديد بدون أخطاء)
c.execute('DROP TABLE IF EXISTS products')
c.execute('DROP TABLE IF EXISTS purchases')
c.execute('DROP TABLE IF EXISTS expenses')
c.execute('DROP TABLE IF EXISTS invoices')

c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS purchases (item_name TEXT, quantity INTEGER, total INTEGER, supplier TEXT, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS expenses (description TEXT, amount INTEGER, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, timestamp TEXT, payment_type TEXT)')
conn.commit()

# --- CSS للتصميم ---
st.markdown("""
    <style>
    .header-box { background-color: #1a4d2e; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    .prod-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #fff; text-align: center; margin: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = []

# --- القائمة الجانبية ---
st.sidebar.title("النظام")
menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "التقارير"])
st.sidebar.write("**المبرمج ياسر - مستمرين نحو الأفضل**")

# --- 1. شاشة البيع ---
if menu == "شاشة البيع":
    st.markdown('<div class="header-box"><h2>🛒 إدارة المبيعات</h2></div>', unsafe_allow_html=True)
    
    # عرض كل المنتجات بدون استثناء
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    
    if products.empty:
        st.warning("لا توجد منتجات حالياً. قم بإضافة منتجات من القائمة الجانبية.")
    else:
        cols = st.columns(2)
        for i, row in products.iterrows():
            with cols[i % 2]:
                st.markdown(f'<div class="prod-card"><h4>{row["name"]}</h4><p>السعر: {row["price"]} د.ع</p><p>الكمية: {row["quantity"]}</p></div>', unsafe_allow_html=True)
                if st.button(f"إضافة {row['name']}", key=f"add_{row['rowid']}"):
                    st.session_state.cart.append({'name': row['name'], 'price': int(row['price'])})
                    st.success(f"تم إضافة {row['name']} للسلة")

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد جديدة")
    with st.form("add_p"):
        n = st.text_input("اسم المادة")
        p = st.text_input("السعر")
        q = st.text_input("الكمية")
        cp = st.text_input("سعر الشراء")
        if st.form_submit_button("إضافة"):
            if n and p.isdigit() and q.isdigit() and cp.isdigit():
                c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, int(p), int(q), int(cp)))
                conn.commit()
                st.success(f"تمت إضافة {n} بنجاح!")
            else:
                st.error("خطأ: يرجى التأكد من كتابة اسم المادة وأرقام صحيحة في خانات السعر والكمية.")

# --- 3. التقارير ---
elif menu == "التقارير":
    st.header("📈 لوحة التحكم")
    st.write("المبرمج ياسر - مستمرين نحو الأفضل")
    products = pd.read_sql("SELECT * FROM products", conn)
    st.table(products)
