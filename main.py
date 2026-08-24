import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timezone

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - إدارة المبيعات والمخزون", page_icon="📦", layout="wide")

# تهيئة الـ Session State
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "customer_list" not in st.session_state:
    st.session_state.customer_list = []

if "invoices_list" not in st.session_state:
    st.session_state.invoices_list = []

if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

st.title("🛍️ نظام Yasser Web المتكامل لإدارة المبيعات والمخزون")

# شاشة تسجيل الدخول
if not st.session_state.logged_in_user:
    st.subheader("🔑 تسجيل الدخول للنظام")
    user_input = st.text_input("ادخل اسم المستخدم أو اسم المحل:")
    
    if st.button("دخول للنظام", type="primary"):
        if user_input.strip():
            username = user_input.strip()
            res = supabase.table("users").select("*").eq("username", username).execute()
            
            if not res.data:
                supabase.table("users").insert({"username": username, "is_paid": False}).execute()
                st.session_state.logged_in_user = username
                st.rerun()
            else:
                user_info = res.data[0]
                if user_info.get("is_paid"):
                    st.session_state.is_vip = True
                st.session_state.logged_in_user = username
                st.rerun()
        else:
            st.warning("يرجى كتابة الاسم أولاً.")
    st.stop()

username = st.session_state.logged_in_user

# الشريط الجانبي للتفعيل (النسخة المجانية والمدفوعة)
st.sidebar.title("⚙️ إعدادات الحساب")
st.sidebar.write(f"👤 المستخدم: **{username}**")

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
    st.sidebar.success("🌟 النسخة المدفوعة (VIP) مفعلة")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in_user = None
    st.session_state.is_vip = False
    st.rerun()

st.divider()

# التبويبات الرئيسية للنظام
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "➕ إضافة مادة جديدة", 
    "📦 عرض المخزن", 
    "👥 إدارة العملاء", 
    "🛒 إجراء بيع جديد", 
    "📄 سجل الفواتير", 
    "📊 تقارير الأرباح"
])

with tab1:
    st.subheader("➕ واجهة إضافة مادة جديدة للمخزن")
    res_prod_count = supabase.table("products").select("id").eq("username", username).execute()
    current_count = len(res_prod_count.data) if res_prod_count.data else 0
    
    if not st.session_state.is_vip and current_count >= 5:
        st.warning("⚠️ **تنبيه النسخة المجانية:** وصلت للحد الأقصى (5 منتجات). فعّل النسخة المدفوعة من القائمة الجانبية لإضافة منتجات بلا حدود!")
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
                        p_buy = int(p_buy_str.strip())
                        p_sell = int(p_sell_str.strip())
                        p_qty = int(p_qty_str.strip())
                        
                        supabase.table("products").insert({
                            "username": username,
                            "product_name": p_name.strip(),
                            "buy_price": float(p_buy),
                            "sell_price": float(p_sell),
                            "quantity": p_qty
                        }).execute()
                        st.success(f"تمت إضافة المادة ({p_name}) بنجاح!")
                        st.rerun()
                    except ValueError:
                        st.error("❌ خطأ: يرجى إدخال أرقام صحيحة حصراً في الأسعار والكمية.")
                else:
                    st.warning("يرجى كتابة اسم المنتج أولاً.")

with tab2:
    st.subheader("🧱 عرض البضائع والمخزن الحالي")
    res_prod = supabase.table("products").select("*").eq("username", username).execute()
    
    if res_prod.data:
        cols = st.columns(3)
        for idx, item in enumerate(res_prod.data):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### 📦 {item['product_name']}")
                    st.markdown(f"💰 **سعر البيع:** `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🏷️ **سعر الشراء:** `{int(item['buy_price']):,}` د.ع")
                    st.markdown(f"🔢 **الكمية المتوفرة:** `{int(item['quantity'])}` قطعة")
                    profit_per_unit = int(item['sell_price'] - item['buy_price'])
                    st.caption(f"📈 ربح القطعة: {profit_per_unit:,} د.ع")
    else:
        st.info("المخزن فارغ حالياً. قم بإضافة مواد من تبويب (إضافة مادة جديدة).")

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
    st.subheader("🛒 تسجيل عملية بيع وتحرير فاتورة جديدة")
    res_sell = supabase.table("products").select("*").eq("username", username).gt("quantity", 0).execute()
    
    if res_sell.data:
        prod_dict = {p["product_name"]: p for p in res_sell.data}
        selected_prod = st.selectbox("اختر البضاعة المراد بيعها:", list(prod_dict.keys()))
        
        item = prod_dict[selected_prod]
        max_q = int(item["quantity"])
        unit_price = int(item["sell_price"])
        
        customer_options = ["زبون محلي / كاش"]
        if st.session_state.customer_list:
            customer_options += [c["اسم العميل"] for c in st.session_state.customer_list]
            
        col_q, col_c = st.columns(2)
        with col_q:
            sell_q_str = st.text_input(f"الكمية المراد بيعها (المتوفّر: {max_q}):", "1")
        with col_c:
            cust_name = st.selectbox("اختر الزبون:", customer_options)
            
        try:
            sell_q = int(sell_q_str.strip())
            if sell_q < 1: sell_q = 1
            if sell_q > max_q: sell_q = max_q
        except ValueError:
            sell_q = 1
            
        total_price = sell_q * unit_price
        st.markdown(f"### 💵 المجموع الكلي للفاتورة: **{total_price:,} د.ع**")
        
        st.write("---")
        pay_type = st.radio("طريقة الدفع ونوع الفاتورة:", ["🟡 نقد بالكامل (كاش)", "🔴 آجل بالكامل (دين)", "🔵 دفعة جزئية"], horizontal=True)
        
        paid_amount = 0
        if pay_type == "🟡 نقد بالكامل (كاش)":
            paid_amount = total_price
        elif pay_type == "🔴 آجل بالكامل (دين)":
            paid_amount = 0
        else:
            paid_amount_str = st.text_input("المبلغ الواصل (المدفوع حالياً):", "0")
            try:
                paid_amount = int(paid_amount_str.strip())
                if paid_amount < 0: paid_amount = 0
                if paid_amount > total_price: paid_amount = total_price
            except ValueError:
                paid_amount = 0
            
        remaining_amount = total_price - paid_amount

        if st.button("تأكيد وحفظ الفاتورة", type="primary"):
            new_q = max_q - sell_q
            supabase.table("products").update({"quantity": new_q}).eq("id", item["id"]).execute()
            
            inv_id = len(st.session_state.invoices_list) + 1
            inv_code = f"INV-{inv_id:03d}"
            
            st.session_state.invoices_list.append({
                "رقم الفاتورة": inv_code,
                "الزبون": cust_name,
                "المنتج": selected_prod,
                "الكمية": sell_q,
                "المبلغ الكلي": total_price,
                "الواصل": paid_amount,
                "المتبقي (الدين)": remaining_amount,
                "نوع الدفع": pay_type,
                "التاريخ": datetime.now().strftime('%Y-%m-%d %H:%M')
            })
            
            st.success("✅ تم حفظ الفاتورة وتحديث المخزون بنجاح!")
            
            invoice_txt = f"""=======================================
           Yasser Web - فاتورة مبيعات
=======================================
رقم الفاتورة: {inv_code}
اسم المحل: {username}
الزبون: {cust_name}
التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
---------------------------------------
المنتج: {selected_prod}
الكمية: {sell_q}
سعر القطعة: {unit_price:,} د.ع
---------------------------------------
المبلغ الكلي: {total_price:,} د.ع
المبلغ الواصل: {paid_amount:,} د.ع
المتبقي بذمة العميل: {remaining_amount:,} د.ع
نوع الدفع: {pay_type}
=======================================
شكراً لتسوقكم معنا في Yasser Web!
"""
            st.download_button(
                label="📄 تحميل الفاتورة رسمياً (TXT)",
                data=invoice_txt,
                file_name=f"{inv_code}.txt",
                mime="text/plain"
            )
    else:
        st.warning("لا توجد بضائع متاحة للبيع بالمخزن حالياً.")

with tab5:
    st.subheader("📄 سجل الفواتير ومتابعة ديون العملاء (الذمم)")
    if st.session_state.invoices_list:
        for inv in reversed(st.session_state.invoices_list):
            with st.container(border=True):
                col_inv1, col_inv2, col_inv3 = st.columns([2, 2, 2])
                with col_inv1:
                    st.markdown(f"#### {inv['رقم الفاتورة']} | {inv['نوع الدفع']}")
                    st.write(f"👤 **الزبون:** {inv['الزبون']}")
                    st.write(f"📅 **التاريخ:** {inv['التاريخ']}")
                with col_inv2:
                    st.write(f"📦 **المنتج:** {inv['المنتج']} (عدد: {inv['الكمية']})")
                    st.write(f"💵 **المبلغ الكلي:** {inv['المبلغ الكلي']:,} د.ع")
                with col_inv3:
                    st.write(f"✅ **الواصل:** {inv['الواصل']:,} د.ع")
                    st.write(f"❌ **المتبقي:** {inv['المتبقي (الدين)']:,} د.ع")
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

with tab6:
    st.subheader("📊 تقارير الأرباح ورأس المال")
    res_stats = supabase.table("products").select("*").eq("username", username).execute()
    if res_stats.data:
        total_count = sum(p["quantity"] for p in res_stats.data)
        total_capital = sum(p["buy_price"] * p["quantity"] for p in res_stats.data)
        total_sales_val = sum(p["sell_price"] * p["quantity"] for p in res_stats.data)
        expected_profit = int(total_sales_val - total_capital)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي القطع", f"{int(total_count)} قطعة")
        m2.metric("رأس المال (شراء)", f"{int(total_capital):,} د.ع")
        m3.metric("الربح المتوقع", f"{expected_profit:,} د.ع")
    else:
        st.info("أضف بضائع لعرض التقارير.")
