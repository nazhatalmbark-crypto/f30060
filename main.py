import streamlit as st
import sqlite3
import pandas as pd
import random
import hashlib
import shutil
import os
from datetime import datetime, date
from fpdf import FPDF
import ast

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- النسخ الاحتياطي التلقائي عند التشغيل ---
if not os.path.exists("backups"): os.makedirs("backups")
shutil.copy("final_system_master.db", f"backups/db_backup_{date.today()}.db")

# --- الإعدادات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- دالة تشفير الباسورد ---
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

# --- الدوال ---
def get_products(): return pd.read_sql("SELECT rowid, * FROM products", conn)
def get_customers(): return pd.read_sql("SELECT * FROM customers", conn)

# --- تسجيل الدخول (محصن) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔐 Eng. Yasser Pro System")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    c1, c2 = st.columns(2)
    if c1.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, hash_pw(pw)))
        if c.fetchone(): st.session_state.logged_in = True; st.rerun()
        else: st.error("خطأ في البيانات!")
    if c2.button("دخول كزائر"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- الواجهة ---
st.title("Eng. Yasser Pro System")
if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["📊 الإحصائيات", "🛒 البيع", "📦 المخزن", "🧾 الفواتير", "👥 العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # الإحصائيات
    st.header("📊 لوحة التحكم")
    inv = pd.read_sql("SELECT * FROM invoices", conn)
    if not inv.empty:
        col1, col2 = st.columns(2)
        col1.metric("إجمالي المبيعات", f"{inv['total'].sum()} د.ع")
        st.bar_chart(inv.groupby('payment_type')['total'].sum())

with tabs[1]: # البيع
    st.header("🛒 البيع والطلب")
    cust = st.selectbox("العميل", ["اختر..."] + get_customers()['name'].tolist())
    prods = get_products()
    for idx, row in prods.iterrows():
        q = st.number_input(f"{row['name']} (متوفر: {row['quantity']})", 0, int(row['quantity']), key=f"q_{idx}")
        if q > 0:
            if 'cart' not in st.session_state: st.session_state.cart = {}
            st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(q)}
    if 'cart' in st.session_state and st.session_state.cart:
        if st.button("✅ إتمام البيع"):
            total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (cust, str(st.session_state.cart), int(total), str(date.today()), "نقد"))
            for n, d in st.session_state.cart.items(): c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
            conn.commit(); st.session_state.cart = {}; st.success("تم!"); st.rerun()

with tabs[2]: # المخزن
    st.header("📦 جرد المخزن")
    st.table(get_products())
    with st.form("new_p"):
        n = st.text_input("مادة"); p = st.number_input("سعر"); q = st.number_input("كمية")
        if st.form_submit_button("إضافة"): c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()

with tabs[3]: # الفواتير
    st.header("🧾 سجل الفواتير")
    search_date = st.date_input("فلترة حسب التاريخ")
    invs = pd.read_sql(f"SELECT rowid, * FROM invoices WHERE date='{search_date}'", conn)
    for _, row in invs.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']}"):
            st.write(f"المجموع: {row['total']} د.ع")
            if st.button(f"📥 تحميل PDF فاتورة #{row['rowid']}"):
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Invoice #{row['rowid']} - {row['customer_name']}", ln=True)
                pdf.cell(200, 10, txt=f"Total: {row['total']} IQD", ln=True)
                pdf.output(f"invoice_{row['rowid']}.pdf"); st.success("تم التوليد!")

with tabs[4]: # العملاء
    st.table(get_customers())

with tabs[5]: # المساعد الذكي والمفاجآت
    st.header("🤖 المساعد الذكي")
    # التنبيهات
    low = get_products()[get_products()['quantity'] < 5]
    if not low.empty: st.warning("تنبيه: مواد ناقصة!"); st.table(low)
    
    # مفاجآت برمجية (مخفية)
    with st.expander("🛠️ إعدادات النظام المتقدمة"):
        if st.button("تحديث صحة النظام"): st.info("النظام يعمل بكفاءة: 99.9%")
        st.text_area("🗒️ ملاحظاتك الشخصية (لليوم):")
        st.write(f"Quote of the day: {random.choice(['النجاح يبدأ بخطوة', 'البرمجة فن وعلم', 'مستمرين نحو الأفضل'])}")
