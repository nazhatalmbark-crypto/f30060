import streamlit as st
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Inventory System", layout="wide")

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    # جدول المواد
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price REAL DEFAULT 0, is_locked INTEGER DEFAULT 0)''')
    # جدول العملاء مع الخانات الجديدة
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    phone TEXT, 
                    shop_location TEXT, 
                    governorate TEXT, 
                    landmark TEXT)''')
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

# --- 2. التحكم بالقفل (2009) ---
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- 3. التبويبات (فصل تام) ---
tab1, tab2, tab3 = st.tabs(["➕ إضافة مادة (شبكة)", "👥 إضافة عميل (كامل)", "📦 عرض المواد"])

# --- تبويب 1: إضافة مادة ---
with tab1:
    st.header("إضافة مادة جديدة للمخزن")
    with st.form("add_item"):
        n = st.text_input("اسم المادة")
        q = st.number_input("الكمية", min_value=1)
        p = st.number_input("السعر (د.ع)", min_value=0.0)
        if st.form_submit_button("حفظ المادة"):
            run_query("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (n, q, p))
            st.success("تم الحفظ")

# --- تبويب 2: إضافة عميل (بالتفاصيل الكاملة) ---
with tab2:
    st.header("إضافة عميل جديد")
    with st.form("add_cust"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الهاتف")
            gov = st.text_input("المحافظة")
        with c2:
            loc = st.text_input("مكان المحل")
            land = st.text_input("أقرب نقطة دالة")
        
        if st.form_submit_button("حفظ بيانات العميل"):
            run_query("INSERT INTO customers (name, phone, shop_location, governorate, landmark) VALUES (?, ?, ?, ?, ?)", 
                      (name, phone, loc, gov, land))
            st.success("تم حفظ بيانات العميل بالكامل")

    st.divider()
    st.subheader("العملاء المسجلين")
    custs = run_query("SELECT * FROM customers", fetch=True)
    for c in custs:
        st.write(f"👤 {c[1]} | 📱 {c[2]} | 📍 {c[3]} | 🏛️ {c[4]} | 🚩 {c[5]}")

# --- تبويب 3: عرض المواد (على شكل شبكة) ---
with tab3:
    st.header("عرض المواد (نظام الشبكة)")
    
    # القفل
    code = st.text_input("أدخل رمز القفل (2009) للتحكم", type="password")
    if code == "2009": st.session_state.is_unlocked = True
    
    items = run_query("SELECT id, name, quantity, price, is_locked FROM inventory", fetch=True)
    if items:
        # عرض الشبكة
        cols = st.columns(3) # 3 أعمدة للشبكة
        for i, it in enumerate(items):
            id, name, q, p, lock = it
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(f"📦 {name}")
                    st.write(f"الكمية: {q}")
                    st.write(f"السعر: {p:,.0f} د.ع")
                    
                    if st.session_state.is_unlocked:
                        btn = "🔓 فتح" if lock else "🔒 قفل"
                        if st.button(btn, key=f"lock_{id}"):
                            run_query("UPDATE inventory SET is_locked = ? WHERE id = ?", (0 if lock else 1, id))
                            st.rerun()
                    elif lock:
                        st.write("🔒 مقفلة")
    else:
        st.info("لا توجد مواد.")
