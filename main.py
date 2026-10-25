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

# **تنسيق CSS دقيق يطابق واجهات TOFA وبإطار موبايل احترافي متجاوب**
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
        padding: 10px 16px !important;
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

# **تهيئة الجلسات نظيفة تماماً (صفر بيانات مسبقة)**
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "مشرف النظام"
if "suppliers_list" not in st.session_state:
    st.session_state.suppliers_list = []
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
                except Exception as e:
                    st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            else:
                st.warning("يرجى إدخال اسم المستخدم.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

# **شريط علوي داخل إطار الموبايل**
top_c1, top_c2, top_c3 = st.columns([1, 3, 1])
with top_c1:
    if st.session_state.active_page != "الرئيسية":
        if st.button("⬅️ رجوع"):
            st.session_state.active_page = "الرئيسية"
            st.rerun()
with top_c2:
    st.markdown(f"<h3 style='text-align: center; margin: 0; font-size: 16px; color: #2d1a4e;'>ياسر ويب</h3>", unsafe_allow_html=True)
with top_c3:
    if st.button("🚪 خروج"):
        st.session_state.logged_in_user = None
        st.session_state.cart = []
        st.session_state.active_page = "الرئيسية"
        st.rerun()

st.divider()

# ================= الشاشة الرئيسية: عرض الـ 11 تبويب ببطاقات بيضاء مطابقة =================
if st.session_state.active_page == "الرئيسية":
    st.markdown("<p style='text-align: center; font-size: 13px; font-weight: bold; margin-bottom: 15px; color: #553c9a;'>إدارة المبيعات والعمليات</p>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.container(border=True):
            st.markdown("### 🏠 الرئيسية والشبكة")
            st.write("عرض شبكة المواد السريعة")
            if st.button("فتح الرئيسية", key="t1"): st.session_state.active_page = "🏠 الرئيسية والشبكة"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### ➕ إضافة وتوريد")
            st.write("إضافة بضاعة ومخزون")
            if st.button("فتح التوريد", key="t3"): st.session_state.active_page = "➕ إضافة وتوريد كميات"; st.rerun()
            
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
            st.markdown("### 🛒 سلة البيع")
            st.write("مراجعة السلة والفاتورة")
            if st.button("فتح السلة", key="t2"): st.session_state.active_page = "🛒 سلة البيع وإتمام الفاتورة"; st.rerun()
            
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

    st.markdown("<br><p style='text-align: center; font-size: 11px; color: #7c6f9f;'>ياسر ويب - الإصدار 4.3.0</p>", unsafe_allow_html=True)

# ================= تشغيل الـ 11 تبويب بالكامل =================

elif st.session_state.active_page == "🏠 الرئيسية والشبكة":
    st.subheader("🏠 شبكة المبيعات السريعة")
    try:
        res = supabase.table("products").select("*").eq("username", username).execute()
        grid_items = res.data if res.data else []
    except:
        grid_items = []

    if grid_items:
        g_cols = st.columns(2)
        for idx, item in enumerate(grid_items):
            with g_cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"#### 📦 {item['product_name']}")
                    st.markdown(f"💰 السعر: `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🔢 المتوفر: `{item['quantity']}` قطعة")
                    if item['quantity'] > 0:
                        if st.button("➕ إضافة", key=f"grid_add_{item['id']}"):
                            found = False
                            for ci in st.session_state.cart:
                                if ci["id"] == item["id"]:
                                    if ci["qty"] < item["quantity"]:
                                        ci["qty"] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({
                                    "id": item["id"],
                                    "product_name": item["product_name"],
                                    "sell_price": item["sell_price"],
                                    "buy_price": item["buy_price"],
                                    "max_qty": item["quantity"],
                                    "qty": 1
                                })
                            st.success("تمت الإضافة!")
                            st.rerun()
                    else:
                        st.error("نفدت الكمية")
    else:
        st.info("لا توجد مواد مضافة في المخزن حالياً. أضف بضاعة جديدة من قسم (إضافة وتوريد كميات).")

elif st.session_state.active_page == "🛒 سلة البيع وإتمام الفاتورة":
    st.subheader("🛒 سلة البيع وإتمام الفاتورة")
    if st.session_state.cart:
        total_cart_price = 0
        for idx, c_item in enumerate(st.session_state.cart):
            with st.container(border=True):
                st.write(f"**{c_item['product_name']}**")
                cols_c = st.columns(2)
                with cols_c[0]:
                    new_q = st.number_input("العدد", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"c_q_{c_item['id']}")
                    c_item['qty'] = new_q
                with cols_c[1]:
                    item_sum = c_item['sell_price'] * c_item['qty']
                    total_cart_price += item_sum
                    st.write(f"المجموع: **{int(item_sum):,}**")
                if st.button("❌ حذف", key=f"rem_{c_item['id']}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()

        st.divider()
        st.markdown(f"### 💵 المجموع الكلي: **{int(total_cart_price):,} د.ع**")

        try:
            res_custs = supabase.table("customers").select("*").eq("username", username).execute()
            customer_records = res_custs.data if res_custs.data else []
        except:
            customer_records = []

        if not customer_records:
            st.warning("⚠️ يرجى إضافة عميل أولاً من قسم (إدارة العملاء والديون).")
            selected_cust_name = ""
        else:
            cust_names = [c["customer_name"] for c in customer_records]
            selected_cust_name = st.selectbox("اسم الزبون:", cust_names)

        paid_str = st.text_input("المبلغ الواصل (د.ع):", value=str(int(total_cart_price)))
        try:
            paid_val = float(paid_str.strip())
            if paid_val < 0: paid_val = 0
            if paid_val > total_cart_price: paid_val = total_cart_price
        except:
            paid_val = 0
        rem_val = total_cart_price - paid_val

        if paid_val >= total_cart_price:
            pay_status = "🟢 كاش"
        elif paid_val == 0:
            pay_status = "🔴 دين كامل"
        else:
            pay_status = "🔵 دفعة جزئية"

        if st.button("💾 بيع وطباعة الفاتورة", type="primary"):
            if not selected_cust_name:
                st.error("يرجى اختيار عميل صالح.")
            else:
                try:
                    prod_str_list = []
                    total_cost_inv = 0
                    for c_item in st.session_state.cart:
                        prod_str_list.append(f"{c_item['product_name']} [العدد: {c_item['qty']}]")
                        total_cost_inv += (c_item['buy_price'] * c_item['qty'])
                        
                        res_p_q = supabase.table("products").select("quantity").eq("id", c_item["id"]).execute()
                        if res_p_q.data:
                            curr_q = res_p_q.data[0]["quantity"]
                            new_q = max(0, curr_q - c_item['qty'])
                            supabase.table("products").update({"quantity": new_q}).eq("id", c_item["id"]).execute()

                    res_inv_len = supabase.table("invoices").select("id").eq("username", username).execute()
                    inv_seq = len(res_inv_len.data) + 1 if res_inv_len.data else 1
                    inv_code = f"INV-{inv_seq:03d}"

                    inv_data = {
                        "username": str(username),
                        "invoice_code": str(inv_code),
                        "customer_name": str(selected_cust_name),
                        "products_text": str(" ، ".join(prod_str_list)),
                        "total_price": int(total_cart_price),
                        "cost_price": int(total_cost_inv),
                        "paid_amount": int(paid_val),
                        "remaining_amount": int(rem_val),
                        "payment_type": str(pay_status),
                        "created_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    }

                    supabase.table("invoices").insert(inv_data).execute()
                    log_audit("إتمام بيع", f"فاتورة رقم {inv_code}")
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع بنجاح!")
                    st.components.v1.html(generate_html_invoice(inv_data), height=400, scrolling=True)
                    st.balloons()
                except Exception as ex:
                    st.error(f"خطأ: {ex}")
    else:
        st.info("🛒 السلة فارغة حالياً. أضف مواد من الرئيسية للبدء.")

elif st.session_state.active_page == "➕ إضافة وتوريد كميات":
    st.subheader("➕ إضافة مادة جديدة")
    with st.form("new_p", clear_on_submit=True):
        pn = st.text_input("اسم المادة:")
        pb = st.text_input("سعر الشراء:", "0")
        ps = st.text_input("سعر البيع:", "0")
        pq = st.text_input("الكمية المتوفرة:", "1")
        if st.form_submit_button("حفظ المادة", type="primary"):
            if pn.strip():
                try:
                    supabase.table("products").insert({
                        "username": username,
                        "product_name": pn.strip(),
                        "buy_price": float(pb),
                        "sell_price": float(ps),
                        "quantity": int(pq),
                        "barcode": "بدون"
                    }).execute()
                    st.success("تم حفظ المادة بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")

elif st.session_state.active_page == "📦 جرد المخزن":
    st.subheader("📦 جرد المخزن الشامل")
    try:
        res = supabase.table("products").select("*").eq("username", username).execute()
        data = res.data if res.data else []
    except:
        data = []
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("المخزن فارغ حالياً.")

elif st.session_state.active_page == "👥 إدارة العملاء والديون":
    st.subheader("👥 إدارة العملاء والذمم")
    with st.form("cust_f", clear_on_submit=True):
        cn = st.text_input("اسم العميل:")
        cp = st.text_input("رقم الهاتف:")
        ca = st.text_input("العنوان:")
        if st.form_submit_button("حفظ العميل"):
            if cn and cp:
                try:
                    supabase.table("customers").insert({
                        "username": username,
                        "customer_name": cn.strip(),
                        "phone": cp.strip(),
                        "address": ca.strip() if ca else "غير محدد",
                        "created_at": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                    }).execute()
                    st.success("تم حفظ العميل بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")

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
    st.subheader("📄 سجل الفواتير الرسمية")
    try:
        res = supabase.table("invoices").select("*").eq("username", username).execute()
        invs = res.data if res.data else []
    except:
        invs = []
    if invs:
        for inv in reversed(invs):
            with st.container(border=True):
                st.write(f"فاتورة: {inv['invoice_code']} | الزبون: {inv['customer_name']} | المجموع: {inv['total_price']:,} د.ع")
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
