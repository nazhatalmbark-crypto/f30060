import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="Prosto - إدارة المبيعات", page_icon="🛍️", layout="wide")

# --- تنسيق الألوان (CSS) ---
st.markdown("""
<style>
    div.stButton > button { background-color: #1a6b51; color: white; border-radius: 8px; border: none; }
    div.stButton > button:hover { background-color: #14523e; }
    .stTabs [data-baseweb="tab"] { background-color: #e6f2ee; border-radius: 8px; color: #1a6b51; font-weight: bold; }
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

# --- المساعد الذكي f30060 (المحدث) ---
st.sidebar.markdown("### 🤖 المساعد الذكي f30060")
with st.sidebar.expander("لوحة تحكم f30060"):
    user_ai = st.text_area("الأمر (إضافة أو جرد):", help="للإضافة اكتب: اسم,عدد,سعر. للجرد اكتب: جرد")
    
    if st.button("تنفيذ 🚀"):
        # 1. عملية الجرد
        if "جرد" in user_ai:
            p_res = run_query("SELECT name, quantity, price FROM products", fetch=True)
            report = f"📋 تقرير الجرد الكامل\nالتاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n--------------------------\n"
            if p_res:
                for pr in p_res:
                    report += f"🔹 {pr[0]}: {pr[1]} قطعة | بسعر {pr[2]}\n"
            else:
                report += "المخزن فارغ حالياً."
            st.text_area("التقرير:", value=report, height=200)

        # 2. عملية الإضافة (الذكية)
        elif "," in user_ai:
            lines = user_ai.split('\n')
            for line in lines:
                if "," in line:
                    parts = line.split(',')
                    if len(parts) == 3:
                        name, qty, price = parts[0].strip(), int(parts[1].strip()), float(parts[2].strip())
                        
                        # تحقق هل المنتج موجود؟
                        exists = run_query("SELECT quantity FROM products WHERE name = ?", (name,), fetch=True)
                        if exists:
                            # تحديث (جمع الكمية)
                            new_qty = exists[0][0] + qty
                            run_query("UPDATE products SET quantity = ?, price = ? WHERE name = ?", (new_qty, price, name))
                            st.success(f"تم تحديث {name} (+{qty})")
                        else:
                            # إضافة جديد
                            run_query("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
                            st.success(f"تمت إضافة {name} للمخزن!")

# القائمة الرئيسية
menu = st.sidebar.radio("القائمة", ["🏪 المبيعات", "📦 المخازن"])

# --- واجهة المبيعات ---
if menu == "🏪 المبيعات":
    if 'cart' not in st.session_state: st.session_state.cart = []
    tab1, tab2, tab3, tab4 = st.tabs(["شاشة البيع", "الفواتير", "العملاء", "مرتجعات الفواتير"])
    
    with tab1:
        products = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
        cols = st.columns(2)
        for i, prod in enumerate(products):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{prod[1]}**")
                    st.write(f"💰 {prod[2]} د | 📦 {prod[3]} قطعه")
                    if st.button(f"إضافة {prod[1]}", key=f"add_{prod[0]}"):
                        st.session_state.cart.append({'id': prod[0], 'name': prod[1], 'price': prod[2]})
                        st.rerun()

    # السلة في القائمة الجانبية
    with st.sidebar.expander("🛒 السلة"):
        total = sum(i['price'] for i in st.session_state.cart)
        for idx, item in enumerate(st.session_state.cart):
            st.write(f"{item['name']} - {item['price']} د")
        st.write(f"### المجموع: {total} دينار")
        if st.button("تأكيد البيع"):
            st.session_state.cart = []
            st.rerun()

elif menu == "📦 المخازن":
    st.title("📦 إدارة المخازن")
    st.dataframe(pd.DataFrame(run_query("SELECT * FROM products", fetch=True), columns=["ID", "الاسم", "السعر", "العدد"]))
