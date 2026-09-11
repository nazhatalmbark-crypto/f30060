with col_inv1:
                    st.markdown(f"#### {inv['رقم الفاتورة']} | الزبون: {inv['الزبون']}")
                    st.write(f"📅 التاريخ: {inv['التاريخ']}")
                    st.write(f"💳 الدفع: {inv['نوع الدفع']}")
                with col_inv2:
                    st.write(f"🛒 **المواد:** {inv['المنتجات']}")
                    st.write(f"💰 الكلي: `{inv['المبلغ الكلي']:,}` د.ع")
                    st.write(f"📥 الواصل: `{inv['الواصل']:,}` د.ع | المتبقي: `{inv['المتبقي (الدين)']:,}` د.ع")
                with col_inv3:
                    # PDF Download
                    pdf_buffer = generate_pdf_invoice(inv)
                    if pdf_buffer:
                        st.download_button(
                            label="📄 تحميل فاتورة PDF",
                            data=pdf_buffer,
                            file_name=f"{inv['رقم الفاتورة']}_{inv['الزبون']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{inv['رقم الفاتورة']}"
                        )
                    
                    # WhatsApp Debt Reminder
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
        st.info("لا توجد فواتير مسجلة حتى الآن.")

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
                    log_audit("تسجيل مصروف", f"تم تسسجيل مصروف ({exp_title.strip()}) بقيمة {int(exp_amt):,} د.ع")
                    st.success("✅ تم تسجيل المصروف بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("يرجى إدخال مبلغ صحيح.")
            else:
                st.warning("يرجى إدخال بيان المصروف.")

    st.divider()
    
    # حساب ملخص الصندوق
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
