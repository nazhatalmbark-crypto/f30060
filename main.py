import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from supabase import create_client, Client
import datetime
import json
import urllib.parse
import barcode
from barcode.writer import ImageWriter
import io

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co"
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web POS", layout="wide")

# **تنسيق التصميم البنفسجي الحديث وواجهة الموبايل**
st.markdown("""
    <style>
    .stApp {
        background-color: #553c9a;
        direction: rtl;
        text-align: right;
        font-family: system-ui, -apple-system, sans-serif;
    }
    input, select, textarea {
        direction: rtl;
        text-align: right;
    }
    .hide-scroll::-webkit-scrollbar { display: none; }
    </style>
""", unsafe_allow_html=True)

# **جلسات النظام الأساسية**
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "مشرف النظام"
if "current_view" not in st.session_state:
    st.session_state.current_view = "dashboard"
if "suppliers_list" not in st.session_state:
    st.session_state.suppliers_list = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "expenses_list" not in st.session_state:
    st.session_state.expenses_list = []
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

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
                <h2>YASSER WEB - فاتورة طلبية رسمية</h2>
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
            <div class="footer"><p>شكراً لتعاملكم معنا - Yasser Web POS</p></div>
        </div>
    </body>
    </html>
    """

# **شاشة تسجيل الدخول الأنيقة**
if not st.session_state.logged_in_user:
    st.markdown("<h2 style='text-align: center; color: white;'>🔐 بوابة الدخول لحسابات المحلات والنظام</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_modern_form"):
            login_user = st.text_input("اسم المستخدم أو اسم المحل:")
            login_role = st.selectbox("حدد الصلاحية عند الدخول:", ["مشرف النظام", "كاشير", "مسؤول مبيعات"])
            sub_log = st.form_submit_button("تسجيل الدخول", type="primary")
            if sub_log:
                if login_user.strip():
                    try:
                        res = supabase.table("users").select("*").eq("username", login_user.strip()).execute()
                        if res.data:
                            user_info = res.data[0]
                            st.session_state.logged_in_user = str(user_info["username"])
                            st.session_state.user_role = str(login_role)
                            st.session_state.is_vip = bool(user_info.get("is_paid", False))
                            log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {user_info['username']}")
                            st.success("تم تسجيل الدخول بنجاح!")
                            st.rerun()
                        else:
                            supabase.table("users").insert({"username": login_user.strip(), "is_paid": False}).execute()
                            st.session_state.logged_in_user = str(login_user.strip())
                            st.session_state.user_role = str(login_role)
                            st.success("تم إنشاء الحساب وتسجيل الدخول بنجاح!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

# **شريط الإعدادات الجانبي (Sidebar)**
st.sidebar.title("⚙️ إعدادات الحساب")
st.sidebar.write(f"👤 المستخدم: **{username}**")
st.sidebar.write(f"👤 الصلاحية: **{user_role}**")
cart_total_count = sum(int(item['qty']) for item in st.session_state.cart)
st.sidebar.info(f"🛒 المواد بالسلة: **{cart_total_count}**")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in_user = None
    st.session_state.cart = []
    st.rerun()

st.divider()

# **قائمة التبويبات الـ 11 الكاملة مدعومة بالتصميم المبتكر**
tab_titles = [
    "🏠 الرئيسية والشبكة",
    "🛒 سلة البيع وإتمام الفاتورة",
    "➕ إضافة وتوريد كميات", 
    "📦 جرد المخزن", 
    "👥 إدارة العملاء والديون", 
    "💵 سداد الديون",
    "🏭 إدارة الموردين",
    "📄 سجل الفواتير وواتساب", 
    "💰 الصندوق والمصاريف", 
    "📊 التقارير والأرباح",
    "📜 سجل النشاطات"
]

selected_tab = st.radio("القائمة الرئيسية:", tab_titles, horizontal=True)

st.divider()

# ================= TAB 1: الرئيسية وشبكة المبيعات =================
if selected_tab == "🏠 الرئيسية والشبكة":
    st.markdown("### 🛍️ شبكة المواد المتاحة للبيع السريع")
    try:
        res_grid = supabase.table("products").select("*").eq("username", username).execute()
        grid_items = res_grid.data if res_grid.data else []
    except:
        grid_items = []

    if grid_items:
        g_cols = st.columns(3)
        for idx, item in enumerate(grid_items):
            with g_cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"#### 📦 {item['product_name']}")
                    st.markdown(f"💰 السعر المفرد: `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🔢 المتوفر بالمخزن: `{item['quantity']}` قطعة")
                    if item['quantity'] > 0:
                        if st.button("➕ إضافة للسلة", key=f"fast_add_{item['id']}"):
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
                                    "color": item.get('color', ''),
                                    "size": item.get('size', ''),
                                    "sell_price": item["sell_price"],
                                    "buy_price": item["buy_price"],
                                    "max_qty": item["quantity"],
                                    "qty": 1
                                })
                            st.toast("✅ تمت الإضافة للسلة بنجاح!", icon="🛒")
                            st.rerun()
                    else:
                        st.error("نفدت الكمية")
    else:
        st.info("لا توجد مواد في المخزن. توجه إلى تبويب (إضافة وتوريد كميات) لإضافة بضاعة جديدة.")

# ================= TAB 2: سلة البيع وإتمام الفاتورة =================
elif selected_tab == "🛒 سلة البيع وإتمام الفاتورة":
    st.markdown("### 🛒 مراجعة السلة وإتمام الفاتورة (مع التعبئة التلقائية للعميل)")
    if st.session_state.cart:
        total_cart_price = 0
        for idx, c_item in enumerate(st.session_state.cart):
            cols_c = st.columns([3, 2, 2, 1])
            with cols_c[0]:
                st.write(f"**{c_item['product_name']}**")
            with cols_c[1]:
                new_q = st.number_input("العدد", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_qty_{c_item['id']}")
                c_item['qty'] = new_q
            with cols_c[2]:
                item_sum = c_item['sell_price'] * c_item['qty']
                total_cart_price += item_sum
                st.write(f"المجموع: **{int(item_sum):,}** د.ع")
            with cols_c[3]:
                if st.button("❌", key=f"remove_c_{c_item['id']}"):
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
            st.warning("⚠️ تنبيه: يرجى إضافة عميل أولاً من تبويب (إدارة العملاء والديون) لتتمكن من إتمام الفاتورة!")
            selected_cust_name = ""
        else:
            cust_names = [c["customer_name"] for c in customer_records]
            selected_cust_name = st.selectbox("اختر اسم الزبون (للتعبئة التلقائية لرقمه وعنوانه):", cust_names)
            
            selected_cust_obj = next((c for c in customer_records if c["customer_name"] == selected_cust_name), None)
            if
