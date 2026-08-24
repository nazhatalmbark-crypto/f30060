import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import urllib.request
import arabic_reshaper
from bidi.algorithm import get_display

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web - إدارة المبيعات والمخزون", page_icon="📦", layout="wide")

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "customer_list" not in st.session_state:
    st.session_state.customer_list = []

if "invoices_list" not in st.session_state:
    st.session_state.invoices_list = []

if "cart" not in st.session_state:
    st.session_state.cart = []

if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

@st.cache_resource
def register_arabic_font():
    try:
        font_url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
        font_path = "Amiri-Regular.ttf"
        urllib.request.urlretrieve(font_url, font_path)
        pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
        return True
    except Exception:
        return False

font_registered = register_arabic_font()

def fix_arabic(text):
    if not text:
        return ""
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return text

def generate_pdf_invoice(inv):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    f_name = 'ArabicFont' if font_registered else 'Helvetica'
    
    p.setFont(f_name, 18)
    p.drawCentredString(width / 2.0, height - 50, fix_arabic("نظام ياسر وب - فاتورة مبيعات"))
    p.setFont(f_name, 12)
    p.drawString(width - 200, height - 90, fix_arabic(f"رقم الفاتورة: {inv['رقم الفاتورة']}"))
    p.drawString(width - 200, height - 115, fix_arabic(f"اسم الزبون: {inv['الزبون']}"))
    p.drawString(width - 200, height - 140, fix_arabic(f"التاريخ: {inv['التاريخ']}"))
    p.drawString(width - 200, height - 165, fix_arabic(f"نوع الدفع: {inv['نوع الدفع']}"))
    p.line(50, height - 180, width - 50, height - 180)
    
    p.setFont(f_name, 13)
    p.drawString(width - 220, height - 210, fix_arabic("المنتجات والمواد المباعة:"))
    
    p.setFont(f_name, 11)
    text_y = height - 235
    for prod_line in inv['المنتجات'].split(" , "):
        p.drawString(width - 240, text_y, fix_arabic(f"- {prod_line}"))
        text_y -= 25
    
    text_y -= 15
    p.line(50, text_y, width - 50, text_y)
    text_y -= 30
    p.setFont(f_name, 12)
    p.drawString(width - 250, text_y, fix_arabic(f"المبلغ الكلي: {inv['المبلغ الكلي']:,} د.ع"))
    text_y -= 25
    p.drawString(width - 250, text_y, fix_arabic(f"المبلغ الواصل: {inv['الواصل']:,} د.ع"))
    text_y -= 25
    p.drawString(width - 250, text_y, fix_arabic(f"المتبقي (الدين): {inv['المتبقي (الدين)']:,} د.ع"))
    text_y -= 35
    p.line(50, text_y, width - 50, text_y)
    p.setFont(f_name, 10)
    p.drawCentredString(width / 2.0, text_y - 30, fix_arabic("شكراً لتعاملكم مع نظام Yasser Web"))
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

st.title("🛍️ نظام Yasser Web لإدارة المبيعات والمخزون")

if not st.session_state.logged_in_user:
    st.subheader("🔐 بوابة الدخول وإنشاء حساب جديد للمحل")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 تسجيل الدخول", "✨ إنشاء حساب جديد"])
    
    with auth_tab1:
        with st.form("login_form"):
            login_user = st.text_input("اسم المستخدم أو اسم المحل:")
            login_submitted = st.form_submit_button("تسجيل الدخول", type="primary")
            if login_submitted:
                if login_user.strip():
                    try:
                        res = supabase.table("users").select("*").eq("username", login_user.strip()).execute()
                        if res.data:
                            st.session_state.logged_in_user = res.data[0]["username"]
                            st.session_state.is_vip = bool(res.data[0].get("is_paid", False))
                            st.success("تم تسجيل الدخول بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ اسم المستخدم غير موجود، يرجى إنشاء حساب جديد.")
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
                    
    with auth_tab2:
        with st.form("signup_form"):
            new_user = st.text_input("اختر اسم المستخدم أو اسم المحل الجديد:")
            signup_submitted = st.form_submit_button("إنشاء الحساب الجديد الآن", type="primary")
            if signup_submitted:
                if new_user.strip():
                    try:
                        check_res = supabase.table("users").select("*").eq("username", new_user.strip()).execute()
                        if check_res.data:
                            st.error("❌ اسم المستخدم هذا مستخدم مسبقاً، اختر غيره.")
                        else:
                            supabase.table("users").insert({"username": new_user.strip(), "is_paid": False}).execute()
                            st.session_state.logged_in_user = new_user.strip()
                            st.session_state.is_vip = False
                            st.success("🎉 تم إنشاء الحساب والدخول بنجاح!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"خطأ في إنشاء الحساب: {e}")
                else:
                    st.warning("يرجى كتابة اسم المستخدم الجديد.")
    st.stop()

# إذا مسجل دخول، اعرض التطبيق الكامل
username = st.session_state.logged_in_user
st.sidebar.title("⚙️ الإعدادات")
st.sidebar.write(f"👤 المستخدم: **{username}**")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in_user = None
    st.rerun()

st.success(f"أهلاً بك يا مبدع ({username}) في نظامك!")
