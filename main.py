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
            "➕ إضافة مادة وتوريد كميات", 
            "📦 جرد المخزن والشبكة", 
            "👥 إدارة العملاء والديون", 
            "💵 سداد الديون",
            "🏭 إدارة الموردين",
            "🛒 شبكة المبيعات والسلة", 
            "📄 سجل الفواتير وواتساب", 
            "💰 صندوق الوردية والمصاريف", 
            "📊 الرسوم البيانية والتقارير",
            "📜 سجل النشاطات (Audit Trail)",
            "📖 دليل الاستخدام والمميزات"
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

# **دالة توليد الفاتورة الاحترافية بصيغة HTML**
def generate_html_invoice(inv):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {inv['invoice_code']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; }}
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
                <h2>YASSER WEB - فاتورة طلبية رسمية</h2>
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
                <p>شكراً لتعاملكم معنا - نظام Yasser Web POS</p>
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
                        st.error(f"❌ خطأ: {e}")
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(t["tabs"])

with tab1:
    st.subheader("➕ إضافة مادة جديدة أو توريد كميات إضافية فوق المخزون الحالي")
    if user_role == "كاشير":
        st.warning("⚠️ عذراً، حساب الكاشير لا يمتلك صلاحية إضافة أو تعديل المواد في المخزن.")
    else:
        # جلب المنتجات الموجودة مسبقاً لنظام التوريد السريع وزيادة الكميات
        try:
            res_existing_prod = supabase.table("products").select("id, product_name, quantity, sell_price").eq("username", username).execute()
            existing_products = res_existing_prod.data if res_existing_prod.data else []
        except:
            existing_products = []

        add_mode = st.radio("اختر طريقة الإضافة:", ["إضافة مادة جديدة تماماً", "توريد وزيادة كمية لمادة موجودة مسبقاً"], horizontal=True)

        if add_mode == "توريد وزيادة كمية لمادة موجودة مسبقاً" and existing_products:
            with st.form("restock_form"):
                prod_options = {f"{p['product_name']} (المتوفر حالياً: {p['quantity']})": p['id'] for p in existing_products}
                selected_prod_label = st.selectbox("اختر المادة لتوريد كمية إضافية فوقها:", list(prod_options.keys()))
                restock_qty_str = st.text_input("الكمية المراد إضافتها (توريد جديد):", "1")
                restock_submitted = st.form_submit_button("إضافة الكمية فوق المخزون الحالي", type="primary")

                if restock_submitted:
                    try:
                        add_qty = int(restock_qty_str.strip())
                        p_id = prod_options[selected_prod_label]
                        curr_item = next(p for p in existing_products if p['id'] == p_id)
                        new_total_qty = curr_item['quantity'] + add_qty

                        supabase.table("products").update({"quantity": new_total_qty}).eq("id", p_id).execute()
                        log_audit("توريد كمية", f"تم توريد {add_qty} قطعة للمنتج {curr_item['product_name']}")
                        st.success(f"🎉 تم إضافة الكمية بنجاح! الإجمالي الجديد للمنتج: {new_total_qty} قطعة.")
                        st.rerun()
                    except ValueError:
                        st.error("❌ يرجى إدخال رقم صحيح للكمية.")
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")
        else:
            if add_mode == "توريد وزيادة كمية لمادة موجودة مسبقاً" and not existing_products:
                st.info("لا توجد مواد مسجلة حالياً، يرجى إضافة مادة جديدة أولاً.")

            try:
                res_prod_count = supabase.table("products").select("id").eq("username", username).execute()
                current_count = len(res_prod_count.data) if res_prod_count.data else 0
            except:
                current_count = 0
                
            if not st.session_state.is_vip and current_count >= 5:
                st.warning("⚠️ **تنبيه النسخة المجانية:** وصلت للحد الأقصى (5 منتجات).")
            else:
                with st.form("add_product_clean_form", clear_on_submit=True):
                    p_name = st.text_input("اسم المادة / المنتج:")
                    c_col, c_sz = st.columns(2)
                    with c_col:
                        p_color = st.text_input("اللون / المواصفات:", "عام")
                    with c_sz:
                        p_size = st.text_input("القياس / الحجم:", "عام")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        p_buy_str = st.text_input("سعر الشراء (د.ع):", "0")
                    with c2:
                        p_sell_str = st.text_input("سعر البيع المفرد (سعر القطعة د.ع):", "0")
                    with c3:
                        p_qty_str = st.text_input("الكمية المبدئية (عدد القطع):", "1")
                    with c4:
                        p_barcode = st.text_input("رمز الباركود:", "")
                    
                    submitted = st.form_submit_button("حفظ المادة الجديدة في المخزن", type="primary")
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
                                log_audit("إضافة منتج", f"تمت إضافة المنتج ({p_name.strip()}) بسعر مفرد {p_sell}")
                                st.success(f"تمت إضافة المادة ({p_name}) بنجاح!")
                                st.rerun()
                            except ValueError:
                                st.error("❌ خطأ: يرجى إدخال أرقام صحيحة.")
                            except Exception as e:
                                st.error(f"❌ خطأ: {e}")
                        else:
                            st.warning("يرجى كتابة اسم المادة.")

with tab2:
    st.subheader("📦 جرد المخزن وعرض المواد على شكل شبكة مع الباركود")
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
                    st.markdown(f"💰 **سعر القطعة المفرد:** `{int(item['sell_price']):,}` د.ع")
                    
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
                        if st.button(f"🛒 إضافة للسلة", key=f"inv_add_cart_{item['id']}"):
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
    st.subheader("👥 إدارة العملاء ومتابعة الديون والذمم")
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

with tab5:
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

with tab6:
    st.subheader("🛒 شبكة المبيعات، السلة الذكية وإتمام الفاتورة")
    
    # عرض المواد على شكل شبكة مع زر إضافة للسلة
    try:
        res_grid_p = supabase.table("products").select("*").eq("username", username).execute()
        grid_products = res_grid_p.data if res_grid_p.data else []
    except:
        grid_products = []

    st.markdown("### 🛍️ اختر المواد من الشبكة (اضغط إضافة لتجميعها في السلة):")
    if grid_products:
        g_cols = st.columns(3)
        for g_idx, g_item in enumerate(grid_products):
            with g_cols[g_idx % 3]:
                with st.container(border=True):
                    st.markdown(f"#### 📦 {g_item['product_name']}")
                    st.markdown(f"💰 **سعر القطعة المفرد:** `{int(g_item['sell_price']):,}` د.ع")
                    st.markdown(f"🔢 **المتوفر:** `{g_item['quantity']}` قطعة")
                    if g_item['quantity'] > 0:
                        if st.button("➕ إضافة للسلة", key=f"grid_add_{g_item['id']}"):
                            found = False
                            for ci in st.session_state.cart:
                                if ci["id"] == g_item["id"]:
                                    if ci["qty"] < g_item["quantity"]:
                                        ci["qty"] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({
                                    "id": g_item["id"],
                                    "product_name": g_item["product_name"],
                                    "color": g_item.get('color', ''),
                                    "size": g_item.get('size', ''),
                                    "sell_price": g_item["sell_price"],
                                    "buy_price": g_item["buy_price"],
                                    "max_qty": g_item["quantity"],
                                    "qty": 1
                                })
                            st.toast("✅ تمت الإضافة للسلة بنجاح!", icon="🛒")
                            st.rerun()
                    else:
                        st.error("نفدت الكمية")
    else:
        st.info("لا توجد مواد في المخزن حالياً. أضف مواد من تبويب (إضافة مادة وتوريد كميات).")

    st.divider()
    st.markdown("### 🛒 محتويات السلة وإتمام الفاتورة:")
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
        
        # جلب العملاء للتعبئة التلقائية للبيانات
        try:
            res_c_box = supabase.table("customers").select("*").eq("username", username).execute()
            cust_records = res_c_box.data if res_c_box.data else []
        except:
            cust_records = []
            
        if not cust_records:
            st.warning("⚠️ تنبيه: يرجى إضافة عميل أولاً من تبويب (إدارة العملاء) لتتمكن من إتمام الفاتورة!")
            selected_customer_name = ""
        else:
            cust_names_list = [c["customer_name"] for c in cust_records]
            selected_customer_name = st.selectbox("اختر اسم الزبون (سيتم تعبئة تفاصيله تلقائياً):", cust_names_list)
            
            # العثور على بيانات العميل المختار للتعبئة التلقائية
            selected_cust_obj = next((c for c in cust_records if c["customer_name"] == selected_customer_name), None)
            if selected_cust_obj:
                c_col_info1, c_col_info2 = st.columns(2)
                with c_col_info1:
                    st.text_input("رقم هاتف العميل (تلقائي):", value=selected_cust_obj.get("phone", ""), disabled=True, key="autofill_phone")
                with c_col_info2:
                    st.text_input("عنوان العميل (تلقائي):", value=selected_cust_obj.get("address", ""), disabled=True, key="autofill_addr")
        
        st.write("---")
        st.markdown("#### 💰 طريقة الدفع وإدخال المبلغ الواصل:")
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

        st.info(f"💡 **تحليل النظام التلقائي للفاتورة:** {auto_pay_type} | الواصل: **{int(paid_amount):,} د.ع** | المتبقي (الدين): **{int(remaining_amount):,} د.ع**")

        if st.button("💾 إتمام البيع، خصم المخزن، وحفظ الفاتورة وطباعتها", type="primary"):
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
                    
                    try:
                        res_inv_count = supabase.table("invoices").select("id").eq("username", username).execute()
                        inv_id = len(res_inv_count.data) + 1 if res_inv_count.data else 1
                    except:
                        inv_id = 1
                        
                    inv_code = f"INV-{inv_id:03d}"
                    
                    invoice_record = {
                        "username": str(username),
                        "invoice_code": str(inv_code),
                        "customer_name": str(selected_customer_name),
                        "products_text": str(" ، ".join(prod_names_str)),
                        "total_price": int(total_cart_price),
                        "cost_price": int(total_buy_cost_of_invoice),
                        "paid_amount": int(paid_amount),
                        "remaining_amount": int(remaining_amount),
                        "payment_type": str(auto_pay_type),
                        "created_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    }

                    supabase.table("invoices").insert(invoice_record).execute()
                    
                    log_audit("إتمام بيع", f"فاتورة {inv_code} للزبون {selected_customer_name}")
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع وتحديث المخزن وحفظ الفاتورة بنجاح!")
                    
                    # عرض الفاتورة الاحترافية الجاهزة للطباعة
                    st.markdown("---")
                    st.subheader("📄 معاينة الفاتورة الرسمية:")
                    st.components.v1.html(generate_html_invoice(invoice_record), height=500, scrolling=True)
                    
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
    else:
        st.info("🛒 السلة فارغة. قم بإضافة مواد من الشبكة بالأعلى.")

with tab7:
    st.subheader("📄 سجل الفواتير، الطباعة المباشرة، وإرسال الفاتورة عبر الواتساب")
    try:
        res_all_inv = supabase.table("invoices").select("*").eq("username", username).execute()
        all_invoices = res_all_inv.data if res_all_inv.data else []
    except:
        all_invoices = []

    if all_invoices:
        for inv in reversed(all_invoices):
            with st.container(border=True):
                st.markdown(f"### 🧾 فاتورة رقم: `{inv['invoice_code']}` | الزبون: **{inv['customer_name']}**")
                st.markdown(f"📅 **التاريخ:** {inv['created_date']} | الحالة: **{inv['payment_type']}**")
                st.markdown(f"📦 **المواد:** {inv['products_text']}")
                st.markdown(f"💰 **المجموع الكلي:** `{inv['total_price']:,}` د.ع | **الواصل:** `{inv['paid_amount']:,}` د.ع | **المتبقي:** `{inv['remaining_amount']:,}` د.ع")
                
                col_inv1, col_inv2 = st.columns(2)
                with col_inv1:
                    with st.expander("🖨️ عرض الفاتورة للطباعة"):
                        st.components.v1.html(generate_html_invoice(inv), height=400, scrolling=True)
                with col_inv2:
                    try:
                        res_cust_phone = supabase.table("customers").select("phone").eq("username", username).eq("customer_name", inv['customer_name']).execute()
                        c_ph = res_cust_phone.data[0]["phone"] if res_cust_phone.data else ""
                    except:
                        c_ph = ""
                    
                    wa_text = f"مرحباً {inv['customer_name']},\nإليك تفاصيل فاتورتك ({inv['invoice_code']}) من Yasser Web POS:\nالمجموع: {inv['total_price']:,} د.ع\nالواصل: {inv['paid_amount']:,} د.ع\nالمتبقي: {inv['remaining_amount']:,} د.ع\nشكراً لتعاملك معنا!"
                    encoded_wa = urllib.parse.quote(wa_text)
                    wa_link = f"https://wa.me/{c_ph}?text={encoded_wa}" if c_ph else f"https://wa.me/?text={encoded_wa}"
                    st.markdown(f"📲 [إرسال الفاتورة عبر الواتساب]({wa_link})", unsafe_allow_html=True)
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

with tab8:
    st.subheader("💰 صندوق الوردية والمصاريف اليومية")
    with st.form("add_expense_form", clear_on_submit=True):
        exp_title = st.text_input("بيان المصروف (مثل: إيجار، خطوط نقل، ضيافة):")
        exp_amount_str = st.text_input("المبلغ (د.ع):", "0")
        if st.form_submit_button("تسجيل المصروف"):
            if exp_title.strip():
                try:
                    exp_val = float(exp_amount_str.strip())
                    st.session_state.expenses_list.append({
                        "البيان": str(exp_title.strip()),
                        "المبلغ": float(exp_val),
                        "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    log_audit("تسجيل مصروف", f"مصروف {exp_title} بقيمة {exp_val}")
                    st.success("تم تسجيل المصروف بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("يرجى إدخال مبلغ صحيح.")
            else:
                st.warning("يرجى كتابة بيان المصروف.")

    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)
        total_exp = sum(e["المبلغ"] for e in st.session_state.expenses_list)
        st.markdown(f"### 📉 إجمالي المصروفات: **{total_exp:,.0f} د.ع**")
    else:
        st.info("لا توجد مصروفات مسجلة اليوم.")

with tab9:
    st.subheader("📊 الرسوم البيانية والتقارير المالية وحساب صافي الأرباح")
    try:
        res_rep_inv = supabase.table("invoices").select("*").eq("username", username).execute()
        rep_invoices = res_rep_inv.data if res_rep_inv.data else []
    except:
        rep_invoices = []

    if rep_invoices:
        total_sales_sum = sum(i['total_price'] for i in rep_invoices)
        total_cost_sum = sum(i.get('cost_price', 0) for i in rep_invoices)
        total_net_profit = total_sales_sum - total_cost_sum
        total_collected_cash = sum(i['paid_amount'] for i in rep_invoices)
        total_remaining_debts = sum(i['remaining_amount'] for i in rep_invoices)

        c_r1, c_r2, c_r3, c_r4 = st.columns(4)
        c_r1.metric("إجمالي المبيعات", f"{total_sales_sum:,.0f} د.ع")
        c_r2.metric("إجمالي تكلفة البضاعة", f"{total_cost_sum:,.0f} د.ع")
        c_r3.metric("صافي الأرباح", f"{total_net_profit:,.0f} د.ع")
        c_r4.metric("الديون المتبقية", f"{total_remaining_debts:,.0f} د.ع")

        df_rep = pd.DataFrame(rep_invoices)
        st.bar_chart(df_rep, x="created_date", y="total_price")
    else:
        st.info("لا توجد بيانات كافية لعرض الرسوم البيانية والتقارير.")

with tab10:
    st.subheader("📜 سجل النشاطات (Audit Trail)")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد سجلات نشاط حتى الآن.")

with tab11:
    st.subheader("📖 دليل الاستخدام والمميزات والدعم الفني")
    st.markdown("""
    ### مرحباً بك في نظام Yasser Web POS 🛍️
    - **إضافة المادة وتوريد الكميات:** أضف منتجاتك بسعر القطعة المفرد والكمية، ويمكنك توريد كميات إضافية لنفس المنتج دون الحاجة لحذفه وإعادة إنشائه.
    - **شبكة المبيعات:** عرض المواد على شكل شبكة بطاقات مع زر إضافة للسلة لسهولة اختيار المواد.
    - **التعبئة التلقائية للعملاء:** عند إتمام البيع، اختر العميل المسجل وسيتم تعبئة رقمه وعنوانه تلقائياً.
    - **الفواتير والواتساب:** توليد فواتير رسمية قابلة للطباعة والإرسال الفوري عبر الواتساب.
    """)
