import streamlit as st

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="نظام ياسر ويب", page_icon="🛍️", layout="wide"
)

# كود الـ CSS الشامل لحل مشكلة تقطيع الحروف في القائمة الجانبية (Sidebar)
st.markdown(
    """
    <style>
    /* توسيع وتعديل اتجاه القائمة الجانبية لمنع تقطيع الحروف */
    [data-testid="stSidebar"] {
        width: 320px !important;
        direction: rtl !important;
    }
    [data-testid="stSidebar"] * {
        direction: rtl !important;
        text-align: right !important;
        writing-mode: horizontal-tb !important;
        white-space: normal !important;
    }
    
    /* اتجاه عام للصفحة باللغة العربية */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# القائمة الجانبية الكاملة للنظام
st.sidebar.title("🛍️ نظام ياسر ويب")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "القائمة الرئيسية",
    [
        "إدارة المخزن والمنتجات",
        "إضافة منتج جديد",
        "إضافة عميل جديد",
        "قسم السداد والبيع",
        "عرض وإدارة المنتجات (بيع وتعديل)",
        "الفواتير والتقارير",
    ],
)

# 1. إدارة المخزن والمنتجات
if menu == "إدارة المخزن والمنتجات":
    st.header("📦 إدارة المخزن والمنتجات")
    st.write("هنا يمكنك متابعة المنتجات والمخزون المتوفر بالكامل.")

# 2. إضافة منتج جديد
elif menu == "إضافة منتج جديد":
    st.header("➕ إضافة منتج / جهاز جديد")

    product_name = st.text_input("اسم المنتج / الجهاز:")
    description = st.text_area("المواصفات والأوصاف الإضافية:")
    price = st.number_input("السعر (د.ع):", min_value=0.0, step=500.0)
    quantity = st.number_input(
        "الكمية المتوفرة:", min_value=0, step=1
    )
    stock_status = st.selectbox("الوفـرة:", ["متوفر في المخزن", "نفذت الكمية"])

    if st.button("حفظ المنتج الجديد"):
        if product_name:
            st.success(
                f"تم حفظ المنتج ({product_name}) والكمية ({quantity}) بنجاح!"
            )
        else:
            st.warning("يرجى إدخال اسم المنتج على الأقل.")

# 3. إضافة عميل جديد
elif menu == "إضافة عميل جديد":
    st.header("👥 إضافة عميل جديد")

    client_name = st.text_input("اسم العميل:")
    client_phone = st.text_input("رقم الهاتف:")
    client_address = st.text_input("العنوان (منطقة / الشارع):")

    if st.button("حفظ بيانات العميل"):
        if client_name:
            st.success(f"تم تسجيل العميل ({client_name}) بنجاح!")
        else:
            st.warning("يرجى إدخال اسم العميل على الأقل.")

# 4. قسم السداد والبيع
elif menu == "قسم السداد والبيع":
    st.header("💳 قسم السداد وإتمام البيع")
    st.write("تسجيل عمليات البيع والدفع المباشر.")

    bill_client = st.selectbox(
        "اختر العميل:", ["زبون نقدي (عام)", "محمد علي", "أحمد حسين"]
    )
    paid_amount = st.number_input("المبلغ المدفوع (د.ع):", min_value=0.0)

    if st.button("إتمام عملية السداد"):
        st.success("تم إتمام عملية السداد وحفظ الفاتورة بنجاح!")

# 5. عرض وإدارة المنتجات (بيع ونقص الكميات)
elif menu == "عرض وإدارة المنتجات (بيع وتعديل)":
    st.header("🛒 عرض المخزن - خصم وبيع المنتجات")
    st.write(
        "من هنا يمكنك استعراض المنتجات الحالية وخصم الكميات عند البيع مباشرة:"
    )

    # محاكاة لعرض منتج مع زر خصم الكمية
    st.markdown("---")
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.write("**اسم المنتج:** جهاز هاتف ذكي (مثال)")
    with col2:
        st.write("الكمية المتبقية: **5**")
    with col3:
        if st.button("بيع / خصم قطعة"):
            st.success("تم خصم قطعة واحدة بنجاح! المتبقي: 4")

# 6. الفواتير والتقارير
elif menu == "الفواتير والتقارير":
    st.header("📄 الفواتير والتقارير السابقة")
    st.write("عرض تفاصيل الفواتير والعمليات اليومية.")
