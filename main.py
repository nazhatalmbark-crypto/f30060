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

# **تنسيق اتجاه النصوص لليمين (RTL)**
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
    </style>
""", unsafe_allow_html=True)

# **إدارة اللغات**
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
        "logout": "تسجيل الخروج",
        "tabs": [
            "➕ إضافة مادة جديدة", 
            "📦 جرد المخزن والباركود", 
            "👥 إدارة العملاء والديون", 
            "🏭 إدارة الموردين",
            "🛒 إتمام البيع والفواتير", 
            "📄 سجل الفواتير وواتساب", 
            "💰 صندوق الوردية والمصاريف", 
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

if "suppliers_list" not in st.session_state or isinstance(st.session_state.suppliers_list, pd.DataFrame):
    st.session_state.suppliers_list = []

if "invoices_list" not in st.session_state or isinstance(st.session_state.invoices_list, pd.DataFrame):
    st.session_state.invoices_list = []

if "cart" not in st.session_state or isinstance(st.session_state.cart, pd.DataFrame):
    st.session_state.cart = []

if "expenses_list" not in st.session_state or isinstance(st.session_state.expenses_list, pd.DataFrame):
    st.session_state.expenses_list = []

if "audit_logs" not in st.session_state or isinstance(st.session_state.audit_logs, pd.DataFrame):
    st.session_state.audit_logs = []

if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

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

# **دالة توليد الفاتورة الاحترافية المضمونة 100% للطباعة أو الحفظ**
def generate_html_invoice(inv):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {inv['رقم الفاتورة']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); background: #fff; }}
            .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ margin-bottom: 20px; font-size: 15px; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; font-size: 14px; }}
            th {{ background-color: #f4f4f4; }}
            .totals {{ font-size: 16px; font-weight: bold; text-align: left; margin-top: 15px; line-height: 1.8; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 13px; color: #77px; border-top: 1px dashed #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <h2>YASSER WEB - فاتورة طلبية توصيل رسمية</h2>
                <p>التاريخ والوقت: {inv['التاريخ']}</p>
            </div>
            <div class="info">
                <p><strong>رقم الفاتورة:</strong> {inv['رقم الفاتورة']}</p>
                <p><strong>اسم الزبون:</strong> {inv['الزبون']}</p>
                <p><strong>طريقة وحالة الدفع:</strong> {inv['نوع الدفع']}</p>
            </div>
            <table>
                <tr>
                    <th>تفاصيل المنتجات والمواد المطلوبة</th>
                </tr>
                <tr>
                    <td>{inv['المنتجات']}</td>
                </tr>
            </table>
            <div class="totals">
                <p>المبلغ الكلي: {inv['المبلغ الكلي']:,} دينار عراقي</p>
                <p>المبلغ الواصل: {inv['الواصل']:,} دينار عراقي</p>
                <p>المتبقي (الدين): {inv['المتبقي (الدين)']:,} دينار عراقي</p>
            </div>
            <div class="footer">
                <p>شكراً لتعاملكم معنا - جاهزة للصقها على شحنة التوصيل وتسليمها لشركة النقل</p>
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
                            st.session_state.is_vip = bool(user_info.get("is_paid", False))
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
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى كتابة اسم المستخدم الجديد.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

st.sidebar.title(t["settings"])
st.sidebar.write(f"👤 المستخدم: **{username}**")
st.sidebar.write(f"{t['role_label']} **{user_role}**")

cart_count_badge = sum(int(item['qty']) for item in st.session_state.cart)
st.sidebar.info(f"{t['cart_badge']} **{cart_count_badge}**")

st.sidebar.divider()
st.sidebar.subheader(t["backup_title"])

# جلب العملاء من قاعدة البيانات لعرضهم بالنسخة الاحتياطية أيضاً
try:
    db_cust_res = supabase.table("customers").select("*").eq("username", username).execute()
    current_customers_data = db_cust_res.data if db_cust_res.data else []
except:
    current_customers_data = []

backup_data = {
    "username": str(username),
    "customers": current_customers_data,
    "suppliers": list(st.session_state.suppliers_list),
    "invoices": list(st.session_state.invoices_list),
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

if not st.session_state.is_vip:
    st.sidebar.warning("🔒 حالة النسخة: **مجانية (محدودة)**")
    vip_code = st.sidebar.text_input("أدخل كود النسخة المدفوعة (VIP):", type="password")
    if st.sidebar.button("تفعيل النسخة المدفوعة"):
        if vip_code.strip() == "YASSER2026":
            st.session_state.is_vip = True
            try:
                supabase.table("users").update({"is_paid": True}).eq("username", username).execute()
            except:
                pass
            st.sidebar.success("تم تفعيل النسخة المدفوعة (VIP) بنجاح! 🎉")
            st.rerun()
        else:
            st.sidebar.error("كود التفعيل غير صحيح!")
else:
    st.sidebar.success("🌟 النسخة المدفوعة (VIP) مفعلة بالكامل")

if st.sidebar.button(t["logout"]):
    log_audit("تسجيل خروج", f"تم تسجيل الخروج للمستخدم {username}")
    st.session_state.logged_in_user = None
    st.session_state.is_vip = False
    st.session_state.cart = []
    st.rerun()

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(t["tabs"])

with tab1:
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
            st.warning("⚠️ **تنبيه النسخة المجانية:** وصلت للحد الأقصى (5 منتجات).")
        else:
            with st.form("add_product_clean_form", clear_on_submit=True):
                p_name = st.text_input("اسم المادة / المنتج / الجهاز:")
                c_col, c_sz = st.columns(2)
                with c_col:
                    p_color = st.text_input("اللون / المواصفات الإضافية:", "عام")
                with c_sz:
                    p_size = st.text_input("القياس / السعة / الحجم:", "عام")
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    p_buy_str = st.text_input("سعر الشراء (د.ع):", "0")
                with c2:
                    p_sell_str = st.text_input("سعر البيع (د.ع):", "0")
                with c3:
                    p_qty_str = st.text_input("الكمية المتوفرة:", "1")
                with c4:
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

with tab2:
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

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search_prod_term = st.text_input("🔍 بحث عن مادة:", "")
    with col_s2:
        search_barcode_term = st.text_input("📷 بحث بالباركود:", "")

    if all_products:
        filtered_products = all_products
        if search_prod_term:
            filtered_products = [p for p in filtered_products if search_prod_term.lower() in p['product_name'].lower()]
        if search_barcode_term:
            filtered_products = [p for p in filtered_products if search_barcode_term.lower() in p.get('barcode','').lower()]

        cols = st.columns(3)
        for idx, item in enumerate(filtered_products):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### 📦 {item['product_name']}")
                    st.markdown(f"🎨 **اللون:** `{item.get('color', 'عام')}` | 📏 **القياس:** `{item.get('size', 'عام')}`")
                    st.markdown(f"🏷️ **الباركود:** `{item.get('barcode', 'بدون')}`")
                    st.markdown(f"💰 **الشراء:** `{int(item['buy_price']):,}` | **البيع:** `{int(item['sell_price']):,}` د.ع")
                    
                    profit_per_unit = int(float(item['sell_price']) - float(item['buy_price']))
                    if profit_per_unit < 0:
                        st.error(f"📉 خسارة القطعة: {profit_per_unit:,} د.ع")
                    else:
                        st.success(f"📈 ربح القطعة: +{profit_per_unit:,} د.ع")
                    
                    st.markdown(f"🔢 **الكمية المتوفرة:** `{int(item['quantity'])}` قطعة")
                    
                    with st.expander("🏷️ باركود المادة"):
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

with tab3:
    st.subheader("👥 إدارة العملاء ومتابعة الديون والذمم (محفوظة بقاعدة البيانات بشكل دائم)")
    iraq_govs = ["بغداد", "البصرة", "نينوى", "أربيل", "النجف", "كربلاء", "ذي قار", "بابل", "الأنبار", "ديالى", "كركوك", "صلاح الدين", "المثنى", "ميسان", "القادسية", "واسط", "دهوك", "السليمانية"]
    
    with st.form("add_customer_db_form", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            c_name = st.text_input("اسم الزبون / العميل:")
        with col_c2:
            c_phone = st.text_input("رقم الهاتف:")
        with col_c3:
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

with tab4:
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

with tab5:
    st.subheader("🛒 سلة المبيعات وإتمام الفاتورة (النظام الذكي للمبالغ)")
    
    if st.session_state.cart:
        total_cart_price = 0
        for idx, c_item in enumerate(st.session_state.cart):
            cols_cart = st.columns([3, 2, 2, 1])
            with cols_cart[0]:
                st.write(f"**{c_item['product_name']}** ({c_item['color']} / {c_item['size']})")
            with cols_cart[1]:
                new_q = st.number_input(f"الكمية", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_q_{c_item['id']}")
                c_item['qty'] = new_q
            with cols_cart[2]:
                item_total = c_item['sell_price'] * c_item['qty']
                total_cart_price += item_total
                st.write(f"المجموع: **{int(item_total):,}** د.ع")
            with cols_cart[3]:
                if st.button("❌", key=f"del_cart_{c_item['id']}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        st.divider()
        st.markdown(f"### 💵 المجموع الكلي المطلوب: **{int(total_cart_price):,} د.ع**")
        
        # جلب العملاء لاختيار اسم العميل من قاعدة البيانات
        try:
            res_c_box = supabase.table("customers").select("customer_name").eq("username", username).execute()
            cust_names_list = [c["customer_name"] for c in res_c_box.data] if res_c_box.data else []
        except:
            cust_names_list = []
            
        if not cust_names_list:
            st.warning("⚠️ تنبيه: يرجى إضافة عميل أولاً من تبويب (إدارة العملاء) لتتمكن من إتمام الفاتورة!")
            selected_customer_name = ""
        else:
            selected_customer_name = st.selectbox("اختر اسم الزبون:", cust_names_list)
        
        # **الحقل الطبيعي الحر للمبلغ الواصل (الذكي)**
        st.write("---")
        st.markdown("#### 💰 طريقة الدفع (أدخل المبلغ الواصل طبيعياً):")
        paid_input_str = st.text_input("أدخل المبلغ الذي دفعه الزبون (د.ع):", value=str(int(total_cart_price)))
        
        try:
            paid_amount = float(paid_input_str.strip())
            if paid_amount < 0: paid_amount = 0
            if paid_amount > total_cart_price: paid_amount = total_cart_price
        except ValueError:
            paid_amount = 0
            
        remaining_amount = total_cart_price - paid_amount

        # التحديد التلقائي لحالة الدفع حسب ما كتبه المستخدم
        if paid_amount >= total_cart_price:
            auto_pay_type = "🟢 نقد بالكامل (كاش)"
        elif paid_amount == 0:
            auto_pay_type = "🔴 دين كامل (آجل)"
        else:
            auto_pay_type = "🔵 دفعة جزئية (أقساط)"

        st.info(f"💡 **تحليل النظام التلقائي للفاتورة:** {auto_pay_type} | الواصل: **{int(paid_amount):,} د.ع** | المتبقي (الدين): **{int(remaining_amount):,} د.ع**")

        if st.button("💾 إتمام البيع، خصم المخزن، وحفظ الفاتورة", type="primary"):
            if not selected_customer_name:
                st.error("❌ خطأ: اختر عميلاً مسجلاً.")
            else:
                try:
                    prod_names_str = []
                    total_buy_cost_of_invoice = 0
                    
                    for c_item in st.session_state.cart:
                        prod_names_str.append(f"{c_item['product_name']} ({c_item['color']}) [العدد: {c_item['qty']}]")
                        total_buy_cost_of_invoice += (c_item['buy_price'] * c_item['qty'])
                        
                        res_p = supabase.table("products").select("quantity").eq("id", c_item["id"]).execute()
                        if res_p.data:
                            current_db_qty = res_p.data[0]["quantity"]
                            new_db_qty = max(0, current_db_qty - c_item['qty'])
                            supabase.table("products").update({"quantity": new_db_qty}).eq("id", c_item["id"]).execute()
                    
                    inv_id = len(st.session_state.invoices_list) + 1
                    inv_code = f"INV-{inv_id:03d}"
                    
                    st.session_state.invoices_list.append({
                        "رقم الفاتورة": str(inv_code),
                        "الزبون": str(selected_customer_name),
                        "المنتجات": str(" , ".join(prod_names_str)),
                        "المبلغ الكلي": int(total_cart_price),
                        "تكلفتها": int(total_buy_cost_of_invoice),
                        "الواصل": int(paid_amount),
                        "المتبقي (الدين)": int(remaining_amount),
                        "نوع الدفع": str(auto_pay_type),
                        "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    
                    log_audit("إتمام بيع", f"فاتورة {inv_code} للزبون {selected_customer_name}")
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع وتحديث المخزن بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
    else:
        st.info("🛒 السلة فارغة.")

with tab6:
    st.subheader("📄 سجل الفواتير، الطباعة المباشرة، ومطالبة الديون عبر واتساب")
    if st.session_state.invoices_list:
        for inv in reversed(st.session_state.invoices_list):
            with st.container(border=True):
                col_inv1, col_inv2, col_inv3 = st.columns([2, 2, 2])
                with col_inv1:
                    st.markdown(f"#### 📄 {inv['رقم الفاتورة']}")
                    st.write(f"👤 **الزبون:** {inv['الزبون']}")
                    st.write(f"📅 **الوقت:** {inv['التاريخ']}")
                with col_inv2:
                    st.write(f"🛒 **المنتجات:** {inv['المنتجات']}")
                    st.write(f"💵 **المبلغ:** `{inv['المبلغ الكلي']:,}` د.ع")
                    st.write(f"💰 **الواصل:** `{inv['الواصل']:,}` | **الدين:** `{inv['المتبقي (الدين)']:,}` د.ع")
                with col_inv3:
                    # زر تحميل الفاتورة كملف HTML جاهز للطباعة أو الحفظ بصيغة PDF فوراً بدون مشاكل
                    html_code = generate_html_invoice(inv)
                    st.download_button(
                        label="🖨️ طباعة / حفظ فاتورة التوصيل",
                        data=html_code,
                        file_name=f"Invoice_{inv['رقم الفاتورة']}.html",
                        mime="text/html",
                        key=f"dl_html_{inv['رقم الفاتورة']}"
                    )
                
                debt_val = inv.get('المتبقي (الدين)', 0)
                if debt_val > 0:
                    try:
                        phone_res = supabase.table("customers").select("phone").eq("customer_name", inv['الزبون']).execute()
                        cust_phone_found = phone_res.data[0]['phone'] if phone_res.data else ""
                    except:
                        cust_phone_found = ""
                        
                    if cust_phone_found:
                        wa_msg = f"مرحباً بالاستاذ {inv['الزبون']},\nنود تذكيركم بوجود مبلغ دين مستحق بقيمة ({debt_val:,} د.ع) بالفاتورة رقم ({inv['رقم الفاتورة']}). شكراً لكم."
                        encoded_wa_msg = urllib.parse.quote(wa_msg)
                        wa_link = f"https://wa.me/{cust_phone_found}?text={encoded_wa_msg}"
                        st.markdown(f"💬 [مراسلة الزبون بالدين عبر واتساب]({wa_link})", unsafe_allow_html=True)
    else:
        st.info("لا توجد فواتير مسجلة.")

with tab7:
    st.subheader("💰 صندوق الوردية اليومي والمصاريف")
    with st.form("expense_form", clear_on_submit=True):
        exp_title = st.text_input("بيان المصروف:")
        exp_amount_str = st.text_input("مبلغ المصروف (د.ع):", "0")
        if st.form_submit_button("تسجيل المصروف"):
            if exp_title.strip():
                try:
                    exp_amt = float(exp_amount_str.strip())
                    st.session_state.expenses_list.append({
                        "البيان": str(exp_title.strip()),
                        "المبلغ": int(exp_amt),
                        "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    st.success("تم تسجيل المصروف!")
                    st.rerun()
                except ValueError:
                    st.error("مبلغ غير صحيح.")
            else:
                st.warning("أدخل بيان المصروف.")

    total_sales_all = sum(inv['المبلغ الكلي'] for inv in st.session_state.invoices_list) if st.session_state.invoices_list else 0
    total_expenses_all = sum(ex['المبلغ'] for ex in st.session_state.expenses_list) if st.session_state.expenses_list else 0
    net_box_balance = total_sales_all - total_expenses_all

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.metric("إجمالي المبيعات", f"{total_sales_all:,} د.ع")
    with col_b2:
        st.metric("إجمالي المصاريف", f"{total_expenses_all:,} د.ع")
    with col_b3:
        st.metric("صافي الصندوق", f"{net_box_balance:,} د.ع")

    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)

with tab8:
    st.subheader("📊 الرسوم البيانية")
    if st.session_state.invoices_list:
        df_inv_charts = pd.DataFrame(st.session_state.invoices_list)
        st.line_chart(df_inv_charts, x="رقم الفاتورة", y="المبلغ الكلي")
    else:
        st.info("لا توجد بيانات كافية.")

with tab9:
    st.subheader("📜 سجل النشاطات")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد نشاطات.")

with tab10:
    st.subheader("📖 الدليل والمميزات")
    st.markdown("""
    * **نظام Yasser Web**
    * تم ربط العملاء بقاعدة البيانات لضمان عدم اختفائهم نهائياً، وتحديث نظام إدخال المبلغ الواصل تلقائياً ليحدد (نقد، أقساط، أو دين).
    """)
