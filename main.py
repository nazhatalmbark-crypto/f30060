import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
import streamlit.components.v1 as components

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي", layout="wide")

# (دوال قاعدة البيانات تبقى كما هي)
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0, selling_price INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, shop_name TEXT, phone TEXT, shop_location TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, total_amount INTEGER, received_amount INTEGER, remaining_amount INTEGER, invoice_date TEXT, details_json TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# --- إدارة الجلسة (نفس الكود السابق لاختصار المساحة) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
# (باقي إدارة الجلسة موجودة)

# --- كود صفحة الطباعة النظيفة ---
# هذا الكود يولد صفحة HTML كاملة، تفتح بصفحة جديدة وتأمر الطابعة تفتح تلقائياً
def get_printable_html(i_id, c_name, total, received, remaining, details_json, date_val):
    items_html = ""
    try:
        df = pd.read_csv(StringIO(details_json))
        for _, row in df.iterrows():
            items_html += f"<tr><td>{row.get('name', '')}</td><td>{int(row.get('price', 0)):,}</td><td>{row.get('qty', 0)}</td></tr>"
    except: items_html = "<tr><td colspan='3'>خطأ في تحميل المواد</td></tr>"
    
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Tahoma, sans-serif; direction: rtl; padding: 20px; }}
            .inv-box {{ border: 2px solid #000; padding: 20px; max-width: 800px; margin: auto; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #000; padding: 10px; text-align: center; }}
            @media print {{ 
                .no-print {{ display: none; }} 
                body {{ padding: 0; }}
            }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="inv-box">
            <h1 style="text-align: center;">ياسر ويب</h1>
            <p>رقم الفاتورة: #{i_id} | التاريخ: {date_val}</p>
            <p>اسم الزبون: {c_name}</p>
            <table>
                <tr><th>المادة</th><th>السعر</th><th>الكمية</th></tr>
                {items_html}
            </table>
            <p>الإجمالي: {int(total):,} دينار</p>
            <p>المستلم: {int(received):,} دينار</p>
            <p><b>المتبقي: {int(remaining):,} دينار</b></p>
            <button class="no-print" onclick="window.print()" style="padding: 10px; cursor: pointer;">🖨️ طباعة الفاتورة</button>
        </div>
    </body>
    </html>
    """

# --- جزء الأرشيف المحدث ---
# بدل الـ expander اللي يفتح بداخل الصفحة، راح نستخدم رابط يفتح صفحة جديدة
if 'show_print_page' in st.session_state and st.session_state.show_print_page:
    # هذا الجزء يعرض الفاتورة فقط للطباعة
    components.html(st.session_state.print_html, height=800)
    if st.button("⬅️ العودة للأرشيف"):
        st.session_state.show_print_page = False
        st.rerun()
else:
    # (بقية التبويبات والبيع والشراء كما هي..)
    # في تبويب الأرشيف، استخدم هذا الزر:
    # if st.button("🖨️ طباعة فاتورة", key=f"print_{i[0]}"):
    #     st.session_state.print_html = get_printable_html(i[0], i[1], i[2], i[3], i[4], i[5], i[6])
    #     st.session_state.show_print_page = True
    #     st.rerun()
    pass
