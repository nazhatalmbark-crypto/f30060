import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات صفحة التطبيق
st.set_page_config(
    page_title="نظام المبيعات والمخزون المتطور",
    page_icon="🛒",
    layout="wide"
)

# ==========================================
# 1. القواميس الخاصة باللغات (عربي / إنجليزي)
# ==========================================
translations = {
    "ar": {
        "page_title": "🛒 نظام المبيعات والمخزون المتطور",
        "login_title": "🔐 تسجيل الدخول للنظام",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_btn": "دخول",
        "login_error": "اسم المستخدم أو كلمة المرور غير صحيحة!",
        "user": "المستخدم",
        "role": "الصلاحية",
        "logout": "تسجيل الخروج",
        "welcome_admin": "أهلاً بك يا مدير. لديك صلاحيات كاملة لإدارة النظام والتقارير.",
        "welcome_cashier": "أهلاً بك. صلاحياتك مقتصرة على إنشاء الفواتير وإجراء عمليات البيع.",
        "nav_title": "القائمة الرئيسية",
        "tab_sales": "نقطة البيع (POS)",
        "tab_inventory": "إدارة المخزون",
        "tab_expenses": "المصروفات النثرية",
        "tab_audit": "سجل النشاطات (Audit Logs)",
        "tab_reports": "التقارير والأرباح",
        "low_stock_title": "⚠️ تنبيهات قرب نفاد المخزون",
        "whatsapp_share": "إرسال الفاتورة عبر واتساب",
        "whatsapp_success": "تم تجهيز رابط الفاتورة والإرسال بنجاح!",
        "save_expense": "حفظ المصروف",
        "expense_added": "تمت إضافة المصروف بنجاح!",
        "currency": "د.ع"
    },
    "en": {
        "page_title": "🛒 Advanced Sales & Inventory System",
        "login_title": "🔐 System Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "login_error": "Incorrect username or password!",
        "user": "User",
        "role": "Role",
        "logout": "Logout",
        "welcome_admin": "Welcome Manager. You have full access to system controls and reports.",
        "welcome_cashier": "Welcome. Your access is restricted to invoicing and sales operations.",
        "nav_title": "Main Menu",
        "tab_sales": "Point of Sale (POS)",
        "tab_inventory": "Inventory Management",
        "tab_expenses": "Daily Expenses",
        "tab_audit": "Audit Trail & Logs",
        "tab_reports": "Reports & Profits",
        "low_stock_title": "⚠️ Low Stock Alerts",
        "whatsapp_share": "Send Invoice via WhatsApp",
        "whatsapp_success": "Invoice link generated and ready to send via WhatsApp!",
        "save_expense": "Save Expense",
        "expense_added": "Expense added successfully!",
        "currency": "IQD"
    }
}

# اختيار اللغة من الشريط الجانبي
st.sidebar.markdown("---")
lang_choice = st.sidebar.selectbox("🌐 Language / اللغة", options=["العربية", "English"])
current_lang = "ar" if lang_choice == "العربية" else "en"
t = translations[current_lang]

# ==========================================
# 2. تهيئة الذاكرة المؤقتة (Session State)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = pd.DataFrame(columns=["التوقيت / Time", "المستخدم / User", "العملية / Action"])

if "expenses_list" not in st.session_state:
    st.session_state.expenses_list = pd.DataFrame(columns=["التاريخ / Date", "البيان / Description", "المبلغ / Amount"])

if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame({
        "المادة / Item": ["لابتوب ديل", "ماوس لاسلكي", "شاشة 24 بوصة"],
        "السعر / Price": [450000, 15000, 180000],
        "الكمية / Qty": [3, 12, 4]  # لابتوب وشاشة قليلين لاختبار التنبيهات
    })

# ==========================================
# 3. شاشة تسجيل الدخول
# ==========================================
if not st.session_state.logged_in:
    st.title(t["page_title"])
    st.subheader(t["login_title"])
    
    users_db = {
        "admin": {"password": "123", "role_ar": "مدير النظام", "role_en": "System Manager", "name": "المدير العام"},
        "cashier": {"password": "456", "role_ar": "كاشير", "role_en": "Cashier", "name": "موظف المبيعات"},
        "sales": {"password": "789", "role_ar": "مسؤول مبيعات", "role_en": "Sales Officer", "name": "مسؤول المعرض"}
    }
    
    with st.form("login_form"):
        username_input = st.text_input(t["username"])
        password_input = st.text_input(t["password"], type="password")
        submit_btn = st.form_submit_button(t["login_btn"])
        
        if submit_btn:
            if username_input in users_db and users_db[username_input]["password"] == password_input:
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.session_state.role = users_db[username_input]["role_ar"] if current_lang == "ar" else users_db[username_input]["role_en"]
                st.session_state.name = users_db[username_input]["name"]
                
                # تسجيل الدخول في السجل
                new_log = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.name, "تسجيل دخول للنظام"]], 
                                         columns=st.session_state.audit_logs.columns)
                st.session_state.audit_logs = pd.concat([st.session_state.audit_logs, new_log], ignore_index=True)
                st.rerun()
            else:
                st.error(t["login_error"])
    st.stop()

# ==========================================
# 4. واجهة المستخدم بعد تسجيل الدخول
# ==========================================
st.sidebar.markdown(f"👤 **{t['user']}:** {st.session_state.name}")
st.sidebar.markdown(f"🏷️ **{t['role']}:** `{st.session_state.role}`")

if st.sidebar.button(t["logout"]):
    st.session_state.logged_in = False
    st.rerun()

st.title(t["page_title"])

# التحقق من الصلاحيات والترحيب
is_manager = "مدير" in st.session_state.role or "Manager" in st.session_state.role

if is_manager:
    st.success(t["welcome_admin"])
else:
    st.info(t["welcome_cashier"])

# نظام التنبيهات للمخزون القليل (أقل من 5 قطع)
low_stock_items = st.session_state.inventory[st.session_state.inventory["الكمية / Qty"] < 5]
if not low_stock_items.empty:
    with st.expander(t["low_stock_title"], expanded=True):
        st.warning("المواد التالية اقتربت على النفاد، يرجى إعادة طلبها:")
        st.dataframe(low_stock_items, use_container_width=True)

# التبويبات الرئيسية للنظام
tabs = [t["tab_sales"], t["tab_inventory"], t["tab_expenses"]]
if is_manager:
    tabs.extend([t["tab_audit"], t["tab_reports"]])

selected_tab = st.selectbox(t["nav_title"], tabs)

# ------------------------------------------
# تبويب 1: نقطة البيع (POS)
# ------------------------------------------
if selected_tab == t["tab_sales"]:
    st.subheader(t["tab_sales"])
    col1, col2 = st.columns(2)
    
    with col1:
        selected_item = st.selectbox("اختر المادة / Select Item", st.session_state.inventory["المادة / Item"])
        item_row = st.session_state.inventory[st.session_state.inventory["المادة / Item"] == selected_item].iloc[0]
        item_price = item_row["السعر / Price"]
        st.write(f"السعر المفرد: **{item_price:,} {t['currency']}**")
        qty = st.number_input("الكمية / Qty", min_value=1, value=1)
        
    with col2:
        total_amount = item_price * qty
        st.info(f"إجمالي الفاتورة: **{total_amount:,} {t['currency']}**")
        if st.button("إتمام البيع / Complete Sale"):
            st.success(f"تمت عملية البيع بنجاح بمبلغ {total_amount:,} {t['currency']}!")
            # زر إرسال واتساب تجريبي
            whatsapp_link = f"https://wa.me/?text=فاتورة مبيعات بقيمة {total_amount} {t['currency']}"
            st.markdown(f"📱 [{t['whatsapp_share']}]({whatsapp_link})")
            
            # تسجيل العملية في السجل
            new_log = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.name, f"إصدار فاتورة مبيعات بقيمة {total_amount}"]], 
                                     columns=st.session_state.audit_logs.columns)
            st.session_state.audit_logs = pd.concat([st.session_state.audit_logs, new_log], ignore_index=True)

# ------------------------------------------
# تبويب 2: إدارة المخزون
# ------------------------------------------
elif selected_tab == t["tab_inventory"]:
    st.subheader(t["tab_inventory"])
    st.dataframe(st.session_state.inventory, use_container_width=True)
    
    if is_manager:
        with st.form("add_item_form"):
            st.subheader("إضافة مادة جديدة للمخزون")
            new_name = st.text_input("اسم المادة")
            new_price = st.number_input("السعر", min_value=0.0)
            new_qty = st.number_input("الكمية", min_value=0, step=1)
            add_btn = st.form_submit_button("إضافة للمخزون")
            
            if add_btn and new_name:
                new_row = pd.DataFrame({"المادة / Item": [new_name], "السعر / Price": [new_price], "الكمية / Qty": [new_qty]})
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
                st.success("تمت إضافة المادة بنجاح!")
                st.rerun()

# ------------------------------------------
# تبويب 3: المصروفات النثرية
# ------------------------------------------
elif selected_tab == t["tab_expenses"]:
    st.subheader(t["tab_expenses"])
    
    with st.form("expense_form"):
        exp_desc = st.text_input("بيان المصروف (مثل: كهرباء، أجور نقل)")
        exp_amount = st.number_input("المبلغ", min_value=0.0)
        exp_btn = st.form_submit_button(t["save_expense"])
        
        if exp_btn and exp_desc:
            new_exp = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), exp_desc, exp_amount]], 
                                     columns=st.session_state.expenses_list.columns)
            st.session_state.expenses_list = pd.concat([st.session_state.expenses_list, new_exp], ignore_index=True)
            st.success(t["expense_added"])
            
    if not st.session_state.expenses_list.empty:
        st.write("سجل المصروفات المسجلة:")
        st.dataframe(st.session_state.expenses_list, use_container_width=True)

# ------------------------------------------
# تبويب 4: سجل النشاطات (خاص بالمدير)
# ------------------------------------------
elif selected_tab == t["tab_audit"] and is_manager:
    st.subheader(t["tab_audit"])
    st.dataframe(st.session_state.audit_logs, use_container_width=True)

# ------------------------------------------
# تبويب 5: التقارير والأرباح (خاص بالمدير)
# ------------------------------------------
elif selected_tab == t["tab_reports"] and is_manager:
    st.subheader(t["tab_reports"])
    total_inventory_value = (st.session_state.inventory["السعر / Price"] * st.session_state.inventory["الكمية / Qty"]).sum()
    total_expenses = st.session_state.expenses_list["المبلغ / Amount"].sum() if not st.session_state.expenses_list.empty else 0
    
    col1, col2 = st.columns(2)
    col1.metric("إجمالي قيمة البضاعة بالمخزون", f"{total_inventory_value:,} {t['currency']}")
    col2.metric("إجمالي المصروفات النثرية", f"{total_expenses:,} {t['currency']}")
