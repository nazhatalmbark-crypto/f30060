import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="Prosto - إدارة المبيعات", page_icon="🛍️", layout="wide")

# --- تنسيق الألوان (CSS) ليطابق التطبيق ---
st.markdown("""
<style>
    /* لون الأزرار الأخضر */
    div.stButton > button {
        background-color: #1a6b51;
        color: white;
        border-radius: 8px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #14523e;
    }
    /* تنسيق التبويبات الفوق */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e6f2ee;
        border-radius: 8px;
        color: #1a6b51;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# العبارة المطلوبة
st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>« أسعد نفسك بنفسك - مستمرون نحو الأفضل »</h2>", unsafe_allow_html=True)

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    price REAL DEFAULT 0,
                    quantity INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT,
                    total REAL,
                    date TEXT)''')
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute(query, params)
    data = None
    if fetch: data = c.fetchall()
    conn.commit()
    conn.close()
    return data

# --- المساعد الذكي f30060 (في القائمة الجانبية) ---
st.sidebar.markdown("### 🤖 المساعد الذكي f30060")
with st.sidebar.expander("إضافة أو استعلام سريع"):
    st.write("أضف منتجات (الاسم, العدد, السعر)")
    user_ai = st.text_area("أمر المساعد:", height=100)
    if st.button("تنفيذ عبر f30060 🚀"):
        if "," in user_ai: # إضافة
            lines = user_ai.split('\n')
            for line in lines:
                if "," in line:
                    parts = line.split(',')
                    if len(parts) == 3:
                        name, qty, price = parts[0].strip(), int(parts[1].strip()), float(parts[2].strip())
                        run_query("INSERT OR REPLACE INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
            st.success("تم التحديث!")
        elif "جرد" in user_ai:
            p_res = run_query("SELECT name, quantity, price FROM products", fetch=True)
            for pr in p_res: st.write(f"{pr[0]}: {pr[1]} قطعة | {pr[2]} دينار")

# القائمة الرئيسية (التنقل)
menu = st.sidebar.radio("القائمة", ["🏪 المبيعات", "🛒 المشتريات", "📦 المخازن", "📊 التقارير", "💰 المالية"])

# --- واجهة المبيعات ---
if menu == "🏪 المبيعات":
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    # تبويبات الصورة
    tab1, tab2, tab3, tab4 = st.tabs(["شاشة البيع", "الفواتير", "العملاء", "مرتجعات الفواتير"])
    
    with tab1:
        search = st.text_input("🔍 ابحث باسم أو باركود ...")
        products = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
        
        # عرض المنتجات ككارتات
        cols = st.columns(2)
        for i, prod in enumerate(products):
            if search.lower() in prod[1].lower():
                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {prod[1]}")
                        st.write(f"💰 {prod[2]} دينار &nbsp; | &nbsp; 📦 {prod[3]} قطعة")
                        if st.button(f"إضافة {prod[1]}", key=f"add_{prod[0]}"):
                            st.session_state.cart.append({'id': prod[0], 'name': prod[1], 'price': prod[2]})
                            st.rerun()

    # السلة (تظهر في كل الشاشات)
    with st.sidebar.expander("🛒 السلة"):
        total = sum(i['price'] for i in st.session_state.cart)
        for idx, item in enumerate(st.session_state.cart):
            st.write(f"{item['name']} - {item['price']} دينار")
        st.write(f"### المجموع: {total} دينار")
        if st.button("تأكيد البيع"):
            st.session_state.cart = []
            st.success("تمت العملية!")
            st.rerun()

elif menu == "📦 المخازن":
    st.title("📦 إدارة المخازن")
    st.dataframe(pd.DataFrame(run_query("SELECT * FROM products", fetch=True), columns=["ID", "الاسم", "السعر", "العدد"]))

# بقية الأقسام فارغة حالياً للتوسعة
else:
    st.title(menu)
    st.info("هذا القسم قيد التجهيز.")
