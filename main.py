import streamlit as st
import sqlite3
import pandas as pd
import ast
import os
import urllib.request
from datetime import date
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="Eng. Yasser Pro System - أسعد نفسك بنفسك", layout="wide")

# --- دالة تحميل الخط ---
def ensure_font():
    font_path = "Amiri-Regular.ttf"
    if not os.path.exists(font_path) or os.path.getsize(font_path) < 10000:
        try:
            url = "https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/fonts/amiri-regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            try:
                url_alt = "https://cdn.jsdelivr.net/npm/kendo-ui-core@2021.1.224/css/web/fonts/DejaVu/DejaVuSans.ttf"
                urllib.request.urlretrieve(url_alt, font_path)
            except:
                pass
    return font_path if os.path.exists(font_path) else None

# --- قاعدة البيانات وتحديث الجداول تلقائياً ---
DB_NAME = 'final_system_master.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, phone TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price_carton INTEGER, quantity INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS customers (name TEXT, shop_name TEXT, phone TEXT, address TEXT, governorate TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS invoices (customer_name TEXT, shop_name TEXT, address TEXT, phone TEXT, items TEXT, total INTEGER, date TEXT, payment_type TEXT)')

# ترقية جدول المستخدمين
try:
    c.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    conn.commit()
except:
    pass

# ترقية الجداول الأخرى تلقائياً
for col_def in [
    ("customers", "shop_name", "TEXT"), ("customers", "phone", "TEXT"), 
    ("customers", "address", "TEXT"), ("customers", "governorate", "TEXT"),
    ("invoices", "shop_name", "TEXT"), ("invoices", "address", "TEXT"), 
    ("invoices", "phone", "TEXT"), ("invoices", "payment_type", "TEXT")
]:
    try:
        c.execute(f"ALTER TABLE {col_def[0]} ADD COLUMN {col_def[1]} {col_def[2]}")
        conn.commit()
    except:
        pass

# --- دالة النص العربي ---
def render_arabic(text):
    try:
        if not text:
            return ""
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    except:
        return str(text)

# --- دالة توليد الفاتورة الاحترافية ---
def generate_pdf(row, items):
    pdf = FPDF()
    pdf.add_page()
    
    font_path = ensure_font()
    if not font_path:
        pdf.set_font("helvetica", size=14)
        pdf.cell(200, 10, "Font Error: Font missing", ln=True, align='C')
        return bytes(pdf.output())
    
    pdf.add_font("ArabicFont", "", font_path)
    
    pdf.set_fill_color(26, 82, 118)
    pdf.rect(10, 10, 190, 26, 'F')
    pdf.set_text_color(255, 255, 255)
    
    pdf.set_font("ArabicFont", size=14)
    pdf.set_xy(10, 12)
    pdf.cell(190, 10, render_arabic("❖ Eng. Yasser Pro System ❖"), align='C', ln=1)
    
    pdf.set_font("ArabicFont", size=11)
    pdf.set_xy(10, 22)
    pdf.cell(190, 7, render_arabic("~ [ أسعد نفسك بنفسك - مستمرون نحو الأفضل ] ~"), align='C')
    
    pdf.ln(28)
    
    pdf.set_text_color(40, 40, 40)
    pdf.set_fill_color(248, 249, 250)
    pdf.rect(10, 39, 190, 36, 'F')
    
    pdf.set_font("ArabicFont", size=12) 
    pdf.set_xy(15, 42)
    pdf.cell(90, 8, render_arabic(f"اسم العميل: {row['customer_name']}"), ln=0, align='R')
    pdf.cell(90, 8, render_arabic(f"اسم المحل: {row.get('shop_name', 'غير متوفر')}"), ln=1, align='R')
    
    pdf.set_xy(15, 52)
    pdf.cell(90, 8, render_arabic(f"رقم الهاتف: {row.get('phone', 'غير متوفر')}"), ln=0, align='R')
    pdf.cell(90, 8, render_arabic(f"تاريخ الفاتورة: {row['date']}"), ln=1, align='R')
    
    pdf.set_xy(15, 62)
    pdf.cell(180, 8, render_arabic(f"العنوان: {row.get('address', 'غير متوفر')}"), ln=1, align='R')
    
    pdf.ln(18)
    
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("ArabicFont", size=12)
    
    pdf.cell(80, 11, render_arabic("◈ المادة ◈"), 1, 0, 'C', fill=True)
    pdf.cell(30, 11, render_arabic("◈ الكمية ◈"), 1, 0, 'C', fill=True)
    pdf.cell(40, 11, render_arabic("◈ السعر ◈"), 1, 0, 'C', fill=True)
    pdf.cell(40, 11, render_arabic("◈ الإجمالي ◈"), 1, 1, 'C', fill=True)
    
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("ArabicFont", size=12)
    pdf.set_draw_color(210, 210, 210)
    
    for item, data in items.items():
        pdf.cell(80, 10, render_arabic(str(item)), 'LRB', 0, 'R')
        pdf.cell(30, 10, str(data['qty']), 'LRB', 0, 'C')
        pdf.cell(40, 10, str(data['price']), 'LRB', 0, 'C')
        pdf.cell(40, 10, str(data['qty'] * data['price']), 'LRB', 1, 'C')
        
    pdf.ln(6)
    pdf.set_fill_color(39, 174, 96)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("ArabicFont", size=13)
    pdf.cell(190, 13, render_arabic(f"✦ المجموع الكلي النهائي: {row['total']} دينار عراقي ✦"), 1, 1, 'C', fill=True)
        
    return bytes(pdf.output())

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 Eng. Yasser Pro System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>« أسعد نفسك بنفسك - مستمرون نحو الأفضل »</h3>", unsafe_allow_html=True)
    st.write("---")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب جديد"])
    
    with auth_tab1:
        st.subheader("تسجيل الدخول إلى حسابك")
        login_user = st.text_input("اسم المستخدم", key="l_user")
        login_pass = st.text_input("كلمة المرور", type="password", key="l_pass")
        
        if st.button("دخول للنظام"):
            if login_user == "admin" and login_pass == "admin":
                st.session_state.logged_in = True
                st.session_state.current_user = "المسؤول (Admin)"
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (login_user, login_pass))
                user_record = c.fetchone()
                if user_record:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.success(f"أهلاً بك مجدداً، {login_user}!")
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")

    with auth_tab2:
        st.subheader("إنشاء حساب جديد بالنظام")
        new_user = st.text_input("اسم المستخدم الجديد", key="n_user")
        new_phone = st.text_input("رقم الهاتف", key="n_phone")
        new_pass = st.text_input("كلمة المرور", type="password", key="n_pass")
        
        if st.button("تسجيل حساب جديد"):
            if new_user and new_pass and new_phone:
                try:
                    c.execute("INSERT INTO users (username, password, phone) VALUES (?, ?, ?)", (new_user, new_pass, new_phone))
                    conn.commit()
                    st.success("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول بسرعة.")
                except sqlite3.IntegrityError:
                    st.error("اسم المستخدم موجود مسبقاً، يرجى اختيار اسم آخر.")
            else:
                st.warning("يرجى ملء جميع الحقول المطلوبة.")
                
    st.stop()

# --- عنوان التطبيق والعبارة بالواجهة ---
st.title("⚙️ Eng. Yasser Pro System - أسعد نفسك بنفسك")
st.markdown(f"### « أسعد نفسك بنفسك - مستمرون نحو الأفضل » | المستخدم الحالي: **{st.session_state.current_user}**")
if st.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.rerun()
st.markdown("---")

# --- أقسام النظام (Tabs) ---
tabs = st.tabs(["🛒 البيع (شبكة)", "🧾 الفواتير والتحميل", "📦 المخزن والكميات", "👥 إدارة العملاء", "🤖 المساعد الذكي"])

with tabs[0]: # البيع بنظام الشبكة وخصم المخزن
    st.header("إدارة المبيعات والطلب (عرض شبكي)")
    
    custs = pd.read_sql("SELECT * FROM customers", conn)
    cust_list = ["اختر العميل..."] + custs['name'].tolist() if not custs.empty else ["اختر العميل..."]
    sel_cust_name = st.selectbox("اختر العميل للفاتورة", cust_list)
    
    shop_name = "غير محدد"
    address = "غير محدد"
    phone = "غير محدد"
    
    if sel_cust_name != "اختر العميل...":
        cust_row = custs[custs['name'] == sel_cust_name]
        if not cust_row.empty:
            shop_name = cust_row.iloc[0].get('shop_name', 'غير محدد')
            address = cust_row.iloc[0].get('address', 'غير محدد')
            phone = cust_row.iloc[0].get('phone', 'غير محدد')
            st.success(f"📍 المحل: {shop_name} | الهاتف: {phone} | العنوان: {address}")

    prods = pd.read_sql("SELECT rowid, * FROM products", conn)
    cart = {}
    
    if not prods.empty:
        st.write("---")
        st.subheader("منتجات المخزن المتاحة:")
        cols = st.columns(3)
        for idx, row in prods.iterrows():
            with cols[idx % 3]:
                st.markdown(f"**{row['name']}**")
                st.text(f"السعر: {row['price_carton']} د.ع\nالمتبقي بالمخزن: {row['quantity']}")
                q = st.number_input(f"الكمية المطلوبة", min_value=0, max_value=int(row['quantity']) if row['quantity'] > 0 else 0, key=f"q_{idx}")
                if q > 0: 
                    cart[row['name']] = {'price': row['price_carton'], 'qty': q}
                st.divider()
                
    if cart and sel_cust_name != "اختر العميل...":
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🛒 إتمام البيع، خصم المخزن، وحفظ الفاتورة"):
                total_amt = sum(d['price'] * d['qty'] for d in cart.values())
                c.execute("INSERT INTO invoices (customer_name, shop_name, address, phone, items, total, date, payment_type) VALUES (?,?,?,?,?,?,?,?)", 
                          (sel_cust_name, shop_name, address, phone, str(cart), total_amt, str(date.today()), "نقد"))
                
                for item_name, data in cart.items():
                    sold_qty = data['qty']
                    c.execute("UPDATE products SET quantity = quantity - ? WHERE name = ?", (sold_qty, item_name))
                    
                conn.commit()
                st.success("✅ تمت العملية بنجاح! تم خصم الكميات من المخزن وحفظ الفاتورة.")
                st.rerun()
        with col_b2:
            if st.button("🗑️ تفريغ السلة"):
                st.rerun()

with tabs[1]: # الفواتير وتحميلها مع إمكانية الحذف
    st.header("سجل الفواتير وطباعتها بصيغة PDF")
    inv_df = pd.read_sql("SELECT rowid, * FROM invoices", conn)
    if inv_df.empty:
        st.info("لا توجد فواتير مسجلة حتى الآن.")
    else:
        for _, row in inv_df.iterrows():
            with st.expander(f"فاتورة رقم #{row['rowid']} | العميل: {row['customer_name']} | المحل: {row.get('shop_name', '')} | المجموع: {row['total']} د.ع"):
                items = ast.literal_eval(row['items'])
                st.table(pd.DataFrame(items).T)
                
                col_inv1, col_inv2 = st.columns(2)
                with col_inv1:
                    try:
                        pdf_data = generate_pdf(row, items)
                        st.download_button(
                            label="📥 تحميل الفاتورة PDF", 
                            data=pdf_data, 
                            file_name=f"invoice_{row['rowid']}.pdf",
                            mime="application/pdf",
                            key=f"dl_{row['rowid']}"
                        )
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                with col_inv2:
                    if st.button(f"🗑️ حذف الفاتورة #{row['rowid']}", key=f"del_inv_{row['rowid']}"):
                        c.execute("DELETE FROM invoices WHERE rowid = ?", (row['rowid'],))
                        conn.commit()
                        st.success(f"تم حذف الفاتورة رقم #{row['rowid']} بنجاح!")
                        st.rerun()

with tabs[2]: # المخزن والكميات
    st.header("إدارة المخزن والمواد")
    p_name = st.text_input("اسم المادة الجديدة")
    p_price = st.number_input("سعر الكارتون", min_value=0)
    p_qty = st.number_input("الكمية المتاحة", min_value=0)
    if st.button("إضافة مادة للمخزن"):
        if p_name:
            c.execute("INSERT INTO products VALUES (?,?,?)", (p_name, p_price, p_qty))
            conn.commit()
            st.success("تمت إضافة المادة بنجاح!")
            st.rerun()
            
    st.subheader("حالة المخزن الحالية:")
    prods_df = pd.read_sql("SELECT rowid, * FROM products", conn)
    if not prods_df.empty:
        for _, p_row in prods_df.iterrows():
            col_p1, col_p2 = st.columns([4, 1])
            with col_p1:
                st.text(f"المادة: {p_row['name']} | السعر: {p_row['price_carton']} د.ع | الكمية: {p_row['quantity']}")
            with col_p2:
                if st.button("حذف", key=f"del_prod_{p_row['rowid']}"):
                    c.execute("DELETE FROM products WHERE rowid = ?", (p_row['rowid'],))
                    conn.commit()
                    st.success("تم حذف المادة بنجاح!")
                    st.rerun()
    else:
        st.info("المخزن فارغ حالياً.")

with tabs[3]: # إدارة العملاء
    st.header("إدارة العملاء وتفاصيل المحلات")
    c_name = st.text_input("اسم العميل")
    c_shop = st.text_input("اسم المحل")
    c_phone = st.text_input("رقم الهاتف")
    c_address = st.text_input("عنوان المحل بالتفصيل")
    c_gov = st.selectbox("المحافظة", ["البصرة", "بغداد", "ذي قار", "ميسان", "البصرة - العشار", "البصرة - التنومة", "أخرى"])
    
    if st.button("حفظ العميل الجديد"):
        if c_name:
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", (c_name, c_shop, c_phone, c_address, c_gov))
            conn.commit()
            st.success("تم إضافة العميل بنجاح!")
            st.rerun()
            
    st.dataframe(pd.read_sql("SELECT rowid, * FROM customers", conn))

with tabs[4]: # المساعد الذكي المتطور (مع الجرد، إضافة وحذف مواد المخزن، وإحصائيات المبيعات)
    st.header("🤖 المساعد الذكي لإدارة النظام - أسعد نفسك بنفسك")
    st.markdown("مرحباً بك في لوحة تحكم المساعد الذكي. يمكنك من هنا إجراء جرد شامل، إضافة منتجات جديدة، وحذف المواد غير الضرورية مباشرةً.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📊 إحصائيات النظام العامة")
        prod_count = pd.read_sql("SELECT COUNT(*) FROM products", conn).iloc[0, 0]
        cust_count = pd.read_sql("SELECT COUNT(*) FROM customers", conn).iloc[0, 0]
        inv_count = pd.read_sql("SELECT COUNT(*) FROM invoices", conn).iloc[0, 0]
        total_sales = pd.read_sql("SELECT SUM(total) FROM invoices", conn).iloc[0, 0] or 0
        
        st.metric("عدد المواد في المخزن", prod_count)
        st.metric("عدد العملاء", cust_count)
        st.metric("إجمالي الفواتير المصدرة", inv_count)
        st.metric("إجمالي إيرادات المبيعات", f"{total_sales:,} د.ع")
        
    with col_b:
        st.subheader("⚡ تنبيهات النواقص")
        low_stock = pd.read_sql("SELECT name, quantity FROM products WHERE quantity <= 5", conn)
        if low_stock.empty:
            st.success("المخزن ممتاز، لا توجد نواقص خطيرة.")
        else:
            st.warning("تنبيه: المواد التالية قاربت على النفاذ:")
            st.dataframe(low_stock)

    st.write("---")
    st.subheader("📦 أدوات المخزن الذكية السريعة")
    
    # نموذج إضافة مادة سريعة من المساعد الذكي
    with st.expander("➕ إضافة مادة جديدة عبر المساعد الذكي"):
        ai_p_name = st.text_input("اسم المنتج الجديد", key="ai_p_name")
        ai_p_price = st.number_input("سعر الكارتون", min_value=0, key="ai_p_price")
        ai_p_qty = st.number_input("الكمية المتاحة", min_value=0, key="ai_p_qty")
        if st.button("إضافة للمخزن فوراً", key="ai_add_btn"):
            if ai_p_name:
                c.execute("INSERT INTO products VALUES (?,?,?)", (ai_p_name, ai_p_price, ai_p_qty))
                conn.commit()
                st.success(f"تمت إضافة المادة ({ai_p_name}) بنجاح للمخزن!")
                st.rerun()
            else:
                st.error("يرجى كتابة اسم المادة.")

    # جدول جرد المخزن مع أزرار الحذف السريع
    st.subheader("📋 جرد المخزن الشامل وإدارة الحذف")
    stock_df = pd.read_sql("SELECT rowid, * FROM products", conn)
    if not stock_df.empty:
        for _, s_row in stock_df.iterrows():
            col_s1, col_s2 = st.columns([4, 1])
            with col_s1:
                st.write(f"🔹 **{s_row['name']}** | السعر: {s_row['price_carton']} د.ع | المخزون: **{s_row['quantity']}**")
            with col_s2:
                if st.button("🗑️ حذف المادة", key=f"ai_del_prod_{s_row['rowid']}"):
                    c.execute("DELETE FROM products WHERE rowid = ?", (s_row['rowid'],))
                    conn.commit()
                    st.success(f"تم حذف المادة ({s_row['name']}) بنجاح!")
                    st.rerun()
    else:
        st.info("لا توجد مواد مسجلة في المخزن حالياً.")
