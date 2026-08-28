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
import arabic_reshaper
from bidi.algorithm import get_display

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - نظام إدارة المبيعات والمخزون", page_icon="📦", layout="wide")

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

def fix_arabic(text):
    if not text:
        return ""
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return text

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
    for prod_line in inv['المنتجات'].split(" , "):
        p.drawString(width - 240, text_y, fix_arabic(f"- {prod_line}"))
        text_y -= 25
    
    text_y -= 15
    p.line(50, text_y, width - 50, text_y)
    text_y -= 30
    p.setFont(f_name, 12)
    p.drawString(width - 250, text_y, fix_arabic(f"المبلغ الكلي: {inv['المبلغ الكلي']:,} د.ع"))
    text_y -= 25
    p.drawString(width - 250, text_y, fix_arabic(f"المبلغ الواصل: {inv['الواصل']:,} د.ع"))
    text_y -= 25
    p.drawString(width - 250, text_y, fix_arabic(f"المتبقي (الدين): {inv['المتبقي (الدين)']:,} د.ع"))
    text_y -= 35
    p.line(50, text_y, width - 50, text_y)
    p.setFont(f_name, 10)
    p.drawCentredString(width / 2.0, text_y - 30, fix_arabic("شكراً لتعاملكم مع نظام Yasser Web"))
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

st.title("🛍️ نظام Yasser Web المتكامل لإدارة المبيعات والمخزون")

# شاشة الدخول وتسجيل حساب جديد (واضحة وصريحة)
if not st.session_state.logged_in_user:
    st.subheader("🔐 بوابة الدخول وإنشاء حساب جديد للمحل")
    
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
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
                    
    with auth_tab2:
        with st.form("signup_form"):
            new_user = st.text_input("اختر اسم المستخدم أو اسم المحل الجديد:")
            signup_submitted = st.form_submit_button("إنشاء الحساب الجديد الآن", type="primary")
            if signup_submitted:
                if new_user.strip():
                    try:
                        check_res = supabase.table("users").select("*").eq("username", new_user.strip()).execute()
                        if check_res.data:
                            st.error("❌ اسم المستخدم هذا مستخدم مسبقاً، اختر غيره.")
                        else:
                            supabase.table("users").insert({
                                "username": new_user.strip(),
                                "is_paid": False
                            }).execute()
                            st.session_state.logged_in_user = new_user.strip()
                            st.session_state.is_vip = False
                            st.success("🎉 تم إنشاء الحساب والدخول بنجاح!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى كتابة اسم المستخدم الجديد.")
    st.stop()

# واجهة التطبيق الكاملة بعد الدخول
username = st.session_state.logged_in_user

st.sidebar.title("⚙️ إعدادات الحساب")
st.sidebar.write(f"👤 المستخدم الحالي: **{username}**")

cart_count_badge = sum(item['qty'] for item in st.session_state.cart)
st.sidebar.info(f"🛒 المواد بالسلة: **{cart_count_badge}** قطعة")

if not st.session_state.is_vip:
    st.sidebar.warning("🔒 النسخة: **مجانية (محدودة)**")
    vip_code = st.sidebar.text_input("كود التفعيل (VIP):", type="password")
    if st.sidebar.button("تفعيل النسخة"):
        if vip_code.strip() == "YASSER2026":
            st.session_state.is_vip = True
            try:
                supabase.table("users").update({"is_paid": True}).eq("username", username).execute()
            except Exception:
                pass
            st.sidebar.success("تم التفعيل بنجاح! 🎉")
            st.rerun()
        else:
            st.sidebar.error("الكود خطأ! (الكود: YASSER2026)")
else:
    st.sidebar.success("🌟 النسخة مفعلة بالكامل (VIP)")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in_user = None
    st.session_state.is_vip = False
    st.session_state.cart = []
    st.rerun()

st.divider()

# التبويبات الستة الأساسية
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "➕ إضافة مادة جديدة", 
    "📦 عرض المخزن والسلة", 
    "👥 إدارة العملاء", 
    "🛒 إتمام البيع والفواتير", 
    "📄 سجل الفواتير", 
    "📊 تقارير الأرباح"
])

with tab1:
    st.subheader("➕ إضافة مادة جديدة للمخزن")
    try:
        res_prod_count = supabase.table("products").select("id").eq("username", username).execute()
        current_count = len(res_prod_count.data) if res_prod_count.data else 0
    except Exception:
        current_count = 0
    
    if not st.session_state.is_vip and current_count >= 5:
        st.warning("⚠️ وصل للحد الأقصى (5 منتجات) للنسخة المجانية. فعّل النسخة المدفوعة بكود (`YASSER2026`) من القائمة الجانبية.")
    else:
        with st.form("add_p_form", clear_on_submit=True):
            p_name = st.text_input("اسم المنتج:")
            c1, c2, c3 = st.columns(3)
            with c1:
                p_buy_str = st.text_input("سعر الشراء (د.ع):", "0")
            with c2:
                p_sell_str = st.text_input("سعر البيع (د.ع):", "0")
            with c3:
                p_qty_str = st.text_input("الكمية:", "1")
            
            if st.form_submit_button("حفظ المادة", type="primary"):
                if p_name.strip():
                    try:
                        p_buy = float(p_buy_str.strip())
                        p_sell = float(p_sell_str.strip())
                        p_qty = int(p_qty_str.strip())
                        
                        supabase.table("products").insert({
                            "username": username,
                            "product_name": p_name.strip(),
                            "buy_price": p_buy,
                            "sell_price": p_sell,
                            "quantity": p_qty
                        }).execute()
                        st.success(f"تمت إضافة ({p_name}) بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى كتابة اسم المنتج.")

with tab2:
    st.subheader("📦 بضائع ومخزن المحل")
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
                    st.markdown(f"🔢 **الكمية:** `{int(item['quantity'])}` قطعة")
                    if item['quantity'] > 0:
                        if st.button("🛒 أضف للسلة", key=f"c_{item['id']}"):
                            found = False
                            for c_item in st.session_state.cart:
                                if c_item["id"] == item["id"]:
                                    if c_item["qty"] < item["quantity"]:
                                        c_item["qty"] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({
                                    "id": item["id"],
                                    "product_name": item["product_name"],
                                    "sell_price": item["sell_price"],
                                    "max_qty": item["quantity"],
                                    "qty": 1
                                })
                            st.success("تمت الإضافة للسلة!")
                            st.rerun()
                    else:
                        st.warning("نفذت الكمية")
    else:
        st.info("المخزن فارغ.")

with tab3:
    st.subheader("👥 إدارة العملاء")
    iraq_govs = ["البصرة", "بغداد", "نينوى", "أربيل", "النجف", "كربلاء", "ذي قار", "بابل", "الأنبار", "ديالى", "كركوك"]
    with st.form("cust_form", clear_on_submit=True):
        cc1, cc2, cc3 = st.columns(3)
        with cc1: c_name = st.text_input("اسم العميل:")
        with cc2: c_phone = st.text_input("رقم الهاتف:")
        with cc3: c_gov = st.selectbox("المحافظة:", iraq_govs)
        
        if st.form_submit_button("تسجيل العميل"):
            if c_name and c_phone:
                st.session_state.customer_list.append({"اسم العميل": c_name, "رقم الهاتف": c_phone, "المحافظة": c_gov})
                st.success("تم تسجيل العميل بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى ملء الحقول المطلوبة.")
    if st.session_state.customer_list:
        st.dataframe(pd.DataFrame(st.session_state.customer_list), use_container_width=True)

with tab4:
    st.subheader("🛒 سلة المبيعات وإصدار الفواتير")
    if st.session_state.cart:
        total_price = 0
        for idx, c_item in enumerate(st.session_state.cart):
            col_s = st.columns([3, 2, 2, 1])
            with col_s[0]: st.write(f"**{c_item['product_name']}**")
            with col_s[1]: c_item['qty'] = st.number_input("الكمية", 1, int(c_item['max_qty']), int(c_item['qty']), key=f"q_{c_item['id']}")
            with col_s[2]:
                it_tot = c_item['sell_price'] * c_item['qty']
                total_price += it_tot
                st.write(f"**{int(it_tot):,}** د.ع")
            with col_s[3]:
                if st.button("❌", key=f"del_{c_item['id']}" ):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        st.divider()
        st.markdown(f"### المجموع الكلي: **{int(total_price):,} د.ع**")
        cust_opts = [c["اسم العميل"] for c in st.session_state.customer_list] if st.session_state.customer_list else ["لا يوجد عملاء"]
        cust_name = st.selectbox("اختر الزبون:", cust_opts)
        pay_type = st.radio("طريقة الدفع:", ["نقد (كاش)", "آجل (دين)", "دفعة جزئية"], horizontal=True)
        paid = total_price if pay_type == "نقد (كاش)" else (0 if pay_type == "آجل (دين)" else float(st.text_input("المبلغ المدفوع:", "0") or 0))
        rem = total_price - paid

        if st.button("💾 إتمام البيع وحفظ الفاتورة", type="primary"):
            if not st.session_state.customer_list or cust_name == "لا يوجد عملاء":
                st.error("اختر عميلاً أولاً!")
            else:
                try:
                    p_names = []
                    for c_item in st.session_state.cart:
                        p_names.append(f"{c_item['product_name']} (عدد: {c_item['qty']})")
                        res_p = supabase.table("products").select("quantity").eq("id", c_item["id"]).execute()
                        if res_p.data:
                            curr_q = res_p.data[0]["quantity"]
                            supabase.table("products").update({"quantity": max(0, curr_q - c_item['qty'])}).eq("id", c_item["id"]).execute()
                    
                    inv_code = f"INV-{len(st.session_state.invoices_list) + 1:03d}"
                    st.session_state.invoices_list.append({
                        "رقم الفاتورة": inv_code, "الزبون": cust_name, "المنتجات": " , ".join(p_names),
                        "المبلغ الكلي": int(total_price), "الواصل": int(paid), "المتبقي (الدين)": int(rem),
                        "نوع الدفع": pay_type, "التاريخ": datetime.now().strftime('%Y-%m-%d %H:%M')
                    })
                    st.session_state.cart = []
                    st.success("تمت عملية البيع بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
    else:
        st.info("السلة فارغة.")

with tab5:
    st.subheader("📄 سجل الفواتير وتحميل PDF")
    if st.session_state.invoices_list:
        for inv in reversed(st.session_state.invoices_list):
            with st.container(border=True):
                col_i1, col_i2 = st.columns([2, 1])
                with col_i1:
                    st.markdown(f"#### {inv['رقم الفاتورة']} - {inv['الزبون']}")
                    st.write(f"📦 المواد: {inv['المنتجات']}")
                    st.write(f"💵 المجموع: {inv['المبلغ الكلي']:,} د.ع | الواصل: {inv['الواصل']:,} د.ع")
                with col_i2:
                    pdf_buf = generate_pdf_invoice(inv)
                    st.download_button("📥 تحميل PDF", data=pdf_buf, file_name=f"{inv['رقم الفاتورة']}.pdf", mime="application/pdf", key=f"pdf_{inv['رقم الفاتورة']}")
    else:
        st.info("لا توجد فواتير.")

with tab6:
    st.subheader("📊 تقارير الأرباح")
    if not st.session_state.is_vip:
        st.info("فعّل النسخة المدفوعة بكود `YASSER2026` لعرض التقارير والأرباح الكاملة.")
    else:
        try:
            res_s = supabase.table("products").select("*").eq("username", username).execute()
            if res_s and res_s.data:
                tot_cap = sum(p["buy_price"] * p["quantity"] for p in res_s.data)
                tot_sal = sum(p["sell_price"] * p["quantity"] for p in res_s.data)
                k1, k2, k3 = st.columns(3)
                k1.metric("إجمالي القطع", f"{sum(p['quantity'] for p in res_s.data)}")
                k2.metric("رأس المال", f"{int(tot_cap):,} د.ع")
                k3.metric("الأرباح المتوقعة", f"{int(tot_sal - tot_cap):,} د.ع")
        except Exception:
            pass
