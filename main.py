import streamlit as st
import pandas as pd
import datetime

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام ياسر ويب - إدارة العملاء",
    page_icon="👥",
    layout="wide"
)

# تهيئة الذاكرة المؤقتة للعملاء والمنتجات
if "customers_list" not in st.session_state:
    st.session_state.customers_list = []
if "products_list" not in st.session_state:
    st.session_state.products_list = [
        {"اسم المنتج": "منتج تجريبي 1", "سعر البيع": 15000, "الكمية": 50, "الربح المتوقع": 3000}
    ]

st.title("👥 إدارة العملاء والديون - نظام ياسر ويب")
st.caption("تم تعديل الجدول وربطه بالذاكرة المؤقتة ليعمل بسرعة وبدون أي أخطاء قاعدة بيانات أثناء التسجيل.")

tab1, tab2 = st.tabs(["👥 تسجيل العملاء والديون", "📦 المخزن والفواتير"])

# ---------------- تبويب العملاء المعدل ----------------
with tab1:
    st.subheader("إضافة وتسجيل عميل جديد")
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
    st.subheader("📋 جدول العملاء المسجلين والديون")
    if st.session_state.customers_list:
        df_cust = pd.DataFrame(st.session_state.customers_list)
        st.dataframe(df_cust, use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلين حالياً. جرب إضافة عميل جديد الآن بكل سهولة.")

# ---------------- تبويب المخزن والفواتير ----------------
with tab2:
    st.subheader("إدارة المخزن السريعة")
    if st.session_state.products_list:
        st.dataframe(pd.DataFrame(st.session_state.products_list), use_container_width=True)
    else:
        st.info("لا توجد منتجات مسجلة.")
