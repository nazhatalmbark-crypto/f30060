import streamlit as st
import sqlite3
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="Yasser Web - Complete System", layout="wide")

# --- 1. إعداد قاعدة البيانات (أعداد صحيحة بدون بوينتات) ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, shop_location TEXT, governorate TEXT, landmark TEXT)''')
    
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
    except sqlite3.IntegrityError:
        pass
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

# --- 2. إدارة الجلسة والسلة ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False
if 'cart' not in st.session_state: st.session_state.cart = []

# --- 3. تسجيل الدخول أو إنشاء حساب ---
if not st.session_state.logged_in:
    st.title("⚡ ياسر ويب - نظام إدارة المحلات والأرباح")
    choice = st.radio("اختر العملية:", ["تسجيل دخول", "إنشاء حساب جديد"])
    
    if choice == "تسجيل دخول":
        st.subheader("🔐 تسجيل الدخول")
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                user = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username.strip(), password), fetch=True)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error("خطأ في اسم المستخدم أو كلمة المرور.")
    else:
        st.subheader("📝 إنشاء حساب جديد")
        with st.form("signup_form"):
            new_user = st.text_input("اسم مستخدم جديد")
            new_pass = st.text_input("كلمة مرور جديدة", type="password")
            if st.form_submit_button("إنشاء الحساب"):
                if new_user and new_pass:
                    try:
                        run_query("INSERT INTO users (username, password) VALUES (?, ?)", (new_user.strip(), new_pass))
                        st.success("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
                    except sqlite3.IntegrityError:
                        st.error("اسم المستخدم موجود مسبقاً.")
                else:
                    st.error("الرجاء ملء جميع الحقول.")
else:
    # --- الشريط الجانبي ---
    st.sidebar.write(f"المستخدم: **{st.session_state.username}**")
    st.sidebar.divider()
    
    st.sidebar.subheader("🔐 حالة النسخة")
    if not st.session_state.is_unlocked:
        st.sidebar.warning("النسخة حالياً تجريبية")
    else:
        st.sidebar.success("✅ النسخة الكاملة مفعلة")
        if st.sidebar.button("إيقاف التفعيل"):
            st.session_state.is_unlocked = False
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.cart = []
        st.rerun()

    st.title("📦 ياسر ويب - نظام إدارة المخزون والفواتير")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ إضافة مادة", "👥 العملاء", "📦 شبكة المواد", "📊 التقارير والأرباح", "🧾 سلة المشتريات والفواتير"
    ])

    # --- تبويب 1: إضافة مادة (أعداد صحيحة حصراً) ---
    with tab1:
        st.subheader("إضافة أو تحديث مادة (أعداد صحيحة بدون بوينتات)")
        with st.form("add_item_form"):
            name = st.text_input("اسم المادة").strip()
            qty = st.number_input("الكمية (عدد صحيح)", min_value=1, value=1, step=1, format="%d")
            price = st.number_input("السعر بالدينار (عدد صحيح)", min_value=0, value=1000, step=250, format="%d")
            
            if st.form_submit_button("حفظ المادة"):
                if not st.session_state.is_unlocked and qty > 100:
                    st.error("⚠️ النسخة المجانية تسمح بحد أقصى 100 لكل إدخال!")
                elif name:
                    existing = run_query("SELECT id, quantity FROM inventory WHERE name = ?", (name,), fetch=True)
                    if existing:
                        item_id, current_qty = existing[0]
                        new_qty = current_qty + qty
                        run_query("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (new_qty, price, item_id))
                        st.success(f"تم تحديث مادة '{name}' بنجاح! الكمية الجديدة: {new_qty}")
                    else:
                        run_query("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
                        st.success(f"تم إضافة مادة '{name}' بنجاح!")
                else:
                    st.error("الرجاء إدخال اسم المادة.")

    # --- تبويب 2: العملاء ---
    with tab2:
        st.subheader("إدارة العملاء")
        with st.form("add_cust"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("اسم العميل")
                p = st.text_input("رقم الهاتف")
                g = st.text_input("المحافظة")
            with c2:
                s = st.text_input("مكان المحل")
                l = st.text_input("أقرب نقطة دالة")
            if st.form_submit_button("حفظ بيانات العميل"):
                if n:
                    run_query("INSERT INTO customers (name, phone, shop_location, governorate, landmark) VALUES (?, ?, ?, ?, ?)", (n, p, s, g, l))
                    st.success("تم حفظ العميل بنجاح!")
                else:
                    st.error("أدخل اسم العميل على الأقل.")
        
        st.divider()
        customers = run_query("SELECT name, phone, shop_location, governorate, landmark FROM customers", fetch=True)
        if customers:
            for c in customers:
                st.write(f"- 👤 **{c[0]}** | 📱 الهاتف: {c[1] or 'لا يوجد'} | 📍 المحل: {c[2] or 'لا يوجد'} | 🏛️ المحافظة: {c[3] or 'لا يوجد'} | 🚩 نقطة دالة: {c[4] or 'لا توجد'}")

    # --- تبويب 3: شبكة المواد ---
    with tab3:
        st.subheader("شبكة المواد الحالية")
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        if items:
            cols = st.columns(3)
            for index, item in enumerate(items):
                item_id, name, quantity, price = item
                with cols[index % 3]:
                    with st.container(border=True):
                        st.markdown(f"### 📦 {name}")
                        st.metric("الكمية المتاحة", quantity)
                        st.metric("السعر", f"{price:,} د.ع")
                        st.write(f"**القيمة الكلية**: {(quantity * price):,} د.ع")
                        
                        if st.button("حذف المادة ❌", key=f"del_{item_id}"):
                            run_query("DELETE FROM inventory WHERE id = ?", (item_id,))
                            st.rerun()
        else:
            st.info("المخزن فارغ حالياً.")

    # --- تبويب 4: التقارير (مع قفل الرمز) ---
    with tab4:
        st.subheader("📊 تقارير الأرباح والمبيعات")
        
        if not st.session_state.is_unlocked:
            st.warning("🔒 **تقارير الأرباح المتقدمة وتصدير ملفات Excel مقفلة في النسخة التجريبية**")
            code_input = st.text_input("أدخل رمز التفعيل لفتح التقارير (رمز التفعيل: 2009):", type="password")
            if st.button("تفعيل التقارير"):
                if code_input == "2009":
                    st.session_state.is_unlocked = True
                    st.success("تم تفعيل النسخة الكاملة بنجاح!")
                    st.rerun()
                else:
                    st.error("رمز التفعيل غير صحيح!")
        else:
            st.success("✅ النسخة الكاملة مفعلة وتعمل بكامل طاقتها!")
            items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
            if items:
                total_unique = len(items)
                total_quantity = sum([it[2] for it in items])
                total_capital = sum([it[2] * it[3] for it in items])
                
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("إجمالي المواد المختلفة", total_unique)
                col_r2.metric("إجمالي الكمية بالمخزن", total_quantity)
                col_r3.metric("إجمالي قيمة المخزن", f"{total_capital:,} د.ع")
                
                st.divider()
                chart_data = {it[1]: it[2] * it[3] for it in items}
                st.bar_chart(chart_data)

    # --- تبويب 5: سلة المشتريات والفواتير المتكاملة ---
    with tab5:
        st.subheader("🧾 سلة المشتريات وإتمام الفاتورة")
        items = run_query("SELECT id, name, quantity, price FROM inventory", fetch=True)
        if items:
            item_names = [it[1] for it in items]
            
            c_add1, c_add2, c_add3 = st.columns([2, 1, 1])
            with c_add1:
                selected_item = st.selectbox("اختر المادة للإضافة للسلة", item_names)
            
            curr_item_data = run_query("SELECT quantity, price FROM inventory WHERE name = ?", (selected_item,), fetch=True)
            avail_qty = curr_item_data[0][0] if curr_item_data else 0
            item_price = curr_item_data[0][1] if curr_item_data else 0
            
            with c_add2:
                cart_qty = st.number_input("الكمية", min_value=1, max_value=max(1, avail_qty), step=1, format="%d")
            with c_add3:
                st.write(f"المتوفر: {avail_qty}")
                if st.button("➕ إضافة للسلة"):
                    found = False
                    for idx, cart_item in enumerate(st.session_state.cart):
                        if cart_item['name'] == selected_item:
                            new_q = cart_item['qty'] + cart_qty
                            if new_q <= avail_qty:
                                st.session_state.cart[idx]['qty'] = new_q
                                st.session_state.cart[idx]['total'] = new_q * item_price
                                st.success("تم تحديث الكمية في السلة!")
                            else:
                                st.error("الكمية المطلوبة تتجاوز المخزون!")
                            found = True
                            break
                    if not found:
                        if cart_qty <= avail_qty:
                            st.session_state.cart.append({
                                'name': selected_item,
                                'qty': cart_qty,
                                'price': item_price,
                                'total': cart_qty * item_price
                            })
                            st.success("تمت الإضافة للسلة!")
                        else:
                            st.error("الكمية تتجاوز المخزون المتوفر!")
            
            st.divider()
            st.subheader("🛒 محتويات السلة الحالية")
            if st.session_state.cart:
                grand_total = 0
                for i, cart_item in enumerate(st.session_state.cart):
                    row_c1, row_c2, row_c3, row_c4 = st.columns([3, 2, 2, 1])
                    row_c1.write(f"**{cart_item['name']}**")
                    row_c2.write(f"الكمية: {cart_item['qty']}")
                    row_c3.write(f"المبلغ: {cart_item['total']:,} د.ع")
                    grand_total += cart_item['total']
                    if row_c4.button("حذف", key=f"del_cart_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                
                st.markdown(f"### 💰 الإجمالي الكلي: `{grand_total:,} د.ع`")
                st.divider()
                
                # اختيار العميل للفاتورة
                cust_data = run_query("SELECT name FROM customers", fetch=True)
                cust_names = [c[0] for c in cust_data] if cust_data else ["عميل نقدي (عام)"]
                if "عميل نقدي (عام)" not in cust_names:
                    cust_names.insert(0, "عميل نقدي (عام)")
                
                selected_cust = st.selectbox("اختر العميل للفاتورة", cust_names)
                
                if st.button("✅ إتمام عملية البيع وقص المواد من المخزن"):
                    success_checkout = True
                    for cart_item in st.session_state.cart:
                        db_check = run_query("SELECT quantity FROM inventory WHERE name = ?", (cart_item['name'],), fetch=True)
                        if db_check and db_check[0][0] >= cart_item['qty']:
                            new_stock = db_check[0][0] - cart_item['qty']
                            run_query("UPDATE inventory SET quantity = ? WHERE name = ?", (new_stock, cart_item['name']))
                        else:
                            success_checkout = False
                            st.error(f"فشل قص المادة '{cart_item['name']}' لعدم كفاية المخزون!")
                    
                    if success_checkout:
                        invoice_text = f"""
=====================================
          YASSER WEB INVOICE
=====================================
التاريخ: {date.today()}
المستخدم: {st.session_state.username}
العميل: {selected_cust}
-------------------------------------
"""
                        for cart_item in st.session_state.cart:
                            invoice_text += f"- {cart_item['name']} | الكمية: {cart_item['qty']} | السعر: {cart_item['price']:,} | المجموع: {cart_item['total']:,}\n"
                        
                        invoice_text += f"""-------------------------------------
الإجمالي الكلي: {grand_total:,} د.ع
=====================================
تابع الحساب اسهل الطرق لإداره محلك
"""
                        st.success("تم إتمام عملية البيع وقص المواد من المخزن بنجاح!")
                        st.text(invoice_text)
                        st.download_button(
                            label="📥 تحميل الفاتورة (ملف نصي TXT)",
                            data=invoice_text,
                            file_name=f"invoice_{date.today()}.txt",
                            mime="text/plain"
                        )
                        st.session_state.cart = []
            else:
                st.info("السلة فارغة حالياً. قم بإضافة مواد لإنشاء الفاتورة.")
        else:
            st.info("المخزن فارغ، لا يمكن إنشاء سلة أو فاتورة.")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>تابع الحساب اسهل الطرق لإداره محلك | ياسر ويب (yasser17781)</p>", unsafe_allow_html=True)
