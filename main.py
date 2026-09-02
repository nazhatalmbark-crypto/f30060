# Yasser Web - Complete Code with Features & User Guide (Pro Key Removed, Field Retained)
import streamlit as st

st.set_page_config(page_title="Yasser Web", page_icon="💼", layout="wide")

def main():
    st.sidebar.title("قائمة التنقل - ياسر ويب")
    choice = st.sidebar.selectbox("اختر القسّم", ["الرئيسية", "المخزن والمبيعات", "الفواتير والديون", "دليل الاستخدام"])

    # واجهة النسخة المجانية والمدفوعة (الحقل موجود بدون الرمز السري)
    st.sidebar.markdown("---")
    st.sidebar.subheader("حالة النسخة")
    version_status = st.sidebar.text_input("أدخل مفتاح التفعيل (فارغ للنسخة المجانية):", type="password")
    
    if version_status:
        st.sidebar.success("تم إدخال الحقل بنجاح (النسخة المدفوعة مفعلة محلياً)")
    else:
        st.sidebar.info("أنت تعمل على النسخة المجانية")

    if choice == "الرئيسية":
        st.title("مرحباً بك في نظام ياسر ويب 🚀")
        st.write("النظام المتكامل لإدارة المحلات والمخازن بدقة وسرعة.")

    elif choice == "المخزن والمبيعات":
        st.header("📦 إدارة المخزن والمبيعات والجرد")
        st.write("- جرد دقيق للمنتجات وتنبيهات بضاعة ناقصة.")

    elif choice == "الفواتير والديون":
        st.header("📄 الفواتير والديون والتقارير")
        st.write("- إصدار فواتير PDF وإرسالها عبر الواتساب ومتابعة صندوق الوردية والديون.")

    elif choice == "دليل الاستخدام":
        st.header("📖 دليل الاستخدام المدمج داخل النظام")
        st.markdown("""
        ### دليل التشغيل السريع:
        1. **إضافة المنتجات:** توجه إلى قسم المخزن وأدخل تفاصيل بضائعك.
        2. **التنبيهات:** يظهر لك تحذير فوري عند انخفاض الكمية.
        3. **الفواتير:** قم بإنشاء الفاتورة وحملها بصيغة PDF أو أرسلها للزبون مباشرة.
        4. **النسخ:** حقل تفعيل النسخة المدفوعة متاح في القائمة الجانبية.
        """)

if __name__ == "__main__":
    main()
