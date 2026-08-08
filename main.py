import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(page_title="Eng. Yasser Pro System", page_icon="🛒", layout="wide")

# عرض العبارة الخاصة بك في أعلى الواجهة
st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>« أسعد نفسك بنفسك - مستمرون نحو الأفضل »</h2>", unsafe_allow_html=True)
st.divider()

# إنشاء وتجهيز قاعدة البيانات
def init_db():
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    # جدول المنتجات
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    barcode TEXT,
                    price REAL DEFAULT 0,
                    cost REAL DEFAULT 0,
                    quantity INTEGER DEFAULT 0)''')
    # جدول العملاء والديون
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    debt REAL DEFAULT 0)''')
    # جدول الفواتير
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT,
                    total REAL,
                    profit REAL,
                    date TEXT)''')
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute(query, params)
    data = None
    if fetch:
        data = c.fetchall()
    conn.commit()
    conn.close()
    return data

# القائمة الجانبية
st.sidebar.title("🚀 Eng. Yasser Pro")
menu = st.sidebar.selectbox("القائمة الرئيسية", ["🛒 نقطة البيع (السلة)", "📦 إدارة المخزون", "📊 التقارير والأرباح", "👥 العملاء والديون"])

# --- المساعد الذكي المصغر ---
st.sidebar.markdown("---")
with st.sidebar.expander("🤖 مساعدي الذكي السريع"):
    task = st.radio("اختر العملية:", ["استعلام (ديون/جرد)", "إضافة مخزون (جملة)"])
    
    if task == "استعلام (ديون/جرد)":
        query_text = st.text_input("اكتب اسم العميل للديون أو كلمة 'جرد':")
        if query_text:
            if "جرد" in query_text:
                p_res = run_query("SELECT name, quantity FROM products", fetch=True)
                st.write("📦 **جرد المخزون:**")
                for pr in p_res:
                    st.write(f"- {pr[0]}: {pr[1]}")
            else:
                cust_res = run_query("SELECT name, debt FROM customers WHERE name LIKE ?", (f"%{query_text}%",), fetch=True)
                for cr in cust_res:
                    st.success(f"العميل: {cr[0]} | الدين: {cr[1]} د.ع")
    
    else: # إضافة مخزون بالجملة
        st.write("اكتب (اسم المنتج, العدد) كل واحد بسطر:")
        batch_input = st.text_area("مثال:\nبيبسي, 50\nحليب, 20")
        if st.button("إضافة للمخزن"):
            lines = batch_input.split('\n')
            for line in lines:
                if "," in line:
                    p_name, p_qty = line.split(',')
                    p_name = p_name.strip()
                    try:
                        p_qty = int(p_qty.strip())
                        # تحديث أو إضافة
                        exists = run_query("SELECT quantity FROM products WHERE name = ?", (p_name,), fetch=True)
                        if exists:
                            new_q = exists[0][0] + p_qty
                            run_query("UPDATE products SET quantity = ? WHERE name = ?", (new_q, p_name))
                        else:
                            run_query("INSERT INTO products (name, quantity, price, cost) VALUES (?, ?, 0, 0)", (p_name, p_qty))
                    except:
                        st.error(f"خطأ في تنسيق السطر: {line}")
            st.success("تمت الإضافة بنجاح!")

# ---------------- 1. نقطة البيع (السلة) ----------------
if menu == "🛒 نقطة البيع (السلة)":
    st.header("🛒 نقطة البيع")
    products = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
    if not products:
        st.warning("المخزون فارغ!")
    else:
        if 'cart' not in st.session_state: st.session_state.cart = []
        
        # اختيار المنتجات
        with st.expander("اضغط هنا لاختيار المنتجات للسلة"):
            for prod in products:
                p_id, name, price, qty = prod
                cols = st.columns([2, 1, 1])
                cols[0].write(f"{name} (المتوفر: {qty})")
                add_q = cols[1].number_input("العدد", 1, qty, 1, key=f"q_{p_id}")
                if cols[2].button("إضافة", key=f"add_{p_id}"):
                    st.session_state.cart.append({'id': p_id, 'name': name, 'price': price, 'qty': add_q})
                    st.rerun()

        # عرض السلة
        st.subheader("🛍️ السلة")
        total = 0
        for i, item in enumerate(st.session_state.cart):
            st.write(f"{item['name']} - {item['qty']} عدد")
            total += (item['price'] * item['qty'])
        
        st.write(f"### المجموع: {total} د.ع")
        cust_name = st.text_input("اسم العميل")
        if st.button("تثبيت الفاتورة"):
            if cust_name:
                for item in st.session_state.cart:
                    # خصم الكمية
                    run_query("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['qty'], item['id']))
                run_query("INSERT INTO invoices (customer_name, total, date) VALUES (?, ?, ?)", (cust_name, total, datetime.now().strftime("%Y-%m-%d")))
                st.session_state.cart = []
                st.success("تم الحفظ!")
            else:
                st.error("أدخل اسم العميل")

# ---------------- 2. إدارة المخزون ----------------
elif menu == "📦 إدارة المخزون":
    st.header("📦 إدارة المخزون")
    # (هذا القسم نفس المنطق السابق، تركت لك الحرية هنا للتركيز على المساعد)
    st.info("استخدم المساعد الجانبي لإضافة المنتجات بسرعة أو قسم إضافة منتج.")

# ---------------- 3. التقارير ----------------
elif menu == "📊 التقارير والأرباح":
    st.header("📊 التقارير")
    inv = run_query("SELECT * FROM invoices", fetch=True)
    st.dataframe(pd.DataFrame(inv, columns=["ID", "العميل", "المجموع", "الربح", "التاريخ"]))

# ---------------- 4. العملاء ----------------
elif menu == "👥 العملاء والديون":
    st.header("👥 العملاء")
    custs = run_query("SELECT * FROM customers", fetch=True)
    st.dataframe(pd.DataFrame(custs, columns=["ID", "الاسم", "الهاتف", "الديون"]))
