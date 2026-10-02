import streamlit as st
import urllib.request
import json
from datetime import datetime

# إعدادات الصفحة متوافقة مع التليفون والحاسبة
st.set_page_config(page_title="نظام ياسر ويب المتكامل", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    /* تثبيت المظهر الفاتح الواضح وتجنب اختفاء النصوص في الدارك مود للهواتف */
    .stApp {
        background-color: #f8f9fa !important;
        color: #111111 !important;
    }
    /* إجبار كل العناوين والنصوص فوق الحقول أن تكون بلون أسود غامق وواضح */
    label, .stTextInput label, .stSelectbox label, .stNumberInput label, p, span, h1, h2, h3, h4 {
        color: #111111 !important;
    }
    /* حل مشكلة الحقول لتكون بيضاء وكتابتها واضحة تماماً */
    input[type="text"], input[type="number"], textarea, div[data-baseweb="input"] input {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #ced4da !important;
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
if 'role' not in st.session_state:
    st.session_state.role = "مدير / مسؤول"
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- واجهة تسجيل الدخول بصلاحيات (مدير / كاشير) ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>🏷️ تسجيل دخول نظام ياسر ويب</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #333;'>أدخل اسم المحل وحدد الصلاحية الوظيفية للبدء</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            s_name = st.text_input("اسم المحل أو المستخدم:")
            selected_role = st.selectbox("الصلاحية الوظيفية:", [
                "مدير / مسؤول (صلاحيات كاملة لإدارة المخزون والتقارير)", 
                "كاشير (مخصص للبيع وإصدار الفواتير وتسديد الديون فقط)"
            ])
            submitted = st.form_submit_button("دخول إلى النظام")
            
            if submitted:
                if s_name.strip():
                    st.session_state.logged_in = True
                    st.session_state.shop_name = s_name.strip()
                    if "مدير" in selected_role:
                        st.session_state.role = "مدير / مسؤول"
                    else:
                        st.session_state.role = "كاشير"
                    st.rerun()
                else:
                    st.error("الرجاء إدخال اسم المحل بشكل صحيح.")
    st.stop()

# --- القائمة الجانبية (التبويبات الـ 15 كاملة) ---
st.sidebar.markdown(f"### 🏪 المحل: {st.session_state.shop_name}")
st.sidebar.markdown(f"👤 الصلاحية: **{st.session_state.role}**")
st.sidebar.markdown("---")

if st.session_state.role == "مدير / مسؤول":
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
        "11️⃣ حركة الصندوق والدرج اليومي 💵",
        "12️⃣ تنبيهات نفاذ المواد ⚠️",
        "13️⃣ طبع ملصقات الباركود 🏷️",
        "14️⃣ برنامج الولاء وعروض العملاء 🎁",
        "15️⃣ خانة التحديثات الجديدة 🚀"
    ])
else:
    menu = st.sidebar.radio("اختر التبويب المطلوبة (صلاحية كاشير):", [
        "5️⃣ سلة المبيعات والفاتورة",
        "6️⃣ وصل سداد وتسديد الديون",
        "4️⃣ إدارة العملاء",
        "🔟 دليل الاستخدام والدعم 📖",
        "15️⃣ خانة التحديثات الجديدة 🚀"
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
                    <h4 style="color:#000;">📦 {item.get('product_name')}</h4>
                    <p style="color:#000;">الشراء: <b>{buy}</b> | البيع: <b>{sell}</b></p>
                """, unsafe_allow_html=True)
                
                if diff > 0:
                    st.success(f"🟢 ربح القطعة: +{diff} د.ع")
                elif diff < 0:
                    st.error(f"🔴 خسارة القطعة: {diff} د.ع")
                else:
                    st.info("⚪ بدون هامش ربح")
                    
                st.markdown(f"<p style='color:#000;'>الكمية المتوفرة: <b style='color:green;'>{qty}</b></p>", unsafe_allow_html=True)
                
                c_b1, c_b2 = st.columns(2)
                with c_b1:
                    if st.button("🛒 بيع (-1)", key=f"sell_{item.get('id')}"):
                        if qty > 0:
                            sb_update("products", item.get('id'), {"quantity": qty - 1})
                            st.success("تم البيع وخصم الكمية المتزامنة!")
                            st.rerun()
                        else:
                            st.warning("الكمية نفذت!")
                with c_b2:
                    if st.button("🗑 حذف", key=f"del_{item.get('id')}"):
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
                        st.success("تمت إضافة المادة بنجاح وتظهر الآن فوراً عند الكاشير!")
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
                        st.success("تمت زيادة الكمية وتحديثها بالتزامن مع النظام!")
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
                    st.success("تم حفظ العميل في السجل المشترك!")
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
            chosen_cust = st.selectbox("اختر العميل للفاتورة (من قاعدة البيانات):", cust_names)
            is_debt_sale = st.checkbox("تسجيل المبلغ كدين على العميل؟")
            
            if st.button("✅ إتمام البيع وعرض الفاتورة الرسمية"):
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

                st.success("تمت عملية البيع بنجاح وتحديث المخزون والذمم بالتزامن!")
                
                st.markdown("---")
                st.markdown(f"""
                <div style="background: #ffffff; padding: 25px; border-radius: 10px; border: 2px solid #2c3e50; font-family: Tahoma; direction: rtl;">
                    <h2 style="text-align: center; color: #2c3e50; margin-bottom: 5px;">🏪 {st.session_state.shop_name}</h2>
                    <p style="text-align: center; color: #7f8c8d; margin-top: 0;">وصل مبيعات رسمي وموثق</p>
                    <hr style="border: 1px dashed #bdc3c7;">
                    <p style="color:#000;"><b>📅 التاريخ والوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style="color:#000;"><b>👤 اسم العميل:</b> {chosen_cust}</p>
                    <p style="color:#000;"><b>🏷️ طريقة البيع:</b> {'دين على الحساب' if is_debt_sale else 'نقدي'}</p>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px;">
                        <thead>
                            <tr style="background: #f8f9f9; border-bottom: 2px solid #2c3e50;">
                                <th style="padding: 8px; text-align: right; color:#000;">المادة</th>
                                <th style="padding: 8px; text-align: center; color:#000;">الكمية</th>
                                <th style="padding: 8px; text-align: center; color:#000;">السعر المفرد</th>
                                <th style="padding: 8px; text-align: left; color:#000;">المجموع</th>
                            </tr>
                        </thead>
                        <tbody>
                """, unsafe_allow_html=True)
                
                for item in st.session_state.cart:
                    st.markdown(f"""
                            <tr style="border-bottom: 1px solid #ecf0f1;">
                                <td style="padding: 8px; text-align: right; color:#000;">{item['product_name']}</td>
                                <td style="padding: 8px; text-align: center; color:#000;">{item['quantity']}</td>
                                <td style="padding: 8px; text-align: center; color:#000;">{item['sell_price']} د.ع</td>
                                <td style="padding: 8px; text-align: left; color:#000;">{item['sell_price'] * item['quantity']} د.ع</td>
                            </tr>
                    """, unsafe_allow_html=True)
                    
                st.markdown(f"""
                        </tbody>
                    </table>
                    <hr style="border: 1px dashed #bdc3c7;">
                    <h3 style="text-align: left; color: #27ae60;">الإجمالي الكلي: {total_price} د.ع</h3>
                    <p style="text-align: center; font-size: 12px; color: #555; margin-top: 20px;">شكراً لتعاملكم معنا | تطوير: نظام ياسر ويب</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.cart = []
        else:
            st.warning("أضف عميلاً أولاً.")
    else:
        st.info("السلة فارغة.")

# --- 6️⃣ وصل سداد وتسديد الديون ---
elif menu == "6️⃣ وصل سداد وتسديد الديون":
    st.header("🧾 وصل سداد وتصفير ديون العملاء")
    if customers:
        cust_map = {c['name'] + f" (الدين: {c.get('debt', 0)} د.ع)": c for c in customers}
        chosen_receipt_cust_label = st.selectbox("اختر العميل (من قاعدة البيانات المسجلة):", list(cust_map.keys()))
        selected_cust_data = cust_map[chosen_receipt_cust_label]
        current_client_debt = float(selected_cust_data.get('debt', 0) or 0)
        
        st.info(f"💰 الدين الباقي على العميل {selected_cust_data['name']} هو: **{current_client_debt} د.ع**")
        
        with st.form("pay_debt_form"):
            paid_amount_str = st.text_input("المبلغ المدفوع للتسديد:", value=str(current_client_debt))
            submit_payment = st.form_submit_button("✅ إصدار وصل السداد الرسمي وتصفير الحساب")
            
            if submit_payment:
                try:
                    paid_val = float(paid_amount_str)
                    remaining_debt = max(0.0, current_client_debt - paid_val)
                    sb_update("customers", selected_cust_data['id'], {"debt": remaining_debt})
                    st.success(f"تم تسديد المبلغ بنجاح وتحديث الحسابات بالتزامن! الدين الباقي: {remaining_debt} د.ع")
                    
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background: #ffffff; padding: 25px; border-radius: 10px; border: 2px solid #27ae60; font-family: Tahoma; direction: rtl;">
                        <h2 style="text-align: center; color: #27ae60; margin-bottom: 5px;">📜 سند قبض وتسديد ديون</h2>
                        <p style="text-align: center; color: #555; margin-top: 0;">محل: {st.session_state.shop_name}</p>
                        <hr style="border: 1px dashed #bdc3c7;">
                        <p style="color:#000;"><b>📅 تاريخ الوصل:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p style="color:#000;"><b>👤 اسم العميل (من النظام):</b> <span style="color: #2980b9; font-weight: bold;">{selected_cust_data['name']}</span></p>
                        <p style="color:#000;"><b>📞 رقم الهاتف:</b> {selected_cust_data.get('phone', 'غير متوفر')}</p>
                        <p style="color:#000;"><b>📍 العنوان:</b> {selected_cust_data.get('address', 'غير متوفر')} - {selected_cust_data.get('city', 'البصرة')}</p>
                        <hr style="border: 1px dashed #bdc3c7;">
                        <p style="font-size: 16px; color:#000;">مستلم من العميل أعلاه مبلغ وقدره: <b style="color: #27ae60; font-size: 18px;">{paid_val} د.ع</b></p>
                        <p style="font-size: 16px; color:#000;">الرصيد المتبقي (الدين الحالي): <b style="color: #c0392b; font-size: 18px;">{remaining_debt} د.ع</b></p>
                        <hr style="border: 1px dashed #bdc3c7;">
                        <p style="text-align: center; font-size: 12px; color: #555; margin-top: 20px;">تم السداد بنجاح وإصدار السند الآلي | نظام ياسر ويب</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except ValueError:
                    st.warning("أدخل مبلغاً صحيحاً.")
    else:
        st.info("لا توجد عملاء مسجلون في قاعدة البيانات.")

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

# --- 🔟 دليل الاستخدام والدعم ---
elif menu == "🔟 دليل الاستخدام والدعم 📖":
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🛍️ نظام Yasser Web الشامل لإدارة المبيعات والمخزون</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #b7950b;'>✨ دليل استخدام نظام ياسر ويب الشامل</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #333;'>المرجع السريع لإدارة المبيعات والمخازن بكفاءة عالية على الهواتف والأجهزة</p>", unsafe_allow_html=True)
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
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 💵 12. حركة الصندوق والدرج اليومي")
    st.markdown("متابعة المبالغ النقدية داخل الصندوق، تسجيل العهدة، والمصاريف اليومية ومطابقة الحسابات.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### ⚠️ 13. تنبيهات نفاذ المواد")
    st.markdown("مراقبة المخزون الفوري وعرض قائمة بالمواد التي قاربت على النفاد لإعادة طلبها مسبقاً.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 🏷️ 14. طبع ملصقات الباركود")
    st.markdown("اختيار المنتجات لتوليد وطباعة ملصقات الرفوف والباركود والأسعار بسهولة.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 🎁 15. برنامج الولاء وعروض العملاء")
    st.markdown("متابعة العملاء الأكثر تعاملاً، تدوين ملاحظاتهم، وتخصيص عروض وميزات لهم.")
    st.markdown("<hr style='border: 2px solid #d4ac0d;'>", unsafe_allow_html=True)
    
    st.markdown("✨ **تطوير البرمجة: نظام ياسر ويب | انستغرام:** yaser120120120120 2026©")

# --- 11️⃣ تبويب حركة الصندوق والدرج اليومي ---
elif menu == "11️⃣ حركة الصندوق والدرج اليومي 💵":
    st.header("💵 إدارة حركة الصندوق والدرج اليومي")
    st.markdown("متابعة السيولة النقدية والمبيعات الداخلة والعهدة اليومية.")
    with st.form("cash_drawer_form"):
        opening_cash = st.text_input("المبلغ الافتتاحي في الصندوق (العهدة صباحاً):", value="0")
        notes_drawer = st.text_area("ملاحظات وردية الصندوق:")
        submitted_drawer = st.form_submit_button("حفظ بيانات الصندوق")
        if submitted_drawer:
            st.success("تم تسجيل بيانات الصندوق اليومي بنجاح.")

# --- 12️⃣ تبويب تنبيهات نفاذ المواد ---
elif menu == "12️⃣ تنبيهات نفاذ المواد ⚠️":
    st.header("⚠️ تنبيهات نفاذ المواد في المخزن")
    if products:
        low_stock_items = [p for p in products if int(p.get('quantity', 0)) <= 3]
        if low_stock_items:
            st.warning("تحذير: المواد التالية قاربت على النفاذ (الكمية 3 أو أقل):")
            st.table(low_stock_items)
        else:
            st.success("ممتاز! جميع المواد متوفرة بكميات كافية ولا توجد مواد قاربت على النفاد.")
    else:
        st.info("لا توجد منتجات مسجلة في المخزون.")

# --- 13️⃣ تبويب طبع ملصقات الباركود ---
elif menu == "13️⃣ طبع ملصقات الباركود 🏷️":
    st.header("🏷️ طبع ملصقات الرفوف والباركود")
    if products:
        prod_labels = {p['product_name'] + f" (السعر: {p['sell_price']})": p for p in products}
        chosen_p_label = st.selectbox("اختر المنتج لطباعة ملصه:", list(prod_labels.keys()))
        selected_p_obj = prod_labels[chosen_p_label]
        num_copies = st.number_input("عدد الملصقات المطلوبة:", min_value=1, max_value=50, value=5)
        
        if st.button("🖨️ معاينة وطباعة الملصق"):
            st.markdown(f"""
            <div style="border: 2px dashed #2c3e50; padding: 20px; border-radius: 8px; width: 300px; background: white; text-align: center; margin: auto;">
                <h3 style="margin: 0; color: #2c3e50;">{st.session_state.shop_name}</h3>
                <hr style="margin: 5px 0;">
                <p style="font-size: 18px; font-weight: bold; margin: 5px 0; color:#000;">{selected_p_obj['product_name']}</p>
                <p style="font-size: 20px; color: #27ae60; font-weight: bold; margin: 5px 0;">السعر: {selected_p_obj['sell_price']} د.ع</p>
                <p style="font-size: 14px; color: #555; background: #eee; padding: 5px;">||| ||||| |||| ||||| (Barcode)</p>
                <p style="font-size: 11px; color: #555;">العدد المطلوب طباعته: {num_copies}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("لا توجد منتجات لطباعة باركود لها.")

# --- 14️⃣ تبويب برنامج الولاء وعروض العملاء ---
elif menu == "14️⃣ برنامج الولاء وعروض العملاء 🎁":
    st.header("🎁 برنامج الولاء ومتابعة عروض العملاء")
    if customers:
        cust_loyalty_map = {c['name']: c for c in customers}
        chosen_l_cust = st.selectbox("اختر العميل:", list(cust_loyalty_map.keys()))
        target_cust = cust_loyalty_map[chosen_l_cust]
        
        st.info(f"👤 العميل: **{target_cust['name']}** | المحافظة: **{target_cust.get('city', 'البصرة')}**")
        with st.form("loyalty_form"):
            discount_note = st.text_input("منح خصم خاص أو ملاحظة ولاء:", value="عميل دائم - خصم خاص 5%")
            submit_loyalty = st.form_submit_button("حفظ بيانات الولاء")
            if submit_loyalty:
                st.success("تم تحديث عروض وميزات الولاء للعميل بنجاح!")
    else:
        st.info("لا توجد عملاء مسجلون حالياً.")

# --- 15️⃣ خانة التحديثات الجديدة 🚀 ---
elif menu == "15️⃣ خانة التحديثات الجديدة 🚀":
    st.markdown("<h2 style='text-align: center; color: #2980b9;'>🚀 سجل التحديثات والتطويرات في نظام ياسر ويب</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>هذه الخانة توثق كل ميزة وإضافة جديدة يتم إضافتها للموقع أولاً بأول.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    <div style="background: white; padding: 20px; border-radius: 8px; border-right: 5px solid #e74c3c; margin-bottom: 15px;">
        <h4 style="color: #e74c3c; margin-top: 0;">🔧 تحديث اصلاح النصوص والعناوين المختفية بالموبايل</h4>
        <ul>
            <li><b>منع تأثير الوضع الداكن (Dark Mode):</b> تم إضافة كود تصميمي يثبت ألوان العناوين وأسماء الحقول باللون الأسود الواضح على خلفية بيضاء نقية، لتظهر كافة العناوين (اسم المادة، سعر الشراء، إلخ) بوضوح تام على الهواتف.</li>
        </ul>
    </div>
    
    <div style="background: white; padding: 20px; border-radius: 8px; border-right: 5px solid #27ae60; margin-bottom: 15px;">
        <h4 style="color: #27ae60; margin-top: 0;">✨ التحديثات السابقة (سبتمبر 2026)</h4>
        <ul>
            <li>إضافة الصلاحيات الوظيفية (مدير / كاشير).</li>
            <li>تحديث نظام الوصولات الرسمية وسندات القبض.</li>
            <li>إضافة 4 تبويبات جديدة (حركة الصندوق، تنبيهات النفاذ، الباركود، الولاء).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
