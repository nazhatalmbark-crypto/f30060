import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# إعداد قاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS purchases (item_name TEXT, quantity INTEGER, total INTEGER, supplier TEXT, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS expenses (description TEXT, amount INTEGER, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, timestamp TEXT, payment_type TEXT)')
conn.commit()

# --- CSS ---
st.markdown("""
    <style>
    .prod-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #fff; text-align: center; margin: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = []

# --- القائمة ---
menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "التقارير"])

# --- 1. شاشة البيع ---
if menu == "شاشة البيع":
    st.header("🛒 إدارة المبيعات")
    
    # جلب المنتجات من القاعدة
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    
    if products.empty:
        st.info("قاعدة البيانات فارغة، أضف مواد من صفحة 'إضافة مواد'")
    else:
        cols = st.columns(2)
        for i, row in products.iterrows():
            with cols[i % 2]:
                st.markdown(f'<div class="prod-card"><h4>{row["name"]}</h4><p>السعر: {row["price"]} د.ع</p><p>الكمية: {row["quantity"]}</p></div>', unsafe_allow_html=True)
                if st.button(f"إضافة {row['name']}", key=f"add_{row['rowid']}"):
                    st.session_state.cart.append({'name': row['name'], 'price': int(row['price'])})
                    st.success(f"تم إضافة {row['name']}")

# --- 2. إضافة مواد (مع جدول مراقبة) ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد جديدة")
    with st.form("add_p"):
        n = st.text_input("اسم المادة")
        p = st.text_input("السعر")
        q = st.text_input("الكمية")
        cp = st.text_input("سعر الشراء")
        submit = st.form_submit_button("إضافة")
        
        if submit:
            if n and p.isdigit() and q.isdigit() and cp.isdigit():
                c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, int(p), int(q), int(cp)))
                conn.commit()
                st.success("تم الحفظ!")
            else:
                st.error("خطأ في البيانات! تأكد أن السعر والكمية أرقام.")
    
    # جدول المراقبة (هنا ستعرف إذا كانت البيانات انحفظت فعلاً)
    st.subheader("📋 جدول المراقبة (كل المنتجات في القاعدة)")
    df_debug = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(df_debug)

# --- 3. التقارير ---
elif menu == "التقارير":
    st.header("📈 لوحة التحكم")
    st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
