import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System Pro", layout="wide")

conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# تحديث الجداول لدعم نوع الدفع
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, shop_name TEXT, phone TEXT, items TEXT, total INTEGER, timestamp TEXT, payment_type TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, area TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS debts (customer_name TEXT, amount INTEGER, note TEXT)')
conn.commit()

# تنسيق CSS
st.markdown("""
    <style>
    .prod-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; text-align: center; margin: 10px; background-color: #f9f9f9; }
    .debt-row { background-color: #ffcccc !important; color: #cc0000; padding: 5px; border-radius: 5px; }
    .cash-row { background-color: #ffffcc !important; color: #888800; padding: 5px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("Eng. Yasser System")
menu = st.sidebar.radio("القائمة", ["سلة البيع", "إضافة مواد", "جرد المخزن", "أرشيف الفواتير", "العملاء", "لوحة التحكم"])

if 'cart' not in st.session_state: st.session_state.cart = []

# --- 1. واجهة البيع الاحترافية ---
if menu == "سلة البيع":
    st.header("🛒 سلة البيع")
    
    # عرض السلة في القائمة الجانبية
    st.sidebar.subheader("🛒 السلة")
    total_cart = sum(i['price'] for i in st.session_state.cart)
    st.sidebar.write(f"المجموع: {total_cart} د.ع")
    if st.sidebar.button("إتمام البيع"):
        st.session_state.checkout = True
    
    # شبكة المنتجات (Prost Style)
    products = pd.read_sql("SELECT * FROM products WHERE quantity > 0", conn)
    cols = st.columns(3)
    for i, row in products.iterrows():
        with cols[i % 3]:
            st.markdown(f"""
                <div class="prod-card">
                    <h4>{row['name']}</h4>
                    <p>السعر: {row['price']} د.ع</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"أضف {row['name']}", key=f"add_{i}"):
                st.session_state.cart.append({'name': row['name'], 'price': int(row['price'])})
                st.rerun()

    # نافذة إتمام البيع
    if 'checkout' in st.session_state and st.session_state.checkout:
        st.subheader("إتمام عملية البيع")
        cust_df = pd.read_sql("SELECT * FROM customers", conn)
        sel_name = st.selectbox("اختر الزبون", ["عام"] + cust_df['name'].tolist())
        pay_type = st.radio("نوع الدفع", ["نقد", "دين"])
        
        if st.button("تأكيد وحفظ الفاتورة"):
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?,?,?)", 
                      (sel_name, "N/A", "N/A", str(st.session_state.cart), total_cart, datetime.now().strftime("%Y-%m-%d"), pay_type))
            conn.commit()
            st.session_state.cart = []
            st.session_state.checkout = False
            st.success("تمت العملية بنجاح!")
            st.rerun()

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر"); q = st.text_input("الكمية")
        if st.form_submit_button("حفظ"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, int(p), int(q), 0))
            conn.commit()
            st.success("تم")

# --- 3. الأرشيف مع التلوين ---
elif menu == "أرشيف الفواتير":
    st.header("📜 الأرشيف")
    df = pd.read_sql("SELECT * FROM invoices", conn)
    for i, row in df.iterrows():
        color_class = "debt-row" if row['payment_type'] == "دين" else "cash-row"
        st.markdown(f"""
            <div class="{color_class}">
                <strong>الزبون:</strong> {row['customer_name']} | <strong>المبلغ:</strong> {row['total']} | <strong>النوع:</strong> {row['payment_type']}
            </div>
        """, unsafe_allow_html=True)
        st.write("---")

# (باقي الأقسام تبقى كما هي...)
elif menu == "جرد المخزن":
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    for _, row in products.iterrows():
        st.write(f"**{row['name']}** - الكمية: {row['quantity']}")
        if st.button("حذف", key=row['rowid']):
            c.execute("DELETE FROM products WHERE rowid=?", (row['rowid'],))
            conn.commit(); st.rerun()

elif menu == "العملاء":
    st.header("👥 العملاء")
    # (كود إضافة عملاء)
    
elif menu == "لوحة التحكم":
    st.header("📈 لوحة التحكم")
    st.write("المبرمج ياسر - مستمرين نحو الأفضل")
