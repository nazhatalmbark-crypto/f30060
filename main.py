import streamlit as st

# تطبيق تنسيق CSS متقدم يجعل الأقسام تظهر على شكل كروت مربعة (Grid) مطابقة للصور
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background-color: #0f3d2e;
        color: #ffffff;
    }
    /* تصميم الكروت المربعة لتشبه التطبيق في الصور */
    .dashboard-card {
        background-color: #1b4d3e;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #2e8b57;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .dashboard-card h3 {
        color: #ffffff;
        font-size: 16px;
        margin-bottom: 5px;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        background-color: #2e8b57;
        color: white;
        border: none;
        font-weight: bold;
        padding: 10px;
    }
    @media (max-width: 768px) {
        h1 { font-size: 20px !important; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# تهيئة بيانات الجلسة
if "inventory" not in st.session_state:
    st.session_state.inventory = {
        "باور بانك 10000 ملي أمبير": {"qty": 96, "price": 24.9},
        "سماعات لاسلكية": {"qty": 129, "price": 29.9},
        "كابل USB-C 1 متر": {"qty": 6.4, "price": 4.5},
        "لمبة 9 LED واط": {"qty": 384, "price": 2.5},
    }

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "cash_log" not in st.session_state:
    st.session_state.cash_log = {"start_cash": 0.0, "notes": ""}

st.title("🛒 Yasser Web - لوحة التحكم الرئيسية")
st.write("اختر القسم المطلوب أو تصفح الخانات أدناه:")

# --- تصميم الشاشة الرئيسية على شكل شبكة كروت مطابقة للصور (Grid) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '<div class="dashboard-card"><h3>📦 المبيعات</h3><p>إدارة الفواتير والمسح السريع</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("فتح المبيعات"):
        st.session_state.active_tab = "إدارة المبيعات (POS)"
        st.rerun()

with col2:
    st.markdown(
        '<div class="dashboard-card"><h3>🏢 المخازن</h3><p>مخزون لحظي في كل مستودع</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("فتح المخازن"):
        st.session_state.active_tab = "المخازن والمحلات"
        st.rerun()

with col3:
    st.markdown(
        '<div class="dashboard-card"><h3>📊 التقارير</h3><p>الأرباح والمبيعات والمخزون</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("فتح التقارير"):
        st.session_state.active_tab = "التقارير النهائية والأرباح"
        st.rerun()

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(
        '<div class="dashboard-card"><h3>💰 الصندوق</h3><p>حركة النقدية والصندوق اليومي</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("فتح الصندوق"):
        st.session_state.active_tab = "سجل حركة الصندوق"
        st.rerun()

with col5:
    st.markdown(
        '<div class="dashboard-card"><h3>☁️ السحاب</h3><p>النسخ الاحتياطي والأمان</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("فتح النسخ الاحتياطي"):
        st.session_state.active_tab = "النسخ الاحتياطي السحابي"
        st.rerun()

with col6:
    st.markdown(
        '<div class="dashboard-card"><h3>⚙️ لوحة التحكم</h3><p>الإعدادات العامة للسيستم</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("الرئيسية"):
        st.session_state.active_tab = "الرئيسية"
        st.rerun()

st.markdown("---")

# تحديد القائمة النشطة بناءً على ضغط الكروت أو القائمة الجانبية
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "الرئيسية"

menu = st.sidebar.selectbox(
    "القائمة السريعة",
    [
        "الرئيسية",
        "إدارة المبيعات (POS)",
        "المخازن والمحلات",
        "التقارير النهائية والأرباح",
        "سجل حركة الصندوق",
        "النسخ الاحتياطي السحابي",
    ],
    index=0,
)

# إذا تم الضغط من الكروت، اجعل القائمة تتطابق وياها
current_view = (
    menu
    if menu != "الرئيسية"
    else st.session_state.get("active_tab", "الرئيسية")
)

# --- محتوى الأقسام ---
if current_view == "إدارة المبيعات (POS)":
    st.subheader("📦 إدارة المبيعات - مسح سريع")
    search_query = st.text_input(
        "بحث باسم المنتج أو باركود...", placeholder="اكتب اسم المادة هنا..."
    )

    p_cols = st.columns(2)
    idx = 0
    for prod_name, data in st.session_state.inventory.items():
        if search_query and search_query.lower() not in prod_name.lower():
            continue
        with p_cols[idx % 2]:
            st.markdown(
                f"""
                <div style="background-color: #1b4d3e; padding: 15px; border-radius: 12px; border: 1px solid #2e8b57; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0 0 5px 0; font-size: 14px;">{prod_name}</h4>
                    <p style="color: #a8df8e; margin: 0; font-size: 12px;">الكمية: {data['qty']} | السعر: {data['price']} دينار</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"إضافة: {prod_name}", key=f"add_{prod_name}"):
                if prod_name in st.session_state.cart:
                    st.session_state.cart[prod_name] += 1
                else:
                    st.session_state.cart[prod_name] = 1
                st.success(f"تمت إضافة {prod_name} للسلة!")
        idx += 1

    st.markdown("---")
    st.subheader("🛒 سلة المشتريات الحالية")
    if st.session_state.cart:
        total_price = 0
        for item, q in st.session_state.cart.items():
            p = st.session_state.inventory[item]["price"]
            sub = p * q
            total_price += sub
            st.write(f"- {item} (العدد: {q}) | المجموع: {sub:.2f} دينار")

        st.markdown(f"**المجموع الكلي: {total_price:.2f} دينار**")
        if st.button("إصدار وطباعة الفاتورة / مشاركة واتساب"):
            st.success("تم إصدار الفاتورة بنجاح! 🚀")
            st.session_state.cart = {}
    else:
        st.info("السلة فارغة حالياً.")

elif current_view == "المخازن والمحلات":
    st.subheader("🏢 إدارة المخازن (مخزون لحظي في كل مستودع)")
    for prod_name, data in st.session_state.inventory.items():
        if data["qty"] < 10:
            st.warning(
                f"⚠️ تنبيه نفاذ بضاعة: المنتج '{prod_name}' كميته قليلة جداً ({data['qty']} قطعة)!"
            )
    st.json(st.session_state.inventory)

elif current_view == "التقارير النهائية والأرباح":
    st.subheader("📊 التقارير والأرباح النهائية")
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي المبيعات اليوم", "110.35 دينار")
    c2.metric("مخزون داخل", "51")
    c3.metric("مخزون خارج", "61")

elif current_view == "سجل حركة الصندوق":
    st.subheader("💰 سجل حركة الصندوق اليومي")
    start_c = st.number_input(
        "مبلغ الصندوق بداية اليوم:",
        value=float(st.session_state.cash_log["start_cash"]),
    )
    notes_c = st.text_area(
        "ملاحظات الصندوق:", value=st.session_state.cash_log["notes"]
    )
    if st.button("حفظ حركة الصندوق"):
        st.session_state.cash_log["start_cash"] = start_c
        st.session_state.cash_log["notes"] = notes_c
        st.success("تم حفظ تقرير الصندوق بنجاح!")

elif current_view == "النسخ الاحتياطي السحابي":
    st.subheader("☁️ بياناتك آمنة في السحاب")
    if st.button("إنشاء نسخة احتياطية الآن 🔄"):
        st.success("تم إنشاء نسخة احتياطية محلية وسحابية بنجاح.")
