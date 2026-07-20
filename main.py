import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import ast
import os
from datetime import date
from fpdf import FPDF

st.set_page_config(page_title="Eng. Yasser Pro System", layout="wide")

# --- قاعدة البيانات ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, phone TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')

# تحديث الجدول إذا كان ناقصاً
try:
    c.execute("ALTER TABLE invoices ADD COLUMN payment_type TEXT")
    conn.commit()
except:
    pass

def hash_pw(pw): 
    return hashlib.sha256(pw.encode()).hexdigest()

c.execute("SELECT COUNT(*) FROM users")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users VALUES (?, ?)", ("admin", hash_pw("1234")))
    conn.commit()

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_guest' not in st.session_state: st.session_state.is_guest = False

if not st.session_state.logged_in:
    st.title("🔐 Eng. Yasser Pro System - تسجيل الدخول")
    tab1, tab2 = st.tabs(["🔑 تسجيل دخول المسؤول", "👤 دخول الضيف"])
    with tab1:
        user = st.text_input("اسم المستخدم", key="u1")
        pw = st.text_input("كلمة المرور", type="password", key="p1")
        if st.button("دخول كمسؤول"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, hash_pw(pw)))
            if c.fetchone(): 
                st.session_state.logged_in = True
                st.session_state.is_guest = False
                st.rerun()
            else: st.error("خطأ في اسم المستخدم أو كلمة المرور!")
    with tab2:
        if st.button("🚀 الدخول السريع كضيف"):
            st.session_state.logged_in = True
            st.session_state.is_guest = True
            st.rerun()
    st.stop()

# --- الواجهة الرئيسية ---
st.title("Eng. Yasser Pro System ✨")
if st.session_state.is_guest:
    st.info("أنت متصفح الآن في وضع (الضيف).")

if st.button("تسجيل الخروج"): 
    st.session_state.logged_in = False
    st.session_state.is_guest = False
    st.rerun()

tabs = st.tabs(["🛒 البيع", "📦 المخزن", "🧾 الفواتير", "👥 العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # البيع
    st.header("🛒 نقطة البيع")
    custs = pd.read_sql("SELECT name FROM customers", conn)
    if custs.empty: st.warning("أضف عملاء أولاً من تبويب العملاء!")
    else:
        selected_c = st.selectbox("اختر العميل", ["اختر..."] + custs['name'].tolist())
        prods = pd.read_sql("SELECT rowid, * FROM products", conn)
        cart = {}
        for idx, row in prods.iterrows():
            qty = st.number_input(f"{row['name']} (متوفر: {row['quantity']})", min_value=0, step=1, key=f"q_{idx}")
            if qty > 0: cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
        if cart and st.button("✅ إتمام البيع"):
            total = sum(d['price'] * d['qty'] for d in cart.values())
            c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_c, str(cart), int(total), str(date.today()), "نقد"))
            for n, d in cart.items(): c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
            conn.commit(); st.success("تم الحفظ بنجاح!"); st.rerun()

with tabs[1]: # المخزن
    st.header("📦 عرض المخزن")
    st.dataframe(pd.read_sql("SELECT * FROM products", conn), use_container_width=True)

with tabs[2]: # الفواتير
    st.header("🧾 سجل الفواتير وتوليد الـ PDF (عربي / إنجليزي)")
    invs_df = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    if invs_df.empty:
        st.info("لا توجد فواتير مسجلة حتى الآن.")
    else:
        for _, row in invs_df.iterrows():
            with st.expander(f"فاتورة رقم #{row['rowid']} - العميل: {row['customer_name']} | التاريخ: {row['date']}"):
                items = ast.literal_eval(row['items'])
                st.table(pd.DataFrame(items).T)
                
                # إعداد الـ PDF مع دعم الخطوط العربية والإنجليزية (Unicode)
                pdf = FPDF()
                pdf.add_page()
                
                # محاولة تحميل خط يدعم العربية (DejaVuSans المدمج في السيرفر)
                font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
                font_bold_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
                
                if os.path.exists(font_path):
                    pdf.add_font('UnicodeFont', '', font_path, uni=True)
                    if os.path.exists(font_bold_path):
                        pdf.add_font('UnicodeFont', 'B', font_bold_path, uni=True)
                    else:
                        pdf.add_font('UnicodeFont', 'B', font_path, uni=True)
                    pdf.set_font('UnicodeFont', 'B', 16)
                else:
                    pdf.set_font("Arial", 'B', 16)

                # رأس الفاتورة (مزدوج اللغة)
                pdf.cell(200, 10, "INVOICE / فاتورة مبيعات", ln=True, align='C')
                
                if os.path.exists(font_path):
                    pdf.set_font('UnicodeFont', '', 12)
                else:
                    pdf.set_font("Arial", size=12)
                    
                pdf.ln(5)
                pdf.cell(200, 8, f"Invoice ID / رقم الفاتورة: #{row['rowid']}", ln=True)
                pdf.cell(200, 8, f"Customer Name / اسم العميل: {row['customer_name']}", ln=True)
                pdf.cell(200, 8, f"Date / التاريخ: {row['date']}", ln=True)
                pdf.ln(5)
                
                # جدول الفاتورة
                if os.path.exists(font_path):
                    pdf.set_font('UnicodeFont', 'B', 10)
                else:
                    pdf.set_font("Arial", 'B', 10)
                    
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(80, 10, "Item Name / اسم المادة", border=1, fill=True, align='C')
                pdf.cell(30, 10, "Qty / الكمية", border=1, fill=True, align='C')
                pdf.cell(40, 10, "Price / السعر", border=1, fill=True, align='C')
                pdf.cell(40, 10, "Total / الإجمالي", border=1, fill=True, ln=True, align='C')
                
                if os.path.exists(font_path):
                    pdf.set_font('UnicodeFont', '', 10)
                else:
                    pdf.set_font("Arial", size=10)
                    
                for item_name, data in items.items():
                    q = data['qty']
                    p = data['price']
                    tot = q * p
                    pdf.cell(80, 9, str(item_name), border=1, align='L')
                    pdf.cell(30, 9, str(q), border=1, align='C')
                    pdf.cell(40, 9, str(p), border=1, align='R')
                    pdf.cell(40, 9, str(tot), border=1, ln=True, align='R')
                
                pdf.ln(5)
                if os.path.exists(font_path):
                    pdf.set_font('UnicodeFont', 'B', 12)
                else:
                    pdf.set_font("Arial", 'B', 12)
                    
                pdf.cell(190, 10, f"GRAND TOTAL / المجموع الكلي: {row['total']} IQD", border=1, align='R')
                
                # تحويل آمن لبيانات الـ PDF للتحميل
                raw_pdf = pdf.output()
                if isinstance(raw_pdf, str):
                    pdf_data = raw_pdf.encode('latin-1')
                else:
                    pdf_data = bytes(raw_pdf)

                st.download_button(
                    label="📥 تحميل الفاتورة PDF (عربي/إنجليزي)", 
                    data=pdf_data, 
                    file_name=f"invoice_{row['rowid']}.pdf", 
                    mime="application/pdf",
                    key=f"dl_pdf_{row['rowid']}"
                )

with tabs[3]: # العملاء
    st.header("👥 العملاء")
    with st.form("add_c", clear_on_submit=True):
        n = st.text_input("اسم العميل / المحل")
        p = st.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة"): 
            if n:
                c.execute("INSERT INTO customers VALUES (?,?)", (n, p))
                conn.commit()
                st.success("تم إضافة العميل بنجاح!")
                st.rerun()
            else:
                st.warning("أدخل اسم العميل على الأقل.")
    st.table(pd.read_sql("SELECT * FROM customers", conn))

with tabs[4]: # المساعد الذكي وجرد المخزن
    st.header("🤖 المساعد الذكي - جرد المخزن")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("➕ إضافة مادة جديدة")
        with st.form("add_p", clear_on_submit=True):
            n = st.text_input("اسم المادة")
            p = st.number_input("السعر", min_value=0, step=1)
            q = st.number_input("الكمية", min_value=0, step=1)
            if st.form_submit_button("حفظ المادة"):
                if n:
                    c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q))
                    conn.commit()
                    st.success("تم حفظ المادة بنجاح!")
                    st.rerun()
                else:
                    st.warning("أدخل اسم المادة.")
    with c2:
        st.subheader("📊 جرد المخزن الشامل")
        st.dataframe(pd.read_sql("SELECT * FROM products", conn), use_container_width=True)
        if st.button("🔍 فحص النواقص"):
            low_stock = pd.read_sql("SELECT * FROM products WHERE quantity < 5", conn)
            if not low_stock.empty:
                st.warning("مواد شارفت على النفاذ:")
                st.table(low_stock)
            else:
                st.success("المخزن بحالة ممتازة ولا توجد نواقص حرجة.")
