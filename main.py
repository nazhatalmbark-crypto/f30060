import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, timestamp TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, area TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS debts (customer_name TEXT, amount INTEGER, note TEXT)')
conn.commit()

# --- القائمة الجانبية ---
st.sidebar.title("Eng. Yasser System")
menu = st.sidebar.radio("القائمة", ["سلة البيع", "إضافة مواد", "جرد المخزن", "أرشيف الفواتير", "العملاء", "الديون"])

# --- 1. سلة البيع ---
if 'cart' not in st.session_state: st.session_state.cart = []
if menu == "سلة البيع":
    st.header("🛒 سلة البيع")
    
    col1, col2 = st.columns([2, 1])
    products = pd.read_sql("SELECT * FROM products WHERE quantity > 0", conn)
    
    with col1:
        st.subheader("قائمة المواد")
        for _, row in products.iterrows():
            if st.button(f"إضافة {row['name']} ({row['price']})", key=f"add_{row['name']}"):
                st.session_state.cart.append({'name': row['name'], 'price': int(row['price'])})
                st.rerun()

    with col2:
        st.subheader("السلة")
        cust_name = st.text_input("اسم الزبون")
        if st.session_state.cart:
            # عرض المواد في السلة مع زر حذف
            for i, item in enumerate(st.session_state.cart):
                c1, c2 = st.columns([3, 1])
                c1.write(f"{item['name']} - {item['price']}")
                if c2.button("❌", key=f"del_cart_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            
            total = int(sum(i['price'] for i in st.session_state.cart))
            st.write(f"### المجموع الكلي: {total}")
            
            if st.button("حفظ وإصدار الفاتورة"):
                c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (cust_name, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d %H:%M")))
                for item in st.session_state.cart:
                    c.execute("UPDATE products SET quantity = quantity - 1 WHERE name = ?", (item['name'],))
                conn.commit()
                st.session_state.cart = []
                st.success("تم الحفظ!")
                st.rerun()

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد جديدة")
    with st.form("add_p"):
        name = st.text_input("اسم المادة")
        price = st.number_input("السعر", step=1, min_value=0)
        qty = st.number_input("الكمية", step=1, min_value=0)
        if st.form_submit_button("حفظ"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (name, int(price), int(qty)))
            conn.commit()
            st.success("تمت الإضافة!")

# --- 3. جرد المخزن (مع خيار الحذف) ---
elif menu == "جرد المخزن":
    st.header("📊 جرد المخزن")
    products = pd.read_sql("SELECT * FROM products", conn)
    for _, row in products.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"{row['name']} | السعر: {row['price']} | الكمية: {row['quantity']}")
        if c2.button(f"حذف المادة", key=f"delete_db_{row['name']}"):
            c.execute("DELETE FROM products WHERE name = ?", (row['name'],))
            conn.commit()
            st.rerun()

# --- 4. أرشيف الفواتير ---
elif menu == "أرشيف الفواتير":
    st.header("📜 أرشيف الفواتير")
    st.dataframe(pd.read_sql("SELECT * FROM invoices", conn), use_container_width=True)

# --- 5. العملاء ---
elif menu == "العملاء":
    st.header("👥 العملاء")
    with st.form("add_c"):
        name = st.text_input("اسم العميل")
        shop = st.text_input("المحل")
        phone = st.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers (name, shop_name, phone) VALUES (?,?,?)", (name, shop, phone))
            conn.commit()
            st.success("تم!")
    st.dataframe(pd.read_sql("SELECT * FROM customers", conn), use_container_width=True)

# --- 6. الديون ---
elif menu == "الديون":
    st.header("💸 الديون")
    with st.form("add_d"):
        name = st.text_input("اسم العميل")
        amount = st.number_input("المبلغ", step=1, min_value=0)
        note = st.text_input("ملاحظات")
        if st.form_submit_button("إضافة دين"):
            c.execute("INSERT INTO debts VALUES (?,?,?)", (name, int(amount), note))
            conn.commit()
            st.success("تمت إضافة الدين!")
    st.dataframe(pd.read_sql("SELECT * FROM debts", conn), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.write("المبرمج ياسر")
st.sidebar.write("مستمرين نحو الأفضل")
