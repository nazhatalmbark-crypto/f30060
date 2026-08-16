import streamlit as st
import sqlite3
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Complete System", layout="wide")

# --- 1. إعداد قاعدة البيانات (تخزين الأرقام كـ REAL لدعم البوينتات) ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity REAL DEFAULT 0, price REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, shop_location TEXT, governorate TEXT, landmark TEXT)''')
    
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

# --- 2. إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- 3. تسجيل الدخول أو إنشاء حساب ---
if not st.session_state.logged_in:
    st.title("⚡ ياسر ويب - نظام إدارة المحلات والأرباح")
    choice = st.radio("اختر العملية:", ["تسجيل دخول", "إنشاء حساب جديد"])
    
    if choice == "تسجيل دخول":
        st.subheader("🔐 تسجيل الدخول")
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                user = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username.strip(), password), fetch=True)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error("خطأ في اسم المستخدم أو كلمة المرور.")
    else:
        st.subheader("📝 إنشاء حساب جديد")
        with st.form("signup_form"):
            new_user = st.text_input("اسم مستخدم جديد")
            new_pass = st.text_input("كلمة مرور جديدة", type="password")
            if st.form_submit_button("إنشاء الحساب"):
                if new_user and new_pass:
                    try:
                        run_query("INSERT INTO users (username, password) VALUES (?, ?)", (new_user.strip(), new_pass))
                        st.success("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
                    except sqlite3.IntegrityError:
                        st.error("اسم المستخدم موجود مسبقاً.")
                else:
                    st.error("الرجاء ملء جميع الحقول.")
else:
    # --- الشريط الجانبي ---
    st.sidebar.write(f"المستخدم: **{st.session_state.username}**")
    st.sidebar.divider()
    
    st.sidebar.subheader("🔐 حالة النسخة")
    if not st.session_state.is_unlocked:
        st.sidebar.warning("النسخة حالياً تجريبية")
    else:
        st.sidebar.success("✅ النسخة الكاملة مفعلة")
        if st.sidebar.button("إيقاف التفعيل"):
            st.session_state.is_unlocked = False
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📦 ياسر ويب - نظام إدارة المخزون والفواتير (يدعم البوينتات)")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ إضافة مادة", "👥 إضافة عميل", "📦 شبكة المواد", "📊 التقارير والأرباح", "🧾 الفواتير (قص المواد)"
    ])

    # --- تبويب 1: إضافة مادة (تدعم البوينتات) ---
    with tab1:
        st.subheader("إضافة أو تحديث مادة (تدعم الكسور والبوينتات)")
        with st.form("add_item_form"):
            name = st.text_input("اسم المادة").strip()
            qty = st.number_input("الكمية (تقبل بوينتات مثل 1.5)", min_value=0.01, value=1.0, step=0.25, format="%.2f")
            price = st.number_input("السعر بالدينار (يقبل بوينتات مثل 425.5)", min_value=0.0, value=1000.0, step=0.25, format="%.2f")
            
            if st.form_submit_button("حفظ المادة"):
                if not st.session_state.is_unlocked and qty > 100:
                    st.error("⚠️ النسخة المجانية تسمح بحد أقصى 100 لكل إدخال!")
                elif name:
                    existing = run_query("SELECT id, quantity FROM inventory WHERE name = ?", (name,), fetch=True)
                    if existing:
                        item_id, current_qty = existing[0]
                        new_qty = current_qty + qty
                        run_query("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (new_qty, price, item_id))
                        st.success(f"تم تحديث مادة '{name}' بنجاح! الكمية الجديدة: {new_qty}")
                    else:
                        run_query("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
                        st.success(f"تم إضافة مادة '{name}' بنجاح!")
                else:
                    st.error("الرجاء إدخال اسم المادة.")

    # --- تبويب 2: العملاء ---
    with tab2:
        st.subheader("إضافة عميل جديد")
        with st.form("add_cust"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("اسم العميل")
                p = st.text_input("رقم الهاتف")
                g = st.text_input("المحافظة")
            with c2:
                s = st.text_input("مكان المحل")
                l = st.text_input("أقرب نقطة دالة")
            if st.form_submit_button("حفظ بيانات العميل"):
                if n:
                    run_query("INSERT INTO customers (name, phone, shop_location, governorate, landmark) VALUES (?, ?, ?, ?, ?)", (n, p, s, g, l))
                    st.success("تم حفظ العميل بنجاح!")
                else:
                    st.error("أدخل اسم العميل على الأقل.")
        
        st.divider()
        customers = run_query("SELECT name, phone, shop_location, governorate, landmark FROM customers", fetch=True)
        if customers:
            for c in customers:
                st.write(f"- 👤 **{c[0]}** | 📱 الهاتف: {c[1] or 'لا يوجد'} | 📍 المحل: {c[2] or 'لا يوجد'} | 🏛️ المحافظة: {c[3] or 'لا يوجد'} | 🚩 نقطة دالة: {c[4] or 'لا توجد'}")

    # --- تبويب 3: شبكة المواد ---
    with tab3:
        st.subheader("شبكة المواد الحالية")
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        if items:
            cols = st.columns(3)
            for index, item in enumerate(items):
                item_id, name, quantity, price = item
                with cols[index % 3]:
                    with st.container(border=True):
                        st.markdown(f"### 📦 {name}")
                        st.metric("الكمية المتاحة", f"{quantity:,.2f}")
                        st.metric("السعر", f"{price:,.2f} د.ع")
                        st.write(f"**القيمة الكلية**: {(quantity * price):,.2f} د.ع")
                        
                        if st.button("حذف المادة ❌", key=f"del_{item_id}"):
                            run_query("DELETE FROM inventory WHERE id = ?", (item_id,))
                            st.rerun()
        else:
            st.info("المخزن فارغ حالياً.")

    # --- تبويب 4: التقارير (مع قفل الرمز) ---
    with tab4:
        st.subheader("📊 تقارير الأرباح والمبيعات")
        
        if not st.session_state.is_unlocked:
            st.warning("🔒 **تقارير الأرباح المتقدمة وتصدير ملفات Excel مقفلة في النسخة التجريبية**")
            code_input = st.text_input("أدخل رمز التفعيل لفتح التقارير (رمز التفعيل: 2009):", type="password")
            if st.button("تفعيل التقارير"):
                if code_input == "2009":
                    st.session_state.is_unlocked = True
                    st.success("تم تفعيل النسخة الكاملة بنجاح!")
                    st.rerun()
                else:
                    st.error("رمز التفعيل غير صحيح!")
        else:
            st.success("✅ النسخة الكاملة مفعلة وتعمل بكامل طاقتها!")
            items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
            if items:
                total_unique = len(items)
                total_quantity = sum([it[2] for it in items])
                total_capital = sum([it[2] * it[3] for it in items])
                
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("إجمالي المواد المختلفة", total_unique)
                col_r2.metric("إجمالي الكمية بالمخزن", f"{total_quantity:,.2f}")
                col_r3.metric("إجمالي قيمة المخزن", f"{total_capital:,.2f} د.ع")
                
                st.divider()
                chart_data = {it[1]: it[2] * it[3] for it in items}
                st.bar_chart(chart_data)

    # --- تبويب 5: الفواتير وقص المواد (بالبوينتات) ---
    with tab5:
        st.subheader("🧾 مولد الفواتير وقص المواد تلقائياً من المخزن")
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        if items:
            item_names = [it[1] for it in items]
            selected_inv_item = st.selectbox("اختر المادة للبيع (القص)", item_names)
            
            curr_item_data = run_query("SELECT quantity, price FROM inventory WHERE name = ?", (selected_inv_item,), fetch=True)
            available_qty = curr_item_data[0][0] if curr_item_data else 0.0
            item_price = curr_item_data[0][1] if curr_item_data else 0.0
            
            st.info(f"الكمية المتاحة حالياً في المخزن: **{available_qty:,.2f}** | سعر المفرد: **{item_price:,.2f} د.ع**")
            
            # الكمية المباعة تقبل بوينتات
            inv_qty = st.number_input("الكمية المباعة (المراد قصها - تقبل بوينتات)", min_value=0.01, max_value=max(0.01, float(available_qty)), value=1.0, step=0.25, format="%.2f")
            
            if st.button("إصدار الفاتورة وقص الكمية"):
                if available_qty >= inv_qty:
                    new_qty = available_qty - inv_qty
                    run_query("UPDATE inventory SET quantity = ? WHERE name = ?", (new_qty, selected_inv_item))
                    
                    total_amount = inv_qty * item_price
                    invoice_text = f"""
=====================================
          YASSER WEB INVOICE
=====================================
التاريخ: {date.today()}
المستخدم: {st.session_state.username}
-------------------------------------
المادة المباعة: {selected_inv_item}
الكمية المقصوصة: {inv_qty:,.2f}
سعر المفرد: {item_price:,.2f} د.ع
-------------------------------------
إجمالي المبلغ: {total_amount:,.2f} د.ع
المتبقي بالمخزن: {new_qty:,.2f}
=====================================
تابع الحساب اسهل الطرق لإداره محلك
"""
                    st.success(f"تم إصدار الفاتورة وقص **{inv_qty:,.2f}** من مادة '{selected_inv_item}' بنجاح!")
                    st.text(invoice_text)
                    st.download_button(
                        label="📥 تحميل الفاتورة (ملف نصي TXT)",
                        data=invoice_text,
                        file_name=f"invoice_{selected_inv_item}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("الكمية المطلوبة أكبر من المتوفر في المخزن!")
        else:
            st.info("المخزن فارغ، لا يمكن إصدار فاتورة.")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>تابع الحساب اسهل الطرق لإداره محلك | ياسر ويب (yasser17781)</p>", unsafe_allow_html=True)
