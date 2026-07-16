with tabs[3]: # الفواتير
    st.header("🧾 الفواتير")
    if st.button("🧹 تصفير وتنظيف كل شيء"):
        c.execute("DELETE FROM invoices")
        conn.commit(); st.rerun()
    
    invoices = pd.read_sql("SELECT rowid, * FROM invoices ORDER BY rowid DESC", conn)
    for _, row in invoices.iterrows():
        with st.expander(f"فاتورة #{row['rowid']} | {row['customer_name']}"):
            try:
                # --- التعديل السحري هنا: تنظيف النص قبل قراءته ---
                clean_str = row['items'].replace('np.int64(', '').replace(')', '')
                items = ast.literal_eval(clean_str)
                
                for n, d in items.items(): 
                    st.write(f"🔹 {n} | {int(d['qty'])} قطعة")
                st.write(f"المجموع: {int(row['total'])}")
                
                if st.button(f"📥 PDF", key=f"pdf_{row['rowid']}"):
                    generate_pdf(row['rowid'], row['customer_name'], items, int(row['total']))
                    st.success("تم إنشاء الملف")
            except:
                st.error("فاتورة تالفة وغير قابلة للقراءة.")
                if st.button(f"🗑️ حذف هذه الفاتورة #{row['rowid']}", key=f"del_{row['rowid']}"):
                    c.execute("DELETE FROM invoices WHERE rowid=?", (row['rowid'],))
                    conn.commit(); st.rerun()
