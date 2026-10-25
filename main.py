<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ياسر ويب - نظام إدارة المبيعات والمخزون</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#10b981',
                        darkGreen: '#047857',
                        lightGreen: '#ecfdf5'
                    }
                }
            }
        }
    </script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 font-sans antialiased text-gray-800 pb-20">

    <!-- Header / Top Bar -->
    <header class="bg-darkGreen text-white shadow-md sticky top-0 z-50">
        <div class="max-w-md mx-auto px-4 py-3 flex justify-between items-center">
            <div class="flex items-center space-x-2 space-x-reverse">
                <div class="bg-white text-darkGreen p-2 rounded-xl font-bold shadow">
                    <i class="fa-solid fa-store text-xl"></i>
                </div>
                <div>
                    <h1 class="font-bold text-lg">ياسر ويب POS</h1>
                    <p class="text-xs text-emerald-200">إدارة المبيعات والمخزون</p>
                </div>
            </div>
            <div class="flex items-center space-x-3 space-x-reverse">
                <span id="current-date" class="text-xs bg-emerald-900 px-2 py-1 rounded-lg">اليوم</span>
            </div>
        </div>
    </header>

    <!-- Main Container (Mobile Frame Look) -->
    <main class="max-w-md mx-auto p-4 space-y-4">

        <!-- Top Summary Cards -->
        <div class="grid grid-cols-2 gap-3">
            <div class="bg-white p-3 rounded-2xl shadow-sm border border-emerald-100 flex items-center justify-between">
                <div>
                    <p class="text-xs text-gray-500">إجمالي المبيعات</p>
                    <h3 id="total-sales" class="text-lg font-bold text-darkGreen">0.00 د.ع</h3>
                </div>
                <div class="bg-emerald-50 p-2.5 rounded-xl text-primary">
                    <i class="fa-solid fa-chart-line text-lg"></i>
                </div>
            </div>
            <div class="bg-white p-3 rounded-2xl shadow-sm border border-emerald-100 flex items-center justify-between">
                <div>
                    <p class="text-xs text-gray-500">مخزون داخل</p>
                    <h3 id="total-stock-count" class="text-lg font-bold text-darkGreen">0</h3>
                </div>
                <div class="bg-emerald-50 p-2.5 rounded-xl text-primary">
                    <i class="fa-solid fa-boxes-stacked text-lg"></i>
                </div>
            </div>
        </div>

        <!-- Dashboard Grid Menu (Modern Tiles) -->
        <div class="grid grid-cols-3 gap-3">
            <!-- لوحة التحكم -->
            <button onclick="switchTab('dashboard')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-border-all text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">لوحة التحكم</span>
            </button>
            <!-- المبيعات -->
            <button onclick="switchTab('sales')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-cash-register text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">المبيعات</span>
            </button>
            <!-- المشتريات -->
            <button onclick="switchTab('purchases')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-cart-shopping text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">المشتريات</span>
            </button>
            <!-- المخازن -->
            <button onclick="switchTab('inventory')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-warehouse text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">المخزن</span>
            </button>
            <!-- تقرير الأرباح -->
            <button onclick="switchTab('profits')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-chart-pie text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">تقرير الأرباح</span>
            </button>
            <!-- تقرير الصندوق -->
            <button onclick="switchTab('cashbox')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-wallet text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">تقرير الصندوق</span>
            </button>
            <!-- العملاء / الديون -->
            <button onclick="switchTab('customers')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-users text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">العملاء والديون</span>
            </button>
            <!-- الموردين -->
            <button onclick="switchTab('suppliers')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-truck-field text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">الموردين</span>
            </button>
            <!-- التقارير الرسمية -->
            <button onclick="switchTab('reports')" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:bg-emerald-50 transition active:scale-95">
                <div class="bg-emerald-100 text-darkGreen p-3 rounded-2xl mb-2">
                    <i class="fa-solid fa-file-lines text-xl"></i>
                </div>
                <span class="text-xs font-bold text-gray-700">تقارير نهائية</span>
            </button>
        </div>

        <!-- Dynamic Section Content -->
        <div id="content-area" class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 min-h-[300px]">
            <!-- Content changes based on active tab -->
            <div id="tab-dashboard" class="tab-content space-y-4">
                <h2 class="font-bold text-gray-800 text-base border-b pb-2"><i class="fa-solid fa-fire text-primary ml-2"></i>الإشعارات والتنبيهات السريعة</h2>
                <div id="low-stock-alert" class="bg-amber-50 border border-amber-200 p-3 rounded-xl text-amber-800 text-sm flex items-center justify-between">
                    <span><i class="fa-solid fa-triangle-exclamation ml-2"></i> لا توجد مواد منخفضة حالياً.</span>
                </div>
                <div class="bg-emerald-50 border border-emerald-200 p-4 rounded-xl text-center">
                    <p class="text-xs text-emerald-700 font-bold mb-1">مرحباً بك في نظام ياسر ويب POS</p>
                    <p class="text-xs text-gray-600">اختر من الأقسام بالأعلى لإدارة المبيعات، المخزن، والديون بكل سهولة.</p>
                </div>
            </div>

            <div id="tab-sales" class="tab-content hidden space-y-3">
                <h2 class="font-bold text-gray-800 text-base border-b pb-2">تسجيل مبيعات جديدة</h2>
                <div class="space-y-2">
                    <label class="text-xs font-bold text-gray-600">اختر المادة</label>
                    <select id="sale-product" class="w-full p-2.5 border rounded-xl text-sm focus:outline-none focus:border-primary"></select>
                </div>
                <div class="space-y-2">
                    <label class="text-xs font-bold text-gray-600">الكمية المباعة</label>
                    <input type="number" id="sale-qty" value="1" min="1" class="w-full p-2.5 border rounded-xl text-sm focus:outline-none focus:border-primary">
                </div>
                <button onclick="executeSale()" class="w-full bg-primary text-white py-3 rounded-xl font-bold shadow hover:bg-darkGreen transition">إتمام البيع وتوليد الفاتورة</button>
            </div>

            <div id="tab-inventory" class="tab-content hidden space-y-3">
                <div class="flex justify-between items-center border-b pb-2">
                    <h2 class="font-bold text-gray-800 text-base">إدارة المخزن</h2>
                    <button onclick="openAddProductModal()" class="bg-primary text-white text-xs px-3 py-1.5 rounded-lg"><i class="fa-solid fa-plus ml-1"></i>مادة جديدة</button>
                </div>
                <div id="inventory-list" class="space-y-2 max-h-60 overflow-y-auto">
                    <!-- Products list injected via JS -->
                </div>
            </div>

            <div id="tab-customers" class="tab-content hidden space-y-3">
                <h2 class="font-bold text-gray-800 text-base border-b pb-2">سجل العملاء والديون</h2>
                <div class="space-y-2">
                    <input type="text" id="cust-name" placeholder="اسم الزبون" class="w-full p-2.5 border rounded-xl text-sm">
                    <input type="number" id="cust-debt" placeholder="المبلغ الدائن/المديون" class="w-full p-2.5 border rounded-xl text-sm">
                    <button onclick="addCustomer()" class="w-full bg-primary text-white py-2 rounded-xl text-sm font-bold">حفظ الزبون والديون</button>
                </div>
                <div id="customers-list" class="space-y-2 mt-4 max-h-48 overflow-y-auto"></div>
            </div>

            <div id="tab-purchases" class="tab-content hidden space-y-3">
                <h2 class="font-bold text-gray-800 text-base border-b pb-2">المشتريات وإدخال بضاعة</h2>
                <p class="text-xs text-gray-500">أضف بضاعة جديدة للمخزن مباشرة.</p>
            </div>

            <div id="tab-profits" class="tab-content hidden space-y-3">
                <h2 class="font-bold text-gray-800 text-base border-b pb-2">تقرير الأرباح</h2>
                <p class="text-xs text-gray-500">صافي الأرباح يعتمد على فرق سعر الشراء وسعر البيع.</p>
                <div class="bg-gray-50 p-4 rounded-xl text-center">
                    <span class="text-sm text-gray-600">إجمالي الأرباح الصافية:</span>
                    <h3 id="net-profit-val" class="text-xl font-bold text-primary mt-1">0.00 د.ع</h3>
                </div>
            </div>

            <div id="tab-cashbox" class="tab-content hidden space-y-3">
                <h2 class="font-bold text-gray-800 text-base border-b pb-2">تقرير الصندوق اليومي</h2>
                <div class="bg-emerald-50 p-4 rounded-xl text-center space-y-1">
                    <span class="text-xs text-emerald-800">حركة الصندوق لهذا اليوم</span>
                    <h3 id="cashbox-total" class="text-2xl font-bold text-darkGreen">0.00 د.ع</h3>
                </div>
            </div>

            <div id="tab-suppliers" class="tab-content hidden space-y-3">
                <h2 class="font-bold text-gray-800 text-base border-b pb-2">الموردين</h2>
                <p class="text-xs text-gray-500">قائمة الموردين وأرقام التواصل.</p>
            </div>

            <div id="tab-reports" class="tab-content hidden space-y-3">
                <h2 class="font-bold text-gray-800 text-base border-b pb-2">التقارير النهائية</h2>
                <p class="text-xs text-gray-500">تقارير عامة لحركة المحل والمخزون.</p>
            </div>
        </div>

    </main>

    <!-- Bottom Navigation Bar -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-50">
        <div class="max-w-md mx-auto flex justify-around py-2">
            <button onclick="switchTab('sales')" class="flex flex-col items-center text-primary text-xs">
                <i class="fa-solid fa-cash-register text-lg"></i>
                <span>المبيعات</span>
            </button>
            <button onclick="switchTab('purchases')" class="flex flex-col items-center text-gray-500 text-xs hover:text-primary">
                <i class="fa-solid fa-cart-shopping text-lg"></i>
                <span>المشتريات</span>
            </button>
            <button onclick="switchTab('inventory')" class="flex flex-col items-center text-gray-500 text-xs hover:text-primary">
                <i class="fa-solid fa-warehouse text-lg"></i>
                <span>المخازن</span>
            </button>
            <button onclick="switchTab('reports')" class="flex flex-col items-center text-gray-500 text-xs hover:text-primary">
                <i class="fa-solid fa-chart-column text-lg"></i>
                <span>التقارير</span>
            </button>
            <button onclick="switchTab('dashboard')" class="flex flex-col items-center text-gray-500 text-xs hover:text-primary">
                <i class="fa-solid fa-wallet text-lg"></i>
                <span>المالية</span>
            </button>
        </div>
    </nav>

    <!-- Modal for adding product -->
    <div id="product-modal" class="fixed inset-0 bg-black/50 hidden z-50 flex items-center justify-center p-4">
        <div class="bg-white p-5 rounded-2xl w-full max-w-sm space-y-3">
            <h3 class="font-bold text-gray-800">إضافة مادة جديدة للمخزن</h3>
            <input type="text" id="new-p-name" placeholder="اسم المادة" class="w-full p-2.5 border rounded-xl text-sm">
            <input type="number" id="new-p-price" placeholder="سعر البيع" class="w-full p-2.5 border rounded-xl text-sm">
            <input type="number" id="new-p-qty" placeholder="الكمية المتوفرة" class="w-full p-2.5 border rounded-xl text-sm">
            <div class="flex space-x-2 space-x-reverse pt-2">
                <button onclick="saveNewProduct()" class="flex-1 bg-primary text-white py-2 rounded-xl text-sm font-bold">حفظ</button>
                <button onclick="closeAddProductModal()" class="flex-1 bg-gray-200 text-gray-700 py-2 rounded-xl text-sm">إلغاء</button>
            </div>
        </div>
    </div>

    <!-- JavaScript Logic -->
    <script>
        let products = JSON.parse(localStorage.getItem('yasser_products')) || [
            { id: 1, name: 'عطر الفخامة', price: 15000, qty: 12 },
            { id: 2, name: 'كريم مرطب', price: 8000, qty: 3 }
        ];
        let customers = JSON.parse(localStorage.getItem('yasser_customers')) || [];
        let totalSales = parseFloat(localStorage.getItem('yasser_sales')) || 0.0;

        function initApp() {
            document.getElementById('current-date').innerText = new Date().toLocaleDateString('ar-IQ');
            updateUI();
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById('tab-' + tabId).classList.remove('hidden');
        }

        function updateUI() {
            document.getElementById('total-sales').innerText = totalSales.toLocaleString() + ' د.ع';
            document.getElementById('cashbox-total').innerText = totalSales.toLocaleString() + ' د.ع';
            
            let totalStock = products.reduce((sum, p) => sum + parseInt(p.qty), 0);
            document.getElementById('total-stock-count').innerText = totalStock;

            let select = document.getElementById('sale-product');
            select.innerHTML = '';
            let invList = document.getElementById('inventory-list');
            invList.innerHTML = '';

            let lowStockHtml = '';
            products.forEach(p => {
                select.innerHTML += `<option value="${p.id}">${p.name} - ${p.price} د.ع (متوفر: ${p.qty})</option>`;
                invList.innerHTML += `<div class="flex justify-between items-center p-2.5 bg-gray-50 rounded-xl text-sm">
                    <span>${p.name}</span>
                    <span class="font-bold text-darkGreen">${p.price} د.ع | الكمية: ${p.qty}</span>
                </div>`;
                if(p.qty <= 5) {
                    lowStockHtml += `<div class="text-xs text-amber-800"><i class="fa-solid fa-triangle-exclamation ml-1"></i> مادة (${p.name}) قاربت على النفاد (المتبقي: ${p.qty})</div>`;
                }
            });

            if(lowStockHtml !== '') {
                document.getElementById('low-stock-alert').innerHTML = lowStockHtml;
            } else {
                document.getElementById('low-stock-alert').innerHTML = `<span><i class="fa-solid fa-circle-check ml-2 text-emerald-600"></i> المخزون مستقر ولا توجد نواقص حرجة.</span>`;
            }

            let custList = document.getElementById('customers-list');
            custList.innerHTML = '';
            customers.forEach(c => {
                custList.innerHTML += `<div class="flex justify-between items-center p-2.5 bg-gray-50 rounded-xl text-sm">
                    <span>${c.name}</span>
                    <span class="font-bold text-red-600">المبلغ: ${c.debt} د.ع</span>
                </div>`;
            });

            localStorage.setItem('yasser_products', JSON.stringify(products));
            localStorage.setItem('yasser_customers', JSON.stringify(customers));
            localStorage.setItem('yasser_sales', totalSales);
        }

        function executeSale() {
            let pId = document.getElementById('sale-product').value;
            let qty = parseInt(document.getElementById('sale-qty').value);
            let product = products.find(p => p.id == pId);
            
            if(product && product.qty >= qty) {
                product.qty -= qty;
                totalSales += (product.price * qty);
                updateUI();
                alert('تمت عملية البيع بنجاح وتم تحديث المخزن والصندوق!');
            } else {
                alert('الكمية المطلوبة غير متوفرة في المخزن!');
            }
        }

        function openAddProductModal() {
            document.getElementById('product-modal').classList.remove('hidden');
        }

        function closeAddProductModal() {
            document.getElementById('product-modal').classList.add('hidden');
        }

        function saveNewProduct() {
            let name = document.getElementById('new-p-name').value;
            let price = parseFloat(document.getElementById('new-p-price').value);
            let qty = parseInt(document.getElementById('new-p-qty').value);

            if(name && price && qty) {
                products.push({ id: Date.now(), name, price, qty });
                closeAddProductModal();
                updateUI();
                document.getElementById('new-p-name').value = '';
                document.getElementById('new-p-price').value = '';
                document.getElementById('new-p-qty').value = '';
            } else {
                alert('يرجى ملء جميع الحقول بشكل صحيح.');
            }
        }

        function addCustomer() {
            let name = document.getElementById('cust-name').value;
            let debt = parseFloat(document.getElementById('cust-debt').value) || 0;
            if(name) {
                customers.push({ name, debt });
                updateUI();
                document.getElementById('cust-name').value = '';
                document.getElementById('cust-debt').value = '';
                alert('تم حفظ بيانات العميل بنجاح.');
            }
        }

        initApp();
    </script>
</body>
</html>
