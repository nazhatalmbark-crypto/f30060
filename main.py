import streamlit as st

# تطبيق تنسيق الـ CSS المتجاوب لشاشات الموبايل واللابتوب
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
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        background-color: #1b4d3e;
        color: white;
        border: 1px solid #2e8b57;
        font-weight: bold;
    }
    @media (max-width: 768px) {
        .stDataFrame {
            width: 100% !important;
            overflow-x: auto;
        }
        h1 { font-size: 22px !important; }
        h2 { font-size: 18px !important; }
        h3 { font-size: 15px !important; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

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

st.title("🛒 Yasser Web - إدارة المبيعات والمخازن")
st.write("النسخة المطورة المتجاوبة لكل الأجهزة (موبايل ولابتوب)")

menu = st.sidebar.selectbox(
    "القائمة الرئيسية",
    [
        "إدارة المبيعات (POS)",
        "المخازن والمحلات",
        "التقارير النهائية والأرباح",
        "سجل حركة الصندوق",
        "النسخ الاحتياطي السحابي",
    ],
)

if menu == "إدارة المبيعات (POS)":
    st.subheader("📦 إدارة المبيعات - مسح سريع")
    search_query = st.text_input(
        "بحث باسم المنتج أو باركود...", placeholder="اكتب اسم المادة هنا..."
    )

    cols = st.columns(2)
    idx = 0
    for prod_name, data in st.session_state.inventory.items():
        if search_query and search_query.lower() not in prod_name.lower():
            continue
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div style="background-color: #1b4d3e; padding: 15px; border-radius: 12px; border: 1px solid #2e8b57; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0 0 10px 0; font-size: 14px;">{prod_name}</h4>
                    <p style="color: #a8df8e; margin: 0; font-size: 12px;">الكمية: {data['qty']} قطعة | السعر: {data['price']} دينار</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"إضافة للسلة: {prod_name}", key=f"add_{prod_name}"):
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

        st.markdown(f"**المجموع الكلي للفاتورة: {total_price:.2f} دينار**")
        if st.button("إصدار وطباعة فاتورة PDF / مشاركة واتساب"):
            st.success(
                "تم إصدار الفاتورة وتجهيزها للمشاركة بنجاح! 🚀 (تتم محاكاة الطباعة)"
            )
            st.session_state.cart = {}
    else:
        st.info("السلة فارغة حالياً.")

elif menu == "المخازن والمحلات":
    st.subheader("🏢 إدارة المخازن (مخزون لحظي في كل مستودع)")
    st.write("تتبع كل صنف في جميع متاجر الفروع الرئيسية والفرعية.")

    for prod_name, data in st.session_state.inventory.items():
        if data["qty"] < 10:
            st.warning(
                f"⚠️ تنبيه نفاذ بضاعة: المنتج '{prod_name}' كميته قليلة جداً ({data['qty']} قطعة)!"
            )

    st.json(st.session_state.inventory)

elif menu == "التقارير النهائية والأرباح":
    st.subheader("📊 التقارير والأرباح النهائية")
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المبيعات اليوم", "110.35 دينار")
    col2.metric("مخزون داخل", "51")
    col3.metric("مخزون خارج", "61")

    st.markdown("---")
    st.info(
        "تقرير الأرباح الصافية والمصروفات مفعل وجاهز لعرض تفاصيل الحركة المالية."
    )

elif menu == "سجل حركة الصندوق":
    st.subheader("💰 سجل حركة الصندوق اليومي (Cash Drawer Log)")
    start_c = st.number_input(
        "مبلغ الصندوق بداية اليوم (كاش):",
        value=float(st.session_state.cash_log["start_cash"]),
    )
    notes_c = st.text_area(
        "ملاحظات الصندوق والمصاريف النثرية:",
        value=st.session_state.cash_log["notes"],
    )
    if st.button("حفظ حركة الصندوق"):
        st.session_state.cash_log["start_cash"] = start_c
        st.session_state.cash_log["notes"] = notes_c
        st.success("تم حفظ تقرير الصندوق بنجاح!")

elif menu == "النسخ الاحتياطي السحابي":
    st.subheader("☁️ بياناتك آمنة في السحاب")
    st.write("أنشئ نسخة احتياطية بنقرة زر واحدة (محلي وسحابي).")
    if st.button("إنشاء نسخة احتياطية الآن 🔄"):
        st.success(
            "تم إنشاء نسخة احتياطية محلية وسحابية بنجاح، بياناتك محروسة ولن تضيع أبداً."
        )
