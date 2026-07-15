import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eng. Yasser System", layout="wide")

# إعداد قاعدة البيانات
conn = sqlite3.connect('shop_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price INTEGER, quantity INTEGER, cost_price INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, items TEXT, total INTEGER, timestamp TEXT)')
conn.commit()

# --- CSS ---
st.markdown("""
    <style>
    .prod-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9; text-align: center; margin: 10px; }
    .header-box { background-color: #1a4d2e; color: white; padding: 10px; border-radius: 5px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}

# --- القائمة الجانبية ---
st.sidebar.title("النظام")
menu = st.sidebar.radio("القائمة", ["شاشة البيع", "إضافة مواد", "جرد المخزن", "التقارير"])
st.sidebar.markdown("---")
st.sidebar.write("**المبرمج ياسر - مستمرين نحو الأفضل**")

# --- 1. شاشة البيع ---
if menu == "شاشة البيع":
    st.markdown('<div class="header-box"><h2>🛒 شاشة البيع</h2></div>', unsafe_allow_html=True)
    
    products = pd.read_sql("SELECT rowid, * FROM products", conn)
    cols = st.columns(3)
    
    for i, row in products.iterrows():
        with cols[i % 3]:
            st.markdown(f'<div class="prod-card"><h4>{row["name"]}</h4><p>السعر: {row["price"]} د.ع | المتوفر: {row["quantity"]}</p></div>', unsafe_allow_html=True)
            qty_to_sell = st.number_input(f"الكمية لـ {row['name']}", min_value=0, max_value=row["quantity"], key=f"qty_{row['rowid']}")
            
            if qty_to_sell > 0:
                if st.button(f"أضف {row['name']} للسلة", key=f"add_{row['rowid']}"):
                    st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty_to_sell}
                    st.success(f"تم إضافة {qty_to_sell} من {row['name']}")

    # عرض السلة
    st.divider()
    st.header("الفاتورة الحالية")
    if st.session_state.cart:
        cart_df = pd.DataFrame.from_dict(st.session_state.cart, orient='index')
        st.table(cart_df)
        total = sum(item['price'] * item['qty'] for item in st.session_state.cart.values())
        st.write(f"### المجموع الكلي: {total} د.ع")
        
        if st.button("إتمام البيع وخصم المخزن"):
            for name, data in st.session_state.cart.items():
                c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (data['qty'], name))
            c.execute("INSERT INTO invoices VALUES (?,?,?,?)", ("زبون", str(st.session_state.cart), total, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.session_state.cart = {}
            st.success("تمت عملية البيع بنجاح!")
            st.rerun()
    else:
        st.info("السلة فارغة")

# --- 2. إضافة مواد ---
elif menu == "إضافة مواد":
    st.header("➕ إضافة مواد جديدة")
    with st.form("add_p"):
        n = st.text_input("اسم المادة"); p = st.text_input("السعر"); q = st.text_input("الكمية")
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO products VALUES (?,?,?,?)", (n, int(p), int(q), 0))
            conn.commit(); st.success("تمت الإضافة!")

# --- 3. جرد المخزن ---
elif menu == "جرد المخزن":
    st.header("📦 جرد المخزن")
    df = pd.read_sql("SELECT * FROM products", conn)
    st.table(df)

# --- 4. التقارير ---
elif menu == "التقارير":
    st.header("📈 التقارير")
    st.write("**المبرمج ياسر - مستمرين نحو الأفضل**")
    sales = pd.read_sql("SELECT * FROM invoices", conn)
    st.table(sales)
