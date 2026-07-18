import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- إعداد قاعدة البيانات ---
DB_NAME = 'shop_data_final.db' # اسم موحد
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')
conn.commit()

# --- دالة PDF ---
def generate_pdf(invoice_id, customer_name, items, total, p_type):
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
    file_name = f"invoice_{invoice_id}.pdf"
    pdf.output(file_name)
    return file_name

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
                conn.commit(); st.success("تم!")
            except: st.error("المستخدم موجود!")
        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
            if c.fetchone(): st.session_state.logged_in = True; st.rerun()
            else: st.error("خطأ!")
    st.stop()

st.title("⚙️ نظام المبرمج ياسر - النسخة النهائية")
if st.button("خروج"): st.session_state.logged_in = False; st.rerun()

tabs = st.tabs(["🛒 البيع (السلة)", "📦 إضافة مواد", "📊 المخزن", "🧾 الفواتير", "👥 العملاء"])

with tabs[0]: # البيع
    st.header("🛒 البيع والطلب")
    cust_list = ["اختر عميل..."] + pd.read_sql("SELECT name FROM customers", conn)['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_list)
    p_type = st.radio("طريقة الدفع", ["نقد", "أقساط"])
    
    prods = pd.read_sql("SELECT * FROM products", conn)
    cols = st.columns(3)
    for idx, row in prods.iterrows():
        with cols[idx % 3]:
            st.info(f"### {row['name']}\nالسعر: {row['price_carton']}\nالكمية: {row['quantity']}")
            if row['quantity'] > 0:
                qty = st.number_input(f"كمية {row['name']}", min_value=1, max_value=int(row['quantity']), key=f"qty_{idx}")
                if st.button(f"➕ إضافة {row['name']}", key=f"add_{idx}"):
                    if 'cart' not in st.session_state: st.session_state.cart = {}
                    st.session_state.cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
                    st.rerun()
    
    if 'cart' in st.session_state and st.session_state.cart:
        st.write("---")
        st.subheader("🛒 السلة")
        for item_name, data in list(st.session_state.cart.items()):
            col_a, col_b = st.columns([0.8, 0.2])
            with col_a: st.write(f"🔹 **{item_name}** | الكمية: {data['qty']}")
            with col_b:
                if st.button(f"❌", key=f"del_cart_{item_name}"):
                    del st.session_state.cart[item_name]; st.rerun()
        
        if st.button("✅ إتمام البيع"):
            total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d"), p_type))
            for name, data in st.session_state.cart.items():
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(data['qty']), name))
            conn.commit(); st.session_state.cart = {}; st.success("تم!"); st.rerun()

with tabs[1]: # إضافة مواد
    with st.form("add_prod", clear_on_submit=True):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر"); q = st.text_input("الكمية")
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (n, int(p), int(q))); conn.commit(); st.success("تم!")

with tabs[2]: # المخزن (مع زر الحذف)
    st.header("📊 جرد المخزن")
    prods_data = pd.read_sql("SELECT rowid, * FROM products", conn)
    for _, row in prods_data.iterrows():
        c1, c2 = st.columns([0.8, 0.2])
        with c1: st.write(f"🔹 **{row['name']}** | السعر: {row['price_carton']} | الكمية: {row['quantity']}")
        with c2:
            if st.button("🗑️ حذف", key=f"del_prod_{row['rowid']}"):
                c.execute("DELETE FROM products WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tabs[3]: # الفواتير (نظام الطوارئ)
    st.header("🧾 سجل الفواتير")
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        color = "green" if row['payment_type'] == "نقد" else "orange"
        with st.expander(f"فاتورة #{row['rowid']} | العميل: {row['customer_name']} | التاريخ: {row['date']}"):
            st.markdown(f"نوع الدفع: :{color}[{row['payment_type']}]")
            try:
                raw = row['items'].replace('np.int64', '').replace('(', '').replace(')', '')
                items = ast.literal_eval(raw)
                for n, d in items.items(): st.write(f"🔹 {n} | الكمية: {int(d['qty'])}")
                st.write(f"المجموع: {int(row['total'])}")
                if st.button(f"📥 PDF", key=f"pdf_{row['rowid']}"):
                    generate_pdf(row['rowid'], row['customer_name'], items, int(row['total']), row['payment_type'])
                    st.success("تم!")
            except:
                st.error("فاتورة تالفة.")
            
            # زر حذف الفاتورة حتى لو كانت تالفة
            if st.button(f"🗑️ حذف هذه الفاتورة #{row['rowid']}", key=f"del_inv_{row['rowid']}"):
                c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tabs[4]: # العملاء
    with st.form("add_c", clear_on_submit=True):
        n, p = st.columns(2); name = n.text_input("اسم العميل"); phone = p.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, "", "", "البصرة")); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))
