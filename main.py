import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# إعداد قاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول (هيكل ثابت ومستقر)
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS purchases (item_name TEXT, quantity INTEGER, total INTEGER, supplier TEXT, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS expenses (description TEXT, amount INTEGER, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, timestamp TEXT, payment_type TEXT)')
conn.commit()

# --- CSS للتصميم الاحترافي ---
st.markdown("""
    <style>
    .header-box { background-color: #1a4d2e; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;}
    .prod-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #fff; text-align: center; margin: 10px; box-shadow: 2px 2px 5px #ccc; }
    .invoice-box { border: 2px solid #333; padding: 20px; border-radius: 10px; background-color: #fff; max-width: 500px; margin: auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = []
if 'checkout_mode' not in st.session_state: st.session_state.checkout_mode = False

# --- القائمة الجانبية ---
st.sidebar.title("النظام")
menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "المشتريات", "المصروفات", "التقارير"])
st.sidebar.markdown("---")
st.sidebar.write("**المبرمج ياسر - مستمرين نحو الأفضل**")

# --- 1. شاشة البيع (نظام الاختيار المتعدد) ---
if menu == "شاشة البيع":
    st.markdown('<div class="header-box"><h2>🛒 إدارة المبيعات</h2></div>', unsafe_allow_html=True)
    
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    
    # اختيار متعدد
    selected_indices = []
    cols = st.columns(3)
    
    for i, row in products.iterrows():
        with cols[i % 3]:
            st.markdown(f'<div class="prod-card"><h4>{row["name"]}</h4><p>{row["price"]} د.ع</p></div>', unsafe_allow_html=True)
            if st.checkbox(f"تحديد {row['name']}", key=f"check_{row['rowid']}"):
                selected_indices.append(row)

    if st.button("إضافة المحددين للسلة"):
        for item in selected_indices:
            st.session_state.cart.append({'name': item['name'], 'price': int(item['price'])})
        st.success(f"تمت إضافة {len(selected_indices)} منتجات للسلة!")
        st.rerun()

    # السلة
    if st.button(f"🛒 السلة ({len(st.session_state.cart)})"):
        st.session_state.checkout_mode = True
        st.rerun()

    if st.session_state.checkout_mode:
        st.markdown('<div class="invoice-box">', unsafe_allow_html=True)
        st.header("الفاتورة")
        total = 0
        for item in st.session_state.cart: 
            st.write(f"{item['name']} - {item['price']} د.ع")
            total += item['price']
        st.write(f"### المجموع: {total} د.ع")
        if st.button("تأكيد وحفظ"):
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", ("عام", str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d"), "نقد"))
            conn.commit(); st.session_state.cart = []; st.session_state.checkout_mode = False; st.rerun()
        st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد")
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر")
        q = st.text_input("الكمية"); cp = st.text_input("سعر الشراء")
        if st.form_submit_button("إضافة"):
            if n and p.isdigit() and q.isdigit() and cp.isdigit():
                c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, int(p), int(q), int(cp)))
                conn.commit(); st.success("تم!")
            else: st.error("خطأ في البيانات!")

# --- 3. المشتريات والمصروفات ---
elif menu == "المشتريات":
    st.header("📦 المشتريات")
    with st.form("pur"):
        i = st.text_input("المادة"); q = st.text_input("الكمية"); t = st.text_input("المبلغ")
        if st.form_submit_button("حفظ"):
            c.execute("INSERT INTO purchases VALUES (?,?,?,?,?)", (i, int(q), int(t), "مورد", datetime.now().strftime("%Y-%m-%d")))
            conn.commit(); st.success("تم")

elif menu == "المصروفات":
    st.header("💸 المصروفات")
    with st.form("exp"):
        d = st.text_input("السبب"); a = st.text_input("المبلغ")
        if st.form_submit_button("تسجيل"):
            c.execute("INSERT INTO expenses VALUES (?,?,?)", (d, int(a), datetime.now().strftime("%Y-%m-%d")))
            conn.commit(); st.success("تم")

# --- 4. التقارير ---
elif menu == "التقارير":
    st.header("📈 التقارير")
    st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
    sales = pd.read_sql("SELECT * FROM invoices", conn)
    st.metric("إجمالي المبيعات", f"{sales['total'].sum() if not sales.empty else 0}")
