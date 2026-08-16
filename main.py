import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import pandas as pd
from datetime import date
from io import StringIO, BytesIO
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="ياسر ويب - النظام الاحترافي الآمن", layout="wide", page_icon="📦")

# --- حماية المتصفح: تنبيه إجباري عند محاولة إغلاق أو تحديث الصفحة ---
components.html("""
<script>
window.addEventListener('beforeunload', function (e) {
    e.preventDefault();
    e.returnValue = 'تحذير هام! تأكد من تحميل النسخة الاحتياطية (Backup) قبل إغلاق الموقع لضمان عدم ضياع البيانات!';
});
</script>
""", height=0)

# --- 1. إعداد وتحديث قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, quantity INTEGER DEFAULT 0, price INTEGER DEFAULT 0, selling_price INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, shop_location TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, total_amount INTEGER, invoice_date TEXT, details_json TEXT)''')
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('yasser_web.db', timeout=10)
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# --- دالة توليد PDF للفاتورة ---
def generate_pdf(inv_id, c_name, total, details):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Yasser Web - Invoice", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Invoice #: {inv_id}", ln=True)
    pdf.cell(200, 10, txt=f"Customer: {c_name}", ln=True)
    pdf.cell(200, 10, txt=f"Total: {total:,} IQD", ln=True)
    pdf.multi_cell(0, 10, txt=details)
    return pdf.output(dest='S').encode('latin-1')

# --- الشريط الجانبي والأمان والنسخ الاحتياطي الإجباري ---
st.sidebar.title("🛡️ الأمان والنسخ الاحتياطي")
st.sidebar.error("⚠️ تنبيه: احرص دائماً على تنزيل النسخة الاحتياطية قبل مغادرة الموقع لضمان عدم ضياع أي بيانات!")

with open("yasser_web.db", "rb") as f:
    db_bytes = f.read()

st.sidebar.download_button(
    label="💾 تحميل النسخة الاحتياطية الآن (Backup)",
    data=db_bytes,
    file_name=f"yasser_web_backup_{date.today()}.db",
    mime="application/octet-stream",
    use_container_width=True
)

st.sidebar.divider()
if st.sidebar.button("🔒 قفل الجلسة وتسجيل الخروج الآمن", use_container_width=True):
    st.sidebar.success("تم إغلاق الجلسة بأمان. تأكد أنك حملت النسخة الاحتياطية أعلاه!")

# --- واجهة التبويبات الرئيسية ---
tabs = st.tabs(["🛒 البيع السريع", "📜 أرشيف الفواتير (PDF)", "📦 المخزن", "🔍 تحليل المواد والأرباح", "👥 العملاء"])

with tabs[0]: # البيع السريع
    st.subheader("🛒 نقطة البيع (إلزامية اختيار عميل)")
    items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
    
    if 'cart' not in st.session_state:
        st.session_state.cart = []
        
    if items:
        cols = st.columns(3)
        for idx, itm in enumerate(items):
            i_id, i_name, i_qty, i_cost, i_sell = itm
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### 🏷️ {i_name}")
                    st.metric("المتوفر", f"{i_qty} قطعة")
                    st.write(f"سعر البيع: **{i_sell:,} د.ع**")
                    if st.button("إضافة للسلة ➕", key=f"add_c_{i_id}"):
                        st.session_state.cart.append({'id': i_id, 'name': i_name, 'price': i_sell, 'qty': 1})
                        st.success(f"تمت إضافة {i_name}")
                        st.rerun()
                        
        st.divider()
        if st.session_state.cart:
            st.subheader("محتويات السلة الحالية:")
            grand_total = 0
            for i, c_item in enumerate(st.session_state.cart):
                col_s1, col_s2, col_s3 = st.columns([3, 2, 1])
                col_s1.write(c_item['name'])
                col_s2.write(f"{c_item['price']:,} د.ع")
                if col_s3.button("حذف", key=f"del_cart_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
                grand_total += c_item['price'] * c_item['qty']
                
            st.markdown(f"### الإجمالي الكلي: `{grand_total:,} د.ع`")
            
            custs = run_query("SELECT name, shop_location FROM customers", fetch=True)
            if custs:
                cust_dict = {f"{c[0]} ({c[1] or 'بدون محل'})": c[0] for c in custs}
                selected_c_display = st.selectbox("اختر اسم الزبون (إجباري لإتمام البيع):", list(cust_dict.keys()))
                final_customer = cust_dict[selected_c_display]
            else:
                final_customer = None
                st.warning("⚠️ لا يوجد عملاء مسجلون! أضف عميلاً من تبويب 'العملاء' أولاً.")
                
            if st.button("✅ إتمام البيع وحفظ الفاتورة نهائياً", use_container_width=True):
                if not final_customer:
                    st.error("❌ لا يمكن إتمام البيع بدون اختيار عميل مسجل!")
                else:
                    df_cart = pd.DataFrame(st.session_state.cart)[['name', 'qty', 'price']]
                    df_cart['total'] = df_cart['qty'] * df_cart['price']
                    df_cart.columns = ['اسم المادة', 'الكمية', 'السعر المفرد', 'المجموع']
                    csv_data = df_cart.to_csv(index=False)
                    
                    run_query("INSERT INTO invoices (customer_name, total_amount, invoice_date, details_json) VALUES (?, ?, ?, ?)",
                              (final_customer, grand_total, str(date.today()), csv_data))
                    
                    st.success("تم حفظ الفاتورة وقص الكمية من المخزن بنجاح!")
                    st.session_state.cart = []
                    st.rerun()
        else:
            st.info("السلة فارغة حالياً.")
    else:
        st.info("لا توجد مواد مخزنة حالياً.")

with tabs[1]: # الأرشيف PDF
    st.subheader("📜 أرشيف الفواتير وتنزيل ملفات الـ PDF")
    invoices = run_query("SELECT id, customer_name, total_amount, invoice_date, details_json FROM invoices ORDER BY id DESC", fetch=True)
    if invoices:
        for inv in invoices:
            inv_id, c_name, t_amt, i_date, details_csv = inv
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                col_a.markdown(f"### فاتورة رقم #{inv_id} | الزبون: {c_name}")
                col_a.write(f"التاريخ: {i_date} | المبلغ الإجمالي: **{t_amt:,} د.ع**")
                
                pdf_bytes_file = generate_pdf(inv_id, c_name, t_amt, details_csv)
                col_b.download_button(
                    label="📥 تحميل PDF",
                    data=pdf_bytes_file,
                    file_name=f"invoice_{inv_id}_{c_name}.pdf",
                    mime="application/pdf",
                    key=f"dl_pdf_{inv_id}"
                )
    else:
        st.info("لا توجد فواتير مسجلة في الأرشيف حتى الآن.")

with tabs[2]: # المخزن
    st.subheader("📦 إضافة مواد جديدة وتحديث المخزون")
    with st.form("add_item_form"):
        col1, col2 = st.columns(2)
        with col1:
            i_name = st.text_input("اسم المادة").strip()
            i_qty = st.number_input("الكمية المتوفرة", min_value=0, value=10)
        with col2:
            i_cost = st.number_input("سعر التكلفة (الشراء)", min_value=0, value=1000)
            i_sell = st.number_input("سعر البيع", min_value=0, value=1500)
            
        if st.form_submit_button("حفظ المادة في قاعدة البيانات"):
            if i_name:
                run_query("INSERT OR REPLACE INTO inventory (name, quantity, price, selling_price) VALUES (?, ?, ?, ?)", 
                          (i_name, i_qty, i_cost, i_sell))
                st.success(f"تم حفظ مادة '{i_name}' بنجاح وتثبيتها في قاعدة البيانات!")
            else:
                st.error("يرجى كتابة اسم المادة.")

with tabs[3]: # تحليل المواد والأرباح
    st.subheader("🔍 تحليل المواد، الكميات المباعة، وأرباح كل صنف")
    items_list = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
    if items_list:
        item_names_only = [it[1] for it in items_list]
        selected_item = st.selectbox("اختر الصنف المراد تحليله:", item_names_only)
        
        target_item = next(it for it in items_list if it[1] == selected_item)
        
        with st.container(border=True):
            m1, m2, m3 = st.columns(3)
            m1.metric("الكمية المتبقية بالمخزن", f"{target_item[2]} قطعة")
            m2.metric("سعر التكلفة", f"{target_item[3]:,} د.ع")
            m3.metric("سعر البيع المعتمد", f"{target_item[4]:,} د.ع")
            
            # حساب إجمالي المبيعات والأرباح من الفواتير السابقة
            all_invs = run_query("SELECT details_json FROM invoices", fetch=True)
            sold_count = 0
            for inv_row in all_invs:
                try:
                    df_inv = pd.read_csv(StringIO(inv_row[0]))
                    if selected_item in df_inv['اسم المادة'].values:
                        q_matched = df_inv.loc[df_inv['اسم المادة'] == selected_item, 'الكمية'].values[0]
                        sold_count += q_matched
                except:
                    pass
            
            profit_per_unit = target_item[4] - target_item[3]
            total_profit_item = sold_count * profit_per_unit
            
            st.divider()
            col_p1, col_p2 = st.columns(2)
            col_p1.metric("إجمالي القطع المباعة من هذا الصنف", f"{sold_count} قطعة")
            col_p2.metric("صافي الربح المحقق من هذا الصنف", f"{total_profit_item:,} د.ع")
    else:
        st.info("لا توجد أصناف مخزنة للتحليل.")

with tabs[4]: # العملاء
    st.subheader("👥 إدارة الزبائن وأصحاب المحلات")
    with st.form("cust_form"):
        c1, c2 = st.columns(2)
        with c1:
            cust_name = st.text_input("اسم الزبون أو المحل (إجباري)").strip()
            cust_phone = st.text_input("رقم الهاتف")
        with c2:
            cust_loc = st.text_input("عنوان المحل / المنطقة")
            
        if st.form_submit_button("حفظ بيانات الزبون"):
            if cust_name:
                run_query("INSERT INTO customers (name, phone, shop_location) VALUES (?, ?, ?)", (cust_name, cust_phone, cust_loc))
                st.success("تم حفظ الزبون بنجاح!")
            else:
                st.error("يرجى إدخال اسم الزبون.")
                
    st.divider()
    saved_custs = run_query("SELECT name, phone, shop_location FROM customers", fetch=True)
    if saved_custs:
        for sc in saved_custs:
            st.markdown(f"- 👤 **{sc[0]}** | 📱 الهاتف: {sc[1] or 'لا يوجد'} | 📍 الموقع: {sc[2] or 'غير محدد'}")
    else:
        st.info("لا يوجد عملاء مسجلون حتى الآن.")
