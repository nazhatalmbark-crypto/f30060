import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي", layout="wide", page_icon="📦")

# --- 1. إعداد وتحديث قاعدة البيانات بأمان ---
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
    
    # إضافة الأعمدة الجديدة بأمان إذا لم تكن موجودة في الجداول القديمة
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

# --- دالة توليد PDF للفاتورة ---
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
    
    # الحسابات المالية داخل الفاتورة
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

# --- إدارة حالة الترخيص (النسخة المجانية والمدفوعة) ---
if 'is_unlocked' not in st.session_state:
    st.session_state.is_unlocked = False

# --- الشريط الجانبي للترخيص والنسخ الاحتياطي ---
st.sidebar.title("🛡️ لوحة التحكم والأمان")
st.sidebar.subheader("🔐 حالة النسخة والترخيص")

if not st.session_state.is_unlocked:
    st.sidebar.warning("⚠️ النسخة التجريبية (بحد أقصى 5 مواد بالمخزن)")
    act_code = st.sidebar.text_input("أدخل كود التفعيل للنسخة الكاملة:", type="password")
    if st.sidebar.button("تفعيل النسخة"):
        if act_code == "2009":
            st.session_state.is_unlocked = True
            st.sidebar.success("✅ تم تفعيل النسخة الكاملة بنجاح!")
            st.rerun()
        else:
            st.sidebar.error("كود التفعيل غير صحيح!")
else:
    st.sidebar.success("✅ النسخة الكاملة مفعلة بلا حدود")
    if st.sidebar.button("إلغاء التفعيل"):
        st.session_state.is_unlocked = False
        st.rerun()

st.sidebar.divider()
try:
    with open("yasser_web.db", "rb") as f:
        db_bytes = f.read()
    st.sidebar.download_button(
        label="💾 تحميل النسخة الاحتياطية (Backup)",
        data=db_bytes,
        file_name=f"yasser_web_backup_{date.today()}.db",
        mime="application/octet-stream",
        use_container_width=True
    )
except:
    pass

# --- واجهة التبويبات الرئيسية ---
tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "➕ إضافة مواد", "🔍 ذمم العملاء", "👥 العملاء"])

with tabs[0]: # البيع
    st.subheader("🛒 نقطة البيع")
    items = run_query("SELECT id, name, quantity, selling_price FROM inventory WHERE quantity > 0", fetch=True)
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    if items:
        item_options = {f"{i[1]} (متوفر: {i[2]} | السعر: {i[3]:,} د.ع)": i for i in items}
        selected_item_display = st.selectbox("اختر مادة لإضافتها:", list(item_options.keys()))
        if st.button("إضافة للسلة ➕"):
            it = item_options[selected_item_display]
            st.session_state.cart.append({'id': it[0], 'name': it[1], 'price': it[3], 'qty': 1})
            st.rerun()
            
        if st.session_state.cart:
            st.divider()
            st.subheader("محتويات السلة:")
            grand_total = 0
            for i, c_item in enumerate(st.session_state.cart):
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(c_item['name'])
                col2.write(f"{c_item['price']:,} د.ع")
                if col3.button("حذف", key=f"del_cart_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
                grand_total += c_item['price'] * c_item['qty']
                
            st.markdown(f"### الإجمالي الكلي: `{grand_total:,} د.ع`")
            
            # حقل المبلغ المستلم
            received_amt = st.number_input("المبلغ المستلم من الزبون (نقداً):", min_value=0, value=grand_total)
            remaining_amt = grand_total - received_amt
            
            if remaining_amt > 0:
                st.error(f"⚠️ المبلغ المتبقي (دين على الزبون): {remaining_amt:,} د.ع")
            else:
                st.success("✅ الفاتورة مدفوعة بالكامل (نقداً).")
            
            custs = run_query("SELECT name FROM customers", fetch=True)
            c_name = st.selectbox("اختر اسم العميل:", [c[0] for c in custs] if custs else [])
            
            if st.button("✅ إتمام البيع وحفظ الفاتورة", use_container_width=True):
                if not c_name:
                    st.error("❌ يرجى اختيار العميل أولاً!")
                else:
                    csv_data = pd.DataFrame(st.session_state.cart).to_csv(index=False)
                    run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, invoice_date, details_json) VALUES (?, ?, ?, ?, ?, ?)",
                              (c_name, grand_total, received_amt, remaining_amt, str(date.today()), csv_data))
                    
                    # خصم الكمية من المخزن
                    for item in st.session_state.cart:
                        run_query("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (item['qty'], item['id']))
                    
                    st.session_state.cart = []
                    st.success("تم إتمام البيع وحفظ الفاتورة بنجاح!")
                    st.rerun()
    else:
        st.info("لا توجد مواد متوفرة في المخزن حالياً.")

with tabs[1]: # الأرشيف
    st.subheader("📜 أرشيف الفواتير")
    invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True)
    if invs:
        for i in invs:
            # إذا المتبقي > 0 (دين) يظهر أحمر، إذا 0 (نقد) يظهر أصفر
            container_type = st.error if i[4] > 0 else st.warning
            with container_type():
                st.markdown(f"**فاتورة #{i[0]} | العميل: {i[1]}**")
                st.write(f"المجموع: {i[2]:,} د.ع | المستلم: {i[3]:,} د.ع | المتبقي (الدين): **{i[4]:,} د.ع**")
                
                pdf_data = generate_pdf(i[0], i[1], i[2], i[3], i[4], i[5])
                st.download_button("📥 تحميل الفاتورة PDF", pdf_data, f"invoice_{i[0]}.pdf", "application/pdf", key=f"pdf_{i[0]}")
    else:
        st.info("لا توجد فواتير مسجلة.")

with tabs[2]: # المخزن
    st.subheader("📦 إدارة المخزن")
    items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
    if items:
        cols = st.columns(3)
        for idx, itm in enumerate(items):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### 🏷️ {itm[1]}")
                    st.metric("الكمية المتوفرة", f"{itm[2]} قطعة")
                    st.write(f"التكلفة: {itm[3]:,} | البيع: {itm[4]:,}")
                    if st.button("حذف المادة 🗑️", key=f"del_inv_{itm[0]}"):
                        run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                        st.rerun()
    else:
        st.info("المخزن فارغ.")

with tabs[3]: # إضافة مواد
    st.subheader("➕ إضافة مادة جديدة")
    current_items_count = run_query("SELECT COUNT(*) FROM inventory", fetch=True)[0][0]
    
    if not st.session_state.is_unlocked and current_items_count >= 5:
        st.warning("⚠️ لقد وصلت للحد الأقصى في النسخة التجريبية (5 مواد). أدخل كود التفعيل **2009** في القائمة الجانبية لفتح النسخة الكاملة!")
    
    with st.form("add_item_form"):
        col1, col2 = st.columns(2)
        with col1:
            i_name = st.text_input("اسم المادة").strip()
            i_qty = st.number_input("الكمية", min_value=0, value=10)
        with col2:
            i_cost = st.number_input("سعر التكلفة", min_value=0, value=1000)
            i_sell = st.number_input("سعر البيع", min_value=0, value=1500)
            
        if st.form_submit_button("حفظ المادة"):
            if not st.session_state.is_unlocked and current_items_count >= 5:
                st.error("❌ النسخة التجريبية محدودة بـ 5 مواد فقط!")
            elif i_name:
                run_query("INSERT OR REPLACE INTO inventory (name, quantity, price, selling_price) VALUES (?, ?, ?, ?)", 
                          (i_name, i_qty, i_cost, i_sell))
                st.success("تم حفظ المادة بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم المادة.")

with tabs[4]: # ذمم العملاء
    st.subheader("🔍 ذمم العملاء (إجمالي الديون)")
    debts = run_query("SELECT customer_name, SUM(remaining_amount) FROM invoices GROUP BY customer_name HAVING SUM(remaining_amount) > 0", fetch=True)
    if debts:
        for d in debts:
            st.metric(f"العميل: {d[0]}", f"{d[1]:,} د.ع")
    else:
        st.info("لا توجد ذمم أو ديون مترتبة على العملاء حالياً.")

with tabs[5]: # العملاء
    st.subheader("👥 إضافة وإدارة العملاء")
    with st.form("cust_form"):
        c1, c2 = st.columns(2)
        with c1:
            c_name = st.text_input("اسم الزبون أو المحل (إجباري)").strip()
            c_phone = st.text_input("رقم الهاتف")
        with c2:
            c_loc = st.text_input("عنوان المحل / المنطقة")
            
        if st.form_submit_button("حفظ الزبون"):
            if c_name:
                run_query("INSERT INTO customers (name, phone, shop_location) VALUES (?, ?, ?)", (c_name, c_phone, c_loc))
                st.success("تم حفظ الزبون بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم الزبون.")
                
    st.divider()
    saved_custs = run_query("SELECT name, phone, shop_location FROM customers", fetch=True)
    if saved_custs:
        for sc in saved_custs:
            st.markdown(f"- 👤 **{sc[0]}** | 📱 الهاتف: {sc[1] or 'لا يوجد'} | 📍 الموقع: {sc[2] or 'غير محدد'}")
    else:
        st.info("لا توجد عملاء مسجلون حتى الآن.")
