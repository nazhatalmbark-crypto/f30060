import streamlit as st

# إعداد الصفحة وتفعيل اللغة العربية والاتجاه من اليمين ليسار
st.set_page_config(
    page_title="نظام ياسر ويب", page_icon="🛍️", layout="wide"
)

# كود الـ CSS الشامل لحل مشكلة تقطيع الحروف وتعديل القائمة الجانبية (Sidebar)
st.markdown(
    """
    <style>
    /* توجيه القائمة الجانبية ومحتواها لليمين بشكل صحيح */
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stSidebar"] * {
        text-align: right;
        direction: rtl;
    }
    
    /* محاذاة عامة للنصوص في الصفحة لتناسب اللغة العربية */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* تنسيق الحقول والنصوص */
    label, .stTextInput, .stSelectbox, .stNumberInput {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# القائمة الجانبية للتطبيق
st.sidebar.title("🛍️ نظام ياسر ويب")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "القائمة الرئيسية",
    ["إدارة المخزن والمنتجات", "إضافة منتج جديد", "الفواتير والتقارير"],
)

# محتوى الصفحات
if menu == "إدارة المخزن والمنتجات":
    st.header("📦 إدارة المخزن والمنتجات")
    st.write("هنا يمكنك متابعة المنتجات والمخزون المتوفر.")

elif menu == "إضافة منتج جديد":
    st.header("➕ إضافة منتج / جهاز جديد")

    product_name = st.text_input("المنتج / الجهاز:")
    description = st.text_area("الوصفات الإضافية:")
    price = st.number_input("السعر (د.ع):", min_value=0.0)
    stock_status = st.selectbox("الوفـرة:", ["متوفر في المخزن", "نفذت الكمية"])

    if st.button("حفظ المنتج"):
        if product_name:
            st.success(f"تم حفظ المنتج ({product_name}) بنجاح!")
        else:
            st.warning("يرجى إدخال اسم المنتج على الأقل.")

elif menu == "الفواتير والتقارير":
    st.header("📄 الفواتير والتقارير")
    st.write("عرض تفاصيل الفواتير والعمليات السابقة.")
