def create_safe_pdf(row, items):
    pdf = FPDF()
    pdf.add_page()
    
    # --- إعداد الخط ---
    # تأكد أن اسم الملف هنا يطابق اسم ملف الخط الذي رفعته في GitHub حرفياً
    font_filename = "DejaVuSans.ttf" 
    
    # نستخدم Latin-1 للترميز لتجنب أي انهيار، ونستبدل الحروف غير المدعومة بعلامة استفهام
    def clean_text(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    # محاولة إضافة الخط العربي
    if os.path.exists(font_filename):
        try:
            pdf.add_font("CustomFont", "", font_filename, uni=True)
            pdf.set_font("CustomFont", size=12)
        except:
            pdf.set_font("Arial", size=12) # فشل الخط، نستخدم Arial
    else:
        pdf.set_font("Arial", size=12) # الملف غير موجود، نستخدم Arial
    
    # --- كتابة البيانات ---
    try:
        # استخدام clean_text لكل النصوص لضمان عدم حدوث EncodingException
        pdf.cell(200, 10, clean_text("INVOICE / فاتورة مبيعات"), ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, clean_text(f"Customer: {row['customer_name']}"), ln=True)
        pdf.ln(5)
        
        # الجدول
        pdf.cell(80, 10, clean_text("Item"), 1)
        pdf.cell(30, 10, clean_text("Qty"), 1)
        pdf.cell(40, 10, clean_text("Price"), 1)
        pdf.cell(40, 10, clean_text("Total"), 1, ln=True)
        
        for item, data in items.items():
            pdf.cell(80, 10, clean_text(str(item)), 1)
            pdf.cell(30, 10, clean_text(str(data['qty'])), 1)
            pdf.cell(40, 10, clean_text(str(data['price'])), 1)
            pdf.cell(40, 10, clean_text(str(data['qty']*data['price'])), 1, ln=True)
            
    except Exception as e:
        # إذا فشل الرسم تماماً، يكتب الخطأ داخل ملف الـ PDF لنعرف السبب
        pdf.cell(200, 10, f"Critical Error: {str(e)}", ln=True)
        
    return pdf.output(dest='S')
