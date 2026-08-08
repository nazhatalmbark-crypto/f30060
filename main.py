import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="إدارة المبيعات", page_icon="🛒", layout="wide")

# --- تنسيق الألوان والتصميم (CSS) ليطابق الصورة ---
st.markdown("""
<style>
    /* تغيير لون الأزرار الأساسية للأخضر */
    div.stButton > button:first-child {
        background-color: #1a6b51;
        color: white;
        border-radius: 8px;
        width: 100%;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #14523e;
        color: white;
    }
    /* تصميم تبويبات الأقسام */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #e6f2ee;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        color: #1a6b51;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a6b51 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_pro_pro.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    barcode TEXT,
                    price REAL DEFAULT 0,
                    cost REAL DEFAULT 0,
                    quantity INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    debt REAL DEFAULT 0)''')
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

# المتغيرات الخاصة بالجلسة
if 'cart' not in st.session_state: 
    st.session_state.cart = []

# حساب مجموع السلة
cart_items_count = sum(item['qty'] for item in st.session_state.cart)
cart_total_price = sum(item['price'] * item['qty'] for item in st.session_state.cart)

# --- القائمة الرئيسية (تمثل القائمة السفلية في التطبيق) ---
menu = st.sidebar.radio("التنقل الأساسي", ["🏪 المبيعات", "🛒 المشتريات", "📦 المخازن", "📊 التقارير", "💰 المالية"])

# --- 🤖 المساعد الذكي Prosto AI (القائمة الجانبية) ---
st.sidebar.markdown("---")
with st.sidebar.expander("🤖 اسأل Prosto AI..."):
    st.write("اكتب (الاسم, العدد, السعر) للإضافة، أو استعلم عن ديون أو جرد.")
    user_ai_input = st.text_area("رسالتك:", height=100)
    
    if st.button("إرسال للمساعد 🚀"):
        if "جرد" in user_ai_input:
            p_res = run_query("SELECT name, quantity, price FROM products", fetch=True)
            st.success("📦 جرد المخزون:")
            for pr in p_res:
                st.write(f"{pr[0]} | متوفر: {pr[1]} | السعر: {pr[2]}")
                
        elif "ديون" in user_ai_input:
            cust_res = run_query("SELECT name, debt FROM customers WHERE debt > 0", fetch=True)
            st.success("👥 الديون:")
            if cust_res:
                for cr in cust_res:
                    st.write(f"{cr[0]}: {cr[1]} د.ع")
            else:
                st.write("لا توجد ديون.")
                
        elif "," in user_ai_input:
            lines = user_ai_input.split('\n')
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
                            st.error(f"خطأ في قراءة السطر: {line}")
                    else:
                        st.error(f"التنسيق خاطئ بالسطر: {line} (يجب: اسم,عدد,سعر)")
            if success_count > 0:
                st.success(f"✅ تم إضافة/تحديث {success_count} منتج للمخزن!")
        else:
            st.warning("يرجى إدخال أمر مفهوم (جرد، ديون، أو منتجات بالتنسيق الصحيح).")

# ---------------- 1. شاشة المبيعات (نفس التطبيق) ----------------
if menu == "🏪 المبيعات":
    # الهيدر والسلة
    col_title, col_cart = st.columns([3, 1])
    with col_title:
        st.title("🏪 إدارة المبيعات")
    with col_cart:
        # زر السلة الفوقاني مثل التطبيق
        with st.expander(f"🛒 السلة ({cart_items_count}) - المجموع: {cart_total_price} د.ع"):
            if not st.session_state.cart:
                st.info("السلة فارغة.")
            else:
                for i, item in enumerate(st.session_state.cart):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"{item['name']} (x{item['qty']})")
                    if c2.button("❌", key=f"del_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                st.write("---")
                cust_name = st.text_input("اسم العميل:", placeholder="اختر عميل أو اكتب نقدي")
                if st.button("✅ تأكيد الدفع"):
                    if cust_name:
                        for item in st.session_state.cart:
                            run_query("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['qty'], item['id']))
                        run_query("INSERT INTO invoices (customer_name, total, date) VALUES (?, ?, ?)", 
                                  (cust_name, cart_total_price, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        st.session_state.cart = []
                        st.success("تم تأكيد الفاتورة بنجاح!")
                        st.rerun()
                    else:
                        st.error("يرجى كتابة اسم العميل.")

    # التبويبات العلوية مثل التطبيق
    tab1, tab2, tab3, tab4 = st.tabs(["شاشة البيع", "الفواتير", "العملاء", "مرتجعات الفواتير"])

    # === تبويب شاشة البيع ===
    with tab1:
        search_box = st.text_input("🔍 ابحث بإسم أو باركود ...")
        
        products = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
        filtered_prods = [p for p in products if search_box.lower() in p[1].lower()]
        
        if not filtered_prods:
            st.info("لا توجد منتجات مطابقة أو المخزون فارغ. استخدم المساعد الذكي للإضافة.")
        else:
            # عرض المنتجات كبطاقات شبكية (Grid)
            cols = st.columns(2) # عمودين مثل التطبيق
            for idx, prod in enumerate(filtered_prods):
                p_id, name, price, qty = prod
                
                # حساب الكمية الموجودة مسبقاً في السلة لهذا المنتج
                qty_in_cart = sum(item['qty'] for item in st.session_state.cart if item['id'] == p_id)
                
                with cols[idx % 2]:
                    with st.container(border=True): # يصنع شكل البطاقة
                        st.markdown(f"**{name}**")
                        st.write(f"💰 {price} دينار &nbsp; | &nbsp; 📦 {qty} قطعة")
                        
                        add_col, q_col = st.columns([2, 1])
                        add_q = q_col.number_input("", min_value=1, max_value=max(1, qty), value=1, label_visibility="collapsed", key=f"q_{p_id}")
                        
                        if add_col.button(f"إضافة 🛒 ({qty_in_cart})", key=f"add_{p_id}", use_container_width=True):
                            if qty >= add_q:
                                found = False
                                for item in st.session_state.cart:
                                    if item['id'] == p_id:
                                        item['qty'] += add_q
                                        found = True
                                        break
                                if not found:
                                    st.session_state.cart.append({'id': p_id, 'name': name, 'price': price, 'qty': add_q})
                                st.rerun()
                            else:
                                st.error("غير متوفر!")

    # === تبويب الفواتير ===
    with tab2:
        st.subheader("🧾 الفواتير السابقة")
        invs = run_query("SELECT id, customer_name, total, date FROM invoices ORDER BY id DESC", fetch=True)
        if invs:
            st.dataframe(pd.DataFrame(invs, columns=["رقم الفاتورة", "العميل", "المبلغ الكلي", "التاريخ"]), use_container_width=True)
        else:
            st.write("لا توجد فواتير بعد.")

    # === تبويب العملاء ===
    with tab3:
        st.subheader("👥 إدارة العملاء والديون")
        custs = run_query("SELECT id, name, phone, debt FROM customers", fetch=True)
        if custs:
            st.dataframe(pd.DataFrame(custs, columns=["الرقم", "الاسم", "الهاتف", "الدين"]), use_container_width=True)
        else:
            st.write("لا يوجد عملاء مسجلين.")

    # === تبويب المرتجعات ===
    with tab4:
        st.subheader("↩️ مرتجعات الفواتير")
        st.info("هذه الميزة قيد التطوير. سيتم إضافتها قريباً.")

# ---------------- 2. باقي الأقسام (المخازن, التقارير, إلخ) ----------------
elif menu == "📦 المخازن":
    st.title("📦 إدارة المخازن")
    prods = run_query("SELECT id, name, price, quantity FROM products", fetch=True)
    if prods:
        st.dataframe(pd.DataFrame(prods, columns=["ID", "اسم المنتج", "السعر", "الكمية المتوفرة"]), use_container_width=True)
    else:
        st.info("المخزن فارغ.")

elif menu in ["🛒 المشتريات", "📊 التقارير", "💰 المالية"]:
    st.title(menu)
    st.info("هذا القسم متاح للتوسعة بناءً على تفاصيل عملك القادمة.")
