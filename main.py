import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Yasser POS - TOFA", layout="centered", initial_sidebar_state="collapsed")

# **إخفاء هوامش ستريمليت وتطبيق تصميم الموبايل الكامل**
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    .stApp {
        background: #553c9a;
    }
    </style>
""", unsafe_allow_html=True)

# **تطبيق TOFA المتكامل (HTML/JS/CSS) داخل Streamlit**
tofa_app_code = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YASSER POS - TOFA</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; user-select: none; }
        body { background-color: #553c9a; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 10px; }
        
        /* إطار الموبايل */
        .phone-frame {
            width: 100%;
            max-width: 410px;
            height: 840px;
            background: #ffffff;
            border-radius: 40px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
            border: 8px solid #2d1a4e;
        }

        /* الشريط العلوي للموبايل */
        .status-bar {
            height: 45px;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            font-size: 14px;
            color: #333;
            background: #fff;
        }

        .notch {
            width: 12px;
            height: 12px;
            background: #000;
            border-radius: 50%;
        }

        /* الهيدر */
        .app-header {
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #fff;
        }
        .app-header h2 { font-size: 20px; color: #2d1a4e; font-weight: 800; letter-spacing: 1px; }
        .icon-btn { font-size: 22px; color: #333; cursor: pointer; border: none; background: none; }

        .sub-title { text-align: center; color: #888; font-size: 13px; padding-bottom: 15px; background: #fff; }

        /* منطقة المحتوى القابلة للتمرير */
        .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f8f6fc;
        }
        .content-area::-webkit-scrollbar { display: none; }

        /* شبكة الكروت الرئيسية (TOFA Grid) */
        .tofa-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .tofa-card {
            background: #ffffff;
            border-radius: 24px;
            padding: 25px 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(85, 60, 154, 0.05);
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid #f0ebf8;
            text-align: center;
        }
        .tofa-card:active { transform: scale(0.96); background: #f3edff; }

        .icon-wrapper {
            width: 55px;
            height: 55px;
            background: #f3edff;
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            color: #553c9a;
            margin-bottom: 12px;
        }

        .card-title { font-size: 16px; font-weight: 700; color: #2d1a4e; margin-bottom: 4px; }
        .card-sub { font-size: 11px; color: #8a81ab; }

        /* شاشات الأقسام داخل الموبايل */
        .page { display: none; }
        .page.active { display: block; }

        /* إحصائيات وتقارير */
        .stat-card {
            border-radius: 20px;
            padding: 15px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .stat-blue { background: #eef6ff; border: 1px solid #cce5ff; color: #0066cc; }
        .stat-green { background: #eefbfa; border: 1px solid #ccf5f0; color: #00aa88; }
        
        .footer-ver { text-align: center; font-size: 12px; color: #aaa; margin-top: 30px; }
    </style>
</head>
<body>

<div class="phone-frame">
    <!-- الشريط العلوي -->
    <div class="status-bar">
        <span>5:26</span>
        <div class="notch"></div>
        <div><i class="bi bi-wifi"></i> <i class="bi bi-battery-full"></i></div>
    </div>

    <!-- الهيدر الرئيسي -->
    <div class="app-header">
        <button class="icon-btn" onclick="showPage('home')"><i class="bi bi-text-paragraph"></i></button>
        <h2>TOFA</h2>
        <button class="icon-btn" onclick="showPage('settings')"><i class="bi bi-gear"></i></button>
    </div>
    <div class="sub-title">إدارة المبيعات والعمليات</div>

    <!-- منطقة الشاشات -->
    <div class="content-area">
        
        <!-- 1. الشاشة الرئيسية (TOFA Grid) -->
        <div id="page-home" class="page active">
            <div class="tofa-grid">
                <div class="tofa-card" onclick="showPage('create-inv')">
                    <div class="icon-wrapper"><i class="bi bi-file-earmark-plus"></i></div>
                    <div class="card-title">إنشاء فاتورة</div>
                    <div class="card-sub">إصدار الفواتير والطباعة</div>
                </div>

                <div class="tofa-card" onclick="alert('سجل الفواتير جاهز')">
                    <div class="icon-wrapper"><i class="bi bi-journal-text"></i></div>
                    <div class="card-title">قائمة الفواتير</div>
                    <div class="card-sub">سجل الفواتير المباعة</div>
                </div>

                <div class="tofa-card" onclick="alert('قسم العملاء والديون')">
                    <div class="icon-wrapper"><i class="bi bi-people"></i></div>
                    <div class="card-title">العملاء</div>
                    <div class="card-sub">إدارة العملاء والديون</div>
                </div>

                <div class="tofa-card" onclick="alert('إدارة المخزن والمشتريات')">
                    <div class="icon-wrapper"><i class="bi bi-box-seam"></i></div>
                    <div class="card-title">المخزن</div>
                    <div class="card-sub">إدارة المشتريات والمخزون</div>
                </div>

                <div class="tofa-card" onclick="showPage('bonds')">
                    <div class="icon-wrapper"><i class="bi bi-wallet2"></i></div>
                    <div class="card-title">السندات</div>
                    <div class="card-sub">سندات قبض وصرف</div>
                </div>

                <div class="tofa-card" onclick="showPage('stats')">
                    <div class="icon-wrapper"><i class="bi bi-arrow-return-left"></i></div>
                    <div class="card-title">الإحصائيات</div>
                    <div class="card-sub">التقارير والأرباح</div>
                </div>
            </div>
            <div class="footer-ver">الإصدار 4.3.0</div>
        </div>

        <!-- 2. شاشة الإحصائيات والتقارير -->
        <div id="page-stats" class="page">
            <h3 style="margin-bottom:15px; color:#333;">الإحصائيات والتقارير</h3>
            <div class="stat-card stat-blue">
                <div>
                    <div style="font-size:12px;">رصيد الصندوق</div>
                    <div style="font-size:18px; font-weight:bold;">15,002,550 د.ع</div>
                </div>
                <i class="bi bi-wallet-fill" style="font-size:28px;"></i>
            </div>
            <div class="stat-card stat-green">
                <div>
                    <div style="font-size:12px;">صافي الربح</div>
                    <div style="font-size:18px; font-weight:bold;">2,040,299 د.ع</div>
                </div>
                <i class="bi bi-graph-up-arrow" style="font-size:28px;"></i>
            </div>
            <button onclick="showPage('home')" style="width:100%; padding:12px; background:#553c9a; color:#fff; border:none; border-radius:12px; margin-top:15px; font-weight:bold;">الرجوع للرئيسية</button>
        </div>

        <!-- 3. شاشة السندات -->
        <div id="page-bonds" class="page">
            <h3 style="margin-bottom:15px; color:#333;">السندات</h3>
            <div style="background:#fff; padding:15px; border-radius:15px; margin-bottom:10px; border:1px solid #eee;">
                <div style="display:flex; justify-content:space-between; color:#d9534f; font-weight:bold;">
                    <span>سند صرف #149</span>
                    <span>50,000 د.ع</span>
                </div>
                <div style="font-size:12px; color:#777; margin-top:5px;">مصاريف إدارية - وقود</div>
            </div>
            <button onclick="showPage('home')" style="width:100%; padding:12px; background:#553c9a; color:#fff; border:none; border-radius:12px; margin-top:15px; font-weight:bold;">الرجوع للرئيسية</button>
        </div>

        <!-- 4. شاشة إنشاء فاتورة -->
        <div id="page-create-inv" class="page">
            <h3 style="margin-bottom:15px; color:#333;">فاتورة جديدة</h3>
            <input type="text" placeholder="اسم العميل (حضرة السيد)" style="width:100%; padding:12px; border:1px solid #ddd; border-radius:10px; margin-bottom:10px; text-align:right;">
            <input type="text" placeholder="رقم الهاتف" style="width:100%; padding:12px; border:1px solid #ddd; border-radius:10px; margin-bottom:10px; text-align:right;">
            <button onclick="alert('تم البيع وحفظ الفاتورة بنجاح!'); showPage('home');" style="width:100%; padding:14px; background:#553c9a; color:#fff; border:none; border-radius:12px; font-weight:bold; margin-top:10px;">بيع وطباعة الفاتورة</button>
            <button onclick="showPage('home')" style="width:100%; padding:12px; background:#eee; color:#333; border:none; border-radius:12px; margin-top:8px;">إلغاء</button>
        </div>

    </div>
</div>

<script>
    function showPage(pageId) {
        document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
        document.getElementById('page-' + pageId).classList.add('active');
    }
</script>

</body>
</html>
"""

components.html(tofa_app_code, height=860, scrolling=False)
