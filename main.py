import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import json
import qrcode
import arabic_reshaper
from bidi.algorithm import get_display
import urllib.parse
import barcode
from barcode.writer import ImageWriter

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - النظام الشامل لإدارة المحلات", page_icon="🛍️", layout="wide")

try:
    pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
    ARABIC_FONT = 'Amiri'
except:
    ARABIC_FONT = 'Helvetica'

def format_arabic(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

# **إدارة اللغات (العربية والإنجليزية)**
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
            "📖 دليل الاستخدام الشامل"
        ]
    },
    "English": {
        "title": "🛍️ Yasser Web - Comprehensive Sales & Inventory Management System",
        "login_title": "🔐 Login Portal for Store Accounts & System",
        "login_tab": "🔑 Login",
        "signup_tab": "✨ Create New Account",
        "username_label": "Username or Store Name:",
        "login_btn": "Login",
        "signup_btn": "Create Account Now",
        "settings": "⚙️ Account Settings & Backup",
        "lang_select": "🌐 Language / اللغة",
        "role_label": "👤 Role:",
        "cart_badge": "🛒 Items currently in cart:",
        "backup_title": "🔄 Instant Data Backup",
        "backup_download": "📥 Download Backup (JSON)",
        "backup_upload": "📂 Restore Data from File",
        "logout": "Logout",
        "tabs": [
            "➕ Add New Product", 
            "📦 Inventory & Barcode", 
            "👥 Customers & Debts", 
            "🏭 Suppliers",
            "🛒 Checkout & Invoices", 
            "📄 Invoice History & WhatsApp", 
            "💰 Shift Box & Expenses", 
            "📊 Charts & Reports",
            "📜 Audit Trail / Logs",
            "📖 Comprehensive User Guide"
        ]
    }
}

t = lang_dict[st.session_state.lang]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "user_role" not in st.session_state:
    st.session_state.user_role = "مشرف النظام"

# تهيئة آمنة تمنع تحول القوائم إلى DataFrame بالخطأ
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

def generate_pdf_invoice(inv):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "YASSER WEB - فاتورة مبيعات رسمية")
    
    p.setFont("Helvetica", 10)
    p.drawString(width - 200, height - 50, f"Date: {inv['التاريخ']}")
    
    p.setStrokeColorRGB(0.2, 0.2, 0.2)
    p.setLineWidth(1)
    p.line(50, height - 65, width - 50, height - 65)
    
    p.setFont(ARABIC_FONT, 12)
    p.drawString(50, height - 95, format_arabic(f"رقم الفاتورة: {inv['رقم الفاتورة']}"))
    p.drawString(50, height - 120, format_arabic(f"اسم الزبون: {inv['الزبون']}"))
    p.drawString(50, height - 145, format_arabic(f"نوع الدفع: {inv['نوع الدفع']}"))
    
    p.line(50, height - 165, width - 50, height - 165)
    p.drawString(50, height - 195, format_arabic("تفاصيل المنتجات والمواد المباعة:"))
    
    text_y = height - 225
    items_list_str = inv['المنتجات'].split(" , ")
    for prod_line in items_list_str:
        p.drawString(70, text_y, format_arabic(f">> {prod_line}"))
        text_y -= 25
        
    text_y -= 10
    p.line(50, text_y, width - 50, text_y)
    
    text_y -= 35
    p.drawString(50, text_y, format_arabic(f"المبلغ الكلي: {inv['المبلغ الكلي']:,} دينار عراقي"))
    text_y -= 25
    p.drawString(50, text_y, format_arabic(f"المبلغ الواصل: {inv['الواصل']:,} دينار عراقي"))
    text_y -= 25
    p.drawString(50, text_y, format_arabic(f"المتبقي (الدين): {inv['المتبقي (الدين)']:,} دينار عراقي"))
    
    text_y -= 45
    p.setLineWidth(0.5)
    p.line(50, text_y, width - 50, text_y)
    p.drawCentredString(width / 2.0, text_y - 35, format_arabic("شكراً لتعاملكم مع نظام Yasser Web لإدارة المبيعات والمخزن!"))
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

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

st.sidebar.divider()
st.sidebar.subheader(t["backup_title"])

backup_data = {
    "username": str(username),
    "customers": list(st.session_state.customer_list),
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
            st.session_state.audit_logs = restored_data.get("audit_logs", [])
            log_audit("استعادة بيانات", "تم استعادة البيانات بنجاح من ملف نسخ احتياطي خارجي")
            st.sidebar.success("✅ تمت استعادة البيانات بنجاح!")
            st.rerun()
        else:
            st.sidebar.error("❌ ملف النسخة الاحتياطي غير صالح.")
    except Exception as e:
        st.sidebar.error(f"خطأ في استعادة الملف: {e}")

st.sidebar.divider()

if not st.session_state.is_vip:
    st.sidebar.warning("🔒 حالة النسخة: **مجانية (محدودة)**")
    vip_code = st.sidebar.text_input("أدخل كود النسخة المدفوعة (VIP):", type="password")
    if st.sidebar.button("تفعيل النسخة المدفوعة"):
        if vip_code.strip() == "YASSER2026":
            st.session_state.is_vip = True
            try:
                supabase.table("users").update({"is_paid": True}).eq("username", username).execute()
            except Exception:
                pass
            log_audit("تفعيل النسخة المدفوعة", "تم تفعيل النسخة المدفوعة VIP بنجاح")
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
        except Exception:
            current_count = 0
            
        if not st.session_state.is_vip and current_count >= 5:
            st.warning("⚠️ **تنبيه النسخة المجانية:** وصلت للحد الأقصى (5 منتجات). فعّل النسخة المدفوعة لإضافة منتجات بلا حدود!")
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

with tab2:
    st.subheader("📦 جرد المخزن الشامل مع ميزة توليد وطباعة الباركود والتنبيهات الذكية")
    
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
                    st.markdown(f"💰 **سعر البيع:** `{int(item['sell_price']):,}` د.ع")
                    
                    if item['quantity'] <= 2:
                        st.error(f"🔢 **الكمية المتوفرة:** `{int(item['quantity'])}` قطعة (مخزون منخفض!)")
                    else:
                        st.markdown(f"🔢 **الكمية المتوفرة:** `{int(item['quantity'])}` قطعة")
                    
                    profit_per_unit = int(item['sell_price'] - item['buy_price'])
                    if profit_per_unit < 0:
                        st.error(f"📉 ربح القطعة: {profit_per_unit:,} د.ع (خسارة)")
                    else:
                        st.success(f"📈 ربح القطعة: {profit_per_unit:,} د.ع")
                    
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

with tab3:
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

    st.divider()
    st.subheader("📋 سجل العملاء والذمم المالية المستحقة")
    if st.session_state.customer_list:
        search_cust = st.text_input("🔍 بحث عن عميل بالاسم أو رقم الهاتف:", "")
        filtered_cust = [c for c in st.session_state.customer_list if search_cust.lower() in c['اسم العميل'].lower() or search_cust in c['رقم الهاتف']]
        st.dataframe(pd.DataFrame(filtered_cust), use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلون حالياً.")

with tab4:
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
                
    st.divider()
    st.subheader("📋 قائمة الموردين المسجلين")
    if st.session_state.suppliers_list:
        st.dataframe(pd.DataFrame(st.session_state.suppliers_list), use_container_width=True)
    else:
        st.info("لا توجد جهات موردة مسجلة حالياً.")

with tab5:
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
                    
        st.divider()
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
                    
                    st.session_state.invoices_list.append({
                        "رقم الفاتورة": str(inv_code),
                        "الزبون": str(cust_name),
                        "المنتجات": str(" , ".join(prod_names_str)),
                        "المبلغ الكلي": int(total_cart_price),
                        "تكلفتها": int(total_buy_cost_of_invoice),
                        "الواصل": int(paid_amount),
                        "المتبقي (الدين)": int(remaining_amount),
                        "نوع الدفع": str(pay_type),
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

with tab6:
    st.subheader("📄 سجل الفواتير، تحميل PDF، ومطالبة الديون عبر واتساب و QR Code")
    
    if st.session_state.invoices_list:
        if st.button("🗑️ مسح سجل الفواتير القديم"):
            st.session_state.invoices_list = []
            log_audit("مسح سجل", "تم مسح سجل الفواتير بالكامل")
            st.success("تم مسح السجل بنجاح.")
            st.rerun()
            
        for inv in reversed(st.session_state.invoices_list):
            with st.container(border=True):
                col_inv1, col_inv2, col_inv3 = st.columns([2, 2, 2])
                with col_inv1:
                    st.markdown(f"#### {inv['رقم الفاتورة']} | {inv['نوع الدفع']}")
                    st.write(f"👤 **الزبون:** {inv['الزبون']}")
                with col_inv2:
                    st.write(f"📅 **التاريخ:** {inv['التاريخ']}")
                    st.write(f"🛒 **المواد:** {inv['المنتجات']}")
                with col_inv3:
                    st.write(f"💵 **المبلغ الكلي:** `{inv['المبلغ الكلي']:,}` د.ع")
                    st.write(f"📥 **الواصل:** `{inv['الواصل']:,}` د.ع")
                    if inv['المتبقي (الدين)'] > 0:
                        st.error(f"🔴 **المتبقي (دين):** `{inv['المتبقي (الدين)']:,}` د.ع")
                    else:
                        st.success(f"🟢 **المتبقي (دين):** 0 د.ع (مسدد بالكامل)")
                
                with st.expander("📱 عرض QR Code الفاتورة السريع"):
                    qr_text = f"Invoice: {inv['رقم الفاتورة']} | Cust: {inv['الزبون']} | Total: {inv['المبلغ الكلي']} IQD | Remaining: {inv['المتبقي (الدين)']} IQD"
                    img = qrcode.make(qr_text)
                    buf_qr = io.BytesIO()
                    img.save(buf_qr, format="PNG")
                    st.image(buf_qr.getvalue(), width=150, caption=f"رمز QR لفاتورة {inv['رقم الفاتورة']}")

                pdf_buffer = generate_pdf_invoice(inv)
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.download_button(
                        label=f"📥 تحميل فاتورة PDF ({inv['رقم الفاتورة']})",
                        data=pdf_buffer,
                        file_name=f"{inv['رقم الفاتورة']}_{inv['الزبون']}.pdf",
                        mime="application/pdf",
                        key=f"download_pdf_{inv['رقم الفاتورة']}"
                    )
                with col_btn2:
                    cust_phone_w = ""
                    for c_obj in st.session_state.customer_list:
                        if c_obj["اسم العميل"] == inv["الزبون"]:
                            cust_phone_w = c_obj["رقم الهاتف"]
                            break
                    
                    wa_msg = f"مرحباً {inv['الزبون']}، شكراً لتعاملكم معنا. تفاصيل فاتورتكم ({inv['رقم الفاتورة']}):\nالمواد: {inv['المنتجات']}\nالمبلغ الكلي: {inv['المبلغ الكلي']:,} د.ع\nالواصل: {inv['الواصل']:,} د.ع\nالمتبقي بذمتكم: {inv['المتبقي (الدين)']:,} د.ع"
                    encoded_msg = urllib.parse.quote(wa_msg)
                    wa_url = f"https://wa.me/{cust_phone_w}?text={encoded_msg}" if cust_phone_w else "https://wa.me/?text=" + encoded_msg
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px 12px; border-radius:5px; cursor:pointer; font-weight:bold;">💬 إرسال الفاتورة والمطالبة عبر الواتساب</button></a>', unsafe_allow_html=True)
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

with tab7:
    st.subheader("💰 إدارة المصروفات النثرية اليومية وصندوق الوردية وحساب صافي الربح")
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        with st.form("add_expense_form", clear_on_submit=True):
            st.write("### 💸 تسجيل مصروف أو سحب نقدي من الصندوق")
            exp_title = st.text_input("بيان المصروف (مثل: إيجار، إنترنت، سحب شخصي):")
            exp_amount_str = st.text_input("المبلغ (د.ع):", "0")
            if st.form_submit_button("تسجيل المصروف"):
                if exp_title.strip():
                    try:
                        exp_amt = float(exp_amount_str.strip())
                        st.session_state.expenses_list.append({
                            "البيان": str(exp_title.strip()),
                            "المبلغ": int(exp_amt),
                            "الوقت": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                        })
                        log_audit("تسجيل مصروف", f"تم تسجيل مصروف ({exp_title.strip()}) بمبلغ {int(exp_amt):,} د.ع")
                        st.success("تم تسجيل المصروف بنجاح!")
                        st.rerun()
                    except ValueError:
                        st.error("يرجى إدخال مبلغ صحيح.")
                else:
                    st.warning("يرجى كتابة بيان المصروف.")

    with col_exp2:
        st.write("### 📊 ملخص سيولة صندوق الوردية وصافي الربح")
        total_cash_in = sum(int(inv['الواصل']) for inv in st.session_state.invoices_list)
        total_expenses = sum(int(e['المبلغ']) for e in st.session_state.expenses_list)
        net_box = total_cash_in - total_expenses

        total_sales_all = sum(int(inv['المبلغ الكلي']) for inv in st.session_state.invoices_list)
        total_cost_of_goods = sum(int(inv.get('تكلفتها', 0)) for inv in st.session_state.invoices_list)
        gross_profit = total_sales_all - total_cost_of_goods
        net_profit = gross_profit - total_expenses

        st.metric(label="إجمالي النقدية الداخلة (المقبوضات)", value=f"{int(total_cash_in):,} د.ع")
        st.metric(label="إجمالي المصاريف والنثريات", value=f"{int(total_expenses):,} د.ع")
        st.metric(label="الصافي الفعلي بالصندوق حالياً", value=f"{int(net_box):,} د.ع")
        st.metric(label="صافي الربح الحقيقي 🌟", value=f"{int(net_profit):,} د.ع")

    st.divider()
    st.write("### 📋 سجل المصروفات النثرية")
    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)
        if st.button("🗑️ تصفية ومسح سجل المصاريف"):
            st.session_state.expenses_list = []
            log_audit("مسح المصاريف", "تم تفريغ سجل المصاريف النثرية")
            st.rerun()
    else:
        st.info("لا توجد مصاريف مسجلة للوردية الحالية.")

with tab8:
    st.subheader("📊 الرسوم البيانية التفاعلية وتقارير الأرباح الصافية")
    
    if st.session_state.invoices_list:
        total_sales_all = sum(int(inv['المبلغ الكلي']) for inv in st.session_state.invoices_list)
        total_received_all = sum(int(inv['الواصل']) for inv in st.session_state.invoices_list)
        total_debts_all = sum(int(inv['المتبقي (الدين)']) for inv in st.session_state.invoices_list)
        
        total_cost_of_goods = sum(int(inv.get('تكلفتها', 0)) for inv in st.session_state.invoices_list)
        gross_profit = total_sales_all - total_cost_of_goods
        total_expenses = sum(int(e['المبلغ']) for e in st.session_state.expenses_list)
        net_profit = gross_profit - total_expenses
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="إجمالي المبيعات", value=f"{int(total_sales_all):,} د.ع")
        with m2:
            st.metric(label="إجمالي المبالغ الواصلة", value=f"{int(total_received_all):,} د.ع")
        with m3:
            st.metric(label="إجمالي الديون المعلقة", value=f"{int(total_debts_all):,} د.ع")
        with m4:
            st.metric(label="صافي الربح الحقيقي 🌟", value=f"{int(net_profit):,} د.ع")
            
        st.divider()
        st.write("### 📈 الرسوم البيانية التحليلية لحركة المبيعات")
        chart_data = pd.DataFrame(
            [
                {
                    "الفاتورة": str(inv["رقم الفاتورة"]),
                    "المبلغ الكلي": int(inv["المبلغ الكلي"]),
                    "الواصل": int(inv["الواصل"]),
                    "الدين المتبقي": int(inv["المتبقي (الدين)"]),
                }
                for inv in st.session_state.invoices_list
            ]
        )
        if not chart_data.empty:
            chart_data.set_index("الفاتورة", inplace=True)
            st.bar_chart(chart_data)
        else:
            st.info("لا توجد بيانات كافية لعرض الرسوم البيانية.")
    else:
        st.info("لا توجد فواتير أو مبيعات مسجلة لعرض التقارير الإحصائية والرسوم البيانية.")

with tab9:
    st.subheader("📜 سجل نشاطات المستخدمين (Audit Trail / Logs)")
    st.write("تتبع كافة العمليات والنشاطات التي قام بها المستخدمون داخل النظام للرقابة والتدقيق:")
    
    # فحص آمن يمنع أي خطأ لتقييم الـ DataFrame كقيمة منطقية
    logs_data = st.session_state.audit_logs
    is_logs_empty = logs_data.empty if isinstance(logs_data, pd.DataFrame) else (not logs_data)
    
    if not is_logs_empty:
        if st.button("🗑️ مسح سجل النشاطات"):
            st.session_state.audit_logs = []
            st.success("تم مسح سجل النشاطات بنجاح.")
            st.rerun()
        st.dataframe(pd.DataFrame(logs_data), use_container_width=True)
    else:
        st.info("لا توجد نشاطات مسجلة حتى الآن.")

with tab10:
    st.subheader("📖 دليل الاستخدام الشامل لنظام Yasser Web")
    st.markdown("""
    مرحباً بك في **Yasser Web**، النظام المتكامل لإدارة المحلات التجارية والمخازن. فيما يلي أبرز الميزات الجديدة المضافة:

    * **👥 إدارة الصلاحيات:** إمكانية تحديد أدوار المستخدمين (مشرف النظام، كاشير، مسؤول مبيعات) لتقييد أو إتاحة الصلاحيات.
    * **🌐 دعم كامل للغتين:** إمكانية التبديل السريع بين اللغة العربية والإنجليزية من القائمة الجانبية بسهولة.
    * **🚨 تنبيهات المخزون (Low Stock Alerts):** نظام ذكي ينبهك فوراً عند قرب نفاد أي مادة أو منتج في المخزن.
    * **📜 سجل النشاطات (Audit Trail):** تتبع جميع العمليات التي يقوم بها المستخدمون في النظام بدقة لضمان الأمان والرقابة.
    * **💰 إدارة المصروفات النثرية وحساب صافي الربح:** متابعة دقيقة للمصاريف اليومية وسحوبات الوردية لحساب صافي الربح الفعلي بدقة.
    * **💬 ربط وتصدير الفواتير عبر الواتساب:** إرسال الفواتير والمطالبات المالية مباشرة للعملاء عبر روابط واتساب مخصصة.
    """)
