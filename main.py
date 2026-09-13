import os
import requests

def generate_pdf_invoice(inv):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # تحميل خط أميري الحقيقي من مصدر موثوق لتجنب مشكلة المربعات السوداء تماماً
    font_path = "Amiri-Regular.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
            r = requests.get(url)
            with open(font_path, "wb") as f:
                f.write(r.content)
        except:
            pass

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # تسجيل خط أميري في ReportLab
    try:
        pdfmetrics.registerFont(TTFont('Amiri', font_path))
        font_name = 'Amiri'
    except:
        font_name = 'Helvetica' # كاحتياط أخير

    p.setFont(font_name, 14)
    
    # رأس الفاتورة
    p.drawRightString(width - 50, height - 50, format_arabic("فاتورة مبيعات رسمية - Yasser Web"))
    p.setFont('Helvetica', 10)
    p.drawString(50, height - 50, f"Date: {inv['التاريخ']}")
    
    p.setStrokeColorRGB(0.2, 0.2, 0.2)
    p.setLineWidth(1)
    p.line(50, height - 65, width - 50, height - 65)
    
    p.setFont(font_name, 11)
    
    def draw_right_arabic_fixed(canvas_obj, text, y_pos):
        processed = format_arabic(text)
        canvas_obj.drawRightString(width - 50, y_pos, processed)

    draw_right_arabic_fixed(p, f"رقم الفاتورة: {inv['رقم الفاتورة']}", height - 95)
    draw_right_arabic_fixed(p, f"اسم الزبون: {inv['الزبون']}", height - 120)
    draw_right_arabic_fixed(p, f"نوع الدفع: {inv['نوع الدفع']}", height - 145)
    
    p.line(50, height - 165, width - 50, height - 165)
    draw_right_arabic_fixed(p, "تفاصيل المنتجات والمواد المباعة:", height - 195)
    
    text_y = height - 225
    items_list_str = str(inv['المنتجات']).split(" , ")
    for prod_line in items_list_str:
        draw_right_arabic_fixed(p, f">> {prod_line}", text_y)
        text_y -= 25
        
    text_y -= 10
    p.line(50, text_y, width - 50, text_y)
    
    text_y -= 35
    draw_right_arabic_fixed(p, f"المبلغ الكلي: {int(inv['المبلغ الكلي']):,} دينار عراقي", text_y)
    text_y -= 25
    draw_right_arabic_fixed(p, f"المبلغ الواصل: {int(inv['الواصل']):,} دينار عراقي", text_y)
    text_y -= 25
    draw_right_arabic_fixed(p, f"المتبقي (الدين): {int(inv['المتبقي (الدين)']):,} دينار عراقي", text_y)
    
    text_y -= 45
    p.setLineWidth(0.5)
    p.line(50, text_y, width - 50, text_y)
    
    footer_text = format_arabic("شكراً لتعاملكم مع نظام Yasser Web لإدارة المبيعات والمخزن!")
    p.drawCentredString(width / 2.0, text_y - 35, footer_text)
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
