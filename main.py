import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="Eng. Yasser Pro System",
    page_icon="🔓",
    layout="wide"
)

# شريط جانبي
st.sidebar.title("إدارة المستخدم")
user_name = st.sidebar.text_input("اسم المستخدم الحالي", "ياسر")
st.sidebar.success(f"مرحباً بك، {user_name}")

# العنوان الرئيسي
st.title("🔐 Eng. Yasser Pro System")

# رسالة الترحيب والحالة
st.markdown(
    f"""
    <div style="padding: 10px; background-color: #d4edda; color: #155724; border-radius: 5px; margin-bottom: 20px;">
    أهلاً وسهلاً بك يا ({user_name}) في النظام الكامل!<br>
    <b>النظام شغال بكامل تفاصيله وجاهز للاستخدام الفوري!</b>
    </div>
    """,
    unsafe_allow_html=True
)

# تبويبات النظام الرئيسية
tab_reports, tab_sales, tab_inventory, tab_pro = st.tabs([
    "📊 التقارير", 
    "🛒 سلة المبيعات", 
    "📦 المخزن والبضائع", 
    "🔑 تفعيل النسخة المدفوعة"
])

with tab_reports:
    st.subheader("تقارير المبيعات والأرباح")
    st.info("هنا تظهر تقارير الحركة المالية والتحليلات الخاصة بالمخزن.")
    st.metric(label="إجمالي المبيعات", value="0 د.ع", delta="0%")

with tab_sales:
    st.subheader("إدارة سلة المبيعات والفواتير")
    st.write("قم بإتمام عمليات البيع وإصدار الفواتير للزبائن بسهولة.")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("اسم الزبون")
    with col2:
        st.number_input("المبلغ الإجمالي", min_value=0, step=1000)
    st.button("إصدار وطباعة الفاتورة", type="primary")

with tab_inventory:
    st.subheader("إدارة المخزن")
    st.info("هنا تظهر بضائع المستخدم حصراً.")
    st.text_input("بحث عن مادة في المخزن...")
    st.write("قائمة البضائع الحالية فارغة حالياً، أضف بضائع جديدة.")

with tab_pro:
    st.subheader("إدخال كود النسخة المدفوعة / الاحترافية")
    st.write("أدخل الكود الخاص لفتح كافة ميزات النظام المتقدمة:")
    
    activation_code = st.text_input("حقل إدخال الكود السري:", type="password")
    
    if st.button("تحقق وتفعيل النسخة"):
        if activation_code == "YASSER2026":
            st.success("🎉 مبروك! تم تفعيل النسخة المدفوعة بنجاح كامل.")
            st.balloons()
        elif activation_code == "":
            st.warning("الرجاء إدخال الكود أولاً.")
        else:
            st.error("❌ الكود غير صحيح، تأكد من الرقم وادخله مجدداً.")

# فاصل سفلي
st.divider()
st.caption("Eng. Yasser Pro System - النسخة الاحترافية المحلية 2026")
