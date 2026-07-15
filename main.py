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
c.execute('CREATE TABLE IF NOT EXISTS purchases (item_name TEXT, quantity INTEGER, total INTEGER, supplier TEXT, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS expenses (description TEXT, amount INTEGER, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, timestamp TEXT, payment_type TEXT)')
conn.commit()

# --- CSS للتصميم الاحترافي (شكل البروست) ---
st.markdown("""
    <style>
    .header-box { background-color: #1a4d2e; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    .prod-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #fff; text-align: center; margin: 10px; box-shadow: 2px 2px 5px #ccc; }
    .invoice-box { border: 2px solid #333; padding: 20px; border-radius: 10px; background-color: #fff; max-width: 400px; margin: auto; }
    </style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = []
if 'checkout_mode' not in st.session_state: st.session_state.checkout_mode = False

# --- القائمة الجانبية ---
st.sidebar.title("النظام")
menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "المشتريات", "المصروفات", "التقارير"])
st.sidebar.markdown("---")
st.sidebar.write("**المبرمج ياسر - مستمرين نحو الأفضل**")

# --- 1. شاشة البيع (شكل البروست) ---
if menu == "شاشة البيع":
    st.markdown('<div class="header-box"><h2>🛒 إدارة المبيعات</h2></div>', unsafe_allow_html=True)
    
    # السلة العلوية
    col_h1, col_h2 = st.columns([4, 1])
    with col_h2:
        if st.button(f"🛒 السلة ({len(st.session_state.cart)})"):
            if len(st.session_state.cart) > 0: st.session_state.checkout_mode = True
    
    # البحث
    search = st.text_input("🔍 ابحث عن مادة...", "")
    
    # وضع الفاتورة
    if st.session_state.checkout_mode:
        st.markdown('<div class="invoice-box">', unsafe_allow_html=True)
        st.header("الفاتورة")
        for item in st.session_state.cart: st.write(f"{item['name']} - {item['price']} د.ع")
        total = sum(i['price'] for i in st.session_state.cart)
        st.write(f"### المجموع: {total} د.ع")
        if st.button("تأكيد وحفظ"):
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", ("عام", str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d"), "نقد"))
            conn.commit(); st.session_state.cart = []; st.session_state.checkout_mode = False; st.rerun()
        st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # عرض المنتجات (Grid 2 columns)
        query = "SELECT rowid, * FROM products WHERE quantity > 0"
        if search: query += f" AND name LIKE '%{search}%'"
        products = pd.read_sql(query, conn)
        
        cols = st.columns(2)
        for i, row in products.iterrows():
            with cols[i % 2]:
                st.markdown(f'<div class="prod-card"><h4>{row["name"]}</h4><p>{row["price"]} د.ع</p></div>', unsafe_allow_html=True)
                if st.button(f"إضافة {row['name']}", key=f"add_{row['rowid']}"):
                    st.session_state.cart.append({'name': row['name'], 'price': int(row['price'])})
                    st.rerun()

# --- 2. باقي الأقسام (إضافة مواد، مشتريات، تقارير) ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد")
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر", value=0)
        q = st.number_input("الكمية", value=0); cp = st.number_input("سعر الشراء", value=0)
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, p, q, cp))
            conn.commit(); st.success("تم!")

elif menu == "المشتريات":
    st.header("📦 المشتريات")
    with st.form("add_pur"):
        i = st.text_input("اسم المادة"); q = st.number_input("الكمية"); t = st.number_input("المبلغ")
        if st.form_submit_button("حفظ"):
            c.execute("INSERT INTO purchases VALUES (?,?,?,?,?)", (i, q, t, "مورد", datetime.now().strftime("%Y-%m-%d")))
            conn.commit(); st.success("تم")

elif menu == "المصروفات":
    st.header("💸 المصروفات")
    with st.form("exp"):
        d = st.text_input("السبب"); a = st.number_input("المبلغ")
        if st.form_submit_button("تسجيل"):
            c.execute("INSERT INTO expenses VALUES (?,?,?)", (d, a, datetime.now().strftime("%Y-%m-%d")))
            conn.commit(); st.success("تم")

elif menu == "التقارير":
    st.header("📈 التقارير والأرباح")
    sales = pd.read_sql("SELECT * FROM invoices", conn)
    purchases = pd.read_sql("SELECT * FROM purchases", conn)
    expenses = pd.read_sql("SELECT * FROM expenses", conn)
    
    st.metric("إجمالي المبيعات", f"{sales['total'].sum() if not sales.empty else 0}")
    st.write("---")
    st.write("المبرمج ياسر - مستمرين نحو الأفضل")
    if not sales.empty: st.line_chart(sales['total'])
