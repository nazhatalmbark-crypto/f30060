import streamlit as st

# دالة عرض دليل الاستخدام داخل التطبيق
def show_user_guide():
    guide_html = """
    <div style="font-family: 'Cairo', sans-serif; direction: rtl; background-color: #fdfbf7; padding: 20px; border-radius: 12px; border: 1px solid #e6d5b8;">
        
        <!-- عنوان الدليل -->
        <div style="text-align: center; margin-bottom: 25px;">
            <h2 style="color: #8b6508; margin: 0; font-size: 24px; font-weight: 700;">🌟 دليل استخدام نظام ياسر ويب الشامل</h2>
            <p style="color: #666; font-size: 14px; margin-top: 5px;">الدليل المرجعي لإدارة المبيعات، المخازن، والحسابات بكفاءة واحترافية عالية</p>
        </div>

        <!-- القسم الأول -->
        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">🛒 1. نقطة البيع السريعة (POS) وإتمام الفاتورة</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">
                النافذة التشغيلية الأساسية لإتمام عمليات البيع بسلاسة. يتيح لك القسم سحب المواد من المخزن مباشرة إلى سلة المبيعات، مع إمكانية تعديل الكميات أو حذفها بلمسة واحدة. يقوم النظام آلياً بحساب المجاميع، خصم المبالغ، التعرف على بيانات العميل، وتحديد آلية الدفع بدقة (نقدي تام، دين آجل، أو دفعة جزئية)، مع إصدار وحفظ الفواتير بشكل رسمي وموثق.
            </p>
        </div>

        <!-- القسم الثاني -->
        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">📦 2. إدارة المخزن وجرد البضائع</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">
                مرآة المخزون الشاملة؛ تعرض كافة المواد والأجهزة المسجلة تفصيلياً مع بيان الألوان، القياسات، الباركود، أسعار الشراء، تكاليف البيع، والكميات المتاحة لحظياً. مزود بمحرك بحث ذكي وسريع جداً يتيح لك الوصول لأي صنف في المخزن خلال ثوانٍ معدودة لمنع أي نقص أو تضارب.
            </p>
        </div>

        <!-- القسم الثالث -->
        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">➕ 3. إضافة مادة جديدة وتوليد الباركود</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">
                بوابة إدخال البضائع والاصناف الجديدة إلى النظام مع تحديد كافة تفاصيلها المالية والفنية (سعر الشراء، سعر البيع، والكمية الافتتاحية). كما يحتوي على أداة متقدمة لتوليد وطباعة رموز الباركود الخاصة بكل مادة وفق معيار (Code128) العالمي لتسهيل عمليات البيع والمسح الضوئي.
            </p>
        </div>

        <!-- القسم الرابع -->
        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">👥 4. العملاء والديون وسندات القبض</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">
                منظومة متكاملة لإدارة علاقات العملاء، تسجيل بياناتهم، ومتابعة أرصدتهم والديون المرتبطة بفواتيرهم الآجلة. يتيح نظام سندات القبض إثبات الدفعات النقدية المسددة أولاً باول لتحديث حساب العميل آلياً، مع إمكانية إصدار وطباعة سند قبض رسمي بصيغة HTML يحفظ حقوق الطرفين.
            </p>
        </div>

        <!-- القسم الخامس -->
        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">💰 5. صندوق الوردية والمصروفات النقدية</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">
                وحدة الرقابة المالية اليومية المخصصة لتسجيل النثريات، المصروفات التشغيلية (مثل أجور النقل، الصيانة، والإيجارات اليومية). يمنحك رصيداً دقيقاً لصافي الصندوق النقدي الفعلي بمطابقته مع إجمالي المقبوضات لضمان عدم وجود أي عجز أو فروقات مالية بنهاية كل وردية.
            </p>
        </div>

        <!-- القسم السادس -->
        <div style="background: #ffffff; padding: 18px; margin-bottom: 15px; border-radius: 10px; border-right: 5px solid #8b6508; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            <h4 style="color: #8b6508; margin: 0 0 8px 0; font-size: 17px;">📊 6. تقارير الأرباح والسجل الرقابي</h4>
            <p style="color: #444; margin: 0; line-height: 1.7; font-size: 14px;">
                أقسام استراتيجية مصممة خصيصاً لمدير النظام وأصحاب القرار، تعرض تحليلات مالية دقيقة لإجمالي المبيعات، صافي أرباح البضائع، ومتابعة الديون المعلقة. إضافة إلى "السجل الرقابي" الأمني الذي يوثق ويراقب كافة حركات المستخدمين في النظام بدقة لضمان أعلى معايير الموثوقية.
            </p>
        </div>

        <!-- تذييل الصفحة -->
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px dashed #DAA520;">
            <p style="font-size: 14px; color: #444; font-weight: bold; margin-bottom: 8px;">
                ✨ تصميم وبرمجة: <b>نظام ياسر ويب</b> | جميع الحقوق محفوظة للإدارة المتكاملة 2026
            </p>
            <a href="https://instagram.com/yasser_web" target="_blank" style="color: #8b6508; text-decoration: none; font-weight: bold; font-size: 14px;">
                📸 تواصل معنا عبر انستغرام: @yasser_web
            </a>
        </div>

    </div>
    """
    
    st.markdown(guide_html, unsafe_allow_html=True)
