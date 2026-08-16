import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي المتكامل", layout="wide", page_icon="📦")

# --- 1. إعداد قاعدة البيانات ---
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
    pdf.cell(200, 10, txt=f"Total: {total:,} | Paid: {received:,} | Debt: {remaining:,}", ln=True)
    pdf.multi_cell(0, 10, txt=safe(details))
    return pdf.output(dest='S')

# --- الحالة والتفعيل ---
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- الشريط الجانبي ---
st.sidebar.title("🛠️ التحكم")
if not st.session_state.is_unlocked:
    st.sidebar.warning("⚠️ نسخة تجريبية")
    code = st.sidebar.text_input("كود التفعيل:", type="password")
    if st.sidebar.button("تفعيل"):
        if code == "2009": st.session_state.is_unlocked = True; st.rerun()
        else: st.sidebar.error("خطأ")
else:
    st.sidebar.success("✅ نسخة كاملة")

st.sidebar.divider()
# النسخ الاحتياطي
try:
    with open("yasser_web.db", "rb") as f:
        st.sidebar.download_button("📥 تحميل النسخة الاحتياطية", f, "backup.db", "application/octet-stream")
except: st.sidebar.error("فشل النسخ الاحتياطي")

# --- التبويبات ---
tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "🔍 الأرباح", "🔍 الذمم", "👥 العملاء"])

with tabs[0]: # البيع
    st.subheader("🛒 نقطة البيع")
    items = run_query("SELECT id, name, quantity, selling_price FROM inventory WHERE quantity > 0", fetch=True)
    if 'cart' not in st.session_state: st.session_state.cart = []
    if items:
        sel = st.selectbox("اختر مادة:", [f"{i[1]} ({i[3]:,} د.ع)" for i in items])
        if st.button("إضافة للسلة"):
            itm = next(i for i in items if f"{i[1]} ({i[3]:,} د.ع)" == sel)
            st.session_state.cart.append({'id': itm[0], 'name': itm[1], 'price': itm[3], 'qty': 1})
            st.rerun()
        if st.session_state.cart:
            total = sum(i['price'] for i in st.session_state.cart)
            st.write(f"### الإجمالي: {total:,}")
            rec = st.number_input("المستلم:", value=total)
            custs = run_query("SELECT name FROM customers", fetch=True)
            c_name = st.selectbox("العميل:", [c[0] for c in custs] if custs else [])
            if st.button("حفظ الفاتورة"):
                csv = pd.DataFrame(st.session_state.cart).to_csv(index=False)
                run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, invoice_date, details_json) VALUES (?,?,?,?,?,?)",
                          (c_name, total, rec, total-rec, str(date.today()), csv))
                for it in st.session_state.cart: run_query("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (it['id'],))
                st.session_state.cart = []
                st.success("تم!")

with tabs[1]: # الأرشيف
    st.subheader("📜 الأرشيف والفواتير")
    invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True)
    for i in invs:
        with st.container(border=True):
            st.write(f"فاتورة #{i[0]} | العميل: {i[1]} | المتبقي: {i[4]:,}")
            pdf_data = generate_pdf(i[0], i[1], i[2], i[3], i[4], i[5])
            st.download_button(f"📥 تحميل PDF لفاتورة {i[0]}", pdf_data, f"inv_{i[0]}.pdf")

with tabs[2]: # المخزن
    st.subheader("📦 إدارة المخزن")
    # إضافة مادة (فوق)
    with st.expander("➕ إضافة مادة جديدة للمخزن", expanded=True):
        with st.form("new_item"):
            n, q, c, s = st.text_input("اسم المادة"), st.number_input("الكمية"), st.number_input("التكلفة"), st.number_input("سعر البيع")
            if st.form_submit_button("حفظ"):
                run_query("INSERT INTO inventory (name, quantity, price, selling_price) VALUES (?,?,?,?)", (n, q, c, s))
                st.rerun()
    # شبكة المواد
    items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
    cols = st.columns(3)
    for idx, itm in enumerate(items):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {itm[1]}")
                st.write(f"الكمية: {itm[2]} | البيع: {itm[4]}")
                if st.button("حذف", key=f"d{itm[0]}"):
                    run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                    st.rerun()

with tabs[3]: # الأرباح
    st.subheader("🔍 الأرباح")
    itms = run_query("SELECT name, quantity, price, selling_price FROM inventory", fetch=True)
    for i in itms: st.write(f"{i[0]}: ربح الوحدة ({i[3]-i[2]})")

with tabs[4]: # الذمم
    st.subheader("🔍 ذمم العملاء")
    debts = run_query("SELECT customer_name, SUM(remaining_amount) FROM invoices GROUP BY customer_name", fetch=True)
    for d in debts: st.write(f"{d[0]}: {d[1]} د.ع")

with tabs[5]: # العملاء
    st.subheader("👥 إدارة العملاء")
    with st.form("cust"):
        cn, cp, cl = st.text_input("الاسم"), st.text_input("الهاتف"), st.text_input("العنوان")
        if st.form_submit_button("حفظ العميل"):
            run_query("INSERT INTO customers (name, phone, shop_location) VALUES (?,?,?)", (cn, cp, cl))
            st.rerun()
    for c in run_query("SELECT name, phone, shop_location FROM customers", fetch=True):
        st.write(f"👤 {c[0]} | 📞 {c[1]} | 📍 {c[2]}")
