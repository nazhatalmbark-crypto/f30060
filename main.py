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
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, shop_name TEXT, phone TEXT, items TEXT, total INTEGER, timestamp TEXT, payment_type TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, area TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS debts (customer_name TEXT, amount INTEGER, note TEXT)')
conn.commit()

# --- CSS للتصميم الاحترافي ---
st.markdown("""
    <style>
    .invoice-box { border: 2px solid #333; padding: 30px; border-radius: 15px; background-color: #f8f9fa; color: #000; max-width: 500px; margin: auto; box-shadow: 5px 5px 15px #ccc; text-align: center;}
    .prod-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #ffffff; text-align: center; margin: 10px; box-shadow: 2px 2px 5px #eee; }
    .header-box { background-color: #1a4d2e; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = []
if 'checkout_mode' not in st.session_state: st.session_state.checkout_mode = False

# --- شاشة البيع ---
st.markdown('<div class="header-box"><h2>إدارة المبيعات</h2></div>', unsafe_allow_html=True)

# الهيدر العلوي: سلة المشتريات
col1, col2 = st.columns([4, 1])
with col1:
    search_term = st.text_input("🔍 ابحث عن مادة...", "")
with col2:
    if st.button(f"🛒 السلة ({len(st.session_state.cart)})"):
        if len(st.session_state.cart) > 0:
            st.session_state.checkout_mode = True
            st.rerun()

# --- وضع الفاتورة (عند الضغط على السلة) ---
if st.session_state.checkout_mode:
    st.markdown('<div class="invoice-box">', unsafe_allow_html=True)
    st.header("Eng. Yasser System")
    st.write("---")
    for item in st.session_state.cart:
        st.write(f"{item['name']} ... {item['price']} د.ع")
    st.write("---")
    total = sum(i['price'] for i in st.session_state.cart)
    st.write(f"### المجموع الكلي: {total} د.ع")
    st.write("**المبرمج ياسر - مستمرين نحو الأفضل**") # العبارة المطلوبة
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("تأكيد وحفظ الفاتورة"):
        c.execute("INSERT INTO invoices VALUES (?,?,?,?,?,?,?)", 
                  ("عام", "N/A", "N/A", str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d"), "نقد"))
        conn.commit()
        st.session_state.cart = []
        st.session_state.checkout_mode = False
        st.success("تم الحفظ!")
        st.rerun()
    if st.button("رجوع"):
        st.session_state.checkout_mode = False
        st.rerun()

else:
    # --- عرض المنتجات بنظام الشبكة (مثل البروست) ---
    query = "SELECT rowid, * FROM products WHERE quantity > 0"
    if search_term: query += f" AND name LIKE '%{search_term}%'"
    products = pd.read_sql(query, conn)
    
    cols = st.columns(2)
    for i, row in products.iterrows():
        with cols[i % 2]:
            st.markdown(f"""
                <div class="prod-card">
                    <h4>{row['name']}</h4>
                    <p>السعر: {row['price']} دينار</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"إضافة للمبيعات", key=f"add_{row['rowid']}"):
                st.session_state.cart.append({'name': row['name'], 'price': int(row['price'])})
                st.rerun()

# --- القائمة الجانبية للتنقل ---
st.sidebar.title("النظام")
if st.sidebar.button("إضافة مواد"):
    st.info("اذهب لصفحة إضافة المواد")
if st.sidebar.button("الأرشيف"):
    st.info("الأرشيف")
st.sidebar.markdown("---")
st.sidebar.write("المبرمج ياسر - مستمرين نحو الأفضل")
