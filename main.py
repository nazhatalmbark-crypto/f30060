import streamlit as st
import urllib.request
import json

# إعدادات الصفحة لتكون متوافقة مع كل الأجهزة (تليفون وحاسبة) بدقة
st.set_page_config(page_title="نظام ياسر ويب المتكامل - 11 تبويب", page_icon="🛍️", layout="wide")

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

# دوال الاتصال بقاعدة البيانات
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

# تهيئة الجلسة (Session State)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'shop_name' not in st.session_state:
    st.session_state.shop_name = ""
if 'sub_type' not in st.session_state:
    st.session_state.sub_type = "النسخة المجانية"
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- واجهة تسجيل الدخول والاشتراكات ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>🏷️ تسجيل دخول نظام ياسر ويب</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>أدخل اسم المحل وسجل دخولك (تلقائياً تبدأ بالنسخة المجانية)</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            s_name = st.text_input("اسم المحل / المستخدم")
            vip_code = st.text_input("كود التفعيل (اختياري للتحويل إلى النسخة المدفوعة):", type="password")
            submitted = st.form_submit_button("دخول إلى النظام")
            
            if submitted:
                if s_name.strip():
                    st.session_state.logged_in = True
                    st.session_state.shop_name = s_name.strip()
                    # التحقق من كود النسخة المدفوعة (مثلاً الكود ياسر-مدفوع-2026)
                    if vip_code.strip() == "YASER2026VIP" or vip_code.strip() == "ياسر2026":
                        st.session_state.sub_type = "النسخة المدفوعة 🌟"
                    else:
                        st.session_state.sub_type = "النسخة المجانية"
                    st.rerun()
                else:
                    st.error("الرجاء إدخال اسم المحل بشكل صحيح.")
    st.stop()

# --- القائمة الجانبية (11 تبويب كاملة) ---
st.sidebar.markdown(f"### 🏪 المحل: {st.session_state.shop_name}")
st.sidebar.markdown(f"📦 النوع: **{st.session_state.sub_type}**")
st.sidebar.markdown("---")

menu = st.sidebar.radio("اختر التبويب المطلوبة (11 تبويب):", [
    "1️⃣ إدارة المخزون والبطاقات",
    "2️⃣ إضافة مادة جديدة",
    "3️⃣ إدارة العملاء",
    "4️⃣ سلة المبيعات والفاتورة",
    "5️⃣ وصل سداد وتسديد الديون",
    "6️⃣ سجل الديون والذمم",
    "7️⃣ المصاريف اليومية",
    "8️⃣ تقارير الأرباح والخسائر",
    "9️⃣ دليل الاستخدام وشرح التبويبات",
    "🔟 حساب إنستجرام والدعم",
    "1️⃣1️⃣ إعدادات النظام والنسخة المدفوعة"
])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.cart = []
    st.rerun()

# جلب البيانات من السيرفر
products = sb_select("products")
customers = sb_select("customers")

# --- 1️⃣ إدارة المخزون والبطاقات ---
if menu == "1️⃣ إدارة المخزون والبطاقات":
    st.header("📦 1. إدارة المخزون وبطاقات المواد")
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
        st.info("لا توجد مواد مضافة في المخزون حالياً.")

# --- 2️⃣ إضافة مادة جديدة ---
elif menu == "2️⃣ إضافة مادة جديدة":
    st.header("➕ 2. إضافة مادة جديدة إلى المخزون")
    with st.form("add_product_form"):
        p_name = st.text_input("اسم المادة / المنتج")
        c1, c2 = st.columns(2)
        with c1:
            p_buy = st.number_input("سعر الشراء (د.ع)", min_value=0.0, value=0.0, step=0.5)
        with c2:
            p_sell = st.number_input("سعر البيع (د.ع)", min_value=0.0, value=0.0, step=0.5)
        p_qty = st.number_input("الكمية المتوفرة", min_value=1, value=1)
        
        submitted_p = st.form_submit_button("حفظ المادة في المخزون (تحافظ على البضاعة)")
        if submitted_p:
            if p_name.strip():
                payload = {
                    "product_name": p_name.strip(),
                    "buy_price": p_buy,
                    "sell_price": p_sell,
                    "quantity": p_qty
                }
                if sb_insert("products", payload):
                    st.success("تمت إضافة المادة بنجاح دون المساس بباقي البضائع!")
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء الإضافة.")
            else:
                st.warning("الرجاء كتابة اسم المادة.")

# --- 3️⃣ إدارة العملاء ---
elif menu == "3️⃣ إدارة العملاء":
    st.header("👥 3. إدارة العملاء وحقولهم الكاملة")
    with st.form("add_customer_form"):
        c_name = st.text_input("اسم العميل الكامل")
        c_phone = st.text_input("رقم الهاتف")
        c_address = st.text_input("مكان السكن / العنوان الدقيق")
        c_city = st.text_input("المحافظة (مثلاً: البصرة، بغداد...)")
        submitted_c = st.form_submit_button("حفظ العميل الجديد")
        
        if submitted_c:
            if c_name.strip():
                payload = {
                    "name": c_name.strip(),
                    "phone": c_phone.strip(),
                    "address": c_address.strip(),
                    "city": c_city.strip() if c_city.strip() else "البصرة",
                    "debt": 0.0
                }
                if sb_insert("customers", payload):
                    st.success("تم حفظ بيانات العميل بنجاح!")
                    st.rerun()
                else:
                    st.error("خطأ في حفظ العميل.")
            else:
                st.warning("اسم العميل مطلوب.")

    st.subheader("قائمة العملاء المسجلين:")
    if customers:
        st.table(customers)
    else:
        st.info("لا يوجد عملاء مسجلين بعد.")

# --- 4️⃣ سلة المبيعات والفاتورة ---
elif menu == "4️⃣ سلة المبيعات والفاتورة":
    st.header("🛒 4. سلة المبيعات وإصدار الفواتير")
    if products:
        with st.form("cart_form"):
            prod_options = {p['product_name'] + f" (المتوفر: {p['quantity']} | السعر: {p['sell_price']})": p for p in products}
            selected_label = st.selectbox("اختر المادة المراد بيعها:", list(prod_options.keys()))
            cart_qty = st.number_input("الكمية المطلوبة", min_value=1, value=1)
            
            add_to_cart_btn = st.form_submit_button("➕ إضافة إلى السلة")
            if add_to_cart_btn:
                target_prod = prod_options[selected_label]
                st.session_state.cart.append({
                    "id": target_prod['id'],
                    "product_name": target_prod['product_name'],
                    "sell_price": float(target_prod['sell_price']),
                    "quantity": cart_qty
                })
                st.success("تمت الإضافة للسلة!")
                st.rerun()
    else:
        st.warning("لا توجد مواد متوفرة بالمخزون.")

    if st.session_state.cart:
        st.subheader("محتويات السلة الحالية:")
        total_price = 0
        for i, c_item in enumerate(st.session_state.cart):
            sub = c_item['sell_price'] * c_item['quantity']
            total_price += sub
            col_a, col_b, col_c = st.columns([3, 1, 1])
            col_a.write(f"<b>{c_item['product_name']}</b> - السعر: {c_item['sell_price']} × {c_item['quantity']}")
            col_b.write(f"المجموع: {sub} د.ع")
            if col_c.button("حذف", key=f"cart_del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
                
        st.markdown(f"### الإجمالي الكلي: <span style='color:green;'>{total_price} د.ع</span>", unsafe_allow_html=True)
        
        if customers:
            cust_names = [c['name'] for c in customers]
            chosen_cust = st.selectbox("اختر اسم العميل للفاتورة:", cust_names)
            is_debt_sale = st.checkbox("تسجيل المبلغ كدين على العميل؟")
            
            if st.button("✅ إتمام البيع وخصم الكميات فوراً"):
                success_checkout = True
                for c_item in st.session_state.cart:
                    p_id = c_item['id']
                    bought_q = c_item['quantity']
                    current_item = next((p for p in products if p['id'] == p_id), None)
                    if current_item:
                        new_q = max(0, int(current_item['quantity']) - bought_q)
                        if not sb_update("products", p_id, {"quantity": new_q}):
                            success_checkout = False
                
                # تحديث ديون العميل إذا اخترت بيع بالآجل
                if is_debt_sale:
                    target_c_obj = next((c for c in customers if c['name'] == chosen_cust), None)
                    if target_c_obj:
                        old_debt = float(target_c_obj.get('debt', 0)) if target_c_obj.get('debt') else 0.0
                        new_debt = old_debt + total_price
                        sb_update("customers", target_c_obj['id'], {"debt": new_debt})

                if success_checkout:
                    st.success(f"تمت عملية البيع بنجاح للعميل ({chosen_cust}) وتم الخصم من المخزون!")
                    st.session_state.cart = []
                    st.rerun()
                else:
                    st.error("خطأ أثناء خصم المواد.")
        else:
            st.warning("يرجى إضافة عميل أولاً من تبويب العملاء.")
    else:
        st.info("السلة فارغة.")

# --- 5️⃣ وصل سداد وتسديد الديون ---
elif menu == "5️⃣ وصل سداد وتسديد الديون":
    st.header("🧾 5. وصل سداد وتصفير ديون العملاء")
    st.markdown("اختر اسم العميل المسجل بالنظام لمعرفة الدين الباقي عليه وتسديده وتصفيره مباشرة:")
    
    if customers:
        cust_map = {c['name'] + f" (الهاتف: {c.get('phone', 'بدون')} | الدين الحالي: {c.get('debt', 0)} د.ع)": c for c in customers}
        chosen_receipt_cust_label = st.selectbox("اختر العميل:", list(cust_map.keys()))
        selected_cust_data = cust_map[chosen_receipt_cust_label]
        
        current_client_debt = float(selected_cust_data.get('debt', 0)) if selected_cust_data.get('debt') else 0.0
        st.info(f"💰 المبلغ الباقي (الدين المترتب) على العميل {selected_cust_data['name']} هو: **{current_client_debt} د.ع**")
        
        with st.form("pay_debt_form"):
            paid_amount = st.number_input("المبلغ المراد تسديده لتقليل أو تصفير الدين (د.ع):", min_value=0.0, value=current_client_debt, step=0.5)
            submit_payment = st.form_submit_button("✅ إصدار وصل السداد وتصفير الحساب")
            
            if submit_payment:
                remaining_debt = max(0.0, current_client_debt - paid_amount)
                # تحديث دين العميل في القاعدة
                if sb_update("customers", selected_cust_data['id'], {"debt": remaining_debt}):
                    st.success(f"تم إصدار وصل السداد بنجاح! تم تسديد مبلغ ({paid_amount} د.ع). الدين الباقي الآن: {remaining_debt} د.ع")
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء تحديث حساب العميل.")
    else:
        st.warning("لا توجد عملاء مسجلون حالياً لإصدار وصل سداد لهم.")

# --- 6️⃣ سجل الديون والذمم ---
elif menu == "6️⃣ سجل الديون والذمم":
    st.header("📋 6. سجل الديون والذمم المترتبة على العملاء")
    if customers:
        debtors = [c for c in customers if float(c.get('debt', 0)) > 0]
        if debtors:
            st.table(debtors)
        else:
            st.success("ممتاز! لا توجد أي ديون مترتبة على العملاء حالياً، جميع الحسابات مصفرة.")
    else:
        st.info("لا توجد بيانات عملاء.")

# --- 7️⃣ المصاريف اليومية ---
elif menu == "7️⃣ المصاريف اليومية":
    st.header("💸 7. تسجيل المصاريف اليومية للمحل")
    with st.form("expenses_form"):
        exp_title = st.text_input("بيان المصروف (مثلاً: أجور نقل، كهرباء، إيجار...)")
        exp_amount = st.number_input("المبلغ (د.ع)", min_value=0.0, value=0.0)
        exp_sub = st.form_submit_button("حفظ المصروف")
        if exp_sub:
            if exp_title.strip() and exp_amount > 0:
                st.success(f"تم تسجيل مصروف ({exp_title}) بقيمة {exp_amount} د.ع بنجاح.")
            else:
                st.warning("يرجى إدخال اسم المصروف والمبلغ بشكل صحيح.")
    st.info("سجل المصاريف يساعدك بمتابعة صافي أرباح المحل بدقة.")

# --- 8️⃣ تقارير الأرباح والخسائر ---
elif menu == "8️⃣ تقارير الأرباح والخسائر":
    st.header("📊 8. تقارير الأرباح والخسائر وحركة البضائع")
    if products:
        total_inv_buy = sum(float(p.get('buy_price', 0)) * int(p.get('quantity', 0)) for p in products)
        total_inv_sell = sum(float(p.get('sell_price', 0)) * int(p.get('quantity', 0)) for p in products)
        st.metric("إجمالي قيمة البضاعة بسعر الشراء", f"{total_inv_buy} د.ع")
        st.metric("إجمالي قيمة البضاعة المتوقعة بسعر البيع", f"{total_inv_sell} د.ع")
        st.metric("الأرباح التقديرية الكاملة للمخزون", f"{total_inv_sell - total_inv_buy} د.ع")
    else:
        st.info("لا توجد مواد كافية لاحتساب التقارير.")

# --- 9️⃣ دليل الاستخدام وشرح التبويبات ---
elif menu == "9️⃣ دليل الاستخدام وشرح التبويبات":
    st.header("📖 9. دليل الاستخدام الشامل لجميع تبويبات نظام ياسر ويب (11 تبويب)")
    st.markdown("""
    أهلاً بك يا ياسر في الدليل المرتب لكل تبويبات النظام:
    1. **إدارة المخزون والبطاقات:** لعرض المواد والربح والخسارة والبيع السريع.
    2. **إضافة مادة جديدة:** لإدخال المنتجات وحفظها دون ضياع البضاعة السابقة.
    3. **إدارة العملاء:** تسجيل الاسم، الهاتف، العنوان، والمحافظة.
    4. **سلة المبيعات والفاتورة:** لتجميع المنتجات والخصم التلقائي من المخزون مع خيار تسجيل الدين.
    5. **وصل سداد وتسديد الديون:** تختار العميل فيظهر لك دينه الباقي وتكتب مبلغ التسديد ليتم تصفير حسابه بدقة.
    6. **سجل الديون والذمم:** لمتابعة من عليه مبالغ مالية للمحل.
    7. **المصاريف اليومية:** لتسجيل الصرفيات.
    8. **تقارير الأرباح والخسائر:** حساب قيمة رأس المال والأرباح.
    9. **دليل الاستخدام:** هذا الشرح التفصيلي.
    10. **حساب إنستجرام والدعم:** روابط التواصل الاجتماعي.
    11. **إعدادات النظام:** لمعرفة تفاصيل نسختك والمحفظة.
    """)

# --- 🔟 حساب إنستجرام والدعم ---
elif menu == "🔟 حساب إنستجرام والدعم":
    st.header("📸 10. حساب إنستجرام والتواصل")
    st.markdown("يمكنك متابعة أعمال وتحديثات نظام ياسر ويب عبر المنصات الرسمية:")
    st.markdown("- **حساب إنستجرام الرسمي:** [اضغط هنا للمتابعة على إنستجرام](https://instagram.com)")
    st.markdown("- **نظام ياسر ويب المتكامل:** مخصص لإدارة المبيعات والمخازن بكفاءة عالية 2026.")

# --- 1️⃣1️⃣ إعدادات النظام والنسخة المدفوعة ---
elif menu == "1️⃣1️⃣ إعدادات النظام والنسخة المدفوعة":
    st.header("⚙️ 11. إعدادات النظام وحالة الاشتراك")
    st.write(f"اسم المحل المسجل: **{st.session_state.shop_name}**")
    st.write(f"نوع النسخة الحالية: **{st.session_state.sub_type}**")
    st.markdown("---")
    st.markdown("إذا كنت تمتلك كود التفعيل الخاص بالنسخة المدفوعة، يمكنك إعادة تسجيل الدخول وإدخاله في خانة التفعيل مع الحفاظ على كافة بضاعتك ومخزونك وقاعدة بياناتك سليمة وآمنة 100%.")
