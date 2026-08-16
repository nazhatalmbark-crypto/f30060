import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي", layout="wide", page_icon="📦")

# --- 1. إعداد وتحديث قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT UNIQUE, 
                    quantity INTEGER DEFAULT 0, 
                    price INTEGER DEFAULT 0,
                    selling_price INTEGER DEFAULT 0
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    phone TEXT, 
                    shop_location TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    customer_name TEXT, 
                    total_amount INTEGER, 
                    invoice_date TEXT, 
                    details_json TEXT
                )''')
    
    for col, col_type in [("received_amount", "INTEGER DEFAULT 0"), 
                          ("remaining_amount", "INTEGER DEFAULT 0")]:
        try:
            c.execute(f"ALTER TABLE invoices ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass
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
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Invoice ID: #{inv_id}", ln=True)
    pdf.cell(200, 10, txt=f"Customer: {safe(c_name)}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Total Amount: {total:,} IQD", ln=True)
    pdf.cell(200, 10, txt=f"Paid Amount: {received:,} IQD", ln=True)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(200, 10, txt=f"Remaining Debt: {remaining:,} IQD", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=safe(details))
    return pdf.output(dest='S')

# --- حالة الترخيص ---
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- الشريط الجانبي ---
st.sidebar.title("🛡️ لوحة التحكم")
if not st.session_state.is_unlocked:
    st.sidebar.warning("⚠️ النسخة التجريبية (5 مواد)")
    act_code = st.sidebar.text_input("كود التفعيل:", type="password")
    if st.sidebar.button("تفعيل"):
        if act_code == "2009": st.session_state.is_unlocked = True; st.rerun()
        else: st.sidebar.error("خطأ!")
else:
    st.sidebar.success("✅ النسخة الكاملة")

# --- التبويبات ---
tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "🔍 التحليل والأرباح", "🔍 ذمم العملاء", "👥 العملاء"])

with tabs[0]: # البيع
    st.subheader("🛒 نقطة البيع")
    items = run_query("SELECT id, name, quantity, selling_price FROM inventory WHERE quantity > 0", fetch=True)
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    if items:
        item_options = {f"{i[1]} ({i[3]:,} د.ع)": i for i in items}
        selected = st.selectbox("اختر مادة:", list(item_options.keys()))
        if st.button("إضافة للسلة"):
            it = item_options[selected]
            st.session_state.cart.append({'id': it[0], 'name': it[1], 'price': it[3], 'qty': 1})
            st.rerun()
            
        if st.session_state.cart:
            grand_total = sum(i['price'] * i['qty'] for i in st.session_state.cart)
            st.markdown(f"### الإجمالي: `{grand_total:,} د.ع`")
            received = st.number_input("المبلغ المستلم:", min_value=0, value=grand_total)
            remaining = grand_total - received
            custs = run_query("SELECT name FROM customers", fetch=True)
            c_name = st.selectbox("العميل:", [c[0] for c in custs] if custs else [])
            
            if st.button("إتمام البيع"):
                if c_name:
                    csv_data = pd.DataFrame(st.session_state.cart).to_csv(index=False)
                    run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, invoice_date, details_json) VALUES (?, ?, ?, ?, ?, ?)",
                              (c_name, grand_total, received, remaining, str(date.today()), csv_data))
                    for item in st.session_state.cart:
                        run_query("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (item['qty'], item['id']))
                    st.session_state.cart = []
                    st.success("تم البيع!")
                    st.rerun()

with tabs[1]: # الأرشيف
    st.subheader("📜 الأرشيف")
    invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True)
    for i in invs:
        with st.container(border=True):
            if i[4] > 0: st.error(f"فاتورة #{i[0]} - العميل: {i[1]} (دين: {i[4]:,})")
            else: st.warning(f"فاتورة #{i[0]} - العميل: {i[1]} (نقد)")
            pdf_data = generate_pdf(i[0], i[1], i[2], i[3], i[4], i[5])
            st.download_button("📥 تحميل الفاتورة", pdf_data, f"inv_{i[0]}.pdf", "application/pdf")

with tabs[2]: # المخزن (مدمج مع إضافة المواد)
    st.subheader("📦 إدارة المخزن")
    
    # قسم إضافة المواد
    with st.expander("➕ إضافة مادة جديدة للمخزن"):
        count = run_query("SELECT COUNT(*) FROM inventory", fetch=True)[0][0]
        if not st.session_state.is_unlocked and count >= 5:
            st.warning("⚠️ النسخة التجريبية (5 مواد فقط). فعل النسخة الكاملة!")
        else:
            with st.form("add_item"):
                n = st.text_input("اسم المادة")
                q = st.number_input("الكمية", 0)
                c = st.number_input("التكلفة", 0)
                s = st.number_input("البيع", 0)
                if st.form_submit_button("حفظ"):
                    run_query("INSERT OR REPLACE INTO inventory (name, quantity, price, selling_price) VALUES (?, ?, ?, ?)", (n, q, c, s))
                    st.rerun()

    st.divider()
    # عرض المخزن
    items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
    cols = st.columns(3)
    for idx, itm in enumerate(items):
        with cols[idx % 3]:
            with st.container(border=True):
                st.write(f"### {itm[1]}")
                st.write(f"الكمية: {itm[2]} | البيع: {itm[4]}")
                if st.button("حذف", key=f"del_{itm[0]}"):
                    run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                    st.rerun()

with tabs[3]: # تحليل المواد
    st.subheader("🔍 تحليل الأرباح")
    items_list = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
    if items_list:
        name = st.selectbox("اختر الصنف:", [it[1] for it in items_list])
        it = next(i for i in items_list if i[1] == name)
        # حساب المبيعات من الفواتير
        all_invs = run_query("SELECT details_json FROM invoices", fetch=True)
        sold = 0
        for inv in all_invs:
            if inv[0]:
                df = pd.read_csv(StringIO(inv[0]))
                if name in df['name'].values:
                    sold += int(df.loc[df['name'] == name, 'qty'].values[0])
        st.metric("إجمالي المبيعات", f"{sold} قطعة")
        st.metric("صافي الربح", f"{(it[4]-it[3])*sold:,} د.ع")

with tabs[4]: # الذمم
    st.subheader("🔍 ذمم العملاء")
    debts = run_query("SELECT customer_name, SUM(remaining_amount) FROM invoices GROUP BY customer_name HAVING SUM(remaining_amount) > 0", fetch=True)
    for d in debts: st.metric(f"العميل: {d[0]}", f"{d[1]:,} د.ع")

with tabs[5]: # العملاء
    st.subheader("👥 إدارة العملاء")
    with st.form("cust"):
        name = st.text_input("اسم العميل")
        if st.form_submit_button("حفظ"):
            run_query("INSERT INTO customers (name) VALUES (?)", (name,))
            st.rerun()
    custs = run_query("SELECT name FROM customers", fetch=True)
    for c in custs: st.write(f"- {c[0]}")
