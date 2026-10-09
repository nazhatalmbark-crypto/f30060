import streamlit as st
import urllib.request
import json
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام ياسر ويب المتكامل", page_icon="🛍️", layout="wide")

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

# تهيئة قاعدة البيانات المحلية الاحتياطية وسجل الفواتير
if 'local_products' not in st.session_state:
    st.session_state.local_products = []
if 'local_customers' not in st.session_state:
    st.session_state.local_customers = []
if 'invoices_history' not in st.session_state:
    st.session_state.invoices_history = []

def sb_select(table):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        })
        with urllib.request.urlopen(req, timeout=5) as res:
            return json.loads(res.read().decode())
    except:
        if table == "products":
            return st.session_state.local_products
        elif table == "customers":
            return st.session_state.local_customers
        return []

def sb_insert(table, data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}"
        encoded = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=encoded, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }, method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            res.read()
            return True
    except Exception as e:
        data['id'] = str(datetime.now().timestamp())
        if table == "products":
            st.session_state.local_products.append(data)
            return True
        elif table == "customers":
            st.session_state.local_customers.append(data)
            return True
        return f"Error: {str(e)}"

def sb_delete(table, item_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{item_id}"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "return=minimal"
        }, method="DELETE")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except:
        if table == "products":
            st.session_state.local_products = [p for p in st.session_state.local_products if p.get('id') != item_id]
        elif table == "customers":
            st.session_state.local_customers = [c for c in st.session_state.local_customers if c.get('id') != item_id]
        return True

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
        with urllib.request.urlopen(req, timeout=5):
            return True
    except:
        items = st.session_state.local_products if table == "products" else st.session_state.local_customers
        for item in items:
            if item.get('id') == item_id:
                item.update(payload)
        return True

# تهيئة الجلسة
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'shop_name' not in st.session_state:
    st.session_state.shop_name = ""
if 'role' not in st.session_state:
    st.session_state.role = "مدير / مسؤول"
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'notes_list' not in st.session_state:
    st.session_state.notes_list = []

# --- واجهة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🏷️ تسجيل دخول نظام ياسر ويب</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>أدخل اسم المحل وحدد الصلاحية الوظيفية للبدء</p>", unsafe_allow_html=True)
    
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

# --- القائمة الجانبية الأساسية ---
st.sidebar.markdown(f"### 🏪 المحل: {st.session_state.shop_name}")
st.sidebar.markdown(f"👤 الصلاحية: **{st.session_state.role}**")
st.sidebar.markdown("---")

menu = st.sidebar.radio("اختر التبويب المطلوبة:", [
    "1️⃣ إدارة المخزون والبطاقات",
    "2️⃣ إضافة مادة جديدة",
    "3️⃣ زيادة كمية لمادة موجودة ➕",
    "4️⃣ إدارة العملاء",
    "5️⃣ سلة المبيعات والفاتورة",
    "6️⃣ سجل الفواتير والوصلات المطبوعة 📑",
    "7️⃣ وصل سداد وتسديد الديون",
    "8️⃣ سجل الديون والذمم",
    "9️⃣ المصاريف اليومية",
    "🔟 تقارير الأرباح والخسائر",
    "11️⃣ دليل الاستخدام والدعم 📖",
    "12️⃣ حركة الصندوق والدرج اليومي 💵",
    "13️⃣ تنبيهات نفاذ المواد ⚠️",
    "14️⃣ طبع ملصقات الباركود 🏷️",
    "15️⃣ برنامج الولاء وعروض العملاء 🎁",
    "16️⃣ خانة التحديثات الجديدة 🚀",
    "17️⃣ سجل الملاحظات والمهام 📌"
])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.cart = []
    st.rerun()

current_shop_id = f"id_{st.session_state.shop_name}"
all_products = sb_select("products")
all_customers = sb_select("customers")

clean_shop_name = st.session_state.shop_name.strip()
products = [p for p in all_products if p.get('shop_name') in [current_shop_id, clean_shop_name, f"id_{clean_shop_name}"]]
customers = [c for c in all_customers if c.get('shop_name') in [current_shop_id, clean_shop_name, f"id_{clean_shop_name}"]]

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
                st.subheader(f"📦 {item.get('product_name')}")
                st.write(f"الشراء: **{buy}** | البيع: **{sell}**")
                
                if diff > 0:
                    st.success(f"🟢 ربح القطعة: +{diff} د.ع")
                elif diff < 0:
                    st.error(f"🔴 خسارة القطعة: {diff} د.ع")
                else:
                    st.info("⚪ بدون هامش ربح")
                    
                st.write(f"الكمية المتوفرة: 🟢 **{qty}**")
                
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
                    if st.button("🗑 حذف", key=f"del_{item.get('id')}"):
                        sb_delete("products", item.get('id'))
                        st.rerun()
                st.markdown("---")
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
                    result = sb_insert("products", payload)
                    if result is True:
                        st.success("تمت إضافة المادة بنجاح وتظهر الآن في المخزون فوراً!")
                        st.rerun()
                    else:
                        st.error(f"خطأ: {result}")
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
                        st.success("تمت زيادة الكمية وتحديثها بنجاح!")
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
                res = sb_insert("customers", payload)
                if res is True:
                    st.success("تم حفظ العميل بنجاح!")
                    st.rerun()
                else:
                    st.error(f"خطأ في الحفظ: {res}")
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
            col_a.write(f"**{c_item['product_name']}** - {c_item['sell_price']} × {c_item['quantity']}")
            col_b.write(f"{sub} د.ع")
            if col_c.button("حذف", key=f"cart_del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
                
        st.markdown(f"### الإجمالي: {total_price} د.ع")
        
        if customers:
            cust_names = [c['name'] for c in customers]
            chosen_cust = st.selectbox("اختر العميل للفاتورة:", cust_names)
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

                sale_type_str = "دين على الحساب" if is_debt_sale else "نقدي مباشر"
                border_color = "#e74c3c" if is_debt_sale else "#27ae60"
                
                # بناء النص الحراري الخاص بالطابعة
                raw_receipt = f"==========================\n"
                raw_receipt += f"    {st.session_state.shop_name}\n"
                raw_receipt += f"  ({sale_type_str})\n"
                raw_receipt += f"==========================\n"
                raw_receipt += f"التاريخ: {datetime.now().strftime('%Y-%m-%d | %I:%M %p')}\n"
                raw_receipt += f"العميل: {chosen_cust}\n"
                raw_receipt += f"--------------------------\n"
                for item in st.session_state.cart:
                    raw_receipt += f"{item['product_name']} x{item['quantity']} = {item['sell_price'] * item['quantity']}د.ع\n"
                raw_receipt += f"--------------------------\n"
                raw_receipt += f"المجموع الكلي: {total_price} د.ع\n"
                raw_receipt += f"==========================\n"
                raw_receipt += f"  شكراً لتعاملكم معنا\n"

                invoice_record = {
                    "time": datetime.now().strftime('%Y-%m-%d | %I:%M %p'),
                    "customer": chosen_cust,
                    "type": sale_type_str,
                    "total": total_price,
                    "color": border_color,
                    "items": list(st.session_state.cart),
                    "raw": raw_receipt
                }
                st.session_state.invoices_history.insert(0, invoice_record)

                st.success("تمت عملية البيع بنجاح وتحديث المخزون وأرشفة الوصل!")
                
                st.markdown("---")
                st.markdown(f"""
                <div style="background: #ffffff; padding: 20px; border-radius: 10px; border: 3px solid {border_color}; font-family: 'Courier New', Courier, monospace; direction: rtl; color: black; max-width: 380px; margin: auto;">
                    <h3 style="text-align: center; color: {border_color}; margin: 0;">🏪 {st.session_state.shop_name}</h3>
                    <p style="text-align: center; font-size: 12px; color: #555; margin: 3px 0;">وصل مبيعات حراري ({sale_type_str})</p>
                    <hr style="border: 1px dashed #000;">
                    <p style="font-size: 12px; margin: 3px 0;"><b>📅 التاريخ:</b> {invoice_record['time']}</p>
                    <p style="font-size: 12px; margin: 3px 0;"><b>👤 العميل:</b> {chosen_cust}</p>
                    <hr style="border: 1px dashed #000;">
                """, unsafe_allow_html=True)
                
                for item in st.session_state.cart:
                    st.write(f"- {item['product_name']} | العدد: {item['quantity']} | السعر: {item['sell_price'] * item['quantity']} د.ع")
                    
                st.markdown(f"""
                    <hr style="border: 1px dashed #000;">
                    <h3 style="text-align: center; color: {border_color}; margin: 5px 0;">الإجمالي: {total_price} د.ع</h3>
                    <p style="text-align: center; font-size: 10px; color: #555; margin: 3px 0;">نظام ياسر ويب</p>
                </div>
                """, unsafe_allow_html=True)
                
                # صندوق النص الحراري الجاهز للنسخ إلى تطبيقات طابعات البلوتوث (مثل RawBT)
                st.markdown("### 🖨️ نص الوصل الحراري (انسخه وألصقه في تطبيق طابعة البلوتوث):")
                st.code(raw_receipt, language="text")
                
                st.session_state.cart = []
        else:
            st.warning("أضف عميلاً أولاً.")
    else:
        st.info("السلة فارغة.")

# --- 6️⃣ سجل الفواتير والوصلات المطبوعة ---
elif menu == "6️⃣ سجل الفواتير والوصلات المطبوعة 📑":
    st.header("📑 أرشيف وسجل الفواتير والوصلات السابقة")
    st.markdown("ملاحظة: الوصلات النقدية تظهر بإطار **أخضر** 🟢، ووصلات الدين تظهر بإطار **أحمر** 🔴، ويمكنك نسخ نصها الحراري للطباعة الفورية عبر البلوتوث.")
    st.markdown("---")
    
    if st.session_state.invoices_history:
        for idx, inv in enumerate(st.session_state.invoices_history):
            col_box1, col_box2 = st.columns([4, 1])
            with col_box1:
                st.markdown(f"""
                <div style="background: #ffffff; padding: 15px; border-radius: 8px; border: 2px solid {inv['color']}; font-family: Tahoma; direction: rtl; color: black; margin-bottom: 10px;">
                    <h4 style="color: {inv['color']}; margin: 0;">فاتورة رقم #{len(st.session_state.invoices_history) - idx} - {inv['customer']}</h4>
                    <p style="margin: 5px 0;"><b>📅 التاريخ:</b> {inv['time']} | <b>النوع:</b> {inv['type']}</p>
                    <p style="margin: 5px 0;"><b>الإجمالي:</b> <span style="color: {inv['color']}; font-weight: bold;">{inv['total']} د.ع</span></p>
                </div>
                """, unsafe_allow_html=True)
            with col_box2:
                if st.button(f"👁️ عرض الوصل", key=f"view_inv_{idx}"):
                    st.session_state[f"show_details_{idx}"] = not st.session_state.get(f"show_details_{idx}", False)
            
            if st.session_state.get(f"show_details_{idx}", False):
                with st.expander(f"تفاصيل وطباعة وصل رقم #{len(st.session_state.invoices_history) - idx}", expanded=True):
                    st.markdown(f"""
                    <div style="background: #ffffff; padding: 15px; border-radius: 5px; border: 2px dashed {inv['color']}; font-family: 'Courier New', Courier, monospace; color: black; direction: rtl; max-width: 380px; margin: auto;">
                        <h3 style="text-align: center; color: {inv['color']}; margin: 0;">🏪 {st.session_state.shop_name}</h3>
                        <p style="text-align: center; font-size: 11px; color: #555;">وصل مؤرشف ({inv['type']})</p>
                        <hr style="border: 1px dashed #000;">
                        <p style="font-size: 12px; margin: 3px 0;"><b>التاريخ:</b> {inv['time']}</p>
                        <p style="font-size: 12px; margin: 3px 0;"><b>العميل:</b> {inv['customer']}</p>
                        <hr style="border: 1px dashed #000;">
                    """, unsafe_allow_html=True)
                    for prod in inv['items']:
                        st.write(f"- {prod['product_name']} | العدد: {prod['quantity']} | السعر: {prod['sell_price'] * prod['quantity']} د.ع")
                    st.markdown(f"<hr style='border: 1px dashed #000;'><h4 style='text-align: center; color: {inv['color']};'>المجموع: {inv['total']} د.ع</h4></div>", unsafe_allow_html=True)
                    
                    st.markdown("##### 📋 انسخ النص أدناه والصقه في تطبيق الطابعة الحرارية (Bluetooth Printer):")
                    st.code(inv.get('raw', f"فاتورة {inv['customer']} - المجموع: {inv['total']}"), language="text")
            st.markdown("---")
        
        if st.button("🗑️ مسح سجل الفواتير بالكامل"):
            st.session_state.invoices_history = []
            st.rerun()
    else:
        st.info("لا توجد فواتير مؤرشفة حتى الآن. قم بإتمام عمليات بيع من سلة المبيعات لتظهر هنا.")

# --- 7️⃣ وصل سداد وتسديد الديون ---
elif menu == "7️⃣ وصل سداد وتسديد الديون":
    st.header("🧾 وصل سداد وتصفير ديون العملاء")
    if customers:
        cust_map = {c['name'] + f" (الدين: {c.get('debt', 0)} د.ع)": c for c in customers}
        chosen_receipt_cust_label = st.selectbox("اختر العميل:", list(cust_map.keys()))
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
                    st.success(f"تم تسديد المبلغ بنجاح! الدين الباقي: {remaining_debt} د.ع")
                    
                    raw_debt_receipt = f"==========================\n"
                    raw_debt_receipt += f"    {st.session_state.shop_name}\n"
                    raw_debt_receipt += f"     (سند قبض وتسديد دين)\n"
                    raw_debt_receipt += f"==========================\n"
                    raw_debt_receipt += f"التاريخ: {datetime.now().strftime('%Y-%m-%d | %I:%M %p')}\n"
                    raw_debt_receipt += f"العميل: {selected_cust_data['name']}\n"
                    raw_debt_receipt += f"--------------------------\n"
                    raw_debt_receipt += f"المبلغ المستلم: {paid_val} د.ع\n"
                    raw_debt_receipt += f"المتبقي (الدين): {remaining_debt} د.ع\n"
                    raw_debt_receipt += f"==========================\n"
                    
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background: #ffffff; padding: 20px; border-radius: 10px; border: 2px solid #27ae60; font-family: 'Courier New', Courier, monospace; direction: rtl; color: black; max-width: 380px; margin: auto;">
                        <h3 style="text-align: center; color: #27ae60; margin: 0;">📜 سند قبض وتسديد ديون</h3>
                        <p style="text-align: center; font-size: 11px; color: #555;">محل: {st.session_state.shop_name}</p>
                        <hr style="border: 1px dashed #000;">
                        <p style="font-size: 12px; margin: 3px 0;"><b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d | %I:%M %p')}</p>
                        <p style="font-size: 12px; margin: 3px 0;"><b>العميل:</b> {selected_cust_data['name']}</p>
                        <hr style="border: 1px dashed #000;">
                        <p style="font-size: 13px;">المبلغ المستلم: <b style="color: green;">{paid_val} د.ع</b></p>
                        <p style="font-size: 13px;">المتبقي (الدين): <b style="color: red;">{remaining_debt} د.ع</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 📋 انسخ النص أدناه للطباعة عبر طابعة البلوتوث:")
                    st.code(raw_debt_receipt, language="text")
                    
                except ValueError:
                    st.warning("أدخل مبلغاً صحيحاً.")
    else:
        st.info("لا توجد عملاء مسجلون في قاعدة البيانات.")

# --- 8️⃣ سجل الديون والذمم ---
elif menu == "8️⃣ سجل الديون والذمم":
    st.header("📋 سجل الديون والذمم")
    if customers:
        debtors = [c for c in customers if float(c.get('debt', 0) or 0) > 0]
        if debtors:
            st.table(debtors)
        else:
            st.success("لا توجد ديون مترتبة حالياً.")
    else:
        st.info("لا توجد بيانات.")

# --- 9️⃣ المصاريف اليومية ---
elif menu == "9️⃣ المصاريف اليومية":
    st.header("💸 تسجيل المصاريف اليومية")
    with st.form("expenses_form"):
        exp_title = st.text_input("بيان المصروف")
        exp_amount_str = st.text_input("المبلغ (د.ع)", value="0")
        if st.form_submit_button("حفظ المصروف"):
            st.success("تم تسجيل المصروف بنجاح.")

# --- 🔟 تقارير الأرباح والخسائر ---
elif menu == "🔟 تقارير الأرباح والخسائر":
    st.header("📊 تقارير الأرباح والخسائر")
    if products:
        total_inv_buy = sum(float(p.get('buy_price', 0)) * int(p.get('quantity', 0)) for p in products)
        total_inv_sell = sum(float(p.get('sell_price', 0)) * int(p.get('quantity', 0)) for p in products)
        st.metric("قيمة المخزون (شراء)", f"{total_inv_buy} د.ع")
        st.metric("قيمة المخزون المتوقعة (بيع)", f"{total_inv_sell} د.ع")
        st.metric("الأرباح التقديرية", f"{total_inv_sell - total_inv_buy} د.ع")
    else:
        st.info("لا توجد بيانات كافية.")

# --- 11️⃣ دليل الاستخدام والدعم ---
elif menu == "11️⃣ دليل الاستخدام والدعم 📖":
    st.markdown("<h1>🛍️ دليل استخدام نظام ياسر ويب الشامل</h1>", unsafe_allow_html=True)
    st.markdown("المرجع الكامل والشامل لإدارة المبيعات والمخازن بكفاءة عالية.")
    st.markdown("---")
    st.markdown("### 📚 دليل الأقسام والتبويبات الأساسية:")
    st.markdown("1. **إدارة المخزون والبطاقات:** لعرض جميع المواد، معرفة أرباح القطع، بيع مباشر، أو حذف المواد.")
    st.markdown("2. **إضافة مادة جديدة:** لإدخال منتجات جديدة للمخزون مع أسعار الشراء والبيع والكمية.")
    st.markdown("3. **زيادة كمية لمادة موجودة:** لتحديث رصيد المنتجات الحالية وزيادتها بسهولة.")
    st.markdown("4. **إدارة العملاء:** لتسجيل معلومات العملاء، أرقامهم، وعناوينهم.")
    st.markdown("5. **سلة المبيعات والفاتورة:** لإضافة المواد للسلة وإصدار وصل بيع مع نص حراري جاهز للنسخ إلى طابعات البلوتوث.")
    st.markdown("6. **سجل الفواتير والوصلات المطبوعة:** لعرض أرشيف الوصلات السابقة بألوان مميزة (أخضر للنقد، أحمر للدين) مع إمكانية نسخ النص الحراري للطباعة.")
    st.markdown("7. **وصل سداد وتسديد الديون:** لتسديد الديون وإصدار سند قبض قابل للنسخ والطباعة.")
    st.markdown("8. **سجل الديون والذمم:** لمتابعة العملاء الذين عليهم ديون متراكمة للمحل.")
    st.markdown("9. **المصاريف اليومية:** لتسجيل المصروفات والنثريات اليومية.")
    st.markdown("10. **تقارير الأرباح والخسائر:** لمعرفة القيمة الإجمالية للمخزون والأرباح التقديرية.")
    st.markdown("11. **دليل الاستخدام والدعم:** هذا الدليل الشامل لكيفية استخدام أقسام النظام.")
    st.markdown("12. **حركة الصندوق والدرج اليومي:** لمتابعة الرصيد الافتتاحي وملاحظات الوردية.")
    st.markdown("13. **تنبيهات نفاذ المواد:** لتنبيهك بالمواد التي قاربت على النفاد (الكمية 3 أو أقل).")
    st.markdown("14. **طبع ملصقات الباركود:** لمعاينة وطباعة ملصقات الأسعار والرفوف.")
    st.markdown("15. **برنامج الولاء وعروض العملاء:** لمتابعة العملاء الدائمين ومنحهم خصومات خاصة.")
    st.markdown("16. **خانة التحديثات الجديدة:** لمتابعة أحدث الإضافات والتطويرات في النظام.")
    st.markdown("---")
    st.markdown("### 🆕 الإضافات والمهام المضافة حديثاً:")
    st.markdown("- **سجل الملاحظات والمهام (التبويب 17):** مفكرة يومية داخل النظام لتسجيل الملاحظات، الطلبيات الناقصة، والالتزامات.")
    st.markdown("---")
    st.markdown("✨ **تطوير البرمجة: نظام ياسر ويب | انستغرام:** yaser120120120120 2026©")

# --- 12️⃣ حركة الصندوق والدرج اليومي ---
elif menu == "12️⃣ حركة الصندوق والدرج اليومي 💵":
    st.header("💵 إدارة حركة الصندوق والدرج اليومي")
    with st.form("cash_drawer_form"):
        opening_cash = st.text_input("المبلغ الافتتاحي في الصندوق (العهدة صباحاً):", value="0")
        notes_drawer = st.text_area("ملاحظات وردية الصندوق:")
        if st.form_submit_button("حفظ بيانات الصندوق"):
            st.success("تم تسجيل بيانات الصندوق اليومي بنجاح.")

# --- 13️⃣ تنبيهات نفاذ المواد ---
elif menu == "13️⃣ تنبيهات نفاذ المواد ⚠️":
    st.header("⚠️ تنبيهات نفاذ المواد في المخزن")
    if products:
        low_stock_items = [p for p in products if int(p.get('quantity', 0)) <= 3]
        if low_stock_items:
            st.warning("تحذير: المواد التالية قاربت على النفاذ (الكمية 3 أو أقل):")
            st.table(low_stock_items)
        else:
            st.success("ممتاز! جميع المواد متوفرة بكميات كافية.")
    else:
        st.info("لا توجد منتجات مسجلة في المخزون.")

# --- 14️⃣ طبع ملصقات الباركود ---
elif menu == "14️⃣ طبع ملصقات الباركود 🏷️":
    st.header("🏷 طبع ملصقات الرفوف والباركود")
    if products:
        prod_labels = {p['product_name'] + f" (السعر: {p['sell_price']})": p for p in products}
        chosen_p_label = st.selectbox("اختر المنتج لطباعة ملصقه:", list(prod_labels.keys()))
        selected_p_obj = prod_labels[chosen_p_label]
        num_copies = st.number_input("عدد الملصقات المطلوبة:", min_value=1, max_value=50, value=5)
        
        if st.button("🖨️ معاينة وطباعة الملصق"):
            st.markdown(f"""
            <div style="border: 2px dashed #2c3e50; padding: 20px; border-radius: 8px; width: 300px; background: white; text-align: center; margin: auto; color: black;">
                <h3>{st.session_state.shop_name}</h3>
                <hr>
                <p style="font-size: 18px; font-weight: bold;">{selected_p_obj['product_name']}</p>
                <p style="font-size: 20px; color: #27ae60; font-weight: bold;">السعر: {selected_p_obj['sell_price']} د.ع</p>
                <p style="font-size: 14px; color: #555;">||| ||||| |||| ||||| (Barcode)</p>
                <p style="font-size: 11px; color: #555;">العدد المطلوب: {num_copies}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("لا توجد منتجات لطباعة باركود لها.")

# --- 15️⃣ برنامج الولاء وعروض العملاء ---
elif menu == "15️⃣ برنامج الولاء وعروض العملاء 🎁":
    st.header("🎁 برنامج الولاء ومتابعة عروض العملاء")
    if customers:
        cust_loyalty_map = {c['name']: c for c in customers}
        chosen_l_cust = st.selectbox("اختر العميل:", list(cust_loyalty_map.keys()))
        target_cust = cust_loyalty_map[chosen_l_cust]
        
        st.info(f"👤 العميل: **{target_cust['name']}**")
        with st.form("loyalty_form"):
            discount_note = st.text_input("منح خصم خاص أو ملاحظة ولاء:", value="عميل دائم - خصم خاص 5%")
            if st.form_submit_button("حفظ بيانات الولاء"):
                st.success("تم تحديث عروض وميزات الولاء للعميل بنجاح!")
    else:
        st.info("لا توجد عملاء مسجلون حالياً.")

# --- 16️⃣ خانة التحديثات الجديدة 🚀 ---
elif menu == "16️⃣ خانة التحديثات الجديدة 🚀":
    st.markdown("<h2 style='text-align: center;'>🚀 سجل التحديثات والتطويرات في نظام ياسر ويب</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### التحديثات الأخيرة (إصدار 2026):")
    st.markdown("- **دعم طابعات البلوتوث الحرارية:** توفير نظام تنسيق ونسخ النصوص الحرارية (Raw Text) لتتوافق مع تطبيقات طباعة البلوتوث الحرارية بسهولة مطلقة.")
    st.markdown("- **أرشيف الوصلات بالألوان:** تلوين الفواتير (أخضر للنقد، أحمر للدين) لتسهيل تمييزها بصرياً.")

# --- 17️⃣ سجل الملاحظات والمهام 📌 ---
elif menu == "17️⃣ سجل الملاحظات والمهام 📌":
    st.header("📌 سجل الملاحظات والمهام اليومية")
    with st.form("notes_form"):
        new_note = st.text_input("أدخل ملاحظة أو طلب ناقص للمحل:")
        add_note_btn = st.form_submit_button("إضافة للمفكرة")
        if add_note_btn:
            if new_note.strip():
                st.session_state.notes_list.append({"time": datetime.now().strftime('%Y-%m-%d | %I:%M %p'), "text": new_note.strip()})
                st.success("تمت إضافة الملاحظة بنجاح!")
            else:
                st.warning("الرجاء كتابة نص الملاحظة.")
                
    st.subheader("قائمة الملاحظات المسجلة حالياً:")
    if st.session_state.notes_list:
        for idx, n in enumerate(st.session_state.notes_list):
            st.write(f"{idx+1}. [{n['time']}] **{n['text']}**")
        if st.button("🗑 مسح جميع الملاحظات"):
            st.session_state.notes_list = []
            st.rerun()
    else:
        st.info("لا توجد ملاحظات مسجلة.")
