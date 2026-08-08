import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="إدارة المبيعات", page_icon="🛍️", layout="wide")

# --- تنسيق الألوان والأزرار ---
st.markdown("""
<style>
    div.stButton > button { background-color: #1a6b51; color: white; border-radius: 8px; border: none; width: 100%; }
    div.stButton > button:hover { background-color: #14523e; }
    .stTabs [data-baseweb="tab"] { background-color: #e6f2ee; border-radius: 8px; color: #1a6b51; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# العبارة المطلوبة
st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>« أسعد نفسك بنفسك - مستمرون نحو الأفضل »</h2>", unsafe_allow_html=True)

# --- إعداد قاعدة البيانات وتحديث الجداول تلقائياً ---
def init_db():
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    price REAL DEFAULT 0,
                    quantity INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    shop_location TEXT,
                    phone TEXT,
                    governorate TEXT,
                    region TEXT,
                    debt REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT,
                    shop_location TEXT,
                    phone TEXT,
                    governorate TEXT,
                    region TEXT,
                    total REAL,
                    date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    
    for col, col_type in [('shop_location', 'TEXT'), ('phone', 'TEXT'), ('governorate', 'TEXT'), ('region', 'TEXT'), ('debt', 'REAL DEFAULT 0')]:
        try:
            c.execute(f"ALTER TABLE customers ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass

    for col, col_type in [('shop_location', 'TEXT'), ('phone', 'TEXT'), ('governorate', 'TEXT'), ('region', 'TEXT')]:
        try:
            c.execute(f"ALTER TABLE invoices ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute(query, params)
    data = None
    if fetch: data = c.fetchall()
    conn.commit()
    conn.close()
    return data

# --- نظام تسجيل الدخول وإنشاء حساب جديد ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'play_sound' not in st.session_state:
    st.session_state.play_sound = False

# ضمان أن السلة دائماً نوعها Dictionary لمنع الأخطاء
if 'cart' not in st.session_state or not isinstance(st.session_state.cart, dict):
    st.session_state.cart = {}

if not st.session_state.logged_in:
    st.markdown("<h3 style='text-align: center;'>🔐 بوابة الدخول إلى النظام</h3>", unsafe_allow_html=True)
    auth_tab1, auth_tab2 = st.tabs(["تسجيل الدخول", "مستخدم جديد (إنشاء حساب)"])
    
    with auth_tab1:
        st.subheader("تسجيل الدخول للنظام")
        login_user = st.text_input("اسم المستخدم", key="l_user")
        login_pass = st.text_input("كلمة المرور", type="password", key="l_pass")
        if st.button("دخول"):
            user_res = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (login_user, login_pass), fetch=True)
            if user_res:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
                
    with auth_tab2:
        st.subheader("إنشاء حساب مستخدم جديد")
        new_user = st.text_input("اختر اسم مستخدم جديد", key="n_user")
        new_pass = st.text_input("اختر كلمة المرور", type="password", key="n_pass")
        if st.button("تسجيل الحساب"):
            if new_user and new_pass:
                try:
                    run_query("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_pass))
                    st.success("تم إنشاء الحساب بنجاح! انتقل لتبويب تسجيل الدخول والدخول.")
                except sqlite3.IntegrityError:
                    st.error("اسم المستخدم موجود مسبقاً، اختر اسم آخر.")
            else:
                st.error("يرجى ملء كافة الحقول.")
    st.stop()

# --- واجهة البرنامج بعد تسجيل الدخول ---
st.sidebar.success(f"مرحباً بك، {st.session_state.username}")
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

menu = st.sidebar.radio("القائمة الرئيسية", ["🏪 المبيعات", "📦 إدارة المخزون", "📊 التقارير والأرباح", "👥 العملاء والديون"])

# --- تشغيل الصوت عند الإضافة للسلة ---
if st.session_state.play_sound:
    st.markdown("""
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)
    st.session_state.play_sound = False

# --- 1. شاشة المبيعات ---
if menu == "🏪 المبيعات":
    tab1, tab2, tab3, tab4 = st.tabs(["شاشة البيع", "الفواتير", "العملاء", "مرتجعات الفواتير"])
    
    with tab1:
        search = st.text_input("🔍 ابحث باسم المنتج ...")
        products = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
        if products:
            cols = st.columns(3)
            prod_count = 0
            for prod in products:
                if search.lower() in prod[1].lower():
                    clean_price = int(prod[2]) if prod[2] is not None else 0
                    with cols[prod_count % 3]:
                        with st.container(border=True):
                            st.markdown(f"#### {prod[1]}")
                            st.write(f"💰 **السعر:** {clean_price} دينار")
                            st.write(f"📦 **المتوفر:** {prod[3]} قطعة")
                            if st.button(f"إضافة للسلة", key=f"add_{prod[0]}"):
                                prod_id = prod[0]
                                max_qty = prod[3]
                                if prod_id in st.session_state.cart:
                                    if st.session_state.cart[prod_id]['qty'] < max_qty:
                                        st.session_state.cart[prod_id]['qty'] += 1
                                    else:
                                        st.warning("الكمية المطلوبة تتجاوز المخزون المتوفر!")
                                else:
                                    if max_qty > 0:
                                        st.session_state.cart[prod_id] = {
                                            'name': prod[1],
                                            'price': clean_price,
                                            'qty': 1,
                                            'max_qty': max_qty
                                        }
                                    else:
                                        st.warning("المنتج نفذ من المخزون!")
                                st.session_state.play_sound = True
                                st.rerun()
                    prod_count += 1
            if prod_count == 0:
                st.info("لم يتم العثور على المنتج المطلوب.")
        else:
            st.info("لا توجد منتجات حالياً. يمكنك إضافتها من قسم (إدارة المخزون).")

    with tab2:
        st.subheader("🧾 الفواتير السابقة وتفاصيل العملاء")
        invs = run_query("SELECT id, customer_name, shop_location, phone, governorate, region, total, date FROM invoices ORDER BY id DESC", fetch=True)
        if invs:
            for inv in invs:
                clean_total = int(inv[6]) if inv[6] is not None else 0
                with st.expander(f"فاتورة رقم: {inv[0]} | العميل: {inv[1]} | المجموع: {clean_total} دينار"):
                    st.write(f"📅 **تاريخ الفاتورة:** {inv[7]}")
                    st.write(f"👤 **اسم العميل:** {inv[1]}")
                    st.write(f"🏪 **مكان المحل:** {inv[2]} | 📍 **المنطقة:** {inv[5]} | **المحافظة:** {inv[4]}")
                    st.write(f"📞 **رقم الهاتف:** {inv[3]}")
                    st.markdown(f"### المبلغ الإجمالي للفاتورة: {clean_total} دينار")
        else:
            st.info("لا توجد فواتير مسجلة.")

    with tab3:
        st.subheader("👥 العملاء")
        custs = run_query("SELECT id, name, shop_location, phone, governorate, region, debt FROM customers", fetch=True)
        if custs:
            st.dataframe(pd.DataFrame(custs, columns=["ID", "اسم العميل", "مكان المحل", "الهاتف", "المحافظة", "المنطقة", "الدين"]), use_container_width=True)
        else:
            st.info("لا توجد عملاء مسجلين.")

    with tab4:
        st.subheader("↩️ مرتجعات الفواتير")
        st.info("قريباً...")

    with st.sidebar.expander("🛒 سلة المشتريات وإتمام الفاتورة", expanded=True):
        total = 0
        items_to_remove = []
        
        if st.session_state.cart:
            for prod_id, item in list(st.session_state.cart.items()):
                item_total = item['price'] * item['qty']
                total += item_total
                st.markdown(f"**{item['name']}**")
                
                # أزرار التحكم بالكمية والحذف داخل السلة
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.write(f"العدد: {item['qty']}")
                with c2:
                    if st.button("➕", key=f"inc_{prod_id}"):
                        if item['qty'] < item['max_qty']:
                            item['qty'] += 1
                            st.rerun()
                with c3:
                    if st.button("➖", key=f"dec_{prod_id}"):
                        if item['qty'] > 1:
                            item['qty'] -= 1
                        else:
                            items_to_remove.append(prod_id)
                        st.rerun()
                with c4:
                    if st.button("🗑️", key=f"del_{prod_id}"):
                        items_to_remove.append(prod_id)
                        st.rerun()
                
                st.write(f"المجموع: {item_total} دينار")
                st.markdown("---")
            
            for p_id in items_to_remove:
                del st.session_state.cart[p_id]
                st.rerun()
        else:
            st.info("السلة فارغة.")

        st.write(f"### المجموع الكلي: {total} دينار")
        
        st.markdown("---")
        st.subheader("تفاصيل العميل للفاتورة:")
        
        cust_list = run_query("SELECT name, shop_location, phone, governorate, region FROM customers", fetch=True)
        cust_names = ["اختيار من العملاء المسجلين..."] + [c[0] for c in cust_list] if cust_list else ["اختيار من العملاء المسجلين..."]
        
        selected_cust = st.selectbox("اختر عميل:", cust_names)
        
        c_name, c_shop, c_phone, c_gov, c_reg = "", "", "", "", ""
        if selected_cust != "اختيار من العملاء المسجلين...":
            for c in cust_list:
                if c[0] == selected_cust:
                    c_name, c_shop, c_phone, c_gov, c_reg = c[0], c[1], c[2], c[3], c[4]
        
        cust_name = st.text_input("اسم العميل", value=c_name)
        shop_loc = st.text_input("مكان المحل", value=c_shop)
        phone_num = st.text_input("رقم العميل", value=c_phone)
        governorate = st.text_input("المحافظة", value=c_gov)
        region = st.text_input("المنطقة", value=c_reg)
        
        if st.button("✅ تأكيد البيع وحفظ الفاتورة"):
            if cust_name and st.session_state.cart:
                # خصم الكميات من المخزون بشكل فعلي
                for prod_id, item in st.session_state.cart.items():
                    run_query("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['qty'], prod_id))
                
                # حفظ الفاتورة
                run_query("INSERT INTO invoices (customer_name, shop_location, phone, governorate, region, total, date) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (cust_name, shop_loc, phone_num, governorate, region, total, datetime.now().strftime("%Y-%m-%d %H:%M")))
                
                st.session_state.cart = {}
                st.success("تم تثبيت الفاتورة بنجاح ونقصت الكميات المباعة من المخزن!")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم العميل ووضع منتجات بالسلة.")

# --- 2. إدارة المخزون ---
elif menu == "📦 إدارة المخزون":
    st.title("📦 إدارة المخزون")
    
    with st.form("add_product_form"):
        st.subheader("➕ إضافة أو تحديث منتج بالمخزن")
        p_name = st.text_input("اسم المنتج")
        p_qty_str = st.text_input("الكمية", value="1")
        p_price_str = st.text_input("السعر (بالدينار)", value="0")
        submitted_p = st.form_submit_button("حفظ المنتج")
        
        if submitted_p:
            if p_name:
                try:
                    p_qty = int(p_qty_str) if p_qty_str.strip() else 0
                except ValueError:
                    p_qty = 0
                    
                try:
                    p_price = float(p_price_str) if p_price_str.strip() else 0.0
                except ValueError:
                    p_price = 0.0
                
                exists = run_query("SELECT quantity FROM products WHERE name = ?", (p_name,), fetch=True)
                if exists:
                    run_query("UPDATE products SET quantity = quantity + ?, price = ? WHERE name = ?", (p_qty, p_price, p_name))
                    st.success(f"تم تحديث كمية وسعر {p_name} بنجاح!")
                else:
                    run_query("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (p_name, p_qty, p_price))
                    st.success(f"تمت إضافة {p_name} إلى المخزن بنجاح!")
                st.rerun()
            else:
                st.error("يرجى كتابة اسم المنتج.")
                
    st.markdown("---")
    st.subheader("📋 قائمة المنتجات الحالية")
    prods = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
    if prods:
        df_prods = pd.DataFrame(prods, columns=["ID", "اسم المنتج", "السعر", "العدد"])
        df_prods["السعر"] = df_prods["السعر"].astype(int)
        st.dataframe(df_prods, use_container_width=True)
    else:
        st.info("المخزن فارغ حالياً.")

# --- 3. التقارير والأرباح ---
elif menu == "📊 التقارير والأرباح":
    st.title("📊 التقارير والأرباح والفواتير")
    invs = run_query("SELECT id, customer_name, shop_location, phone, governorate, region, total, date FROM invoices", fetch=True)
    if invs:
        df_invs = pd.DataFrame(invs, columns=["رقم الفاتورة", "اسم العميل", "مكان المحل", "الهاتف", "المحافظة", "المنطقة", "المجموع", "التاريخ"])
        df_invs["المجموع"] = df_invs["المجموع"].astype(int)
        st.dataframe(df_invs, use_container_width=True)
    else:
        st.info("لا توجد تقارير أو فواتير مسجلة.")

# --- 4. العملاء والديون ---
elif menu == "👥 العملاء والديون":
    st.title("👥 إضافة وإدارة العملاء والديون")
    
    with st.form("add_customer_form"):
        st.subheader("➕ إضافة عميل جديد للقائمة")
        new_c_name = st.text_input("اسم العميل")
        new_c_shop = st.text_input("مكان المحل")
        new_c_phone = st.text_input("رقم العميل")
        new_c_gov = st.text_input("المحافظة")
        new_c_reg = st.text_input("المنطقة")
        submitted = st.form_submit_button("حفظ العميل الجديد")
        
        if submitted:
            if new_c_name:
                run_query("INSERT INTO customers (name, shop_location, phone, governorate, region, debt) VALUES (?, ?, ?, ?, ?, 0)", 
                          (new_c_name, new_c_shop, new_c_phone, new_c_gov, new_c_reg))
                st.success(f"تم حفظ العميل {new_c_name} بنجاح!")
                st.rerun()
            else:
                st.error("يرجى كتابة اسم العميل على الأقل.")
                
    st.markdown("---")
    st.subheader("📋 قائمة العملاء المسجلين")
    custs = run_query("SELECT id, name, shop_location, phone, governorate, region, debt FROM customers", fetch=True)
    if custs:
        st.dataframe(pd.DataFrame(custs, columns=["ID", "اسم العميل", "مكان المحل", "الهاتف", "المحافظة", "المنطقة", "الدين"]), use_container_width=True)
    else:
        st.info("لا توجد عملاء مسجلين حالياً.")
