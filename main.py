import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول (محدثة)
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER)')
# تم تحديث جدول الفواتير ليشمل بيانات المحل والهاتف
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, shop_name TEXT, phone TEXT, items TEXT, total INTEGER, timestamp TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, area TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS debts (customer_name TEXT, amount INTEGER, note TEXT)')
conn.commit()

st.sidebar.title("Eng. Yasser System")
menu = st.sidebar.radio("القائمة", ["سلة البيع", "إضافة مواد", "جرد المخزن", "أرشيف الفواتير", "العملاء", "الديون"])

if 'cart' not in st.session_state: st.session_state.cart = []

if menu == "سلة البيع":
    st.header("🛒 سلة البيع")
    
    if 'invoice_view' in st.session_state and st.session_state.invoice_view:
        # عرض الفاتورة بعد الحفظ
        inv = st.session_state.temp_invoice
        st.markdown("<div style='border: 2px solid #000; padding: 30px; background-color: white; color: black;'>", unsafe_allow_html=True)
        st.header("Eng. Yasser System")
        st.write(f"**الزبون:** {inv['name']} | **المحل:** {inv['shop']}")
        st.write(f"**هاتف:** {inv['phone']} | **التاريخ:** {inv['time']}")
        st.markdown("---")
        st.table(pd.DataFrame(st.session_state.cart))
        st.write(f"### المجموع الكلي: {sum(i['price'] for i in st.session_state.cart)} د.ع")
        st.markdown("---")
        st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("إغلاق الفاتورة"):
            st.session_state.invoice_view = False
            st.session_state.cart = []
            st.rerun()
    else:
        col1, col2 = st.columns([2, 1])
        products = pd.read_sql("SELECT * FROM products WHERE quantity > 0", conn)
        
        with col1:
            st.subheader("قائمة المواد")
            for _, row in products.iterrows():
                if st.button(f"إضافة {row['name']} ({row['price']})", key=f"add_{row['name']}"):
                    st.session_state.cart.append({'name': row['name'], 'price': int(row['price'])})
                    st.rerun()

        with col2:
            st.subheader("بيانات العميل")
            cust_name = st.text_input("اسم الزبون (مطلوب)")
            shop_name = st.text_input("اسم المحل")
            phone = st.text_input("رقم الهاتف")
            
            if st.session_state.cart:
                for i, item in enumerate(st.session_state.cart):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"{item['name']} - {item['price']}")
                    if c2.button("❌", key=f"del_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                
                if st.button("حفظ وإصدار الفاتورة"):
                    if not cust_name:
                        st.error("يرجى كتابة اسم العميل!")
                    else:
                        total = int(sum(i['price'] for i in st.session_state.cart))
                        c.execute("INSERT INTO invoices VALUES (?,?,?,?,?,?)", (cust_name, shop_name, phone, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        for item in st.session_state.cart:
                            c.execute("UPDATE products SET quantity = quantity - 1 WHERE name = ?", (item['name'],))
                        conn.commit()
                        st.session_state.temp_invoice = {'name': cust_name, 'shop': shop_name, 'phone': phone, 'time': datetime.now().strftime("%Y-%m-%d %H:%M")}
                        st.session_state.invoice_view = True
                        st.rerun()

# --- باقي الأقسام ---
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
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    for _, row in products.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"{row['name']} | السعر: {row['price']} | الكمية: {row['quantity']}")
        if c2.button(f"حذف", key=f"del_db_{row['rowid']}"):
            c.execute("DELETE FROM products WHERE rowid = ?", (row['rowid'],))
            conn.commit()
            st.rerun()

elif menu == "أرشيف الفواتير":
    st.header("📜 أرشيف الفواتير")
    # عرض الفاتورة
    if 'view_invoice' in st.session_state and st.session_state.view_invoice:
        inv = st.session_state.selected_inv
        st.markdown("<div style='border: 2px solid #000; padding: 30px; background-color: white; color: black;'>", unsafe_allow_html=True)
        st.header("Eng. Yasser System")
        st.write(f"**الزبون:** {inv['customer_name']} | **المحل:** {inv['shop_name']}")
        st.write(f"**هاتف:** {inv['phone']} | **التاريخ:** {inv['timestamp']}")
        st.markdown("---")
        st.write(f"{inv['items']}")
        st.write(f"### المجموع الكلي: {inv['total']} د.ع")
        st.markdown("---")
        st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("رجوع للأرشيف"):
            st.session_state.view_invoice = False
            st.rerun()
    else:
        invoices = pd.read_sql("SELECT rowid, * FROM invoices", conn)
        for _, row in invoices.iterrows():
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"{row['customer_name']} - {row['total']} د.ع - {row['timestamp']}")
            if c2.button("عرض", key=f"view_{row['rowid']}"):
                st.session_state.selected_inv = row
                st.session_state.view_invoice = True
                st.rerun()
            if c3.button("❌ حذف", key=f"del_inv_{row['rowid']}"):
                c.execute("DELETE FROM invoices WHERE rowid = ?", (row['rowid'],))
                conn.commit()
                st.rerun()

elif menu == "العملاء":
    st.header("👥 العملاء")
    with st.form("add_c"):
        name = st.text_input("اسم العميل")
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

st.sidebar.markdown("---")
st.sidebar.write("مستمرين نحو الأفضل")
