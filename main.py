import streamlit as st
import datetime

st.set_page_config(page_title="نظام ياسر ويب - الكاشير الذكي", layout="wide")

# تهيئة المتغيرات الأساسية
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = "محل ياسر" # اسم المحل الافتراضي أو المسجل

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'invoices' not in st.session_state:
    st.session_state.invoices = []

if 'products' not in st.session_state:
    st.session_state.products = [
        {"id": 1, "name": "شامبو شعر", "price": 3000, "stock": 10},
        {"id": 2, "name": "معجون أسنان", "price": 1500, "stock": 25},
        {"id": 3, "name": "صابون الاستحمام", "price": 1000, "stock": 15},
        {"id": 4, "name": "عطر رجالي", "price": 12000, "stock": 5},
    ]

if 'subscription_days' not in st.session_state:
    st.session_state.subscription_days = 30

menu = st.sidebar.selectbox("قائمة التنقل", ["🛒 شاشة الكاشير والمبيعات", "📦 إدارة المخزن", "📜 سجل الفواتير", "📖 الدليل وطرق التواصل"])

# عداد الأيام
st.sidebar.markdown("---")
st.sidebar.subheader("⏳ حالة اشتراك النظام")
days_left = st.session_state.subscription_days
if days_left > 0:
    st.sidebar.success(f"الاشتراك نشط: باقي {days_left} يوم")
    if st.sidebar.button("محاكاة مرور يوم (-1 يوم)"):
        st.session_state.subscription_days -= 1
        st.rerun()
else:
    st.sidebar.error("⚠️ انتهى الاشتراك! تحول النظام إلى النسخة المجانية.")

# --- شاشة الكاشير والمبيعات ---
if menu == "🛒 شاشة الكاشير والمبيعات":
    st.title(f"🛒 نقطة البيع - {st.session_state.logged_in_user}")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📦 المنتجات المتوفرة")
        for prod in st.session_state.products:
            c1, c2, c3 = st.columns([3, 2, 2])
            c1.write(f"**{prod['name']}**")
            c2.write(f"السعر: {prod['price']} د.ع")
            c3.write(f"المخزون: {prod['stock']}")
            
            if prod['stock'] > 0:
                if st.button(f"➕ إضفة للعربانة", key=f"add_{prod['id']}"):
                    found = False
                    for item in st.session_state.cart:
                        if item['id'] == prod['id']:
                            if item['qty'] < prod['stock']:
                                item['qty'] += 1
                            found = True
                            break
                    if not found:
                        st.session_state.cart.append({"id": prod['id'], "name": prod['name'], "price": prod['price'], "qty": 1})
                    st.rerun()
            else:
                st.error("خلصت المادة")
            st.markdown("---")

    with col2:
        st.markdown("### 🛍️ سلة المبيعات (العربانة)")
        if not st.session_state.cart:
            st.info("العربانة فارغة حالياً.")
        else:
            total_amount = 0
            for item in st.session_state.cart:
                item_total = item['price'] * item['qty']
                total_amount += item_total
                st.markdown(f"**{item['name']}** (x{item['qty']}) - **{item_total} د.ع**")
            
            st.markdown("---")
            st.markdown(f"**المجموع الكلي:** {total_amount:,} د.ع")
            
            # حقل الخصم الاختياري
            discount_val = st.number_input("حقل الخصم (اختياري - د.ع):", min_value=0, value=0, step=500)
            final_total = max(0, total_amount - discount_val)
            
            if discount_val > 0:
                st.markdown(f"**المجموع بعد الخصم:** `{final_total:,}` د.ع")

            # حقل المبلغ الواصل (المدفوع)
            paid_amount = st.number_input("المبلغ الواصل من الزبون (د.ع):", min_value=0, value=int(final_total), step=1000)
            remaining_debt = max(0, final_total - paid_amount)
            
            if remaining_debt > 0:
                st.warning(f"⚠️ يوجد دين على الزبون بقيمة: **{remaining_debt:,}** د.ع")
            else:
                st.success("✅ الفاتورة مسددة بالكامل (كاش)")

            st.markdown("---")
            
            if st.button("✅ إتمام البيع وطبع الفاتورة", type="primary", use_container_width=True):
                # خصم الكميات من المخزن
                for cart_item in st.session_state.cart:
                    for p in st.session_state.products:
                        if p['id'] == cart_item['id']:
                            p['stock'] -= cart_item['qty']
                
                # حفظ الفاتورة مع تفاصيل المحل والخصم والدين
                new_invoice = {
                    "store": st.session_state.logged_in_user,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "items": list(st.session_state.cart),
                    "total": total_amount,
                    "discount": discount_val,
                    "final_total": final_total,
                    "paid": paid_amount,
                    "debt": remaining_debt
                }
                st.session_state.invoices.append(new_invoice)
                
                # تفريغ العربانة
                st.session_state.cart = []
                st.success("🎉 تمت عملية البيع بنجاح وتفرغت العربانة!")
                st.rerun()

            if st.button("🗑️ تفريغ العربانة", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

# --- إدارة المخزن ---
elif menu == "📦 إدارة المخزن":
    st.title("📦 إدارة المخزن والمنتجات")
    with st.form("add_prod"):
        p_name = st.text_input("اسم المنتج الجديد")
        p_price = st.number_input("السعر (د.ع)", min_value=0, value=1000)
        p_stock = st.number_input("الكمية بالمخزن", min_value=0, value=10)
        submitted = st.form_submit_button("إضافة للمخزن")
        if submitted and p_name:
            new_id = len(st.session_state.products) + 1
            st.session_state.products.append({"id": new_id, "name": p_name, "price": p_price, "stock": p_stock})
            st.success(f"تمت إضافة {p_name} بنجاح!")
            st.rerun()

    st.subheader("قائمة المخزون الحالية:")
    for p in st.session_state.products:
        st.write(f"- {p['name']} | السعر: {p['price']} | المتبقي: {p['stock']} قطعة")

# --- سجل الفواتير ---
elif menu == "📜 سجل الفواتير":
    st.title("📜 سجل الفواتير السابقة")
    if not st.session_state.invoices:
        st.info("لا توجد فواتير مسجلة حتى الآن.")
    else:
        for idx, inv in enumerate(st.session_state.invoices, 1):
            with st.expander(f"فاتورة رقم #{idx} | المحل: {inv['store']} | المجموع النهائي: {inv['final_total']:,} د.ع - الوقت: {inv['time']}"):
                st.write(f"🔹 المجموع الأصلي: {inv['total']:,} د.ع | الخصم: {inv['discount']:,} د.ع")
                st.write(f"🔹 الواصل: {inv['paid']:,} د.ع | المتبقي (الدين): {inv['debt']:,} د.ع")
                st.markdown("---")
                for itm in inv['items']:
                    st.write(f"• {itm['name']} | الكمية: {itm['qty']} | السعر الفردي: {itm['price']:,}")

# --- الدليل وطرق التواصل ---
elif menu == "📖 الدليل وطرق التواصل":
    st.title("📖 دليل الاستخدام وطرق التواصل - نظام ياسر ويب")
    st.markdown("""
    ### 🔍 شرح الواجهات:
    - **شاشة الكاشير:** اختر المواد لتصعد مباشرة للعربانة، أدخل الخصم الاختياري والمبلغ الواصل، ثم اضغط إتمام البيع ليطبع اسم المحل وتتفرغ العربانة تلقائياً.
    """)
    st.markdown("---")
    st.markdown("""
    ### 📞 طرق التواصل والدعم الفني
    * **مطور النظام:** ياسر
    * **تيليجرام الرسمي:** [تواصل عبر تيليجرام](https://t.me/)
    * **المدينة:** العراق - البصرة
    """)
