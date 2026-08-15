import streamlit as st
import sqlite3
from datetime import date

st.set_page_config(page_title="Yasser Web - Pro Inventory", layout="wide")

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, shop_location TEXT, governorate TEXT, landmark TEXT)''')
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

# --- الحالة ---
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False

# --- واجهة القفل (Sidebar) ---
st.sidebar.title("🔐 التحكم بالمخزن")
if not st.session_state.is_unlocked:
    code = st.sidebar.text_input("رمز التفعيل (نسخة مدفوعة):", type="password")
    if st.sidebar.button("تفعيل"):
        if code == "2009": 
            st.session_state.is_unlocked = True
            st.rerun()
        else: st.sidebar.error("رمز خطأ")
else:
    st.sidebar.success("✅ النسخة المدفوعة مفعلة")
    if st.sidebar.button("إيقاف التفعيل"): 
        st.session_state.is_unlocked = False
        st.rerun()

# --- التبويبات ---
tab1, tab2, tab3, tab4 = st.tabs(["➕ إضافة مادة", "👥 إضافة عميل", "📦 شبكة المواد (تحكم)", "🧾 فواتير"])

# --- تبويب 1: إضافة مادة ---
with tab1:
    st.header("إضافة مادة جديدة")
    with st.form("add_item"):
        n = st.text_input("اسم المادة")
        q = st.number_input("الكمية", min_value=1)
        p = st.number_input("السعر (د.ع)", min_value=0.0)
        if st.form_submit_button("حفظ"):
            # التحقق من النسخة المجانية
            if not st.session_state.is_unlocked and q > 100:
                st.error("أنت تستخدم النسخة المجانية! الحد الأقصى 100 كارتون/مادة.")
            else:
                try:
                    run_query("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (n, q, p))
                    st.success("تم إضافة المادة")
                except:
                    st.warning("المادة موجودة مسبقاً، استخدم التعديل من تبويب شبكة المواد.")

# --- تبويب 2: إضافة عميل ---
with tab2:
    st.header("إضافة عميل")
    with st.form("add_cust"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("اسم العميل")
            phone = st.text_input("الهاتف")
        with c2:
            loc = st.text_input("مكان المحل")
            gov = st.text_input("المحافظة")
        land = st.text_input("أقرب نقطة دالة")
        if st.form_submit_button("حفظ العميل"):
            run_query("INSERT INTO customers (name, phone, shop_location, governorate, landmark) VALUES (?, ?, ?, ?, ?)", (name, phone, loc, gov, land))
            st.success("تم حفظ العميل")

# --- تبويب 3: شبكة المواد (مع التعديل والحذف) ---
with tab3:
    st.header("شبكة المواد (إدارة كاملة)")
    items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
    if items:
        cols = st.columns(3)
        for i, it in enumerate(items):
            id, name, q, p = it
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(f"📦 {name}")
                    st.metric("الكمية", q)
                    st.metric("السعر", f"{p:,.0f} د.ع")
                    
                    # أزرار التعديل والحذف
                    if st.button("تعديل/حذف", key=f"edit_{id}"):
                        st.session_state[f"editing_{id}"] = True
                    
                    if st.session_state.get(f"editing_{id}"):
                        new_q = st.number_input("الكمية الجديدة", value=q, key=f"q_{id}")
                        new_p = st.number_input("السعر الجديد", value=p, key=f"p_{id}")
                        if st.button("حفظ التعديل", key=f"save_{id}"):
                            run_query("UPDATE inventory SET quantity=?, price=? WHERE id=?", (new_q, new_p, id))
                            st.session_state[f"editing_{id}"] = False
                            st.rerun()
                        if st.button("حذف المادة نهائياً ❌", key=f"del_{id}"):
                            run_query("DELETE FROM inventory WHERE id=?", (id,))
                            st.rerun()
    else:
        st.info("لا توجد مواد.")

# --- تبويب 4: فواتير ---
with tab4:
    st.header("الفواتير")
    items = run_query("SELECT name, price FROM inventory", fetch=True)
    if items:
        sel = st.selectbox("المادة", [it[0] for it in items])
        q = st.number_input("الكمية", min_value=1)
        if st.button("إصدار"):
            price = [it[1] for it in items if it[0] == sel][0]
            st.write(f"الإجمالي: {(q * price):,.0f} د.ع")
