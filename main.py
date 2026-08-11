import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse
import re

# إعداد الصفحة
st.set_page_config(
    page_title="نظام ياسر الذكي", 
    page_icon="🛍️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- التنسيقات ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    div.stButton > button { background-color: #1a6b51; color: white; border-radius: 8px; border: none; height: 45px; font-weight: bold; }
    div.stButton > button:hover { background-color: #14523e; }
</style>
""", unsafe_allow_html=True)

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, price REAL DEFAULT 0, quantity INTEGER DEFAULT 0, category TEXT DEFAULT 'عام')''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, shop_location TEXT, phone TEXT, governorate TEXT, region TEXT, debt REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, shop_location TEXT, phone TEXT, governorate TEXT, region TEXT, subtotal REAL, discount REAL DEFAULT 0, delivery REAL DEFAULT 0, total REAL, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- تسجيل الدخول (تبسيط) ---
if not st.session_state.logged_in:
    st.subheader("🔐 بوابة الدخول")
    login_user = st.text_input("اسم المستخدم")
    login_pass = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        st.session_state.logged_in = True
        st.session_state.username = login_user
        st.rerun()
    st.stop()

# --- القائمة الرئيسية ---
menu = st.radio("🧭 القائمة الرئيسية:", ["🏪 المبيعات", "📦 المخزون", "🤖 المساعد الذكي والتقارير", "👥 العملاء"], horizontal=True)

# --- 1. المبيعات ---
if menu == "🏪 المبيعات":
    st.subheader("شاشة البيع")
    products = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
    search = st.text_input("🔍 بحث عن منتج...")
    
    if products:
        for prod in products:
            if search.lower() in prod[1].lower():
                c1, c2, c3 = st.columns(3)
                c1.write(f"**{prod[1]}**")
                c2.write(f"السعر: {prod[2]}")
                if c3.button("إضافة للسلة", key=f"add_{prod[0]}"):
                    st.session_state.cart[prod[0]] = {'name': prod[1], 'price': prod[2], 'qty': 1}
                    st.rerun()

# --- 2. المخزون ---
elif menu == "📦 المخزون":
    st.subheader("📦 إدارة المخزون")
    with st.form("add_p"):
        p_name = st.text_input("اسم المنتج")
        p_price = st.number_input("السعر")
        p_qty = st.number_input("الكمية", step=1)
        if st.form_submit_button("إضافة"):
            run_query("INSERT OR REPLACE INTO products (name, price, quantity) VALUES (?, ?, ?)", (p_name, p_price, p_qty))
            st.success("تم!")

# --- 3. المساعد الذكي (هنا التعديل اللي تريده) ---
elif menu == "🤖 المساعد الذكي والتقارير":
    st.subheader("🤖 المساعد الذكي")
    user_ai_query = st.text_input("💬 اسألني أو أمرني (مثلاً: ضيف شاحن بسعر 5000 وعدد 10)")
    
    if user_ai_query:
        q_lower = user_ai_query.lower()
        
        # التعديل الذكي هنا:
        if "ضيف" in q_lower or "أضف" in q_lower:
            try:
                price_match = re.search(r"(?:سعر|بسعر)\s*(\d+(?:\.\d+)?)", q_lower)
                qty_match = re.search(r"(?:عدد|كمية)\s*(\d+)", q_lower)
                
                if price_match and qty_match:
                    p_price = float(price_match.group(1))
                    p_qty = int(qty_match.group(1))
                    
                    # استخراج الاسم بمرونة
                    name_match = re.search(r"(?:ضيف|أضف)\s+(.*?)\s+(?:بسعر|سعر)", q_lower)
                    if name_match:
                        p_name = name_match.group(1).replace("منتج", "").strip().title()
                        
                        exists = run_query("SELECT quantity FROM products WHERE name = ?", (p_name,), fetch=True)
                        if exists:
                            run_query("UPDATE products SET quantity = quantity + ?, price = ? WHERE name = ?", (p_qty, p_price, p_name))
                            msg = f"تم تحديث **{p_name}** بنجاح."
                        else:
                            run_query("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (p_name, p_qty, p_price))
                            msg = f"تمت إضافة **{p_name}** بنجاح."
                        st.success(f"🤖 {msg}")
                    else:
                        st.warning("لم أفهم اسم المنتج. اكتب: ضيف [الاسم] بسعر [السعر] وعدد [العدد]")
                else:
                    st.warning("يرجى تحديد السعر والعدد.")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

# --- 4. العملاء ---
elif menu == "👥 العملاء":
    st.subheader("👥 العملاء")
    # (باقي كود العملاء...)
