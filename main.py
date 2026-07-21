import streamlit as st
import sqlite3
import pandas as pd
import ast
import os
from datetime import date
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="Eng. Yasser Pro System - Master", layout="wide")

# --- دالة النص العربي ---
def render_arabic(text):
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    except:
        return str(text)

# --- قاعدة البيانات وجداولها المتقدمة ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, governorate TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')

# --- دالة توليد الفاتورة العربية ---
def generate_pdf(row, items):
    pdf = FPDF()
    pdf.add_page()
    
    font_path = 'DejaVuSans.ttf'
    if not os.path.exists(font_path):
        raise Exception("ملف الخط DejaVuSans.ttf غير موجود في مجلد المشروع!")
    
    pdf.add_font("ArabicFont", "", font_path, uni=True)
    pdf.set_font("ArabicFont", size=16)
    
    pdf.cell(200, 10, render_arabic("فاتورة مبيعات رسمية"), ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("ArabicFont", size=12)
    pdf.cell(200, 10, render_arabic(f"اسم العميل: {row['customer_name']}"), ln=True)
    pdf.cell(200, 10, render_arabic(f"تاريخ الفاتورة: {row['date']}"), ln=True)
    pdf.ln(10)
    
    pdf.cell(80, 10, render_arabic("المادة"), 1, 0, 'C')
    pdf.cell(30, 10, render_arabic("الكمية"), 1, 0, 'C')
    pdf.cell(40, 10, render_arabic("السعر"), 1, 0, 'C')
    pdf.cell(40, 10, render_arabic("الإجمالي"), 1, 1, 'C')
    
    for item, data in items.items():
        pdf.cell(80, 10, render_arabic(str(item)), 1)
        pdf.cell(30, 10, str(data['qty']), 1, 0, 'C')
        pdf.cell(40, 10, str(data['price']), 1, 0, 'C')
        pdf.cell(40, 10, str(data['qty'] * data['price']), 1, 1, 'C')
        
    pdf.ln(10)
    pdf.set_font("ArabicFont", size=14)
    pdf.cell(200, 10, render_arabic(f"المجموع الكلي: {row['total']} دينار"), ln=True, align='R')
        
    return pdf.output(dest='S')

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول للنظام الشامل")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("دخول كمسؤول"): 
            st.session_state.logged_in = True
            st.rerun()
    with col2:
        if st.button("🚀 دخول الضيف"): 
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- أقسام النظام (Tabs) ---
tabs = st.tabs(["🛒 البيع (شبكة)", "🧾 الفواتير والتحميل", "📦 المخزن والكميات", "👥 إدارة العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # البيع بنظام الشبكة مع خصم الكميات
    st.header("إدارة المبيعات والطلب (عرض شبكي)")
    custs = pd.read_sql("SELECT name FROM customers", conn)
    cust_list = ["اختر العميل..."] + custs['name'].tolist() if not custs.empty else ["اختر العميل..."]
    sel = st.selectbox("اختر العميل للفاتورة", cust_list)
    
    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    cart = {}
    
    if not prods.empty:
        # عرض المنتجات على شكل أعمدة (شبكة)
        cols = st.columns(3)
        for idx, row in prods.iterrows():
            with cols[idx % 3]:
                st.markdown(f"**{row['name']}**")
                st.text(f"السعر: {row['price_carton']} | الباقي بالمخزن: {row['quantity']}")
                q = st.number_input(f"الكمية المطلوبة", min_value=0, max_value=int(row['quantity']) if row['quantity'] > 0 else 0, key=f"q_{idx}")
                if q > 0: 
                    cart[row['name']] = {'price': row['price_carton'], 'qty': q}
                st.divider()
                
    if cart and sel != "اختر العميل..." and st.button("إتمام البيع وخصم المخزن وحفظ الفاتورة"):
        total_amt = sum(d['price'] * d['qty'] for d in cart.values())
        
        # حفظ الفاتورة
        c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (sel, str(cart), total_amt, str(date.today()), "نقد"))
        
        # خصم الكميات من المخزن تلقائياً
        for item_name, data in cart.items():
            sold_qty = data['qty']
            c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (sold_qty, item_name))
            
        conn.commit()
        st.success("تم إتمام البيع، خصم الكميات من المخزن، وحفظ الفاتورة بنجاح!")
        st.rerun()

with tabs[1]: # الفواتير
    st.header("سجل الفواتير وطباعتها")
    inv_df = pd.read_sql("SELECT rowid, * FROM invoices", conn)
    if inv_df.empty:
        st.info("لا توجد فواتير مسجلة حتى الآن.")
    else:
        for _, row in inv_df.iterrows():
            with st.expander(f"فاتورة رقم #{row['rowid']} - العميل: {row['customer_name']} - المجموع: {row['total']}"):
                items = ast.literal_eval(row['items'])
                st.table(pd.DataFrame(items).T)
                try:
                    pdf_data = generate_pdf(row, items)
                    st.download_button(
                        label="📥 تحميل الفاتورة PDF (عربي)", 
                        data=pdf_data, 
                        file_name=f"invoice_{row['rowid']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{row['rowid']}"
                    )
                except Exception as e:
                    st.error(f"خطأ في توليد الملف: {e}")

with tabs[2]: # المخزن والكميات المتبقية
    st.header("إدارة المخزن ومتابعة الكميات المتبقية")
    p_name = st.text_input("اسم المادة الجديدة")
    p_price = st.number_input("سعر الكارتون", min_value=0)
    p_qty = st.number_input("الكمية المتاحة", min_value=0)
    if st.button("إضافة مادة للمخزن"):
        if p_name:
            c.execute("INSERT INTO products VALUES (?,?,?)", (p_name, p_price, p_qty))
            conn.commit()
            st.success("تمت إضافة المادة بنجاح!")
            st.rerun()
            
    st.subheader("حالة المخزن الحالية:")
    st.dataframe(pd.read_sql("SELECT rowid, * FROM products", conn))

with tabs[3]: # إدارة العملاء بالتفاصيل الكاملة
    st.header("إدارة العملاء (مع تفاصيل المحل والمحافظة)")
    c_name = st.text_input("اسم العميل")
    c_shop = st.text_input("اسم المحل")
    c_phone = st.text_input("رقم المحل / الهاتف")
    c_address = st.text_input("عنوان المحل")
    c_gov = st.selectbox("المحافظة", ["البصرة", "بغداد", "ذي قار", "ميسان", "البصرة - العشار", "البصرة - التنومة", "أخرى"])
    
    if st.button("حفظ العميل الجديد"):
        if c_name:
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (c_name, c_shop, c_phone, c_address, c_gov))
            conn.commit()
            st.success("تم إضافة العميل وتفاصيله بنجاح!")
            st.rerun()
            
    st.subheader("قائمة العملاء المسجلين:")
    st.dataframe(pd.read_sql("SELECT rowid, * FROM customers", conn))

with tabs[4]: # المساعد الذكي
    st.header("🤖 المساعد الذكي لإدارة النظام")
    st.info("مرحباً بك يا ياسر في مساعدك الذكي. يمكنك من هنا مراجعة حالة النظام وإجراء عمليات سريعة.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📊 إحصائيات سريعة")
        prod_count = pd.read_sql("SELECT COUNT(*) FROM products", conn).iloc[0, 0]
        cust_count = pd.read_sql("SELECT COUNT(*) FROM customers", conn).iloc[0, 0]
        inv_count = pd.read_sql("SELECT COUNT(*) FROM invoices", conn).iloc[0, 0]
        st.metric("عدد المواد في المخزن", prod_count)
        st.metric("عدد العملاء المسجلين", cust_count)
        st.metric("إجمالي الفواتير الصادرة", inv_count)
        
    with col_b:
        st.subheader("⚡ تنبيهات المخزن")
        low_stock = pd.read_sql("SELECT name, quantity FROM products WHERE quantity <= 5", conn)
        if low_stock.empty:
            st.success("جميع المواد متوفرة بكميات جيدة ولا توجد نواقص خطيرة.")
        else:
            st.warning("تنبيه: المواد التالية قاربت على النفاد:")
            st.dataframe(low_stock)
