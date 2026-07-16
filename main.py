import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- اسم قاعدة بيانات جديد لتجنب الأخطاء القديمة ---
DB_NAME = 'shop_data_final_v2.db'
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
    file_name = f"invoice_{invoice_id}.pdf"
    pdf.output(file_name)
    return file_name

st.title("⚙️ نظام إدارة المبيعات - المبرمج ياسر")

tabs = st.tabs(["🛒 البيع", "📦 إضافة مواد", "📊 المخزن", "🧾 الفواتير", "👥 العملاء", "📊 كشف الحساب"])

with tabs[0]: # البيع
    st.header("🛒 شاشة البيع")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_list = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_list)
    prods = pd.read_sql("SELECT * FROM products", conn)
    if not prods.empty:
        item_select = st.selectbox("المادة", prods['name'].unique().tolist())
        qty_input = st.text_input("الكمية")
        if st.button("➕ أضف للسلة"):
            if selected_customer == "اختر عميل...": st.error("اختر عميلاً!")
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

with tabs[1]: # إضافة مواد
    st.header("📦 إضافة مواد")
    with st.form("add_prod", clear_on_submit=True):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر"); q = st.text_input("الكمية")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (n, int(p), int(q))); conn.commit(); st.success("تم!")

with tabs[2]: # المخزن
    st.header("📊 المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

with tabs[3]: # الفواتير (الجزء المحمي)
    st.header("🧾 الفواتير")
    if st.button("🧹 تصفير وتنظيف كل شيء"):
        c.execute("DELETE FROM invoices")
        conn.commit(); st.rerun()
    
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} | {row['customer_name']}"):
            try:
                # حماية القراءة
                items = ast.literal_eval(row['items'])
                for n, d in items.items(): st.write(f"🔹 {n} | {d['qty']} قطعة")
                st.write(f"المجموع: {row['total']}")
                if st.button(f"📥 PDF", key=f"pdf_{row['rowid']}"):
                    generate_pdf(row['rowid'], row['customer_name'], items, row['total'])
                    st.success("تم")
            except:
                st.error("بيانات هذه الفاتورة تالفة.")
                if st.button(f"🗑️ حذف الفاتورة التالفة {row['rowid']}", key=f"del_{row['rowid']}"):
                    c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],))
                    conn.commit(); st.rerun()

with tabs[4]: # العملاء
    st.header("👥 العملاء")
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tabs[5]: # كشف حساب
    st.header("📊 كشف الحساب")
    sel_cust = st.selectbox("اختر", ["اختر عميل..."] + pd.read_sql("SELECT name FROM customers", conn)['name'].tolist())
    if sel_cust != "اختر عميل...":
        st.table(pd.read_sql("SELECT * FROM invoices WHERE customer_name = ?", conn, params=(sel_cust,)))
