import streamlit as st
import sqlite3
from datetime import date

# إعداد الصفحة وتصميم الواجهة (طابع أخضر فخم)
st.set_page_config(page_title="ياسر ويب - نظام المندوب والمحاسبة", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    div[data-testid="stMetricValue"] {
        font-size: 22px;
        color: #0e4d3a;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. إعداد قاعدة البيانات الشاملة مع جدول الأرشيف والفواتير ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, shop_location TEXT, governorate TEXT, landmark TEXT)''')
    # جدول الأرشيف الخاص بالفواتير والديون
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    customer_name TEXT, 
                    payment_type TEXT, 
                    total_amount INTEGER, 
                    invoice_date TEXT, 
                    details TEXT
                )''')
    
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
    except sqlite3.IntegrityError:
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

# --- 2. إدارة الجلسة والسلة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False
if 'cart' not in st.session_state: st.session_state.cart = []

# --- 3. شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #0e4d3a;'>⚡ ياسر ويب - نظام المندوب والمحلات</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>النظام الشامل للمبيعات، الأرشيف، والديون</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.container(border=True):
            with st.form("login_form"):
                st.subheader("🔐 تسجيل الدخول للنظام")
                username = st.text_input("اسم المستخدم", value="admin")
                password = st.text_input("كلمة المرور", type="password", value="1234")
                if st.form_submit_button("دخول", use_container_width=True):
                    user = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username.strip(), password), fetch=True)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username.strip()
                        st.rerun()
                    else:
                        st.error("خطأ في اسم المستخدم أو كلمة المرور.")
else:
    # --- الشريط الجانبي للتفعيل والتحكم ---
    st.sidebar.markdown(f"### 👤 المستخدم: **{st.session_state.username}**")
    st.sidebar.divider()
    
    st.sidebar.subheader("🔐 حالة النسخة والترخيص")
    if not st.session_state.is_unlocked:
        st.sidebar.warning("⚠️ النسخة التجريبية (بقيود على الإدخال والتقارير)")
        act_code = st.sidebar.text_input("أدخل كود التفعيل:", type="password")
        if st.sidebar.button("تفعيل النسخة الكاملة"):
            if act_code == "2009":
                st.session_state.is_unlocked = True
                st.sidebar.success("✅ تم التفعيل بنجاح!")
                st.rerun()
            else:
                st.sidebar.error("كود التفعيل غير صحيح!")
    else:
        st.sidebar.success("✅ النسخة الكاملة مفعلة بلا حدود")
        if st.sidebar.button("إلغاء التفعيل"):
            st.session_state.is_unlocked = False
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.cart = []
        st.rerun()

    # --- العداد العلوي وعنوان اللوحة ---
    col_top1, col_top2 = st.columns([3, 1])
    col_top1.markdown("<h2 style='color: #0e4d3a;'>📦 لوحة تحكم ياسر ويب للمندوبين</h2>", unsafe_allow_html=True)
    col_top2.metric("عربة المشتريات 🛒", len(st.session_state.cart))

    # --- التبويبات كاملة متضمنة أرشيف الفواتير ---
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🛒 المبيعات والسلة", "📜 أرشيف الفواتير والديون", "📦 شبكة المخزن", "➕ إضافة مواد", "👥 العملاء", "💰 المالية والخزنة", "📊 التقارير"
    ])

    # --- تبويب 1: المبيعات والسلة ---
    with tab1:
        st.subheader("🛒 نقطة البيع السريع (اختر المواد للسلة)")
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        
        if items:
            cols = st.columns(3)
            for index, item in enumerate(items):
                item_id, name, quantity, price = item
                with cols[index % 3]:
                    with st.container(border=True):
                        st.markdown(f"### 🏷️ {name}")
                        st.metric("المتوفر", f"{quantity} قطعة")
                        st.write(f"**السعر**: {price:,} د.ع")
                        
                        if st.button("إضافة للسلة ➕", key=f"cart_add_{item_id}"):
                            found_in_cart = False
                            for cart_item in st.session_state.cart:
                                if cart_item['id'] == item_id:
                                    if cart_item['qty'] < quantity:
                                        cart_item['qty'] += 1
                                        cart_item['total'] = cart_item['qty'] * price
                                        st.toast(f"تم زيادة كمية '{name}' في السلة!", icon="✅")
                                    else:
                                        st.error("الكمية المطلوبة تتجاوز المخزون المتوفر!")
                                    found_in_cart = True
                                    break
                            
                            if not found_in_cart:
                                if quantity > 0:
                                    st.session_state.cart.append({
                                        'id': item_id,
                                        'name': name,
                                        'qty': 1,
                                        'price': price,
                                        'total': price
                                    })
                                    st.toast(f"تمت إضافة '{name}' للسلة!", icon="✅")
                                else:
                                    st.error("المادة نفدت من المخزن!")
                            st.rerun()
            
            st.divider()
            st.subheader("🧾 عربة المشتريات وحفظ الفاتورة بالأرشيف")
            if st.session_state.cart:
                grand_total = 0
                for i, c_item in enumerate(st.session_state.cart):
                    rc1, rc2, rc3, rc4 = st.columns([3, 2, 2, 1])
                    rc1.write(f"**{c_item['name']}**")
                    rc2.write(f"الكمية: {c_item['qty']}")
                    rc3.write(f"المجموع: {c_item['total']:,} د.ع")
                    grand_total += c_item['total']
                    if rc4.button("حذف", key=f"del_c_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                
                st.markdown(f"### 💰 الإجمالي الكلي للفاتورة: `{grand_total:,} د.ع`")
                st.divider()
                
                pay_col1, pay_col2 = st.columns(2)
                with pay_col1:
                    cust_res = run_query("SELECT name FROM customers", fetch=True)
                    cust_list = [c[0] for c in cust_res] if cust_res else ["عميل نقدي عام"]
                    if "عميل نقدي عام" not in cust_list: cust_list.insert(0, "عميل نقدي عام")
                    selected_customer = st.selectbox("اختر اسم الزبون / المحل", cust_list)
                with pay_col2:
                    payment_method = st.radio("طريقة الدفع:", ["نقدي (كاش)", "دين (آجل)"], horizontal=True)
                
                if st.button("✅ إتمام البيع، قص المواد، وحفظها بالأرشيف", use_container_width=True):
                    success_out = True
                    for c_item in st.session_state.cart:
                        db_q = run_query("SELECT quantity FROM inventory WHERE id = ?", (c_item['id'],), fetch=True)
                        if db_q and db_q[0][0] >= c_item['qty']:
                            new_stock = db_q[0][0] - c_item['qty']
                            run_query("UPDATE inventory SET quantity = ? WHERE id = ?", (new_stock, c_item['id']))
                        else:
                            success_out = False
                            st.error(f"فشل بيع مادة '{c_item['name']}' لعدم كفاية المخزن!")
                    
                    if success_out:
                        invoice_details_text = ""
                        for c_item in st.session_state.cart:
                            invoice_details_text += f"- {c_item['name']} | العدد: {c_item['qty']} | السعر: {c_item['price']:,} | المجموع: {c_item['total']:,}\n"
                        
                        # حفظ الفاتورة في جدول الأرشيف الدائم
                        run_query("INSERT INTO invoices (customer_name, payment_type, total_amount, invoice_date, details) VALUES (?, ?, ?, ?, ?)",
                                  (selected_customer, payment_method, grand_total, str(date.today()), invoice_details_text))
                        
                        st.success("تم إتمام الفاتورة وحفظها في أرشيف المندوب وقص المواد بنجاح!")
                        st.session_state.cart = []
                        st.rerun()
            else:
                st.info("السلة فارغة حالياً.")
        else:
            st.info("لا توجد مواد في المخزن.")

    # --- تبويب 2: أرشيف الفواتير والديون (الميزة الأساسية للمندوب) ---
    with tab2:
        st.subheader("📜 أرشيف الفواتير والديون السابقة")
        st.markdown("هنا تلقى كل الفواتير اللي بعتها للمحلات، حتى تراجع ديون الزبون أو ترجع تدزله الفاتورة إذا نساها.")
        
        all_invoices = run_query("SELECT id, customer_name, payment_type, total_amount, invoice_date, details FROM invoices ORDER BY id DESC", fetch=True)
        
        if all_invoices:
            # خيار بحث سريع باسم الزبون
            search_cust = st.text_input("🔍 ابحث عن اسم زبون أو محل لعرض فواتيره السابقة:").strip()
            
            for inv in all_invoices:
                inv_id, c_name, p_type, t_amt, i_date, details = inv
                
                # إذا اكو بحث، نطابق الاسم
                if search_cust and search_cust not in c_name:
                    continue
                
                with st.container(border=True):
                    col_inv1, col_inv2, col_inv3 = st.columns([2, 2, 1])
                    col_inv1.markdown(f"### 🧾 فاتورة رقم #{inv_id}")
                    col_inv1.write(f"👤 **الزبون:** {c_name}")
                    col_inv2.write(f"📅 **التاريخ:** {i_date}")
                    col_inv2.write(f"💳 **الطريقة:** {p_type}")
                    col_inv3.metric("المبلغ الإجمالي", f"{t_amt:,} د.ع")
                    
                    with st.expander("📄 تفاصيل مواد الفاتورة (اضغط للعرض)"):
                        st.text(details)
                    
                    # زر نسخ أو توليد نص لإرسال الفاتورة للزبون
                    full_share_text = f"""⚡ ياسر ويب - فاتورة مبيعات
رقم الفاتورة: #{inv_id}
التاريخ: {i_date}
الزبون: {c_name}
طريقة الدفع: {p_type}
-------------------------
{details}-------------------------
الإجمالي الكلي: {t_amt:,} د.ع
شكراً لتعاملكم معنا!"""
                    
                    st.download_button(
                        label=f"📥 تحميل أو إرسال فاتورة #{inv_id} (TXT)",
                        data=full_share_text,
                        file_name=f"invoice_{inv_id}_{c_name}.txt",
                        mime="text/plain",
                        key=f"dl_inv_{inv_id}"
                    )
        else:
            st.info("لا توجد فواتير محفوظة في الأرشيف حتى الآن.")

    # --- تبويب 3: شبكة المخزن ---
    with tab3:
        st.subheader("📦 شبكة المخازن والمنتجات الحالية")
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        if items:
            cols = st.columns(3)
            for index, item in enumerate(items):
                item_id, name, quantity, price = item
                with cols[index % 3]:
                    with st.container(border=True):
                        st.markdown(f"### 🏷️ {name}")
                        st.metric("الكمية المتوفرة", f"{quantity} قطعة")
                        st.metric("السعر المفرد", f"{price:,} د.ع")
                        if st.button("حذف المادة من المخزن 🗑️", key=f"inv_del_{item_id}"):
                            run_query("DELETE FROM inventory WHERE id = ?", (item_id,))
                            st.rerun()
        else:
            st.info("المخزن فارغ.")

    # --- تبويب 4: إضافة مواد ---
    with tab4:
        st.subheader("➕ إضافة مادة جديدة للمخزن")
        if not st.session_state.is_unlocked:
            st.info("ℹ️ ملاحظة: النسخة التجريبية تسمح بحد أقصى 100 قطعة في الإدخال الواحد.")
        
        with st.form("add_item_form"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                item_name = st.text_input("اسم المادة").strip()
                item_qty = st.number_input("الكمية", min_value=1, value=10, step=1)
            with col_a2:
                item_price = st.number_input("السعر بالدينار", min_value=0, value=1000, step=250)
            
            if st.form_submit_button("حفظ المادة في النظام"):
                if not st.session_state.is_unlocked and item_qty > 100:
                    st.error("⚠️ النسخة التجريبية تحصر الإدخال بـ 100 قطعة كحد أقصى!")
                elif item_name:
                    existing_item = run_query("SELECT id, quantity FROM inventory WHERE name = ?", (item_name,), fetch=True)
                    if existing_item:
                        db_id, cur_q = existing_item[0]
                        updated_q = cur_q + item_qty
                        run_query("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (updated_q, item_price, db_id))
                        st.success(f"تم تحديث مادة '{item_name}' بنجاح! الكمية الجديدة: {updated_q}")
                    else:
                        run_query("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (item_name, item_qty, item_price))
                        st.success(f"تم إضافة مادة '{item_name}' بنجاح!")
                else:
                    st.error("الرجاء إدخال اسم المادة.")

    # --- تبويب 5: العملاء ---
    with tab5:
        st.subheader("👥 إدارة العملاء والزبائن")
        with st.form("add_customer_form"):
            cc1, cc2 = st.columns(2)
            with cc1:
                c_name = st.text_input("اسم العميل أو المحل")
                c_phone = st.text_input("رقم الهاتف")
                c_gov = st.text_input("المحافظة")
            with cc2:
                c_loc = st.text_input("مكان المحل بالتفصيل")
                c_landmark = st.text_input("أقرب نقطة دالة")
            
            if st.form_submit_button("حفظ بيانات العميل"):
                if c_name:
                    run_query("INSERT INTO customers (name, phone, shop_location, governorate, landmark) VALUES (?, ?, ?, ?, ?)", 
                              (c_name, c_phone, c_loc, c_gov, c_landmark))
                    st.success("تم حفظ العميل بنجاح!")
                else:
                    st.error("يرجى إدخال اسم العميل على الأقل.")
        
        st.divider()
        st.subheader("قائمة العملاء المسجلين:")
        saved_customers = run_query("SELECT name, phone, shop_location, governorate, landmark FROM customers", fetch=True)
        if saved_customers:
            for sc in saved_customers:
                st.markdown(f"- 👤 **{sc[0]}** | 📱 الهاتف: {sc[1] or 'غير متوفر'} | 📍 المحل: {sc[2] or 'غير متوفر'} | 🏛️ المحافظة: {sc[3] or 'غير متوفر'} | 🚩 نقطة دالة: {sc[4] or 'لا توجد'}")
        else:
            st.info("لا يوجد عملاء مسجلين حالياً.")

    # --- تبويب 6: المالية ---
    with tab6:
        st.subheader("💰 إدارة الأموال ورأس المال والخزنة")
        items = run_query("SELECT quantity, price FROM inventory", fetch=True)
        total_capital = sum([it[0] * it[1] for it in items]) if items else 0
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("إجمالي رأس مال المخزون الحالي", f"{total_capital:,} د.ع")
        col_m2.metric("حالة الخزنة", "نشطة 🟢")
        st.info("هذا القسم يوضح السيولة وحسابات رأس المال المرتبطة بالبضاعة المتوفرة في المخازن حالياً.")

    # --- تبويب 7: التقارير ---
    with tab7:
        st.subheader("📊 التقارير النهائية والأرباح")
        if not st.session_state.is_unlocked:
            st.warning("🔒 **تقارير الأرباح المتقدمة والتحليلية مقفلة في النسخة التجريبية.** أدخل كود التفعيل لفتحها.")
        else:
            st.success("✅ النسخة الكاملة مفعلة بالكامل للتقارير!")
            items = run_query("SELECT name, quantity, price FROM inventory", fetch=True)
            if items:
                tot_items = len(items)
                tot_qty = sum([i[1] for i in items])
                tot_val = sum([i[1] * i[2] for i in items])
                
                rc1, rc2, rc3 = st.columns(3)
                rc1.metric("عدد الأصناف", tot_items)
                rc2.metric("إجمالي القطع", tot_qty)
                rc3.metric("إجمالي القيمة", f"{tot_val:,} د.ع")
                
                st.divider()
                chart_data = {i[1]: i[1] * i[2] for i in items}
                st.bar_chart(chart_data)
            else:
                st.info("لا توجد بيانات كافية للتقارير.")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>ياسر ويب | نظام إدارة المبيعات للمندوبين والأسواق</p>", unsafe_allow_html=True)
