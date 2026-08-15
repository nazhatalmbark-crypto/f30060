import streamlit as st
import sqlite3
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Inventory System", layout="centered")

# --- 1. إعداد وتحديث قاعدة البيانات ---
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
    
    try:
        c.execute("ALTER TABLE inventory ADD COLUMN price REAL DEFAULT 0;")
    except sqlite3.OperationalError:
        pass
    
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
    # القائمة الجانبية
    st.sidebar.write(f"المستخدم: **{st.session_state.username}**")
    st.sidebar.divider()
    
    # خانة رمز التفعيل (2009)
    st.sidebar.subheader("🔐 تفعيل ميزات القفل")
    if not st.session_state.is_unlocked:
        with st.sidebar.form("activation_form"):
            code_input = st.text_input("أدخل رمز التفعيل:", type="password")
            submit_code = st.form_submit_button("تفعيل")
            
            if submit_code:
                if code_input == "2009":
                    st.session_state.is_unlocked = True
                    st.success("تم التفعيل بنجاح!")
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
    st.title("📦 ياسر ويب - نظام إدارة المخزون")

    # --- خانة إضافة أو تحديث المواد ---
    with st.form("inventory_form"):
        st.subheader("➕ إضافة أو تحديث مادة جديدة")
        item_name = st.text_input("اسم المادة").strip()
        qty = st.number_input("الكمية", min_value=1, step=1)
        price = st.number_input("سعر المفرد (د.ع)", min_value=0.0, step=250.0)
        submit_item = st.form_submit_button("حفظ المادة في المخزن")
    
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

    st.divider()

    # جلب المواد من قاعدة البيانات
    items = run_query("SELECT id, name, quantity, price, is_locked FROM inventory", fetch=True)

    # --- التقارير المالية وحساب الفلوس تلقائياً ---
    if items:
        st.subheader("📊 التقارير المالية والأرباح")
        total_unique = len(items)
        total_quantity = sum([it[2] for it in items])
        total_capital = sum([it[2] * it[3] for it in items])
        
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("إجمالي المواد المختلفة", total_unique)
        col_r2.metric("إجمالي الكمية بالمخزن", total_quantity)
        col_r3.metric("إجمالي فلوسك وقيمة المخزن", f"{total_capital:,.0f} د.ع")
        
        st.divider()

        # --- الرسم البياني للمخزن ---
        st.subheader("📈 الرسم البياني لقيم المواد")
        chart_data = {it[1]: it[2] * it[3] for it in items}
        st.bar_chart(chart_data)

        st.divider()

    # --- شبكة المخزون الحالي (Cards) ---
    st.subheader("📦 شبكة المخزون الحالي")
    if items:
        cols = st.columns(2)
        for index, item in enumerate(items):
            item_id, name, quantity, price, is_locked = item
            target_col = cols[index % 2]
            with target_col:
                with st.container(border=True):
                    st.markdown(f"### 📦 {name}")
                    st.write(f"**الكمية**: {quantity} | **السعر**: {price:,.0f} د.ع")
                    st.write(f"**القيمة الكلية**: {quantity * price:,.0f} د.ع")
                    
                    # أزرار القفل تظهر فقط إذا تم إدخال رمز 2009 في الشريط الجانبي
                    if st.session_state.is_unlocked:
                        btn_text = "فتح القفل" if is_locked == 1 else "قفل المادة"
                        if st.button(btn_text, key=f"lock_btn_{item_id}"):
                            new_lock = 0 if is_locked == 1 else 1
                            run_query("UPDATE inventory SET is_locked = ? WHERE id = ?", (new_lock, item_id))
                            st.rerun()
                    else:
                        if is_locked == 1:
                            st.info("🔒 مقفلة")
    else:
        st.info("المخزن فارغ حالياً.")

    st.divider()
    
    # --- مولد الفواتير السريع ---
    st.subheader("🧾 مولد الفواتير والإيصالات")
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
