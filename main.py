import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse
import re

# إعداد الصفحة لتكون عريضة ومتجاوبة
st.set_page_config(
    page_title="نظام ياسر المعتمد - النسخة الذكية المتكاملة", 
    page_icon="🛍️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- تنسيق الألوان والتصميم الاحترافي المتجاوب ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }
    
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
                    quantity INTEGER DEFAULT 0,
                    category TEXT DEFAULT 'عام')''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
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
                    subtotal REAL,
                    discount REAL DEFAULT 0,
                    delivery REAL DEFAULT 0,
                    total REAL,
                    date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customer_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT,
                    amount REAL,
                    notes TEXT,
                    date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    
    for col, col_type in [('shop_location', 'TEXT'), ('phone', 'TEXT'), ('governorate', 'TEXT'), ('region', 'TEXT'), ('debt', 'REAL DEFAULT 0'), ('category', "TEXT DEFAULT 'عام'")]:
        try:
            c.execute(f"ALTER TABLE products ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass

    for col, col_type in [('shop_location', 'TEXT'), ('phone', 'TEXT'), ('governorate', 'TEXT'), ('region', 'TEXT'), ('debt', 'REAL DEFAULT 0')]:
        try:
            c.execute(f"ALTER TABLE customers ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass

    for col, col_type in [('shop_location', 'TEXT'), ('phone', 'TEXT'), ('governorate', 'TEXT'), ('region', 'TEXT'), ('subtotal', 'REAL'), ('discount', 'REAL DEFAULT 0'), ('delivery', 'REAL DEFAULT 0'), ('total', 'REAL')]:
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
if 'sound_url' not in st.session_state:
    st.session_state.sound_url = None
if 'cart' not in st.session_state or not isinstance(st.session_state.cart, dict):
    st.session_state.cart = {}

def play_sfx(sound_type):
    if sound_type == "add":
        st.session_state.sound_url = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"
    elif sound_type == "success":
        st.session_state.sound_url = "https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"

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
                play_sfx("success")
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
                    play_sfx("success")
                    st.success("تم إنشاء الحساب بنجاح! انتقل لتبويب تسجيل الدخول للدخول.")
                except sqlite3.IntegrityError:
                    st.error("اسم المستخدم موجود مسبقاً، اختر اسم آخر.")
            else:
                st.error("يرجى ملء كافة الحقول المطلوبة.")
    st.stop()

# --- الشريط العلوي للمستخدم وتسجيل الخروج ---
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.info(f"👤 المستخدم الحالي النشط: **{st.session_state.username}**")
with top_col2:
    if st.button("🚪 خروج"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

st.markdown("---")

# --- القائمة الرئيسية أفقية ---
menu = st.radio(
    "🧭 القائمة الرئيسية للنظام (اختر القسم):", 
    ["🏪 المبيعات", "📦 إدارة المخزون", "📊 لوحة التحكم والمساعد الذكي", "👥 العملاء ودفتر الديون"],
    horizontal=True
)

st.markdown("---")

if st.session_state.sound_url:
    st.markdown(f"""
        <audio autoplay style="display:none;">
            <source src="{st.session_state.sound_url}" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)
    st.session_state.sound_url = None

# --- 1. شاشة المبيعات ---
if menu == "🏪 المبيعات":
    tab1, tab2, tab3, tab4 = st.tabs(["شاشة البيع وتصنيفات المنتجات", "🛒 سلة المشتريات وإتمام الفاتورة", "العملاء", "مرتجعات الفواتير"])
    
    with tab1:
        all_prods_for_cat = run_query("SELECT DISTINCT category FROM products", fetch=True)
        categories = ["الكل"] + [p[0] for p in all_prods_for_cat if p[0]] if all_prods_for_cat else ["الكل"]
        
        selected_cat = st.selectbox("📂 تصفية المنتجات حسب القسم:", categories)
        search = st.text_input("🔍 ابحث باسم المنتج السريع ...")
        
        if selected_cat == "الكل":
            products = run_query("SELECT id, name, price, quantity, category FROM products", fetch=True)
        else:
            products = run_query("SELECT id, name, price, quantity, category FROM products WHERE category = ?", (selected_cat,), fetch=True)
            
        if products:
            cols = st.columns(3)
            prod_count = 0
            for prod in products:
                if search.lower() in prod[1].lower():
                    clean_price = int(prod[2]) if prod[2] is not None else 0
                    with cols[prod_count % 3]:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='color: #1a6b51; margin-bottom: 5px;'>{prod[1]}</h4>", unsafe_allow_html=True)
                            st.caption(f"📁 التصنيف: {prod[4]}")
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
                                play_sfx("add")
                                st.rerun()
                    prod_count += 1
            if prod_count == 0:
                st.info("لم يتم العثور على المنتج المطلوب.")
        else:
            st.info("لا توجد منتجات مطابقة حالياً في هذا القسم.")

    with tab2:
        st.subheader("🛒 محتويات السلة وإتمام الفاتورة النهائية")
        subtotal = 0
        items_to_remove = []
        
        if st.session_state.cart:
            for prod_id, item in list(st.session_state.cart.items()):
                item_total = item['price'] * item['qty']
                subtotal += item_total
                
                c_info, c_plus, c_minus, c_del = st.columns([3, 1, 1, 1])
                with c_info:
                    st.markdown(f"**{item['name']}** - العدد: {item['qty']} - المجموع: {item_total} دينار")
                with c_plus:
                    if st.button("➕", key=f"inc_{prod_id}"):
                        if item['qty'] < item['max_qty']:
                            item['qty'] += 1
                            play_sfx("add")
                            st.rerun()
                with c_minus:
                    if st.button("➖", key=f"dec_{prod_id}"):
                        if item['qty'] > 1:
                            item['qty'] -= 1
                        else:
                            items_to_remove.append(prod_id)
                        play_sfx("add")
                        st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"del_{prod_id}"):
                        items_to_remove.append(prod_id)
                        play_sfx("add")
                        st.rerun()
                st.markdown("---")
            
            for p_id in items_to_remove:
                del st.session_state.cart[p_id]
                st.rerun()
        else:
            st.info("السلة فارغة حالياً. اذهب إلى (شاشة البيع) وأضف منتجات.")

        st.markdown("---")
        col_disc, col_deliv = st.columns(2)
        with col_disc:
            discount = st.number_input("🏷️ مبلغ الخصم (دينار)", min_value=0.0, value=0.0, step=500.0)
        with col_deliv:
            delivery = st.number_input("🚚 أجور التوصيل (دينار)", min_value=0.0, value=0.0, step=500.0)
            
        final_total = max(0.0, subtotal - discount + delivery)
        
        st.markdown(f"""
            <div style="background: #e6f2ee; padding: 15px; border-radius: 8px; font-size: 18px; color: #1a6b51; margin-bottom: 15px;">
                <p style="margin: 3px 0;">مجموع المنتجات: <strong>{subtotal}</strong> دينار</p>
                <p style="margin: 3px 0;">الخصم: <span style="color: #FF4B4B;">- {discount}</span> دينار | أجور التوصيل: <strong>+ {delivery}</strong> دينار</p>
                <hr style="border: 0; border-top: 1px solid #1a6b51; margin: 8px 0;">
                <p style="margin: 3px 0; font-size: 20px; font-weight: bold;">💰 المجموع الكلي النهائي للصافي: {final_total} دينار عراقي</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("تفاصيل وعنوان العميل للفاتورة:")
        cust_list = run_query("SELECT name, shop_location, phone, governorate, region FROM customers", fetch=True)
        cust_names = ["اختيار من العملاء المسجلين..."] + [c[0] for c in cust_list] if cust_list else ["اختيار من العملاء المسجلين..."]
        
        selected_cust = st.selectbox("اختر عميل مسجل مسبقاً (اختياري):", cust_names)
        
        c_name, c_shop, c_phone, c_gov, c_reg = "", "", "", "", ""
        if selected_cust != "اختيار من العملاء المسجلين...":
            for c in cust_list:
                if c[0] == selected_cust:
                    c_name, c_shop, c_phone, c_gov, c_reg = c[0], c[1], c[2], c[3], c[4]
        
        cust_name = st.text_input("اسم العميل", value=c_name)
        shop_loc = st.text_input("مكان المحل / مكان العميل", value=c_shop)
        phone_num = st.text_input("رقم الهاتف", value=c_phone)
        governorate = st.text_input("المحافظة", value=c_gov)
        region = st.text_input("المنطقة", value=c_reg)
        
        add_to_debt = st.checkbox("📌 تسجيل المبلغ الكلي (دين) في ذمة العميل (بدون دفع نقدي حالي)")

        if st.button("✅ تأكيد البيع وحفظ الفاتورة النهائية"):
            if cust_name and st.session_state.cart:
                for prod_id, item in st.session_state.cart.items():
                    run_query("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['qty'], prod_id))
                
                run_query("INSERT INTO invoices (customer_name, shop_location, phone, governorate, region, subtotal, discount, delivery, total, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                          (cust_name, shop_loc, phone_num, governorate, region, subtotal, discount, delivery, final_total, datetime.now().strftime("%Y-%m-%d %H:%M")))
                
                if add_to_debt:
                    c_exists = run_query("SELECT id FROM customers WHERE name = ?", (cust_name,), fetch=True)
                    if c_exists:
                        run_query("UPDATE customers SET debt = debt + ? WHERE name = ?", (final_total, cust_name))
                    else:
                        run_query("INSERT INTO customers (name, shop_location, phone, governorate, region, debt) VALUES (?, ?, ?, ?, ?, ?)", 
                                  (cust_name, shop_loc, phone_num, governorate, region, final_total))
                
                st.session_state.cart = {}
                play_sfx("success")
                st.success("تم تثبيت الفاتورة بنجاح وتحديث المخزن والديون!")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم العميل على الأقل ووضع منتجات في السلة.")

    with tab3:
        st.subheader("👥 العملاء المسجلين")
        custs = run_query("SELECT id, name, shop_location, phone, governorate, region, debt FROM customers", fetch=True)
        if custs:
            st.dataframe(pd.DataFrame(custs, columns=["ID", "اسم العميل", "مكان المحل", "الهاتف", "المحافظة", "المنطقة", "الدين المترتب"]), use_container_width=True)
        else:
            st.info("لا توجد عملاء مسجلين حالياً.")

    with tab4:
        st.subheader("↩️ مرتجعات الفواتير")
        st.info("قسم المرتجعات قيد التفعيل...")

# --- 2. إدارة المخزون ---
elif menu == "📦 إدارة المخزون":
    st.title("📦 إدارة المخزون وتصنيفات المنتجات")
    
    with st.form("add_product_form"):
        st.subheader("➕ إضافة أو تحديث منتج بالمخزن")
        p_name = st.text_input("اسم المنتج")
        p_cat = st.text_input("تصنيف المنتج (مثال: اكسسوارات، قطع غيار، صيانة)", value="عام")
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
                    run_query("UPDATE products SET quantity = quantity + ?, price = ?, category = ? WHERE name = ?", (p_qty, p_price, p_cat, p_name))
                    play_sfx("success")
                    st.success(f"تم تحديث بيانات {p_name} بنجاح!")
                else:
                    run_query("INSERT INTO products (name, quantity, price, category) VALUES (?, ?, ?, ?)", (p_name, p_qty, p_price, p_cat))
                    play_sfx("success")
                    st.success(f"تمت إضافة {p_name} إلى المخزن بنجاح!")
                st.rerun()
            else:
                st.error("يرجى كتابة اسم المنتج.")
                
    st.markdown("---")
    st.subheader("📋 قائمة المنتجات الحالية في المخزن")
    prods = run_query("SELECT id, name, category, price, quantity FROM products", fetch=True)
    if prods:
        df_prods = pd.DataFrame(prods, columns=["ID", "اسم المنتج", "التصنيف", "السعر", "العدد"])
        df_prods["السعر"] = df_prods["السعر"].astype(int)
        st.dataframe(df_prods, use_container_width=True)
    else:
        st.info("المخزن فارغ حالياً.")

# --- 3. لوحة التحكم والمساعد الذكي ---
elif menu == "📊 لوحة التحكم والمساعد الذكي":
    st.title("📊 لوحة التحكم، المساعد الذكي المطور والفواتير")
    
    rep_tab1, rep_tab2 = st.tabs(["📈 لوحة المؤشرات والمساعد الذكي المتطور (AI Commands)", "📄 استعراض وفاتورة الطباعة والواتساب"])
    
    with rep_tab1:
        st.subheader("📊 نظرة عامة على أداء المتجر")
        
        all_inv = run_query("SELECT total FROM invoices", fetch=True)
        total_sales = sum([i[0] for i in all_inv if i[0]]) if all_inv else 0
        total_invoices_count = len(all_inv) if all_inv else 0
        
        all_custs_debt = run_query("SELECT debt FROM customers", fetch=True)
        total_outstanding_debt = sum([c[0] for c in all_custs_debt if c[0]]) if all_custs_debt else 0
        
        all_prods = run_query("SELECT quantity, price FROM products", fetch=True)
        total_inventory_items = sum([p[0] for p in all_prods if p[0]]) if all_prods else 0
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("إجمالي المبيعات", f"{int(total_sales):,} دينار")
        m2.metric("عدد الفواتير الكلي", f"{total_invoices_count} فاتورة")
        m3.metric("ديون العملاء الذمة", f"{int(total_outstanding_debt):,} دينار")
        m4.metric("قطع المنتجات بالمخزن", f"{total_inventory_items} قطعة")
        
        st.markdown("---")
        
        # --- المساعد الذكي المتطور (تنفيذ الأوامر والاستعلامات) ---
        st.subheader("🤖 المساعد الذكي المتطور (تنفيد الأوامر عبر المحادثة)")
        st.caption("اسأل عن أرباحك ومبيعاتك، أو أمره بإضافة منتج مباشرة (مثلاً: ضيف منتج شاحن بسعر 5000 وعدد 10)")
        
        user_ai_query = st.text_input("💬 اكتب أمرك أو سؤالك للمساعد هنا ...", key="ai_command_input")
        
        if user_ai_query:
            q_lower = user_ai_query.lower()
            
            if "ضيف" in q_lower or "أضف" in q_lower:
                try:
                    price_match = re.search(r"(?:سعر|بسعر)\s*(\d+(?:\.\d+)?)", q_lower)
                    qty_match = re.search(r"(?:عدد|كمية)\s*(\d+)", q_lower)
                    
                    if price_match and qty_match:
                        p_price = float(price_match.group(1))
                        p_qty = int(qty_match.group(1))
                        
                        name_match = re.search(r"منتج\s+(.*?)\s+(?:بسعر|سعر)", user_ai_query)
                        if name_match:
                            p_name = name_match.group(1).strip()
                            
                            exists = run_query("SELECT quantity FROM products WHERE name = ?", (p_name,), fetch=True)
                            if exists:
                                run_query("UPDATE products SET quantity = quantity + ?, price = ? WHERE name = ?", (p_qty, p_price, p_name))
                                msg = f"تم تحديث المنتج **{p_name}** بنجاح (أُضيف للعدد: {p_qty}، والسعر: {p_price})."
                            else:
                                run_query("INSERT INTO products (name, quantity, price, category) VALUES (?, ?, ?, ?)", (p_name, p_qty, p_price, "عام"))
                                msg = f"تمت إضافة المنتج الجديد **{p_name}** بنجاح إلى المخزن! (السعر: {p_price}، العدد: {p_qty})."
                            
                            play_sfx("success")
                            st.success(f"🤖 **المساعد الذكي:** {msg}")
                            st.balloons()
                        else:
                            st.warning("🤖 **المساعد الذكي:** لم أستطع تمييز اسم المنتج بدقة. تأكد من كتابتها هكذا: (ضيف منتج [الاسم] بسعر [السعر] وعدد [العدد]).")
                    else:
                        st.warning("🤖 **المساعد الذكي:** يرجى تحديد السعر والعدد بوضوح في الأمر.")
                except Exception as e:
                    st.error(f"🤖 **المساعد الذكي:** حدث خطأ في تحليل الأمر. ({e})")
                    
            elif "مبيعات" in q_lower or "بيع" in q_lower or "إيراد" in q_lower:
                st.info(f"🤖 **المساعد الذكي:** إجمالي المبيعات المسجلة لديك هو **{int(total_sales):,}** دينار عبر {total_invoices_count} فاتورة.")
            elif "منتج" in q_lower or "مخزن" in q_lower or "بضاعة" in q_lower:
                prods_count_res = run_query("SELECT COUNT(*), SUM(quantity) FROM products", fetch=True)
                p_cnt = prods_count_res[0][0] if prods_count_res and prods_count_res[0][0] else 0
                total_items = prods_count_res[0][1] if prods_count_res and prods_count_res[0][1] else 0
                st.info(f"🤖 **المساعد الذكي:** لديك حالياً **{p_cnt}** صنف مختلف في المخزن بإجمالي **{total_items}** قطعة.")
            elif "ديون" in q_lower or "دين" in q_lower:
                all_custs_debt = run_query("SELECT SUM(debt) FROM customers", fetch=True)
                total_debt = all_custs_debt[0][0] if all_custs_debt and all_custs_debt[0][0] else 0
                st.info(f"🤖 **المساعد الذكي:** إجمالي الديون المترتبة بذمة العملاء حالياً هو **{int(total_debt):,}** دينار.")
            else:
                st.warning("🤖 **المساعد الذكي:** لم أفهم أمرك بدقة. يمكنك سؤالي عن (المبيعات)، (المنتجات)، (الديون)، أو كتابة أمر إضافة مثل: (ضيف منتج [اسم] بسعر [سعر] وعدد [عدد]).")

        st.markdown("---")
        st.subheader("📈 رسم بياني لحركة المبيعات حسب الفواتير المسجلة")
        df_inv_chart = run_query("SELECT date, total FROM invoices", fetch=True)
        if df_inv_chart:
            df_chart = pd.DataFrame(df_inv_chart, columns=["التاريخ", "المجموع"])
            st.bar_chart(df_chart.set_index("التاريخ"))
        else:
            st.info("لا توجد مبيعات كافية لعرض الرسوم البيانية حالياً.")

    with rep_tab2:
        st.subheader("🎨 تخصيص لون الفاتورة")
        invoice_color = st.color_picker("اختر لون هوية الفاتورة المفضل لديك:", "#1a6b51")
        
        invs = run_query("SELECT id, customer_name, shop_location, phone, governorate, region, subtotal, discount, delivery, total, date FROM invoices ORDER BY id DESC", fetch=True)
        if invs:
            inv_options = [f"فاتورة رقم {inv[0]} - العميل: {inv[1]} - المجموع: {int(inv[9]) if inv[9] else 0} دينار" for inv in invs]
            selected_inv_str = st.selectbox("اختر الفاتورة لعرضها وتصديرها أو إرسالها:", inv_options)
            
            selected_idx = inv_options.index(selected_inv_str)
            inv = invs[selected_idx]
            
            inv_id, cust_name, shop_loc, phone, gov, reg, sub_val, disc_val, deliv_val, total_val, date_val = inv
            total_clean = int(total_val) if total_val else 0
            sub_clean = int(sub_val) if sub_val else total_clean
            disc_clean = int(disc_val) if disc_val else 0
            deliv_clean = int(deliv_val) if deliv_val else 0
            
            invoice_html = f"""
            <div dir="rtl" style="font-family: 'Cairo', Arial, sans-serif; background: #ffffff; padding: 30px; border-radius: 15px; border: 2px solid {invoice_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 700px; margin: auto;">
                <div style="text-align: center; border-bottom: 2px solid {invoice_color}; padding-bottom: 15px; margin-bottom: 20px;">
                    <h1 style="color: {invoice_color}; margin: 0; font-size: 26px;">🛍️ فاتورة مبيعات رسمية</h1>
                    <p style="color: #FF4B4B; font-weight: bold; margin: 5px 0 0 0; font-size: 16px;">« أسعد نفسك بنفسك - مستمرون نحو الأفضل »</p>
                </div>
                
                <table style="width: 100%; margin-bottom: 20px; background: #f4faf8; padding: 15px; border-radius: 8px; border-collapse: collapse;">
                    <tr>
                        <td style="width: 50%; vertical-align: top; border: none; padding: 5px;">
                            <p style="margin: 4px 0; color: #333;"><strong>رقم الفاتورة:</strong> #{inv_id}</p>
                            <p style="margin: 4px 0; color: #333;"><strong>تاريخ اليوم:</strong> {date_val}</p>
                        </td>
                        <td style="width: 50%; vertical-align: top; border: none; padding: 5px; text-align: right;">
                            <p style="margin: 4px 0; color: #333;"><strong>اسم العميل:</strong> {cust_name}</p>
                            <p style="margin: 4px 0; color: #333;"><strong>رقم الهاتف:</strong> {phone if phone else 'غير متوفر'}</p>
                        </td>
                    </tr>
                </table>
                
                <div style="margin-bottom: 20px; background: #f9f9f9; padding: 12px; border-radius: 8px; border: 1px solid #ddd;">
                    <p style="margin: 4px 0; color: #333;"><strong>مكان المحل / مكان العميل:</strong> {shop_loc if shop_loc else 'غير محدد'}</p>
                    <p style="margin: 4px 0; color: #333;"><strong>العنوان (المحافظة - المنطقة):</strong> {gov if gov else 'غير محدد'} {(' - ' + reg) if reg else ''}</p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: {invoice_color}; color: white;">
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: right;">بيان الفاتورة والخدمة</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">المبلغ الإجمالي</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 12px; border: 1px solid #ddd; color: #333;">مشتريات المنتجات للعميل الكريم ({cust_name})<br><small>الخصم: -{disc_clean} دينار | أجور التوصيل: +{deliv_clean} دينار</small></td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: bold; color: {invoice_color};">{total_clean} دينار</td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="text-align: left; background: #e6f2ee; padding: 15px; border-radius: 8px; font-size: 18px; font-weight: bold; color: {invoice_color};">
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
                wa_text = f"مرحباً {cust_name} 🛍️\nإليك تفاصيل فاتورتك من متجرنا:\n\n📄 فاتورة رقم: #{inv_id}\n📅 تاريخ اليوم: {date_val}\n📍 مكان المحل/العميل: {shop_loc}\n💰 المجموع الكلي: {total_clean} دينار\n\n« أسعد نفسك بنفسك - مستمرون نحو الأفضل »"
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

# --- 4. العملاء ودفتر الديون ---
elif menu == "👥 العملاء ودفتر الديون":
    st.title("👥 إدارة العملاء ودفتر الديون المتطور")
    
    cust_tab1, cust_tab2, cust_tab3 = st.tabs(["➕ إضافة عميل جديد", "📋 جدول العملاء والديون", "💵 تسديد الدفعات (دفتر الديون)"])
    
    with cust_tab1:
        with st.form("add_customer_form"):
            st.subheader("إضافة عميل جديد للقائمة")
            new_c_name = st.text_input("اسم العميل")
            new_c_shop = st.text_input("مكان المحل / مكان العميل")
            new_c_phone = st.text_input("رقم العميل")
            new_c_gov = st.text_input("المحافظة")
            new_c_reg = st.text_input("المنطقة")
            submitted = st.form_submit_button("حفظ العميل الجديد")
            
            if submitted:
                if new_c_name:
                    try:
                        run_query("INSERT INTO customers (name, shop_location, phone, governorate, region, debt) VALUES (?, ?, ?, ?, ?, 0)", 
                                  (new_c_name, new_c_shop, new_c_phone, new_c_gov, new_c_reg))
                        play_sfx("success")
                        st.success(f"تم حفظ العميل {new_c_name} بنجاح!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("اسم العميل موجود مسبقاً.")
                else:
                    st.error("يرجى كتابة اسم العميل على الأقل.")
                    
    with cust_tab2:
        st.subheader("قائمة العملاء وأرصدة الديون المترتبة")
        custs = run_query("SELECT id, name, shop_location, phone, governorate, region, debt FROM customers", fetch=True)
        if custs:
            df_custs = pd.DataFrame(custs, columns=["ID", "اسم العميل", "مكان المحل", "الهاتف", "المحافظة", "المنطقة", "الدين المتبقي"])
            st.dataframe(df_custs, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد عملاء مسجلين حالياً.")

    with cust_tab3:
        st.subheader("💵 دفتر تسديد الديون (خصم دفعة من دين العميل)")
        debt_custs = run_query("SELECT name, debt FROM customers WHERE debt > 0", fetch=True)
        if debt_custs:
            debt_cust_names = [c[0] for c in debt_custs]
            selected_debt_cust = st.selectbox("اختر العميل لتسديد جزء أو كل دينه:", debt_cust_names)
            
            current_debt = 0.0
            for c in debt_custs:
                if c[0] == selected_debt_cust:
                    current_debt = c[1]
            
            st.info(f"الدين الحالي على العميل ({selected_debt_cust}) هو: **{current_debt}** دينار")
            
            payment_amount = st.number_input("المبلغ المدفوع حالياً (دينار)", min_value=0.0, max_value=float(current_debt), value=float(current_debt), step=1000.0)
            payment_notes = st.text_input("ملاحظات السند (اختياري - مثلاً: تسديد نقدي)", value="تسديد نقدي")
            
            if st.button("✅ تأكيد تسجيل وتسديد الدفعة"):
                if payment_amount > 0:
                    run_query("UPDATE customers SET debt = debt - ? WHERE name = ?", (payment_amount, selected_debt_cust))
                    run_query("INSERT INTO customer_payments (customer_name, amount, notes, date) VALUES (?, ?, ?, ?)", 
                              (selected_debt_cust, payment_amount, payment_notes, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    play_sfx("success")
                    st.success(f"تم تسجيل سداد مبلغ {payment_amount} دينار بنجاح وتحديث ذمة العميل!")
                    st.rerun()
                else:
                    st.error("يرجى إدخال مبلغ صحيح للتسديد.")
        else:
            st.success("ممتاز! لا توجد ديون مترتبة على أي عميل حالياً.")
