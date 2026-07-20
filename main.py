import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import ast
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
conn.commit()

# --- دالة حماية النصوص للـ PDF ---
def safe_pdf_text(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def hash_pw(pw): 
    return hashlib.sha256(pw.encode()).hexdigest()

c.execute("SELECT COUNT(*) FROM users")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users VALUES (?, ?)", ("admin", hash_pw("1234")))
    conn.commit()

# --- نظام تسجيل الدخول (مع دعم تسجيل دخول الضيف المسؤول عنه) ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'is_guest' not in st.session_state:
    st.session_state.is_guest = False

if not st.session_state.logged_in:
    st.title("🔐 Eng. Yasser Pro System - تسجيل الدخول")
    
    tab_login, tab_guest = st.tabs(["🔑 تسجيل دخول المسؤول", "👤 دخول الضيف"])
    
    with tab_login:
        user = st.text_input("اسم المستخدم", key="admin_user")
        pw = st.text_input("كلمة المرور", type="password", key="admin_pw")
        if st.button("دخول كمسؤول"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, hash_pw(pw)))
            if c.fetchone(): 
                st.session_state.logged_in = True
                st.session_state.is_guest = False
                st.rerun()
            else: 
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")
                
    with tab_guest:
        st.write("يمكنك الدخول السريع كضيف لاستعراض النظام واستخدام المميزات المتاحة.")
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

tabs = st.tabs(["🛒 البيع", "📦 عرض المخزن", "🧾 الفواتير", "👥 إدارة العملاء", "🤖 المساعد الذكي"])

# --- 1. تبويب البيع ---
with tabs[0]:
    st.header("🛒 نقطة البيع والطلب")
    custs = pd.read_sql("SELECT name FROM customers", conn)
    if custs.empty:
        st.warning("يرجى إضافة عملاء أولاً من تبويب 'إدارة العملاء'!")
    else:
        selected_c = st.selectbox("اختر العميل", ["اختر العميل..."] + custs['name'].tolist())
        prods = pd.read_sql("SELECT rowid, * FROM products", conn)
        
        current_cart = {}
        for idx, row in prods.iterrows():
            qty = st.number_input(f"مادة: {row['name']} | السعر: {row['price_carton']} د.ع | (المتوفر: {row['quantity']})", min_value=0, step=1, key=f"q_{idx}")
            if qty > 0:
                current_cart[row['name']] = {'price': int(row['price_carton']), 'qty': int(qty)}
        
        if current_cart:
            st.subheader("📋 سلة المشتريات:")
            cart_df = pd.DataFrame.from_dict(current_cart, orient='index')
            cart_df.columns = ['السعر', 'الكمية']
            cart_df['الإجمالي'] = cart_df['السعر'] * cart_df['الكمية']
            st.table(cart_df)
            
            total_amount = cart_df['الإجمالي'].sum()
            st.info(f"المجموع الكلي: {total_amount} د.ع")
            
            if selected_c != "اختر العميل...":
                if st.button("✅ إتمام البيع"):
                    c.execute("INSERT INTO invoices VALUES (?,?,?,?,?)", (selected_c, str(current_cart), int(total_amount), str(date.today()), "نقد"))
                    for n, d in current_cart.items(): 
                        c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (int(d['qty']), n))
                    conn.commit()
                    st.success("تم الحفظ بنجاح!")
                    st.rerun()
            else:
                st.warning("الرجاء اختيار العميل.")

# --- 2. تبويب المخزن ---
with tabs[1]:
    st.header("📦 عرض المخزن")
    st.dataframe(pd.read_sql("SELECT rowid as ID, name as 'اسم المادة', price_carton as 'السعر', quantity as 'الكمية' FROM products", conn), use_container_width=True)

# --- 3. تبويب الفواتير وتوليد الـ PDF ---
with tabs[2]:
    st.header("🧾 سجل الفواتير وتوليد الـ PDF")
    invs = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    if invs.empty:
        st.info("لا توجد فواتير مسجلة حتى الآن.")
    else:
        for _, row in invs.iterrows():
            with st.expander(f"فاتورة رقم #{row['rowid']} | العميل: {row['customer_name']} | التاريخ: {row['date']} | المجموع: {row['total']} د.ع"):
                items = ast.literal_eval(row['items'])
                
                df_items = pd.DataFrame.from_dict(items, orient='index')
                df_items.columns = ['السعر', 'الكمية']
                df_items['الإجمالي'] = df_items['السعر'] * df_items['الكمية']
                st.table(df_items)
                st.write(f"**المجموع الكلي:** {row['total']} د.ع")
                
                # توليد PDF احترافي ومنسق
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="INVOICE / فاتورة مبيعات", ln=True, align='C')
                pdf.set_font("Arial", size=11)
                pdf.cell(200, 8, txt=f"Invoice ID: #{row['rowid']}", ln=True)
                pdf.cell(200, 8, txt=f"Customer Name: {safe_pdf_text(row['customer_name'])}", ln=True)
                pdf.cell(200, 8, txt=f"Date: {row['date']}", ln=True)
                pdf.ln(5)
                
                pdf.set_fill_color(220, 220, 220)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(80, 10, "Item Name", border=1, fill=True, align='C')
                pdf.cell(30, 10, "Qty", border=1, fill=True, align='C')
                pdf.cell(40, 10, "Price", border=1, fill=True, align='C')
                pdf.cell(40, 10, "Total", border=1, fill=True, ln=True, align='C')
                
                pdf.set_font("Arial", size=10)
                for item_name, data in items.items():
                    q = data['qty']
                    p = data['price']
                    tot = q * p
                    pdf.cell(80, 9, safe_pdf_text(item_name), border=1, align='L')
                    pdf.cell(30, 9, str(q), border=1, align='C')
                    pdf.cell(40, 9, str(p), border=1, align='R')
                    pdf.cell(40, 9, str(tot), border=1, ln=True, align='R')
                
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(190, 10, txt=f"GRAND TOTAL: {row['total']} IQD", border=1, align='R')
                
                st.download_button(
                    label=f"📥 تحميل فاتورة #{row['rowid']} PDF", 
                    data=pdf.output(dest='S').encode('latin-1'), 
                    file_name=f"invoice_{row['rowid']}.pdf",
                    key=f"dl_inv_{row['rowid']}"
                )

# --- 4. تبويب العملاء ---
with tabs[3]:
    st.header("👥 إدارة العملاء")
    with st.form("add_cust_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم العميل / المحل")
        phone = c2.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة العميل"):
            if name:
                c.execute("INSERT INTO customers (name, phone) VALUES (?,?)", (name, phone))
                conn.commit()
                st.success("تم إضافة العميل بنجاح!")
                st.rerun()
            else:
                st.warning("الرجاء إدخال اسم العميل على الأقل.")
    
    st.subheader("قائمة العملاء المسجلين:")
    st.dataframe(pd.read_sql("SELECT rowid as ID, name as 'اسم العميل', phone as 'الهاتف' FROM customers", conn), use_container_width=True)

# --- 5. تبويب المساعد الذكي وجرد المخزن ---
with tabs[4]:
    st.header("🤖 المساعد الذكي - لوحة التحكم الشاملة وجرد المخزن")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ إضافة مادة جديدة للمخزن")
        with st.form("add_p_form", clear_on_submit=True):
            n = st.text_input("اسم المادة الجديدة")
            p = st.number_input("سعر الكارتون (د.ع)", min_value=0, step=1)
            q = st.number_input("الكمية الأولية", min_value=0, step=1)
            if st.form_submit_button("حفظ المادة"):
                if n:
                    c.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q))
                    conn.commit()
                    st.success(f"تمت إضافة المادة ({n}) بنجاح!")
                    st.rerun()
                else:
                    st.warning("الرجاء إدخال اسم المادة.")
    with col2:
        st.subheader("❌ حذف مادة من المخزن")
        all_prods = pd.read_sql("SELECT name FROM products", conn)
        if not all_prods.empty:
            prod_del = st.selectbox("اختر المادة للحذف", all_prods['name'].tolist())
            if st.button("🗑️ حذف المادة المحددة"):
                c.execute("DELETE FROM products WHERE name = ?", (prod_del,))
                conn.commit()
                st.success("تم حذف المادة بنجاح!")
                st.rerun()
        else:
            st.info("لا توجد مواد في المخزن للحذف.")
    
    st.divider()
    st.subheader("📊 جرد المخزن المباشر وفحص النواقص")
    c3, c4 = st.columns([1, 2])
    with c3:
        if st.button("🔍 فحص المواد قليلة الكمية (< 5)"):
            low = pd.read_sql("SELECT * FROM products WHERE quantity < 5", conn)
            if not low.empty:
                st.warning("تنبيه: توجد مواد شارفت على النفاذ!")
                st.table(low)
            else:
                st.success("المخزن بحالة ممتازة، لا توجد نواقص حرجة!")
    with c4:
        st.write("**جرد شامل للمخزن:**")
        st.dataframe(pd.read_sql("SELECT * FROM products", conn), use_container_width=True)
