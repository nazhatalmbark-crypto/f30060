import streamlit as st
import sqlite3
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Inventory System", layout="wide")

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price REAL DEFAULT 0, is_locked INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, phone TEXT, notes TEXT)''')
    
    try: c.execute("ALTER TABLE inventory ADD COLUMN price REAL DEFAULT 0;")
    except sqlite3.OperationalError: pass
    
    try: c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
    except sqlite3.IntegrityError: pass
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

# --- 2. تهيئة الحالة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- 3. تسجيل الدخول ---
if not st.session_state.logged_in:
    st.subheader("🔐 تسجيل الدخول")
    with st.form("login"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            user = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (u, p), fetch=True)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else: st.error("خطأ في المعلومات")
else:
    # القائمة الجانبية (للقفل فقط)
    st.sidebar.title("إعدادات النظام")
    if not st.session_state.is_unlocked:
        code = st.sidebar.text_input("رمز فتح القفل (2009)", type="password")
        if st.sidebar.button("تفعيل الميزات"):
            if code == "2009": st.session_state.is_unlocked = True; st.rerun()
            else: st.sidebar.error("رمز خطأ")
    else:
        st.sidebar.success("ميزات القفل مفعلة ✅")
        if st.sidebar.button("إيقاف التفعيل"): st.session_state.is_unlocked = False; st.rerun()
    
    if st.sidebar.button("تسجيل خروج"): st.session_state.logged_in = False; st.rerun()

    # --- التبويبات (هنا الفصل التام) ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ إضافة مادة", 
        "👥 إضافة عميل", 
        "📦 المخزون (شبكة)", 
        "📊 التقارير والأرباح", 
        "🧾 الفواتير"
    ])

    # --- تبويب 1: إضافة المواد ---
    with tab1:
        st.header("إضافة مادة جديدة")
        with st.form("add_item"):
            n = st.text_input("اسم المادة")
            q = st.number_input("الكمية", min_value=1)
            p = st.number_input("السعر (د.ع)", min_value=0.0)
            if st.form_submit_button("حفظ المادة"):
                run_query("INSERT OR IGNORE INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (n, q, p))
                st.success("تم الحفظ")

    # --- تبويب 2: إضافة العملاء ---
    with tab2:
        st.header("إضافة عميل جديد")
        with st.form("add_cust"):
            cn = st.text_input("اسم العميل")
            cp = st.text_input("رقم الهاتف")
            if st.form_submit_button("حفظ العميل"):
                run_query("INSERT INTO customers (name, phone) VALUES (?, ?)", (cn, cp))
                st.success("تم حفظ العميل")

    # --- تبويب 3: شبكة المخزون ---
    with tab3:
        st.header("شبكة المواد")
        items = run_query("SELECT id, name, quantity, price, is_locked FROM inventory", fetch=True)
        if items:
            cols = st.columns(3)
            for i, it in enumerate(items):
                id, name, q, p, lock = it
                with cols[i % 3]:
                    with st.container(border=True):
                        st.subheader(name)
                        st.write(f"الكمية: {q}")
                        st.write(f"السعر: {p:,.0f} د.ع")
                        if st.session_state.is_unlocked:
                            btn = "فتح القفل" if lock else "قفل المادة"
                            if st.button(btn, key=f"lock_{id}"):
                                run_query("UPDATE inventory SET is_locked = ? WHERE id = ?", (0 if lock else 1, id))
                                st.rerun()
                        elif lock: st.write("🔒 مقفلة")

    # --- تبويب 4: التقارير ---
    with tab4:
        st.header("التقارير المالية")
        items = run_query("SELECT name, quantity, price FROM inventory", fetch=True)
        if items:
            total = sum([it[1] * it[2] for it in items])
            st.metric("إجمالي قيمة المخزن", f"{total:,.0f} د.ع")
            st.bar_chart({it[0]: it[1] * it[2] for it in items})

    # --- تبويب 5: الفواتير ---
    with tab5:
        st.header("إصدار فاتورة")
        items = run_query("SELECT name, price FROM inventory", fetch=True)
        if items:
            sel = st.selectbox("اختر المادة", [it[0] for it in items])
            qty = st.number_input("الكمية المباعة", min_value=1)
            if st.button("توليد الفاتورة"):
                price = [it[1] for it in items if it[0] == sel][0]
                st.text(f"الإجمالي: {(qty * price):,.0f} د.ع")
