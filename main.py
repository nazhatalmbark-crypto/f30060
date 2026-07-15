import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="Eng. Yasser System Pro", layout="wide")

# إعداد قاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول (هيكل متكامل)
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, shop_name TEXT, phone TEXT, items TEXT, total INTEGER, timestamp TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, area TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS debts (customer_name TEXT, amount INTEGER, note TEXT)')
conn.commit()

# --- CSS للتصميم والطباعة ---
st.markdown("""
<style>
    .invoice-box { border: 2px solid #333; padding: 30px; border-radius: 15px; background-color: #f8f9fa; color: #000; max-width: 600px; margin: auto; box-shadow: 5px 5px 15px #ccc; }
    @media print { .stSidebar {display: none;} .invoice-box {box-shadow: none; border: 1px solid #000;} }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Eng. Yasser System Pro")
menu = st.sidebar.radio("القائمة", ["سلة البيع", "إضافة مواد", "جرد المخزن", "أرشيف الفواتير", "العملاء", "الديون", "لوحة التحكم"])

if 'cart' not in st.session_state: st.session_state.cart = []

# --- 1. سلة البيع ---
if menu == "سلة البيع":
    st.header("🛒 سلة البيع")
    if 'invoice_view' in st.session_state and st.session_state.invoice_view:
        inv = st.session_state.temp_invoice
        st.markdown(f"""
        <div class="invoice-box">
            <h2 style="text-align: center;">Eng. Yasser System</h2>
            <hr>
            <p><strong>الزبون:</strong> {inv['name']} | <strong>التاريخ:</strong> {inv['time']}</p>
            <p><strong>المحل:</strong> {inv['shop']} | <strong>هاتف:</strong> {inv['phone']}</p>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #ddd;"><th>المادة</th><th>السعر</th></tr>
                {"".join([f"<tr><td style='padding: 8px; border: 1px solid #999;'>{i['name']}</td><td style='padding: 8px; border: 1px solid #999;'>{i['price']} د.ع</td></tr>" for i in st.session_state.cart])}
            </table>
            <h3 style="text-align: right;">المجموع الكلي: {sum(i['price'] for i in st.session_state.cart)} د.ع</h3>
            <p style="text-align: center;">المبرمج ياسر - مستمرين نحو الأفضل</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("إغلاق الفاتورة"):
            st.session_state.invoice_view = False
            st.session_state.cart = []
            st.rerun()
    else:
        col1, col2 = st.columns([2, 1])
        products = pd.read_sql("SELECT * FROM products WHERE quantity > 0", conn)
        cust_df = pd.read_sql("SELECT * FROM customers", conn)
        with col1:
            for _, row in products.iterrows():
                if st.button(f"إضافة {row['name']} ({row['price']})", key=f"add_{row['name']}"):
                    st.session_state.cart.append({'name': row['name'], 'price': int(row['price'])})
                    st.rerun()
        with col2:
            sel_name = st.selectbox("اسم الزبون", ["--- اختر ---"] + cust_df['name'].tolist())
            shop_name = st.text_input("اسم المحل")
            phone = st.text_input("رقم الهاتف")
            if st.button("حفظ وإصدار الفاتورة"):
                total = sum(i['price'] for i in st.session_state.cart)
                c.execute("INSERT INTO invoices VALUES (?,?,?,?,?,?)", (sel_name, shop_name, phone, str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d")))
                for item in st.session_state.cart:
                    c.execute("UPDATE products SET quantity = quantity - 1 WHERE name = ?", (item['name'],))
                conn.commit()
                st.session_state.temp_invoice = {'name': sel_name, 'shop': shop_name, 'phone': phone, 'time': datetime.now().strftime("%Y-%m-%d")}
                st.session_state.invoice_view = True
                st.rerun()

# --- 2. إضافة مواد (بدون أزرار +/-) ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد جديدة")
    with st.form("add_p"):
        n = st.text_input("اسم المادة")
        p = st.text_input("سعر البيع")
        c_p = st.text_input("سعر الشراء")
        q = st.text_input("الكمية")
        if st.form_submit_button("حفظ"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, int(p), int(q), int(c_p)))
            conn.commit()
            st.success("تم إضافة المادة!")

# --- 3. جرد المخزن (مع تنبيهات) ---
elif menu == "جرد المخزن":
    st.header("📊 جرد المخزن")
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    for _, row in products.iterrows():
        status = "🔴 (قربت تخلص)" if int(row['quantity']) <= 5 else "✅"
        st.write(f"{status} **{row['name']}** | الكمية: {row['quantity']} | البيع: {row['price']} | الشراء: {row['cost_price']}")
        if st.button("حذف", key=f"del_{row['rowid']}"):
            c.execute("DELETE FROM products WHERE rowid = ?", (row['rowid'],))
            conn.commit()
            st.rerun()

# --- 4. الأرشيف (بحث + تصدير) ---
elif menu == "أرشيف الفواتير":
    st.header("📜 أرشيف الفواتير")
    search = st.text_input("بحث باسم العميل")
    query = "SELECT * FROM invoices"
    if search: query += f" WHERE customer_name LIKE '%{search}%'"
    df = pd.read_sql(query, conn)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 تحميل الفواتير (Excel)", csv, "invoices.csv", "text/csv")

# --- 5. لوحة التحكم (الأرباح) ---
elif menu == "لوحة التحكم":
    st.header("📈 لوحة التحكم")
    inv = pd.read_sql("SELECT * FROM invoices", conn)
    prod = pd.read_sql("SELECT * FROM products", conn)
    st.metric("إجمالي المبيعات", f"{inv['total'].sum() if not inv.empty else 0} د.ع")
    st.write("استمر في العمل - المبرمج ياسر")

# --- الأقسام الأخرى ---
elif menu == "العملاء":
    st.header("👥 العملاء")
    with st.form("add_c"):
        n = st.text_input("اسم العميل"); s = st.text_input("المحل"); ph = st.text_input("الهاتف")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (n, s, ph, "", ""))
            conn.commit()
            st.rerun()
    st.dataframe(pd.read_sql("SELECT * FROM customers", conn))

elif menu == "الديون":
    st.header("💸 الديون")
    with st.form("add_d"):
        n = st.text_input("اسم العميل"); a = st.number_input("المبلغ"); nt = st.text_input("ملاحظات")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO debts VALUES (?,?,?)", (n, int(a), nt))
            conn.commit()
            st.rerun()
    st.dataframe(pd.read_sql("SELECT * FROM debts", conn))
