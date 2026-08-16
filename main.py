import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي المتكامل", layout="wide", page_icon="📦")

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0, selling_price INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    
    for col, col_type in [('shop_name', 'TEXT'), ('phone', 'TEXT'), ('shop_location', 'TEXT')]:
        try:
            c.execute(f"ALTER TABLE customers ADD COLUMN {col} {col_type}")
        except:
            pass
            
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
    st.title("🔐 ياسر ويب - بوابة الدخول")
    auth_tab1, auth_tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب جديد"])
    
    with auth_tab1:
        with st.form("login_form"):
            u_input = st.text_input("اسم المستخدم")
            p_input = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("تسجيل الدخول"):
                user_record = run_query("SELECT password FROM system_users WHERE username = ?", (u_input,), fetch=True)
                if user_record and user_record[0][0] == p_input:
                    st.session_state.logged_in = True
                    st.session_state.username = u_input
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور خطأ")
                    
    with auth_tab2:
        with st.form("register_form"):
            new_u = st.text_input("اختر اسم مستخدم جديد")
            new_p = st.text_input("اختر كلمة المرور", type="password")
            if st.form_submit_button("إنشاء الحساب"):
                if new_u.strip() == "" or new_p.strip() == "":
                    st.error("يرجى ملء كافة الحقول")
                else:
                    try:
                        run_query("INSERT INTO system_users (username, password) VALUES (?, ?)", (new_u, new_p))
                        st.success("تم إنشاء الحساب بنجاح.")
                    except:
                        st.error("اسم المستخدم مستخدم مسبقاً")
else:
    # --- الشريط الجانبي ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.sidebar.divider()
    
    # حقل تفعيل النسخة المدفوعة (مخفي النص بالكامل)
    if not st.session_state.is_unlocked:
        code_input = st.sidebar.text_input("رمز التفعيل:", type="password")
        if st.sidebar.button("تفعيل النسخة"):
            if code_input == "2009":
                st.session_state.is_unlocked = True
                st.success("تم تفعيل النسخة الكاملة!")
                st.rerun()
            else:
                st.sidebar.error("رمز التفعيل غير صحيح")
    else:
        st.sidebar.success("النسخة الكاملة مفعلة ✓")

    st.sidebar.divider()
    try:
        with open("yasser_web.db", "rb") as f:
            st.sidebar.download_button("📥 تحميل نسخة احتياطية", f, "backup.db")
    except:
        pass

    # --- التبويبات ---
    tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "🔍 الأرباح", "👥 العملاء"])

    with tabs[0]: # نقطة البيع
        st.subheader("🛒 نقطة البيع")
        items = run_query("SELECT id, name, quantity, selling_price FROM inventory WHERE quantity > 0", fetch=True)
        if 'cart' not in st.session_state: st.session_state.cart = []
        
        if items:
            cols = st.columns(3)
            for idx, itm in enumerate(items):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {itm[1]}")
                        st.write(f"المتوفر: {itm[2]} | السعر: {int(itm[3]):,} د.ع")
                        if st.button("إضافة للسلة", key=f"pos_add_{itm[0]}"):
                            found = False
                            for cart_item in st.session_state.cart:
                                if cart_item['id'] == itm[0]:
                                    cart_item['qty'] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({'id': itm[0], 'name': itm[1], 'price': itm[3], 'qty': 1})
                            st.rerun()
        
        if st.session_state.cart:
            st.divider()
            st.write("### السلة الحالية")
            for idx, cart_item in enumerate(st.session_state.cart):
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(f"**{cart_item['name']}**")
                c2.write(f"{int(cart_item['price']):,}")
                c3.write(f"العدد: {cart_item['qty']}")
                if c4.button("🗑️", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            
            st.divider()
            total = sum(int(i['price']) * int(i['qty']) for i in st.session_state.cart)
            st.write(f"### الإجمالي: {int(total):,} د.ع")
            
            rec_input_str = st.text_input("المبلغ المستلم:", value=str(int(total)))
            custs = run_query("SELECT name FROM customers", fetch=True)
            c_name = st.selectbox("اختر العميل:", [c[0] for c in custs] if custs else [])
            
            if st.button("حفظ الفاتورة"):
                rec = int(rec_input_str) if rec_input_str.isdigit() else total
                csv = pd.DataFrame(st.session_state.cart).to_csv(index=False)
                run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, invoice_date, details_json) VALUES (?,?,?,?,?,?)",
                          (c_name, total, rec, total-rec, str(date.today()), csv))
                for it in st.session_state.cart: 
                    run_query("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (it['qty'], it['id']))
                st.session_state.cart = []
                st.success("تم الحفظ بنجاح")
                st.rerun()

    with tabs[1]: # الأرشيف
        st.subheader("📜 أرشيف الفواتير")
        invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True)
        if invs:
            for i in invs:
                with st.container(border=True):
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.write(f"فاتورة رقم {i[0]} | العميل: {i[1]} | الإجمالي: {int(i[2]):,} | المتبقي: {int(i[4]):,}")
                    with col_b:
                        if st.button("🗑️ حذف", key=f"del_inv_{i[0]}"):
                            run_query("DELETE FROM invoices WHERE id = ?", (i[0],))
                            st.rerun()
                    pdf_data = generate_pdf(i[0], i[1], i[2], i[3], i[4], i[5])
                    st.download_button(f"تحميل PDF", pdf_data, f"inv_{i[0]}.pdf", key=f"pdf_{i[0]}")
        else:
            st.info("لا توجد فواتير مسجلة حالياً")

    with tabs[2]: # المخزن
        st.subheader("📦 إدارة المخزن")
        with st.expander("إضافة مادة جديدة"):
            with st.form("new_item"):
                n = st.text_input("اسم المادة")
                q = st.text_input("الكمية")
                c = st.text_input("سعر التكلفة")
                s = st.text_input("سعر البيع")
                if st.form_submit_button("حفظ المادة"):
                    try:
                        run_query("INSERT INTO inventory (name, quantity, price, selling_price) VALUES (?,?,?,?)", (n, int(q), int(c), int(s)))
                        st.success("تمت الإضافة بنجاح")
                        st.rerun()
                    except:
                        st.error("تأكد من صحة البيانات أو أن المادة موجودة مسبقاً")
        
        items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
        if items:
            for itm in items:
                cols = st.columns([3, 1, 1, 1])
                cols[0].write(f"**{itm[1]}** (المتوفر: {itm[2]})")
                cols[1].write(f"التكلفة: {int(itm[3]):,}")
                cols[2].write(f"البيع: {int(itm[4]):,}")
                if cols[3].button("🗑️ حذف", key=f"del_inv_item_{itm[0]}"):
                    run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                    st.rerun()

    with tabs[3]: # الأرباح
        st.subheader("🔍 تحليل الأرباح")
        if st.session_state.is_unlocked:
            st.success("مرحببك في لوحة تحليل الأرباح الكاملة.")
            # يمكنك إضافة تفاصيل الأرباح هنا
        else:
            st.warning("هذه الميزة تتطلب تفعيل النسخة المدفوعة عبر رمز التفعيل في الشريط الجانبي.")
    
    with tabs[4]: # العملاء
        st.subheader("👥 إدارة العملاء")
        with st.form("cust_form"):
            c_name = st.text_input("اسم الزبون")
            c_shop = st.text_input("اسم المحل")
            c_phone = st.text_input("رقم الهاتف")
            c_loc = st.text_input("عنوان المحل أو المنطقة")
            if st.form_submit_button("حفظ الزبون"):
                if c_name.strip():
                    run_query("INSERT INTO customers (name, shop_name, phone, shop_location) VALUES (?,?,?,?)", (c_name, c_shop, c_phone, c_loc))
                    st.success("تم حفظ الزبون بنجاح")
                    st.rerun()
                else:
                    st.error("يرجى إدخال اسم الزبون على الأقل")
        
        custs = run_query("SELECT id, name, shop_name, phone, shop_location FROM customers", fetch=True)
        if custs:
            for c in custs:
                cols = st.columns([4, 1])
                cols[0].write(f"**الاسم:** {c[1]} | **المحل:** {c[2]} | **الهاتف:** {c[3]} | **العنوان:** {c[4]}")
                if cols[1].button("🗑️ حذف", key=f"del_c_{c[0]}"):
                    run_query("DELETE FROM customers WHERE id = ?", (c[0],))
                    st.rerun()
        else:
            st.info("لا يوجد عملاء مسجلون حالياً")
