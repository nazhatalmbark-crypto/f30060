import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, timestamp TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, area TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS debts (customer_name TEXT, amount INTEGER, note TEXT)')
conn.commit()

st.sidebar.title("Eng. Yasser System")
menu = st.sidebar.radio("القائمة", ["سلة البيع", "إضافة مواد", "جرد المخزن", "أرشيف الفواتير", "العملاء", "الديون"])

if 'cart' not in st.session_state: st.session_state.cart = []

if menu == "سلة البيع":
    st.header("🛒 سلة البيع")
    
    # --- عرض الفاتورة ---
    if 'invoice_view' in st.session_state and st.session_state.invoice_view:
        st.markdown("<div style='border: 2px solid #000; padding: 30px; background-color: white; color: black;'>", unsafe_allow_html=True)
        st.header("Eng. Yasser System")
        st.write(f"**الزبون/المحل:** {st.session_state.temp_cust_name}")
        st.write(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.markdown("---")
        
        # تحويل السلة لجدول مفصل (اسم المادة، العدد، السعر، المجموع)
        df_cart = pd.DataFrame(st.session_state.cart)
        invoice_table = df_cart.groupby(['name', 'price']).size().reset_index(name='العدد')
        invoice_table['المجموع'] = invoice_table['price'] * invoice_table['العدد']
        
        st.table(invoice_table[['name', 'العدد', 'price', 'المجموع']])
        
        st.write(f"### المجموع الكلي: {invoice_table['المجموع'].sum()} د.ع")
        st.markdown("---")
        st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("إغلاق الفاتورة"):
            st.session_state.invoice_view = False
            st.session_state.cart = []
            st.rerun()
    else:
        # --- واجهة البيع ---
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
            cust_name = st.text_input("اسم الزبون/المحل")
            if st.session_state.cart:
                for i, item in enumerate(st.session_state.cart):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"{item['name']} - {item['price']}")
                    if c2.button("❌", key=f"del_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                
                if st.button("حفظ وإصدار الفاتورة"):
                    total = int(sum(i['price'] for i in st.session_state.cart))
                    c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (cust_name, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    for item in st.session_state.cart:
                        c.execute("UPDATE products SET quantity = quantity - 1 WHERE name = ?", (item['name'],))
                    conn.commit()
                    st.session_state.temp_cust_name = cust_name
                    st.session_state.invoice_view = True
                    st.rerun()

# --- باقي الأقسام كما هي ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد جديدة")
    with st.form("add_p"):
        name = st.text_input("اسم المادة")
        price = st.number_input("السعر", step=1, min_value=0)
        qty = st.number_input("الكمية", step=1, min_value=0)
        if st.form_submit_button("حفظ"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (name, int(price), int(qty)))
            conn.commit()
            st.success("تم!")

elif menu == "جرد المخزن":
    st.header("📊 جرد المخزن")
    products = pd.read_sql("SELECT * FROM products", conn)
    for _, row in products.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"{row['name']} | السعر: {row['price']} | الكمية: {row['quantity']}")
        if c2.button(f"حذف", key=f"del_db_{row['name']}"):
            c.execute("DELETE FROM products WHERE name = ?", (row['name'],))
            conn.commit()
            st.rerun()

elif menu == "أرشيف الفواتير":
    st.header("📜 أرشيف الفواتير")
    st.dataframe(pd.read_sql("SELECT * FROM invoices", conn), use_container_width=True)

elif menu == "العملاء":
    st.header("👥 العملاء")
    with st.form("add_c"):
        name = st.text_input("اسم العميل/المحل")
        phone = st.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers (name, phone) VALUES (?,?)", (name, phone))
            conn.commit()
            st.success("تم!")
    st.dataframe(pd.read_sql("SELECT * FROM customers", conn), use_container_width=True)

elif menu == "الديون":
    st.header("💸 الديون")
    with st.form("add_d"):
        name = st.text_input("اسم العميل")
        amount = st.number_input("المبلغ", step=1, min_value=0)
        note = st.text_input("ملاحظات")
        if st.form_submit_button("إضافة دين"):
            c.execute("INSERT INTO debts VALUES (?,?,?)", (name, int(amount), note))
            conn.commit()
            st.success("تم!")
    st.dataframe(pd.read_sql("SELECT * FROM debts", conn), use_container_width=True)
