import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي", layout="wide", page_icon="📦")

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0, selling_price INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, shop_location TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, total_amount INTEGER, received_amount INTEGER, remaining_amount INTEGER, invoice_date TEXT, details_json TEXT)''')
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

# --- دالة PDF ---
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

# --- الحالة ---
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- Sidebar ---
st.sidebar.title("🔐 إدارة النسخة")
if not st.session_state.is_unlocked:
    st.sidebar.warning("⚠️ النسخة المجانية (5 مواد)")
    code = st.sidebar.text_input("كود التفعيل (2009):", type="password")
    if st.sidebar.button("تفعيل"):
        if code == "2009": st.session_state.is_unlocked = True; st.rerun()
else:
    st.sidebar.success("✅ النسخة الكاملة")

st.sidebar.divider()
try:
    with open("yasser_web.db", "rb") as f:
        st.sidebar.download_button("📥 نسخة احتياطية", f, "backup.db")
except: pass

# --- التبويبات ---
tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "🔍 الأرباح", "👥 العملاء"])

with tabs[0]: # البيع
    st.subheader("🛒 نقطة البيع")
    items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory WHERE quantity > 0", fetch=True)
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    if items:
        cols = st.columns(3)
        for idx, itm in enumerate(items):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.write(f"### {itm[1]}")
                    st.write(f"المتوفر: {itm[2]} | السعر: {int(itm[4]):,} د.ع")
                    if st.button("➕ إضافة", key=f"add_{itm[0]}"):
                        st.session_state.cart.append({'id': itm[0], 'name': itm[1], 'price': itm[4], 'qty': 1})
                        st.rerun()
    
    if st.session_state.cart:
        st.divider()
        st.write("### السلة")
        total = sum(i['price'] for i in st.session_state.cart)
        st.write(f"**الإجمالي: {int(total):,} د.ع**")
        # مبلغ مستلم بخطوات 1000
        rec = st.number_input("المبلغ المستلم:", value=int(total), step=1000)
        c_name = st.selectbox("العميل:", [c[0] for c in run_query("SELECT name FROM customers", fetch=True)] or [])
        if st.button("حفظ الفاتورة"):
            run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, invoice_date, details_json) VALUES (?,?,?,?,?,?)",
                      (c_name, total, rec, total-rec, str(date.today()), "تم البيع"))
            for it in st.session_state.cart: run_query("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (it['id'],))
            st.session_state.cart = []
            st.rerun()

with tabs[1]: # الأرشيف
    for i in run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True):
        with st.container(border=True):
            st.write(f"فاتورة #{i[0]} | العميل: {i[1]} | المتبقي: {int(i[4]):,}")
            st.download_button(f"📥 PDF #{i[0]}", generate_pdf(i[0], i[1], i[2], i[3], i[4], i[5]), f"inv_{i[0]}.pdf")

with tabs[2]: # المخزن (مع ربح القطعة)
    st.subheader("📦 إدارة المخزن")
    count = run_query("SELECT COUNT(*) FROM inventory", fetch=True)[0][0]
    with st.expander("➕ إضافة مادة"):
        if not st.session_state.is_unlocked and count >= 5: st.warning("فعل النسخة الكاملة!")
        else:
            with st.form("new"):
                n, q, c, s = st.text_input("اسم المادة"), st.number_input("الكمية"), st.number_input("التكلفة"), st.number_input("البيع")
                if st.form_submit_button("حفظ"):
                    run_query("INSERT INTO inventory (name, quantity, price, selling_price) VALUES (?,?,?,?)", (n, q, c, s))
                    st.rerun()
    
    st.divider()
    cols = st.columns(3)
    items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
    for idx, itm in enumerate(items):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {itm[1]}")
                st.write(f"الكمية: **{itm[2]}**")
                # الحساب الجديد للربح
                profit = itm[4] - itm[3]
                st.write(f"الربح/قطعة: {int(profit):,} د.ع")
                if st.button("حذف", key=f"d{itm[0]}"):
                    run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                    st.rerun()

with tabs[3]: # الأرباح
    for i in run_query("SELECT name, price, selling_price FROM inventory", fetch=True):
        st.write(f"{i[0]}: ربح الوحدة {int(i[2]-i[1]):,} د.ع")

with tabs[4]: # العملاء (كامل)
    with st.form("cust"):
        cn, cp, cl = st.text_input("الاسم"), st.text_input("الهاتف"), st.text_input("العنوان")
        if st.form_submit_button("حفظ"):
            run_query("INSERT INTO customers (name, phone, shop_location) VALUES (?,?,?)", (cn, cp, cl))
            st.rerun()
    for c in run_query("SELECT name, phone, shop_location FROM customers", fetch=True):
        st.write(f"👤 {c[0]} | 📞 {c[1]} | 📍 {c[2]}")
