import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- الإعدادات ---
DB_NAME = 'final_system_pro.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        if c.fetchone(): st.session_state.logged_in = True; st.rerun()
        else: st.error("خطأ!")
    st.stop()

st.title("⚙️ نظام المبرمج ياسر")
if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 المخزن", "🧾 الفواتير", "👥 العملاء"])

with tabs[0]: # البيع
    cust_list = ["اختر عميل..."] + pd.read_sql("SELECT name FROM customers", conn)['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_list)
    p_type = st.radio("نوع الدفع", ["نقد", "أقساط"])
    
    prods = pd.read_sql("SELECT * FROM products", conn)
    for idx, row in prods.iterrows():
        qty = st.number_input(f"{row['name']} (المتوفر: {row['quantity']})", 0, int(row['quantity']), key=f"q_{idx}")
        if qty > 0:
            if st.button(f"➕ أضف {row['name']}", key=f"btn_{idx}"):
                if 'cart' not in st.session_state: st.session_state.cart = {}
                st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
                st.rerun()

    if 'cart' in st.session_state and st.session_state.cart:
        st.subheader("🛒 السلة")
        if st.button("✅ إتمام البيع"):
            if selected_customer == "اختر عميل...": st.error("يجب اختيار عميل!")
            else:
                total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), p_type))
                for n, d in st.session_state.cart.items():
                    c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
                conn.commit(); st.session_state.cart = {}; st.success("تم البيع!"); st.rerun()

with tabs[1]: # المخزن
    st.header("📊 جرد المخزن")
    data = pd.read_sql("SELECT rowid, * FROM products", conn)
    for _, row in data.iterrows():
        c1, c2 = st.columns([0.8, 0.2])
        c1.write(f"🔹 **{row['name']}** | السعر: {row['price_carton']} | المتوفر: {row['quantity']}")
        if c2.button("🗑️ حذف", key=f"d_{row['rowid']}"):
            c.execute("DELETE FROM products WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tabs[2]: # الفواتير (عرض مباشر)
    st.header("🧾 سجل الفواتير")
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']}"):
            # جلب معلومات العميل
            cust_info = c.execute("SELECT * FROM customers WHERE name=?", (row['customer_name'],)).fetchone()
            
            # --- تصميم الفاتورة ---
            st.markdown("---")
            st.markdown(f"### 🏢 {cust_info[2] if cust_info else 'محل المبيعات'}") # اسم المحل
            st.write(f"العميل: {row['customer_name']} | الهاتف: {cust_info[1] if cust_info else 'غير متوفر'}")
            st.write(f"العنوان: {cust_info[3] if cust_info else ''}, {cust_info[4] if cust_info else ''}")
            st.markdown("---")
            
            # جدول المواد
            items = ast.literal_eval(row['items'])
            st.table(pd.DataFrame(items).T)
            
            # المجموع والعبارة
            st.markdown(f"### المجموع الكلي: {row['total']} دينار")
            st.markdown(f"**طريقة الدفع:** {row['payment_type']}")
            st.info("💡 ملاحظة: بضاعة المباعة لا ترد ولا تستبدل، شكراً لتعاملكم معنا") # <--- العبارة هنا
            st.markdown("---")
            
            if st.button(f"🗑️ حذف الفاتورة", key=f"del_{row['rowid']}"):
                c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tabs[3]: # العملاء
    with st.form("add_c", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم العميل")
        phone = c2.text_input("رقم الهاتف")
        shop = c1.text_input("اسم المحل")
        addr = c2.text_input("العنوان")
        prov = c1.text_input("المحافظة")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop, addr, prov)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))
