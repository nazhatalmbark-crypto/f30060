import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import arabic_reshaper
from bidi.algorithm import get_display
import urllib.parse

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - النظام الشامل لإدارة المحلات", page_icon="🛍️", layout="wide")

# تسجيل خط عربي مدعوم
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

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "customer_list" not in st.session_state:
    st.session_state.customer_list = []

if "suppliers_list" not in st.session_state:
    st.session_state.suppliers_list = []

if "invoices_list" not in st.session_state:
    st.session_state.invoices_list = []

if "cart" not in st.session_state:
    st.session_state.cart = []

if "expenses_list" not in st.session_state:
    st.session_state.expenses_list = []

if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

# دالة توليد ملف الـ PDF بالفاتورة
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

st.title("🛍️ نظام Yasser Web الشامل لإدارة المبيعات والمخزون")

if not st.session_state.logged_in_user:
    st.subheader("🔐 بوابة الدخول لحسابات المحلات والنظام")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 تسجيل الدخول", "✨ إنشاء حساب جديد"])
    
    with auth_tab1:
        with st.form("login_form"):
            login_user = st.text_input("اسم المستخدم أو اسم المحل:")
            login_submitted = st.form_submit_button("تسجيل الدخول", type="primary")
            
            if login_submitted:
                if login_user.strip():
                    try:
                        res = supabase.table("users").select("*").eq("username", login_user.strip()).execute()
                        if res.data:
                            user_info = res.data[0]
                            st.session_state.logged_in_user = user_info["username"]
                            st.session_state.is_vip = bool(user_info.get("is_paid", False))
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
            signup_submitted = st.form_submit_button("إنشاء الحساب الآن", type="primary")
            
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
                            st.session_state.logged_in_user = new_user.strip()
                            st.session_state.is_vip = False
                            st.success("🎉 تم إنشاء الحساب وتسجيل الدخول بنجاح!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"خطأ في إنشاء الحساب بقاعدة البيانات: {e}")
                else:
                    st.warning("يرجى كتابة اسم المستخدم الجديد.")
    st.stop()

username = st.session_state.logged_in_user

st.sidebar.title("⚙️ إعدادات الحساب")
st.sidebar.write(f"👤 المستخدم: **{username}**")

cart_count_badge = sum(item['qty'] for item in st.session_state.cart)
st.sidebar.info(f"🛒 المواد الحالية بالسلة: **{cart_count_badge}** قطعة")

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
            st.sidebar.success("تم تفعيل النسخة المدفوعة (VIP) بنجاح! 🎉")
            st.rerun()
        else:
            st.sidebar.error("كود التفعيل غير صحيح!")
else:
    st.sidebar.success("🌟 النسخة المدفوعة (VIP) مفعلة بالكامل")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in_user = None
    st.session_state.is_vip = False
    st.session_state.cart = []
    st.rerun()

st.divider()

# التبويبات الشاملة لكافة أنواع المحلات
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "➕ إضافة مادة جديدة", 
    "📦 جرد المخزن", 
    "👥 إدارة العملاء والديون", 
    "🏭 إدارة الموردين",
    "🛒 إتمام البيع والفواتير", 
    "📄 سجل الفواتير وواتساب", 
    "💰 صندوق الوردية والمصاريف", 
    "📊 تقارير الأرباح",
    "📖 دليل الاستخدام الشامل"
])

with tab1:
    st.subheader("➕ واجهة إضافة مادة أو بضاعة جديدة للمخزن")
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
                            "username": username,
                            "product_name": p_name.strip(),
                            "color": p_color.strip() if p_color else "عام",
                            "size": p_size.strip() if p_size else "عام",
                            "buy_price": p_buy,
                            "sell_price": p_sell,
                            "quantity": p_qty,
                            "barcode": p_barcode.strip() if p_barcode else "بدون"
                        }).execute()
                        st.success(f"تمت إضافة المادة ({p_name}) بنجاح!")
                        st.rerun()
                    except ValueError:
                        st.error("❌ خطأ: يرجى إدخال أرقام صحيحة حصراً.")
                    except Exception as e:
                        st.error(f"❌ خطأ في حفظ المنتج بقاعدة البيانات: {e}")
                else:
                    st.warning("يرجى كتابة اسم المادة على الأقل.")

with tab2:
    st.subheader("📦 جرد المخزن الشامل (بحث بالاسم، الباركود، الألوان والقياسات)")
    
    try:
        res_all_p = supabase.table("products").select("*").eq("username", username).execute()
        all_products = res_all_p.data if res_all_p.data else []
    except:
        all_products = []

    low_stock_items = [p for p in all_products if p['quantity'] <= 1]
    if low_stock_items:
        low_names = " ، ".join([f"**{i['product_name']}** ({i.get('color','')} - {i.get('size','')})" for i in low_stock_items])
        st.error(f"🚨 **تنبيه نفاذ المخزون:** المواد التالية وشيكة النفاذ أو نفدت: {low_names}")

    if st.session_state.cart:
        total_items_in_cart = sum(i['qty'] for i in st.session_state.cart)
        total_price_preview = sum(i['sell_price'] * i['qty'] for i in st.session_state.cart)
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
                    st.markdown(f"🎨 **اللون / المواصفات:** `{item.get('color', 'عام')}` | 📏 **القياس / السعة:** `{item.get('size', 'عام')}`")
                    st.markdown(f"🏷️ **الباركود:** `{item.get('barcode', 'بدون')}`")
                    st.markdown(f"💰 **سعر البيع:** `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🔢 **الكمية المتوفرة:** `{int(item['quantity'])}` قطعة")
                    
                    profit_per_unit = int(item['sell_price'] - item['buy_price'])
                    if profit_per_unit < 0:
                        st.error(f"📉 ربح القطعة: {profit_per_unit:,} د.ع (خسارة)")
                    else:
                        st.success(f"📈 ربح القطعة: {profit_per_unit:,} د.ع")
                    
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
                    "اسم العميل": c_name, 
                    "رقم الهاتف": c_phone, 
                    "المحافظة": c_gov,
                    "العنوان": c_address if c_address else "غير محدد",
                    "ملاحظات": c_notes if c_notes else "لا يوجد",
                    "تاريخ التسجيل": datetime.now().strftime('%Y-%m-%d')
                })
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
                    "اسم المورد": sup_name.strip(),
                    "رقم الهاتف": sup_phone.strip() if sup_phone else "غير محدد",
                    "التخصص": sup_notes.strip() if sup_notes else "عام",
                    "تاريخ الإضافة": datetime.now().strftime('%Y-%m-%d')
                })
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
                        "رقم الفاتورة": inv_code,
                        "الزبون": cust_name,
                        "المنتجات": " , ".join(prod_names_str),
                        "المبلغ الكلي": int(total_cart_price),
                        "تكلفتها": int(total_buy_cost_of_invoice),
                        "الواصل": int(paid_amount),
                        "المتبقي (الدين)": int(remaining_amount),
                        "نوع الدفع": pay_type,
                        "التاريخ": datetime.now().strftime('%Y-%m-%d %H:%M')
                    })
                    
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع بنجاح، وتحديث المخزن، وتسجيل الفاتورة في الذمم!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ أثناء إتمام البيع: {e}")
    else:
        st.info("🛒 السلة فارغة حالياً.")

with tab6:
    st.subheader("📄 سجل الفواتير، تحميل PDF، ومطالبة الديون عبر واتساب")
    
    if st.session_state.invoices_list:
        if st.button("🗑️ مسح سجل الفواتير القديم"):
            st.session_state.invoices_list = []
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
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px 12px; border-radius:5px; cursor:pointer; font-weight:bold;">💬 إرسال الفاتورة والمطالبة واتساب</button></a>', unsafe_allow_html=True)
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

with tab7:
    st.subheader("💰 صندوق الوردية والمصاريف اليومية")
    
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
                            "البيان": exp_title.strip(),
                            "المبلغ": int(exp_amt),
                            "الوقت": datetime.now().strftime('%Y-%m-%d %H:%M')
                        })
                        st.success("تم تسجيل المصروف بنجاح!")
                        st.rerun()
                    except ValueError:
                        st.error("يرجى إدخال مبلغ صحيح.")
                else:
                    st.warning("يرجى كتابة بيان المصروف.")

    with col_exp2:
        st.write("### 📊 ملخص سيولة صندوق الوردية")
        total_cash_in = sum(inv['الواصل'] for inv in st.session_state.invoices_list)
        total_expenses = sum(e['المبلغ'] for e in st.session_state.expenses_list)
        net_box = total_cash_in - total_expenses

        st.metric(label="إجمالي النقدية الداخلة (المقبوضات)", value=f"{int(total_cash_in):,} د.ع")
        st.metric(label="إجمالي المصاريف والسحوبات", value=f"{int(total_expenses):,} د.ع")
        st.metric(label="الصافي الفعلي بالصندوق حالياً", value=f"{int(net_box):,} د.ع")

    st.divider()
    st.write("### 📋 سجل المصاريف")
    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)
        if st.button("🗑️ تصفية ومسح سجل المصاريف"):
            st.session_state.expenses_list = []
            st.rerun()
    else:
        st.info("لا توجد مصاريف مسجلة للوردية الحالية.")

with tab8:
    st.subheader("📊 تقارير الأرباح الصافية وحركة المبيعات العامة")
    
    if st.session_state.invoices_list:
        total_sales_all = sum(inv['المبلغ الكلي'] for inv in st.session_state.invoices_list)
        total_received_all = sum(inv['الواصل'] for inv in st.session_state.invoices_list)
        total_debts_all = sum(inv['المتبقي (الدين)'] for inv in st.session_state.invoices_list)
        
        total_cost_of_goods = sum(inv.get('تكلفتها', 0) for inv in st.session_state.invoices_list)
        gross_profit = total_sales_all - total_cost_of_goods
        total_expenses = sum(e['المبلغ'] for e in st.session_state.expenses_list)
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
        st.write("### 📈 جدول حركة الفواتير التفصيلي")
        df_invoices = pd.DataFrame(st.session_state.invoices_list)
        st.dataframe(df_invoices, use_container_width=True)
    else:
        st.info("لا توجد بيانات مبيعات كافية لعرض التقارير حالياً.")

with tab9:
    st.subheader("📖 دليل الاستخدام التفصيلي والمرتب لكل تبويب في نظام Yasser Web")
    
    st.markdown("""
    أهلاً بك يا غالي. تم تصميم هذا الدليل ليشرح لك **كل تبويب وكل ميزة بالتفصيل الممل** لتعمل على النظام بكل ثقة واحترافية:

    ---

    ### 1️⃣ تبويب (➕ إضافة مادة جديدة)
    * **الغرض منه:** إدخال البضائع أو الأجهزة أو المواد الجديدة إلى المخزن.
    * **طريقة الاستخدام:**
      * أدخل **اسم المادة/المنتج** (مثلاً: آيفون 13، قميص رجالي، سماعة بلوتوث).
      * حدد **اللون أو المواصفات الإضافية** (اختياري، مثل: أسود، أبيض، أو 128GB).
      * حدد **القياس أو السعة أو الحجم** (اختياري، مثل: Large، XL، أو عام).
      * اكتب **سعر الشراء** (تكلفة المادة عليك) و**سعر البيع** (السعر للزبون).
      * حدد **الكمية المتوفرة** ورمز **الباركود** (إن وجد).
      * اضغط على **"حفظ المادة في المخزن"** لتنضاف فوراً لقاعدة البيانات.

    ---

    ### 2️⃣ تبويب (📦 جرد المخزن)
    * **الغرض منه:** استعراض جميع البضائع المتوفرة، البحث السريع، ومعرفة النواقص.
    * **طريقة الاستخدام:**
      * يمكنك البحث السريع عن أي منتج كتابةً بالاسم أو عبر ماسح الباركود.
      * يعرض لك كارد لكل منتج يوضح السعر، الكمية المتبقية، وربح القطعة الواحدة.
      * يظهر تنبيه تلقائي باللون الأحمر إذا كانت المادة وشيكة النفاذ (الكمية 1 أو أقل).
      * يحتوي كل منتج على زر **"إضافة إلى السلة"** لنقله مباشرة إلى قائمة البيع.

    ---

    ### 3️⃣ تبويب (👥 إدارة العملاء والديون)
    * **الغرض منه:** حفظ معلومات الزبائن ومتابعة ذممهم المالية ومحافظاتهم.
    * **طريقة الاستخدام:**
      * أدخل اسم العميل، رقم الهاتف، اختر المحافظة العراقية، والعنوان التفصيلي.
      * اضغط **"تسجيل بيانات العميل"** لحفظه في القائمة.
      * يتيح لك الجدول الأسفل البحث عن أي عميل ومعرفة تفاصيله بسرعة.

    ---

    ### 4️⃣ تبويب (🏭 إدارة الموردين)
    * **الغرض منه:** تسجيل أسماء الشركات ووكلاء الجملة الذين تجهز منهم البضاعة.
    * **طريقة الاستخدام:**
      * أدخل اسم المورد، رقم هاتفه، ونوع التخصص أو البضاعة الموردة.
      * يساعدك في الاحتفاظ بسجل كامل لجهات التجهيز الخاصة بمحلك.

    ---

    ### 5️⃣ تبويب (🛒 إتمام البيع والفواتير)
    * **الغرض منه:** تجميع المواد التي اختارها الزبون في سلة المبيعات وإصدار الفاتورة.
    * **طريقة الاستخدام:**
      * استعرض المواد المضافة للسلة، وعدّل الكميات حسب رغبة الزبون.
      * اختر اسم الزبون المسجل مسبقاً من القائمة المنسدلة (إلزامي).
      * حدد **طريقة الدفع**: (كاش نقداً بالكامل، آجل بالكامل كدين، أو دفعة جزئية مع كتابة المبلغ الواصل).
      * اضغط **"إتمام البيع، خصم المخزن، وحفظ الفاتورة"** ليقوم النظام بخصم الكمية من المخزن وتسجيل الفاتورة في السجل.

    ---

    ### 6️⃣ تبويب (📄 سجل الفواتير وواتساب)
    * **الغرض منه:** متابعة الفواتير السابقة، تحميلها بصيغة PDF، أو إرسالها للزبون عبر واتساب.
    * **طريقة الاستخدام:**
      * استعرض كافة الفواتير المصدرة مع تفاصيل المبالغ والديون المتبقية.
      * اضغط على **"تحميل فاتورة PDF"** لتنزيل فاتورة رسمية وجاهزة للطباعة.
      * اضغط على زر **"إرسال الفاتورة والمطالبة واتساب"** ليتم فتح محادثة الواتساب مع رقم الزبون متضمنةً نص الفاتورة والمبلغ المتبقي بذمته بضغطة زر واحدة!

    ---

    ### 7️⃣ تبويب (💰 صندوق الوردية والمصاريف)
    * **الغرض منه:** تتبع حركة النقدية اليومية، تسجيل المصاريف وسحوبات الصندوق.
    * **طريقة الاستخدام:**
      * أدخل بيان المصروف (مثل: إيجار، خط إنترنت، سحب شخصي) مع المبلغ.
      * يعرض لك النظام ملخصاً حياً ودقيقاً لـ: إجمالي النقدية الداخلة، إجمالي المصاريف، و**الصافي الفعلي بالصندوق حالياً**.

    ---

    ### 8️⃣ تبويب (📊 تقارير الأرباح)
    * **الغرض منه:** معرفة الأداء المالي العام للمحل وصافي الأرباح الحقيقية.
    * **طريقة الاستخدام:**
      * يعرض مؤشرات عليا لإجمالي المبيعات، المبالغ الواصلة، الديون المعلقة.
      * يحسب **صافي الربح الحقيقي** بعد خصم تكلفة شراء المواد والمصاريف المسجلة.
      * يوضح جدولاً تفصيلياً لكل حركة البيع داخل المحل.

    ---

    💡 **هذا الدليل مصمم ليكون مرجعك الدائم داخل النظام لإدارة محلك بكل احترافية ويسر!**
    """)
