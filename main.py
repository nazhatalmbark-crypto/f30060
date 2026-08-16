with tabs[2]: # المخزن
    st.subheader("📦 إدارة المخزن")
    
    # --- إضافة مادة جديدة ---
    with st.expander("➕ إضافة مادة جديدة للمخزن"):
        with st.form("new_item_form"):
            n = st.text_input("اسم المادة")
            q = st.number_input("الكمية الأولية", min_value=0, step=1)
            c = st.number_input("سعر التكلفة", min_value=0, step=1000)
            s = st.number_input("سعر البيع", min_value=0, step=1000)
            if st.form_submit_button("حفظ المادة"):
                run_query("INSERT INTO inventory (name, quantity, price, selling_price) VALUES (?,?,?,?)", (n, q, c, s))
                st.rerun()

    # --- تحديث كمية مادة موجودة (هذا اللي طلبته!) ---
    with st.expander("🔄 إضافة كمية لمادة موجودة (تزويد المخزن)"):
        # جلب أسماء المواد الموجودة
        existing_items = run_query("SELECT name FROM inventory", fetch=True)
        if existing_items:
            item_names = [i[0] for i in existing_items]
            selected_item = st.selectbox("اختر المادة لتزويد كميتها:", item_names)
            qty_to_add = st.number_input("الكمية المراد إضافتها:", min_value=1, step=1)
            
            if st.button("إضافة الكمية للمخزن"):
                # تحديث الكمية (الكمية القديمة + الكمية الجديدة)
                run_query("UPDATE inventory SET quantity = quantity + ? WHERE name = ?", (qty_to_add, selected_item))
                st.success(f"تمت إضافة {qty_to_add} قطعة للمادة: {selected_item}")
                st.rerun()
        else:
            st.info("لا توجد مواد في المخزن حالياً لإضافتها.")

    st.divider()
    
    # --- عرض المواد ---
    st.markdown("### قائمة المواد الحالية:")
    cols = st.columns(3)
    items = run_query("SELECT id, name, quantity, price, selling_price FROM inventory", fetch=True)
    if items:
        for idx, itm in enumerate(items):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {itm[1]}")
                    st.write(f"الكمية المتاحة: **{itm[2]}**")
                    st.write(f"التكلفة: {int(itm[3]):,} | البيع: {int(itm[4]):,}")
                    profit = itm[4] - itm[3]
                    st.markdown(f"📈 ربح القطعة: **{int(profit):,} د.ع**")
                    if st.button("حذف المادة", key=f"del_{itm[0]}"):
                        run_query("DELETE FROM inventory WHERE id = ?", (itm[0],))
                        st.rerun()
    else:
        st.info("المخزن فارغ.")
