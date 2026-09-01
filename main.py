import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="نظام ياسر ويب", page_icon="📊", layout="wide")

# حفظ البيانات الأساسية
if 'inventory' not in st.session_state:
    st.session_state.inventory = [
        {"id": "101", "name": "كرتون بيبسي", "qty": 5, "price": 15000},
        {"id": "102", "name": "شوكولاتة", "qty": 2, "price": 1000}
    ]

if 'debts' not in st.session_state:
    st.session_state.debts = [
        {"customer": "أحمد علي", "amount": 25000, "phone": "9647800000000"}
    ]

if 'shift_box' not in st.session_state:
    st.session_state.shift_box = {"cash": 50000, "expenses": 5000}

st.title("🚀 نظام ياسر ويب - إدارة المحلات الذكية")
st.markdown("---")

# استخدام التبويبات (Tabs) لأنها أضبط وأرتب وأضمن ما تعلگ
tab1, tab2, tab3 = st.tabs(["📦 المخزن والجرد", "💰 الديون والواتساب", "💵 صندوق الوردية"])

# 1. قسم المخزن
with tab1:
    st.subheader("إدارة المخزن والمواد")
    
    # تنبيه النفاذ
    low_stock = [item for item in st.session_state.inventory if item['qty'] <= 3]
    if low_stock:
        for item in low_stock:
            st.warning(f"⚠️ تنبيه: المادة '{item['name']}' اقتربت على النفاذ! الكمية المتبقية: {item['qty']}")

    with st.form("add_item_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            item_id = st.text_input("رمز الباركود / ID")
        with col2:
            item_name = st.text_input("اسم المادة")
        with col3:
            item_qty = st.number_input("الكمية", min_value=0, value=10)
        with col4:
            item_price = st.number_input("السعر", min_value=0, value=1000)
        
        submitted = st.form_submit_button("إضافة للمخزن")
        if submitted and item_name:
            st.session_state.inventory.append({"id": item_id, "name": item_name, "qty": item_qty, "price": item_price})
            st.success(f"تمت إضافة المادة {item_name} بنجاح!")

    st.write("### قائمة المواد الحالية:")
    for item in st.session_state.inventory:
        st.write(f"- الباركود: {item['id']} | المادة: **{item['name']}** | العدد: {item['qty']} قطع | السعر: {item['price']} د.ع")

# 2. قسم الديون والواتساب
with tab2:
    st.subheader("متابعة الديون وإرسال التنبيهات")
    
    for debt in st.session_state.debts:
        st.info(f"الزبون: **{debt['customer']}** | المبلغ الذمي: **{debt['amount']} د.ع**")
        
        wa_message = f"مرحباً {debt['customer']}, نود تذكيركم بأن لديكم مبلغ ذمي بقيمة {debt['amount']} د.ع لصالح المحل. يرجى التسديد في أقرب وقت."
        wa_link = f"https://wa.me/{debt['phone']}?text={wa_message.replace(' ', '%20')}"
        
        st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer;">💬 إرسال كشف الدين للواتساب</button></a>', unsafe_allow_html=True)

# 3. صندوق الوردية
with tab3:
    st.subheader("تقارير الوردية والصندوق")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="النقد الحالي في الصندوق", value=f"{st.session_state.shift_box['cash']} د.ع")
    with col2:
        st.metric(label="المصاريف المسجلة", value=f"{st.session_state.shift_box['expenses']} د.ع")
        
    st.markdown("---")
    new_expense = st.number_input("تسجيل مصروف جديد للوردية", min_value=0, value=0)
    if st.button("خصم من الصندوق"):
        st.session_state.shift_box['expenses'] += new_expense
        st.session_state.shift_box['cash'] -= new_expense
        st.success("تم تحديث حسابات الوردية بنجاح!")
