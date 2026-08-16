import streamlit as st
import sqlite3
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Complete System", layout="wide")

# --- 1. إعداد وتحديث قاعدة البيانات بالكامل ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    
    # الجدول الرئيسي للمستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    
    # جدول المواد المخزنة
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    quantity INTEGER DEFAULT 0,
                    price REAL DEFAULT 0)''')
    
    # جدول العملاء الكامل
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    shop_location TEXT,
                    governorate TEXT,
                    landmark TEXT)''')
    
    # تحديثات أمان الجداول القديمة
    for col in ["shop_location TEXT", "governorate TEXT", "landmark TEXT"]:
        try:
            c.execute(f"ALTER TABLE customers ADD COLUMN {col};")
        except sqlite3.OperationalError:
            pass
            
    # حساب الافتراضي
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

# --- 3. واجهة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("⚡ ياسر ويب - نظام إدارة المحلات والأرباح")
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
    # --- الشريط الجانبي (القفل والتحكم) ---
    st.sidebar.write(f"المستخدم: **{st.session_state.username}**")
    st.sidebar.divider()
    
    st.sidebar.subheader("🔐 تفعيل النسخة الكاملة")
    if not st.session_state.is_unlocked:
        code_input = st.sidebar.text_input("رمز التفعيل:", type="password")
        if st.sidebar.button("تفعيل"):
            if code_input == "2009":
                st.session_state.is_unlocked = True
                st.success("تم تفعيل النسخة الكاملة!")
                st.rerun()
            else:
                st.sidebar.error("رمز التفعيل خطأ!")
    else:
        st.sidebar.success("✅ النسخة المدفوعة مفعلة (بلا قيود)")
        if st.sidebar.button("إيقاف التفعيل"):
            st.session_state.is_unlocked = False
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    # --- واجهة النظام الرئيسية ---
    st.title("📦 ياسر ويب - نظام إدارة المخزون والعملاء والفواتير")

    # التبويبات الشاملة لكل الخانات
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ إضافة مادة", 
        "👥 إضافة عميل (كامل)", 
        "📦 شبكة المواد والتحكم", 
        "📊 التقارير والأرباح", 
        "🧾 الفواتير (قص المواد)"
    ])

    # --- تبويب 1: إضافة مادة ---
    with tab1:
        st.subheader("إضافة مادة جديدة للمخزن")
        with st.form("add_item_form"):
            item_name = st.text_input("اسم المادة").strip()
            qty = st.number_input("الكمية", min_value=1, step=1)
            price = st.number_input("السعر (د.ع)", min_value=0.0, step=250.0)
            
            if st.form_submit_button("حفظ المادة"):
                if not st.session_state.is_unlocked and qty > 100:
                    st.error("⚠️ النسخة المجانية تسمح بحد أقصى 100 كارتون/قطعة لكل إدخال! (أدخل رمز 2009 للتفعيل الحر).")
                elif item_name:
                    existing = run_query("SELECT id, quantity FROM inventory WHERE name = ?", (item_name,), fetch=True)
                    if existing:
                        item_id, current_qty = existing[0]
                        new_qty = current_qty + qty
                        run_query("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (new_qty, price, item_id))
                        st.success(f"تم تحديث مادة '{item_name}' بنجاح! الكمية الجديدة: {new_qty}")
                    else:
                        run_query("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (item_name, qty, price))
                        st.success(f"تم إضافة مادة '{item_name}' بنجاح!")
                else:
                    st.error("الرجاء إدخال اسم المادة.")

    # --- تبويب 2: إضافة عميل بكافة التفاصيل ---
    with tab2:
        st.subheader("إضافة عميل جديد (تفاصيل كاملة)")
        with st.form("add_customer_form"):
            c1, c2 = st.columns(2)
            with c1:
                cust_name = st.text_input("اسم العميل").strip()
                cust_phone = st.text_input("رقم الهاتف").strip()
                cust_gov = st.text_input("المحافظة").strip()
            with c2:
                cust_shop = st.text_input("مكان المحل").strip()
                cust_landmark = st.text_input("أقرب نقطة دالة").strip()
                
            if st.form_submit_button("حفظ بيانات العميل"):
                if cust_name:
                    run_query("INSERT INTO customers (name, phone, shop_location, governorate, landmark) VALUES (?, ?, ?, ?, ?)", 
                              (cust_name, cust_phone, cust_shop, cust_gov, cust_landmark))
                    st.success(f"تم حفظ العميل '{cust_name}' بنجاح!")
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

    # --- تبويب 3: شبكة المواد مع التحكم والتعديل الحقيقي ---
    with tab3:
        st.subheader("شبكة المواد (إدارة وتعديل مباشر)")
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        if items:
            cols = st.columns(3)
            for index, item in enumerate(items):
                item_id, name, quantity, price = item
                target_col = cols[index % 3]
                with target_col:
                    with st.container(border=True):
                        st.markdown(f"### 📦 {name}")
                        st.metric("الكمية المتاحة", quantity)
                        st.metric("السعر", f"{price:,.0f} د.ع")
                        st.write(f"**القيمة الكلية**: {(quantity * price):,.0f} د.ع")
                        
                        if st.button("تعديل / حذف", key=f"edit_btn_{item_id}"):
                            st.session_state[f"editing_{item_id}"] = True
                            
                        if st.session_state.get(f"editing_{item_id}", False):
                            new_qty_val = st.number_input("الكمية الجديدة", value=int(quantity), key=f"new_q_{item_id}")
                            new_price_val = st.number_input("السعر الجديد", value=float(price), key=f"new_p_{item_id}")
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("حفظ التعديل", key=f"save_{item_id}"):
                                    run_query("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (new_qty_val, new_price_val, item_id))
                                    st.session_state[f"editing_{item_id}"] = False
                                    st.rerun()
                            with col_btn2:
                                if st.button("حذف نهائي ❌", key=f"del_{item_id}"):
                                    run_query("DELETE FROM inventory WHERE id = ?", (item_id,))
                                    st.session_state[f"editing_{item_id}"] = False
                                    st.rerun()
        else:
            st.info("المخزن فارغ حالياً.")

    # --- تبويب 4: التقارير المالية (شكل الستوري + الأرقام الحقيقية) ---
    with tab4:
        st.subheader("📊 تقارير الأرباح والمبيعات")
        if not st.session_state.is_unlocked:
            st.warning("🔒 **تقارير الأرباح المتقدمة وتصدير ملفات Excel مقفلة في النسخة التجريبية**")
            st.info("أدخل رمز التفعيل (2009) في القائمة الجانبية لفتح التقارير الكاملة وحسابصافي الربح التلقائي.")
        
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        if items:
            total_unique = len(items)
            total_quantity = sum([it[2] for it in items])
            total_capital = sum([it[2] * it[3] for it in items])
            
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("إجمالي المواد المختلفة", total_unique)
            col_r2.metric("إجمالي الكمية بالمخزن", total_quantity)
            col_r3.metric("إجمالي قيمة المخزن", f"{total_capital:,.0f} د.ع")
            
            st.divider()
            st.subheader("الرسم البياني لقيم المواد")
            chart_data = {it[1]: it[2] * it[3] for it in items}
            st.bar_chart(chart_data)
        else:
            st.info("لا توجد بيانات كافية لعرض التقارير.")

    # --- تبويب 5: الفواتير وقص المواد ---
    with tab5:
        st.subheader("🧾 مولد الفواتير وقص المواد تلقائياً من المخزن")
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        if items:
            item_names = [it[1] for it in items]
            selected_inv_item = st.selectbox("اختر المادة للبيع (لقصها من المخزن)", item_names)
            
            curr_item_data = run_query("SELECT quantity, price FROM inventory WHERE name = ?", (selected_inv_item,), fetch=True)
            available_qty = curr_item_data[0][0] if curr_item_data else 0
            item_price = curr_item_data[0][1] if curr_item_data else 0.0
            
            st.info(f"الكمية المتاحة حالياً في المخزن: **{available_qty}**")
            inv_qty = st.number_input("الكمية المباعة (المراد قصها)", min_value=1, max_value=max(1, available_qty), step=1)
            
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
الكمية المقصوصة: {inv_qty}
سعر المفرد: {item_price:,.0f} د.ع
-------------------------------------
إجمالي المبلغ: {total_amount:,.0f} د.ع
المتبقي بالمخزن: {new_qty}
=====================================
تابع الحساب اسهل الطرق لإداره محلك
"""
                    st.success(f"تم إصدار الفاتورة وقص **{inv_qty}** من مادة '{selected_inv_item}' بنجاح!")
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
