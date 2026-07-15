import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, color TEXT)')
conn.commit()

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- نظام الدخول ---
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
        else: st.error("بيانات غير صحيحة")
    st.stop()

# --- القائمة الجانبية ---
with st.sidebar:
    st.subheader(f"مرحباً {st.session_state.username}")
    menu = st.radio("القائمة", ["شاشة البيع", "إضافة مواد", "العملاء", "جرد المخزن", "الفواتير"])

# --- شاشة البيع ---
if menu == "شاشة البيع":
    st.header("🛒 شاشة البيع")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_options = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer_name = st.selectbox("🔎 ابحث عن العميل", cust_options)

    if selected_customer_name != "اختر عميل...":
        cust_data = cust_df[cust_df['name'] == selected_customer_name].iloc[0]
        st.success(f"العميل: {cust_data['name']} | هاتف: {cust_data['phone']} | محل: {cust_data['shop_name']}")

    st.divider()
    # جلب المنتجات مع حذف التكرار
    products_df = pd.read_sql("SELECT rowid, * FROM products", conn).drop_duplicates(subset=['name'])
    
    cols = st.columns(3)
    for i, row in products_df.iterrows():
        with cols[i % 3]:
            st.write(f"**{row['name']}**")
            st.caption(f"المتوفر: {row['quantity']} | السعر: {row['price']}")
            qty_input = st.number_input(f"الكمية", min_value=1, max_value=int(row['quantity']), key=f"inp_{row['rowid']}")
            if st.button(f"➕ أضف {row['name']}", key=f"btn_{row['rowid']}"):
                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty_input}
                st.rerun()

    # الفاتورة
    if st.session_state.cart:
        st.divider()
        st.subheader("📝 الفاتورة")
        for item, data in list(st.session_state.cart.items()):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔹 {item} | {data['qty']} × {data['price']} = {data['qty']*data['price']} د.ع")
            if c2.button("❌", key=f"del_{item}"):
                del st.session_state.cart[item]
                st.rerun()

        total = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
        st.write(f"### المجموع الكلي: {total} د.ع")
        pay_method = st.radio("طريقة الدفع", ["نقد", "دين"], horizontal=True)

        if st.button("✅ إتمام البيع"):
            if selected_customer_name == "اختر عميل...":
                st.error("⚠️ يرجى اختيار العميل أولاً!")
            else:
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", 
                          (selected_customer_name, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), pay_method))
                for name, data in st.session_state.cart.items():
                    c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(data['qty']), name))
                conn.commit(); st.session_state.cart = {}; st.success("تم البيع بنجاح!"); st.rerun()

# --- باقي الصفحات ---
elif menu == "إضافة مواد":
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر", 0); q = st.number_input("الكمية", 0)
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, p, q, 0)); conn.commit(); st.success("تم!")

elif menu == "العملاء":
    with st.form("add_c"):
        n = st.text_input("اسم العميل"); ph = st.text_input("رقم الهاتف"); s = st.text_input("اسم المحل"); a = st.text_input("العنوان")
        if st.form_submit_button("إضافة عميل"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (n, ph, s, a, "البصرة")); conn.commit(); st.success("تم!")
    st.table(pd.read_sql("SELECT * FROM customers", conn))

elif menu == "جرد المخزن":
    st.table(pd.read_sql("SELECT * FROM products", conn))

elif menu == "الفواتير":
    st.header("🧾 سجل الفواتير")
    df = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY date DESC", conn)
    
    # تنسيق الألوان
    def color_row(row):
        color = '#d4edda' if row['payment_method'] == 'نقد' else '#f8d7da'
        return [f'background-color: {color}'] * len(row)
    
    st.dataframe(df.style.apply(color_row, axis=1), use_container_width=True)
    
    # عرض الفاتورة
    st.divider()
    st.subheader("🔍 خيارات الفواتير")
    col1, col2 = st.columns(2)
    
    with col1:
        inv_id_view = st.number_input("رقم الفاتورة للعرض (rowid):", min_value=1, step=1, key="view")
        if st.button("عرض الفاتورة"):
            c.execute("SELECT * FROM invoices WHERE rowid=?", (inv_id_view,))
            inv = c.fetchone()
            if inv:
                st.info(f"العميل: {inv[0]} | التاريخ: {inv[3]} | الحالة: {inv[4]}")
                st.write(inv[1])
            else: st.error("غير موجودة!")

    with col2:
        inv_id_del = st.number_input("رقم الفاتورة للحذف (rowid):", min_value=1, step=1, key="del")
        if st.button("❌ حذف الفاتورة"):
            c.execute("DELETE FROM invoices WHERE rowid=?", (inv_id_del,))
            conn.commit()
            st.success("تم حذف الفاتورة!")
            st.rerun()
