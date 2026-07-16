import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import ast
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# إعداد قاعدة البيانات
DB_NAME = 'shop_data_pro.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT, shop_name TEXT, shop_address TEXT, province TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT)')
conn.commit()

# --- دالة PDF ---
def generate_pdf(invoice_id, customer_name, items, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="فاتورة مبيعات - نظام المبرمج ياسر", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"العميل: {customer_name}", ln=True)
    pdf.cell(200, 10, txt=f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(10)
    for item, data in items.items():
        pdf.cell(200, 10, txt=f"{item} | الكمية: {data['qty']} | السعر: {data['price']}", ln=True)
    pdf.cell(200, 10, txt=f"المجموع الكلي: {total}", ln=True)
    pdf.output(f"invoice_{invoice_id}.pdf")
    return f"invoice_{invoice_id}.pdf"

# --- الواجهة ---
st.title("⚙️ نظام إدارة المبيعات - المبرمج ياسر")

# التبويبات (أضفت تبويب إضافة مواد مستقل)
tabs = st.tabs(["🛒 البيع", "📦 إضافة مواد", "📊 المخزن والجرد", "🧾 الفواتير", "👥 العملاء", "📊 كشف الحساب"])

with tabs[0]: # البيع
    st.header("🛒 شاشة البيع")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_list = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_list)
    
    prods = pd.read_sql("SELECT * FROM products", conn)
    if not prods.empty:
        item_select = st.selectbox("المادة", prods['name'].tolist())
        qty_input = st.text_input("الكمية")
        if st.button("➕ أضف للسلة"):
            if selected_customer == "اختر عميل...": st.error("اختر عميلاً أولاً!")
            elif not qty_input.isdigit(): st.error("أدخل رقماً!")
            else:
                price = prods[prods['name'] == item_select]['price_carton'].values[0]
                if 'cart' not in st.session_state: st.session_state.cart = {}
                st.session_state.cart[item_select] = {'price': price, 'qty': int(qty_input)}
                st.rerun()

    if 'cart' in st.session_state and st.session_state.cart:
        st.table(pd.DataFrame(st.session_state.cart).T)
        if st.button("✅ إتمام البيع"):
            total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
            for name, data in st.session_state.cart.items():
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (data['qty'], name))
            c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d")))
            conn.commit(); st.session_state.cart = {}; st.success("تم البيع!"); st.rerun()

with tabs[1]: # إضافة مواد (هذا هو طلبك)
    st.header("📦 إضافة مواد جديدة للمخزن")
    with st.form("add_prod_form", clear_on_submit=True):
        new_name = st.text_input("اسم المادة")
        new_price = st.text_input("سعر الكارتون")
        new_qty = st.text_input("الكمية المتوفرة")
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (new_name, int(new_price), int(new_qty)))
            conn.commit(); st.success(f"تمت إضافة {new_name} بنجاح!")

with tabs[2]: # المخزن
    st.header("📊 جرد المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

with tabs[3]: # الفواتير
    st.header("🧾 سجل الفواتير")
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} | {row['customer_name']}"):
            items = ast.literal_eval(row['items'])
            for n, d in items.items(): st.write(f"🔹 {n} | {d['qty']} قطعة")
            if st.button(f"📥 PDF فاتورة {row['rowid']}", key=f"p_{row['rowid']}"):
                generate_pdf(row['rowid'], row['customer_name'], items, row['total'])
                st.success("تم إنشاء ملف الـ PDF")

with tabs[4]: # العملاء
    st.header("👥 العملاء")
    search = st.text_input("🔍 بحث عن اسم المحل")
    with st.form("add_c", clear_on_submit=True):
        n, p = st.columns(2)
        name = n.text_input("اسم العميل"); phone = p.text_input("رقم الهاتف")
        s, a = st.columns(2)
        shop = s.text_input("اسم المحل"); addr = a.text_input("موقع المحل")
        if st.form_submit_button("إضافة عميل"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop, addr, "البصرة")); conn.commit(); st.rerun()
    
    df_cust = pd.read_sql("SELECT * FROM customers", conn)
    if search: df_cust = df_cust[df_cust['shop_name'].str.contains(search, na=False)]
    st.table(df_cust)

with tabs[5]: # كشف حساب
    st.header("📊 كشف حساب الزبون")
    sel_cust = st.selectbox("اختر عميل", pd.read_sql("SELECT name FROM customers", conn)['name'].tolist())
    if sel_cust:
        inv = pd.read_sql("SELECT * FROM invoices WHERE customer_name = ?", conn, params=(sel_cust,))
        st.table(inv)
        st.write(f"### إجمالي الذمة: {inv['total'].sum()}")
