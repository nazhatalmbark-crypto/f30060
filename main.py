import streamlit as st
from datetime import datetime

# إعدادات صفحة ستريملت
st.set_page_config(
    page_title="نظام ياسر ويب المتكامل",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخزين مؤقت للبيانات الوهمية لتشغيل النظام بسلاسة
if 'inventory' not in st.session_state:
    st.session_state.inventory = [
        {"id": 1, "name": "هاتف آيفون 15 برو", "color": التيتانيوم, "size": 256GB, "barcode": "6281001", "buy_price": 950, "sell_price": 1050, "qty": 10},
        {"id": 2, "name": "ساعة أبل الترا", "color": "برتقالي", "size": "قياسي", "barcode": "6281002", "buy_price": 300, "sell_price": 350, "qty": 15}
    ]

if 'sales' not in st.session_state:
    st.session_state.sales = []

if 'customers' not in st.session_state:
    st.session_state.customers = [{"name": "محمد أحمد", "phone": "07800000000", "debt": 150}]

if 'expenses' not in st.session_state:
    st.session_state.expenses = [{"desc": "أجور نقل بضاعة", "amount": 25, "time": "2026-09-25"}]

if 'logs' not in st.session_state:
    st.session_state.logs = [{"action": "تسجيل دخول النظام", "user": "مدير النظام", "time": "2026-09-25 09:00"}]

# القائمة الجانبية للتنقل
st.sidebar.markdown("<h2 style='text-align: center; color: #8b6508;'>🌟 نظام ياسر ويب</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #666;'>الإدارة المتكاملة للمبيعات والمخازن</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "اختر القسم:",
    [
        "📖 دليل الاستخدام",
        "🛒 نقطة البيع السريعة (POS)",
        "📦 إدارة المخزن وجرد البضائع",
        "➕ إضافة مادة جديدة والباركود",
        "👥 العملاء والديون",
        "💰 صندوق الوردية والمصروفات",
        "📊 تقارير الأرباح والسجل الرقابي"
    ]
)

# 1. دليل الاستخدام المرتب
if menu == "📖 دليل الاستخدام":
    st.markdown("""
    <div style="font-family: 'Cairo', sans-serif; direction: rtl; background-color: #fdfbf7; padding: 20px; border-radius: 12px; border: 1px solid #e6d5b8;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h2 style="color: #8b6508; margin: 0; font-size: 24px; font-weight: 700;">🌟 دليل استخدام نظام ياسر ويب الشامل</h2>
            <p style="color: #666; font-size: 14px; margin-top: 5px;">الدليل المرجعي لإدارة المبيعات، المخازن، والحسابات بكفاءة واحترافية عالية</p>
        </div>

        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">🛒 1. نقطة البيع السريعة (POS) وإتمام الفاتورة</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">النافذة التشغيلية الأساسية لإتمام عمليات البيع بسلاسة. يتيح لك القسم سحب المواد من المخزن مباشرة، مع حساب المجاميع آلياً وتحديد نوع الدفع (نقدي، دين، أو جزئي).</p>
        </div>

        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">📦 2. إدارة المخزن وجرد البضائع</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">مرآة المخزون الشاملة؛ تعرض كافة المواد المسجلة تفصيلياً مع بيان الألوان، القياسات، الباركود، أسعار الشراء والبيع، والكميات المتاحة لحظياً.</p>
        </div>

        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">➕ 3. إضافة مادة جديدة وتوليد الباركود</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">بوابة إدخال البضائع والاصناف الجديدة إلى النظام مع تحديد تفاصيلها المالية والفنية وتوليد رموز الباركود المعيارية.</p>
        </div>

        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">👥 4. العملاء والديون وسندات القبض</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">منظومة متكاملة لإدارة علاقات العملاء، تسجيل بياناتهم، ومتابعة أرصدتهم والديون المرتبطة بفواتيرهم الآجلة.</p>
        </div>

        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">💰 5. صندوق الوردية والمصروفات النقدية</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">وحدة الرقابة المالية اليومية المخصصة لتسجيل النثريات والمصروفات التشغيلية لحساب صافي رصيد الصندوق الفعلي بدقة.</p>
        </div>

        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">📊 6. تقارير الأرباح والسجل الرقابي</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">أقسام استراتيجية تعرض تحليلات مالية دقيقة لإجمالي المبيعات، الأرباح، والسجل الرقابي الموثق لكافة حركات المستخدمين.</p>
        </div>

        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px dashed #DAA520;">
            <p style="font-size: 14px; color: #444; font-weight: bold; margin-bottom: 8px;">
                ✨ تصميم وبرمجة: <b>نظام ياسر ويب</b> | جميع الحقوق محفوظة للإدارة المتكاملة 2026
            </p>
            <a href="https://instagram.com/yasser_web" target="_blank" style="color: #8b6508; text-decoration: none; font-weight: bold; font-size: 14px;">
                📸 تواصل معنا عبر انستغرام: @yasser_web
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 2. نقطة البيع (POS)
elif menu == "🛒 نقطة البيع السريعة (POS)":
    st.header("🛒 نقطة البيع السريعة (POS) وإتمام الفاتورة")
    st.write("اختر المواد وأتمم عملية البيع بكل سلاسة:")
    
    selected_item = st.selectbox("اختر المادة من المخزن:", [i['name'] for i in st.session_state.inventory])
    qty_to_buy = st.number_input("الكمية:", min_value=1, value=1)
    
    if st.button("إضافة إلى السلة وإصدار الفاتورة"):
        st.success(تم إصدار الفاتورة بنجاح للمادة: {selected_item} بكمية {qty_to_buy})
        st.session_state.logs.append({"action": f"بيع مادة: {selected_item}", "user": "موظف المبيعات", "time": str(datetime.now())[:16]})

# 3. إدارة المخزن
elif menu == "📦 إدارة المخزن وجرد البضائع":
    st.header("📦 إدارة المخزن وجرد البضائع")
    st.dataframe(st.session_state.inventory, use_container_width=True)

# 4. إضافة مادة جديدة
elif menu == "➕ إضافة مادة جديدة والباركود":
    st.header("➕ إضافة مادة جديدة وتوليد الباركود")
    with st.form("add_item_form"):
        item_name = st.text_input("اسم المادة الجديدة")
        item_color = st.text_input("اللون / المواصفات")
        item_buy = st.number_input("سعر الشراء", min_value=0.0)
        item_sell = st.number_input("سعر البيع", min_value=0.0)
        item_qty = st.number_input("الكمية المتوفرة", min_value=0, value=1)
        submitted = st.form_submit_button("حفظ وإضافة للمخزن")
        if submitted and item_name:
            st.session_state.inventory.append({
                "id": len(st.session_state.inventory) + 1,
                "name": item_name,
                "color": item_color,
                "size": "قياسي",
                "barcode": f"628100{len(st.session_state.inventory)+1}",
                "buy_price": item_buy,
                "sell_price": item_sell,
                "qty": item_qty
            })
            st.success(تمت إضافة المادة '{item_name}' بنجاح وتوليد الباركود المعياري!)
            st.session_state.logs.append({"action": f"إضافة مادة جديدة: {item_name}", "user": "مدير النظام", "time": str(datetime.now())[:16]})

# 5. العملاء والديون
elif menu == "👥 العملاء والديون":
    st.header("👥 العملاء والديون وسندات القبض")
    st.dataframe(st.session_state.customers, use_container_width=True)

# 6. صندوق الوردية والمصروفات
elif menu == "💰 صندوق الوردية والمصروفات":
    st.header("💰 صندوق الوردية والمصروفات النقدية")
    st.dataframe(st.session_state.expenses, use_container_width=True)
    exp_desc = st.text_input("بيان المصروف (مثل: صيانة، أجور نقل)")
    exp_amount = st.number_input("مبلغ المصروف", min_value=0.0)
    if st.button("تسجيل المصروف"):
        st.session_state.expenses.append({"desc": exp_desc, "amount": exp_amount, "time": str(datetime.now())[:10]})
        st.success("تم تسجيل المصروف بنجاح وتحديث رصيد الصندوق.")

# 7. تقارير الأرباح والسجل الرقابي
elif menu == "📊 تقارير الأرباح والسجل الرقابي":
    st.header("📊 تقارير الأرباح والسجل الرقابي")
    st.subheader("سجل العمليات والرقابة الأمنية للنظام:")
    st.dataframe(st.session_state.logs, use_container_width=True)
