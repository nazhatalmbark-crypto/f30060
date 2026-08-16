import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب", layout="wide")

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0, selling_price INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, shop_name TEXT, phone TEXT, shop_location TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, total_amount INTEGER, received_amount INTEGER, remaining_amount INTEGER, invoice_date TEXT, details_json TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# --- دالة توليد PDF ---
def generate_pdf(inv_id, c_name, total, received, remaining, details):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    def safe(text): return str(text).encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(200, 10, txt="Yasser Web - Invoice", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Invoice ID: #{inv_id}", ln=True)
    pdf.cell(200, 10, txt=f"Customer: {safe(c_name)}", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Total: {int(total):,} | Paid: {int(received):,} | Debt: {int(remaining):,}", ln=True)
    pdf.multi_cell(0, 10, txt=safe(details))
    return pdf.output(dest='S')

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- واجهة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("ياسر ويب")
    tab1, tab2 = st.tabs(["دخول", "حساب جديد"])
    
    with tab1:
        with st.form("login"):
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                res = run_query("SELECT password FROM system_users WHERE username = ?", (u,), fetch=True)
                if res and res[0][0] == p:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("خطأ في البيانات")
    with tab2:
        with st.form("reg"):
            nu = st.text_input("اسم المستخدم")
            np = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("تسجيل"):
                try:
                    run_query("INSERT INTO system_users (username, password) VALUES (?, ?)", (nu, np))
                    st.success("تم الإنشاء")
                except:
                    st.error("مستخدم موجود مسبقاً")
else:
    # --- الشريط الجانبي ---
    st.sidebar.write(f"مرحباً {st.session_state.username}")
    if st.sidebar.button("خروج"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.sidebar.divider()
    
    # حقل إدخال رمز التفعيل (مخفي النص ولا يحتوي على الرقم بالواجهة)
    if not st.session_state.is_unlocked:
        code_input = st.sidebar.text_input("رمز التفعيل:", type="password")
        if st.sidebar.button("تفعيل النسخة"):
            if code_input == "2009":
                st.session_state.is_unlocked = True
                st.success("تم تفعيل النسخة الكاملة!")
                st.rerun()
            else:
                st.sidebar.error("الرمز خطأ")
    else:
        st.sidebar.success("النسخة الكاملة مفعلة ✓")

    try:
        with open("yasser_web.db", "rb") as f:
            st.sidebar.download_button("نسخة احتياطية", f, "backup.db")
    except: pass

    # --- التبويبات ---
    tabs = st.tabs(["البيع", "الأرشيف", "المخزن", "الأرباح", "العملاء"])

    with tabs[0]: # البيع
        items = run_query("SELECT id, name, quantity, selling_price FROM inventory WHERE quantity > 0", fetch=True)
        if 'cart' not in st.session_state: st.session_state.cart = []
        
        if items:
            cols = st.columns(3)
            for idx, itm in enumerate(items):
                with cols[idx % 3]:
                    if st.button(f"{itm[1]} ({itm[3]})", key=f"add_{itm[0]}"):
                        found = False
                        for c in st.session_state.cart:
                            if c['id'] == itm[0]: c['qty'] += 1; found = True
                        if not found: st.session_state.cart.append({'id': itm[0], 'name': itm[1], 'price': itm[3], 'qty': 1})
                        st.rerun()
        
        if st.session_state.cart:
            st.divider()
            for idx, c in enumerate(st.session_state.cart):
                c1, c2, c3 = st.columns(3)
                c1.write(c['name'])
                c2.write(str(c['qty']))
                if c3.button("حذف", key=f"del_{idx}"): st.session_state.cart.pop(idx); st.rerun()
            
            total = sum(i['price'] * i['qty'] for i in st.session_state.cart)
            st.write(f"الإجمالي: {total}")
            rec = st.text_input("المستلم", value=str(total))
            custs = run_query("SELECT name FROM customers", fetch=True)
            c_name = st.selectbox("العميل", [c[0] for c in custs] if custs else [])
            
            if st.button("حفظ"):
                csv = pd.DataFrame(st.session_state.cart).to_csv(index=False)
                run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, details_json) VALUES (?,?,?,?,?)",
                          (c_name, total, int(rec), total-int(rec), csv))
                for it in st.session_state.cart: run_query("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (it['qty'], it['id']))
                st.session_state.cart = []
                st.rerun()

    with tabs[1]: # الأرشيف
        invs = run_query("SELECT id, customer_name, total_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True)
        for i in invs:
            st.write(f"فاتورة {i[0]} | العميل: {i[1]} | المتبقي: {i[3]}")
            if st.button("حذف الفاتورة", key=f"del_inv_{i[0]}"): 
                run_query("DELETE FROM invoices WHERE id = ?", (i[0],))
                st.rerun()

    with tabs[2]: # المخزن
        with st.form("new"):
            n = st.text_input("اسم المادة")
            q = st.text_input("الكمية")
            s = st.text_input("السعر")
            if st.form_submit_button("إضافة"):
                run_query("INSERT INTO inventory (name, quantity, price, selling_price) VALUES (?,?,?,?)", (n, int(q), 0, int(s)))
                st.rerun()
        
        items = run_query("SELECT id, name FROM inventory", fetch=True)
        for i in items:
            if st.button(f"حذف المادة: {i[1]}", key=f"del_m_{i[0]}"): 
                run_query("DELETE FROM inventory WHERE id = ?", (i[0],))
                st.rerun()

    with tabs[3]: # الأرباح
        if st.session_state.is_unlocked:
            st.write("تحليل الأرباح الكامل")
        else:
            st.warning("هذه الميزة تتطلب تفعيل النسخة المدفوعة.")
    
    with tabs[4]: # العملاء
        with st.form("cust"):
            cn = st.text_input("اسم العميل")
            if st.form_submit_button("إضافة"):
                run_query("INSERT INTO customers (name) VALUES (?)", (cn,))
                st.rerun()
        
        custs = run_query("SELECT id, name FROM customers", fetch=True)
        for c in custs:
            if st.button(f"حذف العميل: {c[1]}", key=f"del_c_{c[0]}"): 
                run_query("DELETE FROM customers WHERE id = ?", (c[0],))
                st.rerun()
