import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="Eng. Yasser Pro System - النسخة الكاملة",
    page_icon="🔥",
    layout="wide"
)

# تنسيق الاتجاه من اليمين لليسار (RTL)
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
    }
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
        justify-content: flex-start;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# شريط جانبى لإدارة المستخدم
st.sidebar.title("إدارة المستخدم")
user_name = st.sidebar.text_input("اسم المستخدم الحالي", "ياسر")
st.sidebar.success(f"مرحباً بك، {user_name}")
st.sidebar.divider()
st.sidebar.info("📌 النظام يعمل بكامل الميزات والربط المحلي.")

# العنوان الرئيسي
st.title("🔥 Eng. Yasser Pro System - النظام المتكامل")

# رسالة الترحيب
st.markdown(
    f"""
    <div style="padding: 12px; background-color: #d4edda; color: #155724; border-radius: 6px; margin-bottom: 20px;">
    أهلاً وسهلاً بك يا <b>({user_name})</b> في النظام الكامل!<br>
    <b>تم استرجاع كافة الهوسة، شبكة المواد، ونظام السلة والفواتير بنجاح تام!</b>
    </div>
    """,
    unsafe_allow_html=True
)

# تهيئة سلة المبيعات في الذاكرة المؤقتة (Session State)
if 'cart' not in st.session_state:
    st.session_state.cart = []

# تبويبات النظام الرئيسية
tab_inventory, tab_sales, tab_reports, tab_pro = st.tabs([
    "📦 المخزن وشبكة المواد", 
    "🛒 سلة المبيعات والفاتورة", 
    "📊 التقارير المالية", 
    "🔑 تفعيل النسخة المدفوعة"
])

# 1. تبويب المخزن وشبكة المواد (Grid)
with tab_inventory:
    st.subheader("إدارة المخزن وعرض المواد (Grid System)")
    st.write("هنا تظهر بضائع المخزن على شكل شبكة مرتبة، وتستطيع إضافتها للسلة مباشرة:")

    # قائمة مواد وهمية لعرض الشبكة (تقدر تعدلها أو تربطها بقاعدة البيانات)
    products = [
        {"id": 1, "name": "لابتوب توشيبا / ديل مستعمل", "price": 250000, "stock": 5},
        {"id": 2, "name": "راوتر تي بي لينك اصلي", "price": 35000, "stock": 12},
        {"id": 3, "name": "ماوس وسلك كيبورد جيمينج", "price": 15000, "stock": 20},
        {"id": 4, "name": "هارد SSD سعة 512GB", "price": 45000, "stock": 8}
    ]

    # عرض المواد على شكل أعمدة (شبكة Grid)
    cols = st.columns(2)
    for index, prod in enumerate(products):
        col = cols[index % 2]
        with col:
            with st.container(border=True):
                st.markdown(f"### {prod['name']}")
                st.write(f"💰 السعر: **{prod['price']:,} د.ع**")
                st.write(f"📦 المتبقي بالمخزن: **{prod['stock']} قطعتين**")
                
                if st.button(f"إضافة للسلة 🛒", key=f"add_{prod['id']}"):
                    st.session_state.cart.append(prod)
                    st.success(f"تمت إضافة ({prod['name']}) إلى السلة بنجاح!")

# 2. تبويب سلة المبيعات والفاتورة الموحدة
with tab_sales:
    st.subheader("🛒 سلة المبيعات وإصدار الفاتورة الموحدة")
    
    if len(st.session_state.cart) == 0:
        st.warning("السلة فارغة حالياً! اذهب إلى تبويب (المخزن وشبكة المواد) وأضف مواد.")
    else:
        st.write("المواد المضافة حالياً في السلة:")
        total_price = 0
        
        for idx, item in enumerate(st.session_state.cart):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.write(f"**{item['name']}**")
            with c2:
                st.write(f"{item['price']:,} د.ع")
            with c3:
                if st.button("حذف", key=f"del_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            total_price += item['price']
            
        st.divider()
        st.markdown(f"### 💵 المجموع النهائي للفاتورة: `{total_price:,} د.ع`")
        
        customer_name = st.text_input("اسم الزبون الكريم:")
        
        if st.button("إصدار وطباعة الفاتورة النهائية", type="primary"):
            if customer_name.strip() == "":
                st.error("الرجاء إدخال اسم الزبون قبل إصدار الفاتورة!")
            else:
                st.success(f"🎉 تم إصدار الفاتورة بنجاح للزبون: ({customer_name}) بمبلغ إجمالي ({total_price:,} د.ع)!")
                st.balloons()
                # تفريغ السلة بعد البيع
                st.session_state.cart = []

# 3. تبويب التقارير
with tab_reports:
    st.subheader("📊 تقارير المبيعات والأرباح")
    st.info("هنا تظهر تقارير الحركة المالية والتحليلات الخاصة بالمخزن.")
    st.metric(label="إجمالي المبيعات الكلية", value="0 د.ع", delta="0%")

# 4. تبويب تفعيل النسخة المدفوعة والحقل السري
with tab_pro:
    st.subheader("🔑 إدخال كود النسخة المدفوعة / الاحترافية")
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
st.caption("Eng. Yasser Pro System - النسخة الاحترافية الكاملة 2026")
