import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي المتكامل", layout="wide", page_icon="📦")

# --- إعداد قاعدة البيانات وتحديث الجداول ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, barcode TEXT, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0, selling_price INTEGER DEFAULT 0)''')
    try:
        c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
    except:
        pass
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, shop_name TEXT, phone TEXT, area TEXT, details TEXT)''')
    try: c.execute("ALTER TABLE customers ADD COLUMN area TEXT")
    except: pass
    try: c.execute("ALTER TABLE customers ADD COLUMN details TEXT")
    except: pass

    c.execute('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, total_amount INTEGER, received_amount INTEGER, remaining_amount INTEGER, invoice_date TEXT, details_json TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, amount INTEGER, exp_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS debt_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, amount INTEGER, pay_date TEXT)''')
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
if 'backup_downloaded' not in st.session_state: st.session_state.backup_downloaded = False

# --- واجهة تسجيل الدخول (معدلة لتظهر بوضوح تام على الموبايل والحاسبة) ---
if not st.session_state.logged_in:
    st.title("🔐 ياسر ويب - بوابة الدخول الأمنية")
    
    auth_mode = st.radio("اختر العملية:", ["🔑 تسجيل الدخول", "📝 إنشاء حساب جديد"], horizontal=True)
    
    if auth_mode == "🔑 تسجيل الدخول":
        with st.form("login_form"):
            u_input = st.text_input("اسم المستخدم")
            p_input = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("تسجيل الدخول"):
                user_record = run_query("SELECT password FROM system_users WHERE username = ?", (u_input,), fetch=True)
                if user_record and user_record[0][0] == p_input:
                    st.session_state.logged_in = True
                    st.session_state.username = u_input
                    st.session_state.backup_downloaded = False
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور خطأ")
    else:
        with st.form("register_form"):
            new_u = st.text_input("اختر اسم مستخدم جديد")
            new_p = st.text_input("اختر كلمة المرور", type="password")
            if st.form_submit_button("إنشاء الحساب"):
                if new_u.strip() == "" or new_p.strip() == "":
                    st.error("يرجى ملء كافة الحقول")
                else:
                    try:
                        run_query("INSERT INTO system_users (username, password) VALUES (?, ?)", (new_u, new_p))
                        st.success("تم إنشاء الحساب بنجاح. يمكنك تسجيل الدخول الآن.")
                    except:
                        st.error("اسم المستخدم مستخدم مسبقاً")
else:
    # --- الشريط الجانبي وحماية البيانات الإجبارية ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    
    st.sidebar.divider()
    st.sidebar.subheader("🛡️ حماية البيانات الإجبارية")
    st.sidebar.info("لا يمكنك إغلاق أو تسجيل الخروج إلا بعد تحميل نسخة احتياطية حديثة.")
    
    try:
        with open("yasser_web.db", "rb") as f:
            db_bytes = f.read()
        
        dl_backup = st.sidebar.download_button(
            label="📥 تحميل النسخة الاحتياطية الآن",
            data=db_bytes,
            file_name=f"yasser_web_backup_{date.today()}.db",
            mime="application/octet-stream"
        )
        if dl_backup:
            st.session_state.backup_downloaded = True
            st.sidebar.success("تم تنزيل النسخة الاحتياطية بنجاح!")
    except:
        pass

    if st.sidebar.button("تسجيل الخروج"):
        if not st.session_state.backup_downloaded:
            st.sidebar.error("❌ ممنوع الخروج! يجب عليك تحميل النسخة الاحتياطية أولاً لحماية بياناتك من الضياع.")
        else:
            st.session_state.logged_in = False
            st.session_state.backup_downloaded = False
            st.rerun()
        
    st.sidebar.divider()

    # --- التبويبات الرئيسية ---
    tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "💰 الأرباح والمصاريف", "👥 العملاء والديون"])

    with tabs[0]: # نقطة البيع
        st.subheader("🛒 نقطة البيع السريع والباركود")
        
        search_term = st.text_input("🔍 بحث سريع عن مادة (بالاسم أو الباركود):", placeholder="اكتب اسم المادة أو رقم الباركود...")
        
        if search_term:
            items = run_query("SELECT id, name, barcode, quantity, selling_price FROM inventory WHERE quantity > 0 AND (name LIKE ? OR barcode LIKE ?)", (f"%{search_term}%", f"%{search_term}%"), fetch=True)
        else:
            items = run_query("SELECT id, name, barcode, quantity, selling_price FROM inventory WHERE quantity > 0", fetch=True)
            
        if 'cart' not in st.session_state: st.session_state.cart = []
        
        if items:
            cols = st.columns(3)
            for idx, itm in enumerate(items):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {itm[1]}")
                        barcode_display = f" | باركود: {itm[2]}" if itm[2] else ""
                        st.write(f"المتوفر: {itm[3]}{barcode_display}")
                        st.write(f"السعر: **{int(itm[4]):,} د.ع**")
                        if st.button("إضافة للسلة", key=f"pos_add_{itm[0]}"):
                            found = False
                            for cart_item in st.session_state.cart:
                                if cart_item['id'] == itm[0]:
                                    cart_item['qty'] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({'id': itm[0], 'name': itm[1], 'price': itm[4], 'qty': 1})
                            st.rerun()
        else:
            st.info("لا توجد مواد مطابقة للبحث أو المخزن فارغ.")
        
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
            
            rec_input_str = st.text_input("المبلغ المستلم نقداً:", value=str(int(total)))
            custs = run_query("SELECT name FROM customers", fetch=True)
            c_name = st.selectbox("اختر العميل:", [c[0] for c in custs] if custs else [])
            
            if st.button("حفظ الفاتورة وإتمام البيع"):
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
                st.success("تم حفظ الفاتورة وتحديث المخزن بنجاح! لا تنسَ أخذ نسخة احتياطية من القائمة الجانبية.")
                st.rerun()

    with tabs[1]: # الأرشيف والفاتورة المطابقة لطلبك
        st.subheader("📜 أرشيف الفواتير الرسمية")
        
        f_col1, f_col2 = st.columns(2)
        filter_date = f_col1.date_input("تصفية الأرشيف حسب التاريخ (اختياري):", value=None)
        
        if filter_date:
            invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json, invoice_date FROM invoices WHERE invoice_date = ? ORDER BY id DESC", (str(filter_date),), fetch=True)
        else:
            invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json, invoice_date FROM invoices ORDER BY id DESC", fetch=True)
            
        if invs:
            for i in invs:
                cust_info = run_query("SELECT shop_name, phone, area, details FROM customers WHERE name = ?", (i[1],), fetch=True)
                shop_name = cust_info[0][0] if cust_info and cust_info[0][0] else "غير مسجل"
                phone_num = cust_info[0][1] if cust_info and cust_info[0][1] else ""
                area_val = cust_info[0][2] if cust_info and cust_info[0][2] else "غير مسجل"
                details_val = cust_info[0][3] if cust_info and cust_info[0][3] else "غير مسجل"

                items_html = ""
                num_items = 0
                total_qty = 0
                try:
                    df_details = pd.read_csv(StringIO(i[5]))
                    num_items = len(df_details)
                    for idx, row in df_details.iterrows():
                        p_name = row.get('name', '')
                        p_price = int(row.get('price', 0))
                        p_qty = int(row.get('qty', 0))
                        total_qty += p_qty
                        sub_total = p_price * p_qty
                        items_html += f"<tr><td>{idx+1}</td><td>• {p_name}</td><td>{p_price:,} د.ع</td><td>{p_qty}</td><td>{sub_total:,} د.ع</td></tr>"
                except: 
                    items_html = "<tr><td colspan='5'>خطأ في عرض المواد</td></tr>"

                invoice_code = f"INV-{i[0]:04d}"
                wa_msg = f"اسم العميل: {i[1]}\nالمحل: {shop_name}\nرقم الفاتورة: {invoice_code}\n📅 التاريخ: {i[6]}\n-------------------\nإجمالي القائمة: {int(i[2]):,} د.ع\nالمبلغ المدفوع: {int(i[3]):,} د.ع\nالمتبقي دين: {int(i[4]):,} د.ع\nعدد الأصناف: {num_items} | مجموع الكراتين: {total_qty}\nشكراً لتعاملكم معنا!"
                encoded_wa = urllib.parse.quote(wa_msg)
                wa_link = f"https://api.whatsapp.com/send?phone={phone_num}&text={encoded_wa}" if phone_num else "#"

                with st.container(border=True):
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    with col_a:
                        st.write(f"**فاتورة رقم #{invoice_code}** | العميل: {i[1]} | المحل: {shop_name} | الإجمالي: {int(i[2]):,} د.ع")
                    with col_b:
                        if phone_num:
                            st.markdown(f"<a href='{wa_link}' target='_blank' style='text-decoration:none;'><button style='background-color:#25D366; color:white; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:bold;'>واتساب 💬</button></a>", unsafe_allow_html=True)
                        else:
                            st.write("بدون هاتف")
                    with col_c:
                        if st.button("🗑️ حذف", key=f"del_inv_{i[0]}"):
                            run_query("DELETE FROM invoices WHERE id = ?", (i[0],))
                            st.rerun()

                    pdf_html_content = f"""
                    <html dir='rtl'>
                    <head><meta charset='UTF-8'><title>فاتورة {invoice_code}</title>
                    <style>
                        body {{ font-family: Tahoma, sans-serif; padding: 25px; color: #000; background: #fff; }}
                        .inv-card {{ border: 2px solid #008080; padding: 25px; max-width: 750px; margin: auto; background: #fff; border-radius: 8px; }}
                        h2 {{ text-align: center; color: #008080; margin-bottom: 5px; }}
                        .subtitle {{ text-align: center; color: #666; font-size: 14px; margin-top: 0; }}
                        .info-box {{ background: #f8f9fa; border: 1px solid #ddd; padding: 12px; border-radius: 6px; margin: 15px 0; font-size: 15px; }}
                        .info-box p {{ margin: 6px 0; }}
                        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                        th {{ background-color: #008080; color: white; border: 1px solid #999; padding: 10px; font-size: 14px; text-align: center; }}
                        td {{ border: 1px solid #999; padding: 9px; text-align: center; font-size: 14px; }}
                        td:nth-child(2) {{ text-align: right; padding-right: 12px; }}
                        .totals {{ margin-top: 15px; font-size: 15px; background: #fdfefe; border: 1px solid #ddd; padding: 12px; border-radius: 6px; }}
                        .totals p {{ margin: 6px 0; }}
                        .remaining {{ color: #c0392b; font-weight: bold; }}
                    </style></head>
                    <body>
                        <div class='inv-card'>
                            <h2>📦 ياسر ويب - النظام المحاسبي المتكامل</h2>
                            <p class='subtitle'>فاتورة مبيعات رسمية</p>
                            <hr style='border: 0; border-top: 1px solid #ddd;'>
                            
                            <div class='info-box'>
                                <p><b>اسم العميل:</b> {i[1]} &nbsp;&nbsp;|&nbsp;&nbsp; <b>اسم المحل:</b> {shop_name}</p>
                                <p><b>رقم الفاتورة:</b> {invoice_code} &nbsp;&nbsp;|&nbsp;&nbsp; <b>التاريخ:</b> {i[6]}</p>
                                <p><b>عنوان المحل:</b> {area_val} &nbsp;&nbsp;|&nbsp;&nbsp; <b>العنوان التفصيلي:</b> {details_val}</p>
                                <p><b>رقم الهاتف:</b> {phone_num}</p>
                            </div>

                            <table>
                                <thead>
                                    <tr>
                                        <th>ت</th>
                                        <th>المادة</th>
                                        <th>السعر</th>
                                        <th>الكمية</th>
                                        <th>الإجمالي الفرعي</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items_html}
                                </tbody>
                            </table>

                            <div class='totals'>
                                <p><b>إجمالي القائمة:</b> {int(i[2]):,} د.ع</p>
                                <p><b>المبلغ المدفوع:</b> {int(i[3]):,} د.ع</p>
                                <p class='remaining'><b>المتبقي دين:</b> {int(i[4]):,} د.ع</p>
                                <hr style='border: 0; border-top: 1px dashed #ccc; margin: 10px 0;'>
                                <p><b>عدد الأصناف:</b> {num_items} &nbsp;&nbsp;|&nbsp;&nbsp; <b>مجموع الكراتين/الكميات:</b> {total_qty}</p>
                            </div>
                            
                            <hr style='border: 0; border-top: 1px solid #ddd; margin-top: 20px;'>
                            <p style='text-align: center; font-size: 13px; color: #555;'>شكراً لتعاملكم معنا - ياسر ويب</p>
                        </div>
                    </body></html>
                    """
                    
                    st.download_button(
                        label="📥 تحميل الفاتورة (HTML مرتبة ومنسقة)",
                        data=pdf_html_content,
                        file_name=f"invoice_{invoice_code}.html",
                        mime="text/html",
                        key=f"dl_pdf_{i[0]}"
                    )
        else:
            st.info("لا توجد فواتير مسجلة حسب التصفية الحالية")

    with tabs[2]: # المخزن والباركود
        st.subheader("📦 إدارة المخزن والباركود")
        with st.expander("إضافة مادة جديدة للمخزن مع الباركود"):
            with st.form("new_item"):
                n = st.text_input("اسم المادة")
                b_code = st.text_input("رقم الباركود أو الرمز (اختياري)")
                q = st.text_input("الكمية")
                cost = st.text_input("سعر التكلفة")
                sell = st.text_input("سعر البيع")
                if st.form_submit_button("حفظ المادة"):
                    try:
                        run_query("INSERT INTO inventory (name, barcode, quantity, price, selling_price) VALUES (?,?,?,?,?)", (n, b_code, int(q), int(cost), int(sell)))
                        st.success("تمت إضافة المادة بنجاح")
                        st.rerun()
                    except:
                        st.error("خطأ: المادة موجودة مسبقاً أو البيانات ناقصة")
        
        st.write("---")
        items = run_query("SELECT id, name, barcode, quantity, price, selling_price FROM inventory", fetch=True)
        if items:
            for itm in items:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 2, 1])
                    b_txt = f" | باركود: {itm[2]}" if itm[2] else ""
                    c1.write(f"**{itm[1]}**{b_txt} (المتوفر: {itm[3]})")
                    c2.write(f"تكلفة: {int(itm[4]):,}")
                    c3.write(f"بيع: {int(itm[5]):,}")
                    
                    add_q = c4.number_input("إضافة:", min_value=0, step=1, key=f"inp_{itm[0]}")
                    if c4.button("تحديث الكمية", key=f"btn_{itm[0]}"):
                        current_q = int(itm[3])
                        run_query("UPDATE inventory SET quantity = ? WHERE id = ?", (current_q + int(add_q), itm[0]))
                        st.rerun()
                    
                    if c5.button("🗑️", key=f"del_m_{itm[0]}"):
                        run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                        st.rerun()

    with tabs[3]: # الأرباح والمصاريف
        st.subheader("💰 الأرباح، المبيعات، ومصاريف المحل")
        invs_all = run_query("SELECT total_amount, received_amount, remaining_amount FROM invoices", fetch=True)
        total_sales = sum(i[0] for i in invs_all) if invs_all else 0
        total_received = sum(i[1] for i in invs_all) if invs_all else 0
        total_debts = sum(i[2] for i in invs_all) if invs_all else 0

        exps_all = run_query("SELECT amount FROM expenses", fetch=True)
        total_expenses = sum(e[0] for e in exps_all) if exps_all else 0
        
        net_profit = total_received - total_expenses

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        col_p1.metric("إجمالي المبيعات", f"{int(total_sales):,} د.ع")
        col_p2.metric("الديون المعلقة", f"{int(total_debts):,} د.ع")
        col_p3.metric("إجمالي المصاريف", f"{int(total_expenses):,} د.ع")
        col_p4.metric("صافي الدخل النقدي", f"{int(net_profit):,} د.ع")

        st.divider()
        with st.expander("➕ تسجيل مصروف جديد للمحل"):
            with st.form("exp_form"):
                e_title = st.text_input("بيان المصروف (مثلاً: إيجار، كهرباء)")
                e_amount = st.text_input("المبلغ (د.ع)")
                if st.form_submit_button("حفظ المصروف"):
                    if e_title.strip() and e_amount.isdigit():
                        run_query("INSERT INTO expenses (title, amount, exp_date) VALUES (?, ?, ?)", (e_title, int(e_amount), str(date.today())))
                        st.success("تم تسجيل المصروف بنجاح")
                        st.rerun()
                    else:
                        st.error("يرجى إدخال البيانات بشكل صحيح")

        st.write("### 📋 سجل المصاريف المسجلة")
        exps_list = run_query("SELECT id, title, amount, exp_date FROM expenses ORDER BY id DESC", fetch=True)
        if exps_list:
            for exp in exps_list:
                c_ex1, c_ex2 = st.columns([4, 1])
                c_ex1.write(f"🔹 **{exp[1]}** | المبلغ: **{int(exp[2]):,} د.ع** | التاريخ: {exp[3]}")
                if c_ex2.button("حذف", key=f"del_exp_{exp[0]}"):
                    run_query("DELETE FROM expenses WHERE id = ?", (exp[0],))
                    st.rerun()
        else:
            st.info("لا توجد مصاريف مسجلة حتى الآن.")

        st.divider()
        st.write("### ⚠️ تنبيهات المخزن الذكية")
        low_stock = run_query("SELECT name, quantity FROM inventory WHERE quantity <= 3", fetch=True)
        if low_stock:
            for ls in low_stock:
                st.warning(f"المادة **{ls[0]}** وشكت على النفاذ! الكمية المتبقية: {ls[1]} فقط.")
        else:
            st.success("جميع المواد في المخزن بحالة ممتازة.")
    
    with tabs[4]: # العملاء وتسديد الديون
        st.subheader("👥 إدارة العملاء ونظام تسديد الديون")
        with st.form("cust_form"):
            c_name = st.text_input("اسم العميل")
            c_shop = st.text_input("اسم المحل")
            c_phone = st.text_input("رقم الهاتف (مثلاً: 96478...)")
            c_area = st.text_input("عنوان المحل / المنطقة")
            c_details = st.text_area("العنوان التفصيلي أو الملاحظات")
            if st.form_submit_button("حفظ العميل الجديد"):
                if c_name.strip():
                    run_query("INSERT INTO customers (name, shop_name, phone, area, details) VALUES (?,?,?,?,?)", (c_name, c_shop, c_phone, c_area, c_details))
                    st.success("تم حفظ الزبون بنجاح")
                    st.rerun()
                else:
                    st.error("يرجى إدخال اسم الزبون على الأقل")
        
        st.divider()
        st.write("### 💳 قائمة الزبائن والديون الذمية")
        custs = run_query("SELECT id, name, shop_name, phone, area, details FROM customers", fetch=True)
        if custs:
            for c in custs:
                debt_res = run_query("SELECT SUM(remaining_amount) FROM invoices WHERE customer_name = ?", (c[1],), fetch=True)
                total_invoice_debt = debt_res[0][0] if debt_res and debt_res[0][0] else 0
                
                paid_res = run_query("SELECT SUM(amount) FROM debt_payments WHERE customer_name = ?", (c[1],), fetch=True)
                total_paid_debt = paid_res[0][0] if paid_res and paid_res[0][0] else 0
                
                net_debt = max(0, total_invoice_debt - total_paid_debt)

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**الاسم:** {c[1]} | **المحل:** {c[2]} | **هاتف:** {c[3]} | **المنطقة:** {c[4]} | **التفاصيل:** {c[5]}")
                        if net_debt > 0:
                            st.markdown(f"<p style='color: red; font-weight: bold;'>⚠️ الدين الذمي الحالي: {int(net_debt):,} دينار</p>", unsafe_allow_html=True)
                        else:
                            st.markdown("<p style='color: green;'>✔ الحساب خالص (لا يوجد دين)</p>", unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("🗑️ حذف الزبون", key=f"del_c_{c[0]}"):
                            run_query("DELETE FROM customers WHERE id = ?", (c[0],))
                            st.rerun()

                    if net_debt > 0:
                        with st.expander(f"💵 تسجيل تسديد دفعة دين للزبون: {c[1]}"):
                            with st.form(f"pay_form_{c[0]}"):
                                p_amt = st.text_input("مبلغ التسديد النقدي (د.ع):", key=f"p_amt_{c[0]}")
                                if st.form_submit_button("تثبيت التسديد وتنزيل الدين"):
                                    if p_amt.isdigit() and int(p_amt) > 0:
                                        run_query("INSERT INTO debt_payments (customer_name, amount, pay_date) VALUES (?, ?, ?)", (c[1], int(p_amt), str(date.today())))
                                        st.success(f"تم تسديد مبلغ {int(p_amt):,} دينار وتحديث حساب الزبون بنجاح!")
                                        st.rerun()
                                    else:
                                        st.error("يرجى إدخال مبلغ صحيح.")
