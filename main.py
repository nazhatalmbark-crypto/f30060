import streamlit as st
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Inventory System", layout="centered")

# --- 1. إعداد قاعدة البيانات ---
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
                    is_locked INTEGER DEFAULT 0)''')
    
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

# --- 2. تهيئة حالة الجلسة ---
def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'add_operation_count' not in st.session_state:
        st.session_state.add_operation_count = 0
    if 'is_paid_user' not in st.session_state:
        st.session_state.is_paid_user = False

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
        "user_exists": "Username already exists. Please choose another one.",
        "app_title": "📦 Yasser Web - Inventory System",
        "account_settings": "Account Settings",
        "user": "User",
        "premium": "Upgrade to Premium (Unlock All Features)",
        "free_used": "Free Additions Used",
        "logout": "Logout",
        "add_update": "Add or Update Item",
        "item_name": "Item Name",
        "quantity": "Quantity",
        "save_item": "Save Item",
        "limit_reached": "Free limit reached (5/5)! Upgrade to Premium for unlimited additions.",
        "item_locked": "is locked. You cannot add quantity to it.",
        "updated": "Successfully updated",
        "added": "Successfully added new item",
        "enter_valid": "Please enter a valid item name.",
        "inventory_list": "Current Inventory Grid (Saved in Database)",
        "qty": "Qty",
        "lock": "Lock (Premium)",
        "unlock": "Unlock (Premium)",
        "premium_required": "🔒 Premium Feature",
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
        "user_exists": "اسم المستخدم موجود مسبقاً، يرجى اختيار اسم آخر.",
        "app_title": "📦 ياسر ويب - نظام إدارة المخزون",
        "account_settings": "إعدادات الحساب",
        "user": "المستخدم",
        "premium": "ترقية للحساب المدفوع (فتح كافة الميزات)",
        "free_used": "الإضافات المجانية المستخدمة",
        "logout": "تسجيل الخروج",
        "add_update": "إضافة أو تحديث مادة",
        "item_name": "اسم المادة",
        "quantity": "الكمية",
        "save_item": "حفظ المادة",
        "limit_reached": "وصلت للحد المجاني (5/5)! قم بالترقية للحساب المدفوع لإضافات غير محدودة.",
        "item_locked": "مقفلة. لا يمكنك إضافة كمية لها.",
        "updated": "تم تحديث بنجاح",
        "added": "تم إضافة مادة جديدة بنجاح",
        "enter_valid": "الرجاء إدخال اسم مادة صحيح.",
        "inventory_list": "شبكة المخزون الحالي (محفوظة بقاعدة البيانات)",
        "qty": "الكمية",
        "lock": "قفل (مدفوع)",
        "unlock": "فتح القفل (مدفوع)",
        "premium_required": "🔒 ميزة مدفوعة",
        "empty": "المخزون فارغ حالياً."
    }
}

# --- 4. واجهة تسجيل الدخول وإنشاء الحساب ---
def login_screen():
    selected_lang = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"])
    t = translations[selected_lang]
    
    tab1, tab2 = st.tabs([t["login_tab"], t["register_tab"]])
    
    with tab1:
        st.subheader(t["login_title"])
        with st.form("login_form"):
            username = st.text_input(t["username"], key="login_user")
            password = st.text_input(t["password"], type="password", key="login_pass")
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
            new_username = st.text_input(t["username"], key="reg_user")
            new_password = st.text_input(t["password"], type="password", key="reg_pass")
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
    
    if not st.session_state.is_paid_user:
        st.sidebar.info(f"{t['free_used']}: {st.session_state.add_operation_count} / 5")
    else:
        st.sidebar.success("🌟 Premium User: All features unlocked!")
    
    if st.sidebar.button(t["logout"]):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # نموذج إضافة المواد وتحديثها
    with st.form("inventory_form"):
        st.subheader(t["add_update"])
        item_name = st.text_input(t["item_name"])
        qty = st.number_input(t["quantity"], min_value=1, step=1)
        submit_item = st.form_submit_button(t["save_item"])
    
    if submit_item:
        if item_name.strip():
            if not st.session_state.is_paid_user and st.session_state.add_operation_count >= 5:
                st.error(t["limit_reached"])
            else:
                existing_item = run_query("SELECT id, quantity, is_locked FROM inventory WHERE name = ?", (item_name.strip(),), fetch=True)
                
                if existing_item:
                    item_id, current_qty, is_locked = existing_item[0]
                    if is_locked == 1:
                        st.warning(f"'{item_name}' {t['item_locked']}")
                    else:
                        new_qty = current_qty + qty
                        run_query("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, item_id))
                        if not st.session_state.is_paid_user:
                            st.session_state.add_operation_count += 1
                        st.success(f"{t['updated']} '{item_name}'! New Qty: {new_qty}")
                        st.rerun()
                else:
                    run_query("INSERT INTO inventory (name, quantity, is_locked) VALUES (?, ?, 0)", (item_name.strip(), qty))
                    if not st.session_state.is_paid_user:
                        st.session_state.add_operation_count += 1
                    st.success(f"{t['added']} '{item_name}'!")
                    st.rerun()
        else:
            st.error(t["enter_valid"])

    st.divider()
    st.subheader(t["inventory_list"])
    
    items = run_query("SELECT id, name, quantity, is_locked FROM inventory", fetch=True)
    
    if items:
        # عرض المواد على شكل شبكة (Grid Cards) بعمودين لتظهر بشكل منظم وجميل
        cols = st.columns(2)
        for index, item in enumerate(items):
            item_id, name, quantity, is_locked = item
            target_col = cols[index % 2]
            with target_col:
                with st.container(border=True):
                    st.write(f"📦 **{name}**")
                    st.write(f"{t['qty']}: **{quantity}**")
                    
                    if st.session_state.is_paid_user:
                        if is_locked == 0:
                            if st.button(t["lock"], key=f"lock_{item_id}"):
                                run_query("UPDATE inventory SET is_locked = 1 WHERE id = ?", (item_id,))
                                st.rerun()
                        else:
                            if st.button(t["unlock"], key=f"unlock_{item_id}"):
                                run_query("UPDATE inventory SET is_locked = 0 WHERE id = ?", (item_id,))
                                st.rerun()
                    else:
                        if is_locked == 1:
                            st.write("🚫 Locked")
                        else:
                            st.write(t["premium_required"])
    else:
        st.info(t["empty"])

# --- 6. التوجيه ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
