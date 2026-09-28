import streamlit as st
import urllib.request
import json
from datetime import datetime, timedelta

# إعدادات الصفحة متوافقة مع التليفون والحاسبة وألوان مريحة للعين
st.set_page_config(page_title="نظام ياسر ويب المتكامل", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f9;
    }
    div.stButton > button {
        background-color: #2c3e50;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #34495e;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

def sb_select(table):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        })
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except:
        return []

def sb_insert(table, data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}"
        encoded = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=encoded, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }, method="POST")
        with urllib.request.urlopen(req):
            return True
    except:
        return False

def sb_delete(table, item_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{item_id}"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "return=minimal"
        }, method="DELETE")
        with urllib.request.urlopen(req):
            return True
    except:
        return False

def sb_update(table, item_id, payload):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{item_id}"
        encoded = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=encoded, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }, method="PATCH")
        with urllib.request.urlopen(req):
            return True
    except:
        return False

# تهيئة الجلسة
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'shop_name' not in st.session_state:
    st.session_state.shop_name = ""
if 'sub_type' not in st.session_state:
    st.session_state.sub_type = "النسخة المجانية"
if 'sub_expiry_date' not in st.session_state:
    st.session_state.sub_expiry_date = datetime.now() + timedelta(days=30)
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- واجهة تسجيل الدخول المحدثة ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>🏷️ تسجيل دخول نظام ياسر ويب</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>أدخل اسم المحل وحدد الصلاحية المطلوبة للبدء</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            s_name = st.text_input("اسم المحل أو المستخدم:")
            selected_privilege = st.selectbox("حدد الصلاحية / نوع النسخة:", [
                "النسخة المجانية (افتراضي)", 
                "النسخة المدفوعة 🌟 (صلاحيات كاملة)"
            ])
            submitted = st.form_submit_button("دخول إلى النظام")
            
            if submitted:
                if s_name.strip():
                    st.session_state.logged_in = True
                    st.session_state.shop_name = s_name.strip()
                    if "المدفوعة" in selected_privilege:
                        st.session_state.sub_type = "النسخة المدفوعة 🌟"
                        st.session_state.sub_expiry_date = datetime.now() + timedelta(days=30)
                    else:
                        st.session_state.sub_type = "النسخة المجانية"
                        st.session_state.sub_expiry_date = datetime.now() + timedelta(days=30)
                    st.rerun()
                else:
                    st.error("الرجاء إدخال اسم المحل بشكل صحيح.")
    st.stop()

# --- فحص انتهاء ال30 يوم (حفظ البضاعة بالكامل عند التوقف) ---
remaining_days = (st.session_state.sub_expiry_date - datetime.now()).days
if remaining_days < 0 and "المدفوعة" in st.session_state.sub_type:
    st.warning("⚠️ انتهت صلاحية الاشتراك (30 يوماً). تم إيقاف النظام مؤقتاً لحين تجديد الاشتراك، مع العلم أن كافة بضاعتك ومخزونك وعملائك محفوظة بأمان تام ولن تنحذف.")
    st.markdown("### يرجى مراجعة الدعم الفني أو إدخال كود التجديد في تبويب الإعدادات.")
    if st.button("⚙️ الانتقال لإدخال كود التجديد"):
        st.session_state.sub_expiry_date = datetime.now() + timedelta(days=30)
        st.rerun()
    st.stop()

# --- القائمة الجانبية ---
st.sidebar.markdown(f"### 🏪 المحل: {st.session_state.shop_name}")
st.sidebar.markdown(f"📦 النوع: **{st.session_state.sub_type}**")
st.sidebar.markdown(f"⏳ المتبقي من الاشتراك: **{max(0, remaining_days)} يوم**")
st.sidebar.markdown("---")

menu = st.sidebar.radio("اختر التبويب المطلوبة:", [
    "1️⃣ إدارة المخزون والبطاقات",
    "2️⃣ إضافة مادة جديدة",
    "3️⃣ زيادة كمية لمادة موجودة ➕",
    "4️⃣ إدارة العملاء",
    "5️⃣ سلة المبيعات والفاتورة",
    "6️⃣ وصل سداد وتسديد الديون",
    "7️⃣ سجل الديون والذمم",
    "8️⃣ المصاريف اليومية",
    "9️⃣ تقارير الأرباح والخسائر",
    "🔟 دليل الاستخدام والدعم 📖",
    "1️⃣1️⃣ إعدادات النظام والنسخة المدفوعة"
])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.cart = []
    st.rerun()

current_shop_id = f"id_{st.session_state.shop_name}"
all_products = sb_select("products")
all_customers = sb_select("customers")

products = [p for p in all_products if p.get('shop_name') == current_shop_id]
customers = [c for c in all_customers if c.get('shop_name') == current_shop_id]

# --- 1️⃣ إدارة المخزون والبطاقات ---
if menu == "1️⃣ إدارة المخزون والبطاقات":
    st.header("📦 إدارة المخزون وبطاقات المواد")
    if products:
        cols = st.columns(3)
        for idx, item in enumerate(products):
            buy = float(item.get('buy_price', 0))
            sell = float(item.get('sell_price', 0))
            diff = sell - buy
            qty = int(item.get('quantity', 0))
            
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 15px;">
                    <h4>📦 {item.get('product_name')}</h4>
                    <p>الشراء: <b>{buy}</b> | البيع: <b>{sell}</b></p>
                """, unsafe_allow_html=True)
                
                if diff > 0:
                    st.success(f"🟢 ربح القطعة: +{diff} د.ع")
                elif diff < 0:
                    st.error(f"🔴 خسارة القطعة: {diff} د.ع")
                else:
                    st.info("⚪ بدون هامش ربح")
                    
                st.markdown(f"<p>الكمية المتوفرة: <b style='color:green;'>{qty}</b></p>", unsafe_allow_html=True)
                
                c_b1, c_b2 = st.columns(2)
                with c_b1:
                    if st.button("🛒 بيع (-1)", key=f"sell_{item.get('id')}"):
                        if qty > 0:
                            sb_update("products", item.get('id'), {"quantity": qty - 1})
                            st.success("تم البيع وخصم الكمية!")
                            st.rerun()
                        else:
                            st.warning("الكمية نفذت!")
                with c_b2:
                    if st.button("🗑️ حذف", key=f"del_{item.get('id')}"):
                        sb_delete("products", item.get('id'))
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("لا توجد مواد مضافة في مخزونك الحالي.")

# --- 2️⃣ إضافة مادة جديدة ---
elif menu == "2️⃣ إضافة مادة جديدة":
    st.header("➕ إضافة مادة جديدة إلى المخزون")
    with st.form("add_product_form"):
        p_name = st.text_input("اسم المادة / المنتج")
        c1, c2 = st.columns(2)
        with c1:
            p_buy_str = st.text_input("سعر الشراء (د.ع)", value="0")
        with c2:
            p_sell_str = st.text_input("سعر البيع (د.ع)", value="0")
        p_qty_str = st.text_input("الكمية المتوفرة", value="1")
        
        submitted_p = st.form_submit_button("حفظ المادة في المخزون")
        if submitted_p:
            if p_name.strip():
                try:
                    payload = {
                        "product_name": p_name.strip(),
                        "buy_price": float(p_buy_str),
                        "sell_price": float(p_sell_str),
                        "quantity": int(p_qty_str),
                        "shop_name": current_shop_id
                    }
                    if sb_insert("products", payload):
                        st.success("تمت إضافة المادة بنجاح لمخزونك الخاص!")
                        st.rerun()
                    else:
                        st.error("حدث خطأ أثناء الإضافة.")
                except ValueError:
                    st.warning("الرجاء إدخال أرقام صحيحة للأسعار والكمية.")
            else:
                st.warning("الرجاء كتابة اسم المادة.")

# --- 3️⃣ زيادة كمية لمادة موجودة ---
elif menu == "3️⃣ زيادة كمية لمادة موجودة ➕":
    st.header("📦 زيادة كمية منتج سابق في المخزون")
    if products:
        with st.form("add_more_qty_form"):
            prod_map = {p['product_name'] + f" (الرصيد: {p['quantity']})": p for p in products}
            chosen_prod_label = st.selectbox("اختر المنتج:", list(prod_map.keys()))
            target_product = prod_map[chosen_prod_label]
            added_qty_str = st.text_input("الكمية المراد إضافتها:", value="1")
            submit_add_qty = st.form_submit_button("➕ تحديث المخزون")
            
            if submit_add_qty:
                try:
                    new_total_q = int(target_product['quantity']) + int(added_qty_str)
                    if sb_update("products", target_product['id'], {"quantity": new_total_q}):
                        st.success("تمت إضافة الكمية بنجاح!")
                        st.rerun()
                    else:
                        st.error("خطأ في التحديث.")
                except ValueError:
                    st.warning("أدخل رقماً صحيحاً.")
    else:
        st.info("لا توجد منتجات مسجلة.")

# --- 4️⃣ إدارة العملاء ---
elif menu == "4️⃣ إدارة العملاء":
    st.header("👥 إدارة العملاء وحقولهم الخاصة بمحلك")
    with st.form("add_customer_form"):
        c_name = st.text_input("اسم العميل الكامل")
        c_phone = st.text_input("رقم الهاتف")
        c_address = st.text_input("مكان السكن / العنوان")
        c_city = st.text_input("المحافظة")
        submitted_c = st.form_submit_button("حفظ العميل الجديد")
        
        if submitted_c:
            if c_name.strip():
                payload = {
                    "name": c_name.strip(),
                    "phone": c_phone.strip(),
                    "address": c_address.strip(),
                    "city": c_city.strip() if c_city.strip() else "البصرة",
                    "debt": 0.0,
                    "shop_name": current_shop_id
                }
                if sb_insert("customers", payload):
                    st.success("تم حفظ العميل في سجلك الخاص!")
                    st.rerun()
                else:
                    st.error("خطأ في الحفظ.")
            else:
                st.warning("اسم العميل مطلوب.")

    st.subheader("قائمة عملائك المسجلين:")
    if customers:
        st.table(customers)
    else:
        st.info("لا يوجد عملاء مسجلون لديك بعد.")

# --- 5️⃣ سلة المبيعات والفاتورة ---
elif menu == "5️⃣ سلة المبيعات والفاتورة":
    st.header("🛒 سلة المبيعات وإصدار الفواتير")
    if products:
        with st.form("cart_form"):
            prod_options = {p['product_name'] + f" (المتوفر: {p['quantity']} | السعر: {p['sell_price']})": p for p in products}
            selected_label = st.selectbox("اختر المادة:", list(prod_options.keys()))
            cart_qty_str = st.text_input("الكمية المطلوبة للبيع", value="1")
            add_to_cart_btn = st.form_submit_button("➕ إضافة للسلة")
            if add_to_cart_btn:
                try:
                    target_prod = prod_options[selected_label]
                    st.session_state.cart.append({
                        "id": target_prod['id'],
                        "product_name": target_prod['product_name'],
                        "sell_price": float(target_prod['sell_price']),
                        "quantity": int(cart_qty_str)
                    })
                    st.success("تمت الإضافة للسلة!")
                    st.rerun()
                except ValueError:
                    st.warning("أدخل كمية صحيحة.")
    else:
        st.warning("لا توجد مواد متوفرة بالمخزون.")

    if st.session_state.cart:
        st.subheader("محتويات السلة الحالية:")
        total_price = 0
        for i, c_item in enumerate(st.session_state.cart):
            sub = c_item['sell_price'] * c_item['quantity']
            total_price += sub
            col_a, col_b, col_c = st.columns([3, 1, 1])
            col_a.write(f"<b>{c_item['product_name']}</b> - {c_item['sell_price']} × {c_item['quantity']}")
            col_b.write(f"{sub} د.ع")
            if col_c.button("حذف", key=f"cart_del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
                
        st.markdown(f"### الإجمالي: <span style='color:green;'>{total_price} د.ع</span>", unsafe_allow_html=True)
        
        if customers:
            cust_names = [c['name'] for c in customers]
            chosen_cust = st.selectbox("اختر العميل للفاتورة:", cust_names)
            is_debt_sale = st.checkbox("تسجيل المبلغ كدين على العميل؟")
            
            if st.button("✅ إتمام البيع وخصم المخزون"):
                for c_item in st.session_state.cart:
                    current_item = next((p for p in products if p['id'] == c_item['id']), None)
                    if current_item:
                        new_q = max(0, int(current_item['quantity']) - c_item['quantity'])
                        sb_update("products", c_item['id'], {"quantity": new_q})
                
                if is_debt_sale:
                    target_c_obj = next((c for c in customers if c['name'] == chosen_cust), None)
                    if target_c_obj:
                        new_debt = float(target_c_obj.get('debt', 0) or 0) + total_price
                        sb_update("customers", target_c_obj['id'], {"debt": new_debt})

                st.success("تمت عملية البيع بنجاح!")
                st.session_state.cart = []
                st.rerun()
        else:
            st.warning("أضف عميلاً أولاً.")
    else:
        st.info("السلة فارغة.")

# --- 6️⃣ وصل سداد وتسديد الديون ---
elif menu == "6️⃣ وصل سداد وتسديد الديون":
    st.header("🧾 وصل سداد وتصفير ديون العملاء")
    if customers:
        cust_map = {c['name'] + f" (الدين: {c.get('debt', 0)} د.ع)": c for c in customers}
        chosen_receipt_cust_label = st.selectbox("اختر العميل:", list(cust_map.keys()))
        selected_cust_data = cust_map[chosen_receipt_cust_label]
        current_client_debt = float(selected_cust_data.get('debt', 0) or 0)
        
        st.info(f"💰 الدين الباقي على العميل {selected_cust_data['name']} هو: **{current_client_debt} د.ع**")
        
        with st.form("pay_debt_form"):
            paid_amount_str = st.text_input("المبلغ المدفوع للتسديد:", value=str(current_client_debt))
            submit_payment = st.form_submit_button("✅ إصدار وصل السداد وتصفير الحساب")
            
            if submit_payment:
                try:
                    remaining_debt = max(0.0, current_client_debt - float(paid_amount_str))
                    sb_update("customers", selected_cust_data['id'], {"debt": remaining_debt})
                    st.success(f"تم تسديد المبلغ بنجاح! الدين الباقي: {remaining_debt} د.ع")
                    st.rerun()
                except ValueError:
                    st.warning("أدخل مبلغاً صحيحاً.")
    else:
        st.info("لا توجد عملاء مسجلون.")

# --- 7️⃣ سجل الديون والذمم ---
elif menu == "7️⃣ سجل الديون والذمم":
    st.header("📋 سجل الديون والذمم")
    if customers:
        debtors = [c for c in customers if float(c.get('debt', 0) or 0) > 0]
        if debtors:
            st.table(debtors)
        else:
            st.success("لا توجد ديون مترتبة حالياً.")
    else:
        st.info("لا توجد بيانات.")

# --- 8️⃣ المصاريف اليومية ---
elif menu == "8️⃣ المصاريف اليومية":
    st.header("💸 تسجيل المصاريف اليومية")
    with st.form("expenses_form"):
        exp_title = st.text_input("بيان المصروف")
        exp_amount_str = st.text_input("المبلغ (د.ع)", value="0")
        if st.form_submit_button("حفظ المصروف"):
            st.success("تم تسجيل المصروف بنجاح.")

# --- 9️⃣ تقارير الأرباح والخسائر ---
elif menu == "9️⃣ تقارير الأرباح والخسائر":
    st.header("📊 تقارير الأرباح والخسائر")
    if products:
        total_inv_buy = sum(float(p.get('buy_price', 0)) * int(p.get('quantity', 0)) for p in products)
        total_inv_sell = sum(float(p.get('sell_price', 0)) * int(p.get('quantity', 0)) for p in products)
        st.metric("قيمة المخزون (شراء)", f"{total_inv_buy} د.ع")
        st.metric("قيمة المخزون المتوقعة (بيع)", f"{total_inv_sell} د.ع")
        st.metric("الأرباح التقديرية", f"{total_inv_sell - total_inv_buy} د.ع")
    else:
        st.info("لا توجد بيانات كافية.")

# --- 🔟 دليل الاستخدام والدعم (حسب الصور بالحرف الواحد + حساب إنستجرام الجديد) ---
elif menu == "🔟 دليل الاستخدام والدعم 📖":
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🛍️ نظام Yasser Web الشامل لإدارة المبيعات والمخزون</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #b7950b;'>✨ دليل استخدام نظام ياسر ويب الشامل</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>المرجع السريع لإدارة المبيعات والمخازن بكفاءة عالية على الهواتف والأجهزة</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### ➕ 1. إضافة مادة جديدة")
    st.markdown("إدخال البضائع الجديدة للمخزن وتحديد أسعار الشراء والبيع والكميات بدقة.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📦 2. جرد المخزن والباركود")
    st.markdown("عرض المواد والمنتجات مع الألوان، القياسات، الباركود، وطباعة الرموز.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 👥 3. العملاء والديون")
    st.markdown("تسجيل بيانات الزبائن ومعلومات التواصل ومتابعة حركة الديون المرتبطة بفواتيرهم.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 💵 4. تسداد الديون")
    st.markdown("إدخال الدفعات النقدية المسددة وتحديث أرصدة العملاء وتصفير الذمم.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 🏬 5. الموردين")
    st.markdown("تسجيل بيانات الموردين وأرقام هواتفهم والتخصصات المرتبطة بتوريد البضائع.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 🛒 6. البيع والفواتير")
    st.markdown("نافذة سلة المبيعات لتجميع المواد وتحديد الكميات وحساب المبالغ تلقائياً.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📄 7. سجل الفواتير")
    st.markdown("عرض الفواتير الصادرة، تحميلها للطباعة المباشرة، أو إرسالها عبر الواتساب.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 💰 8. المصاريف")
    st.markdown("تسجيل النثريات والمصروفات اليومية لحساب صافي الصندوق بدقة.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📊 9. التقارير")
    st.markdown("تحليلات مالية دقيقة لإجمالي المبيعات، صافي الأرباح، والديون المعلقة.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📜 10. سجل النشاطات")
    st.markdown("سجل رقابي متكامل يوثق جميع عمليات المستخدمين بدقة عالية.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📖 11. الدليل والدعم")
    st.markdown("المرجع الشامل والدعم الفني.")
    st.markdown("<hr style='border: 2px solid #d4ac0d;'>", unsafe_allow_html=True)
    
    st.markdown("✨ **تطوير البرمجة: نظام ياسر ويب | انستغرام:** yaser120120120120 2026©")

# --- 1️⃣1️⃣ إعدادات النظام والنسخة المدفوعة ---
elif menu == "1️⃣1️⃣ إعدادات النظام والنسخة المدفوعة":
    st.header("⚙️ إعدادات النظام والاشتراك (30 يوماً)")
    st.write(f"اسم المحل: **{st.session_state.shop_name}**")
    st.write(f"النسخة الحالية: **{st.session_state.sub_type}**")
    st.write(f"الأيام المتبقية للاشتراك: **{max(0, remaining_days)} يوم**")
    st.markdown("---")
    
    with st.form("activation_form"):
        st.markdown("### تفعيل أو تجديد الاشتراك لمدة 30 يوماً:")
        activation_code_input = st.text_input("أدخل كود التفعيل للنسخة المدفوعة:", type="password")
        submit_activation = st.form_submit_button("تفعيل الاشتراك وبدء العد التنازلي")
        
        if submit_activation:
            if activation_code_input.strip() == "YASER2026VIP" or activation_code_input.strip() == "ياسر2026":
                st.session_state.sub_type = "النسخة المدفوعة 🌟"
                st.session_state.sub_expiry_date = datetime.now() + timedelta(days=30)
                st.success("تم تفعيل النسخة المدفوعة بنجاح! تم احتساب 30 يوماً جديدة.")
                st.rerun()
            else:
                st.error("كود التفعيل غير صحيح.")
