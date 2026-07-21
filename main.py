import streamlit as st
import sqlite3
import pandas as pd
import ast
import os
import urllib.request
from datetime import date
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser Pro System - Master", layout="wide")

# --- دالة تحميل الخط تلقائياً ---
def ensure_font():
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/dejavu-fonts/dejavu-fonts.github.io/raw/master/ttf/DejaVuSans.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass
    return font_path if os.path.exists(font_path) else None

# --- قاعدة البيانات وتحديث الجداول تلقائياً ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, governorate TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, shop_name TEXT, address TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')

# ترقية الجداول القديمة تلقائياً إذا كانت ناقصة أعمدة
for col_def in [
    ("customers", "shop_name", "TEXT"), ("customers", "phone", "TEXT"), 
    ("customers", "address", "TEXT"), ("customers", "governorate", "TEXT"),
    ("invoices", "shop_name", "TEXT"), ("invoices", "address", "TEXT"), ("invoices", "payment_type", "TEXT")
]:
    try:
        c.execute(f"ALTER TABLE {col_def[0]} ADD COLUMN {col_def[1]} {col_def[2]}")
        conn.commit()
    except:
        pass

# --- دالة توليد الفاتورة العربية بالكامل باستخدام fpdf2 الحديثة ---
def generate_pdf(row, items):
    pdf = FPDF()
    pdf.set_text_shaping(True)  # تفعيل ميزة تشكيل النصوص العربية و RTL تلقائياً في fpdf2
    pdf.add_page()
    
    font_path = ensure_font()
    if not font_path:
        pdf.set_font("helvetica", size=14)
        pdf.cell(200, 10, "Font Error: DejaVuSans missing", ln=True, align='C')
        return pdf.output()
    
    pdf.add_font("ArabicFont", "", font_path)
    pdf.set_font("ArabicFont", size=16)
    
    # رأس الفاتورة
    pdf.cell(200, 10, "فاتورة مبيعات رسمية", ln=True, align='C')
    pdf.ln(5)
    
    # معلومات العميل والمحل
    pdf.set_font("ArabicFont", size=12)
    pdf.cell(200, 10, f"اسم العميل: {row['customer_name']}", ln=True)
    pdf.cell(200, 10, f"اسم المحل: {row.get('shop_name', 'غير متوفر')}", ln=True)
    pdf.cell(200, 10, f"العنوان: {row.get('address', 'غير متوفر')}", ln=True)
    pdf.cell(200, 10, f"تاريخ الفاتورة: {row['date']}", ln=True)
    pdf.ln(10)
    
    # رأس جدول المنتجات
    pdf.cell(80, 10, "المادة", 1, 0, 'C')
    pdf.cell(30, 10, "الكمية", 1, 0, 'C')
    pdf.cell(40, 10, "السعر", 1, 0, 'C')
    pdf.cell(40, 10, "الإجمالي", 1, 1, 'C')
    
    # محتوى الجدول
    for item, data in items.items():
        pdf.cell(80, 10, str(item), 1)
        pdf.cell(30, 10, str(data['qty']), 1, 0, 'C')
        pdf.cell(40, 10, str(data['price']), 1, 0, 'C')
        pdf.cell(40, 10, str(data['qty'] * data['price']), 1, 1, 'C')
        
    # المجموع الكلي النهائي
    pdf.ln(10)
    pdf.set_font("ArabicFont", size=14)
    pdf.cell(200, 10, f"المجموع الكلي النهائي: {row['total']} دينار", ln=True, align='R')
        
    return pdf.output()

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول للنظام")
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

with tabs[0]: # البيع بنظام الشبكة وخصم المخزن
    st.header("إدارة المبيعات والطلب (عرض شبكي)")
    
    custs = pd.read_sql("SELECT * FROM customers", conn)
    cust_list = ["اختر العميل..."] + custs['name'].tolist() if not custs.empty else ["اختر العميل..."]
    sel_cust_name = st.selectbox("اختر العميل للفاتورة", cust_list)
    
    shop_name = "غير محدد"
    address = "غير محدد"
    if sel_cust_name != "اختر العميل...":
        cust_row = custs[custs['name'] == sel_cust_name]
        if not cust_row.empty:
            shop_name = cust_row.iloc[0].get('shop_name', 'غير محدد')
            address = cust_row.iloc[0].get('address', 'غير محدد')
            st.success(f"📍 المحل: {shop_name} | العنوان: {address}")

    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    cart = {}
    
    if not prods.empty:
        st.write("---")
        st.subheader("منتجات المخزن المتاحة:")
        cols = st.columns(3)
        for idx, row in prods.iterrows():
            with cols[idx % 3]:
                st.markdown(f"**{row['name']}**")
                st.text(f"السعر: {row['price_carton']} د.ع\nالمتبقي بالمخزن: {row['quantity']}")
                q = st.number_input(f"الكمية المطلوبة", min_value=0, max_value=int(row['quantity']) if row['quantity'] > 0 else 0, key=f"q_{idx}")
                if q > 0: 
                    cart[row['name']] = {'price': row['price_carton'], 'qty': q}
                st.divider()
                
    if cart and sel_cust_name != "اختر العميل..." and st.button("🛒 إتمام البيع، خصم المخزن، وحفظ الفاتورة"):
        total_amt = sum(d['price'] * d['qty'] for d in cart.values())
        
        c.execute("INSERT INTO invoices (customer_name, shop_name, address, items, total, date, payment_type) VALUES (?,?,?,?,?,?,?)", 
                  (sel_cust_name, shop_name, address, str(cart), total_amt, str(date.today()), "نقد"))
        
        for item_name, data in cart.items():
            sold_qty = data['qty']
            c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (sold_qty, item_name))
            
        conn.commit()
        st.success("✅ تمت العملية بنجاح! تم خصم الكميات من المخزن وحفظ الفاتورة بالمعلومات الكاملة.")
        st.rerun()

with tabs[1]: # الفواتير وتحميلها
    st.header("سجل الفواتير وطباعتها بصيغة PDF")
    inv_df = pd.read_sql("SELECT rowid, * FROM invoices", conn)
    if inv_df.empty:
        st.info("لا توجد فواتير مسجلة حتى الآن.")
    else:
        for _, row in inv_df.iterrows():
            with st.expander(f"فاتورة رقم #{row['rowid']} | العميل: {row['customer_name']} | المحل: {row.get('shop_name', '')} | المجموع: {row['total']} د.ع"):
                items = ast.literal_eval(row['items'])
                st.table(pd.DataFrame(items).T)
                try:
                    pdf_data = generate_pdf(row, items)
                    st.download_button(
                        label="📥 تحميل الفاتورة PDF (عربي مرتب ونظامي)", 
                        data=pdf_data, 
                        file_name=f"invoice_{row['rowid']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{row['rowid']}"
                    )
                except Exception as e:
                    st.error(f"خطأ في توليد الملف: {e}")

with tabs[2]: # المخزن والكميات
    st.header("إدارة المخزن والمواد")
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
    st.header("إدارة العملاء وتفاصيل المحلات")
    c_name = st.text_input("اسم العميل")
    c_shop = st.text_input("اسم المحل")
    c_phone = st.text_input("رقم الهاتف")
    c_address = st.text_input("عنوان المحل بالتفصيل")
    c_gov = st.selectbox("المحافظة", ["البصرة", "بغداد", "ذي قار", "ميسان", "البصرة - العشار", "البصرة - التنومة", "أخرى"])
    
    if st.button("حفظ العميل الجديد"):
        if c_name:
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (c_name, c_shop, c_phone, c_address, c_gov))
            conn.commit()
            st.success("تم إضافة العميل بنجاح!")
            st.rerun()
            
    st.subheader("قائمة العملاء المسجلين:")
    st.dataframe(pd.read_sql("SELECT rowid, * FROM customers", conn))

with tabs[4]: # المساعد الذكي
    st.header("🤖 المساعد الذكي لإدارة النظام")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📊 إحصائيات النظام")
        prod_count = pd.read_sql("SELECT COUNT(*) FROM products", conn).iloc[0, 0]
        cust_count = pd.read_sql("SELECT COUNT(*) FROM customers", conn).iloc[0, 0]
        inv_count = pd.read_sql("SELECT COUNT(*) FROM invoices", conn).iloc[0, 0]
        st.metric("عدد المواد في المخزن", prod_count)
        st.metric("عدد العملاء", cust_count)
        st.metric("إجمالي الفواتير", inv_count)
        
    with col_b:
        st.subheader("⚡ تنبيهات النواقص")
        low_stock = pd.read_sql("SELECT name, quantity FROM products WHERE quantity <= 5", conn)
        if low_stock.empty:
            st.success("المخزن ممتاز، لا توجد نواقص خطيرة.")
        else:
            st.warning("تنبيه: المواد التالية قاربت على النفاذ:")
            st.dataframe(low_stock)
