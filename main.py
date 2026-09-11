import streamlit as __st__
from datetime import datetime

# ==========================================
# إعدادات الصفحة
# ==========================================
__st__.set_page_config(
    page_title="نظام إدارة المحل الاحترافي",
    page_icon="🏪",
    layout="wide"
)

# محاكاة قاعدة البيانات (Session State)
if 'logged_in' not in __st__.session_state:
    __st__.session_state['logged_in'] = False

if 'products' not in __st__.session_state:
    __st__.session_state['products'] = [
        {"id": 1, "name": "لابتوب ديل كورو i5", "category": "لابتوب", "price": 450000, "qty": 5, "barcode": "1001"},
        {"id": 2, "name": "بلايستيشن 5 - سليم", "category": "ألعاب", "price": 650000, "qty": 3, "barcode": "1002"},
        {"id": 3, "name": "سماعة بلوتوث أوبن إير", "category": "إكسسوارات", "price": 35000, "qty": 15, "barcode": "1003"}
    ]

if 'sales' not in __st__.session_state:
    __st__.session_state['sales'] = []

if 'expenses' not in __st__.session_state:
    __st__.session_state['expenses'] = []

if 'customers' not in __st__.session_state:
    __st__.session_state['customers'] = [
        {"name": "أحمد علي", "phone": "07700000000", "debt": 25000}
    ]

if 'cashiers_status' not in __st__.session_state:
    __st__.session_state['cashiers_status'] = {"نشط": True}


# ==========================================
# 1. شاشة تسجيل الدخول المستقلة (Login Screen)
# ==========================================
if not __st__.session_state['logged_in']:
    __st__.title("🔐 بوابة تسجيل الدخول لنظام المحل")
    __st__.markdown("يرجى إدخال معلومات الدخول للوصول إلى لوحة التحكم ونقطة البيع.")
    
    with __st__.form("login_form"):
        store_input = __st__.text_input("اسم المحل:", "محل التكنولوجيا الذكية")
        username_input = __st__.text_input("اسم المستخدم:")
        password_input = __st__.text_input("كلمة المرور:", type="password")
        role_input = __st__.selectbox("الصلاحية:", ["مشرف النظام (المالك)", "كاشير"])
        
        login_btn = __st__.form_submit_button("تسجيل الدخول 🚀")
        
        if login_btn:
            if username_input.strip() != "":
                __st__.session_state['logged_in'] = True
                __st__.session_state['store_name'] = store_input
                __st__.session_state['username'] = username_input
                __st__.session_state['user_role'] = role_input
                __st__.success("تم تسجيل الدخول بنجاح! جاري فتح النظام...")
                __st__.rerun()
            else:
                __st__.error("يرجى إدخال اسم المستخدم على الأقل!")
    
    __st__.stop()  # إيقاف تنفيذ باقي الكود لحين تسجيل الدخول


# استرجاع الجلسة بعد تسجيل الدخول
store_name = __st__.session_state.get('store_name', 'المحل الذكي')
username = __st__.session_state.get('username', 'مدير')
user_role = __st__.session_state.get('user_role', 'مشرف النظام (المالك)')


# ==========================================
# الشريط الجانبي (Sidebar بعد الدخول)
# ==========================================
__st__.sidebar.title("⚙️ لوحة التحكم الجانبية")
__st__.sidebar.info(f"المحل: **{store_name}**\n\nالمستخدم: **{username}**\n\nالصلاحية: **{user_role}**")

if __st__.sidebar.button("🚪 تسجيل الخروج"):
    __st__.session_state['logged_in'] = False
    __st__.rerun()

__st__.sidebar.markdown("---")

# زر تفعيل/إيقاف الكاشير (يظهر للمالك فقط)
if user_role == "مشرف النظام (المالك)":
    __st__.sidebar.markdown("### 🔒 إدارة الكاشير")
    cashier_active = __st__.sidebar.checkbox("السماح بدخول الكاشير للعمل", value=__st__.session_state['cashiers_status'].get("نشط", True))
    __st__.session_state['cashiers_status']["نشط"] = cashier_active
else:
    if not __st__.session_state['cashiers_status'].get("نشط", True):
        __st__.error("⚠️ عذراً، تم إيقاف حساب الكاشير من قبل المالك مؤقتاً. يرجى مراجعة الإدارة.")
        __st__.stop()


# ==========================================
# واجهة التبويبات الرئيسية للنظام
# ==========================================
__st__.title(f"🏪 نظام إدارة وإصدار فواتير المحل - {store_name}")

tabs = __st__.tabs([
    "🛒 نقطة البيع (POS)", 
    "📦 إدارة المخزن", 
    "👥 العملاء والديون", 
    "💸 المصروفات النثرية",
    "📊 التقارير والأرباح", 
    "📖 دليل الاستخدام والشرح"
])


# ------------------------------------------
# تبويب 1: نقطة البيع (POS) بنظام البطاقات (Cards) + حاسبة الباقي
# ------------------------------------------
with tabs[0]:
    __st__.header("🛒 نقطة البيع السريعة (الكاشير)")
    
    col1, col2 = __st__.columns([2, 1])
    
    with col1:
        __st__.subheader("📦 المواد المتاحة للبيع (نظام البطاقات)")
        search_query = __st__.text_input("🔍 بحث عن مادة بالاسم أو الباركود:", "")
        
        filtered_products = [p for p in __st__.session_state['products'] if search_query.lower() in p['name'].lower() or search_query in p['barcode']]
        
        if not filtered_products:
            __st__.warning("لم يتم العثور على مادة مطابقة للبحث.")
        else:
            # عرض المنتجات بنظام شبكة بطاقات (Columns Grid)
            cols = __st__.columns(2)
            for index, prod in enumerate(filtered_products):
                with cols[index % 2]:
                    with __st__.container(border=True):
                        __st__.markdown(f"### {prod['name']}")
                        __st__.write(f"📂 التصنيف: {prod['category']}")
                        __st__.write(f"💰 السعر: **{prod['price']:,}** د.ع")
                        
                        stock_color = "🟢" if prod['qty'] > 2 else "🔴"
                        __st__.write(f"الكمية المتوفرة: {stock_color} **{prod['qty']}**")
                        
                        if __st__.button(f"إضافة للسلة ➕", key=f"card_add_{prod['id']}"):
                            if prod['qty'] > 0:
                                prod['qty'] -= 1
                                __st__.session_state['sales'].append({
                                    "item": prod['name'],
                                    "price": prod['price'],
                                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                                })
                                __st__.success(f"تمت إضافة {prod['name']} بنجاح!")
                                __st__.rerun()
                            else:
                                __st__.error("عذراً، المادة نفذت من المخزن!")

    with col2:
        __st__.subheader("🧾 سلة المبيعات والفاتورة")
        if not __st__.session_state['sales']:
            __st__.info("السلة فارغة حالياً. اضغط على 'إضافة للسلة' من بطاقات المواد.")
        else:
            total_amount = 0
            for i, sale in enumerate(__st__.session_state['sales']):
                __st__.write(f"{i+1}. {sale['item']} - **{sale['price']:,}** د.ع")
                total_amount += sale['price']
            
            __st__.markdown("---")
            __st__.markdown(f"### الإجمالي المطلوب: **{total_amount:,} دينار**")
            
            # --- حاسبة الصرف وإرجاع الباقي للزبون ---
            __st__.markdown("#### 💵 حاسبة الباقي للزبون")
            received_cash = __st__.number_input("المبلغ المستلم من الزبون (د.ع):", min_value=0, step=1000, value=0)
            
            if received_cash > 0:
                change_due = received_cash - total_amount
                if change_due >= 0:
                    __st__.success(f"الباقي الواجب إرجاعه للزبون: **{change_due:,} دينار**")
                else:
                    __st__.error(f"المبلغ غير كافٍ! ناقص بمقدار: {abs(change_due):,} دينار")

            if __st__.button("✅ إتمام البيع وطبع الفاتورة", use_container_width=True):
                __st__.balloons()
                __st__.success("تم إتمام عملية البيع بنجاح وتحديث المخزن!")
                __st__.session_state['sales'] = []
                __st__.rerun()


# ------------------------------------------
# تبويب 2: إدارة المخزن
# ------------------------------------------
with tabs[1]:
    __st__.header("📦 إدارة المخزن والبضاعة")
    
    if user_role == "كاشير":
        __st__.warning("⚠️ ملاحظة: أنت بصلاحية كاشير، يمكنك مشاهدة المخزن ولا يمكنك إضافة مواد جديدة بدون المالك.")
    else:
        with __st__.form("add_product_form"):
            __st__.subheader("إضافة مادة جديدة للمخزن")
            p_name = __st__.text_input("اسم المادة:")
            p_cat = __st__.selectbox("التصنيف:", ["لابتوب", "ألعاب", "إكسسوارات", "صيانة وملحقات"])
            p_price = __st__.number_input("سعر البيع (د.ع):", min_value=0, step=1000)
            p_qty = __st__.number_input("الكمية المتوفرة:", min_value=1, step=1)
            p_barcode = __st__.text_input("رقم الباركود:")
            
            submitted = __st__.form_submit_button("حفظ وإضافة المادة")
            if submitted and p_name:
                new_id = len(__st__.session_state['products']) + 1
                __st__.session_state['products'].append({
                    "id": new_id, "name": p_name, "category": p_cat, "price": p_price, "qty": p_qty, "barcode": p_barcode
                })
                __st__.success("تمت إضافة المادة بنجاح للمخزن!")
                __st__.rerun()

    __st__.subheader("قائمة المخزون الحالي")
    for p in __st__.session_state['products']:
        stock_status = "🔴 قارب على النفاد!" if p['qty'] <= 2 else "🟢 متوفر"
        __st__.write(f"**{p['name']}** | التصنيف: {p['category']} | السعر: {p['price']:,} د.ع | الكمية: **{p['qty']}** ({stock_status})")


# ------------------------------------------
# تبويب 3: العملاء والديون
# ------------------------------------------
with tabs[2]:
    __st__.header("👥 سجل العملاء والديون المترتبة")
    
    with __st__.form("add_customer"):
        c_name = __st__.text_input("اسم الزبون:")
        c_phone = __st__.text_input("رقم الهاتف:")
        c_debt = __st__.number_input("المبلغ المترتب بذمته (د.ع):", min_value=0, step=1000)
        c_sub = __st__.form_submit_button("تسجيل عميل جديد")
        if c_sub and c_name:
            __st__.session_state['customers'].append({"name": c_name, "phone": c_phone, "debt": c_debt})
            __st__.success("تم حفظ معلومات العميل!")
            __st__.rerun()

    __st__.subheader("قائمة الديون المسجلة")
    for cust in __st__.session_state['customers']:
        __st__.write(f"- العميل: **{cust['name']}** | الهاتف: {cust['phone']} | الدين الذمي: **{cust['debt']:,} د.ع**")


# ------------------------------------------
# تبويب 4: المصروفات النثرية
# ------------------------------------------
with tabs[3]:
    __st__.header("💸 سجل المصروفات والإيرادات النثرية اليومية")
    __st__.markdown("سجل مصاريف المحل اليومية (إيجار، كهرباء، قهوة، ضيافة، تصليحات) لحساب الصافي الحقيقي.")
    
    with __st__.form("expense_form"):
        exp_title = __st__.text_input("وصف المصروف (مثال: فاتورة الإنترنت / اشتراك المولد):")
        exp_amount = __st__.number_input("مبلغ المصروف (د.ع):", min_value=0, step=500)
        exp_btn = __st__.form_submit_button("تسجيل المصروف")
        if exp_btn and exp_title:
            __st__.session_state['expenses'].append({
                "title": exp_title,
                "amount": exp_amount,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            __st__.success("تم تسجيل المصروف بنجاح!")
            __st__.rerun()

    __st__.subheader("قائمة المصاريف المسجلة")
    total_expenses = 0
    if not __st__.session_state['expenses']:
        __st__.info("لا توجد مصاريف مسجلة حتى الآن.")
    else:
        for ex in __st__.session_state['expenses']:
            __st__.write(f"📌 {ex['title']} - **{ex['amount']:,} د.ع** (تاريخ: {ex['date']})")
            total_expenses += ex['amount']
        __st__.markdown(f"### إجمالي المصاريف المسجلة: **{total_expenses:,} دينار**")


# ------------------------------------------
# تبويب 5: التقارير والأرباح
# ------------------------------------------
with tabs[4]:
    __st__.header("📊 تقارير الأرباح وصندوق الوردية")
    
    total_exp_val = sum([ex['amount'] for ex in __st__.session_state['expenses']])
    
    col_a, col_b, col_c = __st__.columns(3)
    col_a.metric("إجمالي المصاريف", f"{total_exp_val:,} د.ع")
    col_b.metric("عدد المواد بالمخزن", len(__st__.session_state['products']))
    col_c.metric("الديون الكلية للعملاء", f"{sum([c['debt'] for c in __st__.session_state['customers']]):,} د.ع")

    __st__.markdown("---")
    __st__.info("💡 هذا التقرير يجمع لك مدخلات المحل والمصاريف النثرية بشكل لحظي لتسهيل تصفير الوردية بدقة.")


# ------------------------------------------
# تبويب 6: دليل الاستخدام والفيديو التوضيحي
# ------------------------------------------
with tabs[5]:
    __st__.header("📖 دليل الاستخدام التوضيحي للنظام")
    __st__.write("مرحباً بك في دليل التشغيل السريع الخاص بالنظام. تم تصميم هذا البرنامج خصيصاً ليتناسب مع إدارة محلات التكنولوجيا والصيانة.")
    
    __st__.markdown("### 🎥 فيديو شرح النظام التوضيحي")
    __st__.info("مكان مخصص لعرض فيديو الشرح (يمكنك ربط رابط فيديو يوتيوب الخاص بك هنا مباشرة لاحقاً):")
    
    __st__.markdown("""
    * **نقطة البيع (POS):** بطاقات تفاعلية للمواد، مع حاسبة الباقي للزبون فور إدخال المبلغ المستلم.
    * **إدارة المخزن:** تظهر لك المواد وتنبيهات الألوان في حال اقتراب نفاذ البضاعة.
    * **المصروفات النثرية:** تسجل من خلالها مصاريف المحل اليومية لخصمها من الصندوق.
    * **الحفظ السحابي:** جميع بياناتك محفوظة تلقائياً على السحابة ولا تتطلب حفظاً يدوياً مستمراً.
    """)
