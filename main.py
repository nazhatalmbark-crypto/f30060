import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# إعداد الصفحة لتكون بعرض الشاشة الكامل ومتجاوبة
st.set_page_config(
    page_title="نظام إدارة المبيعات المعتمد", 
    page_icon="🛍️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- تنسيق الألوان والتصميم الاحترافي المتجاوب ---
st.markdown("""
<style>
    div.stButton > button { 
        background-color: #1a6b51; 
        color: white; 
        border-radius: 8px; 
        border: none; 
        width: 100%; 
        height: 45px; 
        font-weight: bold; 
        font-size: 15px;
    }
    div.stButton > button:hover { 
        background-color: #14523e; 
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: #e6f2ee; 
        border-radius: 8px; 
        color: #1a6b51; 
        font-weight: bold; 
        font-size: 15px; 
        padding: 10px; 
    }
</style>
""", unsafe_allow_html=True)

# العبارة الاحترافية المطلوبة
st.markdown("<h2 style='text-align: center; color: #FF4B4B; background-color: #f9f9f9; padding: 10px; border-radius: 10px; border: 1px dashed #FF4B4B;'>« أسعد نفسك بنفسك - مستمرون نحو الأفضل »</h2>", unsafe_allow_html=True)

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
    
    # إضافة الأعمدة تلقائياً إذا لم تكن موجودة (لتفادي أخطاء التحديث)
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
    if fetch: 
        data = c.fetchall()
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
if 'cart' not in st.session_state or not isinstance(st.session_state.cart, dict):
    st.session_state.cart = {}

if not st.session_state.logged_in:
    st.markdown("<h3 style='text-align: center;'>🔐 بوابة الدخول الآمن إلى النظام</h3>", unsafe_allow_html=True)
    auth_tab1, auth_tab2 = st.tabs(["تسجيل الدخول", "مستخدم جديد (إنشاء حساب)"])
    
    with auth_tab1:
        st.subheader("تسجيل الدخول للنظام")
        login_user = st.text_input("اسم المستخدم", key="l_user")
        login_pass = st.text_input("كلمة المرور", type="password", key="l_pass")
        if st.button("دخول للنظام"):
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
        if st.button("تسجيل الحساب الجديد"):
            if new_user and new_pass:
                try:
                    run_query("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_pass))
                    st.success("تم إنشاء الحساب بنجاح! انتقل لتبويب تسجيل الدخول للخول.")
                except sqlite3.IntegrityError:
                    st.error("اسم المستخدم موجود مسبقاً، اختر اسم آخر.")
            else:
                st.error("يرجى ملء كافة الحقول المطلوبة.")
    st.stop()

# --- الشريط العلوي للمستخدم وتسجيل الخروج (ظاهر ومتجاوب بكل الأجهزة) ---
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.info(f"👤 المستخدم الحالي النشط: **{st.session_state.username}**")
with top_col2:
    if st.button("🚪 خروج"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

st.markdown("---")

# --- القائمة الرئيسية أفقية وواضحة في أعلى الشاشة (تظهر بكل الأجهزة بدون اختفاء) ---
menu = st.radio(
    "🧭 القائمة الرئيسية للنظام (اختر القسم):", 
    ["🏪 المبيعات", "📦 إدارة المخزون", "📊 الفواتير والتقارير الاحترافية", "👥 العملاء والديون"],
    horizontal=True
)

st.markdown("---")

# --- تشغيل مؤثر صوتي خفيف عند إضافة منتج ---
if st.session_state.play_sound:
    st.markdown("""
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)
    st.session_state.play_sound = False

# --- 1. شاشة المبيعات ---
if menu == "🏪 المبيعات":
    tab1, tab2, tab3, tab4 = st.tabs(["شاشة البيع", "🛒 سلة المشتريات وإتمام الفاتورة", "العملاء", "مرتجعات الفواتير"])
    
    with tab1:
        search = st.text_input("🔍 ابحث باسم المنتج السريع ...")
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
                st.info("لم يتم العثور على المنتج المطلوب في المخزن.")
        else:
            st.info("لا توجد منتجات حالياً. يمكنك إضافتها من قسم (إدارة المخزون).")

    with tab2:
        st.subheader("🛒 محتويات السلة وإتمام الفاتورة النهائية")
        total = 0
        items_to_remove = []
        
        if st.session_state.cart:
            for prod_id, item in list(st.session_state.cart.items()):
                item_total = item['price'] * item['qty']
                total += item_total
                
                c_info, c_plus, c_minus, c_del = st.columns([3, 1, 1, 1])
                with c_info:
                    st.markdown(f"**{item['name']}** - العدد: {item['qty']} - المجموع: {item_total} دينار")
                with c_plus:
                    if st.button("➕", key=f"inc_{prod_id}"):
                        if item['qty'] < item['max_qty']:
                            item['qty'] += 1
                            st.rerun()
                with c_minus:
                    if st.button("➖", key=f"dec_{prod_id}"):
                        if item['qty'] > 1:
                            item['qty'] -= 1
                        else:
                            items_to_remove.append(prod_id)
                        st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"del_{prod_id}"):
                        items_to_remove.append(prod_id)
                        st.rerun()
                st.markdown("---")
            
            for p_id in items_to_remove:
                del st.session_state.cart[p_id]
                st.rerun()
        else:
            st.info("السلة فارغة حالياً. اذهب إلى (شاشة البيع) وأضف منتجات.")

        st.write(f"### 💰 المجموع الكلي: {total} دينار")
        st.markdown("---")
        st.subheader("تفاصيل العميل للفاتورة:")
        
        cust_list = run_query("SELECT name, shop_location, phone, governorate, region FROM customers", fetch=True)
        cust_names = ["اختيار من العملاء المسجلين..."] + [c[0] for c in cust_list] if cust_list else ["اختيار من العملاء المسجلين..."]
        
        selected_cust = st.selectbox("اختر عميل مسجل مسبقاً (اختياري):", cust_names)
        
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
        
        if st.button("✅ تأكيد البيع وحفظ الفاتورة النهائية"):
            if cust_name and st.session_state.cart:
                for prod_id, item in st.session_state.cart.items():
                    run_query("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['qty'], prod_id))
                
                run_query("INSERT INTO invoices (customer_name, shop_location, phone, governorate, region, total, date) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (cust_name, shop_loc, phone_num, governorate, region, total, datetime.now().strftime("%Y-%m-%d %H:%M")))
                
                st.session_state.cart = {}
                st.success("تم تثبيت الفاتورة بنجاح ونقصت الكميات المباعة من المخزن! انتقل لتبويب (الفواتير والتقارير) لمشاهدتها وإرسالها.")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم العميل على الأقل ووضع منتجات في السلة.")

    with tab3:
        st.subheader("👥 العملاء المسجلين")
        custs = run_query("SELECT id, name, shop_location, phone, governorate, region, debt FROM customers", fetch=True)
        if custs:
            st.dataframe(pd.DataFrame(custs, columns=["ID", "اسم العميل", "مكان المحل", "الهاتف", "المحافظة", "المنطقة", "الدين"]), use_container_width=True)
        else:
            st.info("لا توجد عملاء مسجلين حالياً.")

    with tab4:
        st.subheader("↩️ مرتجعات الفواتير")
        st.info("قسم المرتجعات قيد التفعيل...")

# --- 2. إدارة المخزون ---
elif menu == "📦 إدارة المخزون":
    st.title("📦 إدارة المخزون والمنتجات")
    
    with st.form("add_product_form"):
        st.subheader("➕ إضافة أو تحديث منتج بالمخزن")
        p_name = st.text_input("اسم المنتج")
        p_qty_str = st.text_input("الكمية", value="1")
        p_price_str = st.text_input("السعر (بالدينار)", value="0")
        submitted_p = st.form_submit_button("حفظ المنتج في المخزن")
        
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
    st.subheader("📋 قائمة المنتجات الحالية في المخزن")
    prods = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
    if prods:
        df_prods = pd.DataFrame(prods, columns=["ID", "اسم المنتج", "السعر", "العدد"])
        df_prods["السعر"] = df_prods["السعر"].astype(int)
        st.dataframe(df_prods, use_container_width=True)
    else:
        st.info("المخزن فارغ حالياً.")

# --- 3. الفواتير والتقارير الاحترافية ---
elif menu == "📊 الفواتير والتقارير الاحترافية":
    st.title("📊 الفواتير الإلكترونية المعتمدة")
    
    invs = run_query("SELECT id, customer_name, shop_location, phone, governorate, region, total, date FROM invoices ORDER BY id DESC", fetch=True)
    if invs:
        inv_options = [f"فاتورة رقم {inv[0]} - العميل: {inv[1]} - المجموع: {int(inv[6]) if inv[6] else 0} دينار" for inv in invs]
        selected_inv_str = st.selectbox("اختر الفاتورة لعرضها وتصديرها أو إرسالها:", inv_options)
        
        selected_idx = inv_options.index(selected_inv_str)
        inv = invs[selected_idx]
        
        inv_id, cust_name, shop_loc, phone, gov, reg, total_val, date_val = inv
        total_clean = int(total_val) if total_val else 0
        
        invoice_html = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; background: #ffffff; padding: 25px; border-radius: 15px; border: 2px solid #1a6b51; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 700px; margin: auto;">
            <div style="text-align: center; border-bottom: 2px solid #1a6b51; padding-bottom: 15px; margin-bottom: 20px;">
                <h1 style="color: #1a6b51; margin: 0; font-size: 26px;">🛍️ فاتورة مبيعات رسمية</h1>
                <p style="color: #FF4B4B; font-weight: bold; margin: 5px 0 0 0; font-size: 16px;">« أسعد نفسك بنفسك - مستمرون نحو الأفضل »</p>
            </div>
            
            <div style="margin-bottom: 20px; background: #f4faf8; padding: 12px; border-radius: 8px;">
                <p style="margin: 4px 0;"><strong>رقم الفاتورة:</strong> #{inv_id}</p>
                <p style="margin: 4px 0;"><strong>التاريخ والوقت:</strong> {date_val}</p>
                <p style="margin: 4px 0;"><strong>اسم العميل:</strong> {cust_name}</p>
                <p style="margin: 4px 0;"><strong>رقم الهاتف:</strong> {phone if phone else 'غير متوفر'}</p>
            </div>
            
            <div style="margin-bottom: 20px;">
                <p style="margin: 4px 0;"><strong>مكان المحل:</strong> {shop_loc if shop_loc else 'غير محدد'}</p>
                <p style="margin: 4px 0;"><strong>العنوان:</strong> {gov if gov else ''} - {reg if reg else ''}</p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <thead>
                    <tr style="background-color: #1a6b51; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">بيان الفاتورة</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">المبلغ الإجمالي</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">قيمة المشتريات والمنتجات المطلوبة للعميل ({cust_name})</td>
                        <td style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: bold; color: #1a6b51;">{total_clean} دينار</td>
                    </tr>
                </tbody>
            </table>
            
            <div style="text-align: left; background: #e6f2ee; padding: 12px; border-radius: 8px; font-size: 18px; font-weight: bold; color: #1a6b51;">
                المجموع الكلي النهائي: {total_clean} دينار عراقي
            </div>
        </div>
        """
        
        st.markdown(invoice_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_dl, col_wa = st.columns(2)
        
        with col_dl:
            st.download_button(
                label="📥 تحميل الفاتورة كملف جاهز بجهازي",
                data=invoice_html,
                file_name=f"Invoice_{inv_id}_{cust_name}.html",
                mime="text/html",
                use_container_width=True
            )
            
        with col_wa:
            wa_text = f"مرحباً {cust_name} 🛍️\nإليك تفاصيل فاتورتك من متجرنا:\n\n📄 فاتورة رقم: #{inv_id}\n📅 التاريخ: {date_val}\n💰 المجموع الكلي: {total_clean} دينار\n\n« أسعد نفسك بنفسك - مستمرون نحو الأفضل »"
            encoded_wa_text = urllib.parse.quote(wa_text)
            wa_url = f"https://wa.me/{phone}?text={encoded_wa_text}" if phone else f"https://wa.me/?text={encoded_wa_text}"
            
            st.markdown(f"""
                <a href="{wa_url}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #25D366; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px;">
                        💬 إرسال الفاتورة عبر الواتساب مباشرة
                    </div>
                </a>
            """, unsafe_allow_html=True)
            
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

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
        df_custs = pd.DataFrame(custs, columns=["ID", "اسم العميل", "مكان المحل", "الهاتف", "المحافظة", "المنطقة", "الدين"])
        st.dataframe(df_custs, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد عملاء مسجلين حالياً.")
