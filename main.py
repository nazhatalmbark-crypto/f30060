import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة المبيعات والمخزن",
    page_icon="📦",
    layout="wide"
)

# تهيئة قاعدة البيانات المؤقتة في الذاكرة
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=[
        'رقم المنتج', 'اسم المنتج', 'التصنيف', 'سعر الشراء', 'سعر البيع', 'الكمية المتوفرة'
    ])

if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=[
        'رقم الفاتورة', 'التاريخ', 'اسم العميل', 'المنتجات المباعة', 'المبلغ الإجمالي', 'نوع الدفع'
    ])

if 'is_vip' not in st.session_state:
    st.session_state.is_vip = False

# القائمة الجانبية للتنقل
st.sidebar.title("🗂️ القائمة الرئيسية")
page = st.sidebar.radio("اختر القسم:", [
    "📦 إدارة المخزن",
    "🛒 نقطة البيع (POS)",
    "📊 المبيعات والتقارير",
    "👥 العملاء",
    "⚙️ الإعدادات والدعم"
])

# التحقق من التفعيل في الشريط الجانبي (بدون إظهار الكود علناً)
st.sidebar.markdown("---")
if not st.session_state.is_vip:
    st.sidebar.subheader("🔒 تفعيل النسخة الكاملة")
    vip_code_input = st.sidebar.text_input("أدخل كود التفعيل:", type="password")
    if st.sidebar.button("تفعيل"):
        if vip_code_input == "YASSER2026":
            st.session_state.is_vip = True
            st.sidebar.success("تم تفعيل النسخة بنجاح! 🎉")
            st.rerun()
        else:
            st.sidebar.error("كود التفعيل غير صحيح!")
else:
    st.sidebar.success("✨ النسخة مفعلة بالكامل (VIP)")

# --- 1. قسم إدارة المخزن ---
if page == "📦 إدارة المخزن":
    st.title("📦 إدارة المخزن والمنتجات")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("إضافة منتج جديد")
        with st.form("add_product_form"):
            prod_id = st.text_input("رقم المنتج (Barcode/ID)")
            prod_name = st.text_input("اسم المنتج")
            prod_category = st.selectbox("التصنيف", ["عام", "إلكترونيات", "مواد غذائية", "أجهزة منزلية"])
            buy_price = st.number_input("سعر الشراء", min_value=0.0, step=0.5)
            sell_price = st.number_input("سعر البيع", min_value=0.0, step=0.5)
            quantity = st.number_input("الكمية المتوفرة", min_value=1, step=1)
            
            submit_btn = st.form_submit_button("حفظ المنتج")
            
            if submit_btn:
                # التحقق من القيود للنسخة العادية
                if not st.session_state.is_vip and len(st.session_state.inventory) >= 5:
                    st.error("⚠️ لقد وصلت الحد الأقصى للنسخة المجانية (5 منتجات). قم بتفعيل النظام لإضافة المزيد.")
                elif not prod_id or not prod_name:
                    st.warning("الرجاء إدخال رقم ورسالة اسم المنتج على الأقل.")
                else:
                    new_row = pd.DataFrame({
                        'رقم المنتج': [prod_id],
                        'اسم المنتج': [prod_name],
                        'التصنيف': [prod_category],
                        'سعر الشراء': [buy_price],
                        'سعر البيع': [sell_price],
                        'الكمية المتوفرة': [quantity]
                    })
                    st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
                    st.success(f"تم إضافة المنتج '{prod_name}' بنجاح!")

    with col2:
        st.subheader("حالة المخزن الحالية")
        if not st.session_state.inventory.empty:
            st.dataframe(st.session_state.inventory, use_container_width=True)
            
            # زر حذف منتج
            del_id = st.selectbox("اختر رقم المنتج للحذف:", options=[''] + list(st.session_state.inventory['رقم المنتج'].astype(str)))
            if del_id and st.button("حذف المنتج المحدد"):
                st.session_state.inventory = st.session_state.inventory[st.session_state.inventory['رقم المنتج'].astype(str) != del_id]
                st.success("تم حذف المنتج بنجاح!")
                st.rerun()
        else:
            st.info("لا توجد منتجات مضافة حتى الآن.")

# --- 2. قسم نقطة البيع ---
elif page == "🛒 نقطة البيع (POS)":
    st.title("🛒 نقطة البيع الفورية")
    if st.session_state.inventory.empty:
        st.warning("المخزن فارغ! يرجى إضافة منتجات من قسم إدارة المخزن أولاً.")
    else:
        customer_name = st.text_input("اسم العميل", value="عميل نقدي")
        payment_type = st.radio("طريقة الدفع:", ["نقداً", "أجل / ذمم"], horizontal=True)
        
        selected_prod = st.selectbox("اختر المنتج للبيع:", st.session_state.inventory['اسم المنتج'])
        prod_row = st.session_state.inventory[st.session_state.inventory['اسم المنتج'] == selected_prod].iloc[0]
        
        available_qty = prod_row[' الكمية المتوفرة' if ' الكمية المتوفرة' in prod_row else 'الكمية المتوفرة']
        unit_price = prod_row['سعر البيع']
        
        st.write(-f"السعر المفرد: {unit_price} | الكمية المتاحة: {available_qty}")
        sale_qty = st.number_input("الكمية المطلوبة", min_value=1, max_value=int(available_qty) if available_qty > 0 else 1, step=1)
        
        if st.button("إتمام البيع واصدار الفاتورة"):
            total_amount = unit_price * sale_qty
            invoice_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # تسجيل الفاتورة
            new_sale = pd.DataFrame({
                'رقم الفاتورة': [invoice_id],
                'التاريخ': [datetime.now().strftime('%Y-%m-%d %H:%M')],
                'اسم العميل': [customer_name],
                'المنتجات المباعة': [f"{selected_prod} (الكمية: {sale_qty})"],
                'المبلغ الإجمالي': [total_amount],
                'نوع الدفع': [payment_type]
            })
            st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
            
            # تحديث الكمية بالمخزن
            idx = st.session_state.inventory[st.session_state.inventory['اسم المنتج'] == selected_prod].index[0]
            qty_key = ' الكمية المتوفرة' if ' الكمية المتوفرة' in st.session_state.inventory.columns else 'الكمية المتوفرة'
            st.session_state.inventory.loc[idx, qty_key] -= sale_qty
            
            st.success(f"تمت العملية بنجاح! رقم الفاتورة: {invoice_id} | المبلغ الإجمالي: {total_amount}")

# --- 3. قسم المبيعات والتقارير ---
elif page == "📊 المبيعات والتقارير":
    st.title("📊 سجل المبيعات والتقارير المالية")
    if not st.session_state.sales.empty:
        st.dataframe(st.session_state.sales, use_container_width=True)
        total_revenue = st.session_state.sales['المبلغ الإجمالي'].sum()
        st.metric("إجمالي المبيعات الكلية", f"{total_revenue:,.2f}")
    else:
        st.info("لا توجد مبيعات مسجلة حتى الآن.")

# --- 4. قسم العملاء ---
elif page == "👥 العملاء":
    st.title("👥 إدارة العملاء والديون")
    st.info("هذا القسم مخصص لمتابعة حسابات العملاء والذمم المالية.")
    if not st.session_state.sales.empty:
        credit_sales = st.session_state.sales[st.session_state.sales['نوع الدفع'] == "أجل / ذمم"]
        if not credit_sales.empty:
            st.subheader("قائمة الديون والذمم المترتبة على العملاء")
            st.dataframe(credit_sales[['التاريخ', 'اسم العميل', 'المبلغ الإجمالي']], use_container_width=True)
        else:
            st.success("لا توجد ديون أو حسابات أجل معلقة حالياً.")
    else:
        st.info("لا توجد بيانات مبيعات لعرضها.")

# --- 5. قسم الإعدادات والدعم ---
elif page == "⚙️ الإعدادات والدعم":
    st.title("⚙️ الإعدادات ودليل الاستخدام")
    
    tab1, tab2 = st.tabs(["📖 دليل الاستخدام", "🛠️ إعدادات النظام"])
    
    with tab1:
        st.markdown("""
        ### أهلاً بك في نظام إدارة المبيعات والمخزن المبسط
        
        * **إدارة المخزن:** يمكنك إضافة وترتيب منتجاتك ومعرفة الكميات المتوفرة بسهولة.
        * **نقطة البيع (POS):** لوحة سريعة لإصدار الفواتير وحساب المبالغ وخصم الكميات تلقائياً.
        * **التقارير:** لمتابعة إجمالي الأرباح وحركة المبيعات اليومية.
        * **ملاحظة:** في النسخة المجانية، يمكنك إضافة حتى 5 منتجات فقط. لتفعيل الحساب وإزالة القيود بشكل كامل، يرجى إدخال كود التفعيل الخاص في القائمة الجانبية.
        """)
        
    with tab2:
        st.subheader("إدارة بيانات النظام")
        if st.button("🔄 تصفير وحذف كافة بيانات النظام"):
            st.session_state.inventory = pd.DataFrame(columns=['رقم المنتج', 'اسم المنتج', 'التصنيف', 'سعر الشراء', 'سعر البيع', 'الكمية المتوفرة'])
            st.session_state.sales = pd.DataFrame(columns=['رقم الفاتورة', 'التاريخ', 'اسم العميل', 'المنتجات المباعة', 'المبلغ الإجمالي', 'نوع الدفع'])
            st.success("تم مسح كافة البيانات وإعادة ضبط النظام بنجاح.")
            st.rerun()
