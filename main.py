import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- إعداد قاعدة البيانات ---
DB_NAME = 'system_v_final.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- دالة PDF ---
def get_pdf_bytes(invoice_id, customer_name, items, total, p_type):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="فاتورة مبيعات - نظام المبرمج ياسر", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"العميل: {customer_name}", ln=True)
    pdf.cell(200, 10, txt=f"نوع الدفع: {p_type}", ln=True)
    pdf.cell(200, 10, txt=f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(10)
    for item, data in items.items():
        pdf.cell(200, 10, txt=f"{item} | الكمية: {int(data['qty'])} | السعر: {int(data['price'])}", ln=True)
    pdf.cell(200, 10, txt=f"المجموع الكلي: {int(total)}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول")
    choice = st.radio("العملية:", ["تسجيل دخول", "حساب جديد"])
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("تنفيذ"):
        if choice == "حساب جديد":
            try:
                c.execute("INSERT INTO users VALUES (?,?)", (user, pw))
                conn.commit(); st.success("تم الإنشاء!")
            except: st.error("المستخدم موجود!")
        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
            if c.fetchone(): st.session_state.logged_in = True; st.rerun()
            else: st.error("خطأ في البيانات!")
    st.stop()

# --- الواجهة الرئيسية ---
st.title("⚙️ نظام المبرمج ياسر - النسخة النهائية")
if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 إضافة مواد", "📊 المخزن", "🧾 الفواتير", "👥 العملاء"])

with tabs[0]: # البيع
    st.header("🛒 البيع والطلب")
    cust_list = ["اختر عميل..."] + pd.read_sql("SELECT name FROM customers", conn)['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_list)
    p_type = st.radio("طريقة الدفع", ["نقد", "أقساط"])
    
    prods = pd.read_sql("SELECT * FROM products", conn)
    for idx, row in prods.iterrows():
        qty = st.number_input(f"كمية {row['name']} (المتوفر: {row['quantity']})", 0, int(row['quantity']), key=f"q_{idx}")
        if qty > 0:
            if st.button(f"أضف {row['name']} للسلة", key=f"btn_{idx}"):
                if 'cart' not in st.session_state: st.session_state.cart = {}
                st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
                st.rerun()

    if 'cart' in st.session_state and st.session_state.cart:
        st.subheader("🛒 السلة")
        for n, d in list(st.session_state.cart.items()):
            col1, col2 = st.columns([0.8, 0.2])
            col1.write(f"🔹 {n} | الكمية: {d['qty']}")
            if col2.button(f"❌", key=f"del_{n}"): del st.session_state.cart[n]; st.rerun()
        
        if st.button("✅ إتمام البيع"):
            if selected_customer == "اختر عميل...": st.error("يجب اختيار عميل!")
            else:
                total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
                # الحفظ
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), p_type))
                # الخصم من المخزن
                for n, d in st.session_state.cart.items():
                    c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
                conn.commit(); st.session_state.cart = {}; st.success("تم البيع بنجاح!"); st.rerun()

with tabs[1]: # إضافة مواد
    with st.form("add_prod", clear_on_submit=True):
        n = st.text_input("اسم المادة"); p = st.number_input("السعر", 0); q = st.number_input("الكمية", 0)
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q)); conn.commit(); st.success("تم الإضافة!")

with tabs[2]: # المخزن
    st.header("📊 جرد المخزن")
    data = pd.read_sql("SELECT rowid, * FROM products", conn)
    for _, row in data.iterrows():
        c1, c2 = st.columns([0.8, 0.2])
        c1.write(f"🔹 **{row['name']}** | السعر: {row['price_carton']} | المتوفر: {row['quantity']}")
        if c2.button("🗑️ حذف المادة", key=f"d_{row['rowid']}"):
            c.execute("DELETE FROM products WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tabs[3]: # الفواتير
    st.header("🧾 سجل الفواتير")
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        color = "🟢" if row['payment_type'] == "نقد" else "🟠"
        with st.expander(f"فاتورة #{row['rowid']} | {row['customer_name']} | {color} {row['payment_type']}"):
            try:
                items = ast.literal_eval(row['items'])
                st.table(pd.DataFrame(items).T)
                st.write(f"### المجموع: {row['total']}")
                # تحميل PDF
                pdf_data = get_pdf_bytes(row['rowid'], row['customer_name'], items, row['total'], row['payment_type'])
                st.download_button("📥 تحميل PDF", pdf_data, f"invoice_{row['rowid']}.pdf", "application/pdf")
            except:
                st.error("بيانات الفاتورة تالفة.")
                if st.button(f"🗑️ حذف الفاتورة #{row['rowid']}", key=f"del_{row['rowid']}"):
                    c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tabs[4]: # العملاء
    with st.form("add_c", clear_on_submit=True):
        n = st.text_input("اسم العميل"); phone = st.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (n, phone, "", "", "")); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))
