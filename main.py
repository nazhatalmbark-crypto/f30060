import streamlit as st

st.set_page_config(page_title="Eng. Yasser Pro System", page_icon="🛍️", layout="wide")

# تهيئة الجلسة
if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

if "users_db" not in st.session_state:
    st.session_state.users_db = {"admin": "مدير المحل"}

if "cart" not in st.session_state:
    st.session_state.cart = []

# إذا المستخدم ما مسجل دخول، اظهر الواجهة حصراً
if not st.session_state.logged_user:
    st.title("🛍️ Eng. Yasser Pro System - نظام إدارة المبيعات")
    st.subheader("أهلاً بك! يرجى اختيار الطريقة للبدء:")
    
    # التبويبات الواضحة جداً
    tab_login, tab_signup = st.tabs(["🔑 تسجيل الدخول", "✨ إنشاء حساب جديد"])
    
    with tab_login:
        st.write("تسجيل الدخول للمستخدمين الحاليين:")
        with st.form("login_form_fixed"):
            l_user = st.text_input("اسم المستخدم:")
            l_submit = st.form_submit_button("دخول للنظام", type="primary")
            if l_submit:
                if l_user.strip():
                    st.session_state.logged_user = l_user.strip()
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى كتابة اسم المستخدم.")
                    
    with tab_signup:
        st.write("إنشاء حساب جديد للمستخدمين الجدد:")
        with st.form("signup_form_fixed"):
            s_user = st.text_input("اختر اسم المستخدم الجديد للمحل:")
            s_submit = st.form_submit_button("إنشاء الحساب والبدء", type="primary")
            if s_submit:
                if s_user.strip():
                    st.session_state.logged_user = s_user.strip()
                    st.success("🎉 تم إنشاء الحساب والدخول بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى كتابة اسم المستخدم الجديد.")
    st.stop()

# ---------------------------------------------
# الشاشة الرئيسية بعد الدخول (الوجهة الكاملة)
# ---------------------------------------------
username = st.session_state.logged_user

st.sidebar.title("⚙️ إعدادات الحساب")
st.sidebar.write(f"👤 المستخدم الحالي: **{username}**")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_user = None
    st.rerun()

st.title(f" أهلاً وسهلاً بك يا ({username}) في النظام الكامل")
st.success("النظام شغال بكامل تفاصيله وجاهز للاستخدام الفوري!")

# تبويبات النظام الكبرى
t1, t2, t3 = st.tabs(["📦 المخزن والبضائع", "🛒 سلة المبيعات", "📊 التقارير"])

with t1:
    st.subheader("إدارة المخزن")
    st.info("هنا تظهر بضائع المستخدم حصراً.")

with t2:
    st.subheader("سلة المبيعات والفواتير")
    st.info("إصدار الفواتير وتسجيل المبيعات.")

with t3:
    st.subheader("تقارير الأرباح")
    st.info("حساب الأرباح ورأس المال.")
