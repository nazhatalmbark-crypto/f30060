import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import random

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

# --- دالة توليد لون عشوائي ---
def get_random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# --- نظام الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_color = get_random_color()

if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول إلى نظام المبرمج ياسر")
    tab1, tab2 = st.tabs(["تسجيل دخول", "مستخدم جديد"])
    
    with tab1:
        u = st.text_input("اسم المستخدم", key="login_u")
        p = st.text_input("كلمة المرور", type="password", key="login_p")
        if st.button("دخول"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else: st.error("بيانات غير صحيحة!")
            
    with tab2:
        nu = st.text_input("اسم مستخدم جديد")
        np = st.text_input("كلمة المرور", type="password")
        if st.button("إنشاء حساب"):
            try:
                c.execute("INSERT INTO users VALUES (?,?,?)", (nu, np, get_random_color()))
                conn.commit(); st.success("تم إنشاء الحساب! سجل دخول الآن")
            except: st.error("اسم المستخدم موجود مسبقاً!")
    st.stop()

# --- إذا تم تسجيل الدخول ---
st.sidebar.markdown(f"""
    <div style="background-color: {st.session_state.user_color}; padding: 20px; border-radius: 50%; width: 50px; height: 50px; text-align: center; color: white; font-weight: bold;">
    {st.session_state.username[0].upper()}
    </div>
    <h3>مرحباً، {st.session_state.username}</h3>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# --- القائمة ---
menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "العملاء", "جرد المخزن", "الفواتير", "التقارير"])

# --- 1. شاشة البيع ---
if menu == "شاشة البيع":
    st.header("🛒 شاشة البيع")
    
    # حل مشكلة التكرار (drop_duplicates)
    products = pd.read_sql("SELECT rowid, * FROM products", conn).drop_duplicates(subset=['name'])
    
    customers = pd.read_sql("SELECT name FROM customers", conn)
    selected_customer = st.selectbox("اختر العميل", customers['name'].tolist() if not customers.empty else ["عام"])
    
    cols = st.columns(3)
    for i, row in products.iterrows():
        with cols[i % 3]:
            st.write(f"**{row['name']}**")
            st.write(f"السعر: {row['price']} | المتوفر: {row['quantity']}")
            qty = st.number_input(f"الكمية {row['name']}", min_value=0, max_value=row['quantity'], key=f"q_{row['rowid']}")
            if qty > 0 and st.button(f"أضف {row['name']}", key=f"btn_{row['rowid']}"):
                if 'cart' not in st.session_state: st.session_state.cart = {}
                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty}
                st.rerun()

    if 'cart' in st.session_state and st.session_state.cart:
        st.subheader("الفاتورة")
        cart_df = pd.DataFrame.from_dict(st.session_state.cart, orient='index')
        st.table(cart_df)
        total = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
        st.write(f"### المجموع: {total} د.ع")
        pay_method = st.radio("طريقة الدفع", ["نقد", "دين"])
        if st.button("إتمام البيع"):
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d"), pay_method))
            for name, data in st.session_state.cart.items():
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(data['qty']), name))
            conn.commit(); st.session_state.cart = {}; st.success("تم!"); st.rerun()

# --- 5. الفواتير (ملونة) ---
elif menu == "الفواتير":
    st.header("🧾 سجل الفواتير")
    df = pd.read_sql("SELECT * FROM invoices ORDER BY date DESC", conn)
    
    # دالة تلوين الصفوف
    def color_rows(val):
        color = 'background-color: #90EE90' if val == 'نقد' else 'background-color: #FFC0CB'
        return color

    if not df.empty:
        # تلوين الجدول بناءً على عمود payment_method
        st.dataframe(df.style.map(color_rows, subset=['payment_method']))

# --- باقي الأقسام كما هي ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد")
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر"); q = st.text_input("الكمية")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, int(p), int(q), 0))
            conn.commit(); st.success("تم!")

elif menu == "العملاء":
    st.header("👥 العملاء")
    with st.form("add_c"):
        name = st.text_input("الاسم"); phone = st.text_input("الهاتف")
        shop = st.text_input("اسم المحل"); addr = st.text_input("العنوان"); prov = st.text_input("المحافظة")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop, addr, prov))
            conn.commit(); st.success("تم!")
    st.table(pd.read_sql("SELECT * FROM customers", conn))

elif menu == "جرد المخزن":
    st.table(pd.read_sql("SELECT * FROM products", conn))

elif menu == "التقارير":
    sales = pd.read_sql("SELECT * FROM invoices", conn)
    st.metric("إجمالي المبيعات", f"{sales['total'].sum() if not sales.empty else 0} د.ع")
