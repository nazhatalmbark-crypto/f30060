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
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - النظام الشامل لإدارة المحلات", page_icon="🛍️", layout="wide")

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
            "📦 جرد المخزن", 
            "🏷️ الباركود",
            "👥 إدارة العملاء", 
            "💵 سداد الديون",
            "🏭 إدارة الموردين",
            "🛒 سلة المبيعات", 
            "📄 سجل الفواتير", 
            "💰 صندوق الوردية", 
            "📊 الرسوم والتقارير",
            "📜 سجل النشاطات",
            "📖 الدليل الشامل ومعاينة الطباعة"
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

if "memory_customers" not in st.session_state:
    st.session_state.memory_customers = []

if "memory_products" not in st.session_state:
    st.session_state.memory_products = []

if "memory_invoices" not in st.session_state:
    st.session_state.memory_invoices = []

if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None

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
                <h2>YASSER WEB - فاتورة طلبية توصيل رسمية</h2>
                <p>التاريخ والوقت: {inv['created_date']}</p>
            </div>
            <div class="info">
                <p><strong>رقم الفاتورة:</strong> {inv['invoice_code']}</p>
                <p><strong>اسم الزبون / المحل:</strong> {inv['customer_name']}</p>
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
                <p>المبلغ الكلي: {int(inv['total_price']):,} دينار عراقي</p>
                <p>المبلغ الواصل: {int(inv['paid_amount']):,} دينار عراقي</p>
                <p>المتبقي (الدين): {int(inv['remaining_amount']):,} دينار عراقي</p>
            </div>
            <div class="footer">
                <p>شكراً لتعاملكم معنا - جاهزة للصقها على شحنة التوصيل وتسليمها لشركة النقل</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def generate_html_receipt(rec):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>سند قبض - {rec['customer_name']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; }}
            .receipt-box {{ max-width: 600px; margin: auto; padding: 30px; border: 2px dashed #333; background: #fff; }}
            .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ font-size: 16px; line-height: 2.0; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 14px; border-top: 1px solid #ddd; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="receipt-box">
            <div class="header">
                <h2>YASSER WEB - سند قبض نقدية</h2>
                <p>التاريخ والوقت: {rec['date']}</p>
            </div>
            <div class="info">
                <p><strong>اسم العميل / المكلف:</strong> {rec['customer_name']}</p>
                <p><strong>المبلغ المستلم:</strong> {int(rec['amount']):,} دينار عراقي</p>
                <p><strong>البيان:</strong> استلمت من السيد المذكور أعلاه المبلغ و ثبّت في سجل الذمم كدفعة تسديد حساب.</p>
            </div>
            <div class="footer">
                <p>توقيع أمين الصندوق / المحل: ........................</p>
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
                    st.session_state.logged_in_user = str(login_user.strip())
                    st.session_state.user_role = str(login_role)
                    st.session_state.is_vip = True
                    log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {login_user.strip()}")
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
                    
    with auth_tab2:
        with st.form("signup_form"):
            new_user = st.text_input("اختر اسم المستخدم أو اسم المحل الجديد:")
            signup_role = st.selectbox("حدد الصلاحية للحساب الجديد:", ["مشرف النظام", "كاشير", "مسؤول مبيعات"])
            signup_submitted = st.form_submit_button(t["signup_btn"], type="primary")
            
            if signup_submitted:
                if new_user.strip():
                    st.session_state.logged_in_user = str(new_user.strip())
                    st.session_state.user_role = str(signup_role)
                    st.session_state.is_vip = True
                    log_audit("إنشاء حساب جديد", f"تم إنشاء حساب باسم {new_user.strip()}")
                    st.success("🎉 تم إنشاء الحساب بنجاح!")
                    st.rerun()
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

current_invoices_data = st.session_state.memory_invoices

backup_data = {
    "username": str(username),
    "customers": st.session_state.memory_customers,
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

st.sidebar.success("🌟 النسخة مفعلة بالكامل وتعمل بذاكرة الآمان")

if st.sidebar.button(t["logout"]):
    log_audit("تسجيل خروج", f"تم تسجيل الخروج للمستخدم {username}")
    st.session_state.logged_in_user = None
    st.session_state.is_vip = False
    st.session_state.cart = []
    st.rerun()

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs(t["tabs"])

with tab1:
    st.subheader("➕ واجهة إضافة مادة أو بضاعة جديدة للمخزن")
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
                    
                    new_prod_id = len(st.session_state.memory_products) + 1
                    st.session_state.memory_products.append({
                        "id": new_prod_id,
                        "username": str(username),
                        "product_name": str(p_name.strip()),
                        "color": str(p_color.strip() if p_color else "عام"),
                        "size": str(p_size.strip() if p_size else "عام"),
                        "buy_price": float(p_buy),
                        "sell_price": float(p_sell),
                        "quantity": int(p_qty),
                        "barcode": str(p_barcode.strip() if p_barcode else "بدون")
                    })
                    log_audit("إضافة منتج", f"تمت إضافة المنتج ({p_name.strip()})")
                    st.success(f"تمت إضافة المادة ({p_name}) بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("❌ خطأ: يرجى إدخال أرقام صحيحة.")
            else:
                st.warning("يرجى كتابة اسم المادة.")

with tab2:
    st.subheader("📦 جرد المخزن الشامل وحساب أرباح القطع")
    all_products = st.session_state.memory_products

    low_stock_items = [p for p in all_products if p['quantity'] <= 2]
    if low_stock_items:
        low_names = " ، ".join([f"**{i['product_name']}**" for i in low_stock_items])
        st.error(f"🚨 **تنبيه قرب نفاد المخزون:** المواد التالية وشيكة النفاذ أو نفدت: {low_names}")

    search_prod_term = st.text_input("🔍 بحث عن مادة في المخزن:", "")

    if all_products:
        filtered_products = all_products
        if search_prod_term:
            filtered_products = [p for p in filtered_products if search_prod_term.lower() in p['product_name'].lower()]

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
        st.info("المخزن فارغ حالياً. قم بإضافة مواد من تبويب (إضافة مادة).")

with tab3:
    st.subheader("🏷️ توليد وعرض باركود المواد")
    all_products_bc = st.session_state.memory_products
    search_barcode_term = st.text_input("🔍 بحث عن مادة لطباعة الباركود الخاص بها:", "")

    if all_products_bc:
        filtered_bc_products = all_products_bc
        if search_barcode_term:
            filtered_bc_products = [p for p in filtered_bc_products if search_barcode_term.lower() in p['product_name'].lower() or search_barcode_term.lower() in p.get('barcode','').lower()]

        for item in filtered_bc_products:
            with st.container(border=True):
                st.markdown(f"### 📦 المادة: {item['product_name']}")
                st.markdown(f"🏷️ **الباركود المسجل:** `{item.get('barcode', 'بدون')}`")
                
                b_code_val = item.get('barcode', '')
                if not b_code_val or b_code_val == "بدون":
                    b_code_val = f"PRD{item['id']}"
                
                try:
                    rv = barcode.get('code128', str(b_code_val), writer=ImageWriter())
                    buffer_bc = io.BytesIO()
                    rv.write(buffer_bc)
                    st.image(buffer_bc.getvalue(), caption=f"باركود المادة: {b_code_val}", width=250)
                except Exception as ex:
                    st.error(f"تعذر توليد الباركود: {ex}")
    else:
        st.info("لا توجد مواد مسجلة لتوليد الباركود لها.")

with tab4:
    st.subheader("👥 إدارة العملاء (اسم الشخص/المحل، رقم الهاتف، والمحافظة)")
    
    with st.form("add_customer_db_form", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            c_name = st.text_input("اسم الشخص أو اسم المحل *:")
            c_address = st.text_input("المحافظة / العنوان:")
        with col_c2:
            c_phone = st.text_input("رقم الهاتف *:")
            c_notes = st.text_input("ملاحظات إضافية:")
            
        if st.form_submit_button("تسجيل العميل وحفظه", type="primary"):
            if c_name.strip() and c_phone.strip():
                st.session_state.memory_customers.append({
                    "customer_name": str(c_name.strip()),
                    "phone": str(c_phone.strip()),
                    "address": str(c_address.strip() if c_address else "بغداد"),
                    "notes": str(c_notes.strip() if c_notes else "")
                })
                log_audit("إضافة عميل", f"تم تسجيل العميل {c_name}")
                st.success(f"تم تسجيل العميل ({c_name}) بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى كتابة اسم الشخص/المحل ورقم الهاتف على الأقل.")

    st.divider()
    st.subheader("📋 قائمة العملاء المسجلين")
    if st.session_state.memory_customers:
        df_cust = pd.DataFrame(st.session_state.memory_customers)
        st.dataframe(df_cust, use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلين حالياً.")

with tab5:
    st.subheader("💵 نظام سداد الديون وإصدار سندات القبض")
    debt_cust_list = [c["customer_name"] for c in st.session_state.memory_customers]

    if not debt_cust_list:
        st.info("لا توجد عملاء مسجلين لعرض الديون.")
    else:
        selected_debt_customer = st.selectbox("اختر اسم العميل لتسديد الديون:", debt_cust_list, key="debt_pay_cust_select")
        
        customer_invoices = [inv for inv in st.session_state.memory_invoices if inv['customer_name'] == selected_debt_customer]
        total_customer_debt = sum(float(inv.get('remaining_amount', 0)) for inv in customer_invoices)
        
        st.markdown(f"### 📌 إجمالي الدين الكلي على العميل (`{selected_debt_customer}`): **{int(total_customer_debt):,} د.ع**")
        
        if customer_invoices:
            with st.expander("📄 عرض تفاصيل الفواتير المسجلة على هذا العميل"):
                for cinv in customer_invoices:
                    st.write(f"- **رقم الفاتورة:** {cinv['invoice_code']} | **المبلغ الكلي:** {int(cinv['total_price']):,} د.ع | **الواصل:** {int(cinv['paid_amount']):,} د.ع | **المتبقي:** `{int(cinv['remaining_amount']):,}` د.ع | **التاريخ:** {cinv['created_date']}")
        
        st.divider()
        with st.form("pay_debt_form"):
            payment_input_str = st.text_input("أدخل المبلغ المراد تسديده (د.ع):", "0")
            pay_submitted = st.form_submit_button("إتمام التسديد وتصفير الديون", type="primary")
            
            if pay_submitted:
                try:
                    payment_val = float(payment_input_str.strip() if payment_input_str.strip() else "0")
                    if payment_val < 0:
                        st.warning("يرجى إدخال مبلغ صالح.")
                    elif payment_val > total_customer_debt:
                        st.error("❌ المبلغ المدخل أكبر من إجمالي الدين المطلوب على العميل!")
                    else:
                        remaining_payment = payment_val
                        for cinv in customer_invoices:
                            if remaining_payment <= 0:
                                break
                            curr_rem = float(cinv.get('remaining_amount', 0))
                            if curr_rem > 0:
                                if remaining_payment >= curr_rem:
                                    new_paid = float(cinv['total_price'])
                                    new_rem = 0.0
                                    new_type = "🟢 نقد بالكامل (كاش)"
                                    remaining_payment -= curr_rem
                                else:
                                    new_paid = float(cinv['paid_amount']) + remaining_payment
                                    new_rem = curr_rem - remaining_payment
                                    new_type = "🔵 دفعة جزئية (أقساط)"
                                    remaining_payment = 0.0
                                
                                cinv['paid_amount'] = float(new_paid)
                                cinv['remaining_amount'] = float(new_rem)
                                cinv['payment_type'] = str(new_type)
                        
                        st.session_state.last_receipt = {
                            "customer_name": str(selected_debt_customer),
                            "amount": float(payment_val),
                            "date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                        }

                        log_audit("سداد ديون وسند قبض", f"تم تسديد مبلغ {payment_val:,} د.ع للعميل {selected_debt_customer}")
                        st.success(f"🎉 تم تسديد مبلغ {payment_val:,.0f} دينار بنجاح وتحديث حساب العميل وإصدار سند القبض!")
                        st.rerun()
                except ValueError:
                    st.error("❌ يرجى إدخال رقم صحيح للمبلغ.")

        if st.session_state.get('last_receipt'):
            rec = st.session_state.last_receipt
            st.divider()
            st.markdown("### 🧾 سند القبض (إيصال استلام النقدية) الأخير:")
            with st.container(border=True):
                st.write(f"👤 **العميل:** {rec['customer_name']}")
                st.write(f"💵 **المبلغ المستلم:** **{int(rec['amount']):,} د.ع**")
                st.write(f"📅 **وقت الاستلام:** {rec['date']}")
                st.info("💡 تم استلام المبلغ المذكور أعلاه كدفعة تسديد حساب وإطفاء للذمم.")
                
                html_rec_data = generate_html_receipt(rec)
                st.download_button(
                    label="🖨️ تحميل سند القبض وطباعته (HTML)",
                    data=html_rec_data,
                    file_name=f"receipt_{rec['customer_name']}.html",
                    mime="text/html"
                )

with tab6:
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
        st.info("لا يوجد موردين مسجلين.")

with tab7:
    st.subheader("🛒 سلة المبيعات وإتمام الفاتورة")
    
    if st.session_state.cart:
        total_cart_price = 0.0
        for idx, c_item in enumerate(st.session_state.cart):
            cols_cart = st.columns([3, 2, 2, 1])
            with cols_cart[0]:
                st.write(f"**{c_item['product_name']}** ({c_item['color']} / {c_item['size']})")
            with cols_cart[1]:
                new_q = st.number_input(f"الكمية", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_q_{c_item['id']}")
                c_item['qty'] = new_q
            with cols_cart[2]:
                item_total = float(c_item['sell_price']) * float(c_item['qty'])
                total_cart_price += item_total
                st.write(f"المجموع: **{int(item_total):,}** د.ع")
            with cols_cart[3]:
                if st.button("❌", key=f"del_cart_{c_item['id']}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        st.divider()
        st.markdown(f"### 💵 المجموع الكلي المطلوب: **{int(total_cart_price):,} د.ع**")
        
        cust_names_list = [c["customer_name"] for c in st.session_state.memory_customers]
            
        if not cust_names_list:
            st.warning("⚠️ تنبيه: يرجى إضافة عميل أولاً من تبويب (إدارة العملاء) لتتمكن من اختيار اسمه هنا وإتمام الفاتورة!")
            selected_customer_name = ""
        else:
            selected_customer_name = st.selectbox("اختر اسم الزبون / المحل المسجل:", cust_names_list)
        
        st.write("---")
        st.markdown("#### 💰 طريقة الدفع:")
        paid_input_str = st.text_input("أدخل المبلغ الذي دفعه الزبون (د.ع - اكتب 0 إذا كان آجل بالكامل):", value="0")
        
        try:
            paid_amount = float(paid_input_str.strip() if paid_input_str.strip() else "0")
            if paid_amount < 0: 
                paid_amount = 0.0
            if paid_amount > total_cart_price: 
                paid_amount = float(total_cart_price)
        except ValueError:
            paid_amount = 0.0
            
        remaining_amount = float(total_cart_price) - float(paid_amount)

        if paid_amount >= total_cart_price:
            auto_pay_type = "🟢 نقد بالكامل (كاش)"
        elif paid_amount == 0.0:
            auto_pay_type = "🔴 دين كامل (آجل)"
        else:
            auto_pay_type = "🔵 دفعة جزئية (أقساط)"

        st.info(f"💡 **تحليل النظام التلقائي للفاتورة:** {auto_pay_type} | الواصل: **{int(paid_amount):,} د.ع** | المتبقي (الدين): **{int(remaining_amount):,} د.ع**")

        if st.button("💾 إتمام البيع، خصم المخزن، وحفظ الفاتورة", type="primary"):
            if not selected_customer_name:
                st.error("❌ خطأ: يرجى اختيار عميل مسجل من القائمة أو إضافته أولاً.")
            else:
                try:
                    prod_names_str = []
                    total_buy_cost_of_invoice = 0.0
                    
                    for c_item in st.session_state.cart:
                        prod_names_str.append(f"{c_item['product_name']} ({c_item['color']}) [العدد: {c_item['qty']}]")
                        total_buy_cost_of_invoice += (float(c_item['buy_price']) * float(c_item['qty']))
                        
                        for p_item in st.session_state.memory_products:
                            if p_item["id"] == c_item["id"]:
                                p_item["quantity"] = max(0, int(p_item["quantity"]) - int(c_item['qty']))
                    
                    inv_id = len(st.session_state.memory_invoices) + 1
                    inv_code = f"INV-{inv_id:03d}"
                    
                    st.session_state.memory_invoices.insert(0, {
                        "id": inv_id,
                        "username": str(username),
                        "invoice_code": str(inv_code),
                        "customer_name": str(selected_customer_name),
                        "products_text": str(" ، ".join(prod_names_str)),
                        "total_price": float(total_cart_price),
                        "cost_price": float(total_buy_cost_of_invoice),
                        "paid_amount": float(paid_amount),
                        "remaining_amount": float(remaining_amount),
                        "payment_type": str(auto_pay_type),
                        "created_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    
                    log_audit("إتمام بيع", f"فاتورة {inv_code} للزبون {selected_customer_name}")
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع، حفظ الفاتورة، وتحديث المخزن بنجاح وتلقائي!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ أثناء حفظ الفاتورة: {e}")
    else:
        st.info("🛒 السلة فارغة.")

with tab8:
    st.subheader("📄 سجل الفواتير وإرسالها عبر الواتساب")
    invoices_list = st.session_state.memory_invoices

    if invoices_list:
        for inv in invoices_list:
            with st.expander(f"📄 فاتورة: {inv['invoice_code']} | الزبون: {inv['customer_name']} | المجموع: {int(inv['total_price']):,} د.ع"):
                st.write(f"📅 **التاريخ:** {inv['created_date']}")
                st.write(f"🛍️ **المنتجات:** {inv['products_text']}")
                st.write(f"💵 **المبلغ الكلي:** {int(inv['total_price']):,} د.ع | **الواصل:** {int(inv['paid_amount']):,} د.ع | **المتبقي:** `{int(inv['remaining_amount']):,}` د.ع")
                st.write(f"📌 **الحالة:** {inv['payment_type']}")

                html_inv = generate_html_invoice(inv)
                st.download_button(
                    label="📥 تحميل الفاتورة (HTML)",
                    data=html_inv,
                    file_name=f"invoice_{inv['invoice_code']}.html",
                    mime="text/html",
                    key=f"dl_inv_{inv['id']}"
                )

                cust_ph = ""
                for c in st.session_state.memory_customers:
                    if c["customer_name"] == inv['customer_name']:
                        cust_ph = c["phone"]
                        break

                if cust_ph:
                    wa_msg = f"مرحباً بك أستاذ {inv['customer_name']}\nتفاصيل فاتورتك رقم {inv['invoice_code']}:\nالمجموع: {int(inv['total_price']):,} د.ع\nالواصل: {int(inv['paid_amount']):,} د.ع\nالمتبقي: {int(inv['remaining_amount']):,} د.ع\nشكراً لتعاملكم مع Yasser Web!"
                    encoded_msg = urllib.parse.quote(wa_msg)
                    wa_url = f"https://wa.me/{cust_ph}?text={encoded_msg}"
                    st.markdown(f"📱 [إرسال الفاتورة عبر واتساب للزبون]({wa_url})", unsafe_allow_html=True)
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

with tab9:
    st.subheader("💰 صندوق الوردية والمصاريف اليومية")
    with st.form("expenses_form", clear_on_submit=True):
        exp_desc = st.text_input("بيان المصروف (مثال: أجور نقل، صيانة، ضيافة):")
        exp_amount_str = st.text_input("المبلغ (د.ع):", "0")
        if st.form_submit_button("تسجيل المصروف"):
            if exp_desc.strip():
                try:
                    exp_amt = float(exp_amount_str.strip() if exp_amount_str.strip() else "0")
                    st.session_state.expenses_list.append({
                        "البيان": str(exp_desc.strip()),
                        "المبلغ": int(exp_amt),
                        "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    log_audit("تسجيل مصروف", f"تم تسجيل مصروف {exp_desc} بمبلغ {exp_amt}")
                    st.success("تم تسجيل المصروف بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("أدخل مبلغاً صحيحاً.")
            else:
                st.warning("أدخل بيان المصروف.")

    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)
    else:
        st.info("لا توجد مصاريف مسجلة في هذه الوردية.")

with tab10:
    st.subheader("📊 الرسوم البيانية والتقارير المالية")
    rep_invoices = st.session_state.memory_invoices

    if rep_invoices:
        df_rep = pd.DataFrame(rep_invoices)
        total_sales = df_rep['total_price'].sum()
        total_costs = df_rep['cost_price'].sum()
        net_profit = float(total_sales) - float(total_costs)

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("إجمالي المبيعات", f"{int(total_sales):,} د.ع")
        col_r2.metric("إجمالي التكلفة", f"{int(total_costs):,} د.ع")
        col_r3.metric("صافي الأرباح", f"{int(net_profit):,} د.ع", delta=f"{int(net_profit):,} د.ع")

        st.divider()
        st.bar_chart(df_rep, x="invoice_code", y="total_price")
    else:
        st.info("لا توجد بيانات كافية لعرض التقارير والرسوم البيانية.")

with tab11:
    st.subheader("📜 سجل النشاطات والعمليات")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد نشاطات مسجلة بعد.")

with tab12:
    st.markdown("""
    <div style="font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; color: #000; background: #ffffff;">

        <!-- صندوق الدعم والتواصل الفني البسيط -->
        <div style="border: 2px solid #000; padding: 20px; margin-bottom: 30px; background: #fff;">
            <h2 style="font-size: 28px; color: #000; margin-top: 0; font-weight: bold;">📞 معلومات التواصل والدعم الفني:</h2>
            <p style="font-size: 22px; margin: 8px 0;"><b>اسم المسؤول:</b> """ + str(username) + """</p>
            <p style="font-size: 22px; margin: 8px 0;"><b>حساب انستغرام:</b> <a href="https://instagram.com/yaser120120120120" target="_blank" style="color: #0000EE; font-weight: bold;">@yaser120120120120</a></p>
            <p style="font-size: 20px; margin: 8px 0;">نحن في الخدمة دائماً لدعمكم عبر نظام ياسر ويب.</p>
        </div>

        <!-- الصندوق الرئيسي للدليل -->
        <div style="border: 3px solid #000; padding: 30px; background: #ffffff;">
            <h1 style="font-size: 36px; text-align: center; margin-top: 0; margin-bottom: 30px; font-weight: bold; border-bottom: 3px solid #000; padding-bottom: 15px;">
                📖 الدليل الشامل لنظام ياسر ويب
            </h1>

            <!-- التبويب 1 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">1️⃣ خانة (➕ إضافة مادة)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> تتيح إدخال أي بضاعة أو منتج جديد للمخزن.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> إدخال اسم المادة، اللون، القياس، سعر الشراء، سعر البيع، الكمية، والباركود، ثم الضغط على حفظ.</p>
            </div>

            <!-- التبويب 2 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">2️⃣ خانة (📦 جرد المخزن)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> عرض كافة مواد المخزن مع خاصية البحث السريع.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> يحسب النظام ربح القطعة تلقائياً، ينبهك بحالة نفاد المخزون، ويتيح إضافة المواد للسلة.</p>
            </div>

            <!-- التبويب 3 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">3️⃣ خانة (🏷️ الباركود)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> توليد رموز باركود واضحة ورسمية (Code 128) لكل منتج.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> طباعة الباركود ولصقه على السلع والمنتجات بالمحل.</p>
            </div>

            <!-- التبويب 4 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">4️⃣ خانة (👥 إدارة العملاء)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> تسجيل وإدارة بيانات الزبائن والمحلات المتعاملة معك.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> حفظ الاسم، رقم الهاتف الأساسي، المحافظة، والملاحظات بجدول منظم.</p>
            </div>

            <!-- التبويب 5 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">5️⃣ خانة (💵 سداد الديون)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> إدارة الذمم المالية وديون العملاء بدقة.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> اختيار العميل، إدخال المبلغ المدفوع ليقوم النظام بتحديث الحساب وإصدار سند قبض.</p>
            </div>

            <!-- التبويب 6 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">6️⃣ خانة (🏭 إدارة الموردين)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> حفظ أسماء وأرقام وتخصصات الموردين الأساسيين.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> لضمان بقاء جهات تجهيز البضائع حاضرة ومتاحة دائماً.</p>
            </div>

            <!-- التبويب 7 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">7️⃣ خانة (🛒 سلة المبيعات)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> المحطة الرئيسية للبيع وإصدار الفواتير.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> حساب المجموع، تحديد العميل، تحليل الدفع (كاش/آجل)، والخصم التلقائي من المخزن.</p>
            </div>

            <!-- التبويب 8 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">8️⃣ خانة (📄 سجل الفواتير)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> أرشيف شامل لجميع الفواتير والعمليات السابقة.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> إمكانية تحميل الفاتورة HTML للطباعة، أو إرسال تفاصيلها مباشرة عبر واتساب للزبون.</p>
            </div>

            <!-- التبويب 9 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">9️⃣ خانة (💰 صندوق الوردية)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> تسجيل المصاريف النثرية والتشغيلية اليومية.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> إدخال بيان المصروف والمبلغ لضبط الصندوق اليومي بدقة.</p>
            </div>

            <!-- التبويب 10 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">🔟 خانة (📊 الرسوم والتقارير)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> اللوحة المالية العليا لنشاطك التجاري.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> عرض إجمالي المبيعات، التكاليف، وصافي الأرباح الحقيقية مع رسوم بيانية.</p>
            </div>

            <!-- التبويب 11 -->
            <div style="padding-bottom: 20px; margin-bottom: 20px; border-bottom: 2px solid #000;">
                <h2 style="font-size: 26px; margin-top: 0; margin-bottom: 10px; font-weight: bold;">1️⃣1️⃣ خانة (📜 سجل النشاطات)</h2>
                <p style="font-size: 20px; margin: 5px 0;"><b>العملية:</b> سجل رقابي دقيق ومفصل لكل حركات المستخدمين.</p>
                <p style="font-size: 20px; margin: 5px 0;"><b>الخطوات:</b> توثيق عمليات الدخول، البيع، والإضافة مع التوقيت واسم المستخدم.</p>
            </div>

            <!-- التبويب 12: معاينة النماذج -->
            <div>
                <h2 style="font-size: 28px; text-align: center; margin-top: 0; margin-bottom: 20px; font-weight: bold;">
                    🖨️ 1️⃣2️⃣ معاينة نماذج الطباعة الرسمية
                </h2>
                <p style="font-size: 20px; text-align: center; margin-bottom: 25px;">
                    هذه النماذج توضح شكل الفاتورة ووصل السداد تماماً كما يستلمها الزبون:
                </p>
                
                <div style="display: flex; gap: 20px; flex-wrap: wrap; justify-content: center;">
                    
                    <!-- نموذج الفاتورة -->
                    <div style="flex: 1; min-width: 300px; border: 2px solid #000; padding: 20px; background: #fff;">
                        <h3 style="font-size: 22px; text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-top: 0; font-weight: bold;">
                            📄 نموذج فاتورة بيع
                        </h3>
                        <p style="font-size: 18px; margin: 6px 0;"><b>اسم المحل:</b> YASSER WEB</p>
                        <p style="font-size: 18px; margin: 6px 0;"><b>رقم الفاتورة:</b> INV-001</p>
                        <p style="font-size: 18px; margin: 6px 0;"><b>اسم الزبون:</b> زبون تجريبي</p>
                        <p style="font-size: 18px; margin: 6px 0;"><b>المنتجات:</b> جهاز أو مادة [العدد: 2]</p>
                        <hr style="border: 1px dashed #000; margin: 12px 0;">
                        <p style="font-size: 18px; font-weight: bold; margin: 6px 0;">المبلغ الكلي: 50,000 د.ع</p>
                        <p style="font-size: 18px; font-weight: bold; margin: 6px 0;">المبلغ الواصل: 50,000 د.ع</p>
                        <p style="font-size: 18px; font-weight: bold; margin: 6px 0;">المتبقي (الدين): 0 د.ع</p>
                    </div>

                    <!-- نموذج سند القبض -->
                    <div style="flex: 1; min-width: 300px; border: 2px dashed #000; padding: 20px; background: #fff;">
                        <h3 style="font-size: 22px; text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-top: 0; font-weight: bold;">
                            🧾 نموذج سند قبض نقدية
                        </h3>
                        <p style="font-size: 18px; margin: 6px 0;"><b>مؤسسة:</b> YASSER WEB المالية</p>
                        <p style="font-size: 18px; margin: 6px 0;"><b>اسم العميل:</b> زبون تسديد ديون</p>
                        <p style="font-size: 18px; margin: 6px 0;"><b>المبلغ المستلم:</b> 25,000 د.ع</p>
                        <p style="font-size: 18px; margin: 6px 0;"><b>البيان:</b> دفعة تسديد ذمم مالية.</p>
                        <hr style="border: 1px solid #000; margin: 20px 0 10px 0;">
                        <p style="font-size: 18px; margin: 6px 0;"><b>توقيع أمين الصندوق:</b> ........................</p>
                    </div>

                </div>
            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)
