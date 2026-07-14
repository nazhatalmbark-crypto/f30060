import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="نظام الإدارة - م. ياسر", layout="wide")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول (محدثة مع خانة الكمية)
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price REAL, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total REAL, timestamp TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, area TEXT, debt REAL)')
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

# --- القائمة الجانبية ---
menu = st.sidebar.radio("القائمة", ["سلة البيع", "إضافة مواد", "جرد المخزن", "أرشيف الفواتير", "العملاء والديون"])

# --- 1. سلة البيع ---
if 'cart' not in st.session_state: st.session_state.cart = []
if menu == "سلة البيع":
    tab1, tab2 = st.tabs(["🛒 قائمة المنتجات", "📋 سلة الشراء"])
    with tab1:
        st.title("🍽️ القائمة / المواد")
        search = st.text_input("🔍 بحث عن مادة...")
        products = pd.read_sql("SELECT * FROM products WHERE quantity > 0", conn)
        if search: products = products[products['name'].str.contains(search, na=False)]
        for index, row in products.iterrows():
            col1, col2 = st.columns([3, 1])
            col1.write(f"### {row['name']} - {row['price']} د.ع | المتبقي: {row['quantity']}")
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
            
            if st.button("💾 حفظ الفاتورة وإنقاص المخزن"):
                # 1. حفظ الفاتورة
                c.execute("INSERT INTO invoices VALUES (?,?,?,?)", (cust_name, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                # 2. إنقاص الكمية من الجدول
                for item in st.session_state.cart:
                    c.execute("UPDATE products SET quantity = quantity - 1 WHERE name = ?", (item['name'],))
                conn.commit()
                st.success("تم الحفظ وإنقاص المخزن!")
                
            pdf_data = create_pdf(st.session_state.cart, total)
            st.download_button("📥 تحميل الفاتورة (PDF)", pdf_data, "invoice.pdf", "application/pdf")
            if st.button("تصفير السلة"):
                st.session_state.cart = []
                st.rerun()

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    st.title("➕ إضافة مادة جديدة للمخزن")
    with st.form("add_p"):
        name = st.text_input("اسم المادة")
        price = st.number_input("السعر", min_value=0.0)
        qty = st.number_input("الكمية الأولية", min_value=0)
        if st.form_submit_button("حفظ المادة"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (name, price, qty))
            conn.commit()
            st.success(f"تمت إضافة {name} بنجاح!")

# --- 3. جرد المخزن ---
elif menu == "جرد المخزن":
    st.title("📊 جرد المخزن الحالي")
    df_inv = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(df_inv, use_container_width=True)

# --- 4. أرشيف الفواتير ---
elif menu == "أرشيف الفواتير":
    st.title("📜 أرشيف الفواتير")
    df_inv = pd.read_sql("SELECT * FROM invoices", conn)
    if not df_inv.empty:
        df_inv = df_inv.sort_values(by='timestamp', ascending=False)
        st.dataframe(df_inv, use_container_width=True)

# --- 5. العملاء والديون ---
elif menu == "العملاء والديون":
    st.title("👥 إدارة العملاء والديون")
    with st.form("add_c"):
        name = st.text_input("اسم العميل")
        shop = st.text_input("اسم السنتر/المحل")
        phone = st.text_input("رقم الهاتف")
        addr = st.text_input("العنوان")
        area = st.text_input("المنطقة")
        debt = st.number_input("الدين الحالي (د.ع)", min_value=0.0)
        if st.form_submit_button("إضافة العميل"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?)", (name, shop, phone, addr, area, debt))
            conn.commit()
            st.success("تم إضافة العميل!")
    st.dataframe(pd.read_sql("SELECT * FROM customers", conn))
