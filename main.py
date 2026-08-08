import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="Prosto - إدارة المبيعات", page_icon="🛍️", layout="wide")

# --- تنسيق الألوان (CSS) ---
st.markdown("""
<style>
    div.stButton > button { background-color: #1a6b51; color: white; border-radius: 8px; border: none; }
    div.stButton > button:hover { background-color: #14523e; }
    .stTabs [data-baseweb="tab"] { background-color: #e6f2ee; border-radius: 8px; color: #1a6b51; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# العبارة المطلوبة
st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>« أسعد نفسك بنفسك - مستمرون نحو الأفضل »</h2>", unsafe_allow_html=True)

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    price REAL DEFAULT 0,
                    quantity INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    debt REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT,
                    total REAL,
                    date TEXT)''')
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute(query, params)
    data = None
    if fetch: data = c.fetchall()
    conn.commit()
    conn.close()
    return data

# --- المساعد الذكي f30060 ---
st.sidebar.markdown("### 🤖 المساعد الذكي f30060")
with st.sidebar.expander("لوحة تحكم f30060"):
    user_ai = st.text_area("الأمر (إضافة أو جرد):", help="للإضافة: اسم,عدد,سعر | للجرد: جرد")
    if st.button("تنفيذ 🚀"):
        if "جرد" in user_ai:
            p_res = run_query("SELECT name, quantity, price FROM products", fetch=True)
            report = f"📋 تقرير الجرد الكامل\nالتاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n--------------------------\n"
            if p_res:
                for pr in p_res:
                    report += f"🔹 {pr[0]}: {pr[1]} قطعة | بسعر {pr[2]} دينار\n"
            else:
                report += "المخزن فارغ حالياً."
            st.text_area("التقرير:", value=report, height=200)
        elif "," in user_ai:
            lines = user_ai.split('\n')
            for line in lines:
                if "," in line:
                    parts = line.split(',')
                    if len(parts) == 3:
                        name, qty, price = parts[0].strip(), int(parts[1].strip()), float(parts[2].strip())
                        exists = run_query("SELECT quantity FROM products WHERE name = ?", (name,), fetch=True)
                        if exists:
                            new_qty = exists[0][0] + qty
                            run_query("UPDATE products SET quantity = ?, price = ? WHERE name = ?", (new_qty, price, name))
                            st.success(f"تم تحديث {name} (+{qty})")
                        else:
                            run_query("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
                            st.success(f"تمت إضافة {name} للمخزن!")

# القائمة الرئيسية المكتملة بكل الأقسام
menu = st.sidebar.radio("القائمة الرئيسية", ["🏪 المبيعات", "📦 إدارة المخزون", "📊 التقارير والأرباح", "👥 العملاء والديون"])

# --- 1. شاشة المبيعات ---
if menu == "🏪 المبيعات":
    if 'cart' not in st.session_state: st.session_state.cart = []
    tab1, tab2, tab3, tab4 = st.tabs(["شاشة البيع", "الفواتير", "العملاء", "مرتجعات الفواتير"])
    
    with tab1:
        search = st.text_input("🔍 ابحث باسم المنتج ...")
        products = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
        if products:
            cols = st.columns(2)
            for i, prod in enumerate(products):
                if search.lower() in prod[1].lower():
                    with cols[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"**{prod[1]}**")
                            st.write(f"💰 {prod[2]} دينار &nbsp; | &nbsp; 📦 {prod[3]} قطعة")
                            if st.button(f"إضافة {prod[1]}", key=f"add_{prod[0]}"):
                                st.session_state.cart.append({'id': prod[0], 'name': prod[1], 'price': prod[2]})
                                st.rerun()
        else:
            st.info("لا توجد منتجات حالياً. استخدم المساعد الذكي f30060 للإضافة.")

    with tab2:
        st.subheader("🧾 الفواتير السابقة")
        invs = run_query("SELECT id, customer_name, total, date FROM invoices ORDER BY id DESC", fetch=True)
        if invs:
            st.dataframe(pd.DataFrame(invs, columns=["رقم الفاتورة", "العميل", "المبلغ الكلي", "التاريخ"]), use_container_width=True)
        else:
            st.info("لا توجد فواتير مسجلة.")

    with tab3:
        st.subheader("👥 العملاء")
        custs = run_query("SELECT id, name, phone, debt FROM customers", fetch=True)
        if custs:
            st.dataframe(pd.DataFrame(custs, columns=["ID", "الاسم", "الهاتف", "الدين"]), use_container_width=True)
        else:
            st.info("لا توجد عملاء مسجلين.")

    with tab4:
        st.subheader("↩️ مرتجعات الفواتير")
        st.info("قريباً...")

    # السلة في القائمة الجانبية
    with st.sidebar.expander("🛒 سلة المشتريات"):
        total = sum(i['price'] for i in st.session_state.cart)
        for idx, item in enumerate(st.session_state.cart):
            st.write(f"{item['name']} - {item['price']} دينار")
        st.write(f"### المجموع: {total} دينار")
        cust_input = st.text_input("اسم العميل للفاتورة:")
        if st.button("تأكيد البيع وطباعة الفاتورة"):
            if cust_input and st.session_state.cart:
                for item in st.session_state.cart:
                    run_query("UPDATE products SET quantity = quantity - 1 WHERE id = ?", (item['id'],))
                run_query("INSERT INTO invoices (customer_name, total, date) VALUES (?, ?, ?)", 
                          (cust_input, total, datetime.now().strftime("%Y-%m-%d %H:%M")))
                st.session_state.cart = []
                st.success("تم تثبيت الفاتورة بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم العميل ووضع منتجات بالسلة.")

# --- 2. إدارة المخزون ---
elif menu == "📦 إدارة المخزون":
    st.title("📦 إدارة المخزون")
    prods = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
    if prods:
        st.dataframe(pd.DataFrame(prods, columns=["ID", "اسم المنتج", "السعر", "العدد"]), use_container_width=True)
    else:
        st.info("المخزن فارغ.")

# --- 3. التقارير والأرباح ---
elif menu == "📊 التقارير والأرباح":
    st.title("📊 التقارير والأرباح والفواتير")
    invs = run_query("SELECT id, customer_name, total, date FROM invoices", fetch=True)
    if invs:
        st.dataframe(pd.DataFrame(invs, columns=["رقم الفاتورة", "العميل", "المجموع", "التاريخ"]), use_container_width=True)
    else:
        st.info("لا توجد تقارير أو فواتير مسجلة.")

# --- 4. العملاء والديون ---
elif menu == "👥 العملاء والديون":
    st.title("👥 العملاء والديون")
    custs = run_query("SELECT id, name, phone, debt FROM customers", fetch=True)
    if custs:
        st.dataframe(pd.DataFrame(custs, columns=["ID", "الاسم", "الهاتف", "الدين"]), use_container_width=True)
    else:
        st.info("لا توجد ديون مسجلة للعملاء.")
