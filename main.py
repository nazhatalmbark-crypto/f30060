import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="نظام الإدارة - م. ياسر", layout="wide")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price REAL)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total REAL, timestamp TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, debt REAL)')
conn.commit()

# --- دالة صناعة الـ PDF ---
def create_pdf(cart_data, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Invoice - Eng. Yasser Shop", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for item in cart_data:
        pdf.cell(200, 10, txt=f"Item: {item['name']} | Price: {item['price']} IQD", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Total: {total:,} IQD", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- إدارة الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔐 بوابة النظام - م. ياسر")
    user = st.text_input("اسم المستخدم")
    pwd = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# --- الحالة الابتدائية للسلة ---
if 'cart' not in st.session_state: st.session_state.cart = []

# --- القائمة الجانبية ---
menu = st.sidebar.radio("القائمة", ["سلة البيع", "إضافة مواد", "أرشيف الفواتير", "العملاء والديون"])

# --- 1. سلة البيع ---
if menu == "سلة البيع":
    tab1, tab2 = st.tabs(["🛒 قائمة المنتجات", "📋 سلة الشراء"])
    with tab1:
        st.title("🍽️ القائمة / المواد")
        search = st.text_input("🔍 بحث عن مادة...")
        products = pd.read_sql("SELECT * FROM products", conn)
        if search: products = products[products['name'].str.contains(search, na=False)]
        for index, row in products.iterrows():
            col1, col2 = st.columns([3, 1])
            col1.write(f"### {row['name']} - {row['price']} د.ع")
            if col2.button("إضافة 🛒", key=f"add_{index}"):
                st.session_state.cart.append({'name': row['name'], 'price': row['price']})
                st.rerun()
    with tab2:
        st.title("📋 سلة البيع الحالية")
        cust_name = st.text_input("اسم العميل", value="زبون عام")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            st.table(cart_df)
            total = cart_df['price'].sum()
            st.metric("المبلغ الكلي", f"{total:,} د.ع")
            if st.button("💾 حفظ الفاتورة في الأرشيف"):
                c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (cust_name, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.success("تم الحفظ في الأرشيف!")
            pdf_data = create_pdf(st.session_state.cart, total)
            st.download_button("📥 تحميل الفاتورة (PDF)", pdf_data, "invoice.pdf", "application/pdf")
            if st.button("تصفير السلة"):
                st.session_state.cart = []
                st.rerun()
        else: st.info("السلة فارغة.")

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    st.title("➕ إضافة مادة جديدة")
    with st.form("add_p"):
        name = st.text_input("اسم المادة")
        price = st.number_input("السعر", min_value=0.0)
        if st.form_submit_button("حفظ المادة"):
            c.execute("INSERT INTO products VALUES (?,?)", (name, price))
            conn.commit()
            st.success(f"تمت إضافة {name} بنجاح!")

# --- 3. أرشيف الفواتير ---
elif menu == "أرشيف الفواتير":
    st.title("📜 أرشيف الفواتير")
    df_inv = pd.read_sql("SELECT * FROM invoices", conn)
    if not df_inv.empty:
        df_inv = df_inv.sort_values(by='timestamp', ascending=False)
        st.dataframe(df_inv, use_container_width=True)
    else: st.warning("لا توجد فواتير مؤرشفة.")

# --- 4. العملاء والديون ---
elif menu == "العملاء والديون":
    st.title("👥 إدارة العملاء والديون")
    with st.form("add_c"):
        c_name = st.text_input("اسم العميل")
        c_debt = st.number_input("الدين (د.ع)", min_value=0.0)
        if st.form_submit_button("إضافة عميل"):
            c.execute("INSERT INTO customers VALUES (?,?)", (c_name, c_debt))
            conn.commit()
            st.success("تم إضافة العميل!")
    df_cust = pd.read_sql("SELECT * FROM customers", conn)
    st.dataframe(df_cust, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.write("**م. ياسر / Eng. Yasser**")
