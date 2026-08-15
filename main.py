import streamlit as st
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Inventory System", layout="centered")

# --- 1. إعداد قاعدة البيانات لضمان عدم ضياع أي بيانات ---
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
        "login_title": "🔐 Login to Yasser Web",
        "username": "Username",
        "password": "Password",
        "signin": "Sign In",
        "login_success": "Login successful!",
        "login_error": "Invalid username or password.",
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
        "inventory_list": "Current Inventory List (Saved in Database)",
        "qty": "Qty",
        "lock": "Lock (Premium)",
        "unlock": "Unlock (Premium)",
        "premium_required": "🔒 Premium Feature",
        "empty": "The inventory is currently empty."
    },
    "العربية": {
        "login_title": "🔐 تسجيل الدخول إلى ياسر ويب",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "signin": "تسجيل الدخول",
        "login_success": "تم تسجيل الدخول بنجاح!",
        "login_error": "اسم المستخدم أو كلمة المرور غير صحيحة.",
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
        "inventory_list": "قائمة المخزون الحالي (محفوظة بقاعدة البيانات)",
        "qty": "الكمية",
        "lock": "قفل (مدفوع)",
        "unlock": "فتح القفل (مدفوع)",
        "premium_required": "🔒 ميزة مدفوعة",
        "empty": "المخزون فارغ حالياً."
    }
}

# --- 4. واجهة تسجيل الدخول ---
def login_screen():
    selected_lang = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"])
    t = translations[selected_lang]
    
    st.title(t["login_title"])
    with st.form("login_form"):
        username = st.text_input(t["username"])
        password = st.text_input(t["password"], type="password")
        submit_login = st.form_submit_button(t["signin"])
        
        if submit_login:
            user = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username, password), fetch=True)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(t["login_success"])
                st.rerun()
            else:
                st.error(t["login_error"])

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
        for item in items:
            item_id, name, quantity, is_locked = item
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"**{name}**")
            col2.write(f"{t['qty']}: {quantity}")
            
            if st.session_state.is_paid_user:
                if is_locked == 0:
                    if col3.button(t["lock"], key=f"lock_{item_id}"):
                        run_query("UPDATE inventory SET is_locked = 1 WHERE id = ?", (item_id,))
                        st.rerun()
                else:
                    if col3.button(t["unlock"], key=f"unlock_{item_id}"):
                        run_query("UPDATE inventory SET is_locked = 0 WHERE id = ?", (item_id,))
                        st.rerun()
            else:
                if is_locked == 1:
                    col3.write("🚫 Locked")
                else:
                    col3.write(t["premium_required"])
    else:
        st.info(t["empty"])

# --- 6. التوجيه ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
