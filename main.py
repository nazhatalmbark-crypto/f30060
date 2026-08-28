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

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - نظام إدارة المبيعات", page_icon="📦", layout="wide")

# تسجيل خط عربي مدعوم (مثل Amiri أو Cairo) لتظهر الحروف العربية بشكل صحيح تماماً
# ملاحظة: تأكد من تثبيت مكتبتي arabic-reshaper و python-bidi عبر الـ terminal
try:
    # سيتم استخدام خط افتراضي يدعم العربية إذا توفر، أو نسجل خط Amiri إذا تم تحميله
    pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
    ARABIC_FONT = 'Amiri'
except:
    ARABIC_FONT = 'Helvetica'

def format_arabic(text):
    if not text:
        return ""
    # إعادة تشكيل الحروف العربية وعكسها لتتوافق مع الـ PDF
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

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

# دالة توليد ملف الـ PDF بالفاتورة (مع دعم كامل للغة العربية وترتيب الكلمات)
def generate_pdf_invoice(inv):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # رأس الفاتورة
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "YASSER WEB - فاتورة مبيعات رسمية")
    
    p.setFont("Helvetica", 10)
    p.drawString(width - 200, height - 50, f"Date: {inv['التاريخ']}")
    
    p.setStrokeColorRGB(0.2, 0.2, 0.2)
    p.setLineWidth(1)
    p.line(50, height - 65, width - 50, height - 65)
    
    # معلومات الفاتورة والزبون (مع تحويل النصوص العربية بـ format_arabic)
    p.setFont(ARABIC_FONT, 12)
    p.drawString(50, height - 95, format_arabic(f"رقم الفاتورة: {inv['رقم الفاتورة']}"))
    p.drawString(50, height - 120, format_arabic(f"اسم الزبون: {inv['الزبون']}"))
    p.drawString(50, height - 145, format_arabic(f"نوع الدفع: {inv['نوع الدفع']}"))
    
    p.line(50, height - 165, width - 50, height - 165)
    
    # تفاصيل المواد المباعة
    p.drawString(50, height - 195, format_arabic("تفاصيل المنتجات والمواد المباعة:"))
    
    text_y = height - 225
    items_list_str = inv['المنتجات'].split(" , ")
    for prod_line in items_list_str:
        p.drawString(70, text_y, format_arabic(f">> {prod_line}"))
        text_y -= 25
        
    text_y -= 10
    p.line(50, text_y, width - 50, text_y)
    
    # الملخص المالي
    text_y -= 35
    p.drawString(50, text_y, format_arabic(f"المبلغ الكلي: {inv['المبلغ الكلي']:,} دينار عراقي"))
    
    text_y -= 25
    p.drawString(50, text_y, format_arabic(f"المبلغ الواصل: {inv['الواصل']:,} دينار عراقي"))
    
    text_y -= 25
    p.drawString(50, text_y, format_arabic(f"المتبقي (الدين): {inv['المتبقي (الدين)']:,} دينار عراقي"))
    
    text_y -= 45
    p.setLineWidth(0.5)
    p.line(50, text_y, width - 50, text_y)
    
    # رسالة النهاية
    p.drawCentredString(width / 2.0, text_y - 35, format_arabic("شكراً لتعاملكم مع نظام Yasser Web للمبيعات والمخزن!"))
    
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
    st.subheader("🧱 عرض بضائع المحل (اختر عدة مواد لتكوين طلبة الزبون)")
    
    if st.session_state.cart:
        total_items_in_cart = sum(i['qty'] for i in st.session_state.cart)
        total_price_preview = sum(i['sell_price'] * i['qty'] for i in st.session_state.cart)
        st.success(f"🛒 **السلة حالياً تحتوي على:** {total_items_in_cart} قطعة | المجموع المؤقت: **{int(total_price_preview):,} د.ع** — *(اذهب لتبويب 'إتمام البيع والفواتير' لإنهاء الحساب)*")
    
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
    st.subheader("👥 إضافة وتسجيل العملاء")
    iraq_govs = ["بغداد", "البصرة", "نينوى", "أربيل", "النجف", "كربلاء", "ذي قار", "بابل", "الأنبار", "ديالى", "كركوك", "صلاح الدين", "المثنى", "ميسان", "القادسية", "واسط", "دهوك", "السليمانية"]
    
    with st.form("add_customer_clean_form", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            c_name = st.text_input("اسم العميل كامل:")
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
    st.subheader("📋 سجل العملاء والزبائن")
    if st.session_state.customer_list:
        st.dataframe(pd.DataFrame(st.session_state.customer_list), use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلون حالياً.")

with tab4:
    st.subheader("🛒 سلة المبيعات (تجميع مواد الزبون وإتمام الفاتورة)")
    
    if st.session_state.cart:
        st.write("### 🛍️ المواد التي اختارها الزبون للفاتورة الحالية:")
        total_cart_price = 0
        
        for idx, c_item in enumerate(st.session_state.cart):
            cols_cart = st.columns([3, 2, 2, 1])
            with cols_cart[0]:
                st.write(f"**{c_item['product_name']}** (السعر: {int(c_item['sell_price']):,} د.ع)")
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
        st.markdown(f"### 💵 المجموع الكلي لكل مواد الزبون: **{int(total_cart_price):,} د.ع**")
        
        if not st.session_state.customer_list:
            st.warning("⚠️ تنبيه مهم جداً: يجب إضافة وتسجيل العميل أولاً من تبويب (إدارة العملاء) لكي تتمكن من حفظ الفاتورة!")
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
                    for c_item in st.session_state.cart:
                        prod_names_str.append(f"{c_item['product_name']} (Qty: {c_item['qty']})")
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
        st.info("🛒 السلة فارغة حالياً. اذهب إلى تبويب (عرض المخزن وسلة المبيعات) واضغط على زر (إضافة إلى السلة) لأي مواد تريد بيعها للزبون!")

with tab5:
    st.subheader("📄 سجل الفواتير ومتابعة ديون العملاء (الذمم)")
    
    if st.session_state.invoices_list:
        if st.button("🗑️ مسح السجل القديم"):
            st.session_state.invoices_list = []
            st.success("تم مسح السجل القديم بنجاح.")
            st.rerun()
            
        for inv in reversed(st.session_state.invoices_list):
            with st.container(border=True):
                col_inv1, col_inv2, col_inv3 = st.columns([2, 2, 2])
                with col_inv1:
                    st.markdown(f"#### {inv['رقم الفاتورة']} | {inv['نوع الدفع']}")
                    st.write(f"👤 **الزبون:** {inv['الزبون']}")
                    st.write(f"📅 **التاريخ:** {inv['التاريخ']}")
                with col_inv2:
                    st.write(f"📦 **المواد:** {inv['المنتجات']}")
                with col_inv3:
                    st.write(f"💵 **المجموع:** {inv['المبلغ الكلي']:,} د.ع")
                    st.write(f"✅ **الواصل:** {inv['الواصل']:,} د.ع")
                    st.write(f"❌ **المتبقي:** {inv['المتبقي (الدين)']:,} د.ع")
                    
                    pdf_buffer = generate_pdf_invoice(inv)
                    st.download_button(
                        label="📥 تحميل الفاتورة PDF",
                        data=pdf_buffer,
                        file_name=f"{inv['رقم الفاتورة']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_btn_{inv['رقم الفاتورة']}"
                    )
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

with tab6:
    st.subheader("📊 تقارير الأرباح ورأس المال وجرد المخزن")
    
    if not st.session_state.is_vip:
        st.info("💡 ملاحظة: أنت تستخدم النسخة المجانية. إليك نموذج توضيحي:")
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي القطع بالمخزن", "50 قطعة (نموذج)")
        m2.metric("إجمالي رأس المال", "500,000 د.ع")
        m3.metric("إجمالي الأرباح المتوقعة", "250,000 د.ع")
        st.warning("🔒 لتفعيل التقارير الحقيقية لموادك، أدخل كود التفعيل (`YASSER2026`) من القائمة الجانبية!")
    else:
        try:
            res_stats = supabase.table("products").select("*").eq("username", username).execute()
        except Exception:
            res_stats = None
        
        if res_stats and res_stats.data:
            total_count = sum(p["quantity"] for p in res_stats.data)
            total_capital = sum(p["buy_price"] * p["quantity"] for p in res_stats.data)
            total_sales_val = sum(p["sell_price"] * p["quantity"] for p in res_stats.data)
            expected_profit = int(total_sales_val - total_capital)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي القطع بالمخزن", f"{int(total_count)} قطعة")
            m2.metric("إجمالي رأس المال", f"{int(total_capital):,} د.ع")
            m3.metric("إجمالي الأرباح المتوقعة", f"{expected_profit:,} د.ع")
        else:
            st.info("مخزنك فارغ حالياً.")
