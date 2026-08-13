import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Yasser Web - نظام المبيعات والمخازن", page_icon="📊", layout="wide")

# التنسيق والألوان
st.markdown("""
    <style>
    body { direction: rtl; text-align: right; }
    .stApp { direction: rtl; }
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 { text-align: right; }
    .demo-banner {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ffeeba;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .locked-feature {
        background-color: #f8d7da;
        color: #721c24;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #f5c6cb;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# تهيئة الذاكرة المؤقتة (Session State)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"كود": "101", "الاسم": "قميص رجالي", "الفئة": "ملابس رجالي", "سعر الشراء": 10000, "سعر البيع": 15000, "الكمية": 20},
        {"كود": "102", "الاسم": "بنطلون جينز", "الفئة": "ملابس رجالي", "سعر الشراء": 12000, "سعر البيع": 20000, "الكمية": 15},
        {"كود": "103", "الاسم": "فستان سهرة", "الفئة": "ملابس نسائية", "سعر الشراء": 25000, "سعر البيع": 40000, "الكمية": 8},
    ])

if 'sales' not in st.session_state:
    st.session_state.sales = []

if 'expenses' not in st.session_state:
    st.session_state.expenses = []

# --- شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول - Yasser Web")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة السر", type="password")
        if st.button("دخول للنظام", use_container_width=True):
            if username == "demo" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.user = "demo"
                st.rerun()
            elif username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.user = "admin"
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة السر غير صحيحة!")
        
        st.info("💡 لتجربة النظام: استخدم اسم المستخدم `demo` وكلمة السر `1234`")
    st.stop()

# تحديد هل المستخدم تجريبي أم أدمن
is_demo = (st.session_state.user == "demo")

# --- القائمة الجانبية ---
st.sidebar.title("📊 Yasser Web")
if is_demo:
    st.sidebar.markdown("""
    <div class="demo-banner">
        ⚠️ النسخة التجريبية (Demo Mode)
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.success("✅ النسخة الكاملة (الأدمن)")

page = st.sidebar.radio("القائمة الرئيسية", [
    "🛒 نقطة البيع (الفواتير)",
    "📦 إدارة المخزن",
    "💸 المصاريف",
    "📈 التقارير والأرباح",
])

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# ------------------ 1. نقطة البيع والفواتير ------------------
if page == "🛒 نقطة البيع (الفواتير)":
    st.header("🛒 إنشاء فاتورة مبيعات جديدة")
    
    if is_demo:
        st.warning("⚠️ ملاحظة: الفواتير في النسخة التجريبية تحمل علامة مائية مخصصة للعرض فقط.")

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("إضافة مواد للفاتورة")
        inv_df = st.session_state.inventory
        if not inv_df.empty:
            item_selected = st.selectbox("اختر المادة من المخزن", inv_df['الاسم'].tolist())
            item_row = inv_df[inv_df['الاسم'] == item_selected].iloc[0]
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.write(f"**السعر:** {item_row['سعر البيع']:,} د.ع")
            with col_b:
                st.write(f"**المتوفر بالمخزن:** {item_row['الكمية']}")
            with col_c:
                qty = st.number_input("الكمية المطلوبة", min_value=1, max_value=int(item_row['الكمية']) if item_row['الكمية'] > 0 else 1, value=1)
            
            if st.button("➕ إضافة المادة للفاتورة"):
                if item_row['الكمية'] >= qty:
                    st.session_state.cart.append({
                        "كود": item_row['كود'],
                        "الاسم": item_row['الاسم'],
                        "سعر البيع": item_row['سعر البيع'],
                        "سعر الشراء": item_row['سعر الشراء'],
                        "الكمية": qty,
                        "الإجمالي": item_row['سعر البيع'] * qty
                    })
                    st.success(f"تمت إضافة ({item_row['الاسم']}) للفاتورة")
                else:
                    st.error("الكمية المتوفرة بالمخزن غير كافية!")

    with col_right:
        st.subheader("🧾 تفاصيل الفاتورة")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df[['الاسم', 'الكمية', 'الإجمالي']], hide_index=True)
            
            subtotal = cart_df['الإجمالي'].sum()
            st.write(f"### المجموع: {subtotal:,} د.ع")
            
            # نظام الخصومات
            discount_type = st.radio("نوع الخصم", ["مبلغ ثابت", "نسبة مئوية %"], horizontal=True)
            discount_val = st.number_input("قيمة الخصم", min_value=0.0, value=0.0)
            
            if discount_type == "نسبة مئوية %":
                discount_amount = (subtotal * discount_val) / 100
            else:
                discount_amount = discount_val
                
            final_total = max(0.0, subtotal - discount_amount)
            st.write(f"## 💥 الصافي النهائي: {final_total:,.0f} د.ع")
            
            if st.button("✅ إتمام البيع وطباعة الفاتورة", type="primary"):
                sale_id = f"INV-{len(st.session_state.sales) + 1001}"
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # خصم الكمية من المخزن
                for cart_item in st.session_state.cart:
                    st.session_state.inventory.loc[
                        st.session_state.inventory['كود'] == cart_item['كود'], 'الكمية'
                    ] -= cart_item['الكمية']
                    
                st.session_state.sales.append({
                    "رقم الفاتورة": sale_id,
                    "التاريخ": now_str,
                    "المجموع": subtotal,
                    "الخصم": discount_amount,
                    "الصافي": final_total,
                    "الربح": sum([(x['سعر البيع'] - x['سعر الشراء']) * x['الكمية'] for x in st.session_state.cart]) - discount_amount
                })
                
                st.success("تم تسجيل عملية البيع بنجاح!")
                
                # طباعة الفاتورة بـ HTML
                watermark_html = """<div style="color: red; font-size: 16px; font-weight: bold; border: 2px dashed red; padding: 8px; text-align: center; margin-bottom: 10px;">
                    ⚠️ نسخة تجريبية غير مخصصة للبيع - Yasser Web ⚠️
                </div>""" if is_demo else ""
                
                receipt_items = "".join([f"<tr><td style='padding:5px;'>{i['الاسم']}</td><td style='padding:5px;'>{i['الكمية']}</td><td style='padding:5px;'>{i['الإجمالي']:,} د.ع</td></tr>" for i in st.session_state.cart])
                
                receipt_code = f"""
                <div style="border: 1px solid #ccc; padding: 15px; font-family: Tahoma, Arial; direction: rtl; max-width: 400px; margin: auto;">
                    {watermark_html}
                    <h2 style="text-align: center; margin-bottom: 5px;">Yasser Web</h2>
                    <p style="text-align: center; margin-top: 0;">نظام إدارة المبيعات والمخازن</p>
                    <hr>
                    <p><b>رقم الفاتورة:</b> {sale_id}</p>
                    <p><b>التاريخ:</b> {now_str}</p>
                    <table style="width: 100%; text-align: right; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            <tr style="background-color: #f2f2f2; border-bottom: 1px solid #ddd;">
                                <th style='padding:5px;'>المادة</th><th style='padding:5px;'>الكمية</th><th style='padding:5px;'>السعر</th>
                            </tr>
                        </thead>
                        <tbody>
                            {receipt_items}
                        </tbody>
                    </table>
                    <hr>
                    <p><b>المجموع:</b> {subtotal:,} د.ع</p>
                    <p><b>الخصم:</b> {discount_amount:,.0f} د.ع</p>
                    <h3><b>الصافي:</b> {final_total:,.0f} د.ع</h3>
                    <hr>
                    <p style="text-align: center; font-size: 12px; color: #777;">شكراً لتسوقكم معنا!</p>
                </div>
                """
                st.components.v1.html(receipt_code, height=450, scrolling=True)
                st.session_state.cart = []
        else:
            st.info("الفاتورة فارغة حالياً")

# ------------------ 2. إدارة المخزن ------------------
elif page == "📦 إدارة المخزن":
    st.header("📦 إدارة المواد والمخزن")
    
    # القيد التجريبي
    if is_demo:
        st.info("💡 النسخة التجريبية تسمح لك بإضافة حتى 5 مواد فقط بالمخزن.")
        if len(st.session_state.inventory) >= 5:
            st.markdown("""
            <div class="locked-feature">
                🔒 <b>وصلت للحد الأقصى في النسخة التجريبية (5 مواد)</b><br><br>
                لإضافة عدد غير محدود من المواد والكتالوجات وتصدير بيانات مخزنك، يرجى الترقية للنسخة الكاملة.<br><br>
                📲 تواصل معنا لتفعيل محلك: <b>@yaser177841</b>
            </div>
            """, unsafe_allow_html=True)
    
    # نموذج إضافة مادة جديدة
    if not is_demo or len(st.session_state.inventory) < 5:
        with st.expander("➕ إضافة مادة جديدة للمخزن"):
            col1, col2, col3 = st.columns(3)
            with col1:
                code = st.text_input("كود المادة")
                name = st.text_input("اسم المادة")
            with col2:
                category = st.selectbox("الفئة / القسم", ["ملابس رجالي", "ملابس نسائية", "أطفال", "كوزمتك", "أحذية وحقائب", "عام"])
                qty = st.number_input("الكمية البدائية", min_value=1, value=10)
            with col3:
                cost_price = st.number_input("سعر الشراء (التكلفة)", min_value=0, value=5000)
                sell_price = st.number_input("سعر البيع", min_value=0, value=10000)
            
            if st.button("حفظ المادة"):
                if code and name:
                    new_item = pd.DataFrame([{
                        "كود": code,
                        "الاسم": name,
                        "الفئة": category,
                        "سعر الشراء": cost_price,
                        "سعر البيع": sell_price,
                        "الكمية": qty
                    }])
                    st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                    st.success(f"تمت إضافة المادة ({name}) بنجاح!")
                    st.rerun()
                else:
                    st.error("يرجى ملء الكود واسم المادة!")

    st.subheader("📋 قائمة المواد المخزنة")
    st.dataframe(st.session_state.inventory, use_container_width=True, hide_index=True)

# ------------------ 3. المصاريف ------------------
elif page == "💸 المصاريف":
    st.header("💸 تسجيل المصاريف اليومية")
    
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            exp_title = st.text_input("عنوان المصروف (مثلاً: إيجار، كهرباء، أكياس)")
        with col2:
            exp_amount = st.number_input("المبلغ (د.ع)", min_value=0, value=5000)
        
        exp_submit = st.form_submit_button("تسجيل المصروف")
        if exp_submit and exp_title:
            st.session_state.expenses.append({
                "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "المصروف": exp_title,
                "المبلغ": exp_amount
            })
            st.success("تم تسجيل المصروف بنجاح!")

    if st.session_state.expenses:
        st.subheader("📋 سجل المصاريف")
        st.dataframe(pd.DataFrame(st.session_state.expenses), use_container_width=True, hide_index=True)

# ------------------ 4. التقارير والأرباح ------------------
elif page == "📈 التقارير والأرباح":
    st.header("📈 تقارير الأرباح والمبيعات")
    
    if is_demo:
        st.markdown("""
        <div class="locked-feature">
            🔒 <b>تقارير الأرباح المتقدمة وتصدير ملفات Excel مقفلة في النسخة التجريبية</b><br><br>
            في النسخة الكاملة الخاصة بمحلك ستحصل على:<br>
            • حساب أوتوماتيكي لصافي الربح النهائي (المبيعات - المصاريف).<br>
            • تقارير يومية وشهرية دقيقة.<br>
            • تصدير واستخراج كافة الحسابات بملفات Excel بضغطة زر.<br><br>
            📲 لتفعيل النسخة الكاملة الخاصة بمحلك بالبصرة، تواصل معنا عبر إنستغرام: <b>@yaser177841</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("لمحة عن شكل تقارير النسخة الكاملة:")
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي المبيعات", "150,000 د.ع (عرض تجريبي)")
        col2.metric("إجمالي المصاريف", "10,000 د.ع (عرض تجريبي)")
        col3.metric("صافي الربح", "45,000 د.ع (عرض تجريبي)")
    else:
        # عرض التقارير الكاملة للأدمن
        sales_list = st.session_state.sales
        exp_list = st.session_state.expenses
        
        total_sales = sum([s['الصافي'] for s in sales_list]) if sales_list else 0
        total_profit = sum([s['الربح'] for s in sales_list]) if sales_list else 0
        total_exp = sum([e['المبلغ'] for e in exp_list]) if exp_list else 0
        net_profit = total_profit - total_exp
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("إجمالي المبيعات", f"{total_sales:,.0f} د.ع")
        col2.metric("أرباح المبيعات", f"{total_profit:,.0f} د.ع")
        col3.metric("المصاريف", f"{total_exp:,.0f} د.ع")
        col4.metric("صافي الربح النهائي", f"{net_profit:,.0f} د.ع")
        
        st.subheader("📑 سجل الفواتير المباعة")
        if sales_list:
            sales_df = pd.DataFrame(sales_list)
            st.dataframe(sales_df[['رقم الفاتورة', 'التاريخ', 'المجموع', 'الخصم', 'الصافي', 'الربح']], use_container_width=True, hide_index=True)
