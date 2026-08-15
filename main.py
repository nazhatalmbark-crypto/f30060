import streamlit as st
import sqlite3
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Inventory System", layout="wide")

# --- 1. إعداد وتحديث قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    
    # جدول المواد
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    quantity INTEGER DEFAULT 0,
                    price REAL DEFAULT 0,
                    is_locked INTEGER DEFAULT 0)''')
    
    # جدول العملاء (بالتفاصيل الكاملة التي طلبتها)
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    shop_location TEXT,
                    governorate TEXT,
                    landmark TEXT)''')
    
    # إضافة حساب الافتراضي
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
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'is_unlocked' not in st.session_state:
    st.session_state.is_unlocked = False

# --- 3. واجهة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.subheader("🔐 تسجيل الدخول إلى ياسر ويب")
    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submit_login = st.form_submit_button("تسجيل الدخول")
        
        if submit_login:
            user = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username.strip(), password), fetch=True)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
else:
    # --- الشريط الجانبي للإعدادات والقفل ---
    st.sidebar.write(f"المستخدم: **{st.session_state.username}**")
    st.sidebar.divider()
    
    st.sidebar.subheader("🔐 تفعيل ميزات القفل")
    if not st.session_state.is_unlocked:
        with st.sidebar.form("activation_form"):
            code_input = st.text_input("أدخل رمز التفعيل (2009):", type="password")
            submit_code = st.form_submit_button("تفعيل")
            
            if submit_code:
                if code_input == "2009":
                    st.session_state.is_unlocked = True
                    st.success("تم تفعيل القفل بنجاح!")
                    st.rerun()
                else:
                    st.error("رمز التفعيل خطأ!")
    else:
        st.sidebar.success("✅ ميزات القفل مفعلة")
        if st.sidebar.button("إيقاف التفعيل"):
            st.session_state.is_unlocked = False
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    # العنوان الرئيسي
    st.title("📦 ياسر ويب - نظام إدارة المخزون الشامل")

    # --- التبويبات (فصل تام بين كل الأقسام) ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ إضافة مادة جديدة", 
        "👥 إضافة عميل جديد", 
        "📦 عرض المواد (شبكة)", 
        "📊 التقارير المالية والأرباح", 
        "🧾 مولد الفواتير"
    ])

    # --- تبويب 1: إضافة مادة جديدة ---
    with tab1:
        st.subheader("إضافة أو تحديث مادة في المخزن")
        with st.form("inventory_form"):
            item_name = st.text_input("اسم المادة").strip()
            qty = st.number_input("الكمية", min_value=1, step=1)
            price = st.number_input("سعر المفرد (د.ع)", min_value=0.0, step=250.0)
            submit_item = st.form_submit_button("حفظ المادة")
        
        if submit_item:
            if item_name:
                existing_item = run_query("SELECT id, quantity, is_locked FROM inventory WHERE name = ?", (item_name,), fetch=True)
                
                if existing_item:
                    item_id, current_qty, is_locked = existing_item[0]
                    if is_locked == 1:
                        st.warning(f"مادة '{item_name}' مقفلة! لا يمكنك تعديلها.")
                    else:
                        new_qty = current_qty + qty
                        run_query("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (new_qty, price, item_id))
                        st.success(f"تم تحديث مادة '{item_name}' بنجاح! الكمية الجديدة: {new_qty}")
                        st.rerun()
                else:
                    run_query("INSERT INTO inventory (name, quantity, price, is_locked) VALUES (?, ?, ?, 0)", (item_name, qty, price))
                    st.success(f"تم إضافة مادة '{item_name}' بنجاح!")
                    st.rerun()
            else:
                st.error("الرجاء إدخال اسم مادة صحيح.")

    # --- تبويب 2: إضافة عميل جديد (بالتفاصيل الكاملة) ---
    with tab2:
        st.subheader("إضافة عميل جديد مع كافة التفاصيل")
        with st.form("add_customer_form"):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                cust_name = st.text_input("اسم العميل").strip()
                cust_phone = st.text_input("رقم الهاتف").strip()
                cust_gov = st.text_input("المحافظة").strip()
            with c_col2:
                cust_shop = st.text_input("مكان المحل").strip()
                cust_landmark = st.text_input("أقرب نقطة دالة").strip()
                
            submit_cust = st.form_submit_button("حفظ بيانات العميل")
            
        if submit_cust:
            if cust_name:
                run_query("INSERT INTO customers (name, phone, shop_location, governorate, landmark) VALUES (?, ?, ?, ?, ?)", 
                          (cust_name, cust_phone, cust_shop, cust_gov, cust_landmark))
                st.success(f"تم إضافة العميل '{cust_name}' بنجاح!")
                st.rerun()
            else:
                st.error("الرجاء إدخال اسم العميل على الأقل.")
        
        st.divider()
        st.subheader("قائمة العملاء المسجلين")
        customers = run_query("SELECT name, phone, shop_location, governorate, landmark FROM customers", fetch=True)
        if customers:
            for c in customers:
                st.write(f"- 👤 **{c[0]}** | 📱 الهاتف: {c[1] or 'لا يوجد'} | 📍 المحل: {c[2] or 'لا يوجد'} | 🏛️ المحافظة: {c[3] or 'لا يوجد'} | 🚩 نقطة دالة: {c[4] or 'لا توجد'}")
        else:
            st.info("لا يوجد عملاء مسجلين حالياً.")

    # --- تبويب 3: عرض المواد بشكل شبكة (Grid Cards) ---
    with tab3:
        st.subheader("شبكة المواد الحالية في المخزن")
        items = run_query("SELECT id, name, quantity, price, is_locked FROM inventory", fetch=True)
        
        if items:
            cols = st.columns(3) # شبكة من 3 أعمدة
            for index, item in enumerate(items):
                item_id, name, quantity, price, is_locked = item
                target_col = cols[index % 3]
                with target_col:
                    with st.container(border=True):
                        st.markdown(f"### 📦 {name}")
                        st.write(f"**الكمية**: {quantity}")
                        st.write(f"**السعر**: {price:,.0f} د.ع")
                        st.write(f"**القيمة الكلية**: {quantity * price:,.0f} د.ع")
                        
                        # أزرار القفل تتفعل فقط عند إدخال رمز 2009 في القائمة الجانبية
                        if st.session_state.is_unlocked:
                            btn_text = "🔓 فتح القفل" if is_locked == 1 else "🔒 قفل المادة"
                            if st.button(btn_text, key=f"grid_lock_{item_id}"):
                                new_lock = 0 if is_locked == 1 else 1
                                run_query("UPDATE inventory SET is_locked = ? WHERE id = ?", (new_lock, item_id))
                                st.rerun()
                        else:
                            if is_locked == 1:
                                st.info("🔒 مقفلة")
        else:
            st.info("المخزن فارغ حالياً.")

    # --- تبويب 4: التقارير المالية والرسوم البيانية ---
    with tab4:
        st.subheader("التقارير المالية والأرباح والحسابات التلقائية")
        items = run_query("SELECT id, name, quantity, price, is_locked FROM inventory", fetch=True)
        
        if items:
            total_unique = len(items)
            total_quantity = sum([it[2] for it in items])
            total_capital = sum([it[2] * it[3] for it in items])
            
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("إجمالي المواد المختلفة", total_unique)
            col_r2.metric("إجمالي الكمية بالمخزن", total_quantity)
            col_r3.metric("إجمالي فلوسك وقيمة المخزن", f"{total_capital:,.0f} د.ع")
            
            st.divider()
            st.subheader("الرسم البياني لقيم المواد")
            chart_data = {it[1]: it[2] * it[3] for it in items}
            st.bar_chart(chart_data)
        else:
            st.info("لا توجد بيانات كافية لعرض التقارير.")

    # --- تبويب 5: مولد الفواتير ---
    with tab5:
        st.subheader("مولد الفواتير والإيصالات السريعة")
        items = run_query("SELECT id, name, quantity, price, is_locked FROM inventory", fetch=True)
        
        if items:
            item_names = [it[1] for it in items]
            selected_inv_item = st.selectbox("اختر المادة للفاتورة", item_names)
            inv_qty = st.number_input("الكمية المباعة", min_value=1, step=1, value=1)
            
            if st.button("إصدار الفاتورة"):
                item_data = run_query("SELECT price FROM inventory WHERE name = ?", (selected_inv_item,), fetch=True)
                item_price = item_data[0][0] if item_data else 0.0
                total_amount = inv_qty * item_price
                
                invoice_text = f"""
=====================================
          YASSER WEB INVOICE
=====================================
التاريخ: {date.today()}
المستخدم: {st.session_state.username}
-------------------------------------
المادة: {selected_inv_item}
الكمية: {inv_qty}
سعر المفرد: {item_price:,.0f} د.ع
-------------------------------------
إجمالي المبلغ: {total_amount:,.0f} د.ع
=====================================
شكراً لتعاملكم معنا!
"""
                st.text(invoice_text)
                st.download_button(
                    label="📥 تحميل الفاتورة (ملف نصي TXT)",
                    data=invoice_text,
                    file_name=f"invoice_{selected_inv_item}.txt",
                    mime="text/plain"
                )
        else:
            st.info("المخزن فارغ، لا يمكن إصدار فاتورة.")
