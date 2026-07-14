import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="نظام الإدارة - م. ياسر", layout="wide")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price REAL, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
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
        line = f"Item: {item['name']} | Price: {item['price']}"
        pdf.cell(200, 10, txt=line, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Total: {total:,} IQD", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- إدارة الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 بوابة النظام - م. ياسر")
    choice = st.radio("العملية:", ["تسجيل دخول", "حساب جديد"])
    user = st.text_input("اسم المستخدم")
    pwd = st.text_input("كلمة المرور", type="password")
    
    if st.button("تنفيذ"):
        if choice == "حساب جديد":
            try:
                c.execute("INSERT INTO users VALUES (?,?)", (user, pwd))
                conn.commit()
                st.success("تم إنشاء الحساب!")
            except: st.error("موجود مسبقاً!")
        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
            if c.fetchone():
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("خطأ!")
    st.stop()

# --- القائمة الرئيسية ---
st.sidebar.title("⚙️ لوحة التحكم")
menu = st.sidebar.radio("القائمة", ["سلة البيع", "إضافة مواد", "جرد المخزن"])
if st.sidebar.button("🚪 تسجيل خروج"):
    st.session_state.logged_in = False
    st.rerun()

# تهيئة السلة
if 'cart' not in st.session_state: st.session_state.cart = []

# 1. سلة البيع
if menu == "سلة البيع":
    st.title("🛒 سلة المبيعات")
    products = pd.read_sql("SELECT * FROM products", conn)
    if not products.empty:
        selected_prod = st.selectbox("اختر المادة", products['name'].tolist())
        if st.button("إضافة"):
            row = products[products['name'] == selected_prod].iloc[0]
            st.session_state.cart.append({'name': row['name'], 'price': row['price']})
            st.rerun()
        
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            st.table(cart_df)
            total = cart_df['price'].sum()
            st.metric("المبلغ الكلي", f"{total:,} د.ع")
            
            # تحميل PDF
            pdf_data = create_pdf(st.session_state.cart, total)
            st.download_button("📥 تحميل الفاتورة (PDF)", pdf_data, "invoice.pdf", "application/pdf")
            
            if st.button("تصفير السلة"):
                st.session_state.cart = []
                st.rerun()
    else: st.warning("المخزن فارغ!")

# 2. إضافة مواد
elif menu == "إضافة مواد":
    st.title("➕ إضافة مادة")
    with st.form("add_p"):
        name = st.text_input("اسم المادة")
        price = st.number_input("السعر", min_value=0.0)
        if st.form_submit_button("حفظ"):
            c.execute("INSERT INTO products VALUES (?,?,?)", (name, price, 1))
            conn.commit()
            st.success("تم الحفظ!")

# 3. جرد المخزن (مع بحث وحذف)
elif menu == "جرد المخزن":
    st.title("📊 جرد المخزن")
    search = st.text_input("🔍 بحث عن مادة...")
    query = "SELECT * FROM products"
    if search: query += f" WHERE name LIKE '%{search}%'"
    df = pd.read_sql(query, conn)
    st.dataframe(df, use_container_width=True)
    
    # حذف مادة
    del_name = st.text_input("اسم المادة المراد حذفها")
    if st.button("حذف المادة"):
        c.execute("DELETE FROM products WHERE name=?", (del_name,))
        conn.commit()
        st.rerun()