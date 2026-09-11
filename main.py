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
                        wa_msg = urllib.parse.quote(f"مرحباً بك استاذ {inv['الزبون']},\nنذكركم بوجود مبلغ متبقي (دين) بذمتكم لصالح محلنا بموجب الفاتورة رقم {inv['الزبون']} وقدره {inv['المتبقي (الدين)']:,} دينار عراقي.\nشكراً لتعاملكم معنا!")
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
