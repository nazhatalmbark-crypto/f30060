def create_safe_pdf(row, items):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. تعريف الخط (تأكد أن الاسم بين القوسين يطابق اسم الملف الذي رفعته تماماً)
    font_name = "MyArabicFont"
    font_filename = "DejaVuSans.ttf"  # <--- غيّر هذا الاسم إذا كان اسم ملفك مختلفاً (مثلاً "Cairo.ttf")
    
    try:
        pdf.add_font(font_name, "", font_filename, uni=True)
        pdf.set_font(font_name, size=12)
    except:
        # إذا فشل تحميل الخط، سيستخدم الخط الافتراضي ولا ينهار
        pdf.set_font("Arial", size=12)
    
    # العنوان
    pdf.cell(200, 10, "INVOICE / فاتورة مبيعات", ln=True, align='C')
    
    pdf.ln(5)
    pdf.cell(200, 10, f"Customer / العميل: {row['customer_name']}", ln=True)
    pdf.ln(5)
    
    # الجدول
    pdf.cell(80, 10, "Item / المادة", 1)
    pdf.cell(30, 10, "Qty / الكمية", 1)
    pdf.cell(40, 10, "Price / السعر", 1)
    pdf.cell(40, 10, "Total / المجموع", 1, ln=True)
    
    for item, data in items.items():
        # استخدام try لحماية كل خلية من الانهيار
        try:
            pdf.cell(80, 10, str(item), 1)
        except:
            pdf.cell(80, 10, "Item Name", 1) # إذا فشل الخط، يكتب إنجليزي
            
        pdf.cell(30, 10, str(data['qty']), 1)
        pdf.cell(40, 10, str(data['price']), 1)
        pdf.cell(40, 10, str(data['qty']*data['price']), 1, ln=True)
        
    return pdf.output(dest='S')
