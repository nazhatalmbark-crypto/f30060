import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام المحاسبي المتكامل", layout="wide", page_icon="📦")

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    # إضافة جدول المواد
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, barcode TEXT, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0, selling_price INTEGER DEFAULT 0)''')
    # تحديث جدول العملاء ليدعم تفاصيل أكثر (أضفنا details للعنوان التفصيلي)
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, shop_name TEXT, phone TEXT, area TEXT, details TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, total_amount INTEGER, received_amount INTEGER, remaining_amount INTEGER, invoice_date TEXT, details_json TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, amount INTEGER, exp_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS debt_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, amount INTEGER, pay_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    
    # محاولة إضافة أعمدة جديدة إذا لم تكن موجودة
    try: c.execute("ALTER TABLE customers ADD COLUMN area TEXT")
    except: pass
    try: c.execute("ALTER TABLE customers ADD COLUMN details TEXT")
    except: pass
    
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

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False
if 'backup_downloaded' not in st.session_state: st.session_state.backup_downloaded = False

# --- واجهة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("🔐 ياسر ويب - بوابة الدخول")
    # ... (نفس كود الدخول السابق) ...
    with st.form("login_form"):
        u_input = st.text_input("اسم المستخدم")
        p_input = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("تسجيل الدخول"):
            user_record = run_query("SELECT password FROM system_users WHERE username = ?", (u_input,), fetch=True)
            if user_record and user_record[0][0] == p_input:
                st.session_state.logged_in = True
                st.session_state.username = u_input
                st.rerun()
            else: st.error("خطأ في البيانات")
else:
    # الشريط الجانبي (نسخة احتياطية)
    st.sidebar.title(f"👤 {st.session_state.username}")
    try:
        with open("yasser_web.db", "rb") as f:
            if st.sidebar.download_button("📥 تحميل نسخة احتياطية", f, "backup.db"):
                st.session_state.backup_downloaded = True
    except: pass
    if st.sidebar.button("تسجيل الخروج"): st.session_state.logged_in = False; st.rerun()

    # التبويبات
    tabs = st.tabs(["🛒 البيع", "📜 الأرشيف", "📦 المخزن", "💰 الأرباح والمصاريف", "👥 العملاء والديون"])

    with tabs[0]: # البيع
        # ... (نفس كود البيع السابق) ...
        # (يتم اختيار العميل من القائمة)
        custs = run_query("SELECT name FROM customers", fetch=True)
        c_name = st.selectbox("اختر العميل:", [c[0] for c in custs] if custs else [])
        if 'cart' not in st.session_state: st.session_state.cart = []
        # ... (إضافة المواد والحفظ) ...
        if st.button("حفظ الفاتورة"):
             # حفظ الفاتورة (الكود كما هو)
             st.success("تم الحفظ")
             st.rerun()

    with tabs[1]: # الأرشيف (هنا التعديل الأهم في شكل الفاتورة)
        st.subheader("📜 الأرشيف")
        invs = run_query("SELECT id, customer_name, total_amount, received_amount, remaining_amount, details_json, invoice_date FROM invoices ORDER BY id DESC", fetch=True)
        for i in invs:
            # جلب تفاصيل العميل المحدثة
            c_info = run_query("SELECT shop_name, phone, area, details FROM customers WHERE name = ?", (i[1],), fetch=True)
            shop_n = c_info[0][0] if c_info else "غير محدد"
            phone = c_info[0][1] if c_info else "---"
            area = c_info[0][2] if c_info else "---"
            details = c_info[0][3] if c_info else "---"

            # قالب الفاتورة المطور
            pdf_html_content = f"""
            <html dir='rtl'><head><meta charset='UTF-8'></head>
            <body style='font-family: Tahoma; padding: 20px; border: 2px solid #008080;'>
                <h2 style='text-align:center;'>📦 فاتورة ياسر ويب</h2>
                <div style='background:#f4f4f4; padding:10px; margin-bottom:10px;'>
                    <p><b>اسم العميل:</b> {i[1]}</p>
                    <p><b>اسم المحل:</b> {shop_n}</p>
                    <p><b>المنطقة:</b> {area} | <b>العنوان التفصيلي:</b> {details}</p>
                    <p><b>رقم الهاتف:</b> {phone}</p>
                    <p><b>رقم الفاتورة:</b> INV-{i[0]:04d} | <b>التاريخ:</b> {i[6]}</p>
                </div>
                <table style='width:100%; border-collapse:collapse; text-align:center;'>
                    <tr style='background:#008080; color:#fff;'><th>المادة</th><th>السعر</th><th>الكمية</th><th>الإجمالي</th></tr>
                    <!-- هنا يوضع كود عرض المواد -->
                </table>
                <div style='margin-top:20px; border-top:1px solid #ccc; padding-top:10px;'>
                    <p><b>إجمالي القائمة:</b> {int(i[2]):,} د.ع</p>
                    <p><b>المبلغ المدفوع:</b> {int(i[3]):,} د.ع</p>
                    <p style='color:red;'><b>المتبقي دين:</b> {int(i[4]):,} د.ع</p>
                </div>
            </body></html>
            """
            st.download_button(f"📥 تحميل فاتورة #{i[0]}", pdf_html_content, f"inv_{i[0]}.html")

    with tabs[4]: # إضافة عميل (تحديث النموذج)
        st.subheader("👥 إضافة عميل جديد")
        with st.form("new_cust"):
            n = st.text_input("اسم العميل")
            sn = st.text_input("اسم المحل (إن وجد)")
            ph = st.text_input("رقم الهاتف")
            ar = st.text_input("المنطقة/الموقع العام")
            det = st.text_area("العنوان التفصيلي أو ملاحظات (مثلاً: رقم الدار، قرب فلان مكان)")
            if st.form_submit_button("حفظ العميل"):
                run_query("INSERT INTO customers (name, shop_name, phone, area, details) VALUES (?,?,?,?,?)", (n, sn, ph, ar, det))
                st.success("تم")
                st.rerun()
