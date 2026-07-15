import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- تنسيق CSS لجعل الواجهة تشبه التطبيق ---
st.markdown("""
    <style>
    .invoice-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .badge-price {
        padding: 5px 15px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        display: inline-block;
    }
    .badge-name {
        background-color: #d4edda;
        color: #155724;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_method TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, color TEXT)')
conn.commit()

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول")
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        if c.fetchone(): st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- القوائم العلوية (مثل التطبيق) ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 شاشة البيع", "🧾 الفواتير", "👥 العملاء", "📦 المخزن"])

with tab1:
    st.header("🛒 شاشة البيع")
    # (نفس منطق البيع السابق)
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_options = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 ابحث عن العميل", cust_options)
    
    products_df = pd.read_sql("SELECT rowid, * FROM products", conn).drop_duplicates(subset=['name'])
    cols = st.columns(3)
    for i, row in products_df.iterrows():
        with cols[i % 3]:
            st.write(f"**{row['name']}**")
            qty_input = st.number_input(f"الكمية", min_value=1, max_value=int(row['quantity']), key=f"inp_{row['rowid']}")
            if st.button(f"➕ أضف {row['name']}", key=f"btn_{row['rowid']}"):
                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty_input}
                st.rerun()
    
    if st.session_state.cart:
        if st.button("✅ إتمام البيع"):
            if selected_customer == "اختر عميل...": st.error("اختر عميلاً!")
            else:
                total = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), "نقد"))
                conn.commit(); st.session_state.cart = {}; st.rerun()

with tab2:
    st.header("🧾 الفواتير")
    df = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    
    for i, row in df.iterrows():
        # تحديد لون السعر حسب نوع الدفع
        price_color = "#ffc107" if row['payment_method'] == 'نقد' else "#dc3545"
        
        # رسم البطاقة (Card)
        st.markdown(f"""
            <div class="invoice-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="badge-price" style="background-color: {price_color};">{row['total']} دينار</span>
                        <h4 style="margin:5px 0;">فاتورة #{row['rowid']}</h4>
                    </div>
                    <div class="badge-name">{row['customer_name']}</div>
                </div>
                <p style="margin-top:10px;">التاريخ: {row['date']} | الدفع: {row['payment_method']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # أزرار تحكم تحت كل بطاقة
        c1, c2 = st.columns(2)
        if c1.button(f"👁️ عرض #{row['rowid']}", key=f"view_{row['rowid']}"):
            st.info(f"المواد: {row['items']}")
        if c2.button(f"🗑️ حذف #{row['rowid']}", key=f"del_{row['rowid']}"):
            c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],))
            conn.commit(); st.rerun()

with tab3:
    st.header("👥 إضافة عملاء")
    with st.form("add_c"):
        n = st.text_input("اسم العميل"); ph = st.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (n, ph, "", "", "")); conn.commit(); st.rerun()

with tab4:
    st.header("📦 المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))
