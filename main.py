import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="إدارة المبيعات", page_icon="🛍️", layout="wide")

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=20)
    c = conn.cursor()
    # جداول النظام
    tables = {
        "products": "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, price REAL DEFAULT 0, quantity INTEGER DEFAULT 0",
        "customers": "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, shop_location TEXT, phone TEXT, governorate TEXT, region TEXT, debt REAL DEFAULT 0",
        "invoices": "id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, shop_location TEXT, phone TEXT, governorate TEXT, region TEXT, total REAL, date TEXT",
        "users": "id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT"
    }
    
    for table, schema in tables.items():
        c.execute(f"CREATE TABLE IF NOT EXISTS {table} ({schema})")
    
    # تأكد من وجود الأعمدة (علاج لمشكلة OperationalError)
    try:
        c.execute("ALTER TABLE customers ADD COLUMN debt REAL DEFAULT 0")
    except: pass
    
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=20)
    c = conn.cursor()
    try:
        c.execute(query, params)
        data = c.fetchall() if fetch else None
        conn.commit()
        return data
    except Exception as e:
        st.error(f"خطأ في قاعدة البيانات: {e}")
        return None
    finally:
        conn.close()

# --- واجهة تسجيل الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 بوابة الدخول للنظام</h2>", unsafe_allow_html=True)
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "admin" and pw == "123": # يمكنك تغييرها لقاعدة البيانات لاحقاً
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("خطأ في البيانات")
    st.stop()

# --- المساعد الذكي المطور f30060 ---
st.sidebar.markdown("### 🤖 المساعد الذكي f30060")
with st.sidebar.expander("لوحة التحكم"):
    cmd = st.text_area("أوامر المساعد:", placeholder="مثال للإضافة: اسم المنتج,5,2500\nمثال للجرد: جرد")
    if st.button("تنفيذ 🚀"):
        if cmd.strip() == "جرد":
            res = run_query("SELECT name, quantity, price FROM products", fetch=True)
            if res:
                report = "📦 تقرير المخزن:\n" + "\n".join([f"{r[0]}: {r[1]} قطعة ({r[2]} د)" for r in res])
                st.info(report)
            else:
                st.warning("المخزن فارغ!")
        elif "," in cmd:
            try:
                parts = cmd.split(',')
                name, qty, price = parts[0].strip(), int(parts[1].strip()), float(parts[2].strip())
                # التحقق من وجود المنتج
                check = run_query("SELECT id FROM products WHERE name = ?", (name,), fetch=True)
                if check:
                    run_query("UPDATE products SET quantity = quantity + ?, price = ? WHERE name = ?", (qty, price, name))
                    st.success(f"تم تحديث {name} بنجاح!")
                else:
                    run_query("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
                    st.success(f"تمت إضافة {name} كمادة جديدة!")
            except Exception as e:
                st.error(f"خطأ في الصيغة! اكتبها بالشكل الصحيح: (اسم,عدد,سعر). الخطأ: {e}")

# --- القوائم الرئيسية ---
menu = st.sidebar.radio("القائمة", ["🏪 المبيعات", "📦 المخزن", "👥 العملاء"])

if menu == "🏪 المبيعات":
    if 'cart' not in st.session_state: st.session_state.cart = []
    # هنا كود المبيعات ...
    st.write("شاشة البيع")
    
elif menu == "📦 المخزن":
    st.title("📦 المخزن")
    df = pd.DataFrame(run_query("SELECT * FROM products", fetch=True), columns=["ID", "الاسم", "السعر", "العدد"])
    st.dataframe(df)

elif menu == "👥 العملاء":
    st.title("👥 العملاء")
    # هنا كود العملاء ...
