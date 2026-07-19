import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import ast
from datetime import date
from fpdf import FPDF

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
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, hash_pw(pw)))
        if c.fetchone(): st.session_state.logged_in = True; st.rerun()
        else: st.error("خطأ!")
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
    
    current_cart = {}
    for idx, row in prods.iterrows():
        qty = st.number_input(f"{row['name']} (المتوفر: {row['quantity']})", min_value=0, step=1, key=f"q_{idx}")
        if qty > 0:
            current_cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
    
    if current_cart:
        if st.button("✅ إتمام البيع"):
            total = sum(d['price'] * d['qty'] for d in current_cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_c, str(current_cart), int(total), str(date.today()), "نقد"))
            for n, d in current_cart.items(): 
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
            conn.commit(); st.success("تمت العملية بنجاح!"); st.rerun()

with tabs[1]: # عرض المخزن
    st.header("📦 عرض المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

with tabs[2]: # الفواتير
    st.header("🧾 سجل الفواتير")
    invs = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invs.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} - {row['customer_name']}"):
            items = ast.literal_eval(row['items'])
            st.table(pd.DataFrame(items).T)
            
            # إنشاء PDF بجدول مرتب
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="INVOICE", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Customer: {row['customer_name']}", ln=True)
            pdf.cell(200, 10, txt=f"Date: {row['date']}", ln=True)
            pdf.ln(10)
            
            # رأس الجدول
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(80, 10, "Item", border=1, fill=True)
            pdf.cell(30, 10, "Qty", border=1, fill=True)
            pdf.cell(40, 10, "Price", border=1, fill=True)
            pdf.cell(40, 10, "Total", border=1, fill=True, ln=True)
            
            # محتوى الجدول
            for item, data in items.items():
                qty = data['qty']
                price = data['price']
                total = qty * price
                pdf.cell(80, 10, str(item), border=1)
                pdf.cell(30, 10, str(qty), border=1)
                pdf.cell(40, 10, str(price), border=1)
                pdf.cell(40, 10, str(total), border=1, ln=True)
            
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(190, 10, txt=f"GRAND TOTAL: {row['total']} IQD", border=1, align='R')
            
            st.download_button(label="📥 تحميل الفاتورة PDF", data=pdf.output(), file_name=f"invoice_{row['rowid']}.pdf")

with tabs[3]: # العملاء
    st.header("👥 إدارة العملاء")
    with st.form("add_cust"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم العميل"); phone = c2.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة"): 
            c.execute("INSERT INTO customers (name, phone) VALUES (?,?)", (name, phone)); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tabs[4]: # المساعد الذكي
    st.header("🤖 المساعد الذكي - لوحة التحكم")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ إضافة مادة جديدة")
        with st.form("add_p", clear_on_submit=True):
            n = st.text_input("اسم المادة"); p = st.number_input("السعر", step=1); q = st.number_input("الكمية", step=1)
            if st.form_submit_button("حفظ المادة"): 
                c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.rerun()
    with col2:
        st.subheader("❌ حذف مادة")
        all_prods = pd.read_sql("SELECT name FROM products", conn)
        prod_del = st.selectbox("اختر المادة", all_prods['name'].tolist())
        if st.button("حذف"):
            c.execute("DELETE FROM products WHERE name = ?", (prod_del,))
            conn.commit(); st.rerun()
    
    st.divider()
    st.subheader("📊 جرد المخزن")
    if st.button("تحديث تقرير النواقص"):
        low = pd.read_sql("SELECT * FROM products WHERE quantity < 5", conn)
        if not low.empty: st.warning("مواد شارفت على النفاذ!"); st.table(low)
        else: st.success("المخزن مكتمل!")
    st.table(pd.read_sql("SELECT * FROM products", conn))
