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
                p_res = run_query("SELECT name, quantity, price FROM products", fetch=True)
                st.write("📦 **جرد المخزون:**")
                for pr in p_res:
                    st.write(f"- {pr[0]} | الكمية: {pr[1]} | السعر: {pr[2]} د.ع")
            else:
                cust_res = run_query("SELECT name, debt FROM customers WHERE name LIKE ?", (f"%{query_text}%",), fetch=True)
                if cust_res:
                    for cr in cust_res:
                        st.success(f"العميل: {cr[0]} | الدين: {cr[1]} د.ع")
                else:
                    st.warning("لم يتم العثور على العميل.")
    
    else: # إضافة مخزون بالجملة مع السعر الإجباري
        st.write("اكتب بالتنسيق التالي: `اسم المنتج, العدد, السعر`")
        batch_input = st.text_area("مثال:\nبيبسي, 50, 1000\nحليب, 20, 750")
        if st.button("إضافة للمخزن دفعة واحدة"):
            lines = batch_input.split('\n')
            success_count = 0
            for line in lines:
                if line.strip() and "," in line:
                    parts = line.split(',')
                    if len(parts) == 3:
                        try:
                            p_name = parts[0].strip()
                            p_qty = int(parts[1].strip())
                            p_price = float(parts[2].strip())
                            
                            exists = run_query("SELECT quantity FROM products WHERE name = ?", (p_name,), fetch=True)
                            if exists:
                                new_q = exists[0][0] + p_qty
                                run_query("UPDATE products SET quantity = ?, price = ? WHERE name = ?", (new_q, p_price, p_name))
                            else:
                                run_query("INSERT INTO products (name, quantity, price, cost) VALUES (?, ?, ?, 0)", (p_name, p_qty, p_price))
                            success_count += 1
                        except:
                            st.error(f"خطأ في قراءة البيانات بالسطر: {line}")
                    else:
                        st.error(f"يجب كتابة (الاسم, العدد, السعر) بدقة في السطر: {line}")
            if success_count > 0:
                st.success(f"تمت إضافة وتحديث {success_count} منتج بنجاح مع أسعارها وظهرت في نقطة البيع!")

# ---------------- 1. نقطة البيع (السلة) ----------------
if menu == "🛒 نقطة البيع (السلة)":
    st.header("🛒 نقطة البيع - سلة المشتريات")
    products = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
    
    if not products:
        st.warning("المخزون فارغ حالياً! استخدم المساعد الجانبي لإضافة المنتجات مع أسعارها.")
    else:
        if 'cart' not in st.session_state: 
            st.session_state.cart = []
        
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("اختر المنتجات لإضافتها للسلة")
            search_box = st.text_input("🔍 بحث عن منتج")
            
            filtered_prods = [p for p in products if search_box.lower() in p[1].lower()]
            
            for prod in filtered_prods:
                p_id, name, price, qty = prod
                cols = st.columns([3, 1, 1])
                cols[0].text(f"{name} (المتوفر: {qty}) - السعر: {price} د.ع")
                add_q = cols[1].number_input("العدد", min_value=1, max_value=max(1, qty), value=1, key=f"q_{p_id}")
                if cols[2].button("إضافة ➕", key=f"add_{p_id}"):
                    if qty >= add_q:
                        found = False
                        for item in st.session_state.cart:
                            if item['id'] == p_id:
                                item['qty'] += add_q
                                found = True
                                break
                        if not found:
                            st.session_state.cart.append({'id': p_id, 'name': name, 'price': price, 'qty': add_q})
                        st.success(f"تم إضافة {name} للسلة!")
                    else:
                        st.error("الكمية غير متوفرة بالمخزون!")

        with col2:
            st.subheader("🛍️ سلة المشتريات")
            if not st.session_state.cart:
                st.info("السلة فارغة.")
            else:
                total = 0
                for i, item in enumerate(st.session_state.cart):
                    item_tot = item['price'] * item['qty']
                    total += item_tot
                    st.write(f"**{item['name']}** - {item['qty']} عدد | {item_tot} د.ع")
                    if st.button("حذف ❌", key=f"del_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                    st.divider()
                
                st.markdown(f"### المجموع الكلي: {total} د.ع")
                cust_name = st.text_input("اسم العميل لإتمام الفاتورة")
                
                if st.button("✅ تثبيت وطباعة الفاتورة"):
                    if cust_name:
                        for item in st.session_state.cart:
                            run_query("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['qty'], item['id']))
                        run_query("INSERT INTO invoices (customer_name, total, date) VALUES (?, ?, ?)", 
                                  (cust_name, total, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        st.session_state.cart = []
                        st.success("🎉 تم تثبيت الفاتورة بنجاح!")
                        st.rerun()
                    else:
                        st.error("يرجى إدخال اسم العميل.")

# ---------------- 2. إدارة المخزون ----------------
elif menu == "📦 إدارة المخزون":
    st.header("📦 إدارة المخزون")
    prods = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
    if prods:
        st.dataframe(pd.DataFrame(prods, columns=["ID", "اسم المنتج", "السعر", "الكمية"]), use_container_width=True)
    else:
        st.info("لا توجد منتجات مسجلة.")

# ---------------- 3. التقارير ----------------
elif menu == "📊 التقارير والأرباح":
    st.header("📊 التقارير والفواتير")
    inv = run_query("SELECT id, customer_name, total, date FROM invoices", fetch=True)
    if inv:
        st.dataframe(pd.DataFrame(inv, columns=["رقم الفاتورة", "العميل", "المجموع", "التاريخ"]), use_container_width=True)
    else:
        st.info("لا توجد فواتير مسجلة.")

# ---------------- 4. العملاء ----------------
elif menu == "👥 العملاء والديون":
    st.header("👥 العملاء والديون")
    custs = run_query("SELECT id, name, phone, debt FROM customers", fetch=True)
    if custs:
        st.dataframe(pd.DataFrame(custs, columns=["ID", "الاسم", "الهاتف", "الدين"]), use_container_width=True)
    else:
        st.info("لا توجد ديون مسجلة.")
