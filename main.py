import streamlit as st
import sqlite3
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Inventory System", layout="centered")

# --- 1. إعداد وتحديث قاعدة البيانات الدائمة بأمان ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    quantity INTEGER DEFAULT 0,
                    price REAL DEFAULT 0,
                    is_locked INTEGER DEFAULT 0)''')
    
    # إضافة عمود السعر تلقائياً إذا كانت قاعدة البيانات قديمة ولا يحتويها الجدول
    try:
        c.execute("ALTER TABLE inventory ADD COLUMN price REAL DEFAULT 0;")
    except sqlite3.OperationalError:
        pass  # العمود موجود مسبقاً ولا داعي لإضافته
    
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

# --- 2. تهيئة الحالة الأساسية ---
def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'is_paid_user' not in st.session_state:
        st.session_state.is_paid_user = False
    if 'product_daily_adds' not in st.session_state:
        st.session_state.product_daily_adds = {}
    if 'last_date' not in st.session_state:
        st.session_state.last_date = str(date.today())
    
    if st.session_state.last_date != str(date.today()):
        st.session_state.product_daily_adds = {}
        st.session_state.last_date = str(date.today())

init_session()

# --- 3. قواميس الترجمة ---
translations = {
    "English": {
        "login_tab": "Login",
        "register_tab": "Create New Account",
        "login_title": "🔐 Login to Yasser Web",
        "register_title": "📝 Register New Account",
        "username": "Username",
        "password": "Password",
        "signin": "Sign In",
        "signup": "Sign Up",
        "login_success": "Login successful!",
        "login_error": "Invalid username or password.",
        "register_success": "Account created successfully! Please login now.",
        "user_exists": "Username already exists.",
        "app_title": "📦 Yasser Web - Inventory System",
        "account_settings": "Account Settings",
        "user": "User",
        "premium": "Premium Account (Unlimited Additions)",
        "logout": "Logout",
        "add_update": "Add or Update Item",
        "item_name": "Item Name",
        "quantity": "Quantity",
        "price": "Unit Price ($)",
        "save_item": "Save Item",
        "product_limit_reached": "Free limit reached! You can only add up to 100 units per product per day. Upgrade to Premium for unlimited quantity.",
        "item_locked": "is locked. You cannot add quantity to it.",
        "updated": "Successfully updated",
        "added": "Successfully added new item",
        "enter_valid": "Please enter a valid item name.",
        "inventory_grid": "Current Inventory Grid",
        "qty": "Qty",
        "unit_price": "Price",
        "total_value": "Total Value",
        "lock": "Lock",
        "unlock": "Unlock",
        "reports_title": "📊 Reports, Totals & Profits",
        "total_items": "Total Unique Items",
        "total_qty": "Total Quantity in Stock",
        "total_capital": "Total Inventory Value",
        "invoice_title": "🧾 Invoice & Receipt Generator",
        "select_item": "Select Item for Invoice",
        "invoice_qty": "Quantity to Sell",
        "generate_invoice": "Generate Invoice",
        "download_invoice": "📥 Download Invoice (TXT)",
        "empty": "The inventory is currently empty."
    },
    "العربية": {
        "login_tab": "تسجيل الدخول",
        "register_tab": "إنشاء حساب جديد",
        "login_title": "🔐 تسجيل الدخول إلى ياسر ويب",
        "register_title": "📝 إنشاء حساب جديد",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "signin": "تسجيل الدخول",
        "signup": "إنشاء الحساب",
        "login_success": "تم تسجيل الدخول بنجاح!",
        "login_error": "اسم المستخدم أو كلمة المرور غير صحيحة.",
        "register_success": "تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.",
        "user_exists": "اسم المستخدم موجود مسبقاً.",
        "app_title": "📦 ياسر ويب - نظام إدارة المخزون",
        "account_settings": "إعدادات الحساب",
        "user": "المستخدم",
        "premium": "حساب مدفوع (إضافات غير محدودة لكل المنتجات)",
        "logout": "تسجيل الخروج",
        "add_update": "إضافة أو تحديث مادة",
        "item_name": "اسم المادة",
        "quantity": "الكمية",
        "price": "سعر المفرد / السعر ($)",
        "save_item": "حفظ المادة",
        "product_limit_reached": "وصلت للحد المجاني لهذا المنتج! النسخة المجانية تسمح بحد أقصى 100 قطعة لكل منتج يومياً. قم بالترقية للحساب المدفوع لكميات مفتوحة.",
        "item_locked": "مقفلة. لا يمكنك إضافة كمية لها.",
        "updated": "تم تحديث بنجاح",
        "added": "تم إضافة مادة جديدة بنجاح",
        "enter_valid": "الرجاء إدخال اسم مادة صحيح.",
        "inventory_grid": "شبكة المخزون الحالي (عرض مريح)",
        "qty": "الكمية",
        "unit_price": "السعر",
        "total_value": "القيمة الكلية",
        "lock": "قفل",
        "unlock": "فتح القفل",
        "reports_title": "📊 التقارير، المجاميع والأرباح",
        "total_items": "إجمالي المواد المختلفة",
        "total_qty": "إجمالي الكمية بالمخزن",
        "total_capital": "إجمالي قيمة المخزن",
        "invoice_title": "🧾 مولد الفواتير والإيصالات",
        "select_item": "اختر المادة للفاتورة",
        "invoice_qty": "الكمية المباعة",
        "generate_invoice": "إصدار الفاتورة",
        "download_invoice": "📥 تحميل الفاتورة (ملف نصي جاهز)",
        "empty": "المخزون فارغ حالياً."
    }
}

# --- 4. واجهة تسجيل الدخول ---
def login_screen():
    selected_lang = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"])
    t = translations[selected_lang]
    
    tab1, tab2 = st.tabs([t["login_tab"], t["register_tab"]])
    
    with tab1:
        st.subheader(t["login_title"])
        with st.form("login_form"):
            username = st.text_input(t["username"], key="l_user")
            password = st.text_input(t["password"], type="password", key="l_pass")
            submit_login = st.form_submit_button(t["signin"])
            
            if submit_login:
                user = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username.strip(), password), fetch=True)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username.strip()
                    st.success(t["login_success"])
                    st.rerun()
                else:
                    st.error(t["login_error"])
                    
    with tab2:
        st.subheader(t["register_title"])
        with st.form("register_form"):
            new_username = st.text_input(t["username"], key="r_user")
            new_password = st.text_input(t["password"], type="password", key="r_pass")
            submit_register = st.form_submit_button(t["signup"])
            
            if submit_register:
                if new_username.strip() and new_password.strip():
                    try:
                        run_query("INSERT INTO users (username, password) VALUES (?, ?)", (new_username.strip(), new_password))
                        st.success(t["register_success"])
                    except sqlite3.IntegrityError:
                        st.error(t["user_exists"])
                else:
                    st.error("Please fill in all fields.")

# --- 5. التطبيق الرئيسي ---
def main_app():
    selected_lang = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"])
    t = translations[selected_lang]
    
    st.title(t["app_title"])
    
    st.sidebar.subheader(t["account_settings"])
    st.sidebar.write(f"{t['user']}: **{st.session_state.username}**")
    
    st.session_state.is_paid_user = st.sidebar.checkbox(t["premium"], st.session_state.is_paid_user)
    
    if st.session_state.is_paid_user:
        st.sidebar.success("🌟 Unlimited Premium Access")
    
    if st.sidebar.button(t["logout"]):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # نموذج إضافة المواد وتحديثها
    with st.form("inventory_form"):
        st.subheader(t["add_update"])
        item_name = st.text_input(t["item_name"]).strip()
        qty = st.number_input(t["quantity"], min_value=1, step=1)
        price = st.number_input(t["price"], min_value=0.0, step=0.5)
        submit_item = st.form_submit_button(t["save_item"])
    
    if submit_item:
        if item_name:
            if not st.session_state.is_paid_user:
                current_product_added = st.session_state.product_daily_adds.get(item_name, 0)
                if (current_product_added + qty) > 100:
                    st.error(t["product_limit_reached"])
                    st.stop()

            existing_item = run_query("SELECT id, quantity, is_locked FROM inventory WHERE name = ?", (item_name,), fetch=True)
            
            if existing_item:
                item_id, current_qty, is_locked = existing_item[0]
                if is_locked == 1:
                    st.warning(f"'{item_name}' {t['item_locked']}")
                else:
                    new_qty = current_qty + qty
                    run_query("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (new_qty, price, item_id))
                    if not st.session_state.is_paid_user:
                        st.session_state.product_daily_adds[item_name] = st.session_state.product_daily_adds.get(item_name, 0) + qty
                    st.success(f"{t['updated']} '{item_name}'! New Qty: {new_qty}")
                    st.rerun()
            else:
                run_query("INSERT INTO inventory (name, quantity, price, is_locked) VALUES (?, ?, ?, 0)", (item_name, qty, price))
                if not st.session_state.is_paid_user:
                    st.session_state.product_daily_adds[item_name] = st.session_state.product_daily_adds.get(item_name, 0) + qty
                st.success(f"{t['added']} '{item_name}'!")
                st.rerun()
        else:
            st.error(t["enter_valid"])

    st.divider()
    st.subheader(t["inventory_grid"])
    
    items = run_query("SELECT id, name, quantity, price, is_locked FROM inventory", fetch=True)
    
    if items:
        cols = st.columns(2)
        for index, item in enumerate(items):
            item_id, name, quantity, price, is_locked = item
            target_col = cols[index % 2]
            with target_col:
                with st.container(border=True):
                    st.markdown(f"### 📦 {name}")
                    st.write(f"**{t['qty']}**: {quantity} | **{t['unit_price']}**: ${price}")
                    st.write(f"**{t['total_value']}**: ${quantity * price}")
                    
                    if is_locked == 0:
                        if st.button(t["lock"], key=f"lock_{item_id}"):
                            run_query("UPDATE inventory SET is_locked = 1 WHERE id = ?", (item_id,))
                            st.rerun()
                    else:
                        if st.button(t["unlock"], key=f"unlock_{item_id}"):
                            run_query("UPDATE inventory SET is_locked = 0 WHERE id = ?", (item_id,))
                            st.rerun()
    else:
        st.info(t["empty"])

    st.divider()
    
    # --- التقارير والمجاميع ---
    st.subheader(t["reports_title"])
    if items:
        total_unique = len(items)
        total_quantity = sum([it[2] for it in items])
        total_inventory_val = sum([it[2] * it[3] for it in items])
        
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric(t["total_items"], total_unique)
        col_r2.metric(t["total_qty"], total_quantity)
        col_r3.metric(t["total_capital"], f"${total_inventory_val:.2f}")

    st.divider()
    
    # --- مولد الفواتير ---
    st.subheader(t["invoice_title"])
    if items:
        item_names = [it[1] for it in items]
        selected_inv_item = st.selectbox(t["select_item"], item_names)
        inv_qty = st.number_input(t["invoice_qty"], min_value=1, step=1, value=1)
        
        item_data = run_query("SELECT price FROM inventory WHERE name = ?", (selected_inv_item,), fetch=True)
        item_price = item_data[0][0] if item_data else 0.0
        total_amount = inv_qty * item_price
        
        if st.button(t["generate_invoice"]):
            st.success(f"Invoice Generated for {selected_inv_item}!")
            invoice_text = f"""
=====================================
          YASSER WEB INVOICE
=====================================
Date: {date.today()}
User: {st.session_state.username}
-------------------------------------
Item Name: {selected_inv_item}
Quantity : {inv_qty}
Unit Price: ${item_price}
-------------------------------------
TOTAL AMOUNT: ${total_amount:.2f}
=====================================
Thank you for your business!
"""
            st.text(invoice_text)
            st.download_button(
                label=t["download_invoice"],
                data=invoice_text,
                file_name=f"invoice_{selected_inv_item}.txt",
                mime="text/plain"
            )

# --- 6. التوجيه ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
