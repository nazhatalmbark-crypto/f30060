import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Yasser Pro System", page_icon="🛍️", layout="wide")

# تهيئة الـ Session State
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "users_db" not in st.session_state:
    st.session_state.users_db = {"ياسر": "admin"} # حساب تجريبي أولي

if "customer_list" not in st.session_state:
    st.session_state.customer_list = []

if "invoices_list" not in st.session_state:
    st.session_state.invoices_list = []

if "cart" not in st.session_state:
    st.session_state.cart = []

if "products_db" not in st.session_state:
    st.session_state.products_db = [
        {"id": 1, "name": "منتج تجريبي 1", "buy": 1000, "sell": 1500, "qty": 10}
    ]

# شاشة تسجيل الدخول وإنشاء الحساب
if not st.session_state.logged_in_user:
    st.title("🛍️ Eng. Yasser Pro System")
    st.subheader("بوابة الدخول إلى النظام")
    
    tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "✨ إنشاء حساب جديد"])
    
    with tab1:
        with st.form("login_form"):
            username_input = st.text_input("اسم المستخدم:")
            submitted_login = st.form_submit_button("دخول", type="primary")
            
            if submitted_login:
                if username_input.strip():
                    st.session_state.logged_in_user = username_input.strip()
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
                    
    with tab2:
        with st.form("signup_form"):
            new_user_input = st.text_input("اختر اسم المستخدم الجديد:")
            submitted_signup = st.form_submit_button("إنشاء حساب جديد", type="primary")
            
            if submitted_signup:
                if new_user_input.strip():
                    st.session_state.logged_in_user = new_user_input.strip()
                    st.success("تم إنشاء الحساب وتسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى إدخال اسم المستخدم الجديد.")
    st.stop()

# واجهة النظام الرئيسية بعد تسجيل الدخول
username = st.session_state.logged_in_user

st.sidebar.title("⚙️ الإعدادات")
st.sidebar.write(f"👤 المستخدم الحالي: **{username}**")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in_user = None
    st.rerun()

st.title(f" أهلاً بك يا {username} في نظام إدارة المبيعات والمخزون")

# التبويبات الرئيسية للتطبيق
tab_p1, tab_p2, tab_p3 = st.tabs(["➕ إضافة منتج", "📦 عرض المخزن", "🛒 المبيعات"])

with tab_p1:
    st.subheader("إضافة مادة جديدة للمخزن")
    with st.add_form if hasattr(st, 'form') else st.form("add_p"):
        p_name = st.text_input("اسم المادة:")
        p_buy = st.number_input("سعر الشراء:", min_value=0.0, value=1000.0)
        p_sell = st.number_input("سعر البيع:", min_value=0.0, value=1500.0)
        p_qty = st.number_input("الكمية:", min_value=1, value=10)
        
        if st.form_submit_button("حفظ المادة"):
            if p_name:
                st.session_state.products_db.append({
                    "id": len(st.session_state.products_db) + 1,
                    "name": p_name,
                    "buy": p_buy,
                    "sell": p_sell,
                    "qty": p_qty
                })
                st.success(f"تمت إضافة ({p_name}) للمخزن بنجاح!")
            else:
                st.warning("يرجى كتابة اسم المادة.")

with tab_p2:
    st.subheader("مخزن المحل الحالي")
    if st.session_state.products_db:
        df_prod = pd.DataFrame(st.session_state.products_db)
        st.dataframe(df_prod, use_container_width=True)
    else:
        st.info("المخزن فارغ حالياً.")

with tab_p3:
    st.subheader("قسم البيع السريع")
    st.info("جاهز لإتمام عمليات البيع وإصدار الفواتير.")
