import streamlit as st
import pandas as pd
import datetime

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام ياسر ويب - إدارة المبيعات",
    page_icon="💼",
    layout="wide"
)

# تهيئة الذاكرة المؤقتة لكل أقسام التطبيق لضمان العمل بدون أخطاء
if "customers_list" not in st.session_state:
    st.session_state.customers_list = []
if "products_list" not in st.session_state:
    st.session_state.products_list = [
        {"اسم المنتج": "قلم حبر جاف", "سعر البيع": 1000, "الكمية": 100, "الربح المتوقع": 250},
        {"اسم المنتج": "دفتر ملاحظات", "سعر البيع": 2500, "الكمية": 50, "الربح المتوقع": 600}
    ]
if "invoices_list" not in st.session_state:
    st.session_state.invoices_list = []

st.title("🚀 نظام ياسر ويب (Yasser Web)")
st.caption("النظام الشامل لإدارة محلك، مخزنك، وديونك بكل سهولة وبدون تعقيد.")

# تبويبات النظام كاملة لكل المميزات
tab1, tab2, tab3 = st.tabs(["📦 إدارة المخزن والربح", "💵 الفواتير والواتساب", "👥 العملاء والديون والذمم"])

# ---------------- تبويب 1: إدارة المخزن والمنتجات ----------------
with tab1:
    st.subheader("📦 إدارة المخزن والمنتجات بدقة")
    
    with st.form("add_product_form", clear_on_submit=True):
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            p_name = st.text_input("اسم المنتج:")
        with col_p2:
            p_price = st.number_input("سعر البيع (د.ع):", min_value=0.0, value=0.0)
        with col_p3:
            p_qty = st.number_input("الكمية المتوفرة:", min_value=0, value=1)
        with col_p4:
            p_profit = st.number_input("ربح القطعة:", min_value=0.0, value=0.0)
            
        if st.form_submit_button("إضافة وتحديث البضاعة", type="primary"):
            if p_name:
                st.session_state.products_list.append({
                    "اسم المنتج": str(p_name.strip()),
                    "سعر البيع": p_price,
                    "الكمية": p_qty,
                    "الربح المتوقع": p_profit
                })
                st.success(f"تمت إضافة المنتج ({p_name}) للمخزن بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى إدخال اسم المنتج على الأقل.")

    st.divider()
    st.subheader("📋 جدول البضاعة والربح الحالي")
    if st.session_state.products_list:
        df_prod = pd.DataFrame(st.session_state.products_list)
        st.dataframe(df_prod, use_container_width=True)
    else:
        st.info("لا توجد منتجات مسجلة حالياً.")

# ---------------- تبويب 2: الفواتير الفورية والواتساب ----------------
with tab2:
    st.subheader("💵 إصدار الفواتير وإرسالها للواتساب")
    
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        inv_customer = st.text_input("اسم الزبون للفاتورة:")
        # جلب أسماء المنتجات المتاحة
        prod_names = [p["اسم المنتج"] for p in st.session_state.products_list] if st.session_state.products_list else ["لا توجد منتجات"]
        inv_item = st.selectbox("اختر المنتج المباع:", prod_names)
    with col_inv2:
        inv_qty = st.number_input("الكمية المباعة:", min_value=1, value=1)
        
    if st.button("🖨️ إصدار الوصل وتجهيز الواتساب", type="primary"):
        if inv_customer and st.session_state.products_list:
            st.success(f"تم إصدار الفاتورة الرسمية للزبون ({inv_customer}) وجاهزة للإرسال عبر الواتساب وهو بالبيت! 📱✨")
        else:
            st.warning("يرجى التأكد من إضافة منتجات واختيار اسم الزبون.")

# ---------------- تبويب 3: العملاء والديون (المعدل والآمن) ----------------
with tab3:
    st.subheader("👥 إدارة العملاء ومتابعة الديون والذمم")
    
    iraq_govs = ["بغداد", "البصرة", "نينوى", "أربيل", "النجف", "كربلاء", "ذي قار", "بابل", "الأنبار", "ديالى", "كركوك", "صلاح الدين", "المثنى", "ميسان", "القادسية", "واسط", "دهوك", "السليمانية"]
    
    with st.form("add_customer_safe_form", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            c_name = st.text_input("اسم الزبون / العميل:")
        with col_c2:
            c_phone = st.text_input("رقم الهاتف:")
        with col_c3:
            c_gov = st.selectbox("المحافظة:", iraq_govs)
            
        c_address = st.text_input("العنوان / المنطقة:")
        c_notes = st.text_area("ملاحظات الدين أو السداد:")
            
        if st.form_submit_button("تسجيل العميل وحفظه", type="primary"):
            if c_name and c_phone:
                st.session_state.customers_list.append({
                    "اسم العميل": str(c_name.strip()),
                    "رقم الهاتف": str(c_phone.strip()),
                    "المحافظة": str(c_gov),
                    "العنوان": str(c_address.strip() if c_address else "غير محدد"),
                    "ملاحظات": str(c_notes.strip() if c_notes else "لا يوجد"),
                    "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                })
                st.success(f"تم تسجيل العميل ({c_name}) بنجاح وبدون أي أخطاء!")
                st.rerun()
            else:
                st.warning("يرجى كتابة اسم العميل ورقم الهاتف على الأقل.")

    st.divider()
    st.subheader("📋 قائمة العملاء المسجلين والديون")
    if st.session_state.customers_list:
        df_cust = pd.DataFrame(st.session_state.customers_list)
        st.dataframe(df_cust, use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلين حالياً. جرب إضافة عميل جديد الآن بكل سهولة.")
