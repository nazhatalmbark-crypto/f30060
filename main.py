import streamlit as st
import sqlite3

# --- إعدادات الصفحة ---
st.set_page_config(page_title="ياسر ويب - النظام التجريبي الذكي", layout="wide")

# --- تهيئة الحالة وقاعدة البيانات ---
if 'is_unlocked' not in st.session_state: st.session_state.is_unlocked = False
if 'cart' not in st.session_state: st.session_state.cart = []

def init_db():
    conn = sqlite3.connect('yasser_web.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity INTEGER, price INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- الشريط الجانبي (التفعيل) ---
st.sidebar.title("🔐 لوحة التحكم والتفعيل")
if not st.session_state.is_unlocked:
    st.sidebar.info("💡 **نسخة تجريبية مفتوحة المميزات بحدود استهلاك.** جرب كل شيء بحرية!")
    code = st.sidebar.text_input("أدخل كود التفعيل لرفع الحدود نهائياً:", type="password")
    if st.sidebar.button("تفعيل النسخة الكاملة"):
        if code == "2009": # كود التفعيل السري الخاص بك
            st.session_state.is_unlocked = True
            st.sidebar.success("تم تفعيل النسخة الكاملة بلا حدود!")
            st.rerun()
        else:
            st.sidebar.error("كود غير صحيح!")
else:
    st.sidebar.success("✅ النسخة الكاملة مفعلة (بلا حدود)")
    if st.sidebar.button("إلغاء التفعيل للرجوع للتجريبي"):
        st.session_state.is_unlocked = False
        st.rerun()

# --- عنوان الشاشة والعداد الفوق ---
col_h1, col_h2 = st.columns([3, 1])
col_h1.title("📦 ياسر ويب - نظام إدارة المبيعات")
col_h2.metric("عربات المشتريات 🛒", len(st.session_state.cart))

# --- التبويبات الرئيسية ---
tab1, tab2, tab3 = st.tabs(["🛒 شبكة المواد والبيع", "📊 التقارير والتجربة", "⚙️ إضافة مواد للمخزن"])

# --- تبويب 1: شبكة المواد (الكارتات وسرعة البيع) ---
with tab1:
    st.subheader("اختر المواد للبيع السريع:")
    items = sqlite3.connect('yasser_web.db').cursor().execute("SELECT id, name, quantity, price FROM inventory").fetchall()
    
    if items:
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"### 🏷️ {item[1]}")
                    st.write(f"السعر: {item[3]:,} د.ع")
                    st.write(f"المتوفر بالمخزن: {item[2]}")
                    
                    # زر الإضافة السري
                    if st.button(f"إضافة للسلة ➕", key=f"add_{item[0]}"):
                        st.session_state.cart.append(item)
                        st.toast(f"تمت إضافة {item[1]} للسلة بنجاح!", icon="✅")
                        st.rerun()
    else:
        st.info("المخزن فارغ حالياً. أضف بعض المواد من تبويب 'إضافة مواد للمخزن'.")

    st.divider()
    st.subheader("🛒 سلة المشتريات الحالية والفاتورة")
    if st.session_state.cart:
        grand_total = 0
        for idx, c_item in enumerate(st.session_state.cart):
            st.write(f"{idx+1}. {c_item[1]} - السعر: {c_item[3]:,} د.ع")
            grand_total += c_item[3]
        
        st.markdown(f"### الإجمالي الكلي: `{grand_total:,} د.ع`")
        
        if st.button("✅ إتمام عملية البيع وخصم الكمية"):
            conn = sqlite3.connect('yasser_web.db')
            c = conn.cursor()
            for c_item in st.session_state.cart:
                c.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (c_item[0],))
            conn.commit()
            conn.close()
            st.session_state.cart = []
            st.success("تم إتمام البيع بنجاح وقص المواد من المخزن!")
            st.rerun()
    else:
        st.info("السلة فارغة.")

# --- تبويب 2: التقارير (معاينة تجريبية) ---
with tab2:
    st.subheader("📊 لوحة التقارير والأرباح")
    if not st.session_state.is_unlocked:
        st.warning("⚠️ **أنت تستخدم المعاينة التجريبية للتقارير.** (النسخة الكاملة تتيح تصدير التقارير وتحليل حركة الأرباح بدقة مفصلة).")
    
    items = sqlite3.connect('yasser_web.db').cursor().execute("SELECT name, quantity, price FROM inventory").fetchall()
    if items:
        total_val = sum([i[1] * i[2] for i in items])
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("إجمالي قيمة المخزن التجريبي", f"{total_val:,} د.ع")
        col_r2.metric("عدد الأصناف", len(items))
        
        chart_data = {i[0]: i[1] * i[2] for i in items}
        st.bar_chart(chart_data)
    else:
        st.info("لا توجد بيانات كافية لعرض التقارير.")

# --- تبويب 3: إضافة مواد (مع تطبيق قيد النسخة المجانية) ---
with tab3:
    st.subheader("⚙️ إدارة المخزن وإضافة المواد")
    if not st.session_state.is_unlocked:
        st.info("ℹ️ **ملاحظة للنسخة التجريبية:** يمكنك إضافة مواد بحرية، ولكن بحد أقصى **100 قطعة** في الإدخال الواحد. أدخل كود التفعيل لرفع هذا القيد تماماً.")
    
    with st.form("add_form"):
        name = st.text_input("اسم المادة الجديدة").strip()
        qty = st.number_input("الكمية", min_value=1, value=10)
        price = st.number_input("السعر بالدينار", min_value=0, value=1000)
        
        if st.form_submit_button("حفظ المادة في المخزن"):
            if not st.session_state.is_unlocked and qty > 100:
                st.error("⚠️ عذراً! النسخة التجريبية تحصر الإدخال بـ 100 قطعة كحد أقصى لكل عملية. أدخل كود التفعيل لإلغاء هذا القيد.")
            elif name:
                conn = sqlite3.connect('yasser_web.db')
                c = conn.cursor()
                # التحقق إذا المادة موجودة مسبقاً
                existing = c.execute("SELECT id, quantity FROM inventory WHERE name = ?", (name,)).fetchone()
                if existing:
                    new_q = existing[1] + qty
                    c.execute("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (new_q, price, existing[0]))
                    st.success(f"تم تحديث مادة '{name}' بنجاح! الكمية الجديدة: {new_q}")
                else:
                    c.execute("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
                    st.success(f"تم إضافة مادة '{name}' بنجاح للمخزن!")
                conn.commit()
                conn.close()
                st.rerun()
            else:
                st.error("الرجاء إدخال اسم المادة على الأقل.")
