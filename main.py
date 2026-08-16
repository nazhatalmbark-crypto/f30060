import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
import streamlit.components.v1 as components

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي", layout="wide", page_icon="📦")

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
    except: pass

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
                    item_id = int(it['id'])
                    sold_qty = int(it['qty'])
                    res_q = run_query("SELECT quantity FROM inventory WHERE id = ?", (item_id,), fetch=True)
                    if res_q:
                        current_qty = int(res_q[0][0])
                        new_qty = max(0, current_qty - sold_qty)
                        run_query("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, item_id))
                        
                st.session_state.cart = []
                st.success("تم الحفظ بنجاح")
                st.rerun()

    with tabs[1]: # الأرشيف
        st.subheader("📜 أرشيف الفواتير")
        invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json, invoice_date FROM invoices ORDER BY id DESC", fetch=True)
        if invs:
            for i in invs:
                with st.container(border=True):
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.write(f"**فاتورة رقم #{i[0]}** | العميل: {i[1]} | الإجمالي: {int(i[2]):,} | المتبقي: {int(i[4]):,}")
                    with col_b:
                        if st.button("🗑️ حذف", key=f"del_inv_{i[0]}"):
                            run_query("DELETE FROM invoices WHERE id = ?", (i[0],))
                            st.rerun()
                    
                    items_html = ""
                    try:
                        df_details = pd.read_csv(StringIO(i[5]))
                        for _, row in df_details.iterrows():
                            items_html += f"<tr><td style='border: 1px solid #999; padding: 8px;'>{row.get('name', '')}</td><td style='border: 1px solid #999; padding: 8px;'>{int(row.get('price', 0)):,}</td><td style='border: 1px solid #999; padding: 8px;'>{row.get('qty', 0)}</td></tr>"
                    except: items_html = "<tr><td colspan='3'>خطأ</td></tr>"

                    # تصميم الفاتورة بنسق جاهز للحفظ كـ PDF والطباعة
                    pdf_html_content = f"""
                    <html dir='rtl'>
                    <head>
                        <meta charset='UTF-8'>
                        <title>فاتورة #{i[0]}</title>
                        <style>
                            body {{ font-family: Tahoma, sans-serif; padding: 20px; color: #000; }}
                            .inv-card {{ border: 2px solid #333; padding: 25px; max-width: 650px; margin: auto; background: #fff; border-radius: 8px; }}
                            h2 {{ text-align: center; color: #008080; }}
                            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                            th {{ background-color: #f2f2f2; border: 1px solid #999; padding: 8px; }}
                            td {{ border: 1px solid #999; padding: 8px; text-align: center; }}
                        </style>
                    </head>
                    <body>
                        <div class='inv-card'>
                            <h2>📦 ياسر ويب - النظام المحاسبي</h2>
                            <p style='text-align: center; color: #555; font-size: 14px;'>فاتورة مبيعات رسمية</p>
                            <hr>
                            <p><b>رقم الفاتورة:</b> #{i[0]}</p>
                            <p><b>اسم الزبون:</b> {i[1]}</p>
                            <p><b>التاريخ:</b> {i[6]}</p>
                            <table>
                                <tr><th>المادة</th><th>السعر (د.ع)</th><th>الكمية</th></tr>
                                {items_html}
                            </table>
                            <p><b>إجمالي الفاتورة:</b> {int(i[2]):,} دينار</p>
                            <p><b>المبلغ المستلم:</b> {int(i[3]):,} دينار</p>
                            <p style='color: #c0392b;'><b>المتبقي (الدين):</b> {int(i[4]):,} دينار</p>
                            <hr>
                            <p style='text-align: center; font-size: 13px;'>شكراً لتعاملكم معنا - ياسر ويب</p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    st.download_button(
                        label="📥 تحميل الفاتورة (PDF / جاهزة للطباعة والواتساب)",
                        data=pdf_html_content,
                        file_name=f"invoice_{i[0]}.html",
                        mime="text/html",
                        key=f"dl_pdf_{i[0]}"
                    )
        else:
            st.info("لا توجد فواتير مسجلة حالياً")

    with tabs[2]: # المخزن
        st.subheader("📦 إدارة المخزن")
        with st.expander("إضافة مادة جديدة"):
            with st.form("new_item"):
                n = st.text_input("اسم المادة")
                q = st.text_input("الكمية")
                cost = st.text_input("سعر التكلفة")
                sell = st.text_input("سعر البيع")
                if st.form_submit_button("حفظ المادة"):
                    try:
                        run_query("INSERT INTO inventory (name, quantity, price, selling_price) VALUES (?,?,?,?)", (n, int(q), int(cost), int(sell)))
                        st.success("تمت الإضافة")
                        st.rerun()
                    except:
                        st.error("خطأ: المادة موجودة أو البيانات ناقصة")
        
        st.write("---")
        items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
        if items:
            for itm in items:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 2, 1])
                    c1.write(f"**{itm[1]}** (المتوفر: {itm[2]})")
                    c2.write(f"تكلفة: {int(itm[3]):,}")
                    c3.write(f"بيع: {int(itm[4]):,}")
                    
                    add_q = c4.number_input("إضافة:", min_value=0, step=1, key=f"inp_{itm[0]}")
                    if c4.button("تحديث الكمية", key=f"btn_{itm[0]}"):
                        current_q = int(itm[2])
                        run_query("UPDATE inventory SET quantity = ? WHERE id = ?", (current_q + int(add_q), itm[0]))
                        st.rerun()
                    
                    if c5.button("🗑️", key=f"del_m_{itm[0]}"):
                        run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                        st.rerun()

    with tabs[3]: # الأرباح
        st.subheader("🔍 تحليل الأرباح")
        if st.session_state.is_unlocked:
            st.success("أهلاً بك في النسخة الكاملة - قريباً سيتم إضافة إحصائيات دقيقة")
        else:
            st.warning("هذه الميزة تتطلب تفعيل النسخة المدفوعة.")
    
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
                    st.success("تم حفظ الزبون")
                    st.rerun()
                else:
                    st.error("يرجى إدخال الاسم")
        
        custs = run_query("SELECT id, name, shop_name, phone, shop_location FROM customers", fetch=True)
        if custs:
            for c in custs:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    col1.write(f"**الاسم:** {c[1]} | **المحل:** {c[2]} | **هاتف:** {c[3]} | **عنوان:** {c[4]}")
                    if col2.button("🗑️ حذف", key=f"del_c_{c[0]}"):
                        run_query("DELETE FROM customers WHERE id = ?", (c[0],))
                        st.rerun()
