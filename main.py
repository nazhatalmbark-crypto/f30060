import streamlit as st

def show_guide_page():
    # تنسيق عام لجعل الواجهة متجاوبة وجميلة على الموبايل والحاسبة
    st.markdown("""
        <style>
        .guide-container {
            padding: 10px;
        }
        .guide-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-right: 5px solid #ff4b4b;
        }
        .contact-box {
            background-color: #e3f2fd;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='guide-container'>", unsafe_allow_html=True)
    
    st.title("📖 دليل الاستخدام وطرق التواصل - نظام ياسر ويب")
    st.write("مرحباً بك في الدليل الشامل لنظام إدارة المبيعات والمخزن. هنا شرح مبسط لكل خانة وقسم في التطبيق لتعرف كيفية إدارته بكل سهولة.")

    st.markdown("---")

    # شرح الأقسام
    st.markdown("### 🔍 شروحات أقسام النظام")

    with st.container():
        st.markdown("""
        <div class='guide-card'>
            <h4>1. قائمة المبيعات (Sales & Invoices)</h4>
            <p>من خلال هذه الخانة يمكنك إتمام عمليات البيع، اختيار المنتجات من المخزن، تحديد الكميات، وإصدار الفواتير بشكل فوري مع حساب الإجماليات والخصومات تلقائياً.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='guide-card'>
            <h4>2. إدارة المخزن والمنتجات (Inventory)</h4>
            <p>تستطيع إضافة منتجات جديدة، تعديل الأسعار، ومراقبة الكميات المتوفرة. النظام يدعم الباركود لتسهيل عملية البحث وإضافة المواد بسرعة وسهولة.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='guide-card'>
            <h4>3. إدارة الديون والزبونات (Customers & Debts)</h4>
            <p>تخصيص مكان لتسجيل أسماء الزبائن، المبالغ المدفوعة، والمبالغ المتبقية (الديون) لتتمكن من متابعة الحسابات بدقة دون ضياع أي حق.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='guide-card'>
            <h4>4. تقارير الأرباح والحسابات (Reports)</h4>
            <p>عرض ملخص شامل لحركة المبيعات خلال اليوم أو الفترة المحددة لمعرفة صافي الدخل وحجم البضاعة المباعة.</p>
        </div>
        """, unsafe_allow_html=True)

    # طرق التواصل والدعم
    st.markdown("---")
    st.markdown("""
    <div class='contact-box'>
        <h3>📞 طرق التواصل والدعم الفني</h3>
        <p>إذا واجهتك أي مشكلة برمجية، أو أردت تعديل أو إضافة ميزات جديدة للنظام، يمكنك التواصل مباشرة عبر:</p>
        <p><b>مطور النظام:</b> ياسر</p>
        <p><b>تيليجرام الرسمي:</b> <a href="https://t.me/" target="_blank">تواصل عبر تيليجرام</a></p>
        <p><b>المدينة:</b> العراق - البصرة</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    show_guide_page()
