import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import urllib.request

# مكتبات تعديل وعكس الحروف العربية لتظهر مضبوطة في الـ PDF
import arabic_reshaper
from bidi.algorithm import get_display

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - إدارة المبيعات والمخزون", page_icon="📦", layout="wide")

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "customer_list" not in st.session_state:
    st.session_state.customer_list = []

if "invoices_list" not in st.session_state:
    st.session_state.invoices_list = []

if "cart" not in st.session_state:
    st.session_state.cart = []

if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

# دالة لتسجيل الخط العربي وتنزيله مؤقتاً
@st.cache_resource
def register_arabic_font():
    try:
        font_url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
        font_path = "Amiri-Regular.ttf"
        urllib.request.urlretrieve(font_url, font_path)
        pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
        return True
    except Exception:
        return False

font_registered = register_arabic_font()

# دالة سحرية لتعديل النص العربي
def fix_arabic(text):
    if not text:
        return ""
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception:
        return text

# دالة لتوليد ملف الـ PDF بالفاتورة باللغة العربية
def generate_pdf_invoice(inv):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    f_name = 'ArabicFont' if font_registered else 'Helvetica'
    
    p.setFont(f_name, 18)
    p.drawCentredString(width / 2.0, height - 50, fix_arabic("نظام ياسر وب - فاتورة مبيعات"))
    
    p.setFont(f_name, 12)
    p.drawString(width - 200, height - 90, fix_arabic(f"رقم الفاتورة: {inv['رقم الفاتورة']}"))
    p.drawString(width - 200, height - 115, fix_arabic(f"اسم الزبون: {inv['الزبون']}"))
    p.drawString(width - 200, height - 140, fix_arabic(f"التاريخ: {inv['التاريخ']}"))
    p.drawString(width - 200, height - 165, fix_arabic(f"نوع الدفع: {inv['نوع الدفع']}"))
    
    p.line(50, height - 180, width - 50, height - 180)
    
    p.setFont(f_name, 13)
    p.drawString(width - 220, height - 210, fix_arabic("المنتجات والمواد المباعة:"))
    
    p.setFont(f_name, 11)
    text_y = height - 235
    items_list_str = inv['المنتجات'].split(" , ")
    for prod_line in items_list_str:
        p.drawString(width - 240, text_y, fix_arabic(f"- {prod_line}"))
        text_y -= 25
    
    text_y -= 15
    p.line(50, text_y, width - 50, text_y)
    
    text_y -= 30
    p.setFont(f_name, 12)
    p.drawString(width - 250, text_y, fix_arabic(f"المبلغ الكلي: {inv['المبلغ الكلي']:,} د.ع"))
    
    text_y -= 25
    p.drawString(width - 250, text_y, fix_arabic(f"المبلغ الواصل (المدفوع): {inv['الواصل']:,} د.ع"))
    
    text_y -= 25
    p.drawString(width - 250, text_y, fix_arabic(f"المتبقي (الدين): {inv['المتبقي (الدين)']:,} د.ع"))
    
    text_y -= 35
    p.line(50, text_y, width - 50, text_y)
    
    p.setFont(f_name, 10)
    p.drawCentredString(width / 2.0, text_y - 30, fix_arabic("شكراً لتعاملكم مع نظام Yasser Web - أهلاً وسهلاً بكم!"))
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

st.title("🛍️ نظام Yasser Web المتكامل لإدارة المبيعات والمخزون")

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
                            st.error("❌ اسم المستخدم غير موجود، يرجى إنشاء حساب جديد من التبويب المجاور.")
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
            st.sidebar.error("كود التفعيل غير صحيح! الكود الصحيح هو: YASSER2026")
else:
    st.sidebar.success("🌟 النسخة المدفوعة (VIP) مفعلة بالكامل")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in_user = None
    st.session_state.is_vip = False
    st.session_state.cart = []
    st.rerun()

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "➕ إضافة مادة جديدة", 
    "📦 عرض المخزن وسلة المبيعات", 
    "👥 إدارة العملاء", 
    "🛒 إتمام البيع والفواتير", 
    "📄 سجل الفواتير", 
    "📊 تقارير الأرباح"
])

with tab1:
    st.subheader("➕ واجهة إضافة مادة جديدة للمخزن")
    try:
        res_prod_count = supabase.table("products").select("id").eq("username", username).execute()
        current_count = len(res_prod_count.data) if res_prod_count.data else 0
    except Exception:
        current_count = 0
    
    if not st.session_state.is_vip and current_count >= 5:
        st.warning("⚠️ **تنبيه النسخة المجانية:** وصلت للحد الأقصى (5 منتجات). فعّل النسخة المدفوعة باستخدام كود (`YASSER2026`) من القائمة الجانبية لإضافة منتجات بلا حدود!")
    else:
        with st.form("add_product_clean_form", clear_on_submit=True):
            p_name = st.text_input("اسم القطعة / المنتج:")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                p_buy_str = st.text_input("سعر الشراء (د.ع):", "0")
            with c2:
                p_sell_str = st.text_input("سعر البيع (د.ع):", "0")
            with c3:
                p_qty_str = st.text_input("الكمية بالمخزن:", "1")
            
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
                            "buy_price": p_buy,
                            "sell_price": p_sell,
                            "quantity": p_qty
                        }).execute()
                        st.success(f"تمت إضافة المادة ({p_name}) بنجاح!")
                        st.rerun()
                    except ValueError:
                        st.error("❌ خطأ: يرجى إدخال أرقام صحيحة حصراً.")
                    except Exception as e:
                        st.error(f"❌ خطأ في حفظ المنتج بقاعدة البيانات: {e}")
                else:
                    st.warning("يرجى كتابة اسم المنتج أولاً.")

with tab2:
    st.subheader("🧱 عرض بضائع المحل")
    try:
        res_prod = supabase.table("products").select("*").eq("username", username).execute()
    except Exception:
        res_prod = None
    
    if res_prod and res_prod.data:
        cols = st.columns(3)
        for idx, item in enumerate(res_prod.data):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### 📦 {item['product_name']}")
                    st.markdown(f"💰 **سعر البيع:** `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🏷️ **سعر الشراء:** `{int(item['buy_price']):,}` د.ع")
                    st.markdown(f"🔢 **الكمية المتوفرة:** `{int(item['quantity'])}` قطعة")
                    
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
                                    "sell_price": item["sell_price"],
                                    "buy_price": item["buy_price"],
                                    "max_qty": item["quantity"],
                                    "qty": 1
                                })
                            st.toast(f"✅ تمت إضافة ({item['product_name']}) إلى السلة بنجاح!", icon="🛍️")
                            st.rerun()
                    else:
                        st.warning("⚠️ نفذت الكمية")
    else:
        st.info("المخزن فارغ حالياً. أضف مواد من تبويب (إضافة مادة جديدة).")

with tab3:
    st.subheader("👥 إدارة وتسجيل العملاء")
    iraq_govs = ["البصرة", "بغداد", "نينوى", "أربيل", "النجف", "كربلاء", "ذي قار", "بابل", "الأنبار", "ديالى", "كركوك", "صلاح الدين", "المثنى", "ميسان", "القادسية", "واسط", "دهوك", "السليمانية"]
    
    with st.form("add_customer_clean_form", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            c_name = st.text_input("اسم العميل كامل:")
        with col_c2:
            c_phone = st.text_input("رقم الهاتف:")
        with col_c3:
            c_gov = st.selectbox("المحافظة:", iraq_govs)
            
        c_address = st.text_input("العنوان التفصيلي / المنطقة:")
            
        if st.form_submit_button("تسجيل بيانات العميل"):
            if c_name and c_phone:
                st.session_state.customer_list.append({
                    "اسم العميل": c_name, 
                    "رقم الهاتف": c_phone, 
                    "المحافظة": c_gov,
                    "العنوان": c_address if c_address else "غير محدد",
                    "تاريخ التسجيل": datetime.now().strftime('%Y-%m-%d')
                })
                st.success(f"تم تسجيل العميل ({c_name}) بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى كتابة الاسم ورقم الهاتف.")

    st.divider()
    if st.session_state.customer_list:
        st.dataframe(pd.DataFrame(st.session_state.customer_list), use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلون حالياً.")

with tab4:
    st.subheader("🛒 سلة المبيعات والفواتير")
    if st.session_state.cart:
        total_cart_price = 0
        for idx, c_item in enumerate(st.session_state.cart):
            cols_cart = st.columns([3, 2, 2, 1])
            with cols_cart[0]:
                st.write(f"**{c_item['product_name']}**")
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
        st.markdown(f"### 💵 المجموع الكلي: **{int(total_cart_price):,} د.ع**")
        
        customer_options = [c["اسم العميل"] for c in st.session_state.customer_list] if st.session_state.customer_list else ["لا توجد عملاء مسجلين"]
        cust_name = st.selectbox("اختر اسم الزبون للفاتورة:", customer_options)
        
        pay_type = st.radio("طريقة الدفع:", ["🟡 نقد بالكامل (كاش)", "🔴 آجل بالكامل (دين)", "🔵 دفعة جزئية"], horizontal=True)
        
        paid_amount = total_cart_price if pay_type == "🟡 نقد بالكامل (كاش)" else (0 if pay_type == "🔴 آجل بالكامل (دين)" else float(st.text_input("المبلغ المدفوع حالياً:", "0") or 0))
        remaining_amount = total_cart_price - paid_amount

        if st.button("💾 إتمام البيع وحفظ الفاتورة", type="primary"):
            if not st.session_state.customer_list or cust_name == "لا توجد عملاء مسجلين":
                st.error("❌ يرجى تسجيل واختيار عميل أولاً!")
            else:
                try:
                    prod_names_str = []
                    for c_item in st.session_state.cart:
                        prod_names_str.append(f"{c_item['product_name']} (عدد: {c_item['qty']})")
                        res_p = supabase.table("products").select("quantity").eq("id", c_item["id"]).execute()
                        if res_p.data:
                            current_db_qty = res_p.data[0]["quantity"]
                            supabase.table("products").update({"quantity": max(0, current_db_qty - c_item['qty'])}).eq("id", c_item["id"]).execute()
                    
                    inv_code = f"INV-{len(st.session_state.invoices_list) + 1:03d}"
                    st.session_state.invoices_list.append({
                        "رقم الفاتورة": inv_code,
                        "الزبون": cust_name,
                        "المنتجات": " , ".join(prod_names_str),
                        "المبلغ الكلي": int(total_cart_price),
                        "الواصل": int(paid_amount),
                        "المتبقي (الدين)": int(remaining_amount),
                        "نوع الدفع": pay_type,
                        "التاريخ": datetime.now().strftime('%Y-%m-%d %H:%M')
                    })
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع وحفظ الفاتورة بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
    else:
        st.info("السلة فارغة.")

with tab5:
    st.subheader("📄 سجل الفواتير")
    if st.session_state.invoices_list:
        for inv in reversed(st.session_state.invoices_list):
            with st.container(border=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"#### {inv['رقم الفاتورة']} - {inv['الزبون']}")
                    st.write(f"📦 المواد: {inv['المنتجات']}")
                    st.write(f"💵 المجموع: {inv['المبلغ الكلي']:,} د.ع | الواصل: {inv['الواصل']:,} د.ع")
                with col2:
                    pdf_buffer = generate_pdf_invoice(inv)
                    st.download_button("📥 تحميل PDF بالعربي", data=pdf_buffer, file_name=f"{inv['رقم الفاتورة']}.pdf", mime="application/pdf", key=f"pdf_{inv['رقم الفاتورة']}")
    else:
        st.info("لا توجد فواتير مسجلة.")

with tab6:
    st.subheader("📊 تقارير الأرباح والجرد")
    if not st.session_state.is_vip:
        st.info("💡 النسخة المجانية (نموذج تجريبي). فعّل النسخة المدفوعة بكود `YASSER2026` لعرض بياناتك الحقيقية.")
    else:
        try:
            res_stats = supabase.table("products").select("*").eq("username", username).execute()
            if res_stats and res_stats.data:
                total_capital = sum(p["buy_price"] * p["quantity"] for p in res_stats.data)
                total_sales_val = sum(p["sell_price"] * p["quantity"] for p in res_stats.data)
                m1, m2, m3 = st.columns(3)
                m1.metric("إجمالي القطع", f"{sum(p['quantity'] for p in res_stats.data)}")
                m2.metric("إجمالي رأس المال", f"{int(total_capital):,} د.ع")
                m3.metric("الأرباح المتوقعة", f"{int(total_sales_val - total_capital):,} د.ع")
        except Exception:
            pass
