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

st.set_page_config(page_title="Yasser Web Pro - النظام الذكي المتكامل", page_icon="🛍️", layout="wide")

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
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

if "lang" not in st.session_state:
    st.session_state.lang = "العربية"

lang_dict = {
    "العربية": {
        "title": "🛍️ Yasser Web Pro - النظام الذكي الشامل لإدارة المحلات والمبيعات",
        "login_title": "🔐 بوابة الدخول الذكية لنظام ياسر ويب",
        "login_tab": "🔑 تسجيل الدخول",
        "signup_tab": "✨ إنشاء حساب جديد",
        "username_label": "اسم المستخدم أو اسم المحل:",
        "login_btn": "دخول للنظام",
        "signup_btn": "إنشاء حساب جديد",
        "settings": "⚙️ إعدادات النظام والنسخ الاحتياطي",
        "role_label": "👤 الصلاحية:",
        "cart_badge": "🛒 المنتجات بالسلة:",
        "backup_title": "🔄 النسخ الاحتياطي الفوري",
        "backup_download": "📥 تحميل النسخة الاحتياطية (JSON)",
        "logout": "تسجيل الخروج",
        "tabs": [
            "➕ إضافة مادة ذكية", 
            "📦 المخزن وجرد البضائع", 
            "🏷️ توليد الباركود",
            "👥 إدارة العملاء والديون", 
            "💵 سندات القبض والدفع",
            "🏭 إدارة الموردين",
            "🛒 نقطة البيع (POS) والسلة", 
            "📄 سجل الفواتير الذكي", 
            "💰 صندوق الوردية والمصروفات", 
            "📊 تقارير الأرباح والذكاء الاصطناعي",
            "📜 سجل النشاطات الكامل",
            "📖 الدليل الشامل ومعاينة الطباعة"
        ]
    }
}

t = lang_dict[st.session_state.lang]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "user_role" not in st.session_state:
    st.session_state.user_role = "مدير عام"

if "suppliers_list" not in st.session_state or isinstance(st.session_state.suppliers_list, pd.DataFrame):
    st.session_state.suppliers_list = []

if "cart" not in st.session_state or isinstance(st.session_state.cart, pd.DataFrame):
    st.session_state.cart = []

if "expenses_list" not in st.session_state or isinstance(st.session_state.expenses_list, pd.DataFrame):
    st.session_state.expenses_list = []

if "audit_logs" not in st.session_state or isinstance(st.session_state.audit_logs, pd.DataFrame):
    st.session_state.audit_logs = []

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
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #ccc; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); background: #fff; border-radius: 8px; }}
            .header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ margin-bottom: 20px; font-size: 15px; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: right; font-size: 14px; }}
            th {{ background-color: #f8f9fa; color: #2c3e50; }}
            .totals {{ font-size: 16px; font-weight: bold; text-align: left; margin-top: 15px; line-height: 1.8; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 13px; color: #666; border-top: 1px dashed #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <h2>YASSER WEB PRO - فاتورة بيع وتوصيل رسمية</h2>
                <p>تاريخ الإصدار: {inv['created_date']}</p>
            </div>
            <div class="info">
                <p><strong>رقم الفاتورة:</strong> {inv['invoice_code']}</p>
                <p><strong>اسم العميل / المحل:</strong> {inv['customer_name']}</p>
                <p><strong>حالة وطريقة الدفع:</strong> {inv['payment_type']}</p>
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
                <p>المبلغ الإجمالي: {int(inv['total_price']):,} دينار عراقي</p>
                <p>المبلغ الواصل: {int(inv['paid_amount']):,} دينار عراقي</p>
                <p>المتبقي (الدين): {int(inv['remaining_amount']):,} دينار عراقي</p>
            </div>
            <div class="footer">
                <p>شكراً لتعاملكم مع نظام ياسر ويب برو - جميع الحقوق محفوظة</p>
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
            .receipt-box {{ max-width: 600px; margin: auto; padding: 30px; border: 2px dashed #2c3e50; background: #fff; border-radius: 8px; }}
            .header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ font-size: 16px; line-height: 2.0; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 14px; border-top: 1px solid #ddd; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="receipt-box">
            <div class="header">
                <h2>YASSER WEB PRO - سند قبض نقدي رسمي</h2>
                <p>التاريخ والوقت: {rec['date']}</p>
            </div>
            <div class="info">
                <p><strong>اسم العميل:</strong> {rec['customer_name']}</p>
                <p><strong>المبلغ المستلم:</strong> {int(rec['amount']):,} دينار عراقي</p>
                <p><strong>البيان:</strong> استلمنا من السيد المذكور أعلاه المبلغ وتثبيته كدفعة تسديد لحسابه الجاري.</p>
            </div>
            <div class="footer">
                <p>توقيع أمين الصندوق / الإدارة: ........................</p>
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
            login_role = st.selectbox("الصلاحية:", ["مدير عام", "مشرف مبيعات", "كاشير رئيسي"])
            login_submitted = st.form_submit_button(t["login_btn"], type="primary")
            
            if login_submitted:
                if login_user.strip():
                    st.session_state.logged_in_user = str(login_user.strip())
                    st.session_state.user_role = str(login_role)
                    log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {login_user.strip()}")
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
                    
    with auth_tab2:
        with st.form("signup_form"):
            new_user = st.text_input("اختر اسم المستخدم أو المحل الجديد:")
            signup_role = st.selectbox("صلاحية الحساب الجديد:", ["مدير عام", "مشرف مبيعات", "كاشير رئيسي"])
            signup_submitted = st.form_submit_button(t["signup_btn"], type="primary")
            
            if signup_submitted:
                if new_user.strip():
                    st.session_state.logged_in_user = str(new_user.strip())
                    st.session_state.user_role = str(signup_role)
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

backup_data = {
    "username": str(username),
    "customers": st.session_state.memory_customers,
    "suppliers": list(st.session_state.suppliers_list),
    "invoices": st.session_state.memory_invoices,
    "expenses": list(st.session_state.expenses_list),
    "audit_logs": list(st.session_state.audit_logs),
    "export_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
}
backup_json = json.dumps(backup_data, ensure_ascii=False, indent=4, default=str)
st.sidebar.download_button(
    label=t["backup_download"],
    data=backup_json,
    file_name=f"yasser_web_pro_backup_{username}.json",
    mime="application/json"
)

st.sidebar.success("🌟 النسخة الاحترافية مفعلة بالكامل")

if st.sidebar.button(t["logout"]):
    log_audit("تسجيل خروج", f"تم تسجيل الخروج للمستخدم {username}")
    st.session_state.logged_in_user = None
    st.session_state.cart = []
    st.rerun()

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs(t["tabs"])

with tab1:
    st.subheader("➕ إضافة مادة ذكية جديدة للمخزن")
    with st.form("add_product_pro_form", clear_on_submit=True):
        p_name = st.text_input("اسم المادة / المنتج / الجهاز *:")
        c_col, c_sz = st.columns(2)
        with c_col:
            p_color = st.text_input("اللون / الموديل / المواصفات:", "عام")
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
            p_barcode = st.text_input("رمز الباركود (اختياري):", "")
        
        submitted = st.form_submit_button("حفظ وحجز المادة في النظام", type="primary")
        if submitted:
            if p_name.strip():
                try:
                    p_buy = float(p_buy_str.strip())
                    p_sell = float(p_sell_str.strip())
                    p_qty = int(p_qty_str.strip())
                    
                    new_prod_id = len(st.session_state.memory_products) + 1
                    generated_bc = str(p_barcode.strip() if p_barcode else f"PRD{new_prod_id:04d}")
                    
                    st.session_state.memory_products.append({
                        "id": new_prod_id,
                        "username": str(username),
                        "product_name": str(p_name.strip()),
                        "color": str(p_color.strip() if p_color else "عام"),
                        "size": str(p_size.strip() if p_size else "عام"),
                        "buy_price": float(p_buy),
                        "sell_price": float(p_sell),
                        "quantity": int(p_qty),
                        "barcode": generated_bc
                    })
                    log_audit("إضافة منتج", f"تمت إضافة المنتج ({p_name.strip()}) برمز {generated_bc}")
                    st.success(f"تمت إضافة المادة ({p_name}) بنجاح مع الباركود ({generated_bc})!")
                    st.rerun()
                except ValueError:
                    st.error("❌ خطأ: يرجى إدخال قيم رقمية صحيحة في حقول الأعراب والأسعار.")
            else:
                st.warning("يرجى كتابة اسم المادة على الأقل.")

with tab2:
    st.subheader("📦 إدارة المخزن وجرد البضائع المتقدم")
    all_products = st.session_state.memory_products

    low_stock_items = [p for p in all_products if p['quantity'] <= 2]
    if low_stock_items:
        low_names = " ، ".join([f"**{i['product_name']}**" for i in low_stock_items])
        st.error(f"🚨 **تنبيه ذكي لقرب نفاد المخزون:** المواد التالية أصبحت وشيكة النفاد: {low_names}")

    search_prod_term = st.text_input("🔍 بحث سريع عن مادة أو جهاز في المخزن:", "")

    if all_products:
        filtered_products = all_products
        if search_prod_term:
            filtered_products = [p for p in filtered_products if search_prod_term.lower() in p['product_name'].lower() or search_prod_term.lower() in p.get('barcode','').lower()]

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
                        st.error(f"📉 خسارة بالقطعة: {profit_per_unit:,} د.ع")
                    else:
                        st.success(f"📈 ربح القطعة: +{profit_per_unit:,} د.ع")
                    
                    st.markdown(f"🔢 **الكمية المتاحة:** `{int(item['quantity'])}` قطعة")

                    if item['quantity'] > 0:
                        if st.button(f"🛒 إضافة للسلة الذكية", key=f"add_cart_pro_{item['id']}"):
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
                            st.toast(f"✅ تمت الإضافة للسلة بنجاح!", icon="🛒")
                            st.rerun()
                    else:
                        st.warning("⚠️ الكمية نافذة بالكامل")
    else:
        st.info("المخزن فارغ حالياً. قم بإضافة بضائع من تبويب (إضافة مادة ذكية).")

with tab3:
    st.subheader("🏷️ توليد وطباعة باركود المواد والمنتجات")
    all_products_bc = st.session_state.memory_products
    search_barcode_term = st.text_input("🔍 بحث عن مادة لإنشاء وطباعة الباركود:", "")

    if all_products_bc:
        filtered_bc_products = all_products_bc
        if search_barcode_term:
            filtered_bc_products = [p for p in filtered_bc_products if search_barcode_term.lower() in p['product_name'].lower() or search_barcode_term.lower() in p.get('barcode','').lower()]

        for item in filtered_bc_products:
            with st.container(border=True):
                st.markdown(f"### 📦 المادة: {item['product_name']}")
                st.markdown(f"🏷️ **رمز الباركود:** `{item.get('barcode', 'بدون')}`")
                
                b_code_val = item.get('barcode', '')
                if not b_code_val:
                    b_code_val = f"PRD{item['id']}"
                
                try:
                    rv = barcode.get('code128', str(b_code_val), writer=ImageWriter())
                    buffer_bc = io.BytesIO()
                    rv.write(buffer_bc)
                    st.image(buffer_bc.getvalue(), caption=f"باركود رسمي للمادة: {b_code_val}", width=250)
                except Exception as ex:
                    st.error(f"تعذر توليد صورة الباركود: {ex}")
    else:
        st.info("لا توجد مواد مسجلة لتوليد الباركود لها.")

with tab4:
    st.subheader("👥 إدارة العملاء والذمم والديون")
    
    with st.form("add_customer_pro_form", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            c_name = st.text_input("اسم الزبون أو اسم المحل *:")
            c_address = st.text_input("المحافظة / العنوان (مثال: البصرة - العشار):", "البصرة")
        with col_c2:
            c_phone = st.text_input("رقم الهاتف (واتساب) *:")
            c_notes = st.text_input("ملاحظات خاصة بالعميل:")
            
        if st.form_submit_button("حفظ بيانات العميل", type="primary"):
            if c_name.strip() and c_phone.strip():
                st.session_state.memory_customers.append({
                    "customer_name": str(c_name.strip()),
                    "phone": str(c_phone.strip()),
                    "address": str(c_address.strip()),
                    "notes": str(c_notes.strip() if c_notes else "")
                })
                log_audit("إضافة عميل", f"تم تسجيل العميل الجديد {c_name}")
                st.success(f"تم تسجيل العميل ({c_name}) بنجاح في قاعدة البيانات!")
                st.rerun()
            else:
                st.warning("يرجى إدخال اسم العميل ورقم الهاتف على الأقل.")

    st.divider()
    st.subheader("📋 قائمة العملاء والديون المترتبة")
    if st.session_state.memory_customers:
        cust_display_data = []
        for cust in st.session_state.memory_customers:
            c_invs = [inv for inv in st.session_state.memory_invoices if inv['customer_name'] == cust['customer_name']]
            c_total_debt = sum(float(inv.get('remaining_amount', 0)) for inv in c_invs)
            cust_display_data.append({
                "اسم الزبون / المحل": cust['customer_name'],
                "رقم الهاتف": cust['phone'],
                "العنوان": cust['address'],
                "إجمالي الديون المترتبة (د.ع)": int(c_total_debt),
                "ملاحظات": cust['notes']
            })
        st.dataframe(pd.DataFrame(cust_display_data), use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلين حالياً.")

with tab5:
    st.subheader("💵 نظام سداد الديون وإصدار سندات القبض النقدية")
    debt_cust_list = [c["customer_name"] for c in st.session_state.memory_customers]

    if not debt_cust_list:
        st.info("لا توجد عملاء مسجلين لإدارة ديونهم.")
    else:
        selected_debt_customer = st.selectbox("اختر اسم العميل لتسديد الدين:", debt_cust_list, key="debt_pay_cust_select_pro")
        
        customer_invoices = [inv for inv in st.session_state.memory_invoices if inv['customer_name'] == selected_debt_customer]
        total_customer_debt = sum(float(inv.get('remaining_amount', 0)) for inv in customer_invoices)
        
        st.markdown(f"### 📌 الدين الكلي المتبقي على العميل (`{selected_debt_customer}`): **{int(total_customer_debt):,} د.ع**")
        
        if customer_invoices:
            with st.expander("📄 عرض فواتير ومشتريات هذا العميل"):
                for cinv in customer_invoices:
                    st.write(f"- **الفاتورة:** {cinv['invoice_code']} | **المجموع:** {int(cinv['total_price']):,} د.ع | **الواصل:** {int(cinv['paid_amount']):,} د.ع | **المتبقي الذمي:** `{int(cinv['remaining_amount']):,}` د.ع | **التاريخ:** {cinv['created_date']}")
        
        st.divider()
        with st.form("pay_debt_pro_form"):
            payment_input_str = st.text_input("أدخل المبلغ المسدد حالياً نقداً (د.ع):", "0")
            pay_submitted = st.form_submit_button("إتمام التسديد وتوليد سند القبض", type="primary")
            
            if pay_submitted:
                try:
                    payment_val = float(payment_input_str.strip() if payment_input_str.strip() else "0")
                    if payment_val < 0:
                        st.warning("يرجى إدخال مبلغ صحيح.")
                    elif payment_val > total_customer_debt:
                        st.error("❌ المبلغ المدخل أكبر من إجمالي الديون المطلوبة من العميل!")
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
                                    new_type = "🟢 تسديد نقدي تام (كاش)"
                                    remaining_payment -= curr_rem
                                else:
                                    new_paid = float(cinv['paid_amount']) + remaining_payment
                                    new_rem = curr_rem - remaining_payment
                                    new_type = "🔵 تسديد جزئي (أقساط)"
                                    remaining_payment = 0.0
                                
                                cinv['paid_amount'] = float(new_paid)
                                cinv['remaining_amount'] = float(new_rem)
                                cinv['payment_type'] = str(new_type)
                        
                        st.session_state.last_receipt = {
                            "customer_name": str(selected_debt_customer),
                            "amount": float(payment_val),
                            "date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                        }

                        log_audit("سداد ديون", f"تم تسديد مبلغ {payment_val:,} د.ع للعميل {selected_debt_customer}")
                        st.success(f"🎉 تم استلام وسداد مبلغ {payment_val:,.0f} دينار عراقي وتحديث حساب العميل بنجاح!")
                        st.rerun()
                except ValueError:
                    st.error("❌ يرجى إدخال رقم صحيح للمبلغ.")

        if st.session_state.get('last_receipt'):
            rec = st.session_state.last_receipt
            st.divider()
            st.markdown("### 🧾 سند القبض النقدي الرسمي الأخير:")
            with st.container(border=True):
                st.write(f"👤 **اسم العميل:** {rec['customer_name']}")
                st.write(f"💵 **المبلغ المستلم:** **{int(rec['amount']):,} د.ع**")
                st.write(f"📅 **وقت الاستلام:** {rec['date']}")
                st.info("💡 تم تسليم هذا السند كإثبات رسمي لقبض النقدية وإطفاء جزء أو كل الذمم.")
                
                html_rec_data = generate_html_receipt(rec)
                st.download_button(
                    label="🖨️ تحميل وطباعة سند القبض (HTML)",
                    data=html_rec_data,
                    file_name=f"receipt_{rec['customer_name']}.html",
                    mime="text/html"
                )

with tab6:
    st.subheader("🏭 إدارة الموردين وتفاصيل جهات التوريد")
    with st.form("add_supplier_pro_form", clear_on_submit=True):
        sup_name = st.text_input("اسم المورد / الشركة:")
        sup_phone = st.text_input("رقم هاتف المورد:")
        sup_notes = st.text_input("التخصص / نوع البضاعة الموردة:")
        if st.form_submit_button("إضافة المورد لقائمة التوريد"):
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
    st.subheader("🛒 نقطة البيع الذكية (POS) وإتمام الفاتورة")
    
    if st.session_state.cart:
        total_cart_price = 0.0
        for idx, c_item in enumerate(st.session_state.cart):
            cols_cart = st.columns([3, 2, 2, 1])
            with cols_cart[0]:
                st.write(f"**{c_item['product_name']}** ({c_item['color']} / {c_item['size']})")
            with cols_cart[1]:
                new_q = st.number_input(f"الكمية", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_q_pro_{c_item['id']}")
                c_item['qty'] = new_q
            with cols_cart[2]:
                item_total = float(c_item['sell_price']) * float(c_item['qty'])
                total_cart_price += item_total
                st.write(f"المجموع: **{int(item_total):,}** د.ع")
            with cols_cart[3]:
                if st.button("❌ حذف", key=f"del_cart_pro_{c_item['id']}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                
        st.divider()
        st.markdown(f"### 💵 المجموع الكلي المطلوب سداده: **{int(total_cart_price):,} د.ع**")
        
        cust_names_list = [c["customer_name"] for c in st.session_state.memory_customers]
            
        if not cust_names_list:
            st.warning("⚠️ تنبيه: يرجى إضافة عميل من تبويب (إدارة العملاء والديون) أولاً لتتمكن من إصدار الفاتورة باسمه!")
            selected_customer_name = ""
        else:
            selected_customer_name = st.selectbox("اختر اسم العميل / المحل المرتبط بالفاتورة:", cust_names_list)
        
        st.write("---")
        st.markdown("#### 💰 خيارات الدفع والتقسيط:")
        paid_input_str = st.text_input("المبلغ المدفوع حالياً من قبل العميل (د.ع - اكتب 0 إذا كانت الفاتورة آجلة بالكامل):", value="0")
        
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

        st.info(f"💡 **تحليل الدفع:** {auto_pay_type} | الواصل بالصندوق: **{int(paid_amount):,} د.ع** | المتبقي (الدين الذمي): **{int(remaining_amount):,} د.ع**")

        if st.button("💾 إتمام البيع، خصم المخزن، وحفظ الفاتورة رسمياً", type="primary"):
            if not selected_customer_name:
                st.error("❌ خطأ: يرجى اختيار عميل مسجل من القائمة لإتمام الفاتورة.")
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
                    inv_code = f"PRO-INV-{inv_id:03d}"
                    
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
                    
                    log_audit("إتمام بيع", f"فاتورة جديدة {inv_code} للعميل {selected_customer_name}")
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع وحفظ الفاتورة وتحديث المخزن بنجاح تام!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ أثناء حفظ الفاتورة: {e}")
    else:
        st.info("🛒 سلة المبيعات فارغة حالياً. توجه إلى قسم المخزن لإضافة مواد للسلة.")

with tab8:
    st.subheader("📄 سجل الفواتير والمشاركة الذكية عبر الواتساب")
    invoices_list = st.session_state.memory_invoices

    if invoices_list:
        for inv in invoices_list:
            with st.expander(f"📄 فاتورة: {inv['invoice_code']} | الزبون: {inv['customer_name']} | المجموع: {int(inv['total_price']):,} د.ع"):
                st.write(f"📅 **تاريخ الإصدار:** {inv['created_date']}")
                st.write(f"🛍️ **المنتجات والمواد:** {inv['products_text']}")
                st.write(f"💵 **المبلغ الكلي:** {int(inv['total_price']):,} د.ع | **الواصل:** {int(inv['paid_amount']):,} د.ع | **المتبقي الذمي:** `{int(inv['remaining_amount']):,}` د.ع")
                st.write(f"📌 **حالة الدفع:** {inv['payment_type']}")

                html_inv = generate_html_invoice(inv)
                st.download_button(
                    label="📥 تحميل الفاتورة الرسمية (HTML)",
                    data=html_inv,
                    file_name=f"invoice_{inv['invoice_code']}.html",
                    mime="text/html",
                    key=f"dl_inv_pro_{inv['id']}"
                )

                cust_ph = ""
                for c in st.session_state.memory_customers:
                    if c["customer_name"] == inv['customer_name']:
                        cust_ph = c["phone"]
                        break

                if cust_ph:
                    wa_msg = f"مرحباً أستاذ {inv['customer_name']}\nإليك تفاصيل فاتورتك الرسمية برقم {inv['invoice_code']}:\nالمبلغ الإجمالي: {int(inv['total_price']):,} د.ع\nالواصل: {int(inv['paid_amount']):,} د.ع\nالمتبقي الذمي: {int(inv['remaining_amount']):,} د.ع\nشكراً لتعاملكم مع نظام ياسر ويب برو!"
                    encoded_msg = urllib.parse.quote(wa_msg)
                    wa_url = f"https://wa.me/{cust_ph}?text={encoded_msg}"
                    st.markdown(f"📱 [إرسال الفاتورة للعميل مباشرة عبر واتساب]({wa_url})", unsafe_allow_html=True)
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

with tab9:
    st.subheader("💰 صندوق الوردية وتسجيل المصروفات النقدية")
    
    with st.form("add_expense_pro_form", clear_on_submit=True):
        exp_title = st.text_input("بيان المصروف (مثال: أجور نقل، صيانة، إيجار، سحب شخصي):")
        exp_amount_str = st.text_input("مبلغ المصروف (د.ع):", "0")
        if st.form_submit_button("تسجيل المصروف بالصندوق", type="primary"):
            if exp_title.strip():
                try:
                    exp_val = float(exp_amount_str.strip())
                    st.session_state.expenses_list.insert(0, {
                        "البيان": str(exp_title.strip()),
                        "المبلغ": float(exp_val),
                        "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    log_audit("تسجيل مصروف", f"تم تسجيل مصروف {exp_title} بقيمة {exp_val}")
                    st.success("تم تسجيل المصروف بالصندوق بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("يرجى إدخال مبلغ صحيح.")
            else:
                st.warning("يرجى كتابة بيان المصروف.")

    st.divider()
    total_sales_cash = sum(float(inv.get('paid_amount', 0)) for inv in st.session_state.memory_invoices)
    total_expenses = sum(float(ex.get('المبلغ', 0)) for ex in st.session_state.expenses_list)
    net_box = total_sales_cash - total_expenses

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.metric("إجمالي الواصل النقدي بالصندوق", f"{int(total_sales_cash):,} د.ع")
    with col_b2:
        st.metric("إجمالي المصروفات المسجلة", f"{int(total_expenses):,} د.ع")
    with col_b3:
        st.metric("صافي رصيد الصندوق الحالي", f"{int(net_box):,} د.ع")

    if st.session_state.expenses_list:
        st.subheader("📋 سجل المصروفات التفصيلي")
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)

with tab10:
    st.subheader("📊 تقارير الأرباح وتحليلات الذكاء الاصطناعي")
    invoices_report = st.session_state.memory_invoices
    
    total_revenue = sum(float(inv['total_price']) for inv in invoices_report)
    total_cost = sum(float(inv.get('cost_price', 0)) for inv in invoices_report)
    total_net_profit = total_revenue - total_cost
    total_debts = sum(float(inv.get('remaining_amount', 0)) for inv in invoices_report)

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric("إجمالي المبيعات العامة", f"{int(total_revenue):,} د.ع")
    with col_r2:
        st.metric("صافي أرباح البضائع المباعة", f"{int(total_net_profit):,} د.ع")
    with col_r3:
        st.metric("إجمالي الديون المعلقة بذمة العملاء", f"{int(total_debts):,} د.ع")

    st.divider()
    st.markdown("### 🤖 تحليلات المساعد الذكي لنظام ياسر ويب برو:")
    if total_revenue > 0:
        st.success(f"✨ أداء المحل ممتاز! نسبة الربح الإجمالي تشير إلى استقرار مالي جيد مع وجود ديون معلقة بقيمة `{int(total_debts):,}` د.ع تستوجب المتابعة والتحصيل عبر قسم سندات القبض.")
    else:
        st.info("ℹ️ ابدأ بإتمام عمليات بيع لتتمكن من رؤية تحليلات الأداء والرسوم البيانية المتقدمة.")

    if invoices_report:
        df_inv_report = pd.DataFrame(invoices_report)
        st.bar_chart(df_inv_report, x="invoice_code", y="total_price")
    else:
        st.info("لا توجد بيانات كافية للرسم البياني حالياً.")

with tab11:
    st.subheader("📜 سجل النشاطات والعمليات الرقابي (Audit Trail)")
    if st.session_state.audit_logs:
        df_audit = pd.DataFrame(st.session_state.audit_logs)
        st.dataframe(df_audit, use_container_width=True)
    else:
        st.info("لا توجد نشاطات مسجلة حتى الآن.")

with tab12:
    st.subheader("📖 الدليل الشامل ومعاينة طباعة النظام")
    st.markdown("""
    ### دليل الاستخدام السريع لنظام **Yasser Web Pro** الشامل 🛍️
    - **مفهوم النظام:** تم تصميم هذه النسخة الاحترافية لتلبي كافة متطلبات المحلات التجارية، الأجهزة، والشركات مع نظام أمان، تتبع كامل للديون، وسندات قبض فورية.
    - **أبرز المميزات المدمجة:**
      1. واجهة متجاوبة بالكامل (`RTL`) تتوافق مع جميع الهواتف واللابتوبات.
      2. جرد تلقائي للمخزن مع تحذيرات ذكية عند نفاد الكميات.
      3. نظام نقاط بيع (POS) يخصم الكميات تلقائياً ويحتسب الأرباح وصافي الدخل.
      4. إصدار فواتير وسندات قبض احترافية بصيغة `HTML` قابلة للطباعة والإرسال الفوري عبر واتساب.
      5. نسخ احتياطي فوري وسهل لكافة بيانات المحل بضغطة زر واحدة.
    """)
