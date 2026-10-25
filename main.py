import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co"
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="ياسر ويب - YASSER WEB", layout="centered")

# **تنسيق CSS دقيق يطابق واجهات الموبايل وبإطار احترافي**
st.markdown("""
    <style>
    /* خلفية التطبيق الخارجية */
    .stApp {
        background: linear-gradient(135deg, #553c9a 0%, #3b2375 100%) !important;
        direction: rtl;
        text-align: right;
        font-family: system-ui, -apple-system, sans-serif;
    }
    
    /* إطار التطبيق الداخلي ليشبه الموبايل بدقة متناهية */
    .block-container {
        max-width: 420px !important;
        background: #f8f6fc !important;
        border-radius: 32px !important;
        padding: 25px 18px !important;
        margin: 15px auto !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.35) !important;
        border: 6px solid #2d1a4e !important;
    }

    /* وضوح النصوص والعناوين باللون الداكن المريح */
    p, span, label, h1, h2, h3, h4, .stTextInput label, .stSelectbox label {
        color: #2d1a4e !important;
        font-weight: 600;
    }

    /* حقول الإدخال واضحة وبكتابة سوداء صريحة */
    input, select, textarea {
        color: #000000 !important;
        background: #ffffff !important;
        border: 1px solid #dcd6f7 !important;
        border-radius: 12px !important;
        text-align: right !important;
        direction: rtl !important;
    }

    /* الأزرار بتصميم أنيق وبارز */
    .stButton > button {
        background-color: #6b46c1 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 14px !important;
        font-weight: bold !important;
        width: 100% !important;
        font-size: 14px !important;
        box-shadow: 0 4px 10px rgba(107, 70, 193, 0.2);
    }
    .stButton > button:hover {
        background-color: #483185 !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

# **تهيئة الجلسات الآمنة**
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "مشرف النظام"
if "suppliers_list" not in st.session_state:
    st.session_state.suppliers_list = []
if "customers_list" not in st.session_state:
    st.session_state.customers_list = []
if "products_list" not in st.session_state:
    st.session_state.products_list = []
if "invoices_list" not in st.session_state:
    st.session_state.invoices_list = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "expenses_list" not in st.session_state:
    st.session_state.expenses_list = []
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []
if "active_page" not in st.session_state:
    st.session_state.active_page = "الرئيسية"

def log_audit(action, details):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = st.session_state.logged_in_user or "زائر"
    role = st.session_state.user_role
    st.session_state.audit_logs.insert(0, {
        "التاريخ والوقت": str(timestamp),
        "المستخدم": str(user),
        "الصلاحية": str(role),
        "العملية": str(action),
        "التفاصيل": str(details)
    })

def generate_html_invoice(inv):
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {inv['invoice_code']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); background: #fff; }}
            .header {{ text-align: center; border-bottom: 2px solid #6b46c1; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ margin-bottom: 20px; font-size: 15px; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; font-size: 14px; }}
            th {{ background-color: #f3e8ff; color: #6b46c1; }}
            .totals {{ font-size: 16px; font-weight: bold; text-align: left; margin-top: 15px; line-height: 1.8; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 13px; color: #777; border-top: 1px dashed #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <h2>ياسر ويب - فاتورة طلبية رسمية</h2>
                <p>التاريخ والوقت: {inv['created_date']}</p>
            </div>
            <div class="info">
                <p><strong>رقم الفاتورة:</strong> {inv['invoice_code']}</p>
                <p><strong>اسم الزبون:</strong> {inv['customer_name']}</p>
                <p><strong>طريقة وحالة الدفع:</strong> {inv['payment_type']}</p>
            </div>
            <table>
                <tr><th>تفاصيل المنتجات والمواد المطلوبة</th></tr>
                <tr><td>{inv['products_text']}</td></tr>
            </table>
            <div class="totals">
                <p>المبلغ الكلي: {inv['total_price']:,} د.ع</p>
                <p>المبلغ الواصل: {inv['paid_amount']:,} د.ع</p>
                <p>المتبقي (الدين): {inv['remaining_amount']:,} د.ع</p>
            </div>
            <div class="footer"><p>شكراً لتعاملكم معنا - ياسر ويب</p></div>
        </div>
    </body>
    </html>
    """

# **شاشة تسجيل الدخول**
if not st.session_state.logged_in_user:
    st.markdown("<h2 style='text-align: center; font-size: 18px; margin-bottom: 20px; color: #2d1a4e;'>🔐 تسجيل الدخول لنظام (ياسر ويب)</h2>", unsafe_allow_html=True)
    with st.form("login_modern_form"):
        login_user = st.text_input("اسم المستخدم أو المحل:")
        login_role = st.selectbox("الصلاحية:", ["مشرف النظام", "كاشير", "مسؤول مبيعات"])
        sub_log = st.form_submit_button("دخول للنظام", type="primary")
        if sub_log:
            if login_user.strip():
                try:
                    res = supabase.table("users").select("*").eq("username", login_user.strip()).execute()
                    if res.data:
                        user_info = res.data[0]
                        st.session_state.logged_in_user = str(user_info["username"])
                        st.session_state.user_role = str(login_role)
                        log_audit("تسجيل دخول", f"تم الدخول بواسطة {user_info['username']}")
                        st.success("تم الدخول بنجاح!")
                        st.rerun()
                    else:
                        supabase.table("users").insert({"username": login_user.strip(), "is_paid": False}).execute()
                        st.session_state.logged_in_user = str(login_user.strip())
                        st.session_state.user_role = str(login_role)
                        st.success("تم إنشاء الحساب والدخول بنجاح!")
                        st.rerun()
                except Exception:
                    st.session_state.logged_in_user = str(login_user.strip())
                    st.session_state.user_role = str(login_role)
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
            else:
                st.warning("يرجى إدخال اسم المستخدم.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

# ================= الشريط العلوي =================
top_c1, top_c2, top_c3 = st.columns([1, 2, 2])
with top_c1:
    if st.session_state.active_page != "الرئيسية":
        if st.button("⬅️"):
            st.session_state.active_page = "الرئيسية"
            st.rerun()
with top_c2:
    total_cart_qty = sum(item['qty'] for item in st.session_state.cart)
    if st.button(f"🛒 [{total_cart_qty}]"):
        st.session_state.active_page = "🛒 سلة البيع وإتمام الفاتورة"
        st.rerun()
with top_c3:
    if st.button("🚪 خروج"):
        st.session_state.logged_in_user = None
        st.session_state.cart = []
        st.session_state.active_page = "الرئيسية"
        st.rerun()

st.markdown(f"<h3 style='text-align: center; margin: 5px 0 15px 0; font-size: 16px; color: #2d1a4e;'>ياسر ويب</h3>", unsafe_allow_html=True)
st.divider()

# ================= الشاشة الرئيسية =================
if st.session_state.active_page == "الرئيسية":
    st.markdown("<p style='text-align: center; font-size: 13px; font-weight: bold; margin-bottom: 10px; color: #553c9a;'>إدارة المبيعات والعمليات</p>", unsafe_allow_html=True)
    
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    try:
        inv_res = supabase.table("invoices").select("*").eq("username", username).execute()
        all_invs = inv_res.data if inv_res.data else st.session_state.invoices_list
    except:
        all_invs = st.session_state.invoices_list
    
    today_invs = [inv for inv in all_invs if str(inv.get('created_date', '')).startswith(today_str)]
    today_sales_sum = sum(int(inv.get('total_price', 0)) for inv in today_invs)
    
    with st.container(border=True):
        st.markdown(f"📊 **إحصائيات اليوم:** مبيعات: `{today_sales_sum:,} د.ع` | الفواتير: `{len(today_invs)}`")

    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.container(border=True):
            st.markdown("### 🏠 الرئيسية والشبكة")
            st.write("عرض شبكة المواد والضغطة السريعة")
            if st.button("فتح الرئيسية", key="t1"): st.session_state.active_page = "🏠 الرئيسية والشبكة"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 👥 العملاء والديون")
            st.write("إدارة الزبائن والذمم")
            if st.button("فتح العملاء", key="t5"): st.session_state.active_page = "👥 إدارة العملاء والديون"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 🏭 إدارة الموردين")
            st.write("موردين البضاعة")
            if st.button("فتح الموردين", key="t7"): st.session_state.active_page = "🏭 إدارة الموردين"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 💰 الصندوق والمصاريف")
            st.write("سندات المصروفات")
            if st.button("فتح الصندوق", key="t9"): st.session_state.active_page = "💰 الصندوق والمصاريف"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 📜 سجل النشاطات")
            st.write("حركة العمليات")
            if st.button("فتح السجل", key="t11"): st.session_state.active_page = "📜 سجل النشاطات"; st.rerun()

    with col_b:
        with st.container(border=True):
            st.markdown("### ➕ إضافة وتوريد")
            st.write("إضافة بضاعة ومخزون")
            if st.button("فتح التوريد", key="t3"): st.session_state.active_page = "➕ إضافة وتوريد كميات"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 📦 جرد المخزن")
            st.write("عرض رصيد المواد")
            if st.button("فتح المخزن", key="t4"): st.session_state.active_page = "📦 جرد المخزن"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 💵 سداد الديون")
            st.write("تسديد ديون العملاء")
            if st.button("فتح السداد", key="t6"): st.session_state.active_page = "💵 سداد الديون"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 📄 سجل الفواتير")
            st.write("قائمة الفواتير الرسمية")
            if st.button("فتح الفواتير", key="t8"): st.session_state.active_page = "📄 سجل الفواتير وواتساب"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 📊 التقارير والأرباح")
            st.write("الحسابات المالية")
            if st.button("فتح التقارير", key="t10"): st.session_state.active_page = "📊 التقارير والأرباح"; st.rerun()

    st.markdown("<br><p style='text-align: center; font-size: 11px; color: #7c6f9f;'>ياسر ويب - الإصدار 4.4.0</p>", unsafe_allow_html=True)

# ================= تشغيل الأقسام والتبويبات =================

elif st.session_state.active_page == "🏠 الرئيسية والشبكة":
    total_badge = sum(i['qty'] for i in st.session_state.cart)
    st.subheader(f"🏠 شبكة المبيعات [السلة: {total_badge}]")
    
    try:
        res = supabase.table("products").select("*").eq("username", username).execute()
        grid_items = res.data if res.data else []
        if not grid_items and st.session_state.products_list:
            grid_items = st.session_state.products_list
    except Exception:
        grid_items = st.session_state.products_list

    search_query = st.text_input("🔍 بحث سريع عن مادة:", "").strip().lower()
    if search_query:
        grid_items = [item for item in grid_items if search_query in item.get('product_name', '').lower()]

    if grid_items:
        g_cols = st.columns(2)
        for idx, item in enumerate(grid_items):
            with g_cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"#### 📦 {item['product_name']}")
                    st.markdown(f"💰 السعر: `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🔢 المتوفر: `{item['quantity']}` قطعة")
                    
                    if item['quantity'] <= 3 and item['quantity'] > 0:
                        st.warning("⚠️ تنبيه: الكمية قربت تنفد!")

                    if item['quantity'] > 0:
                        if st.button("➕ إضافة", key=f"grid_add_{item.get('id', idx)}"):
                            found = False
                            for ci in st.session_state.cart:
                                if ci["product_name"] == item["product_name"]:
                                    if ci["qty"] < item["quantity"]:
                                        ci["qty"] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({
                                    "id": item.get("id", idx),
                                    "product_name": item["product_name"],
                                    "sell_price": item["sell_price"],
                                    "buy_price": item["buy_price"],
                                    "max_qty": item["quantity"],
                                    "qty": 1
                                })
                            st.success("تمت الإضافة للسلة!")
                            st.rerun()
                    else:
                        st.error("نفدت الكمية")
    else:
        st.info("لا توجد مواد مطابقة للبحث أو في المخزن حالياً.")

elif st.session_state.active_page == "🛒 سلة البيع وإتمام الفاتورة":
    st.subheader("🛒 سلة البيع وإتمام الفاتورة")
    if st.session_state.cart:
        total_cart_price = 0
        for idx, c_item in enumerate(st.session_state.cart):
            with st.container(border=True):
                st.write(f"**{c_item['product_name']}**")
                cols_c = st.columns(2)
                with cols_c[0]:
                    new_q = st.number_input("العدد", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"c_q_{idx}")
                    c_item['qty'] = new_q
                with cols_c[1]:
                    item_sum = c_item['sell_price'] * c_item['qty']
                    total_cart_price += item_sum
                    st.write(f"المجموع: **{int(item_sum):,}**")
                if st.button("❌ حذف", key=f"rem_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()

        st.divider()
        st.markdown(f"### 💵 المجموع الكلي: **{int(total_cart_price):,} د.ع**")

        try:
            res_custs = supabase.table("customers").select("*").eq("username", username).execute()
            customer_records = res_custs.data if res_custs.data else []
            if not customer_records and st.session_state.customers_list:
                customer_records = st.session_state.customers_list
        except Exception:
            customer_records = st.session_state.customers_list

        if not customer_records:
            st.warning("⚠️ يرجى إضافة عميل أولاً من قسم (إدارة العملاء والديون).")
            selected_cust_name = ""
        else:
            cust_names = [c["customer_name"] for c in customer_records]
            selected_cust_name = st.selectbox("اختر اسم العميل:", cust_names)
            
            chosen_cust_obj = next((c for c in customer_records if c["customer_name"] == selected_cust_name), None)
            if chosen_cust_obj:
                c_phone = chosen_cust_obj.get("phone", "غير محدد")
                c_address = chosen_cust_obj.get("address", "غير محدد")
                c_gov = chosen_cust_obj.get("governorate", "غير محدد")
                st.info(f"📍 معلومات العميل:\n الهاتف: `{c_phone}`\n العنوان: `{c_address}`\n المحافظة: `{c_gov}`")

        paid_str = st.text_input("المبلغ الواصل (نقد أو حط 0 للأقساط):", value=str(int(total_cart_price)))
        try:
            paid_val = float(paid_str.strip())
            if paid_val < 0: paid_val = 0
        except:
            paid_val = 0
            
        rem_val = max(0, total_cart_price - paid_val)

        if paid_val > total_cart_price:
            change_due = paid_val - total_cart_price
            st.success(f"💵 الباقي المستحق للزبون (الرجيع): **{int(change_due):,} د.ع**")

        if paid_val >= total_cart_price:
            pay_status = "🟢 نقد (كاش)"
        elif paid_val == 0:
            pay_status = "🔴 دين كامل (آجل)"
        else:
            pay_status = "🔵 دفعة جزئية (أقساط)"

        if st.button("💾 إتمام وحفظ البيع وطباعة الفاتورة", type="primary"):
            if not selected_cust_name:
                st.error("يرجى اختيار عميل صالح.")
            else:
                try:
                    prod_str_list = []
                    total_cost_inv = 0
                    for c_item in st.session_state.cart:
                        prod_str_list.append(f"{c_item['product_name']} [العدد: {c_item['qty']}]")
                        total_cost_inv += (c_item['buy_price'] * c_item['qty'])
                        
                        try:
                            p_res = supabase.table("products").select("*").eq("username", username).eq("product_name", c_item["product_name"]).execute()
                            if p_res.data:
                                p_row = p_res.data[0]
                                curr_q = p_row["quantity"]
                                p_id = p_row["id"]
                                new_q = max(0, curr_q - c_item['qty'])
                                supabase.table("products").update({"quantity": new_q}).eq("id", p_id).execute()
                        except Exception:
                            pass

                        for p_local in st.session_state.products_list:
                            if p_local["product_name"] == c_item["product_name"]:
                                p_local["quantity"] = max(0, p_local["quantity"] - c_item['qty'])

                    inv_seq = len(st.session_state.invoices_list) + 1
                    inv_code = f"INV-{inv_seq:03d}"

                    inv_data = {
                        "username": str(username),
                        "invoice_code": str(inv_code),
                        "customer_name": str(selected_cust_name),
                        "products_text": str(" ، ".join(prod_str_list)),
                        "total_price": int(total_cart_price),
                        "cost_price": int(total_cost_inv),
                        "paid_amount": int(min(paid_val, total_cart_price)),
                        "remaining_amount": int(rem_val),
                        "payment_type": str(pay_status),
                        "created_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    }

                    try:
                        supabase.table("invoices").insert(inv_data).execute()
                    except Exception:
                        pass
                    st.session_state.invoices_list.append(inv_data)

                    log_audit("إتمام بيع", f"فاتورة رقم {inv_code}")
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع بنجاح ونقصان الكميات من المخزن!")
                    
                    st.markdown("### 📄 معاينة الفاتورة للطباعة والواتساب")
                    st.components.v1.html(generate_html_invoice(inv_data), height=400, scrolling=True)
                    
                    w_text = f"مرحباً {selected_cust_name}، تفاصيل فاتورتك رقم {inv_code} من ياسر ويب:%0Aإجمالي المبلغ: {total_cart_price:,} د.ع%0Aالمتبقي: {rem_val:,} د.ع%0Aشكراً لتعاملكم معنا!"
                    st.markdown(f'<a href="https://wa.me/?text={w_text}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px; border:none; border-radius:10px; width:100%; font-weight:bold; cursor:pointer;">💬 إرسال الفاتورة عبر الواتساب</button></a>', unsafe_allow_html=True)
                    
                    st.balloons()
                except Exception as ex:
                    st.error(f"خطأ: {ex}")
    else:
        st.info("🛒 السلة فارغة حالياً. اذهب إلى (الرئيسية والشبكة) وأضف مواد.")

elif st.session_state.active_page == "➕ إضافة وتوريد كميات":
    st.subheader("➕ إضافة مادة جديدة")
    with st.form("new_p", clear_on_submit=True):
        pn = st.text_input("اسم المادة:")
        pb = st.text_input("سعر الشراء:", "0")
        ps = st.text_input("سعر البيع:", "0")
        pq = st.text_input("الكمية المتوفرة:", "1")
        if st.form_submit_button("حفظ المادة", type="primary"):
            if pn.strip():
                new_prod = {
                    "username": str(username),
                    "product_name": str(pn.strip()),
                    "buy_price": float(pb),
                    "sell_price": float(ps),
                    "quantity": int(pq),
                    "barcode": "بدون"
                }
                try:
                    supabase.table("products").insert(new_prod).execute()
                except Exception:
                    pass
                st.session_state.products_list.append(new_prod)
                st.success("تم حفظ المادة بنجاح!")
                st.rerun()

elif st.session_state.active_page == "📦 جرد المخزن":
    st.subheader("📦 جرد المخزن الشامل")
    try:
        res = supabase.table("products").select("*").eq("username", username).execute()
        data = res.data if res.data else []
        if not data and st.session_state.products_list:
            data = st.session_state.products_list
    except Exception:
        data = st.session_state.products_list

    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("المخزن فارغ حالياً.")

elif st.session_state.active_page == "👥 إدارة العملاء والديون":
    st.subheader("👥 إدارة العملاء والذمم")
    with st.form("cust_f", clear_on_submit=True):
        cn = st.text_input("اسم العميل (الاسم):")
        cp = st.text_input("رقم الهاتف (الرقم):")
        ca = st.text_input("العنوان:")
        cg = st.text_input("المحافظة:")
        if st.form_submit_button("حفظ العميل"):
            if cn and cp:
                new_cust = {
                    "username": str(username),
                    "customer_name": str(cn.strip()),
                    "phone": str(cp.strip()),
                    "address": str(ca.strip() if ca else "غير محدد"),
                    "governorate": str(cg.strip() if cg else "غير محدد"),
                    "created_at": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                }
                try:
                    supabase.table("customers").insert(new_cust).execute()
                except Exception:
                    pass
                st.session_state.customers_list.append(new_cust)
                st.success(f"تم حفظ العميل {cn} بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى إدخال اسم العميل ورقم الهاتف على الأقل.")

elif st.session_state.active_page == "💵 سداد الديون":
    st.subheader("💵 نظام سداد ديون العملاء")
    st.info("لا توجد ديون مسجلة حالياً.")

elif st.session_state.active_page == "🏭 إدارة الموردين":
    st.subheader("🏭 إدارة الموردين")
    with st.form("sup_tab", clear_on_submit=True):
        sn = st.text_input("اسم المورد:")
        sp = st.text_input("رقم الهاتف:")
        if st.form_submit_button("إضافة المورد"):
            if sn:
                st.session_state.suppliers_list.append({"اسم المورد": sn, "الهاتف": sp})
                st.success("تمت الإضافة بنجاح!")
                st.rerun()
    if st.session_state.suppliers_list:
        st.dataframe(pd.DataFrame(st.session_state.suppliers_list), use_container_width=True)

elif st.session_state.active_page == "📄 سجل الفواتير وواتساب":
    st.subheader("📄 سجل الفواتير الرسمية والواتساب")
    try:
        res = supabase.table("invoices").select("*").eq("username", username).execute()
        invs = res.data if res.data else []
        if not invs and st.session_state.invoices_list:
            invs = st.session_state.invoices_list
    except Exception:
        invs = st.session_state.invoices_list

    if invs:
        for inv in reversed(invs):
            with st.container(border=True):
                st.write(f"فاتورة: {inv['invoice_code']} | الزبون: {inv['customer_name']} | المجموع: {inv['total_price']:,} د.ع")
                with st.expander("🖨️ عرض الفاتورة والواتساب"):
                    st.components.v1.html(generate_html_invoice(inv), height=350, scrolling=True)
                    w_text = f"فاتورة رقم {inv['invoice_code']} للزبون {inv['customer_name']}%0Aالمبلغ: {inv['total_price']:,} د.ع%0Aالمتبقي: {inv['remaining_amount']:,} د.ع"
                    st.markdown(f'<a href="https://wa.me/?text={w_text}" target="_blank"><button style="background-color:#25D366; color:white; padding:8px; border:none; border-radius:8px; width:100%; font-weight:bold; cursor:pointer;">💬 إرسال عبر الواتساب</button></a>', unsafe_allow_html=True)
    else:
        st.info("لا توجد فواتير مسجلة.")

elif st.session_state.active_page == "💰 الصندوق والمصاريف":
    st.subheader("💰 صندوق الوردية والمصاريف")
    with st.form("exp_tab", clear_on_submit=True):
        et = st.text_input("بيان المصروف:")
        ea = st.text_input("المبلغ (د.ع):", "0")
        if st.form_submit_button("تسجيل المصروف"):
            if et:
                st.session_state.expenses_list.append({"البيان": et, "المبلغ": float(ea)})
                st.success("تم التسجيل بنجاح!")
                st.rerun()
    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)

elif st.session_state.active_page == "📊 التقارير والأرباح":
    st.subheader("📊 التقارير والأرباح المالية")
    st.metric("إجمالي المبيعات", "0 د.ع")
    st.metric("صافي الأرباح", "0 د.ع")

elif st.session_state.active_page == "📜 سجل النشاطات":
    st.subheader("📜 سجل النشاطات والعمليات")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد سجلات نشاط مسجلة حتى الآن.")
