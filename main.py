import streamlit as st
import pandas as pd
import subprocess
import sys

def install_packages():
    packages = ["streamlit", "pandas", "supabase", "python-barcode", "arabic-reshaper", "python-bidi"]
    for pkg in packages:
        try:
            __import__(pkg if pkg != "python-bidi" else "bidi")
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

install_packages()

import datetime
import io
import json
import urllib.parse
import barcode
from barcode.writer import ImageWriter
from supabase import create_client, Client
import arabic_reshaper
from bidi.algorithm import get_display

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - النظام الشامل لإدارة المحلات", page_icon="🛍️", layout="wide")

# تعديلات CSS متقدمة لإخفاء الخطوط الزائدة وضمان التوافق التام مع الموبايل وتنسيق القوائم العمودية
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    input, select, textarea {
        direction: rtl;
        text-align: right;
    }
    hr {
        border: none;
        height: 0px;
        margin: 0px;
    }
    /* تحسين شكل الأزرار والقوائم على الهواتف */
    @media (max-width: 768px) {
        .stButton button {
            width: 100%;
        }
    }
    </style>
""", unsafe_allow_html=True)

if "lang" not in st.session_state:
    st.session_state.lang = "العربية"

lang_dict = {
    "العربية": {
        "title": "🛍️ نظام Yasser Web الشامل لإدارة المبيعات والمخزون",
        "login_title": "🔐 بوابة الدخول لحسابات المحلات والنظام",
        "login_tab": "🔑 تسجيل الدخول",
        "signup_tab": "✨ إنشاء حساب جديد",
        "username_label": "اسم المستخدم أو اسم المحل:",
        "login_btn": "تسجيل الدخول",
        "signup_btn": "إنشاء الحساب الآن",
        "settings": "⚙️ إعدادات الحساب والنسخ الاحتياطي",
        "lang_select": "🌐 اللغة / Language",
        "role_label": "👤 الصلاحية:",
        "cart_badge": "🛒 المواد الحالية بالسلة:",
        "backup_title": "🔄 النسخ الاحتياطي الفوري للبيانات",
        "backup_download": "📥 تحميل نسخة احتياطية (JSON)",
        "backup_upload": "📂 استعادة البيانات من ملف سابق",
        "logout": "تسجيل الخروج",
        "menu_title": "📑 القوائم الرئيسية للنظام",
        "tabs": [
            "➕ إضافة مادة جديدة", 
            "📦 جرد المخزن والباركود", 
            "👥 إدارة العملاء والديون", 
            "🏭 إدارة الموردين",
            "🛒 إتمام البيع والفواتير", 
            "📄 سجل الفواتير والطباعة وواتساب", 
            "💵 صندوق سداد", 
            "📊 الرسوم البيانية والتقارير",
            "📜 سجل النشاطات (Audit Trail)",
            "📖 دليل الاستخدام والمميزات والدعم"
        ]
    }
}

t = lang_dict[st.session_state.lang]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "user_role" not in st.session_state:
    st.session_state.user_role = "مشرف النظام"

if "customer_list" not in st.session_state or isinstance(st.session_state.customer_list, pd.DataFrame):
    st.session_state.customer_list = []

if "suppliers_list" not in st.session_state or isinstance(st.session_state.suppliers_list, pd.DataFrame):
    st.session_state.suppliers_list = []

if "invoices_list" not in st.session_state or isinstance(st.session_state.invoices_list, pd.DataFrame):
    st.session_state.invoices_list = []

if "cart" not in st.session_state or isinstance(st.session_state.cart, pd.DataFrame):
    st.session_state.cart = []

if "expenses_list" not in st.session_state or isinstance(st.session_state.expenses_list, pd.DataFrame):
    st.session_state.expenses_list = []

if "payments_receipts" not in st.session_state:
    st.session_state.payments_receipts = []

if "audit_logs" not in st.session_state or isinstance(st.session_state.audit_logs, pd.DataFrame):
    st.session_state.audit_logs = []

if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

if "vip_expiry_date" not in st.session_state:
    st.session_state.vip_expiry_date = None

def log_audit(action, details):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = st.session_state.logged_in_user or "زائر"
    role = st.session_state.user_role
    if isinstance(st.session_state.audit_logs, pd.DataFrame):
        st.session_state.audit_logs = []
    st.session_state.audit_logs.insert(0, {
        "التاريخ والوقت": str(timestamp),
        "المستخدم": str(user),
        "الصلاحية": str(role),
        "العملية": str(action),
        "التفاصيل": str(details)
    })

def generate_html_invoice(inv, store_name):
    items_html = ""
    items_list_str = str(inv['المنتجات']).split(" , ")
    for item in items_list_str:
        items_html += f"<li>{item}</li>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {inv['رقم الفاتورة']}</title>
        <style>
            body {{ font-family: 'Cairo', Tahoma, sans-serif; background: #fff; color: #333; padding: 20px; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); border-radius: 8px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #333; padding-bottom: 10px; }}
            .details {{ margin: 20px 0; font-size: 16px; }}
            .items {{ margin: 20px 0; }}
            .items ul {{ list-style-type: none; padding: 0; }}
            .items li {{ background: #f9f9f9; margin-bottom: 8px; padding: 10px; border-radius: 5px; border-right: 4px solid #007bff; }}
            .totals {{ margin-top: 20px; border-top: 1px solid #ddd; padding-top: 15px; font-size: 18px; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 14px; color: #777; }}
            .print-btn {{ background: #007bff; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; display: block; margin: 20px auto; }}
            @media print {{ .print-btn {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <h2>{store_name} - فاتورة مبيعات رسمية</h2>
                <div>التاريخ: {inv['التاريخ']}</div>
            </div>
            <div class="details">
                <p><strong>رقم الفاتورة:</strong> {inv['رقم الفاتورة']}</p>
                <p><strong>اسم الزبون:</strong> {inv['الزبون']}</p>
                <p><strong>طريقة الدفع:</strong> {inv['نوع الدفع']}</p>
            </div>
            <div class="items">
                <h3>تفاصيل المنتجات والمواد:</h3>
                <ul>{items_html}</ul>
            </div>
            <div class="totals">
                <p>المبلغ الكلي: {int(inv['المبلغ الكلي']):,} دينار عراقي</p>
                <p>المبلغ الواصل: {int(inv['الواصل']):,} دينار عراقي</p>
                <p>المتبقي (الدين): {int(inv['المتبقي (الدين)']):,} دينار عراقي</p>
            </div>
            <div class="footer">
                <p>شكراً لتعاملكم معنا! نظام Yasser Web لإدارة المحلات</p>
            </div>
            <button class="print-btn" onclick="window.print()">طباعة الفاتورة أو حفظها PDF</button>
        </div>
    </body>
    </html>
    """
    return html_content

st.title(t["title"])

if not st.session_state.logged_in_user:
    st.subheader(t["login_title"])
    
    auth_tab1, auth_tab2 = st.tabs([t["login_tab"], t["signup_tab"]])
    
    with auth_tab1:
        with st.form("login_form"):
            login_user = st.text_input(t["username_label"])
            login_role = st.selectbox("حدد الصلاحية عند الدخول:", ["مشرف النظام", "كاشير", "مسؤول مبيعات"])
            login_submitted = st.form_submit_button(t["login_btn"], type="primary")
            
            if login_submitted:
                if login_user.strip():
                    try:
                        res = supabase.table("users").select("*").eq("username", login_user.strip()).execute()
                        if res.data:
                            user_info = res.data[0]
                            st.session_state.logged_in_user = str(user_info["username"])
                            st.session_state.user_role = str(login_role)
                            is_paid_db = bool(user_info.get("is_paid", False))
                            st.session_state.is_vip = is_paid_db
                            if is_paid_db:
                                st.session_state.vip_expiry_date = datetime.datetime.now() + datetime.timedelta(days=30)
                            log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {user_info['username']} بصلاحية ({login_role})")
                            st.success("تم تسجيل الدخول بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ اسم المستخدم غير موجود، يرجى إنشاء حساب جديد.")
                    except Exception as e:
                        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
                    
    with auth_tab2:
        with st.form("signup_form"):
            new_user = st.text_input("اختر اسم المستخدم أو اسم المحل الجديد:")
            signup_role = st.selectbox("حدد الصلاحية للحساب الجديد:", ["مشرف النظام", "كاشير", "مسؤول مبيعات"])
            signup_submitted = st.form_submit_button(t["signup_btn"], type="primary")
            
            if signup_submitted:
                if new_user.strip():
                    try:
                        check_res = supabase.table("users").select("*").eq("username", new_user.strip()).execute()
                        if check_res.data:
                            st.error("❌ اسم المستخدم هذا مستخدم مسبقاً، اختر اسم آخر.")
                        else:
                            supabase.table("users").insert({
                                "username": new_user.strip(),
                                "is_paid": False
                            }).execute()
                            st.session_state.logged_in_user = str(new_user.strip())
                            st.session_state.user_role = str(signup_role)
                            st.session_state.is_vip = False
                            log_audit("إنشاء حساب جديد", f"تم إنشاء حساب جديد باسم {new_user.strip()} بصلاحية ({signup_role})")
                            st.success("🎉 تم إنشاء الحساب وتسجيل الدخول بنجاح!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"خطأ في إنشاء الحساب بقاعدة البيانات: {e}")
                else:
                    st.warning("يرجى كتابة اسم المستخدم الجديد.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

st.sidebar.title(t["settings"])
selected_lang = st.sidebar.selectbox(t["lang_select"], ["العربية", "English"], index=0 if st.session_state.lang=="العربية" else 1)
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun()

t = lang_dict[st.session_state.lang]

st.sidebar.write(f"👤 المستخدم: **{username}**")
st.sidebar.write(f"{t['role_label']} **{user_role}**")

cart_count_badge = sum(int(item['qty']) for item in st.session_state.cart)
st.sidebar.info(f"{t['cart_badge']} **{cart_count_badge}**")

st.sidebar.markdown("---")
st.sidebar.subheader(t["backup_title"])

backup_data = {
    "username": str(username),
    "customers": list(st.session_state.customer_list),
    "suppliers": list(st.session_state.suppliers_list),
    "invoices": list(st.session_state.invoices_list),
    "expenses": list(st.session_state.expenses_list),
    "payments_receipts": list(st.session_state.payments_receipts),
    "audit_logs": list(st.session_state.audit_logs),
    "export_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
}
backup_json = json.dumps(backup_data, ensure_ascii=False, indent=4, default=str)
st.sidebar.download_button(
    label=t["backup_download"],
    data=backup_json,
    file_name=f"yasser_web_backup_{username}_{datetime.datetime.now().strftime('%Y%m%d')}.json",
    mime="application/json"
)

uploaded_backup = st.sidebar.file_uploader(t["backup_upload"], type=["json"])
if uploaded_backup is not None:
    try:
        restored_data = json.load(uploaded_backup)
        if "customers" in restored_data and "invoices" in restored_data:
            st.session_state.customer_list = restored_data.get("customers", [])
            st.session_state.suppliers_list = restored_data.get("suppliers", [])
            st.session_state.invoices_list = restored_data.get("invoices", [])
            st.session_state.expenses_list = restored_data.get("expenses", [])
            st.session_state.payments_receipts = restored_data.get("payments_receipts", [])
            st.session_state.audit_logs = restored_data.get("audit_logs", [])
            log_audit("استعادة بيانات", "تم استعادة البيانات بنجاح من ملف نسخ احتياطي خارجي")
            st.sidebar.success("✅ تمت استعادة البيانات بنجاح!")
            st.rerun()
        else:
            st.sidebar.error("❌ ملف النسخة الاحتياطي غير صالح.")
    except Exception as e:
        st.sidebar.error(f"خطأ في استعادة الملف: {e}")

st.sidebar.markdown("---")

# نظام التحقق من الأيام المتبقية للنسخة المدفوعة VIP
if st.session_state.is_vip and st.session_state.vip_expiry_date:
    remaining_days = (st.session_state.vip_expiry_date - datetime.datetime.now()).days
    if remaining_days < 0:
        remaining_days = 0
        st.session_state.is_vip = False
        st.sidebar.error("⚠️ انتهت صلاحية اشتراكك في النسخة المدفوعة! يرجى تجديد الاشتراك.")
    else:
        st.sidebar.success(f"🌟 النسخة المدفوعة مفعلة\n⏳ متبقي من اشتراكك: **{remaining_days} يوم**")

if not st.session_state.is_vip:
    st.sidebar.warning("🔒 حالة النسخة: **مجانية (محدودة)**")
    vip_code = st.sidebar.text_input("أدخل كود تجديد/تفعيل النسخة المدفوعة (VIP):", type="password")
    if st.sidebar.button("تفعيل الاشتراك الجديد"):
        if vip_code.strip() == "YASSER2026":
            st.session_state.is_vip = True
            st.session_state.vip_expiry_date = datetime.datetime.now() + datetime.timedelta(days=30)
            try:
                supabase.table("users").update({"is_paid": True}).eq("username", username).execute()
            except Exception:
                pass
            log_audit("تفعيل النسخة المدفوعة", "تم تفعيل أو تجديد النسخة المدفوعة VIP لمدة 30 يوم بنجاح")
            st.sidebar.success("🎉 تم تفعيل النسخة المدفوعة لمدة 30 يوم بنجاح!")
            st.rerun()
        else:
            st.sidebar.error("كود التفعيل غير صحيح!")

if st.sidebar.button(t["logout"]):
    log_audit("تسجيل خروج", f"تم تسجيل الخروج للمستخدم {username}")
    st.session_state.logged_in_user = None
    st.session_state.is_vip = False
    st.session_state.cart = []
    st.rerun()

st.markdown("---")

# تنظيم الخزانات والقوائم بشكل عمودي (وحدة جوة وحدة) لجميع الأجهزة بدون شريط أفقي متعب
st.subheader(t["menu_title"])
selected_tab_name = st.radio("اختر القسم المطلوب:", t["tabs"], label_visibility="collapsed")

# توزيع الأقسام بناءً على الاختيار العمودي
if selected_tab_name == t["tabs"][0]:
    st.subheader("➕ واجهة إضافة مادة أو بضاعة جديدة للمخزن")
    if user_role == "كاشير":
        st.warning("⚠️ عذراً، حساب الكاشير لا يمتلك صلاحية إضافة أو تعديل المواد في المخزن.")
    else:
        try:
            res_prod_count = supabase.table("products").select("id").eq("username", username).execute()
            current_count = len(res_prod_count.data) if res_prod_count.data else 0
        except Exception:
            current_count = 0
            
        if not st.session_state.is_vip and current_count >= 5:
            st.warning("⚠️ **تنبيه النسخة المجانية:** وصلت للحد الأقصى (5 منتجات). قم بتجديد أو تفعيل النسخة المدفوعة لإضافة منتجات بلا حدود!")
        else:
            with st.form("add_product_clean_form", clear_on_submit=True):
                p_name = st.text_input("اسم المادة / المنتج / الجهاز:")
                
                c_col, c_sz = st.columns(2)
                with c_col:
                    p_color = st.text_input("اللون / المواصفات الإضافية (اختياري):", "عام")
                with c_sz:
                    p_size = st.text_input("القياس / السعة / الحجم (اختياري):", "عام")
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    p_buy_str = st.text_input("سعر الشراء (د.ع):", "0")
                with c2:
                    p_sell_str = st.text_input("سعر البيع (د.ع):", "0")
                with c3:
                    p_qty_str = st.text_input("الكمية المتوفرة:", "1")
                with c4:
                    p_barcode = st.text_input("رمز الباركود (اختياري):", "")
                
                submitted = st.form_submit_button("حفظ المادة في المخزن", type="primary")
                if submitted:
                    if p_name.strip():
                        try:
                            p_buy = float(p_buy_str.strip())
                            p_sell = float(p_sell_str.strip())
                            p_qty = int(p_qty_str.strip())
                            
                            if p_sell < p_buy:
                                st.warning("⚠️ تنبيه: سعر البيع أقل من سعر الشراء (خسارة).")
                            
                            supabase.table("products").insert({
                                "username": str(username),
                                "product_name": str(p_name.strip()),
                                "color": str(p_color.strip() if p_color else "عام"),
                                "size": str(p_size.strip() if p_size else "عام"),
                                "buy_price": float(p_buy),
                                "sell_price": float(p_sell),
                                "quantity": int(p_qty),
                                "barcode": str(p_barcode.strip() if p_barcode else "بدون")
                            }).execute()
                            log_audit("إضافة منتج", f"تمت إضافة المنتج ({p_name.strip()}) بكمية {p_qty}")
                            st.success(f"تمت إضافة المادة ({p_name}) بنجاح!")
                            st.rerun()
                        except ValueError:
                            st.error("❌ خطأ: يرجى إدخال أرقام صحيحة حصراً.")
                        except Exception as e:
                            st.error(f"❌ خطأ في حفظ المنتج بقاعدة البيانات: {e}")
                    else:
                        st.warning("يرجى كتابة اسم المادة على الأقل.")

elif selected_tab_name == t["tabs"][1]:
    st.subheader("📦 جرد المخزن الشامل مع ميزة توليد وطباعة الباركود وحساب أرباح القطع")
    
    try:
        res_all_p = supabase.table("products").select("*").eq("username", username).execute()
        all_products = res_all_p.data if res_all_p.data else []
    except:
        all_products = []

    low_stock_items = [p for p in all_products if p['quantity'] <= 2]
    if low_stock_items:
        low_names = " ، ".join([f"**{i['product_name']}** ({i.get('color','')} - {i.get('size','')})" for i in low_stock_items])
        st.error(f"🚨 **تنبيه قرب نفاد المخزون (Low Stock Alerts):** المواد التالية وشيكة النفاذ أو نفدت تماماً: {low_names}")

    if st.session_state.cart:
        total_items_in_cart = sum(int(i['qty']) for i in st.session_state.cart)
        total_price_preview = sum(float(i['sell_price']) * int(i['qty']) for i in st.session_state.cart)
        st.success(f"🛒 **السلة حالياً تحتوي على:** {total_items_in_cart} قطعة | المجموع المؤقت: **{int(total_price_preview):,} د.ع**")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search_prod_term = st.text_input("🔍 بحث سريع عن اسم المادة أو المنتج:", "")
    with col_s2:
        search_barcode_term = st.text_input("📷 بحث سريع بالباركود / الرمز:", "")

    if all_products:
        filtered_products = all_products
        if search_prod_term:
            filtered_products = [p for p in filtered_products if search_prod_term.lower() in p['product_name'].lower() or search_prod_term.lower() in p.get('color','').lower()]
        if search_barcode_term:
            filtered_products = [p for p in filtered_products if search_barcode_term.lower() in p.get('barcode','').lower()]

        cols = st.columns(3)
        for idx, item in enumerate(filtered_products):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### 📦 {item['product_name']}")
                    st.markdown(f"🎨 **اللون:** `{item.get('color', 'عام')}` | 📏 **القياس:** `{item.get('size', 'عام')}`")
                    st.markdown(f"🏷️ **الباركود:** `{item.get('barcode', 'بدون')}`")
                    st.markdown(f"💰 **سعر الشراء:** `{int(item['buy_price']):,}` د.ع | **سعر البيع:** `{int(item['sell_price']):,}` د.ع")
                    
                    buy_p = float(item.get('buy_price', 0))
                    sell_p = float(item.get('sell_price', 0))
                    profit_per_unit = int(sell_p - buy_p)
                    
                    if profit_per_unit < 0:
                        st.error(f"📉 ربح القطعة: {profit_per_unit:,} د.ع (خسارة!)")
                    elif profit_per_unit == 0:
                        st.warning(f"⚠️ ربح القطعة: 0 د.ع (بدون ربح)")
                    else:
                        st.success(f"📈 ربح القطعة: +{profit_per_unit:,} د.ع")
                    
                    if item['quantity'] <= 2:
                        st.error(f"🔢 **الكمية المتوفرة:** `{int(item['quantity'])}` قطعة (مخزون منخفض!)")
                    else:
                        st.markdown(f"🔢 **الكمية المتوفرة:** `{int(item['quantity'])}` قطعة")
                    
                    with st.expander("🏷️ توليد وعرض باركود المادة"):
                        b_code_val = item.get('barcode', '')
                        if not b_code_val or b_code_val == "بدون":
                            b_code_val = f"PRD{item['id']}"
                        try:
                            rv = barcode.get('code128', str(b_code_val), writer=ImageWriter())
                            buffer_bc = io.BytesIO()
                            rv.write(buffer_bc)
                            st.image(buffer_bc.getvalue(), caption=f"باركود: {b_code_val}", width=200)
                        except Exception as ex:
                            st.error(f"تعذر توليد الباركود: {ex}")

                    if item['quantity'] > 0:
                        if st.button(f"🛒 إضافة إلى السلة", key=f"add_cart_{item['id']}"):
                            found_in_cart = False
                            for cart_item in st.session_state.cart:
                                if cart_item["id"] == item["id"]:
                                    if cart_item["qty"] < item["quantity"]:
                                        cart_item["qty"] += 1
                                    found_in_cart = True
                                    break
                            if not found_in_cart:
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
                            st.toast(f"✅ تمت إضافة ({item['product_name']}) إلى السلة!", icon="🛍️")
                            st.rerun()
                    else:
                        st.warning("⚠️ نفذت الكمية")
    else:
        st.info("المخزن فارغ حالياً. أضف مواد من تبويب (إضافة مادة جديدة).")

elif selected_tab_name == t["tabs"][2]:
    st.subheader("👥 إدارة العملاء ومتابعة الديون والذمم")
    iraq_govs = ["بغداد", "البصرة", "نينوى", "أربيل", "النجف", "كربلاء", "ذي قار", "بابل", "الأنبار", "ديالى", "كركوك", "صلاح الدين", "المثنى", "ميسان", "القادسية", "واسط", "دهوك", "السليمانية"]
    
    with st.form("add_customer_clean_form", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            c_name = st.text_input("اسم الزبون / العميل:")
        with col_c2:
            c_phone = st.text_input("رقم الهاتف:")
        with col_c3:
            c_gov = st.selectbox("المحافظة:", iraq_govs)
            
        c_address = st.text_input("العنوان التفصيلي / المنطقة:")
        c_notes = st.text_area("ملاحظات إضافية عن العميل:")
            
        if st.form_submit_button("تسجيل بيانات العميل"):
            if c_name and c_phone:
                st.session_state.customer_list.append({
                    "اسم العميل": str(c_name), 
                    "رقم الهاتف": str(c_phone), 
                    "المحافظة": str(c_gov),
                    "العنوان": str(c_address if c_address else "غير محدد"),
                    "ملاحظات": str(c_notes if c_notes else "لا يوجد"),
                    "تاريخ التسجيل": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                })
                log_audit("إضافة عميل", f"تم تسجيل العميل {c_name} برقم {c_phone}")
                st.success(f"تم تسجيل العميل ({c_name}) بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى كتابة الاسم ورقم الهاتف.")

    st.markdown("---")
    st.subheader("📋 سجل العملاء والذمم المالية المستحقة")
    if st.session_state.customer_list:
        search_cust = st.text_input("🔍 بحث عن عميل بالاسم أو رقم الهاتف:", "")
        filtered_cust = [c for c in st.session_state.customer_list if search_cust.lower() in c['اسم العميل'].lower() or search_cust in c['رقم الهاتف']]
        st.dataframe(pd.DataFrame(filtered_cust), use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلون حالياً.")

elif selected_tab_name == t["tabs"][3]:
    st.subheader("🏭 إدارة الموردين وشركات التجهيز والجملة")
    
    with st.form("add_supplier_form", clear_on_submit=True):
        sup_name = st.text_input("اسم المورد أو شركة التجهيز:")
        sup_phone = st.text_input("رقم هاتف المورد:")
        sup_notes = st.text_input("نوع البضاعة الموردة:")
        
        if st.form_submit_button("إضافة المورد للقائمة"):
            if sup_name.strip():
                st.session_state.suppliers_list.append({
                    "اسم المورد": str(sup_name.strip()),
                    "رقم الهاتف": str(sup_phone.strip() if sup_phone else "غير محدد"),
                    "التخصص": str(sup_notes.strip() if sup_notes else "عام"),
                    "تاريخ الإضافة": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                })
                log_audit("إضافة مورد", f"تم إضافة المورد {sup_name.strip()}")
                st.success(f"تم إضافة المورد ({sup_name}) بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى إدخال اسم المورد على الأقل.")
                
    st.markdown("---")
    st.subheader("📋 قائمة الموردين المسجلين")
    if st.session_state.suppliers_list:
        st.dataframe(pd.DataFrame(st.session_state.suppliers_list), use_container_width=True)
    else:
        st.info("لا توجد جهات موردة مسجلة حالياً.")

elif selected_tab_name == t["tabs"][4]:
    st.subheader("🛒 سلة المبيعات (تجميع مواد الزبون وإتمام الفاتورة)")
    
    if st.session_state.cart:
        st.write("### 🛍️ المواد التي اختارها الزبون للفاتورة الحالية:")
        total_cart_price = 0
        
        for idx, c_item in enumerate(st.session_state.cart):
            cols_cart = st.columns([3, 2, 2, 1])
            with cols_cart[0]:
                st.write(f"**{c_item['product_name']}** ({c_item['color']} / {c_item['size']}) - {int(c_item['sell_price']):,} د.ع")
            with cols_cart[1]:
                new_q = st.number_input(f"الكمية", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_q_{c_item['id']}")
                c_item['qty'] = new_q
            with cols_cart[2]:
                item_total = c_item['sell_price'] * c_item['qty']
                total_cart_price += item_total
                st.write(f"المجموع: **{int(item_total):,}** د.ع")
            with cols_cart[3]:
                if st.button("❌ حذف", key=f"del_cart_{c_item['id']}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        st.markdown("---")
        st.markdown(f"### 💵 المجموع الكلي لكل المواد: **{int(total_cart_price):,} د.ع**")
        
        if not st.session_state.customer_list:
            st.warning("⚠️ تنبيه: يجب إضافة وتسجيل العميل أولاً من تبويب (إدارة العملاء)!")
            customer_options = ["لا توجد عملاء مسجلين"]
        else:
            customer_options = [c["اسم العميل"] for c in st.session_state.customer_list]
            
        cust_name = st.selectbox("اختر اسم الزبون للفاتورة (إلزامي):", customer_options)
        
        pay_type = st.radio("طريقة الدفع ونوع الفاتورة:", ["🟡 نقد بالكامل (كاش)", "🔴 آجل بالكامل (دين)", "🔵 دفعة جزئية"], horizontal=True)
        
        paid_amount = 0
        if pay_type == "🟡 نقد بالكامل (كاش)":
            paid_amount = total_cart_price
        elif pay_type == "🔴 آجل بالكامل (دين)":
            paid_amount = 0
        else:
            paid_amount_str = st.text_input("المبلغ الواصل (المدفوع حالياً):", "0")
            try:
                paid_amount = float(paid_amount_str.strip())
                if paid_amount < 0: paid_amount = 0
                if paid_amount > total_cart_price: paid_amount = total_cart_price
            except ValueError:
                paid_amount = 0
            
        remaining_amount = total_cart_price - paid_amount

        if st.button("💾 إتمام البيع، خصم المخزن، وحفظ الفاتورة", type="primary"):
            if not st.session_state.customer_list or cust_name == "لا توجد عملاء مسجلين":
                st.error("❌ خطأ: لا يمكن حفظ الفاتورة بدون اختيار عميل مسجل بالنظام!")
            else:
                try:
                    prod_names_str = []
                    total_buy_cost_of_invoice = 0
                    
                    for c_item in st.session_state.cart:
                        prod_names_str.append(f"{c_item['product_name']} ({c_item['color']} / {c_item['size']}) [Qty: {c_item['qty']}]")
                        total_buy_cost_of_invoice += (c_item['buy_price'] * c_item['qty'])
                        
                        res_p = supabase.table("products").select("quantity").eq("id", c_item["id"]).execute()
                        if res_p.data:
                            current_db_qty = res_p.data[0]["quantity"]
                            new_db_qty = max(0, current_db_qty - c_item['qty'])
                            supabase.table("products").update({"quantity": new_db_qty}).eq("id", c_item["id"]).execute()
                    
                    inv_id = len(st.session_state.invoices_list) + 1
                    inv_code = f"INV-{inv_id:03d}"
                    
                    if remaining_amount == 0:
                        inv_color_status = "🟢 مسددة بالكامل (كاش)"
                    else:
                        inv_color_status = "🟡 تحتوي على دين (آجل)"

                    st.session_state.invoices_list.append({
                        "رقم الفاتورة": str(inv_code),
                        "الزبون": str(cust_name),
                        "المنتجات": str(" , ".join(prod_names_str)),
                        "المبلغ الكلي": int(total_cart_price),
                        "تكلفتها": int(total_buy_cost_of_invoice),
                        "الواصل": int(paid_amount),
                        "المتبقي (الدين)": int(remaining_amount),
                        "نوع الدفع": str(pay_type),
                        "حالة الفاتورة واللون": str(inv_color_status),
                        "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    
                    log_audit("إتمام عملية بيع", f"تم إصدار الفاتورة {inv_code} للزبون {cust_name} بمبلغ {int(total_cart_price):,} د.ع")
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع بنجاح، وتحديث المخزن، وتسجيل الفاتورة في الذمم!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ أثناء إتمام البيع: {e}")
    else:
        st.info("🛒 السلة فارغة حالياً.")

elif selected_tab_name == t["tabs"][5]:
    st.subheader("📄 سجل الفواتير، الطباعة، وحفظ PDF ومطالبة واتساب")
    
    if st.session_state.invoices_list:
        if st.button("🗑️ مسح سجل الفواتير القديم"):
            st.session_state.invoices_list = []
            log_audit("مسح سجل الفواتير", "تم مسح جميع الفواتير المسجلة")
            st.success("تم مسح السجل.")
            st.rerun()
            
        for idx, inv in enumerate(st.session_state.invoices_list):
            with st.expander(f"📄 فاتورة: {inv['رقم الفاتورة']} | الزبون: {inv['الزبون']} | المجموع: {inv['المبلغ الكلي']:,} د.ع ({inv['حالة الفاتورة واللون']})"):
                st.write(f"📅 **التاريخ والوقت:** {inv['التاريخ']}")
                st.write(f"🛒 **المنتجات والمواد:** {inv['المنتجات']}")
                st.write(f"💰 **المبلغ الكلي:** {inv['المبلغ الكلي']:,} د.ع | **الواصل:** {inv['الواصل']:,} د.ع | **المتبقي (الدين):** {inv['المتبقي (الدين)']:,} د.ع")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    html_code = generate_html_invoice(inv, username)
                    st.download_button(
                        label="🖨️ فتح وعرض الفاتورة للطباعة / حفظ PDF",
                        data=html_code,
                        file_name=f"Invoice_{inv['رقم الفاتورة']}.html",
                        mime="text/html",
                        key=f"html_dl_{idx}"
                    )
                
                with col_btn2:
                    wa_msg = f"مرحباً {inv['الزبون']}, تفاصيل فاتورتك رقم {inv['رقم الفاتورة']}: المجموع الكلي: {inv['المبلغ الكلي']:,} د.ع, الواصل: {inv['الواصل']:,} د.ع, المتبقي (الدين): {inv['المتبقي (الدين)']:,} د.ع. شكراً لتعاملكم معنا!"
                    encoded_wa = urllib.parse.quote(wa_msg)
                    st.markdown(f"📱 [إرسال الفاتورة عبر واتساب](https://wa.me/?text={encoded_wa})", unsafe_allow_html=True)

    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

elif selected_tab_name == t["tabs"][6]:
    st.subheader("💵 صندوق سداد الديون والمصاريف اليومية")
    st.write("إدارة النقدية والمصاريف الواردة والصادرة.")

elif selected_tab_name == t["tabs"][7]:
    st.subheader("📊 الرسوم البيانية والتقارير المالية")
    st.write("تحليلات المبيعات والأرباح والمخزون.")

elif selected_tab_name == t["tabs"][8]:
    st.subheader("📜 سجل النشاطات (Audit Trail)")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد نشاطات مسجلة حتى الآن.")

elif selected_tab_name == t["tabs"][9]:
    st.subheader("📖 دليل الاستخدام والمميزات والدعم")
    st.markdown("""
    * **إضافة المواد:** أضف منتجاتك بسهولة مع تتبع الأسعار والكميات.
    * **إدارة المخزن:** تتبع المخزون وتوليد الباركود.
    * **المبيعات والفواتير:** إصدار فواتير بيع كاش أو آجل وعرضها بتنسيق HTML فائق الوضوح للطباعة أو الحفظ كملف PDF.
    """)
