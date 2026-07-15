import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# إعداد قاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# --- تنظيف وإعادة بناء الجداول (لحل مشكلة OperationalError نهائياً) ---
c.execute('DROP TABLE IF EXISTS products')
c.execute('DROP TABLE IF EXISTS customers')
c.execute('DROP TABLE IF EXISTS invoices')

c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
# تم حذف خانة رقم هاتف المحل هنا (5 حقول فقط)
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT)')
conn.commit()

# --- CSS ---
st.markdown("""
    <style>
    .header-box { background-color: #1a4d2e; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    .card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}

# --- القائمة الجانبية ---
st.sidebar.title("النظام")
menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "العملاء", "جرد المخزن", "التقارير"])
st.sidebar.markdown("---")
st.sidebar.write("**المبرمج ياسر - مستمرين نحو الأفضل**")

# --- 1. شاشة البيع ---
if menu == "شاشة البيع":
    st.markdown('<div class="header-box"><h2>🛒 شاشة البيع</h2></div>', unsafe_allow_html=True)
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    
    customers = pd.read_sql("SELECT name FROM customers", conn)
    selected_customer = st.selectbox("اختر العميل", customers['name'].tolist() if not customers.empty else ["عام"])
    
    cols = st.columns(3)
    for i, row in products.iterrows():
        with cols[i % 3]:
            st.markdown(f'<div class="card"><h4>{row["name"]}</h4><p>السعر: {row["price"]} | المتوفر: {row["quantity"]}</p></div>', unsafe_allow_html=True)
            qty = st.number_input(f"الكمية {row['name']}", min_value=0, max_value=row["quantity"], key=f"q_{row['rowid']}")
            if qty > 0 and st.button(f"إضافة {row['name']}", key=f"btn_{row['rowid']}"):
                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty}
    
    if st.session_state.cart:
        st.divider()
        st.header("الفاتورة")
        total = sum(item['price'] * item['qty'] for item in st.session_state.cart.values())
        st.table(pd.DataFrame.from_dict(st.session_state.cart, orient='index'))
        st.write(f"### المجموع: {total} د.ع")
        if st.button("إتمام البيع"):
            c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (selected_customer, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d")))
            for name, data in st.session_state.cart.items():
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (data['qty'], name))
            conn.commit()
            st.session_state.cart = {}
            st.success("تم البيع بنجاح!")
            st.rerun()

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد جديدة")
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر"); q = st.text_input("الكمية")
        if st.form_submit_button("إضافة"):
            if n and p.isdigit() and q.isdigit():
                c.execute("INSERT INTO products (name, price, quantity, cost_price) VALUES (?,?,?,?)", (n, int(p), int(q), 0))
                conn.commit(); st.success("تمت الإضافة!")
            else: st.error("تأكد من إدخال بيانات صحيحة!")

# --- 3. العملاء ---
elif menu == "العملاء":
    st.header("👥 إدارة العملاء")
    with st.form("add_c"):
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم هاتف العميل")
        shop_name = st.text_input("اسم المحل")
        shop_address = st.text_input("عنوان المحل")
        province = st.text_input("المحافظة")
        
        if st.form_submit_button("إضافة عميل جديد"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop_name, shop_address, province))
            conn.commit(); st.success("تم إضافة العميل بنجاح!")
    
    st.subheader("قائمة العملاء")
    st.table(pd.read_sql("SELECT * FROM customers", conn))

# --- 4. جرد المخزن والتقارير ---
elif menu == "جرد المخزن":
    st.header("📦 جرد المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

elif menu == "التقارير":
    st.header("📈 التقارير")
    st.table(pd.read_sql("SELECT * FROM invoices", conn))
    st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
