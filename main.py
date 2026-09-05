import streamlit as st
import pandas as pd
import datetime

# تعريف دالة السجل التدقيقي ومولد الـ PDF إن لم تكن معرفة مسبقاً
def log_audit(action, details):
    if 'audit_logs' not in st.session_state:
        st.session_state.audit_logs = []
    st.session_state.audit_logs.append({
        "التاريخ والوقت": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "النشاط": action,
        "التفاصيل": details
    })

def generate_pdf_invoice(inv):
    # دالة وهمية أو استبدالها بدالتك الفعلية لتوليد الـ PDF
    return None

# تهيئة المتغيرات في session_state إذا لم تكن موجودة
if 'invoices_list' not in st.session_state:
    st.session_state.invoices_list = []
if 'expenses_list' not in st.session_state:
    st.session_state.expenses_list = []
if 'audit_logs' not in st.session_state:
    st.session_state.audit_logs = []

# تعريف التبويبات العشرة للبرنامج بالكامل
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📦 المخزون", 
    "👥 العملاء", 
    "🛒 نقطة البيع", 
    "🔄 المرتجعات", 
    "💵 سندات القبض", 
    "📄 الفواتير والـ PDF", 
    "💰 الصندوق والمصاريف", 
    "📈 التقارير والأرباح", 
    "📜 سجل النشاطات", 
    "📖 دليل الاستخدام"
])

with tab6:
    st.subheader("📄 سجل الفواتير، تحميل PDF، ومطالبة الديون عبر واتساب و QR Code")
    
    if st.session_state.invoices_list:
        if st.button("🗑️ مسح سجل الفواتير القديم"):
            st.session_state.invoices_list = []
            log_audit("مسح سجل", "تم مسح سجل الفواتير بالكامل")
            st.success("تم مسح السجل بنجاح.")
            st.rerun()
            
        for inv in reversed(st.session_state.invoices_list):
            with st.container(border=True):
                col_inv1, col_inv2, col_inv3 = st.columns([2, 2, 2])
                with col_inv1:
                    st.markdown(f"#### 📄 {inv.get('رقم الفاتورة', '')}")
                    st.write(f"👤 **الزبون:** {inv.get('الزبون', '')}")
                    st.write(f"📅 **التاريخ:** {inv.get('التاريخ', '')}")
                with col_inv2:
                    st.write(f"🛍️ **المنتجات:** {inv.get('المنتجات', '')}")
                    st.write(f"💳 **طريقة الدفع:** {inv.get('نوع الدفع', '')}")
                with col_inv3:
                    st.markdown(f"💰 **المجموع الكلي:** `{inv.get('المبلغ الكلي', 0):,}` د.ع")
                    st.markdown(f"📥 **الواصل:** `{inv.get('الواصل', 0):,}` د.ع")
                    if inv.get('المتبقي (الدين)', 0) > 0:
                        st.markdown(f"🔴 **المتبقي (الدين):** `{inv.get('المتبقي (الدين)', 0):,}` د.ع")
                    else:
                        st.markdown(f"🟢 **المتبقي:** `0` د.ع (مسدد بالكامل)")

                pdf_buffer = generate_pdf_invoice(inv)
                if pdf_buffer:
                    st.download_button(
                        label=f"📥 تحميل فاتورة PDF رسمية ({inv.get('رقم الفاتورة', '')})",
                        data=pdf_buffer,
                        file_name=f"Invoice_{inv.get('رقم الفاتورة', '')}.pdf",
                        mime="application/pdf",
                        key=f"pdf_btn_{inv.get('رقم الفاتورة', '')}"
                    )
                else:
                    st.info("مكتبة توليد الـ PDF غير متوفرة حالياً.")
    else:
        st.info("لا توجد فواتير مسجلة حتى الآن.")

with tab7:
    st.subheader("💰 صندوق الوردية، حركة النقدية، وتسجيل المصاريف اليومية")
    
    with st.form("add_expense_form", clear_on_submit=True):
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            exp_title = st.text_input("بيان المصروف (مثلاً: إيجار، كهرباء، سحب شخصي):")
        with col_e2:
            exp_amount_str = st.text_input("مبلغ المصروف (د.ع):", "0")
            
        if st.form_submit_button("تسجيل وصم المصروف من الصندوق"):
            if exp_title.strip():
                try:
                    exp_amt = float(exp_amount_str.strip())
                    if exp_amt > 0:
                        st.session_state.expenses_list.append({
                            "البيان": str(exp_title.strip()),
                            "المبلغ": int(exp_amt),
                            "التاريخ": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                        })
                        log_audit("تسجيل مصروف", f"تم تسجيل مصروف ({exp_title.strip()}) بمبلغ {int(exp_amt):,} د.ع")
                        st.success("تم تسجيل المصروف بنجاح!")
                        st.rerun()
                    else:
                        st.warning("يرجى إدخال مبلغ صحيح أكبر من الصفر.")
                except ValueError:
                    st.error("خطأ: يرجى إدخال رقم صحيح للمبلغ.")
            else:
                st.warning("يرجى كتابة بيان المصروف.")

    st.divider()
    st.subheader("📊 ملخص حركة صندوق الوردية والمصاريف المسجلة")
    
    total_sales_cash = sum(int(inv.get('الواصل', 0)) for inv in st.session_state.invoices_list)
    total_expenses_sum = sum(int(ex.get('المبلغ', 0)) for ex in st.session_state.expenses_list)
    net_drawer_cash = total_sales_cash - total_expenses_sum
    
    col_box1, col_box2, col_box3 = st.columns(3)
    with col_box1:
        st.metric("إجمالي النقد الواصل للمبيعات", f"{total_sales_cash:,} د.ع")
    with col_box2:
        st.metric("إجمالي المصاريف المسحوبة", f"{total_expenses_sum:,} د.ع", delta_color="inverse")
    with col_box3:
        st.metric("صافي النقدية الحالية بالصندوق", f"{net_drawer_cash:,} د.ع")

    if st.session_state.expenses_list:
        st.write("### قائمة المصاريف التفصيلية:")
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)

with tab8:
    st.subheader("📈 الرسوم البيانية، تحليلات الأرباح، والتقارير المالية")
    
    if st.session_state.invoices_list:
        total_rev = sum(int(i.get('المبلغ الكلي', 0)) for i in st.session_state.invoices_list)
        total_cost_inv = sum(int(i.get('تكلفتها', 0)) for i in st.session_state.invoices_list)
        net_profit_val = total_rev - total_cost_inv
        
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.metric("إجمالي الإيرادات الكلية للمبيعات", f"{total_rev:,} د.ع")
        with c_m2:
            st.metric("إجمالي تكلفة البضاعة المباعة", f"{total_cost_inv:,} د.ع")
        with c_m3:
            st.metric("صافي الأرباح التشغيلية", f"{net_profit_val:,} د.ع", delta="أرباح ممتازة")
            
        st.divider()
        st.write("### 📊 تحليل المبيعات والإيرادات حسب الفواتير:")
        df_inv_chart = pd.DataFrame(st.session_state.invoices_list)
        if not df_inv_chart.empty and "رقم الفاتورة" in df_inv_chart.columns and "المبلغ الكلي" in df_inv_chart.columns:
            st.bar_chart(df_inv_chart, x="رقم الفاتورة", y="المبلغ الكلي")
    else:
        st.info("لا توجد بيانات كافية لعرض الرسوم البيانية. قم بإتمام عمليات بيع أولاً.")

with tab9:
    st.subheader("📜 سجل النشاطات والعمليات (Audit Trail) للمتدخلين والمستخدمين")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد سجلات نشاط حتى الآن.")

with tab10:
    st.subheader("📖 دليل الاستخدام، المميزات، والدعم الفني لنظام Yasser Web")
    st.markdown("""
    * **إدارة المخزون والباركود:** إضافة المنتجات، مراقبة المخزون المنخفض، وتوليد باركود لكل قطعة تلقائياً.
    * **إدارة العملاء والديون:** تسجيل بيانات العملاء ومحافظات العراق ومتابعة الحسابات والذمم بدقة.
    * **نظام البيع السريع (POS):** سلة مبيعات مرنة تدعم الدفع النقدي، الآجل، أو الدفع الجزئي مع الخصم الفوري من المخزن.
    * **الفواتير والـ PDF:** إصدار فواتير رسمية ودعم الطباعة وحفظ ملفات الـ PDF باللغة العربية بالكامل.
    * **الصندوق والتقارير:** تتبع النقدية، المصاريف اليومية، والأرباح الصافية مع رسوم بيانية تفصيلية وسجل نشاطات آمن.
    """)
