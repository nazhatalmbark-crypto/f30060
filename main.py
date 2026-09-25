import streamlit as st
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

st.set_page_config(page_title="Yasser Web - النظام الشامل لإدارة المحلات", page_icon="🛍️", layout="wide")

# إزالة أي خصائص CSS معقدة كانت تسبب انعكاس الكلمات والحروف
st.markdown("""
    <style>
    .stApp {
        direction: rtl !important;
        text-align: right !important;
    }
    </style>
""", unsafe_allow_html=True)

# إدارة اللغات والواجهات
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
        "role_label": "👤 الصلاحية:",
        "cart_badge": "🛒 المواد الحالية بالسلة:",
        "backup_title": "🔄 النسخ الاحتياطي الفوري للبيانات",
        "backup_download": "📥 تحميل نسخة احتياطية (JSON)",
        "logout": "تسجيل الخروج",
        "tabs": [
            "➕ إضافة مادة", 
            "📦 المخزن والباركود", 
            "👥 العملاء والديون", 
            "💵 تسداد الديون",
            "🏭 الموردين",
            "🛒 البيع والفواتير", 
            "📄 سجل الفواتير", 
            "💰 المصاريف", 
            "📊 التقارير",
            "📜 سجل النشاطات",
            "📖 الدليل والدعم"
        ]
    }
}

t = lang_dict[st.session_state.lang]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "user_role" not in st.session_state:
    st.session_state.user_role = "مشرف النظام"

if "suppliers_list" not in st.session_state or isinstance(st.session_state.suppliers_list, pd.DataFrame):
    st.session_state.suppliers_list = []

if "cart" not in st.session_state or isinstance(st.session_state.cart, pd.DataFrame):
    st.session_state.cart = []

if "expenses_list" not in st.session_state or isinstance(st.session_state.expenses_list, pd.DataFrame):
    st.session_state.expenses_list = []

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

def generate_html_invoice(inv):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {inv['invoice_code']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; direction: rtl; text-align: right; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); background: #fff; }}
            .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ margin-bottom: 20px; font-size: 15px; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; font-size: 14px; }}
            th {{ background-color: #f4f4f4; }}
            .totals {{ font-size: 16px; font-weight: bold; text-align: left; margin-top: 15px; line-height: 1.8; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 13px; color: #777; border-top: 1px dashed #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <h2>YASSER WEB - فاتورة طلبية توصيل رسمية</h2>
                <p>التاريخ والوقت: {inv['created_date']}</p>
            </div>
            <div class="info">
                <p><strong>رقم الفاتورة:</strong> {inv['invoice_code']}</p>
                <p><strong>اسم الزبون:</strong> {inv['customer_name']}</p>
                <p><strong>طريقة وحالة الدفع:</strong> {inv['payment_type']}</p>
            </div>
            <table>
                <tr>
                    <th>تفاصيل المنتجات والمواد المطلوبة</th>
                </tr>
                <tr>
                    <td>{inv['products_text']}</td>
                </tr>
            </table>
            <div class="totals">
                <p>المبلغ الكلي: {inv['total_price']:,} دينار عراقي</p>
                <p>المبلغ الواصل: {inv['paid_amount']:,} دينار عراقي</p>
                <p>المتبقي (الدين): {inv['remaining_amount']:,} دينار عراقي</p>
            </div>
            <div class="footer">
                <p>شكراً لتعاملكم معنا - إنستغرام: @yaser120120120120</p>
            </div>
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
                            expiry_str = user_info.get("vip_expiry_date")
                            
                            if is_paid_db and expiry_str:
                                try:
                                    exp_dt = datetime.datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
                                    if datetime.datetime.now() < exp_dt:
                                        st.session_state.is_vip = True
                                        st.session_state.vip_expiry_date = exp_dt
                                    else:
                                        st.session_state.is_vip = False
                                        supabase.table("users").update({"is_paid": False}).eq("username", login_user.strip()).execute()
                                except:
                                    st.session_state.is_vip = is_paid_db
                            else:
                                st.session_state.is_vip = is_paid_db
                                
                            log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {user_info['username']}")
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
                            st.error("❌ اسم المستخدم هذا مستخدم مسبقاً.")
                        else:
                            supabase.table("users").insert({"username": new_user.strip(), "is_paid": False}).execute()
                            st.session_state.logged_in_user = str(new_user.strip())
                            st.session_state.user_role = str(signup_role)
                            st.session_state.is_vip = False
                            log_audit("إنشاء حساب جديد", f"تم إنشاء حساب باسم {new_user.strip()}")
                            st.success("🎉 تم إنشاء الحساب بنجاح!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")
                else:
                    st.warning("يرجى كتابة اسم المستخدم الجديد.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

st.sidebar.title(t["settings"])
st.sidebar.write(f"👤 المستخدم: **{username}**")
st.sidebar.write(f"{t['role_label']} **{user_role}**")
st.sidebar.markdown("📸 إنستغرام: [@yaser120120120120](https://instagram.com/yaser120120120120)")

cart_count_badge = sum(int(item['qty']) for item in st.session_state.cart)
st.sidebar.info(f"{t['cart_badge']} **{cart_count_badge}**")

st.sidebar.divider()
st.sidebar.subheader(t["backup_title"])

try:
    db_cust_res = supabase.table("customers").select("*").eq("username", username).execute()
    current_customers_data = db_cust_res.data if db_cust_res.data else []
except:
    current_customers_data = []

try:
    db_inv_res = supabase.table("invoices").select("*").eq("username", username).execute()
    current_invoices_data = db_inv_res.data if db_inv_res.data else []
except:
    current_invoices_data = []

backup_data = {
    "username": str(username),
    "customers": current_customers_data,
    "suppliers": list(st.session_state.suppliers_list),
    "invoices": current_invoices_data,
    "expenses": list(st.session_state.expenses_list),
    "audit_logs": list(st.session_state.audit_logs),
    "export_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
}
backup_json = json.dumps(backup_data, ensure_ascii=False, indent=4, default=str)
st.sidebar.download_button(
    label=t["backup_download"],
    data=backup_json,
    file_name=f"yasser_web_backup_{username}.json",
    mime="application/json"
)

st.sidebar.divider()
st.sidebar.subheader("💎 حالة النسخة والتفعيل (30 يوم)")

if st.session_state.is_vip and st.session_state.vip_expiry_date:
    if datetime.datetime.now() > st.session_state.vip_expiry_date:
        st.session_state.is_vip = False
        st.session_state.vip_expiry_date = None
        try:
            supabase.table("users").update({"is_paid": False, "vip_expiry_date": None}).eq("username", username).execute()
        except:
            pass

if not st.session_state.is_vip:
    st.sidebar.warning("🔒 حالة النسخة: **مجانية (محدودة)**")
    vip_code_input = st.sidebar.text_input("أدخل كود التفعيل (30 يوماً):", type="password", key="sidebar_vip_code_input")
    if st.sidebar.button("تفعيل النسخة المدفوعة", key="sidebar_vip_submit_btn"):
        if vip_code_input.strip() == "YASSER2026":
            expiry_dt = datetime.datetime.now() + datetime.timedelta(days=30)
            st.session_state.is_vip = True
            st.session_state.vip_expiry_date = expiry_dt
            try:
                supabase.table("users").update({
                    "is_paid": True,
                    "vip_expiry_date": expiry_dt.strftime('%Y-%m-%d %H:%M:%S')
                }).eq("username", username).execute()
            except:
                pass
            st.sidebar.success("🎉 تم تفعيل النسخة المدفوعة بنجاح لمدة 30 يوماً!")
            st.rerun()
        else:
            st.sidebar.error("❌ كود التفعيل غير صحيح!")
else:
    remaining_days = (st.session_state.vip_expiry_date - datetime.datetime.now()).days if st.session_state.vip_expiry_date else 30
    if remaining_days < 0: remaining_days = 0
    st.sidebar.success(f"🌟 النسخة المدفوعة (VIP) مفعلة\n\n⏱️ الوقت المتبقي: **{remaining_days} يوم**")

st.sidebar.divider()

st.sidebar.subheader("📌 أقسام النظام (اختر للفتح)")
selected_tab = st.sidebar.radio("التنقل بين الأقسام:", t["tabs"], label_visibility="collapsed")

st.sidebar.divider()
if st.sidebar.button(t["logout"]):
    log_audit("تسجيل خروج", f"تم تسجيل الخروج للمستخدم {username}")
    st.session_state.logged_in_user = None
    st.session_state.is_vip = False
    st.session_state.vip_expiry_date = None
    st.session_state.cart = []
    st.rerun()

st.divider()

# عرض الأقسام
if selected_tab == "➕ إضافة مادة":
    st.subheader("➕ واجهة إضافة مادة أو بضاعة جديدة للمخزن")
    if user_role == "كاشير":
        st.warning("⚠️ عذراً، حساب الكاشير لا يمتلك صلاحية إضافة أو تعديل المواد في المخزن.")
    else:
        try:
            res_prod_count = supabase.table("products").select("id").eq("username", username).execute()
            current_count = len(res_prod_count.data) if res_prod_count.data else 0
        except:
            current_count = 0
            
        if not st.session_state.is_vip and current_count >= 5:
            st.warning("⚠️ **تنبيه النسخة المجانية:** وصلت للحد الأقصى (5 منتجات). فعّل النسخة المدفوعة لتجاوز الحد.")
        else:
            with st.form("add_product_clean_form", clear_on_submit=True):
                p_name = st.text_input("اسم المادة / المنتج / الجهاز:")
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    p_color = st.text_input("اللون / المواصفات الإضافية:", "عام")
                with col_f2:
                    p_size = st.text_input("القياس / السعة / الحجم:", "عام")
                
                col_f3, col_f4 = st.columns(2)
                with col_f3:
                    p_buy_str = st.text_input("سعر الشراء (د.ع):", "0")
                with col_f4:
                    p_sell_str = st.text_input("سعر البيع (د.ع):", "0")
                
                col_f5, col_f6 = st.columns(2)
                with col_f5:
                    p_qty_str = st.text_input("الكمية المتوفرة:", "1")
                with col_f6:
                    p_barcode = st.text_input("رمز الباركود:", "")
                
                submitted = st.form_submit_button("حفظ المادة في المخزن", type="primary")
                if submitted:
                    if p_name.strip():
                        try:
                            p_buy = float(p_buy_str.strip())
                            p_sell = float(p_sell_str.strip())
                            p_qty = int(p_qty_str.strip())
                            
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
                            log_audit("إضافة منتج", f"تمت إضافة المنتج ({p_name.strip()})")
                            st.success(f"تمت إضافة المادة ({p_name}) بنجاح!")
                            st.rerun()
                        except ValueError:
                            st.error("❌ خطأ: يرجى إدخال أرقام صحيحة.")
                        except Exception as e:
                            st.error(f"❌ خطأ: {e}")
                    else:
                        st.warning("يرجى كتابة اسم المادة.")

elif selected_tab == "📦 المخزن والباركود":
    st.subheader("📦 جرد المخزن الشامل مع الباركود وحساب أرباح القطع")
    try:
        res_all_p = supabase.table("products").select("*").eq("username", username).execute()
        all_products = res_all_p.data if res_all_p.data else []
    except:
        all_products = []

    low_stock_items = [p for p in all_products if p['quantity'] <= 2]
    if low_stock_items:
        low_names = " ، ".join([f"**{i['product_name']}**" for i in low_stock_items])
        st.error(f"🚨 **تنبيه قرب نفاد المخزون:** المواد التالية وشيكة النفاذ أو نفدت: {low_names}")

    search_prod_term = st.text_input("🔍 بحث عن مادة:", "")
    search_barcode_term = st.text_input("📷 بحث بالباركود:", "")

    if all_products:
        filtered_products = all_products
        if search_prod_term:
            filtered_products = [p for p in filtered_products if search_prod_term.lower() in p['product_name'].lower()]
        if search_barcode_term:
            filtered_products = [p for p in filtered_products if search_barcode_term.lower() in p.get('barcode','').lower()]

        cols = st.columns(2)
        for idx, item in enumerate(filtered_products):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"### 📦 {item['product_name']}")
                    st.markdown(f"🎨 **اللون:** `{item.get('color', 'عام')}`")
                    st.markdown(f"📏 **القياس:** `{item.get('size', 'عام')}`")
                    st.markdown(f"🏷️ **الباركود:** `{item.get('barcode', 'بدون')}`")
                    st.markdown(f"💰 **الشراء:** `{int(item['buy_price']):,}` د.ع")
                    st.markdown(f"💵 **البيع:** `{int(item['sell_price']):,}` د.ع")
                    
                    profit_per_unit = int(float(item['sell_price']) - float(item['buy_price']))
                    if profit_per_unit < 0:
                        st.error(f"📉 خسارة القطعة: {profit_per_unit:,} د.ع")
                    else:
                        st.success(f"📈 ربح القطعة: +{profit_per_unit:,} د.ع")
                    
                    st.markdown(f"🔢 **الكمية:** `{int(item['quantity'])}` قطعة")
                    
                    with st.expander("🏷️ الباركود"):
                        b_code_val = item.get('barcode', '')
                        if not b_code_val or b_code_val == "بدون":
                            b_code_val = f"PRD{item['id']}"
                        try:
                            rv = barcode.get('code128', str(b_code_val), writer=ImageWriter())
                            buffer_bc = io.BytesIO()
                            rv.write(buffer_bc)
                            st.image(buffer_bc.getvalue(), caption=f"باركود: {b_code_val}", width=150)
                        except Exception as ex:
                            st.error(f"تعذر توليد الباركود: {ex}")

                    if item['quantity'] > 0:
                        if st.button(f"🛒 إضافة للسلة", key=f"add_cart_{item['id']}"):
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
                            st.toast(f"✅ تمت الإضافة للسلة!", icon="🛍️")
                            st.rerun()
                    else:
                        st.warning("⚠️ نفذت الكمية")
    else:
        st.info("المخزن فارغ حالياً.")

elif selected_tab == "👥 العملاء والديون":
    st.subheader("👥 إدارة العملاء ومتابعة الديون والذمم")
    iraq_govs = ["بغداد", "البصرة", "نينوى", "أربيل", "النجف", "كربلاء", "ذي قار", "بابل", "الأنبار", "ديالى", "كركوك", "صلاح الدين", "المثنى", "ميسان", "القادسية", "واسط", "دهوك", "السليمانية"]
    
    with st.form("add_customer_db_form", clear_on_submit=True):
        c_name = st.text_input("اسم الزبون / العميل:")
        c_phone = st.text_input("رقم الهاتف:")
        c_gov = st.selectbox("المحافظة:", iraq_govs)
        c_address = st.text_input("العنوان / المنطقة:")
        c_notes = st.text_area("ملاحظات:")
            
        if st.form_submit_button("تسجيل العميل وحفظه"):
            if c_name and c_phone:
                try:
                    supabase.table("customers").insert({
                        "username": str(username),
                        "customer_name": str(c_name.strip()),
                        "phone": str(c_phone.strip()),
                        "governorate": str(c_gov),
                        "address": str(c_address.strip() if c_address else "غير محدد"),
                        "notes": str(c_notes.strip() if c_notes else "لا يوجد"),
                        "created_at": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                    }).execute()
                    log_audit("إضافة عميل", f"تم تسجيل العميل {c_name}")
                    st.success(f"تم تسجيل العميل ({c_name}) بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ في حفظ العميل: {e}")
            else:
                st.warning("يرجى كتابة الاسم ورقم الهاتف.")

    st.divider()
    st.subheader("📋 قائمة العملاء المسجلين")
    try:
        res_cust_table = supabase.table("customers").select("*").eq("username", username).execute()
        db_customers = res_cust_table.data if res_cust_table.data else []
    except:
        db_customers = []

    if db_customers:
        df_cust = pd.DataFrame(db_customers)
        st.dataframe(df_cust, use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلين حالياً.")

elif selected_tab == "💵 تسداد الديون":
    st.subheader("💵 نظام سداد الديون والذمم للعملاء")
    try:
        res_cust_debt = supabase.table("customers").select("customer_name").eq("username", username).execute()
        debt_cust_list = [c["customer_name"] for c in res_cust_debt.data] if res_cust_debt.data else []
    except:
        debt_cust_list = []

    if not debt_cust_list:
        st.info("لا توجد عملاء مسجلين لعرض الديون.")
    else:
        selected_debt_customer = st.selectbox("اختر اسم العميل لتسديد الديون:", debt_cust_list, key="debt_pay_cust_select")
        
        try:
            res_cust_invoices = supabase.table("invoices").select("*").eq("username", username).eq("customer_name", selected_debt_customer).execute()
            customer_invoices = res_cust_invoices.data if res_cust_invoices.data else []
        except:
            customer_invoices = []

        total_customer_debt = sum(inv.get('remaining_amount', 0) for inv in customer_invoices)
        
        st.markdown(f"### 📌 إجمالي الدين الكلي على العميل (`{selected_debt_customer}`): **{int(total_customer_debt):,} د.ع**")
        
        if customer_invoices:
            with st.expander("📄 عرض تفاصيل الفواتير المسجلة على هذا العميل"):
                for cinv in customer_invoices:
                    st.write(f"- **رقم الفاتورة:** {cinv['invoice_code']} | **المبلغ الكلي:** {cinv['total_price']:,} د.ع | **الواصل:** {cinv['paid_amount']:,} د.ع | **المتبقي:** `{cinv['remaining_amount']:,}` د.ع | **التاريخ:** {cinv['created_date']}")
        
        st.divider()
        with st.form("pay_debt_form"):
            payment_input_str = st.text_input("أدخل المبلغ المراد تسديده (د.ع):", "0")
            pay_submitted = st.form_submit_button("إتمام التسديد وتصفير الديون", type="primary")
            
            if pay_submitted:
                try:
                    payment_val = float(payment_input_str.strip())
                    if payment_val <= 0:
                        st.warning("يرجى إدخال مبلغ صالح أكبر من الصفر.")
                    elif payment_val > total_customer_debt:
                        st.error("❌ المبلغ المدخل أكبر من إجمالي الدين المطلوب على العميل!")
                    else:
                        remaining_payment = payment_val
                        for cinv in customer_invoices:
                            if remaining_payment <= 0:
                                break
                            curr_rem = cinv.get('remaining_amount', 0)
                            if curr_rem > 0:
                                if remaining_payment >= curr_rem:
                                    new_paid = cinv['total_price']
                                    new_rem = 0
                                    new_type = "🟢 نقد بالكامل (كاش)"
                                    remaining_payment -= curr_rem
                                else:
                                    new_paid = cinv['paid_amount'] + remaining_payment
                                    new_rem = curr_rem - remaining_payment
                                    new_type = "🔵 دفعة جزئية (أقساط)"
                                    remaining_payment = 0
                                
                                supabase.table("invoices").update({
                                    "paid_amount": int(new_paid),
                                    "remaining_amount": int(new_rem),
                                    "payment_type": str(new_type)
                                }).eq("id", cinv["id"]).execute()
                        
                        log_audit("سداد ديون", f"تم تسديد مبلغ {payment_val:,} د.ع للعميل {selected_debt_customer}")
                        st.success(f"🎉 تم تسديد مبلغ {payment_val:,.0f} دينار بنجاح وتحديث حساب العميل والفواتير!")
                        st.rerun()
                except ValueError:
                    st.error("❌ يرجى إدخال رقم صحيح للمبلغ.")
                except Exception as e:
                    st.error(f"❌ خطأ في عملية التسديد: {e}")

elif selected_tab == "🏭 الموردين":
    st.subheader("🏭 إدارة الموردين")
    with st.form("add_supplier_form", clear_on_submit=True):
        sup_name = st.text_input("اسم المورد:")
        sup_phone = st.text_input("رقم هاتف المورد:")
        sup_notes = st.text_input("التخصص / نوع البضاعة:")
        if st.form_submit_button("إضافة المورد"):
            if sup_name.strip():
                st.session_state.suppliers_list.append({
                    "اسم المورد": str(sup_name.strip()),
                    "رقم الهاتف": str(sup_phone.strip() if sup_phone else "غير محدد"),
                    "التخصص": str(sup_notes.strip() if sup_notes else "عام"),
                    "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                })
                st.success("تم إضافة المورد بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى إدخال اسم المورد.")
    if st.session_state.suppliers_list:
        st.dataframe(pd.DataFrame(st.session_state.suppliers_list), use_container_width=True)
    else:
        st.info("لا يوجد موردين.")

elif selected_tab == "🛒 البيع والفواتير":
    st.subheader("🛒 سلة المبيعات وإتمام الفاتورة الذكية")
    
    if st.session_state.cart:
        total_cart_price = 0
        for idx, c_item in enumerate(st.session_state.cart):
            with st.container(border=True):
                st.write(f"**{c_item['product_name']}** ({c_item['color']} / {c_item['size']})")
                new_q = st.number_input(f"الكمية لـ {c_item['product_name']}", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_q_{c_item['id']}")
                c_item['qty'] = new_q
                item_total = c_item['sell_price'] * c_item['qty']
                total_cart_price += item_total
                st.write(f"المجموع: **{int(item_total):,}** د.ع")
                if st.button("❌ حذف المادة", key=f"del_cart_{c_item['id']}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        st.divider()
        st.markdown(f"### 💵 المجموع الكلي المطلوب: **{int(total_cart_price):,} د.ع**")
        
        try:
            res_c_box = supabase.table("customers").select("customer_name").eq("username", username).execute()
            cust_names_list = [c["customer_name"] for c in res_c_box.data] if res_c_box.data else []
        except:
            cust_names_list = []
            
        if not cust_names_list:
            st.warning("⚠️ تنبيه: يرجى إضافة عميل أولاً من تبويب (العملاء والديون) لتتمكن من إتمام الفاتورة!")
            selected_customer_name = ""
        else:
            selected_customer_name = st.selectbox("اختر اسم الزبون:", cust_names_list)
        
        st.write("---")
        st.markdown("#### 💰 طريقة الدفع:")
        paid_input_str = st.text_input("أدخل المبلغ الذي دفعه الزبون (د.ع):", value=str(int(total_cart_price)))
        
        try:
            paid_amount = float(paid_input_str.strip())
            if paid_amount < 0: paid_amount = 0
            if paid_amount > total_cart_price: paid_amount = total_cart_price
        except ValueError:
            paid_amount = 0
            
        remaining_amount = total_cart_price - paid_amount

        if paid_amount >= total_cart_price:
            auto_pay_type = "🟢 نقد بالكامل (كاش)"
        elif paid_amount == 0:
            auto_pay_type = "🔴 دين كامل (آجل)"
        else:
            auto_pay_type = "🔵 دفعة جزئية (أقساط)"

        st.info(f"💡 **تحليل النظام التلقائي:** {auto_pay_type} | الواصل: **{int(paid_amount):,} د.ع** | المتبقي (الدين): **{int(remaining_amount):,} د.ع**")

        if not cust_names_list:
            st.error("❌ لا يمكنك إتمام الفاتورة لعدم وجود عملاء مسجلين.")
        else:
            if st.button("💾 إتمام وحفظ الفاتورة رسمياً", type="primary"):
                try:
                    invoice_code = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    created_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    products_text_summary = " - ".join([f"{item['product_name']} ({item['color']} / {item['size']}) × {item['qty']}" for item in st.session_state.cart])
                    
                    supabase.table("invoices").insert({
                        "username": str(username),
                        "invoice_code": str(invoice_code),
                        "customer_name": str(selected_customer_name),
                        "total_price": float(total_cart_price),
                        "paid_amount": float(paid_amount),
                        "remaining_amount": float(remaining_amount),
                        "payment_type": str(auto_pay_type),
                        "products_text": str(products_text_summary),
                        "created_date": str(created_date)
                    }).execute()
                    
                    for c_item in st.session_state.cart:
                        res_p_db = supabase.table("products").select("quantity").eq("id", c_item["id"]).execute()
                        if res_p_db.data:
                            current_qty_in_db = res_p_db.data[0]["quantity"]
                            new_qty_db = max(0, current_qty_in_db - c_item["qty"])
                            supabase.table("products").update({"quantity": int(new_qty_db)}).eq("id", c_item["id"]).execute()
                    
                    log_audit("إتمام بيع", f"تم إصدار الفاتورة رقم {invoice_code} بمبلغ {total_cart_price:,} د.ع")
                    st.success(f"🎉 تم إتمام الفاتورة وحفظها بنجاح برقم: {invoice_code}")
                    
                    st.session_state.cart = []
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ خطأ أثناء حفظ الفاتورة: {e}")
    else:
        st.info("🛒 سلة المبيعات فارغة حالياً. قم بإضافة مواد من قسم المخزن للبدء بالبيع.")

elif selected_tab == "📄 سجل الفواتير":
    st.subheader("📄 سجل الفواتير الصادرة والبحث فيها")
    try:
        res_inv_all = supabase.table("invoices").select("*").eq("username", username).order("created_date", desc=True).execute()
        invoices_list = res_inv_all.data if res_inv_all.data else []
    except:
        invoices_list = []

    if invoices_list:
        search_inv_term = st.text_input("🔍 بحث برقم الفاتورة أو اسم الزبون:", "")
        filtered_invoices = invoices_list
        if search_inv_term:
            filtered_invoices = [
                inv for inv in filtered_invoices 
                if search_inv_term.lower() in inv.get('invoice_code', '').lower() or 
                   search_inv_term.lower() in inv.get('customer_name', '').lower()
            ]

        for inv in filtered_invoices:
            with st.container(border=True):
                st.markdown(f"### 📄 الفاتورة: `{inv['invoice_code']}`")
                st.write(f"👤 **الزبون:** {inv['customer_name']} | 📅 **التاريخ:** {inv['created_date']}")
                st.write(f"📦 **المواد:** {inv['products_text']}")
                st.markdown(f"💰 **المجموع:** `{int(inv['total_price']):,}` د.ع | **الواصل:** `{int(inv['paid_amount']):,}` د.ع | **المتبقي:** `{int(inv['remaining_amount']):,}` د.ع")
                st.write(f"🏷️ **حالة الدفع:** {inv['payment_type']}")
                
                html_code = generate_html_invoice(inv)
                st.download_button(
                    label=f"📥 تحميل الفاتورة HTML (رقم {inv['invoice_code']})",
                    data=html_code,
                    file_name=f"invoice_{inv['invoice_code']}.html",
                    mime="text/html",
                    key=f"dl_inv_{inv['id']}"
                )
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

elif selected_tab == "💰 المصاريف":
    st.subheader("💰 إدارة المصاريف اليومية للمحل")
    with st.form("add_expense_form", clear_on_submit=True):
        exp_title = st.text_input("عنوان المصروف (مثلاً: إيجار، كهرباء، صيانة):")
        exp_amount_str = st.text_input("المبلغ (د.ع):", "0")
        exp_notes = st.text_input("ملاحظات إضافية:")
        if st.form_submit_button("تسجيل المصروف"):
            if exp_title.strip():
                try:
                    exp_amount = float(exp_amount_str.strip())
                    st.session_state.expenses_list.append({
                        "العنوان": str(exp_title.strip()),
                        "المبلغ": float(exp_amount),
                        "الملاحظات": str(exp_notes.strip() if exp_notes else "لا يوجد"),
                        "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    log_audit("تسجيل مصروف", f"تم تسجيل مصروف {exp_title} بقيمة {exp_amount:,} د.ع")
                    st.success("تم تسجيل المصروف بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("❌ يرجى إدخال مبلغ صحيح.")
            else:
                st.warning("يرجى إدخال عنوان المصروف.")

    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)
        total_exp = sum(e["المبلغ"] for e in st.session_state.expenses_list)
        st.markdown(f"### 📉 إجمالي المصاريف المسجلة: **{int(total_exp):,} د.ع**")
    else:
        st.info("لا توجد مصاريف مسجلة.")

elif selected_tab == "📊 التقارير":
    st.subheader("📊 التقارير المالية والإحصائيات الشاملة")
    try:
        res_rep_inv = supabase.table("invoices").select("*").eq("username", username).execute()
        rep_invoices = res_rep_inv.data if res_rep_inv.data else []
        
        res_rep_prod = supabase.table("products").select("*").eq("username", username).execute()
        rep_products = res_rep_prod.data if res_rep_prod.data else []
    except:
        rep_invoices = []
        rep_products = []

    total_sales_revenue = sum(i.get('total_price', 0) for i in rep_invoices)
    total_remaining_debt = sum(i.get('remaining_amount', 0) for i in rep_invoices)
    total_inventory_items = sum(p.get('quantity', 0) for p in rep_products)
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric("إجمالي المبيعات الكلية", f"{int(total_sales_revenue):,} د.ع")
    with col_r2:
        st.metric("إجمالي الديون المعلقة", f"{int(total_remaining_debt):,} د.ع")
    with col_r3:
        st.metric("إجمالي القطع بالمخزن", f"{int(total_inventory_items)} قطعة")

elif selected_tab == "📜 سجل النشاطات":
    st.subheader("📜 سجل نشاطات النظام والعمليات (Audit Log)")
    if isinstance(st.session_state.audit_logs, list) and st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد نشاطات مسجلة حتى الآن.")

elif selected_tab == "📖 الدليل والدعم":
    st.subheader("📖 دليل الاستخدام والدعم الفني لنظام Yasser Web")
    st.markdown("""
    أهلاً بك يا أسر في نظامك الشامل لإدارة المحلات والمبيعات **Yasser Web** 🛍️.
    
    * **إضافة المواد:** يمكنك إضافة منتجات جديدة مع الباركود وتحديد أسعار الشراء والبيع.
    * **المخزن والباركود:** يتيح لك جرد البضاعة، معرفة الأرباح، وتوليد باركود لكل منتج وطباعته.
    * **العملاء والديون:** لتسجيل بيانات الزبائن ومتابعة الذمم المالية وديون الأقساط.
    * **سداد الديون:** واجهة مخصصة لتسديد وتصفير ديون العملاء وتحديث الفواتير تلقائياً.
    * **البيع والفواتير:** سلة مبيعات ذكية تخصم الكميات من المخزن فوراً وتدعم طباعة وتحميل الفواتير بتنسيق HTML.
    
    📞 **الدعم الفني والتواصل:** إنستغرام: [@yaser120120120120](https://instagram.com/yaser120120120120)
    """)
