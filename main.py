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

# --- واجهة تسجيل الدخول وإنشاء حساب جديد ---
if not st.session_state.logged_in:
    st.title("🔐 ياسر ويب - بوابة الدخول والتسجيل")
    st.write("يرجى تسجيل الدخول أو إنشاء حساب جديد للوصول إلى النظام المحاسبي.")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب جديد"])
    
    with auth_tab1:
        with st.form("login_form"):
            u_input = st.text_input("اسم المستخدم")
            p_input = st.text_input("كلمة المرور", type="password")
            submitted_login = st.form_submit_button("تسجيل الدخول")
            if submitted_login:
                user_record = run_query("SELECT password FROM system_users WHERE username = ?", (u_input,), fetch=True)
                if user_record and user_record[0][0] == p_input:
                    st.session_state.logged_in = True
                    st.session_state.username = u_input
                    st.success("تم تسجيل الدخول بنجاح")
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور خطأ")
                    
    with auth_tab2:
        with st.form("register_form"):
            new_u = st.text_input("اختر اسم مستخدم جديد")
            new_p = st.text_input("اختر كلمة المرور", type="password")
            submitted_reg = st.form_submit_button("إنشاء الحساب")
            if submitted_reg:
                if new_u.strip() == "" or new_p.strip() == "":
                    st.error("يرجى ملء كافة الحقول")
                else:
                    try:
                        run_query("INSERT INTO system_users (username, password) VALUES (?, ?)", (new_u, new_p))
                        st.success("تم إنشاء الحساب بنجاح. انتقل لتبويب تسجيل الدخول للدخول بحسابك.")
                    except:
                        st.error("اسم المستخدم مستخدم مسبقاً، اختر اسماً آخر")
else:
    # --- الشريط الجانبي ---
    st.sidebar.title(f"👤 مرحباً، {st.session_state.username}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
        
    st.sidebar.divider()
    st.sidebar.title("🔐 ترخيص النسخة الكاملة")
    if not st.session_state.is_unlocked:
        st.sidebar.warning("النسخة المجانية (5 مواد فقط)")
        code = st.sidebar.text_input("رمز التفعيل (2009):", type="password")
        if st.sidebar.button("تفعيل"):
            if code == "2009":
                st.session_state.is_unlocked = True
                st.success("تم التفعيل بنجاح")
                st.rerun()
            else:
                st.sidebar.error("الرمز خطأ")
    else:
        st.sidebar.success("النسخة الكاملة مفعلة")

    st.sidebar.divider()
    try:
        with open("yasser_web.db", "rb") as f:
            st.sidebar.download_button("📥 تحميل نسخة احتياطية", f, "backup.db")
    except:
        pass

    # --- التبويبات الرئيسية للنظام (مع إرجاع الرموز والصور فوق الخانات) ---
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
                        if st.button("اختيار للسلة", key=f"pos_add_{itm[0]}"):
                            found = False
                            for cart_item in st.session_state.cart:
                                if cart_item['id'] == itm[0]:
                                    if cart_item['qty'] < itm[2]:
                                        cart_item['qty'] += 1
                                        found = True
                                    else:
                                        st.warning("يتجاوز المخزون المتوفر")
                                        found = True
                                    break
                            if not found:
                                st.session_state.cart.append({'id': itm[0], 'name': itm[1], 'price': itm[3], 'qty': 1})
                            st.rerun()
        else:
            st.info("لا توجد مواد متوفرة للبيع حالياً")

        if st.session_state.cart:
            st.divider()
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df[['name', 'price', 'qty']], use_container_width=True)
            
            total = sum(int(i['price']) * int(i['qty']) for i in st.session_state.cart)
            st.write(f"### الإجمالي: {int(total):,} د.ع")
            
            # حقل نصي خالص بدون أي علامات زاد أو ناقص
            rec_input_str = st.text_input("المبلغ المستلم:", value=str(int(total)))
            try:
                rec = int(rec_input_str)
            except:
                rec = int(total)

            custs = run_query("SELECT name FROM customers", fetch=True)
            c_name = st.selectbox("اختر العميل:", [c[0] for c in custs] if custs else [])
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("حفظ الفاتورة"):
                    csv = pd.DataFrame(st.session_state.cart).to_csv(index=False)
                    run_query("INSERT INTO invoices (customer_name, total_amount, received_amount, remaining_amount, invoice_date, details_json) VALUES (?,?,?,?,?,?)",
                              (c_name, total, rec, total-rec, str(date.today()), csv))
                    for it in st.session_state.cart: 
                        run_query("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (it['qty'], it['id']))
                    st.session_state.cart = []
                    st.success("تم حفظ الفاتورة بنجاح")
                    st.rerun()
            with col_b2:
                if st.button("تفريغ السلة"):
                    st.session_state.cart = []
                    st.rerun()

    with tabs[1]: # الأرشيف
        st.subheader("📜 أرشيف الفواتير")
        invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json FROM invoices ORDER BY id DESC", fetch=True)
        if invs:
            for i in invs:
                with st.container(border=True):
                    st.write(f"فاتورة رقم {i[0]} | العميل: {i[1]} | الإجمالي: {int(i[2]):,} | المتبقي: {int(i[4]):,}")
                    pdf_data = generate_pdf(i[0], i[1], i[2], i[3], i[4], i[5])
                    st.download_button(f"تحميل ملف PDF رقم {i[0]}", pdf_data, f"inv_{i[0]}.pdf", key=f"pdf_{i[0]}")
        else:
            st.info("لا توجد فواتير محفوظة بعد")

    with tabs[2]: # المخزن
        st.subheader("📦 إدارة المخزن")
        count = run_query("SELECT COUNT(*) FROM inventory", fetch=True)[0][0]
        
        with st.expander("إضافة مادة جديدة"):
            if not st.session_state.is_unlocked and count >= 5:
                st.warning("وصل الحد الأقصى للنسخة المجانية (5 مواد). أدخل رمز 2009 في الشريط الجانبي للتفعيل")
            else:
                with st.form("new_item"):
                    n = st.text_input("اسم المادة")
                    q_str = st.text_input("الكمية", value="0")
                    c_str = st.text_input("سعر التكلفة", value="0")
                    s_str = st.text_input("سعر البيع", value="0")
                    if st.form_submit_button("حفظ المادة"):
                        try:
                            q = int(q_str)
                            c = int(c_str)
                            s = int(s_str)
                        except:
                            q, c, s = 0, 0, 0

                        if n.strip() == "": st.error("أدخل اسم المادة")
                        else:
                            try:
                                run_query("INSERT INTO inventory (name, quantity, price, selling_price) VALUES (?,?,?,?)", (n, q, c, s))
                                st.success("تمت الإضافة بنجاح")
                                st.rerun()
                            except:
                                st.error("المادة موجودة مسبقاً")

        with st.expander("زيادة كمية مادة موجودة"):
            existing = run_query("SELECT name FROM inventory", fetch=True)
            if existing:
                item_names = [i[0] for i in existing]
                sel_item = st.selectbox("اختر المادة:", item_names)
                add_qty_str = st.text_input("الكمية المضافة:", value="1")
                if st.button("تحديث المخزن"):
                    try:
                        add_qty = int(add_qty_str)
                    except:
                        add_qty = 1
                    run_query("UPDATE inventory SET quantity = quantity + ? WHERE name = ?", (add_qty, sel_item))
                    st.success(f"تمت إضافة الكمية للمادة: {sel_item}")
                    st.rerun()
            else:
                st.info("لا توجد مواد متوفرة")
                
        st.divider()
        items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
        if items:
            cols = st.columns(3)
            for idx, itm in enumerate(items):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {itm[1]}")
                        st.write(f"الكمية: **{itm[2]}**")
                        st.write(f"تكلفة: {int(itm[3]):,} | بيع: {int(itm[4]):,}")
                        profit = itm[4] - itm[3]
                        st.write(f"ربح القطعة: **{int(profit):,} د.ع**")
                        if st.button("حذف المادة", key=f"del_{itm[0]}"):
                            run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                            st.rerun()

    with tabs[3]: # الأرباح
        st.subheader("🔍 تحليل الأرباح")
        items = run_query("SELECT name, quantity, price, selling_price FROM inventory", fetch=True)
        all_invs = run_query("SELECT details_json FROM invoices", fetch=True)
        
        profit_data = []
        if items:
            for itm in items:
                name, qty, cost, sell = itm
                p_unit = sell - cost
                sold_qty = 0
                try:
                    for inv in all_invs:
                        if inv[0]:
                            df = pd.read_csv(StringIO(inv[0]))
                            if 'name' in df.columns and 'qty' in df.columns:
                                match = df.loc[df['name'] == name]
                                if not match.empty: sold_qty += int(match['qty'].sum())
                except:
                    pass
                
                profit_data.append({
                    "المادة": name,
                    "الكمية الحالية": qty,
                    "الكمية المباعة": sold_qty,
                    "ربح القطعة": p_unit,
                    "إجمالي الربح": p_unit * sold_qty
                })
            if profit_data:
                st.dataframe(pd.DataFrame(profit_data), use_container_width=True)

    with tabs[4]: # العملاء
        st.subheader("👥 إدارة العملاء")
        with st.form("cust_form"):
            c_name = st.text_input("اسم الزبون")
            c_shop = st.text_input("اسم المحل")
            c_phone = st.text_input("رقم الهاتف")
            c_loc = st.text_input("عنوان المحل أو المنطقة")
            if st.form_submit_button("حفظ الزبون"):
                if c_name.strip() == "": st.error("أدخل اسم الزبون")
                else:
                    run_query("INSERT INTO customers (name, shop_name, phone, shop_location) VALUES (?,?,?,?)", (c_name, c_shop, c_phone, c_loc))
                    st.success("تم حفظ الزبون بنجاح")
                    st.rerun()
                    
        st.divider()
        custs = run_query("SELECT id, name, shop_name, phone, shop_location FROM customers", fetch=True)
        if custs:
            for c in custs:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"الاسم: {c[1]} | المحل: {c[2] or 'غير متوفر'} | الهاتف: {c[3] or 'غير متوفر'} | العنوان: {c[4] or 'غير متوفر'}")
                    with col2:
                        if st.button("حذف العميل", key=f"del_c_{c[0]}"):
                            run_query("DELETE FROM customers WHERE id = ?", (c[0],))
                            st.rerun()
