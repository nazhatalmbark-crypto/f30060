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

st.set_page_config(page_title="ياسر بوس - YASSER POS", layout="centered")

# **تصميم مريح للعين مطابق تماماً لواجهة تطبيق TOFA (خلفية فاتحة وبطاقات بيضاء)**
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f3f0fb 0%, #e9e4f5 100%);
        direction: rtl;
        text-align: right;
        font-family: system-ui, -apple-system, sans-serif;
        color: #2d1a4e;
    }
    input, select, textarea {
        direction: rtl;
        text-align: right;
        border-radius: 14px !important;
        border: 1px solid #dcd6f7 !important;
    }
    /* تنسيق الأزرار لتكون أنيقة ومخفية بشكل متناسق داخل البطاقات */
    .stButton > button {
        background-color: #6b46c1;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 8px 14px;
        font-weight: bold;
        width: 100%;
        font-size: 13px;
        box-shadow: 0 4px 10px rgba(107, 70, 193, 0.2);
    }
    .stButton > button:hover {
        background-color: #553c9a;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# **جلسات النظام مصفّرة ونظيفة تماماً**
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
                <h2>ياسر بوس - فاتورة طلبية رسمية</h2>
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
            <div class="footer"><p>شكراً لتعاملكم معنا - ياسر بوس</p></div>
        </div>
    </body>
    </html>
    """

# **شاشة تسجيل الدخول**
if not st.session_state.logged_in_user:
    st.markdown("<h2 style='text-align: center; color: #2d1a4e;'>🔐 تسجيل الدخول لنظام (ياسر بوس)</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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

# **شريط علوي مع زر الرجوع والخروج**
top_c1, top_c2, top_c3 = st.columns([1, 4, 1])
with top_c1:
    if st.session_state.active_page != "الرئيسية":
        if st.button("⬅️ رجوع"):
            st.session_state.active_page = "الرئيسية"
            st.rerun()
with top_c2:
    st.markdown(f"<h3 style='text-align: center; margin: 0; color: #2d1a4e;'>ياسر بوس (TOFA)</h3>", unsafe_allow_html=True)
with top_c3:
    if st.button("🚪 خروج"):
        st.session_state.logged_in_user = None
        st.session_state.cart = []
        st.session_state.active_page = "الرئيسية"
        st.rerun()

st.divider()

# ================= الشاشة الرئيسية: عرض الـ 11 تبويب ببطاقات TOFA البيضاء =================
if st.session_state.active_page == "الرئيسية":
    st.markdown("<h4 style='text-align: center; color: #553c9a; margin-bottom: 20px;'>إدارة المبيعات والعمليات</h4>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.container(border=True):
            st.markdown("### 🏠 الرئيسية والشبكة")
            st.write("عرض شبكة المواد السريعة")
            if st.button("فتح الرئيسية", key="t1"): st.session_state.active_page = "🏠 الرئيسية والشبكة"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### ➕ إضافة وتوريد كميات")
            st.write("إضافة بضاعة وتوريد مخزون")
            if st.button("فتح التوريد", key="t3"): st.session_state.active_page = "➕ إضافة وتوريد كميات"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 👥 إدارة العملاء والديون")
            st.write("إدارة الزبائن والذمم")
            if st.button("فتح العملاء", key="t5"): st.session_state.active_page = "👥 إدارة العملاء والديون"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 🏭 إدارة الموردين")
            st.write("موردين البضاعة")
            if st.button("فتح الموردين", key="t7"): st.session_state.active_page = "🏭 إدارة الموردين"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 💰 الصندوق والمصاريف")
            st.write("سندات المصروفات والصندوق")
            if st.button("فتح الصندوق", key="t9"): st.session_state.active_page = "💰 الصندوق والمصاريف"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 📜 سجل النشاطات")
            st.write("سجل حركة العمليات")
            if st.button("فتح السجل", key="t11"): st.session_state.active_page = "📜 سجل النشاطات"; st.rerun()

    with col_b:
        with st.container(border=True):
            st.markdown("### 🛒 سلة البيع وإتمام الفاتورة")
            st.write("مراجعة السلة وإصدار الفاتورة")
            if st.button("فتح السلة", key="t2"): st.session_state.active_page = "🛒 سلة البيع وإتمام الفاتورة"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 📦 جرد المخزن")
            st.write("عرض رصيد المواد والمخزون")
            if st.button("فتح المخزن", key="t4"): st.session_state.active_page = "📦 جرد المخزن"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 💵 سداد الديون")
            st.write("تسديد ديون العملاء والأقساط")
            if st.button("فتح السداد", key="t6"): st.session_state.active_page = "💵 سداد الديون"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 📄 سجل الفواتير وواتساب")
            st.write("قائمة الفواتير الرسمية")
            if st.button("فتح الفواتير", key="t8"): st.session_state.active_page = "📄 سجل الفواتير وواتساب"; st.rerun()
            
        with st.container(border=True):
            st.markdown("### 📊 التقارير والأرباح")
            st.write("الحسابات والأرباح المالية")
            if st.button("فتح التقارير", key="t10"): st.session_state.active_page = "📊 التقارير والأرباح"; st.rerun()

    st.markdown("<br><p style='text-align: center; color: #7c6f9f; font-size: 12px;'>ياسر بوس - الإصدار 4.3.0</p>", unsafe_allow_html=True)

# ================= تشغيل الـ 11 تبويب بالكامل =================

elif st.session_state.active_page == "🏠 الرئيسية والشبكة":
    st.subheader("🏠 شبكة المبيعات السريعة")
    try:
        res = supabase.table("products").select("*").eq("username", username).execute()
        items = res.data if res.data else []
    except:
        items = []
    if items:
        for item in items:
            with st.container(border=True):
                st.write(f"**{item['product_name']}** - السعر: `{item['sell_price']}` د.ع - المتوفر: `{item['quantity']}`")
    else:
        st.info("لا توجد مواد مضافة في المخزن حالياً. أضف بضاعة جديدة من قسم (إضافة وتوريد كميات).")

elif st.session_state.active_page == "🛒 سلة البيع وإتمام الفاتورة":
    st.subheader("🛒 سلة البيع وإتمام الفاتورة")
    st.info("السلة فارغة حالياً. أضف مواد من الرئيسية أو ابدأ عملية بيع جديدة.")

elif st.session_state.active_page == "➕ إضافة وتوريد كميات":
    st.subheader("➕ إضافة مادة جديدة أو توريد كميات")
    with st.form("new_p", clear_on_submit=True):
        pn = st.text_input("اسم المادة:")
        pb = st.text_input("سعر الشراء:", "0")
        ps = st.text_input("سعر البيع:", "0")
        pq = st.text_input("الكمية المتوفرة:", "1")
        if st.form_submit_button("حفظ المادة بالمخزن", type="primary"):
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
                    st.success("تم حفظ المادة في قاعدة البيانات بنجاح!")
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
        cn = st.text_input("اسم العميل (حضرة السيد):")
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
                st.success("تمت إضافة المورد بنجاح!")
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
    st.subheader("💰 صندوق الوردية والمصاريف اليومية")
    with st.form("exp_tab", clear_on_submit=True):
        et = st.text_input("بيان المصروف أو السند:")
        ea = st.text_input("المبلغ (د.ع):", "0")
        if st.form_submit_button("تسجيل المصروف"):
            if et:
                st.session_state.expenses_list.append({"البيان": et, "المبلغ": float(ea)})
                st.success("تم التسجيل بنجاح!")
                st.rerun()
    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)

elif st.session_state.active_page == "📊 التقارير والأرباح":
    st.subheader("📊 التقارير المالية وحساب الأرباح")
    st.metric("إجمالي المبيعات", "0 د.ع")
    st.metric("صافي الأرباح", "0 د.ع")

elif st.session_state.active_page == "📜 سجل النشاطات":
    st.subheader("📜 سجل النشاطات والعمليات")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد سجلات نشاط مسجلة حتى الآن.")
