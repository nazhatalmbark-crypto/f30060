import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import date
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# --- دالة ترتيب الحروف العربية ---
def fix_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- الإعدادات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- دالة التشفير ---
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔐 Eng. Yasser Pro System")
    st.subheader("مستمرين نحو الأفضل")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    c1, c2 = st.columns(2)
    if c1.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, hash_pw(pw)))
        if c.fetchone(): st.session_state.logged_in = True; st.rerun()
        else: st.error("خطأ!")
    if c2.button("دخول كزائر"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- الواجهة ---
st.title("Eng. Yasser Pro System ✨")
if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 عرض المخزن", "🧾 الفواتير", "👥 إدارة العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # البيع
    st.header("🛒 البيع والطلب")
    custs = pd.read_sql("SELECT name FROM customers", conn)
    selected_c = st.selectbox("اختر العميل", ["اختر..."] + custs['name'].tolist())
    
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    for idx, row in prods.iterrows():
        qty = st.number_input(f"{row['name']} (المتوفر: {row['quantity']})", min_value=0, step=1, format="%d", key=f"q_{idx}")
        if qty > 0:
            if 'cart' not in st.session_state: st.session_state.cart = {}
            st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
    
    if 'cart' in st.session_state and st.session_state.cart:
        if st.button("✅ إتمام البيع"):
            total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_c, str(st.session_state.cart), int(total), str(date.today()), "نقد"))
            for n, d in st.session_state.cart.items(): c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
            conn.commit(); st.session_state.cart = {}; st.success("تمت العملية! مستمرين نحو الأفضل"); st.rerun()

with tabs[1]: # عرض المخزن
    st.header("📦 عرض المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

with tabs[2]: # الفواتير
    st.header("🧾 سجل الفواتير")
    invs = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invs.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']}"):
            st.write(f"المجموع: {row['total']} د.ع")
            
            # --- كود الـ PDF العربي ---
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # تحويل النصوص للعربية
            cust_text = fix_arabic(f"العميل: {row['customer_name']}")
            total_text = fix_arabic(f"المجموع الكلي: {row['total']} دينار عراقي")
            
            pdf.cell(200, 10, txt=cust_text, ln=True, align='R')
            pdf.cell(200, 10, txt=total_text, ln=True, align='R')
            
            pdf_bytes = pdf.output()
            
            st.download_button(label="📥 تحميل الفاتورة PDF", data=pdf_bytes, file_name=f"invoice_{row['rowid']}.pdf")

with tabs[3]: # العملاء
    st.header("👥 إدارة العملاء")
    with st.form("add_cust"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم العميل"); phone = c2.text_input("رقم الهاتف")
        shop = c1.text_input("اسم المحل"); addr = c2.text_input("عنوان المحل")
        prov = c1.text_input("المحافظة")
        if st.form_submit_button("إضافة عميل"): 
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop, addr, prov)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tabs[4]: # المساعد الذكي
    st.header("🤖 المساعد الذكي - لوحة التحكم")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ إضافة مادة")
        with st.form("add_p"):
            n = st.text_input("اسم المادة"); p = st.number_input("السعر", step=1, format="%d"); q = st.number_input("الكمية", step=1, format="%d")
            if st.form_submit_button("إضافة"): c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()
    with col2:
        st.subheader("❌ حذف مادة")
        all_prods = pd.read_sql("SELECT name FROM products", conn)
        prod_del = st.selectbox("اختر المادة للحذف", all_prods['name'].tolist())
        if st.button("حذف المادة المحددة"):
            c.execute("DELETE FROM products WHERE name = ?", (prod_del,))
            conn.commit(); st.rerun()
    st.divider()
    st.subheader("📊 تقرير الجرد والتنبيهات")
    if st.button("تشغيل جرد المخزن"): st.table(pd.read_sql("SELECT * FROM products", conn))
    if st.button("فحص النواقص"):
        low = pd.read_sql("SELECT * FROM products WHERE quantity < 5", conn)
        if not low.empty: st.warning("مواد شارفت على النفاذ:"); st.table(low)
        else: st.success("المخزن مكتمل!")
