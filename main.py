import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي", layout="wide", page_icon="📦")

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    # التأكد من وجود الأعمدة المطلوبة
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT UNIQUE, quantity INTEGER, price INTEGER, selling_price INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, shop_location TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    customer_name TEXT, total_amount INTEGER, 
                    received_amount INTEGER, remaining_amount INTEGER,
                    invoice_date TEXT, details_json TEXT
                )''')
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

# --- دالة توليد PDF (محدثة لتوضيح الدين) ---
def generate_pdf(inv_id, c_name, total, received, remaining, details):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # تحويل النصوص لترميز آمن
    def safe(text): return str(text).encode('latin-1', 'replace').decode('latin-1')

    pdf.cell(200, 10, txt="Yasser Web - Invoice", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Invoice ID: #{inv_id}", ln=True)
    pdf.cell(200, 10, txt=f"Customer: {safe(c_name)}", ln=True)
    pdf.ln(5)
    
    # قسم الحسابات
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Total Amount: {total:,} IQD", ln=True)
    pdf.cell(200, 10, txt=f"Paid Amount: {received:,} IQD", ln=True)
    pdf.set_text_color(200, 0, 0) # لون أحمر للمتبقي
    pdf.cell(200, 10, txt=f"Remaining Debt: {remaining:,} IQD", ln=True)
    pdf.set_text_color(0, 0, 0) # عودة للأسود
    
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=safe(details))
    return pdf.output(dest='S')

# --- الواجهة ---
tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "🔍 ذمم العملاء", "👥 العملاء"])

with tabs[0]: # البيع
    st.subheader("🛒 نقطة البيع")
    items = run_query("SELECT id, name, selling_price FROM inventory WHERE quantity > 0", fetch=True)
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    item_options = {f"{i[1]} ({i[2]} د.ع)": i for i in items}
    selected_item_display = st.selectbox("اختر مادة:", list(item_options.keys()))
    if st.button("إضافة للسلة"):
        it = item_options[selected_item_display]
        st.session_state.cart.append({'id': it[0], 'name': it[1], 'price': it[2], 'qty': 1})
        st.rerun()
        
    if st.session_state.cart:
        grand_total = sum(i['price'] * i['qty'] for i in st.session_state.cart)
        st.markdown(f"### الإجمالي الكلي: `{grand_total:,} د.ع`")
        
        # حقل المبلغ المستلم
        received_amt = st.number_input("المبلغ المستلم (نقداً):", min_value=0, value=grand_total)
        remaining_amt = grand_total - received_amt
        st.info(f"المبلغ المتبقي (دين): {remaining_amt:,} د.ع")
        
        custs = run_query("SELECT name FROM customers", fetch=True)
        c_name = st.selectbox("اختر العميل:", [c[0] for c in custs] if custs else [])
        
        if st.button("إتمام البيع"):
            if c_name:
                csv_data = pd.DataFrame(st.session_state.cart).to_csv(index=False)
                run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, invoice_date, details_json) VALUES (?, ?, ?, ?, ?, ?)",
                          (c_name, grand_total, received_amt, remaining_amt, str(date.today()), csv_data))
                
                for item in st.session_state.cart:
                    run_query("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (item['qty'], item['id']))
                
                st.session_state.cart = []
                st.success("تم الحفظ!")
                st.rerun()

with tabs[1]: # الأرشيف
    invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True)
    for i in invs:
        # إذا المتبقي > 0 يظهر باللون الأحمر (Error)، إذا 0 يظهر بالأصفر (Warning)
        container_type = st.error if i[4] > 0 else st.warning
        with container_type():
            st.markdown(f"**فاتورة #{i[0]} | العميل: {i[1]}**")
            st.write(f"المجموع: {i[2]:,} | المستلم: {i[3]:,} | المتبقي: {i[4]:,}")
            
            # PDF المحدث
            pdf_data = generate_pdf(i[0], i[1], i[2], i[3], i[4], i[5])
            st.download_button("📥 تحميل الفاتورة", pdf_data, f"inv_{i[0]}.pdf", "application/pdf")

with tabs[3]: # ذمم العملاء
    st.subheader("🔍 ذمم العملاء")
    debts = run_query("SELECT customer_name, SUM(remaining_amount) FROM invoices GROUP BY customer_name HAVING SUM(remaining_amount) > 0", fetch=True)
    if debts:
        for d in debts:
            st.metric(f"العميل: {d[0]}", f"{d[1]:,} د.ع")
    else:
        st.info("لا توجد ديون مسجلة.")
