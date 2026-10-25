import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ياسر ويب POS", layout="wide")

html_code = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ياسر ويب POS - نظام إدارة المبيعات</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        purpleBrand: '#6b46c1',
                        purpleLight: '#f3e8ff',
                        bgApp: '#faf5ff',
                        cardBg: '#ffffff'
                    }
                }
            }
        }
    </script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #553c9a;
            font-family: system-ui, -apple-system, sans-serif;
        }
        .hide-scroll::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="text-gray-800 flex justify-center items-start min-h-screen p-0 sm:p-4">

    <!-- Phone Container -->
    <div class="w-full max-w-md bg-white min-h-screen sm:min-h-[840px] sm:rounded-[38px] shadow-2xl overflow-hidden flex flex-col relative pb-16 border-4 border-gray-900/10">

        <!-- Top Status/App Bar -->
        <header class="bg-white px-4 pt-4 pb-2 border-b border-purple-50 flex justify-between items-center sticky top-0 z-40">
            <button onclick="switchTab('dashboard')" class="text-purpleBrand text-lg">
                <i class="fa-solid fa-bars-staggered"></i>
            </button>
            <div class="text-center">
                <h1 class="font-bold text-gray-800 text-base tracking-wide">YASSER POS</h1>
                <p class="text-[10px] text-purpleBrand font-semibold">إدارة المبيعات والمخزن</p>
            </div>
            <div class="flex items-center space-x-2 space-x-reverse">
                <!-- Shopping Cart Icon with Count Badge -->
                <button onclick="openCartView()" class="relative text-purpleBrand text-xl p-1">
                    <i class="fa-solid fa-cart-shopping"></i>
                    <span id="cart-badge" class="absolute -top-1 -right-1 bg-purpleBrand text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">0</span>
                </button>
                <button onclick="logout()" class="text-gray-400 text-sm hover:text-red-500">
                    <i class="fa-solid fa-gear"></i>
                </button>
            </div>
        </header>

        <!-- Main Workspace Area -->
        <main class="flex-1 overflow-y-auto bg-purple-50/30 p-4 space-y-4 hide-scroll">

            <!-- 1. DASHBOARD VIEW (Grid Menu matching TOFA Design) -->
            <div id="view-dashboard" class="view-panel space-y-4">
                <div class="grid grid-cols-2 gap-3">

                    <button onclick="switchTab('create-invoice')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl">
                            <i class="fa-solid fa-file-circle-plus text-xl"></i>
                        </div>
                        <span class="text-xs font-bold text-gray-800">إنشاء فاتورة</span>
                        <span class="text-[10px] text-gray-400">إصدار الفواتير والطباعة</span>
                    </button>

                    <button onclick="switchTab('invoices-list')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl">
                            <i class="fa-solid fa-receipt text-xl"></i>
                        </div>
                        <span class="text-xs font-bold text-gray-800">قائمة الفواتير</span>
                        <span class="text-[10px] text-gray-400">سجل الفواتير المباعة</span>
                    </button>

                    <button onclick="switchTab('inventory')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl">
                            <i class="fa-solid fa-box text-xl"></i>
                        </div>
                        <span class="text-xs font-bold text-gray-800">المخزن</span>
                        <span class="text-[10px] text-gray-400">إدارة المشتريات والمخزون</span>
                    </button>

                    <button onclick="switchTab('customers')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl">
                            <i class="fa-solid fa-user-group text-xl"></i>
                        </div>
                        <span class="text-xs font-bold text-gray-800">العملاء</span>
                        <span class="text-[10px] text-gray-400">إدارة العملاء والديون</span>
                    </button>

                    <button onclick="switchTab('bonds')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl">
                            <i class="fa-solid fa-wallet text-xl"></i>
                        </div>
                        <span class="text-xs font-bold text-gray-800">السندات</span>
                        <span class="text-[10px] text-gray-400">سندات قبض وصرف</span>
                    </button>

                    <button onclick="switchTab('reports')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl">
                            <i class="fa-solid fa-chart-pie text-xl"></i>
                        </div>
                        <span class="text-xs font-bold text-gray-800">الإحصائيات</span>
                        <span class="text-[10px] text-gray-400">التقارير وصافي الربح</span>
                    </button>

                </div>
            </div>

            <!-- 2. CREATE INVOICE VIEW (Products Grid + Add to Cart) -->
            <div id="view-create-invoice" class="view-panel hidden space-y-3">
                <div class="flex justify-between items-center bg-white p-3 rounded-2xl border border-purple-100">
                    <span class="text-xs font-bold text-gray-700">اختيار المواد من المعرض</span>
                    <span id="inv-num-tag" class="bg-purpleLight text-purpleBrand px-2 py-0.5 rounded-full text-xs font-bold">#1001</span>
                </div>

                <!-- Products Grid -->
                <div id="products-grid" class="grid grid-cols-2 gap-3">
                    <!-- Dynamic Product Cards Injected Here -->
                </div>
            </div>

            <!-- 3. CART & CHECKOUT MODAL VIEW -->
            <div id="view-cart" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-3">
                    <h3 class="font-bold text-gray-800 text-sm border-b pb-2">تفاصيل الفاتورة والعميل</h3>
                    
                    <!-- Select Customer -->
                    <div class="space-y-1">
                        <label class="text-[11px] font-bold text-gray-500">اختر العميل (مضاف مسبقاً)</label>
                        <select id="cart-customer-select" class="w-full p-2.5 border rounded-xl text-xs bg-gray-50 focus:outline-none focus:border-purpleBrand">
                            <!-- Customers Injected -->
                        </select>
                    </div>

                    <!-- Cart Selected Items List -->
                    <div class="space-y-2">
                        <label class="text-[11px] font-bold text-gray-500">المواد المضافة بالسلة</label>
                        <div id="cart-items-container" class="space-y-2 max-h-48 overflow-y-auto">
                            <!-- Items Injected -->
                        </div>
                    </div>

                    <!-- Invoice Summary -->
                    <div class="bg-purpleLight/50 p-3 rounded-xl space-y-1">
                        <div class="flex justify-between text-xs">
                            <span class="text-gray-600">المجموع الكلي:</span>
                            <span id="cart-total-price" class="font-bold text-purpleBrand">0 د.ع</span>
                        </div>
                    </div>

                    <button onclick="finalizeSale()" class="w-full bg-purpleBrand text-white py-3 rounded-xl text-xs font-bold shadow-md hover:bg-purple-800 transition flex items-center justify-center space-x-2 space-x-reverse">
                        <i class="fa-solid fa-print"></i>
                        <span>بيع وطباعة الفاتورة</span>
                    </button>
                </div>
            </div>

            <!-- 4. INVENTORY MANAGEMENT VIEW -->
            <div id="view-inventory" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-3">
                    <div class="flex justify-between items-center border-b pb-2">
                        <h3 class="font-bold text-gray-800 text-sm">إدارة المخزن والمواد</h3>
                        <button onclick="toggleAddProductForm()" class="bg-purpleBrand text-white text-xs px-3 py-1.5 rounded-lg"><i class="fa-solid fa-plus ml-1"></i>مادة جديدة</button>
                    </div>

                    <div id="add-p-form" class="hidden space-y-2 bg-purple-50/50 p-3 rounded-xl">
                        <input type="text" id="p-name" placeholder="اسم المادة" class="w-full p-2 border rounded-lg text-xs">
                        <input type="number" id="p-price" placeholder="السعر (د.ع)" class="w-full p-2 border rounded-lg text-xs">
                        <input type="number" id="p-qty" placeholder="الكمية" class="w-full p-2 border rounded-lg text-xs">
                        <button onclick="saveProduct()" class="w-full bg-purpleBrand text-white py-2 rounded-lg text-xs font-bold">حفظ المادة</button>
                    </div>

                    <div id="inventory-list" class="space-y-2 max-h-60 overflow-y-auto"></div>
                </div>
            </div>

            <!-- 5. CUSTOMERS VIEW -->
            <div id="view-customers" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-3">
                    <h3 class="font-bold text-gray-800 text-sm border-b pb-2">إدارة العملاء والديون</h3>
                    <div class="space-y-2">
                        <input type="text" id="c-name" placeholder="اسم العميل" class="w-full p-2 border rounded-lg text-xs">
                        <input type="text" id="c-phone" placeholder="رقم الهاتف" class="w-full p-2 border rounded-lg text-xs">
                        <input type="number" id="c-debt" placeholder="مبلغ الدين الساقط" class="w-full p-2 border rounded-lg text-xs">
                        <button onclick="saveCustomer()" class="w-full bg-purpleBrand text-white py-2 rounded-lg text-xs font-bold">إضافة عميل</button>
                    </div>
                    <div id="customers-list" class="space-y-2 max-h-48 overflow-y-auto pt-2"></div>
                </div>
            </div>

            <!-- 6. BONDS & EXPENSES VIEW -->
            <div id="view-bonds" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-2">
                    <h3 class="font-bold text-gray-800 text-sm border-b pb-2">السندات والمصروفات</h3>
                    <div class="grid grid-cols-2 gap-2 text-center text-xs">
                        <div class="bg-green-50 text-green-700 p-2.5 rounded-xl border border-green-100">
                            <span>سند قبض</span>
                            <h4 id="bond-in" class="font-bold text-sm mt-0.5">0 د.ع</h4>
                        </div>
                        <div class="bg-red-50 text-red-700 p-2.5 rounded-xl border border-red-100">
                            <span>سند صرف</span>
                            <h4 id="bond-out" class="font-bold text-sm mt-0.5">0 د.ع</h4>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 7. REPORTS & STATS VIEW -->
            <div id="view-reports" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-3">
                    <h3 class="font-bold text-gray-800 text-sm border-b pb-2">الإحصائيات والتقارير</h3>
                    <div class="bg-purpleLight p-3 rounded-xl text-center">
                        <span class="text-xs text-purpleBrand font-semibold">رصيد الصندوق والأرباح</span>
                        <h2 id="stats-total" class="text-xl font-bold text-purpleBrand mt-1">0 د.ع</h2>
                    </div>
                </div>
            </div>

        </main>

        <!-- Dynamic Floating Cart Bar (Appears when items added) -->
        <div id="floating-cart-bar" class="hidden absolute bottom-16 left-4 right-4 bg-purpleBrand text-white p-3 rounded-2xl shadow-xl flex justify-between items-center z-30">
            <div class="flex items-center space-x-2 space-x-reverse">
                <i class="fa-solid fa-basket-shopping text-lg"></i>
                <span id="floating-cart-text" class="text-xs font-bold">1 مواد مضافة</span>
            </div>
            <button onclick="openCartView()" class="bg-white text-purpleBrand text-xs font-bold px-3 py-1.5 rounded-xl">عرض السلة</button>
        </div>

        <!-- Bottom Navigation Bar -->
        <nav class="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-100 py-2 px-4 flex justify-around items-center z-40">
            <button onclick="switchTab('dashboard')" class="flex flex-col items-center text-purpleBrand text-[10px] font-bold">
                <i class="fa-solid fa-house text-base"></i>
                <span>الرئيسية</span>
            </button>
            <button onclick="switchTab('create-invoice')" class="flex flex-col items-center text-gray-400 hover:text-purpleBrand text-[10px]">
                <i class="fa-solid fa-plus-circle text-base"></i>
                <span>فاتورة</span>
            </button>
            <button onclick="switchTab('inventory')" class="flex flex-col items-center text-gray-400 hover:text-purpleBrand text-[10px]">
                <i class="fa-solid fa-boxes-stacked text-base"></i>
                <span>المخزن</span>
            </button>
            <button onclick="switchTab('customers')" class="flex flex-col items-center text-gray-400 hover:text-purpleBrand text-[10px]">
                <i class="fa-solid fa-users text-base"></i>
                <span>العملاء</span>
            </button>
        </nav>

    </div>

    <script>
        let products = JSON.parse(localStorage.getItem('tofa_products')) || [
            { id: 1, name: 'شاشة 32 سمارت', price: 350000, qty: 5 },
            { id: 2, name: 'شاشة 42 سمارت', price: 420000, qty: 3 }
        ];
        let customers = JSON.parse(localStorage.getItem('tofa_customers')) || [
            { id: 1, name: 'السيد احمد', phone: '07700000000', debt: 0 }
        ];
        let cart = [];
        let totalSales = parseFloat(localStorage.getItem('tofa_sales')) || 0;

        function switchTab(viewId) {
            document.querySelectorAll('.view-panel').forEach(el => el.classList.add('hidden'));
            let target = document.getElementById('view-' + viewId);
            if(target) target.classList.remove('hidden');
        }

        function renderProductsGrid() {
            let grid = document.getElementById('products-grid');
            grid.innerHTML = '';
            products.forEach(p => {
                grid.innerHTML += `
                    <div class="bg-white p-3 rounded-2xl border border-purple-100 shadow-sm flex flex-col justify-between space-y-2">
                        <div class="bg-purple-50 p-4 rounded-xl flex items-center justify-center text-purpleBrand">
                            <i class="fa-solid fa-box-open text-2xl"></i>
                        </div>
                        <div>
                            <h4 class="font-bold text-xs text-gray-800">${p.name}</h4>
                            <p class="text-[10px] text-gray-400">المخزن: ${p.qty} | السعر: ${p.price.toLocaleString()} د.ع</p>
                        </div>
                        <button onclick="addToCart(${p.id})" class="w-full bg-purpleLight text-purpleBrand py-1.5 rounded-xl text-xs font-bold hover:bg-purpleBrand hover:text-white transition">
                            + إضافة للسلة
                        </button>
                    </div>
                `;
            });
        }

        function addToCart(pId) {
            let item = products.find(p => p.id === pId);
            if(item && item.qty > 0) {
                let cartItem = cart.find(c => c.id === pId);
                if(cartItem) {
                    cartItem.cartQty++;
                } else {
                    cart.push({ ...item, cartQty: 1 });
                }
                updateCartUI();
            } else {
                alert('المادة غير متوفرة بالكمية الكافية!');
            }
        }

        function updateCartUI() {
            let totalCount = cart.reduce((acc, i) => acc + i.cartQty, 0);
            let totalPrice = cart.reduce((acc, i) => acc + (i.price * i.cartQty), 0);

            document.getElementById('cart-badge').innerText = totalCount;
            document.getElementById('cart-total-price').innerText = totalPrice.toLocaleString() + ' د.ع';

            let bar = document.getElementById('floating-cart-bar');
            if(totalCount > 0) {
                bar.classList.remove('hidden');
                document.getElementById('floating-cart-text').innerText = totalCount + ' مواد مضافة للسلة';
            } else {
                bar.classList.add('hidden');
            }

            // Render Cart Container
            let container = document.getElementById('cart-items-container');
            container.innerHTML = '';
            cart.forEach(c => {
                container.innerHTML += `
                    <div class="flex justify-between items-center bg-gray-50 p-2 rounded-xl text-xs">
                        <span>${c.name} (${c.cartQty})</span>
                        <span class="font-bold text-purpleBrand">${(c.price * c.cartQty).toLocaleString()} د.ع</span>
                    </div>
                `;
            });
        }

        function openCartView() {
            let custSelect = document.getElementById('cart-customer-select');
            custSelect.innerHTML = '';
            customers.forEach(cust => {
                custSelect.innerHTML += `<option value="${cust.id}">${cust.name} - ${cust.phone}</option>`;
            });
            switchTab('cart');
        }

        function finalizeSale() {
            if(cart.length === 0) {
                alert('السلة فارغة!');
                return;
            }

            cart.forEach(cItem => {
                let original = products.find(p => p.id === cItem.id);
                if(original) original.qty -= cItem.cartQty;
            });

            let sum = cart.reduce((acc, i) => acc + (i.price * i.cartQty), 0);
            totalSales += sum;

            cart = [];
            updateCartUI();
            saveData();
            renderProductsGrid();
            renderInventory();
            switchTab('dashboard');
            alert('تمت عملية البيع وطباعة الفاتورة بنجاح!');
        }

        function renderInventory() {
            let inv = document.getElementById('inventory-list');
            inv.innerHTML = '';
            products.forEach(p => {
                inv.innerHTML += `
                    <div class="flex justify-between items-center bg-gray-50 p-2 rounded-xl text-xs">
                        <span>${p.name}</span>
                        <span class="font-bold text-purpleBrand">${p.price.toLocaleString()} د.ع (المتبقي: ${p.qty})</span>
                    </div>
                `;
            });
        }

        function toggleAddProductForm() {
            document.getElementById('add-p-form').classList.toggle('hidden');
        }

        function saveProduct() {
            let name = document.getElementById('p-name').value;
            let price = parseFloat(document.getElementById('p-price').value);
            let qty = parseInt(document.getElementById('p-qty').value);
            if(name && price && qty) {
                products.push({ id: Date.now(), name, price, qty });
                saveData();
                renderProductsGrid();
                renderInventory();
                toggleAddProductForm();
            }
        }

        function saveCustomer() {
            let name = document.getElementById('c-name').value;
            let phone = document.getElementById('c-phone').value;
            let debt = parseFloat(document.getElementById('c-debt').value) || 0;
            if(name) {
                customers.push({ id: Date.now(), name, phone, debt });
                saveData();
                renderCustomers();
            }
        }

        function renderCustomers() {
            let list = document.getElementById('customers-list');
            list.innerHTML = '';
            customers.forEach(c => {
                list.innerHTML += `
                    <div class="flex justify-between items-center bg-gray-50 p-2 rounded-xl text-xs">
                        <span>${c.name} (${c.phone})</span>
                        <span class="font-bold text-red-600">${c.debt} د.ع</span>
                    </div>
                `;
            });
        }

        function saveData() {
            localStorage.setItem('tofa_products', JSON.stringify(products));
            localStorage.setItem('tofa_customers', JSON.stringify(customers));
            localStorage.setItem('tofa_sales', totalSales);
            document.getElementById('stats-total').innerText = totalSales.toLocaleString() + ' د.ع';
        }

        renderProductsGrid();
        renderInventory();
        renderCustomers();
        saveData();
    </script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=True)
