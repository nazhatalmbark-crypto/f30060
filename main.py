import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ياسر ويب POS", layout="wide")

html_code = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقارير نهائية - ياسر ويب POS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#045b3e',
                        darkGreen: '#033f2b',
                        bgGreen: '#064e3b',
                        cardBg: '#e8f0ec',
                        activeCard: '#d1e3d9'
                    }
                }
            }
        }
    </script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #064e3b;
            font-family: system-ui, -apple-system, sans-serif;
        }
    </style>
</head>
<body class="text-gray-800 flex justify-center items-start min-h-screen p-0 sm:p-4">

    <!-- Screen Container Frame -->
    <div class="w-full max-w-md bg-bgGreen min-h-screen sm:min-h-[840px] sm:rounded-3xl shadow-2xl overflow-hidden flex flex-col relative pb-20">

        <!-- Top Header Navigation -->
        <header class="p-4 text-white flex justify-between items-center">
            <div class="flex items-center space-x-3 space-x-reverse">
                <button onclick="toggleSidebar()" class="text-white text-xl p-1">
                    <i class="fa-solid fa-bars"></i>
                </button>
                <h1 class="text-xl font-bold">تقارير نهائيه</h1>
            </div>
            <div class="flex items-center space-x-3 space-x-reverse">
                <button onclick="openModal('add-modal')" class="text-white text-lg">
                    <i class="fa-solid fa-plus"></i>
                </button>
                <button onclick="logout()" class="text-white text-sm bg-red-600/80 px-2 py-1 rounded-lg">
                    <i class="fa-solid fa-right-from-bracket"></i>
                </button>
            </div>
        </header>

        <!-- Floating Badge Widget (Dynamic Report Counter) -->
        <div class="px-4 relative z-20 -mb-6">
            <div class="bg-white rounded-2xl p-4 shadow-xl w-44 space-y-1 border border-gray-100">
                <span class="text-xs text-gray-400 font-medium block text-right">التقارير</span>
                <div id="dynamic-badge-num" class="text-3xl font-black text-gray-900 text-right">+50</div>
                <div class="flex items-center space-x-1 space-x-reverse bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full text-[11px] font-bold w-fit">
                    <span>مبيعات</span>
                    <span>•</span>
                    <span>أرباح</span>
                    <span>•</span>
                    <span>مخزون</span>
                </div>
            </div>
        </div>

        <!-- Top Overview Panel -->
        <div class="px-4 pt-2">
            <div class="bg-darkGreen/60 rounded-2xl p-4 text-white space-y-2 border border-emerald-600/30">
                <div class="flex justify-between items-center text-xs text-emerald-200 border-b border-emerald-700/50 pb-2">
                    <span id="current-date-str">اليوم 21 مايو</span>
                    <span class="bg-emerald-800/80 px-2 py-0.5 rounded-md">حالة الصندوق: نشط</span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-center pt-1">
                    <div class="border-l border-emerald-700/50 pl-2">
                        <span class="text-[11px] text-emerald-200 block">إجمالي المبيعات</span>
                        <span id="overview-sales" class="text-lg font-bold text-white">110.35 جنيه</span>
                    </div>
                    <div>
                        <span class="text-[11px] text-emerald-200 block">مخزون داخل</span>
                        <span id="overview-stock" class="text-lg font-bold text-white">51</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Workspace Canvas -->
        <main class="flex-1 bg-white mt-4 rounded-t-3xl p-4 space-y-4">

            <!-- Grid Modules (Matches Design 1:1 with all user sections) -->
            <div id="grid-menu" class="grid grid-cols-3 gap-3">
                
                <!-- لوحة التحكم -->
                <button onclick="switchTab('dashboard')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-solid fa-table-cells-large text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">لوحة التحكم</span>
                </button>

                <!-- المبيعات -->
                <button onclick="switchTab('sales')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-solid fa-box-archive text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">المبيعات</span>
                </button>

                <!-- المشتريات -->
                <button onclick="switchTab('purchases')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-solid fa-cart-flatbed text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">المشتريات</span>
                </button>

                <!-- تقرير الأرباح -->
                <button onclick="switchTab('profits')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-solid fa-chart-line text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">تقرير الأرباح</span>
                </button>

                <!-- المصروفات -->
                <button onclick="switchTab('expenses')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-solid fa-receipt text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">المصروفات</span>
                </button>

                <!-- تقرير الصندوق -->
                <button onclick="switchTab('cashbox')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-solid fa-cash-register text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">تقرير الصندوق</span>
                </button>

                <!-- تقرير المخزن -->
                <button onclick="switchTab('inventory')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-solid fa-boxes-stacked text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">تقرير المخزن</span>
                </button>

                <!-- العملاء -->
                <button onclick="switchTab('customers')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-regular fa-user text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">العملاء</span>
                </button>

                <!-- الموردين -->
                <button onclick="switchTab('suppliers')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-regular fa-id-card text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">الموردين</span>
                </button>

                <!-- تقارير الرسم البياني -->
                <button onclick="switchTab('charts')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-regular fa-user text-emerald-800 text-2xl"></i>
                    <span class="text-xs font-bold text-gray-800">تقارير الرسم البياني</span>
                </button>

                <!-- رأس المال -->
                <button onclick="switchTab('capital')" class="bg-cardBg hover:bg-activeCard p-4 rounded-2xl flex flex-col items-center justify-center space-y-2 transition shadow-sm h-28 border border-emerald-900/5">
                    <i class="fa-solid fa-dollar-sign text-emerald-800 text-2xl border border-emerald-800 rounded-full w-7 h-7 flex items-center justify-center"></i>
                    <span class="text-xs font-bold text-gray-800">رأس المال</span>
                </button>

            </div>

            <!-- Content Details Container -->
            <div id="tab-viewer" class="bg-gray-50 p-4 rounded-2xl border border-gray-200 min-h-[220px]">
                <div id="content-dashboard" class="tab-pane space-y-2">
                    <h3 class="font-bold text-gray-800 border-b pb-1 text-sm">تنبيهات المخزون والنظام</h3>
                    <div id="stock-alerts" class="text-xs text-emerald-800 bg-emerald-100/60 p-2.5 rounded-xl">
                        حالة المخزون مستقرة حالياً.
                    </div>
                </div>

                <div id="content-sales" class="tab-pane hidden space-y-2">
                    <h3 class="font-bold text-gray-800 border-b pb-1 text-sm">إجراء بيع سريع</h3>
                    <select id="sale-item-select" class="w-full p-2 border rounded-xl text-xs"></select>
                    <input type="number" id="sale-item-qty" value="1" min="1" class="w-full p-2 border rounded-xl text-xs">
                    <button onclick="processSale()" class="w-full bg-emerald-800 text-white py-2 rounded-xl text-xs font-bold">تسجيل العملية</button>
                </div>

                <div id="content-inventory" class="tab-pane hidden space-y-2">
                    <h3 class="font-bold text-gray-800 border-b pb-1 text-sm">قائمة المواد بالمخزن</h3>
                    <div id="inventory-items" class="space-y-1.5 max-h-40 overflow-y-auto text-xs"></div>
                </div>

                <div id="content-customers" class="tab-pane hidden space-y-2">
                    <h3 class="font-bold text-gray-800 border-b pb-1 text-sm">سجل الديون والعملاء</h3>
                    <input type="text" id="cust-n" placeholder="اسم الزبون" class="w-full p-2 border rounded-xl text-xs">
                    <input type="number" id="cust-d" placeholder="المبلغ الدائن" class="w-full p-2 border rounded-xl text-xs">
                    <button onclick="saveCust()" class="w-full bg-emerald-800 text-white py-2 rounded-xl text-xs font-bold">إضافة دين/زبون</button>
                    <div id="customers-items" class="space-y-1 max-h-32 overflow-y-auto text-xs mt-2"></div>
                </div>

                <div id="content-profits" class="tab-pane hidden space-y-2 text-center">
                    <h3 class="font-bold text-gray-800 border-b pb-1 text-sm text-right">تقرير الأرباح الصافية</h3>
                    <span class="text-xs text-gray-500">إجمالي صافي الربح المسجل:</span>
                    <div id="profit-amount" class="text-xl font-black text-emerald-800 mt-1">0.00 د.ع</div>
                </div>

                <div id="content-cashbox" class="tab-pane hidden space-y-2 text-center">
                    <h3 class="font-bold text-gray-800 border-b pb-1 text-sm text-right">تقرير الصندوق اليومي</h3>
                    <div id="cashbox-amount" class="text-xl font-black text-emerald-800 mt-1">0.00 د.ع</div>
                </div>

                <div id="content-purchases" class="tab-pane hidden text-xs text-gray-600">سجل عمليات المشتريات وإدخال البضاعة.</div>
                <div id="content-expenses" class="tab-pane hidden text-xs text-gray-600">سجل المصروفات التشغيلية والنثرية.</div>
                <div id="content-suppliers" class="tab-pane hidden text-xs text-gray-600">قائمة الموردين والشركات المجهزة.</div>
                <div id="content-charts" class="tab-pane hidden text-xs text-gray-600">الرسم البياني للمبيعات والمصروفات.</div>
                <div id="content-capital" class="tab-pane hidden text-xs text-gray-600">إجمالي رأس المال والأصول المتاحة.</div>
            </div>

        </main>

        <!-- Bottom Tab Bar -->
        <nav class="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-100 py-2 px-3 flex justify-between items-center z-30">
            <button onclick="switchTab('sales')" class="flex flex-col items-center text-gray-400 hover:text-emerald-800 text-[10px]">
                <i class="fa-solid fa-store text-lg"></i>
                <span>المبيعات</span>
            </button>
            <button onclick="switchTab('purchases')" class="flex flex-col items-center text-gray-400 hover:text-emerald-800 text-[10px]">
                <i class="fa-solid fa-receipt text-lg"></i>
                <span>المشتريات</span>
            </button>
            <button onclick="switchTab('inventory')" class="flex flex-col items-center text-gray-400 hover:text-emerald-800 text-[10px]">
                <i class="fa-solid fa-box-archive text-lg"></i>
                <span>المخازن</span>
            </button>
            <button onclick="switchTab('dashboard')" class="flex flex-col items-center text-emerald-800 text-[10px] font-bold">
                <i class="fa-solid fa-chart-pie text-lg"></i>
                <span>التقارير</span>
            </button>
            <button onclick="switchTab('capital')" class="flex flex-col items-center text-gray-400 hover:text-emerald-800 text-[10px]">
                <i class="fa-solid fa-wallet text-lg"></i>
                <span>المالية</span>
            </button>
        </nav>

        <!-- Login Screen Modal -->
        <div id="login-modal" class="fixed inset-0 bg-bgGreen/95 z-50 flex items-center justify-center p-4">
            <div class="bg-white p-6 rounded-3xl w-full max-w-xs space-y-4 shadow-2xl text-center">
                <div class="bg-emerald-100 text-emerald-800 w-14 h-14 rounded-full flex items-center justify-center mx-auto text-xl font-bold">
                    <i class="fa-solid fa-lock"></i>
                </div>
                <h2 class="text-base font-bold text-gray-800">تسجيل الدخول - ياسر ويب</h2>
                <div class="space-y-2 text-right">
                    <input type="text" id="user-in" placeholder="اسم المستخدم" class="w-full p-2.5 border rounded-xl text-xs">
                    <input type="password" id="pass-in" placeholder="كلمة المرور" class="w-full p-2.5 border rounded-xl text-xs">
                </div>
                <button onclick="auth()" class="w-full bg-emerald-800 text-white py-2.5 rounded-xl font-bold text-xs shadow">دخول</button>
            </div>
        </div>

    </div>

    <script>
        let products = JSON.parse(localStorage.getItem('yw_products')) || [
            { id: 1, name: 'عطر كوزمتك', price: 12000, qty: 30 },
            { id: 2, name: 'كريم عناية', price: 5000, qty: 4 }
        ];
        let customers = JSON.parse(localStorage.getItem('yw_customers')) || [];
        let totalSales = parseFloat(localStorage.getItem('yw_sales')) || 110.35;

        function auth() {
            let u = document.getElementById('user-in').value;
            let p = document.getElementById('pass-in').value;
            if(u && p) {
                document.getElementById('login-modal').classList.add('hidden');
                localStorage.setItem('yw_auth', '1');
            }
        }

        function logout() {
            localStorage.removeItem('yw_auth');
            document.getElementById('login-modal').classList.remove('hidden');
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
            let target = document.getElementById('content-' + tabId);
            if(target) target.classList.remove('hidden');
        }

        function render() {
            if(localStorage.getItem('yw_auth') === '1') {
                document.getElementById('login-modal').classList.add('hidden');
            }

            document.getElementById('overview-sales').innerText = totalSales.toLocaleString() + ' د.ع';
            document.getElementById('cashbox-amount').innerText = totalSales.toLocaleString() + ' د.ع';
            document.getElementById('profit-amount').innerText = (totalSales * 0.25).toLocaleString() + ' د.ع';

            let stockCount = products.reduce((acc, p) => acc + parseInt(p.qty), 0);
            document.getElementById('overview-stock').innerText = stockCount;
            document.getElementById('dynamic-badge-num').innerText = '+' + stockCount;

            let sel = document.getElementById('sale-item-select');
            let inv = document.getElementById('inventory-items');
            sel.innerHTML = '';
            inv.innerHTML = '';

            products.forEach(p => {
                sel.innerHTML += `<option value="${p.id}">${p.name} - ${p.price} د.ع</option>`;
                inv.innerHTML += `<div class="flex justify-between items-center bg-gray-100 p-2 rounded-lg">
                    <span>${p.name}</span>
                    <span class="font-bold text-emerald-800">${p.price} د.ع | الكمية: ${p.qty}</span>
                </div>`;
            });

            let custDiv = document.getElementById('customers-items');
            custDiv.innerHTML = '';
            customers.forEach(c => {
                custDiv.innerHTML += `<div class="flex justify-between p-1.5 bg-gray-100 rounded-lg">
                    <span>${c.name}</span>
                    <span class="text-red-600 font-bold">${c.debt} د.ع</span>
                </div>`;
            });

            localStorage.setItem('yw_products', JSON.stringify(products));
            localStorage.setItem('yw_customers', JSON.stringify(customers));
            localStorage.setItem('yw_sales', totalSales);
        }

        function processSale() {
            let pId = document.getElementById('sale-item-select').value;
            let qty = parseInt(document.getElementById('sale-item-qty').value);
            let item = products.find(p => p.id == pId);

            if(item && item.qty >= qty) {
                item.qty -= qty;
                totalSales += (item.price * qty);
                render();
                alert('تم تسجيل العملية بنجاح');
            } else {
                alert('الكمية غير متوفرة');
            }
        }

        function saveCust() {
            let name = document.getElementById('cust-n').value;
            let debt = parseFloat(document.getElementById('cust-d').value) || 0;
            if(name) {
                customers.push({ name, debt });
                document.getElementById('cust-n').value = '';
                document.getElementById('cust-d').value = '';
                render();
            }
        }

        render();
    </script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=True)
