import streamlit as st

# إعدادات الصفحة الأساسية لتكون واسعة وملائمة لكل الشاشات
st.set_page_config(
    page_title="نظام ياسر ويب",
    layout="wide",
    initial_sidebar_state="expanded"
)

# كود الـ CSS النهائي والجذري لمنع تكسير الحروف وحل المشكلة على شاشات الحاسبة والموبايل
st.markdown("""
    <style>
    /* فرض الاتجاه الصحيح لكل التطبيق وحل مشكلة الحروف العمودية */
    .stApp {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* توسيع القائمة الجانبية بالحاسبة ومنع أي تداخل بالنصوص */
    section[data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
        min-width: 320px !important;
    }
    
    /* السماح للكلمات بالالتفاف الطبيعي ومنع النزول الطولي للحروف في أزرار القائمة */
    section[data-testid="stSidebar"] .stRadio label div,
    section[data-testid="stSidebar"] .stRadio label p,
    section[data-testid="stSidebar"] span {
        direction: rtl !important;
        text-align: right !important;
        white-space: normal !important;
        word-break: normal !important;
        font-size: 15px !important;
    }
    
    /* تنسيق حاوية خيارات الروابط لضمان عدم تداخلها */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# هيكل التطبيق الرئيسي (نظام ياسر ويب)
# ---------------------------------------------------------

st.sidebar.title("📦 نظام ياسر ويب")
st.sidebar.markdown("---")

# القائمة الجانبية
menu = st.sidebar.radio(
    "اختر القسم:",
    [
        "🏠 الرئيسية",
        "📊 إدارة المخزن والمبيعات",
        "👥 إدارة الزبائن",
        "📄 التقارير المالية",
        "⚙️ الإعدادات"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("الإصدار: 2.0 | متصل بقاعدة البيانات")

# محتوى الصفحة بناءً على الاختيار
if menu == "🏠 الرئيسية":
    st.title("أهلاً بك في لوحة تحكم نظام ياسر ويب")
    st.write("هنا تظهر الإحصائيات العامة للمبيعات والحركة اليومية.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("مبيعات اليوم", "0 د.ع", "0%")
    with col2:
        st.metric("عدد الزبائن", "0", "0")
    with col3:
        st.metric("المواد في المخزن", "0", "0")

elif menu == "📊 إدارة المخزن والمبيعات":
    st.title("إدارة المخزن والمبيعات")
    st.write("قسم إضافة المواد، تسجيل المبيعات، وإصدار الفواتير.")

elif menu == "👥 إدارة الزبائن":
    st.title("إدارة الزبائن")
    st.write("قائمة الزبائن، الحسابات، والديون.")

elif menu == "📄 التقارير المالية":
    st.title("التقارير المالية")
    st.write("عرض الأرباح، التقارير اليومية والشهرية.")

elif menu == "⚙️ الإعدادات":
    st.title("إعدادات النظام")
    st.write("تعديل إعدادات الربط والواتساب.")
