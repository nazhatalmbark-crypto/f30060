import streamlit as st
import pandas as pd

def main():
    # إعدادات الصفحة الأساسية
    st.set_page_config(page_title="منظومة Yasser Web", layout="wide")
    
    # تهيئة حالة الجلسة للتسجيل والحسابات الجديدة
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'users_db' not in st.session_state:
        # قاعدة بيانات بسيطة مخزنة مؤقتاً لتسجيل الحسابات الجديدة
        st.session_state['users_db'] = {"admin": "1234"}

    if not st.session_state['logged_in']:
        st.subheader("🔐 منظومة Yasser Web - بوابة الدخول")
        
        # تقسيم الشاشة إلى تبويبين (تسجيل دخول / إنشاء حساب جديد)
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])
        
        with tab1:
            st.markdown("### تسـجيل الدخول إلى الحساب")
            username = st.text_input("اسم المستخدم", key="login_user")
            password = st.text_input("كلمة المرور", type="password", key="login_pass")
            if st.button("دخول"):
                if username in st.session_state['users_db'] and st.session_state['users_db'][username] == password:
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.warning("اسم المستخدم أو كلمة المرور غير صحيحة")
                    
        with tab2:
            st.markdown("### إنشاء حساب جديد")
            new_user = st.text_input("اختر اسم المستخدم الجديد", key="new_user")
            new_pass = st.text_input("اختر كلمة المرور الجديدة", type="password", key="new_pass")
            if st.button("تسجيل الحساب"):
                if new_user and new_pass:
                    if new_user in st.session_state['users_db']:
                        st.warning("اسم المستخدم موجود مسبقاً، ياختر غيره")
                    else:
                        st.session_state['users_db'][new_user] = new_pass
                        st.success("تم إنشاء الحساب بنجاح! يمكنك الانتقال لتبويب تسجيل الدخول والدخول الآن.")
                else:
                    st.warning("يرجى ملء جميع الحقول المطلوبة")
        return

    # بيانات التطبيق الأصلية
    data = {
        'المنتج': ['تيشيرت كلاسيك', 'بنطلون جينز', 'حذاء رياضي', 'ساعة ذكية', 'ساعة ذكية'],
        'سعر البيع': [85.00, 405.00, 255.00, 155.00, 1355.00],
        'تكلفة الوحدة': [3.00, 0.00, 0.10, 0.00, 0.00],
        'الكمية المباعة': [1, 25, 230, 10, 250],
        'إجمالي الربح': [95900, 17400, 58950, 15300, 57500],
        'المخزون المتبقي': [41.50, 0.60, 0.50, 0.50, 0.50]
    }
    df_sales = pd.DataFrame(data)

    st.title("📊 منظومة Yasser Web - إدارة المبيعات والمخزون")
    st.markdown("---")

    # القائمة الجانبية الأصلية كاملة بدون أي حذف
    menu = st.sidebar.selectbox("القائمة الرئيسية", ["لوحة التحكم والأرباح", "إدارة الفواتير", "المخزون", "إدارة الموظفين", "إدارة المشاريع"])

    if menu == "لوحة التحكم والأرباح":
        st.subheader("تحليل الأرباح وتفاصيل المخزون - هذا الشهر")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(df_sales, use_container_width=True)
            
        with col2:
            st.markdown("### إجمالي الربح")
            st.success("إجمالي الربح المتوقع \n\n **+5.5%**")
            st.bar_chart(df_sales['إجمالي الربح'])

    elif menu == "إدارة الفواتير":
        # التعديل المطلوب على واجهة الفاتورة لتكون مرتبة
        st.markdown("### 📄 فاتورة المبيعات الرسمية")
        st.markdown("---")
        
        invoice_id = st.selectbox("اختر رقم الفاتورة للعرض:", df_sales.index.tolist() if not df_sales.empty else [1])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**معلومات المتجر:**")
            st.write("اسم النظام: منظومة Yasser Web")
            st.write("المطور: Eng. Yasser")
            st.write("المعرف: @yasser120120120120")
            
        with col2:
            st.markdown("**تفاصيل الفاتورة:**")
            st.write(f"رقم الفاتورة: #INV-{invoice_id}")
            st.write("الحالة: مدفوعة ومؤكدة ✅")
            
        st.markdown("---")
        st.markdown("#### 🛒 المواد المباعة:")
        if not df_sales.empty:
            st.dataframe(df_sales[['المنتج', 'سعر البيع', 'الكمية المباعة', 'إجمالي الربح']], use_container_width=True)
        else:
            st.info("لا توجد بيانات متاحة لعرضها في الفاتورة حالياً.")
            
        st.markdown("---")
        st.success("شكراً لتعاملكم معنا! لخدمة أفضل، يرجى مراجعة الإدارة عند وجود أي استفسار.")

    elif menu == "المخزون":
        st.subheader("إدارة المخزون الحالي")
        st.dataframe(df_sales[['المنتج', 'المخزون المتبقي']], use_container_width=True)

    elif menu == "إدارة الموظفين":
        st.subheader("قسم إدارة الموظفين والأداء")
        st.write("عرض تفاصيل الموظفين والتقييمات الشهرية...")
        st.dataframe(df_sales, use_container_width=True)

    elif menu == "إدارة المشاريع":
        st.subheader("قسم إدارة المشاريع وتطوير التطبيقات")
        st.write("متابعة حالة المشاريع ونسب الإنجاز الحالية...")
        st.progress(0.75)
        st.write("نسبة إنجاز المشروع الحالي: 75%")

    # زر تسجيل الخروج الأصلي
    st.sidebar.markdown("---")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()

if __name__ == '__main__':
    main()
