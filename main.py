import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
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
    pdf.cell(200, 10, txt=f"Total: {int(total):,} | Paid: {int(received):,} | Debt: {int(remaining):,}", ln=True)
    pdf.multi_cell(0, 10, txt=safe(details))
    return pdf.output(dest='S')

# --- حالة النسخة ---
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- الشريط الجانبي (الرمز والتفعيل والنسخ الاحتياطي) ---
st.sidebar.title("🔐 إدارة النسخة والترخيص")
if not st.session_state.is_unlocked:
    st.sidebar.warning("⚠️ النسخة المجانية (محدودة بـ 5 مواد فقط)")
    code = st.sidebar.text_input("أدخل رمز التفعيل (2009):", type="password")
    if st.sidebar.button("تفعيل النسخة الكاملة"):
        if code == "2009":
            st.session_state.is_unlocked = True
            st.success("تم تفعيل النسخة الكاملة بنجاح!")
            st.rerun()
        else:
            st.sidebar.error("الرمز خطأ، حاول مجدداً")
else:
    st.sidebar.success("✅ النسخة الكاملة مفعلة")

st.sidebar.divider()
try:
    with open("yasser_web.db", "rb") as f:
        st.sidebar.download_button("📥 تحميل النسخة الاحتياطية", f, "backup.db")
except:
    pass

# --- التبويبات ---
tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "🔍 الأرباح", "👥 العملاء"])

with tabs[0]: # نقطة البيع (شبكة بطاقات)
    st.subheader("🛒 نقطة البيع (اختر المواد كبطاقات)")
    items = run_query("SELECT id, name, quantity, selling_price FROM inventory WHERE quantity > 0", fetch=True)
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    if items:
        st.write("### المواد المتوفرة في المخزن:")
        cols = st.columns(3)
        for idx, itm in enumerate(items):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {itm[1]}")
                    st.write(f"الكمية المتاحة: {itm[2]}")
                    st.write(f"سعر البيع: {int(itm[3]):,} د.ع")
                    if st.button("➕ إضافة للسلة", key=f"pos_add_{itm[0]}"):
                        found = False
                        for cart_item in st.session_state.cart:
                            if cart_item['id'] == itm[0]:
                                if cart_item['qty'] < itm[2]:
                                    cart_item['qty'] += 1
                                    found = True
                                else:
                                    st.warning("الكمية المطلوبة تتجاوز المخزون!")
                                    found = True
                                break
                        if not found:
                            st.session_state.cart.append({'id': itm[0], 'name': itm[1], 'price': itm[3], 'qty': 1})
                        st.rerun()
    else:
        st.info("لا توجد مواد متوفرة للبيع حالياً في المخزن.")

    st.divider()
    st.subheader("🛒 سلة المشتريات والفاتورة الحالية")
    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df[['name', 'price', 'qty']], use_container_width=True)
        
        total = sum(i['price'] * i['qty'] for i in st.session_state.cart)
        st.write(f"### الإجمالي الكلي: {int(total):,} د.ع")
        
        rec = st.number_input("المبلغ المستلم:", value=int(total), step=1000)
        custs = run_query("SELECT name FROM customers", fetch=True)
        c_name = st.selectbox("اختر العميل:", [c[0] for c in custs] if custs else [])
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 حفظ الفاتورة وإتمام البيع"):
                details_str = "\n".join([f"- {item['name']} | العدد: {item['qty']} | السعر: {item['price']:,}" for item in st.session_state.cart])
                csv = pd.DataFrame(st.session_state.cart).to_csv(index=False)
                run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, invoice_date, details_json) VALUES (?,?,?,?,?,?)",
                          (c_name, total, rec, total-rec, str(date.today()), details_str))
                for it in st.session_state.cart: 
                    run_query("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (it['qty'], it['id']))
                st.session_state.cart = []
                st.success("تم حفظ الفاتورة بنجاح!")
                st.rerun()
        with col_btn2:
            if st.button("🗑️ تفريغ السلة"):
                st.session_state.cart = []
                st.rerun()
    else:
        st.info("السلة فارغة. اضغط على زر 'إضافة للسلة' في أي مادة بالاعلى لإضافتها.")

with tabs[1]: # الأرشيف
    st.subheader("📜 أرشيف الفواتير و تحميل الـ PDF")
    invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True)
    if invs:
        for i in invs:
            with st.container(border=True):
                st.write(f"فاتورة #{i[0]} | العميل: {i[1]} | الإجمالي: {int(i[2]):,} | المتبقي: {int(i[4]):,}")
                st.text(f"التفاصيل:\n{i[5]}")
                pdf_data = generate_pdf(i[0], i[1], i[2], i[3], i[4], i[5])
                st.download_button(f"📥 تحميل فاتورة #{i[0]} PDF", pdf_data, f"inv_{i[0]}.pdf", key=f"pdf_{i[0]}")
    else:
        st.info("لا توجد فواتير محفوظة بعد.")

with tabs[2]: # المخزن (شبكة 3 أعمدة + قيد النسخة المجانية)
    st.subheader("📦 إدارة المخزن (عرض شبكي)")
    count = run_query("SELECT COUNT(*) FROM inventory", fetch=True)[0][0]
    
    with st.expander("➕ إضافة مادة جديدة للمخزن", expanded=True):
        if not st.session_state.is_unlocked and count >= 5:
            st.warning("⚠️ وصلت لحد النسخة المجانية (5 مواد فقط). أدخل رمز التفعيل (2009) في الشريط الجانبي لفتح النسخة الكاملة!")
        else:
            with st.form("new_item_form"):
                n = st.text_input("اسم المادة")
                q = st.number_input("الكمية", min_value=0, step=1)
                c = st.number_input("سعر التكلفة", min_value=0, step=1000)
                s = st.number_input("سعر البيع", min_value=0, step=1000)
                if st.form_submit_button("حفظ المادة"):
                    if n.strip() == "":
                        st.error("يرجى إدخال اسم المادة")
                    else:
                        try:
                            run_query("INSERT INTO inventory (name, quantity, price, selling_price) VALUES (?,?,?,?)", (n, q, c, s))
                            st.success("تمت الإضافة بنجاح!")
                            st.rerun()
                        except:
                            st.error("المادة موجودة مسبقاً أو حدث خطأ!")
    
    st.divider()
    items = run_query("SELECT id, name, quantity, selling_price FROM inventory", fetch=True)
    if items:
        cols = st.columns(3)
        for idx, itm in enumerate(items):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {itm[1]}")
                    st.write(f"الكمية: {itm[2]} | البيع: {int(itm[3]):,} د.ع")
                    if st.button("حذف", key=f"del_inv_{itm[0]}"):
                        run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                        st.rerun()
    else:
        st.info("المخزن فارغ حالياً.")

with tabs[3]: # الأرباح
    st.subheader("🔍 تقرير الأرباح")
    itms = run_query("SELECT name, price, selling_price FROM inventory", fetch=True)
    if itms:
        for i in itms:
            profit = i[2] - i[1]
            st.write(f"🏷️ **{i[0]}**: ربح الوحدة = {int(profit):,} د.ع")
    else:
        st.info("لا توجد مواد لحساب الأرباح.")

with tabs[4]: # العملاء (جميع الحقول الثلاثة كاملة تماماً)
    st.subheader("👥 إدارة العملاء (الحقول الثلاثة كاملة)")
    with st.form("cust_form"):
        cn = st.text_input("اسم الزبون")
        cp = st.text_input("رقم الهاتف")
        cl = st.text_input("عنوان المحل")
        if st.form_submit_button("حفظ الزبون"):
            if cn.strip() == "":
                st.error("يرجى إدخال اسم الزبون على الأقل")
            else:
                run_query("INSERT INTO customers (name, phone, shop_location) VALUES (?,?,?)", (cn, cp, cl))
                st.success("تم حفظ الزبون بنجاح!")
                st.rerun()
                
    st.divider()
    st.subheader("📋 قائمة العملاء المسجلين")
    custs_list = run_query("SELECT id, name, phone, shop_location FROM customers", fetch=True)
    if custs_list:
        for c in custs_list:
            with st.container(border=True):
                col_c1, col_c2 = st.columns([4, 1])
                with col_c1:
                    st.write(f"👤 **الاسم:** {c[1]} | 📞 **الهاتف:** {c[2] if c[2] else 'غير متوفر'} | 📍 **العنوان:** {c[3] if c[3] else 'غير متوفر'}")
                with col_c2:
                    if st.button("حذف", key=f"del_cust_{c[0]}"):
                        run_query("DELETE FROM customers WHERE id = ?", (c[0],))
                        st.rerun()
    else:
        st.info("لا يوجد عملاء مسجلين حالياً.")
