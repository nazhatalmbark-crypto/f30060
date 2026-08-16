import streamlit as st
import sqlite3
from datetime import date
import pandas as pd

# إعداد الصفحة وتصميم الواجهة (طابع أخضر فخم)
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي الاحترافي", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    div[data-testid="stMetricValue"] {
        font-size: 22px;
        color: #0e4d3a;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. إعداد قاعدة البيانات الشاملة ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, shop_location TEXT, governorate TEXT, landmark TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    customer_name TEXT, 
                    payment_type TEXT, 
                    total_amount INTEGER, 
                    invoice_date TEXT, 
                    details_json TEXT
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
    st.markdown("<p style='text-align: center; color: gray;'>النظام الشامل للمبيعات، الأرشيف الدقيق، وإدارة الديون</p>", unsafe_allow_html=True)
    
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
        st.sidebar.warning("⚠️ النسخة التجريبية (بحد أقصى 5 مواد بالمخزن)")
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

    # --- التبويبات كاملة ومتكاملة ---
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🛒 المبيعات والسلة", "📜 أرشيف الفواتير", "📦 شبكة المخزن", "➕ إضافة مواد", "👥 العملاء", "💰 المالية والخزنة", "📊 التقارير"
    ])

    # --- تبويب 1: المبيعات والسلة (مع إلزامية اختيار عميل) ---
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
            st.subheader("🧾 عربة المشتريات وإنشاء الفاتورة")
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
                    # جلب العملاء المسجلين فقط (بدون عميل نقدي عام لضمان إجبار المندوب على اختيار عميل حقيقي)
                    cust_res = run_query("SELECT name, phone, shop_location FROM customers", fetch=True)
                    if cust_res:
                        cust_dict = {f"{c[0]} ({c[2] or 'بدون محل'})": c[0] for c in cust_res}
                        selected_display = st.selectbox("اختر اسم الزبون / المحل المسجل (إجباري)", list(cust_dict.keys()))
                        selected_customer = cust_dict[selected_display]
                    else:
                        selected_customer = None
                        st.warning("⚠️ لا يوجد عملاء مسجلين! يجيب إضافة عميل في تبويب 'العملاء' أولاً لإتمام البيع.")
                with pay_col2:
                    payment_method = st.radio("طريقة الدفع:", ["نقدي (كاش)", "دين (آجل)"], horizontal=True)
                
                if st.button("✅ إتمام البيع وحفظ الفاتورة بالأرشيف", use_container_width=True):
                    if not selected_customer:
                        st.error("❌ عذراً، لا يمكن إتمام الفاتورة بدون اختيار عميل مسجل!")
                    else:
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
                            # حفظ تفاصيل المواد كجدول بيانات مدمج
                            df_cart = pd.DataFrame(st.session_state.cart)[['name', 'qty', 'price', 'total']]
                            df_cart.columns = ['اسم المادة', 'الكمية', 'السعر المفرد', 'المجموع']
                            details_csv = df_cart.to_csv(index=False)
                            
                            run_query("INSERT INTO invoices (customer_name, payment_type, total_amount, invoice_date, details_json) VALUES (?, ?, ?, ?, ?)",
                                      (selected_customer, payment_method, grand_total, str(date.today()), details_csv))
                            
                            st.success("تم إتمام الفاتورة وحفظها بنجاح في أرشيف المندوب وقص المواد من المخزن!")
                            st.session_state.cart = []
                            st.rerun()
            else:
                st.info("السلة فارغة حالياً.")
        else:
            st.info("لا توجد مواد في المخزن.")

    # --- تبويب 2: أرشيف الفواتير والديون (مع جدول مرتب لتفاصيل الفاتورة) ---
    with tab2:
        st.subheader("📜 أرشيف الفواتير والديون السابقة")
        st.markdown("هنا تظهر لك الفواتير السابقة لكل محل وزبون، مع جدول مرتب بالتفاصيل لمعرفة الديون وسجل المبيعات.")
        
        all_invoices = run_query("SELECT id, customer_name, payment_type, total_amount, invoice_date, details_json FROM invoices ORDER BY id DESC", fetch=True)
        
        if all_invoices:
            search_cust = st.text_input("🔍 ابحث عن اسم زبون أو محل لاستعراض ديونه وفواتيره:").strip()
            
            for inv in all_invoices:
                inv_id, c_name, p_type, t_amt, i_date, details_csv = inv
                
                if search_cust and search_cust not in c_name:
                    continue
                
                with st.container(border=True):
                    col_inv1, col_inv2, col_inv3 = st.columns([2, 2, 1])
                    col_inv1.markdown(f"### 🧾 فاتورة رقم #{inv_id}")
                    col_inv1.write(f"👤 **الزبون / المحل:** {c_name}")
                    col_inv2.write(f"📅 **التاريخ:** {i_date}")
                    col_inv2.write(f"💳 **الطريقة:** {p_type}")
                    col_inv3.metric("المبلغ الإجمالي", f"{t_amt:,} د.ع")
                    
                    with st.expander("📄 جدول تفاصيل المواد والفاتورة الكاملة (اضغط للعرض)"):
                        # تحويل بيانات الـ CSV المخزنة إلى جدول نظيف ومتقن
                        try:
                            from io import StringIO
                            df_view = pd.read_csv(StringIO(details_csv))
                            st.dataframe(df_view, use_container_width=True, hide_index=True)
                        except Exception:
                            st.text(details_csv)
                    
                    full_share_text = f"""⚡ ياسر ويب - فاتورة مبيعات معتمدة
رقم الفاتورة: #{inv_id}
التاريخ: {i_date}
الزبون: {c_name}
طريقة الدفع: {p_type}
-------------------------
الإجمالي الكلي: {t_amt:,} د.ع
شكراً لتعاملكم مع ياسر ويب!"""
                    
                    st.download_button(
                        label=f"📥 تحميل الفاتورة نصياً للواتساب / التليجرام (فاتورة #{inv_id})",
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

    # --- تبويب 4: إضافة مواد (مع حد النسخة التجريبية المرن) ---
    with tab4:
        st.subheader("➕ إضافة مادة جديدة للمخزن")
        
        # فحص حدود النسخة التجريبية المرنة
        current_items_count = run_query("SELECT COUNT(*) FROM inventory", fetch=True)[0][0]
        if not st.session_state.is_unlocked and current_items_count >= 5:
            st.warning("⚠️ لقد وصلت للحد الأقصى في النسخة التجريبية (5 مواد). أدخل كود التفعيل **2009** في القائمة الجانبية لفتح عدد غير محدود من المواد.")
        
        with st.form("add_item_form"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                item_name = st.text_input("اسم المادة").strip()
                item_qty = st.number_input("الكمية", min_value=1, value=10, step=1)
            with col_a2:
                item_price = st.number_input("السعر بالدينار", min_value=0, value=1000, step=250)
            
            if st.form_submit_button("حفظ المادة في النظام"):
                if not st.session_state.is_unlocked and current_items_count >= 5:
                    st.error("❌ النسخة التجريبية محدودة بـ 5 مواد كحد أقصى. يرجى تفعيل النسخة الكاملة!")
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
        st.subheader("👥 إدارة العملاء والزبائن (أصحاب المحلات)")
        with st.form("add_customer_form"):
            cc1, cc2 = st.columns(2)
            with cc1:
                c_name = st.text_input("اسم العميل أو المحل (إجباري)")
                c_phone = st.text_input("رقم الهاتف")
                c_gov = st.text_input("المحافظة")
            with cc2:
                c_loc = st.text_input("مكان المحل بالتفصيل")
                c_landmark = st.text_input("أقرب نقطة دالة")
            
            if st.form_submit_button("حفظ بيانات العميل"):
                if c_name:
                    run_query("INSERT INTO customers (name, phone, shop_location, governorate, landmark) VALUES (?, ?, ?, ?, ?)", 
                              (c_name, c_phone, c_loc, c_gov, c_landmark))
                    st.success("تم حفظ العميل بنجاح وأصبح متاحاً بقائمة الفواتير!")
                else:
                    st.error("يرجى إدخال اسم العميل على الأقل.")
        
        st.divider()
        st.subheader("قائمة العملاء المسجلين:")
        saved_customers = run_query("SELECT name, phone, shop_location, governorate, landmark FROM customers", fetch=True)
        if saved_customers:
            for sc in saved_customers:
                st.markdown(f"- 👤 **{sc[0]}** | 📱 الهاتف: {sc[1] or 'غير متوفر'} | 📍 المحل: {sc[2] or 'غير متوفر'} | 🏛️ المحافظة: {sc[3] or 'غير متوفر'} | 🚩 نقطة دالة: {sc[4] or 'لا توجد'}")
        else:
            st.info("لا يوجد عملاء مسجلين حالياً. أضف عملاء لكي تستطيع إصدار الفواتير لهم.")

    # --- تبويب 6: المالية ---
    with tab6:
        st.subheader("💰 إدارة الأموال ورأس المال والخزنة")
        items = run_query("SELECT quantity, price FROM inventory", fetch=True)
        total_capital = sum([it[0] * it[1] for it in items]) if items else 0
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("إجمالي رأس مال المخزون الحالي", f"{total_capital:,} د.ع")
        col_m2.metric("حالة الخزنة", "نشطة 🟢")
        st.info("هذا القسم يوضح السيولة وحسابات رأس المال المرتبطة بالبضاعة المتوفرة في المخازن حالياً.")

    # --- تبويب 7: التقارير (بدون أي رسومات زرقاء - جداول وأرقام نظيفة فقط) ---
    with tab7:
        st.subheader("📊 التقارير النهائية والأرباح (جداول إحصائية دقيقة)")
        
        items = run_query("SELECT name, quantity, price FROM inventory", fetch=True)
        if items:
            tot_items = len(items)
            tot_qty = sum([i[1] for i in items])
            tot_val = sum([i[1] * i[2] for i in items])
            
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("عدد الأصناف", tot_items)
            rc2.metric("إجمالي القطع بالمخزن", tot_qty)
            rc3.metric("إجمالي القيمة المالية", f"{tot_val:,} د.ع")
            
            st.divider()
            st.markdown("### 📋 جدول تفصيلي لحالة المخزون والقيمة:")
            df_report = pd.DataFrame(items, columns=['اسم المادة', 'الكمية المتوفرة', 'السعر المفرد'])
            df_report['إجمالي القيمة'] = df_report['الكمية المتوفرة'] * df_report['السعر المفرد']
            st.dataframe(df_report, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد بيانات كافية للتقارير حالياً.")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>ياسر ويب | نظام إدارة المبيعات للمندوبين والأسواق</p>", unsafe_allow_html=True)
