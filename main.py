import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

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
                    name TEXT,
                    barcode TEXT,
                    price REAL,
                    cost REAL,
                    quantity INTEGER)''')
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

# دوال مساعدة للتعامل مع قاعدة البيانات
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

# القائمة الجانبية للتنقل (بدون خيار المساعد الذكي كقائمة رئيسية)
st.sidebar.title("🚀 Eng. Yasser Pro")
menu = st.sidebar.selectbox("القائمة الرئيسية", ["🛒 نقطة البيع (السلة)", "📦 إدارة المخزون", "📊 التقارير والأرباح", "👥 العملاء والديون"])

# --- المساعد الذكي المصغر (على صفحة بوحده في الشريط الجانبي) ---
st.sidebar.markdown("---")
with st.sidebar.expander("🤖 مساعدي الذكي السريع"):
    st.write("استعلم بسرعة عن الديون أو اطلب جرد للمنتجات:")
    ai_query = st.text_input("اكتب طلبك (مثلاً: ديون فلان، أو جرد)")
    if ai_query:
        if "ديون" in ai_query or "دين" in ai_query:
            search_name = ai_query.replace("ديون", "").replace("دين", "").strip()
            if search_name:
                cust_res = run_query("SELECT name, phone, debt FROM customers WHERE name LIKE ?", (f"%{search_name}%",), fetch=True)
                if cust_res:
                    for cr in cust_res:
                        st.success(f"العميل: {cr[0]} | الهاتف: {cr[1]} | الدين: {cr[2]} د.ع")
                else:
                    st.warning("لم يتم العثور على عميل بهذا الاسم.")
            else:
                st.info("يرجى كتابة اسم العميل مع الكلمة.")
        elif "جرد" in ai_query or "مخزون" in ai_query:
            p_res = run_query("SELECT name, quantity, price FROM products", fetch=True)
            if p_res:
                st.write("📦 **جرد المخزون الحالي:**")
                for pr in p_res:
                    st.write(f"- {pr[1]}x {pr[0]} ({pr[2]} د.ع)")
            else:
                st.info("المخزون فارغ حالياً.")
        else:
            st.info("جرب كتابة: (ديون [اسم العميل]) أو كلمة (جرد).")

# ---------------- 1. نقطة البيع (السلة والفاتورة) ----------------
if menu == "🛒 نقطة البيع (السلة)":
    st.header("🛒 نقطة البيع - سلة المشتريات")
    
    products = run_query("SELECT id, name, price, quantity, barcode FROM products", fetch=True)
    
    if not products:
        st.warning("لا توجد منتجات مضافة في المخزون حالياً. يرجى إضافتها من قسم إدارة المخزون.")
    else:
        # تهيئة السلة في الذاكرة المؤقتة
        if 'cart' not in st.session_state:
            st.session_state.cart = []

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("اختر المنتجات لإضافتها للسلة")
            search_query = st.text_input("🔍 بحث سريع عن منتج (بالاسم أو الباركود)")
            
            # فلترة المنتجات حسب البحث
            filtered_products = [p for p in products if search_query.lower() in p[1].lower() or search_query in str(p[4])]
            
            for prod in filtered_products:
                p_id, name, price, qty, barcode = prod
                cols = st.columns([3, 1, 1, 1])
                cols[0].text(f"{name} (المتوفر: {qty}) - السعر: {price} د.ع")
                cols[1].text(f"الباركود: {barcode}")
                add_qty = cols[2].number_input("الكمية", min_value=1, max_value=max(1, qty), value=1, key=f"qty_{p_id}")
                if cols[3].button("إضافة للسلة ➕", key=f"add_{p_id}"):
                    if qty >= add_qty:
                        found = False
                        for item in st.session_state.cart:
                            if item['id'] == p_id:
                                item['qty'] += add_qty
                                found = True
                                break
                        if not found:
                            st.session_state.cart.append({'id': p_id, 'name': name, 'price': price, 'qty': add_qty, 'max_qty': qty})
                        st.success(f"تم إضافة {name} للسلة بنجاح!")
                    else:
                        st.error("الكمية المطلوبة غير متوفرة في المخزون!")

        with col2:
            st.subheader("🛍️ سلة المشتريات الحالية")
            if not st.session_state.cart:
                st.info("السلة فارغة حالياً.")
            else:
                total_amount = 0
                for index, item in enumerate(st.session_state.cart):
                    item_total = item['price'] * item['qty']
                    total_amount += item_total
                    st.write(f"**{item['name']}**")
                    st.write(f"الكمية: {item['qty']} | السعر: {item_total} د.ع")
                    if st.button("حذف ❌", key=f"del_{index}"):
                        st.session_state.cart.pop(index)
                        st.rerun()
                    st.divider()

                st.markdown(f"### المجموع الكلي: {total_amount} د.ع")
                
                st.subheader("معلومات العميل لإتمام الفاتورة")
                cust_name = st.text_input("اسم العميل")
                cust_phone = st.text_input("رقم الهاتف")
                is_debt = st.checkbox("تسجيل كدين على العميل؟")

                if st.button("✅ تثبيت وطباعة الفاتورة"):
                    if not cust_name:
                        st.warning("يرجى إدخال اسم العميل على الأقل لإتمام الفاتورة.")
                    else:
                        total_profit = 0
                        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        for item in st.session_state.cart:
                            prod_info = run_query("SELECT cost, quantity FROM products WHERE id = ?", (item['id'],), fetch=True)
                            cost = prod_info[0][0]
                            old_qty = prod_info[0][1]
                            
                            item_profit = (item['price'] - cost) * item['qty']
                            total_profit += item_profit
                            
                            new_qty = old_qty - item['qty']
                            run_query("UPDATE products SET quantity = ? WHERE id = ?", (new_qty, item['id']))

                        run_query("INSERT INTO invoices (customer_name, total, profit, date) VALUES (?, ?, ?, ?)", 
                                  (cust_name, total_amount, total_profit, current_date))

                        if is_debt:
                            check_cust = run_query("SELECT id, debt FROM customers WHERE name = ?", (cust_name,), fetch=True)
                            if check_cust:
                                new_debt = check_cust[0][1] + total_amount
                                run_query("UPDATE customers SET debt = ? WHERE name = ?", (new_debt, cust_name))
                            else:
                                run_query("INSERT INTO customers (name, phone, debt) VALUES (?, ?, ?)", (cust_name, cust_phone, total_amount))

                        st.success("🎉 تم تثبيت الفاتورة وتحديث المخزون بنجاح!")
                        st.session_state.cart = []
                        st.rerun()

# ---------------- 2. إدارة المخزون ----------------
elif menu == "📦 إدارة المخزون":
    st.header("📦 إدارة المخزون والمنتجات")
    
    low_stock_items = run_query("SELECT name, quantity FROM products WHERE quantity <= 3", fetch=True)
    if low_stock_items:
        st.error("⚠️ تنبيه: المنتجات التالية اقتربت على النفاد في المخزون!")
        for item in low_stock_items:
            st.warning(f"- المنتج: **{item[0]}** | الكمية المتبقية: **{item[1]}**")

    tab1, tab2 = st.tabs(["إضافة منتج جديد", "عرض المنتجات الحالية"])
    
    with tab1:
        st.subheader("إضافة منتج جديد للمخزن")
        with st.form("add_product_form"):
            p_name = st.text_input("اسم المنتج")
            p_barcode = st.text_input("رقم الباركود")
            p_price = st.number_input("سعر البيع", min_value=0.0, step=0.5)
            p_cost = st.number_input("سعر التكلفة (الشراء)", min_value=0.0, step=0.5)
            p_qty = st.number_input("الكمية المتوفرة", min_value=1, step=1)
            
            submit_prod = st.form_submit_button("حفظ المنتج")
            if submit_prod:
                if p_name and p_price > 0:
                    run_query("INSERT INTO products (name, barcode, price, cost, quantity) VALUES (?, ?, ?, ?, ?)", 
                              (p_name, p_barcode, p_price, p_cost, p_qty))
                    st.success(f"تم إضافة المنتج '{p_name}' بنجاح!")
                else:
                    st.error("يرجى إدخال اسم المنتج وسعر البيع بشكل صحيح.")

    with tab2:
        st.subheader("قائمة المخزون الحالي")
        prods = run_query("SELECT id, name, barcode, price, cost, quantity FROM products", fetch=True)
        if prods:
            df_prods = pd.DataFrame(prods, columns=["ID", "اسم المنتج", "الباركود", "سعر البيع", "التكلفة", "الكمية"])
            st.dataframe(df_prods, use_container_width=True)
        else:
            st.info("لا توجد منتجات مسجلة حالياً.")

# ---------------- 3. التقارير والأرباح ----------------
elif menu == "📊 التقارير والأرباح":
    st.header("📊 تقارير المبيعات والأرباح المتقدمة")
    
    invoices = run_query("SELECT id, customer_name, total, profit, date FROM invoices", fetch=True)
    
    if invoices:
        df_inv = pd.DataFrame(invoices, columns=["رقم الفاتورة", "اسم العميل", "المجموع (د.ع)", "صافي الربح (د.ع)", "التاريخ"])
        
        total_sales = df_inv["المجموع (د.ع)"].sum()
        total_profits = df_inv["صافي الربح (د.ع)"].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("إجمالي المبيعات العامة", f"{total_sales} د.ع")
        col2.metric("إجمالي صافي الأرباح", f"{total_profits} د.ع")
        
        st.subheader("سجل الفواتير السابقة")
        st.dataframe(df_inv, use_container_width=True)
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن لعرض التقارير.")

# ---------------- 4. العملاء والديون ----------------
elif menu == "👥 العملاء والديون":
    st.header("👥 إدارة حسابات الديون والعملاء")
    
    tab_cust1, tab_cust2 = st.tabs(["قائمة العملاء والديون", "➕ إضافة عميل جديد"])
    
    with tab_cust1:
        customers = run_query("SELECT id, name, phone, debt FROM customers", fetch=True)
        if customers:
            df_cust = pd.DataFrame(customers, columns=["ID", "اسم العميل", "رقم الهاتف", "الديون المترتبة (د.ع)"])
            st.dataframe(df_cust, use_container_width=True)
            
            st.subheader("تسديد دين عميل")
            selected_cust = st.selectbox("اختر العميل لتسديد دينه", [c[1] for c in customers])
            pay_amount = st.number_input("مبلغ التسديد", min_value=0.0, step=1000.0)
            
            if st.button("تحديث وتسجيل السداد"):
                c_info = run_query("SELECT debt FROM customers WHERE name = ?", (selected_cust,), fetch=True)
                if c_info:
                    new_debt = max(0.0, c_info[0][0] - pay_amount)
                    run_query("UPDATE customers SET debt = ? WHERE name = ?", (new_debt, selected_cust))
                    st.success(f"تم تحديث دين العميل {selected_cust} بنجاح. الدين الحالي: {new_debt} د.ع")
                    st.rerun()
        else:
            st.info("لا توجد ديون أو عملاء مسجلين حالياً.")
            
    with tab_cust2:
        st.subheader("إضافة عميل جديد يدوياً")
        with st.form("add_customer_form"):
            new_c_name = st.text_input("اسم العميل")
            new_c_phone = st.text_input("رقم الهاتف")
            new_c_debt = st.number_input("دين سابق (إن وجد)", min_value=0.0, step=1000.0)
            
            submit_cust = st.form_submit_button("حفظ العميل")
            if submit_cust:
                if new_c_name:
                    run_query("INSERT INTO customers (name, phone, debt) VALUES (?, ?, ?)", (new_c_name, new_c_phone, new_c_debt))
                    st.success(f"تم إضافة العميل {new_c_name} بنجاح!")
                else:
                    st.error("يرجى إدخال اسم العميل على الأقل.")
