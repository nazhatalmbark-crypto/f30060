import streamlit as st
import pandas as pd
import datetime
import io
import urllib.parse
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# إعداد الصفحة
st.set_page_config(page_title="نظام إدارة المبيعات - Yasser Web", layout="wide")

# تهيئة الـ Session State المتغيرات الأساسية
if "invoices_list" not in st.session_state:
    st.session_state.invoices_list = []
if "customer_list" not in st.session_state:
    st.session_state.customer_list = []
if "expenses_list" not in st.session_state:
    st.session_state.expenses_list = []
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

def log_audit(action, details):
    st.session_state.audit_logs.append({
        "العملية": action,
        "التفاصيل": details,
        "الوقت": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

def generate_pdf_invoice(inv):
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"Invoice No: {inv['رقم الفاتورة']}")
        c.drawString(100, 730, f"Customer: {inv['الزبون']}")
        c.drawString(100, 710, f"Date: {inv['التاريخ']}")
        c.drawString(100, 690, f"Items: {inv['المنتجات']}")
        c.drawString(100, 670, f"Total: {inv['المبلغ الكلي']} IQD")
        c.drawString(100, 650, f"Paid: {inv['الواصل']} IQD")
        c.drawString(100, 630, f"Remaining: {inv['المتبقي (الدين)']} IQD")
        c.save()
        buffer.seek(0)
        return buffer
    except Exception:
        return None

# تعريف جميع التبويبات في بداية الواجهة لتجنب الأخطاء
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📦 المواد", 
    "📊 المخزن", 
    "👥 العملاء والموردين", 
    "🛒 نظام البيع", 
    "📋 السلة والفواتير", 
    "📜 سجل الفواتير وواتساب", 
    "💰 صندوق الوردية", 
    "📈 التقارير والرسوم", 
    "🔍 سجل النشاطات", 
    "📖 الدعم الفني"
])

with tab1:
    st.subheader("📦 إدارة المواد والمنتجات")
    st.info("قسم إدخال وتسجيل المواد والمنتجات في النظام.")

with tab2:
    st.subheader("📊 جرد المخزن")
    st.info("مراقبة المخزون والمنتجات.")

with tab3:
    st.subheader("👥 إدارة العملاء والموردين")
    # مثال مبسط لتسجيل العملاء لكي تظهر أسماؤهم في الفواتير
    with st.form("add_cust_form", clear_on_submit=True):
        c_name = st.text_input("اسم العميل:")
        c_phone = st.text_input("رقم الهاتف (واتساب):")
        if st.form_submit_button("حفظ العميل"):
            if c_name.strip():
                st.session_state.customer_list.append({"اسم العميل": c_name.strip(), "رقم الهاتف": c_phone.strip()})
                st.success("تم حفظ العميل بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى كتابة اسم العميل على الأقل.")
    
    if st.session_state.customer_list:
        st.dataframe(pd.DataFrame(st.session_state.customer_list), use_container_width=True)

with tab4:
    st.subheader("🛒 نظام البيع السريع")
    st.info("واجهة إتمام عمليات البيع واختيار المواد.")

with tab5:
    st.subheader("📋 سلة المشتريات وإصدار الفواتير")
    st.info("إتمام الفاتورة وتثبيتها للسجل.")

with tab6:
    st.subheader("📜 سجل الفواتير وواتساب")
    if st.session_state.invoices_list:
        for inv in reversed(st.session_state.invoices_list):
            with st.container():
                col_inv1, col_inv2, col_inv3 = st.columns([2, 2, 2])
                with col_inv1:
                    st.markdown(f"#### {inv['رقم الفاتورة']} | الزبون: {inv['الزبون']}")
                    st.write(f"📅 التاريخ: {inv['التاريخ']}")
                    st.write(f"💳 الدفع: {inv['نوع الدفع']}")
                with col_inv2:
                    st.write(f"🛒 **المواد:** {inv['المنتجات']}")
                    st.write(f"💰 الكلي: `{inv['المبلغ الكلي']:,}` د.ع")
                    st.write(f"📥 الواصل: `{inv['الواصل']:,}` د.ع | المتبقي: `{inv['المتبقي (الدين)']:,}` د.ع")
                with col_inv3:
                    pdf_buffer = generate_pdf_invoice(inv)
                    if pdf_buffer:
                        st.download_button(
                            label="📄 تحميل فاتورة PDF",
                            data=pdf_buffer,
                            file_name=f"{inv['رقم الفاتورة']}_{inv['الزبون']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{inv['رقم الفاتورة']}"
                        )
                    
                    cust_phone_val = ""
                    for c_obj in st.session_state.customer_list:
                        if c_obj["اسم العميل"] == inv["الزبون"]:
                            cust_phone_val = c_obj["رقم الهاتف"]
                            break
                    
                    if cust_phone_val:
                        wa_msg = urllib.parse.quote(f"مرحباً بك استاذ {inv['الزبون']},\nنذكركم بوجود مبلغ متبقي (دين) بذمتكم لصالح محلنا بموجب الفاتورة رقم {inv['رقم الفاتورة']} وقدره {inv['المتبقي (الدين)']:,} دينار عراقي.\nشكراً لتعاملكم معنا!")
                        st.markdown(f"📱 [مراسلة العميل واتساب](https://wa.me/{cust_phone_val}?text={wa_msg})", unsafe_allow_html=True)

                    with st.expander("📌 QR Code الفاتورة"):
                        qr = qrcode.QRCode(version=1, box_size=5, border=2)
                        qr.add_data(f"Invoice: {inv['رقم الفاتورة']}, Customer: {inv['الزبون']}, Total: {inv['المبلغ الكلي']}, Remaining: {inv['المتبقي (الدين)']}")
                        qr.make(fit=True)
                        img_qr = qr.make_image(fill_color="black", back_color="white")
                        buf_qr = io.BytesIO()
                        img_qr.save(buf_qr)
                        st.image(buf_qr.getvalue(), width=130)
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن. يمكنك إضافة فواتير تجريبية أو عبر نظام البيع.")

with tab7:
    st.subheader("💰 صندوق الوردية والمصاريف اليومية")
    
    with st.form("add_expense_form", clear_on_submit=True):
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            exp_title = st.text_input("بيان المصروف (مثال: أجور كهرباء، إيجار، ضيافة):")
        with col_e2:
            exp_amount_str = st.text_input("المبلغ (د.ع):", "0")
            
        if st.form_submit_button("تسجيل وحفظ المصروف"):
            if exp_title.strip():
                try:
                    exp_amt = float(exp_amount_str.strip())
                    st.session_state.expenses_list.append({
                        "البيان": str(exp_title.strip()),
                        "المبلغ": int(exp_amt),
                        "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    log_audit("تسجيل مصروف", f"تم تسجيل مصروف ({exp_title.strip()}) بقيمة {int(exp_amt):,} د.ع")
                    st.success("✅ تم تسجيل المصروف بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("يرجى إدخال مبلغ صحيح.")
            else:
                st.warning("يرجى إدخال بيان المصروف.")

    st.divider()
    
    total_sales_cash = sum(inv['الواصل'] for inv in st.session_state.invoices_list)
    total_expenses = sum(exp['المبلغ'] for exp in st.session_state.expenses_list)
    net_cash_box = total_sales_cash - total_expenses
    
    col_box1, col_box2, col_box3 = st.columns(3)
    col_box1.metric("إجمالي الواصل من المبيعات", f"{int(total_sales_cash):,} د.ع")
    col_box2.metric("إجمالي المصاريف المسجلة", f"{int(total_expenses):,} د.ع")
    col_box3.metric("صافي الصندوق الحالي", f"{int(net_cash_box):,} د.ع")
    
    st.divider()
    st.subheader("📋 سجل المصاريف التفصيلي")
    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)
    else:
        st.info("لا توجد مصاريف مسجلة في هذه الوردية.")

with tab8:
    st.subheader("📊 الرسوم البيانية والتقارير المالية التحليلية")
    
    if st.session_state.invoices_list:
        df_inv = pd.DataFrame(st.session_state.invoices_list)
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.write("### 📈 حجم المبيعات حسب الفواتير")
            st.bar_chart(df_inv.set_index("رقم الفاتورة")["المبلغ الكلي"])
            
        with col_r2:
            st.write("### 📉 مقارنة المبالغ الواصلة والمتبقية")
            st.line_chart(df_inv.set_index("رقم الفاتورة")[["الواصل", "المتبقي (الدين)"]])
            
        total_rev = df_inv["المبلغ الكلي"].sum()
        total_cost = df_inv["تكلفتها"].sum() if "تكلفتها" in df_inv.columns else 0
        total_net_profit = total_rev - total_cost
        
        st.divider()
        st.metric("إجمالي الأرباح التقديرية الصافية للمبيعات المسجلة", f"{int(total_net_profit):,} دينار عراقي")
    else:
        st.info("لا توجد بيانات كافية لعرض الرسوم البيانية والتقارير حالياً.")

with tab9:
    st.subheader("📜 سجل النشاطات والعمليات (Audit Trail)")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد نشاطات مسجلة حتى الآن.")

with tab10:
    st.subheader("📖 دليل الاستخدام والمميزات والدعم الفني")
    st.markdown("""
    * **إضافة المواد:** تسجيل المنتجات مع تحديد أسعار الشراء، البيع، الكمية، والباركود.
    * **جرد المخزن:** مراقبة المواد منخفضة المخزون وتوليد أكواد باركود لكل منتج.
    * **العملاء والموردين:** إدارة سجل الزبائن والمحافظات العراقية بالإضافة إلى شركات التجهيز.
    * **نظام السلة والفواتير:** تجميع المواد، حساب الخصم أو الدين، وطبع فواتير PDF رسمية.
    * **التواصل عبر واتساب:** إرسال تذكيرات بالديون مباشرة للعملاء بنقرة زر واحدة.
    * **صندوق الوردية:** متابعة المصاريف اليومية وصافي الأرباح بدقة عالية.
    """)
    st.success("📞 للتواصل والدعم الفني والنظام الشامل: مبرمج ومطور الأنظمة **ياسر المبارك** (البصرة، العراق).")
