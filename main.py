import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import ast
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# --- إعداد قاعدة البيانات ---
DB_NAME = 'shop_data_pro_v3.db'
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
        pdf.cell(200, 10, txt=f"{item} | الكمية: {int(data['qty'])} | السعر: {int(data['price'])}", ln=True)
    pdf.cell(200, 10, txt=f"المجموع الكلي: {int(total)}", ln=True)
    file_name = f"invoice_{invoice_id}.pdf"
    pdf.output(file_name)
    return file_name

# --- واجهة النظام ---
st.title("⚙️ نظام المبرمج ياسر - النسخة النهائية")
tabs = st.tabs(["🛒 البيع (السلة)", "📦 إضافة مواد", "📊 المخزن", "🧾 الفواتير", "👥 العملاء"])

with tabs[0]: # شاشة البيع
    st.header("🛒 البيع والطلب")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    cust_list = ["اختر عميل..."] + cust_df['name'].tolist()
    selected_customer = st.selectbox("🔎 اختر العميل", cust_list)
    
    prods = pd.read_sql("SELECT * FROM products", conn)
    
    # شبكة المنتجات مع مفاتيح فريدة (idx) لمنع الخطأ
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
            else:
                st.error("🚫 خارج المخزون")

    # السلة وإكمال البيع
    if 'cart' in st.session_state and st.session_state.cart:
        st.write("---")
        st.subheader("🛒 محتويات السلة")
        cart_df = pd.DataFrame(st.session_state.cart).T
        st.table(cart_df)
        
        if st.button("✅ إتمام البيع وإصدار الفاتورة"):
            if selected_customer == "اختر عميل...":
                st.error("خطأ: يجب اختيار عميل أولاً!")
            else:
                total = sum(d['price'] * d['qty'] for d in st.session_state.cart.values())
                # الحفظ في قاعدة البيانات
                c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (selected_customer, str(st.session_state.cart), int(total), datetime.now().strftime("%Y-%m-%d")))
                # خصم الكميات
                for name, data in st.session_state.cart.items():
                    c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(data['qty']), name))
                conn.commit()
                st.session_state.cart = {}
                st.success("تم البيع بنجاح!")
                st.rerun()
        
        if st.button("🗑️ مسح السلة"):
            st.session_state.cart = {}
            st.rerun()

with tabs[1]: # إضافة مواد
    st.header("📦 إضافة مواد")
    with st.form("add_prod", clear_on_submit=True):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر"); q = st.text_input("الكمية")
        if st.form_submit_button("إضافة للمخزن"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (n, int(p), int(q))); conn.commit(); st.success("تمت الإضافة!")

with tabs[2]: # المخزن
    st.header("📊 جرد المخزن")
    st.table(pd.read_sql("SELECT * FROM products", conn))

with tabs[3]: # الفواتير
    st.header("🧾 سجل الفواتير")
    # زر تنظيف شامل للطوارئ
    if st.button("⚠️ تنظيف شامل للفواتير التالفة"):
        c.execute("DELETE FROM invoices")
        conn.commit(); st.rerun()
        
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} | العميل: {row['customer_name']}"):
            try:
                # محاولة قراءة وتصحيح البيانات
                items = ast.literal_eval(row['items'])
                for n, d in items.items(): st.write(f"🔹 {n} | {int(d['qty'])} قطعة")
                st.write(f"المجموع: {int(row['total'])}")
                if st.button(f"📥 PDF", key=f"pdf_{row['rowid']}"):
                    generate_pdf(row['rowid'], row['customer_name'], items, int(row['total']))
                    st.success("تم!")
            except:
                st.error("بيانات الفاتورة تالفة.")
                if st.button(f"🗑️ حذف هذه الفاتورة", key=f"del_{row['rowid']}"):
                    c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],)); conn.commit(); st.rerun()

with tabs[4]: # العملاء
    st.header("👥 العملاء")
    with st.form("add_c", clear_on_submit=True):
        n, p = st.columns(2); name = n.text_input("اسم العميل"); phone = p.text_input("رقم الهاتف")
        s, a = st.columns(2); shop = s.text_input("اسم المحل"); addr = a.text_input("موقع المحل")
        if st.form_submit_button("إضافة عميل"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (name, phone, shop, addr, "البصرة")); conn.commit(); st.rerun()
    st.table(pd.read_sql("SELECT * FROM customers", conn))
