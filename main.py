import streamlit as st
import sqlite3

# --- إعدادات الصفحة ---
st.set_page_config(page_title="ياسر ويب - النسخة الاحترافية", layout="wide")

# --- تهيئة البيانات ---
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False
if 'cart' not in st.session_state: st.session_state.cart = []

def init_db():
    conn = sqlite3.connect('yasser_web.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity INTEGER, price INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- واجهة التفعيل (SideBar) ---
st.sidebar.title("🔐 لوحة التحكم")
if not st.session_state.is_unlocked:
    st.sidebar.warning("أنت تستخدم النسخة المجانية")
    code = st.sidebar.text_input("أدخل كود التفعيل لفتح النسخة الكاملة:", type="password")
    if st.sidebar.button("تفعيل الآن"):
        if code == "2009": # هذا هو الكود السري
            st.session_state.is_unlocked = True
            st.sidebar.success("تم التفعيل بنجاح! مبروك النسخة الكاملة.")
            st.rerun()
        else:
            st.sidebar.error("كود غير صحيح!")
else:
    st.sidebar.success("✅ النسخة الكاملة مفعلة (أنت المدير)")

# --- العداد الفوق (العربانة) ---
col_head1, col_head2 = st.columns([4, 1])
col_head1.title("📦 مخزن ياسر ويب")
col_head2.metric("السلة 🛒", len(st.session_state.cart))

# --- تبويب الشبكة (الكارتات) ---
st.subheader("اختر المواد للبيع:")
items = sqlite3.connect('yasser_web.db').cursor().execute("SELECT id, name, quantity, price FROM inventory").fetchall()

if items:
    # تقسيم المواد على شكل شبكة (Grid)
    cols = st.columns(3)
    for i, item in enumerate(items):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {item[1]}")
                st.write(f"السعر: {item[3]:,} د.ع")
                st.write(f"المتوفر: {item[2]}")
                
                # زر الإضافة (اللي يسوي الصوت والعداد)
                if st.button(f"إضافة للسلة ➕", key=f"add_{item[0]}"):
                    st.session_state.cart.append(item)
                    st.toast(f"تم إضافة {item[1]} للسلة!", icon="✅")
                    st.rerun() # تحديث الصفحة عشان العداد يتغير فوراً
else:
    st.info("لا توجد مواد في المخزن.")

# --- قسم السلة (إتمام البيع) ---
st.divider()
st.subheader("🛒 محتويات السلة")

if st.session_state.cart:
    total_price = 0
    for idx, cart_item in enumerate(st.session_state.cart):
        st.write(f"{idx+1}. {cart_item[1]} - {cart_item[3]:,} د.ع")
        total_price += cart_item[3]
    
    st.markdown(f"### الإجمالي: `{total_price:,} د.ع`")
    
    if st.button("✅ إتمام البيع وخصم المواد من المخزن"):
        conn = sqlite3.connect('yasser_web.db')
        c = conn.cursor()
        for cart_item in st.session_state.cart:
            # خصم الكمية من قاعدة البيانات
            c.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (cart_item[0],))
        conn.commit()
        conn.close()
        
        st.session_state.cart = [] # تصفير السلة
        st.success("تم خصم المواد بنجاح!")
        st.rerun()
else:
    st.write("السلة فارغة.")

# --- إضافة مادة (ميزة للمدير فقط) ---
if st.session_state.is_unlocked:
    st.divider()
    st.subheader("⚙️ إضافة مادة جديدة (للمدير)")
    with st.form("add_new"):
        name = st.text_input("اسم المادة")
        qty = st.number_input("الكمية", value=10)
        price = st.number_input("السعر", value=1000)
        if st.form_submit_button("إضافة للمخزن"):
            conn = sqlite3.connect('yasser_web.db')
            c = conn.cursor()
            c.execute("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
            conn.commit()
            conn.close()
            st.rerun()
