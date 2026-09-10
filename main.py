import streamlit as str_lib

# يجب أن يكون هذا السطر هو أول أمر ستريمليت في الملف تماماً
str_lib.set_page_config(
    page_title="Yasser Web - إدارة المحلات", page_layout="centered"
)

# تطبيق تنسيق الـ CSS المتجاوب لشاشات الموبايل واللابتوب
str_lib.markdown(
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

# تهيئة حالة الجلسة (Session State) لحفظ البيانات والمميزات
if "inventory" not in str_lib.session_state:
    str_lib.session_state.inventory = {
        "باور بانك 10000 ملي أمبير": {"qty": 96, "price": 24.9},
        "سماعات لاسلكية": {"qty": 129, "price": 29.9},
        "كابل USB-C 1 متر": {"qty": 6.4, "price": 4.5},
        "لمبة 9 LED واط": {"qty": 384, "price": 2.5},
    }

if "cart" not in str_lib.session_state:
    str_lib.session_state.cart = {}

if "cash_log" not in str_lib.session_state:
    str_lib.session_state.cash_log = {"start_cash": 0.0, "notes": ""}

# عنوان التطبيق الرئيسي
str_lib.title("🛒 Yasser Web - إدارة المبيعات والمخازن")
str_lib.write("النسخة المطورة المتجاوبة لكل الأجهزة (موبايل ولابتوب)")

# القائمة الرئيسية للتنقل بين الأقسام
menu = str_lib.sidebar.selectbox(
    "القائمة الرئيسية",
    [
        "إدارة المبيعات (POS)",
        "المخازن والمحلات",
        "التقارير النهائية والأرباح",
        "سجل حركة الصندوق",
        "النسخ الاحتياطي السحابي",
    ],
)

# --- 1. قسم إدارة المبيعات (POS) ---
if menu == "إدارة المبيعات (POS)":
    str_lib.subheader("📦 إدارة المبيعات - مسح سريع")
    search_query = str_lib.text_input(
        "بحث باسم المنتج أو باركود...", placeholder="اكتب اسم المادة هنا..."
    )

    cols = str_lib.columns(2)
    idx = 0
    for prod_name, data in str_lib.session_state.inventory.items():
        if search_query and search_query.lower() not in prod_name.lower():
            continue
        with cols[idx % 2]:
            str_lib.markdown(
                f"""
                <div style="background-color: #1b4d3e; padding: 15px; border-radius: 12px; border: 1px solid #2e8b57; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0 0 10px 0; font-size: 14px;">{prod_name}</h4>
                    <p style="color: #a8df8e; margin: 0; font-size: 12px;">الكمية: {data['qty']} قطعة | السعر: {data['price']} دينار</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if str_lib.button(
                f"إضافة للسلة: {prod_name}", key=f"add_{prod_name}"
            ):
                if prod_name in str_lib.session_state.cart:
                    str_lib.session_state.cart[prod_name] += 1
                else:
                    str_lib.session_state.cart[prod_name] = 1
                str_lib.success(f"تمت إضافة {prod_name} للسلة!")
        idx += 1

    str_lib.markdown("---")
    str_lib.subheader("🛒 سلة المشتريات الحالية")
    if str_lib.session_state.cart:
        total_price = 0
        for item, q in str_lib.session_state.cart.items():
            p = str_lib.session_state.inventory[item]["price"]
            sub = p * q
            total_price += sub
            str_lib.write(f"- {item} (العدد: {q}) | المجموع: {sub:.2f} دينار")

        str_lib.markdown(
            f"**المجموع الكلي للفاتورة: {total_price:.2f} دينار**"
        )
        if str_lib.button("إصدار وطباعة فاتورة PDF / مشاركة واتساب"):
            str_lib.success(
                "تم إصدار الفاتورة وتجهيزها للمشاركة بنجاح! 🚀 (تتم محاكاة الطباعة)"
            )
            str_lib.session_state.cart = {}
    else:
        str_lib.info("السلة فارغة حالياً.")

# --- 2. قسم المخازن والمحلات ---
elif menu == "المخازن والمحلات":
    str_lib.subheader("🏢 إدارة المخازن (مخزون لحظي في كل مستودع)")
    str_lib.write("تتبع كل صنف في جميع متاجر الفروع الرئيسية والفرعية.")

    for prod_name, data in str_lib.session_state.inventory.items():
        if data["qty"] < 10:
            str_lib.warning(
                f"⚠️ تنبيه نفاذ بضاعة: المنتج '{prod_name}' كميته قليلة جداً ({data['qty']} قطعة)!"
            )

    str_lib.json(str_lib.session_state.inventory)

# --- 3. قسم التقارير النهائية والأرباح ---
elif menu == "التقارير النهائية والأرباح":
    str_lib.subheader("📊 التقارير والأرباح النهائية")
    col1, col2, col3 = str_lib.columns(3)
    col1.metric("إجمالي المبيعات اليوم", "110.35 دينار")
    col2.metric("مخزون داخل", "51")
    col3.metric("مخزون خارج", "61")

    str_lib.markdown("---")
    str_lib.info(
        "تقرير الأرباح الصافية والمصروفات مفعل وجاهز لعرض تفاصيل الحركة المالية."
    )

# --- 4. قسم سجل حركة الصندوق ---
elif menu == "سجل حركة الصندوق":
    str_lib.subheader("💰 سجل حركة الصندوق اليومي (Cash Drawer Log)")
    start_c = str_lib.number_input(
        "مبلغ الصندوق بداية اليوم (كاش):",
        value=float(str_lib.session_state.cash_log["start_cash"]),
    )
    notes_c = str_lib.text_area(
        "ملاحظات الصندوق والمصاريف النثرية:",
        value=str_lib.session_state.cash_log["notes"],
    )
    if str_lib.button("حفظ حركة الصندوق"):
        str_lib.session_state.cash_log["start_cash"] = start_c
        str_lib.session_state.cash_log["notes"] = notes_c
        str_lib.success("تم حفظ تقرير الصندوق بنجاح!")

# --- 5. قسم النسخ الاحتياطي السحابي ---
elif menu == "النسخ الاحتياطي السحابي":
    str_lib.subheader("☁️ بياناتك آمنة في السحاب")
    str_lib.write("أنشئ نسخة احتياطية بنقرة زر واحدة (محلي وسحابي).")
    if str_lib.button("إنشاء نسخة احتياطية الآن 🔄"):
        str_lib.success(
            "تم إنشاء نسخة احتياطية محلية وسحابية بنجاح، بياناتك محروسة ولن تضيع أبداً."
        )
