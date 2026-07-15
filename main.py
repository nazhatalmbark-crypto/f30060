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
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT)')
conn.commit()

# --- CSS للتصميم ---
st.markdown("""
    <style>
    .header-box { background-color: #1a4d2e; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    .card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}

# --- القائمة الجانبية ---
st.sidebar.title("النظام")
menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "العملاء", "جرد المخزن", "الفواتير", "التقارير"])
st.sidebar.markdown("---")
st.sidebar.write("**المبرمج ياسر - مستمرين نحو الأفضل**")

# --- 1. شاشة البيع ---
if menu == "شاشة البيع":
    st.markdown('<div class="header-box"><h2>🛒 شاشة البيع</h2></div>', unsafe_allow_html=True)
    
    customers = pd.read_sql("SELECT name FROM customers", conn)
    customer_list = customers['name'].tolist() if not customers.empty else ["عام"]
    selected_customer = st.selectbox("اختر العميل", customer_list)
    
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    cols = st.columns(3)
    for i, row in products.iterrows():
        with cols[i % 3]:
            st.markdown(f'<div class="card"><h4>{row["name"]}</h4><p>السعر: {row["price"]} | المتوفر: {row["quantity"]}</p></div>', unsafe_allow_html=True)
            qty = st.number_input(f"الكمية {row['name']}", min_value=0, max_value=row["quantity"], key=f"q_{row['rowid']}")
            if qty > 0 and st.button(f"أضف {row['name']}", key=f"btn_{row['rowid']}"):
                st.session_state.cart[row['name'].strip()] = {'price': row['price'], 'qty': qty}
                st.rerun()

    if st.session_state.cart:
        st.divider()
        st.header("الفاتورة الحالية")
        st.table(pd.DataFrame.from_dict(st.session_state.cart, orient='index'))
        total = sum(item['price'] * item['qty'] for item in st.session_state.cart.values())
        st.write(f"### المجموع الكلي: {total} د.ع")
        
        if st.button("✅ إتمام البيع وتخفيض المخزن"):
            c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (selected_customer, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d")))
            for name, data in st.session_state.cart.items():
                # استخدام strip لضمان تطابق الاسم بدقة
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(data['qty']), name.strip()))
            conn.commit()
            st.session_state.cart = {}
            st.success("تم البيع بنجاح ونقصت المواد من المخزن!")
            st.rerun()

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد جديدة")
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر"); q = st.text_input("الكمية")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products (name, price, quantity, cost_price) VALUES (?,?,?,?)", (n.strip(), int(p), int(q), 0))
            conn.commit(); st.success("تمت الإضافة!")

# --- 3. العملاء ---
elif menu == "العملاء":
    st.header("👥 إدارة العملاء")
    with st.form("add_c"):
        name = st.text_input("اسم العميل"); phone = st.text_input("رقم هاتف العميل")
        shop_name = st.text_input("اسم المحل"); shop_address = st.text_input("عنوان المحل"); province = st.text_input("المحافظة")
        if st.form_submit_button("إضافة عميل جديد"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop_name, shop_address, province))
            conn.commit(); st.success("تم إضافة العميل!")
    st.table(pd.read_sql("SELECT * FROM customers", conn))

# --- 4. جرد المخزن ---
elif menu == "جرد المخزن":
    st.header("📦 جرد المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

# --- 5. الفواتير (خانة جديدة) ---
elif menu == "الفواتير":
    st.header("🧾 سجل الفواتير")
    st.table(pd.read_sql("SELECT * FROM invoices ORDER BY date DESC", conn))

# --- 6. التقارير ---
elif menu == "التقارير":
    st.header("📈 التقارير المالية")
    sales = pd.read_sql("SELECT * FROM invoices", conn)
    st.metric("إجمالي المبيعات", f"{sales['total'].sum() if not sales.empty else 0} د.ع")
    st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
