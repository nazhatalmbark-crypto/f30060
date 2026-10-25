import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ياسر ويب POS", layout="wide")

html_code = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ياسر ويب POS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        purpleBrand: '#6b46c1',
                        purpleLight: '#f3e8ff',
                        bgApp: '#faf5ff',
                    }
                }
            }
        }
    </script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #553c9a; font-family: system-ui, -apple-system, sans-serif; }
        .hide-scroll::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="text-gray-800 flex justify-center items-start min-h-screen p-0 sm:p-4">

    <!-- Phone Container -->
    <div class="w-full max-w-md bg-white min-h-screen sm:min-h-[840px] sm:rounded-[38px] shadow-2xl overflow-hidden flex flex-col relative pb-16 border-4 border-gray-900/10">

        <!-- Header -->
        <header class="bg-white px-4 pt-4 pb-2 border-b border-purple-50 flex justify-between items-center sticky top-0 z-40">
            <button onclick="switchTab('dashboard')" class="text-purpleBrand text-lg">
                <i class="fa-solid fa-bars-staggered"></i>
            </button>
            <div class="text-center">
                <h1 class="font-bold text-gray-800 text-base tracking-wide">YASSER POS</h1>
                <p class="text-[10px] text-purpleBrand font-semibold">إدارة المبيعات والمخزن</p>
            </div>
            <div class="flex items-center space-x-3 space-x-reverse">
                <!-- Shopping Cart Icon with Live Count -->
                <button onclick="openCartView()" class="relative text-purpleBrand text-xl p-1">
                    <i class="fa-solid fa-cart-shopping"></i>
                    <span id="cart-badge" class="absolute -top-1 -right-2 bg-purpleBrand text-white text-[10px] w-5 h-5 rounded-full flex items-center justify-center font-bold">0</span>
                </button>
                <button onclick="logout()" class="text-gray-400 text-sm hover:text-red-500">
                    <i class="fa-solid fa-gear"></i>
                </button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="flex-1 overflow-y-auto bg-purple-50/30 p-4 space-y-4 hide-scroll">

            <!-- 1. DASHBOARD VIEW -->
            <div id="view-dashboard" class="view-panel space-y-4">
                <div class="grid grid-cols-2 gap-3">
                    <button onclick="switchTab('create-invoice')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl"><i class="fa-solid fa-file-circle-plus text-xl"></i></div>
                        <span class="text-xs font-bold text-gray-800">إنشاء فاتورة (عرض الشبكة)</span>
                        <span class="text-[10px] text-gray-400">إصدار الفواتير والطباعة</span>
                    </button>

                    <button onclick="switchTab('invoices-list')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl"><i class="fa-solid fa-receipt text-xl"></i></div>
                        <span class="text-xs font-bold text-gray-800">قائمة الفواتير</span>
                        <span class="text-[10px] text-gray-400">سجل الفواتير المباعة</span>
                    </button>

                    <button onclick="switchTab('inventory')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl"><i class="fa-solid fa-box text-xl"></i></div>
                        <span class="text-xs font-bold text-gray-800">المخزن</span>
                        <span class="text-[10px] text-gray-400">إدارة المواد والمشتريات</span>
                    </button>

                    <button onclick="switchTab('customers')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl"><i class="fa-solid fa-user-group text-xl"></i></div>
                        <span class="text-xs font-bold text-gray-800">العملاء والديون</span>
                        <span class="text-[10px] text-gray-400">سجل العملاء والحسابات</span>
                    </button>

                    <button onclick="switchTab('bonds')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl"><i class="fa-solid fa-wallet text-xl"></i></div>
                        <span class="text-xs font-bold text-gray-800">السندات والمصروفات</span>
                        <span class="text-[10px] text-gray-400">سندات قبض وصرف</span>
                    </button>

                    <button onclick="switchTab('reports')" class="bg-white p-4 rounded-2xl shadow-sm border border-purple-100 flex flex-col items-center justify-center text-center space-y-2 hover:bg-purple-50 transition">
                        <div class="bg-purpleLight text-purpleBrand p-3 rounded-2xl"><i class="fa-solid fa-chart-pie text-xl"></i></div>
                        <span class="text-xs font-bold text-gray-800">الإحصائيات والأرباح</span>
                        <span class="text-[10px] text-gray-400">التقارير والصندوق</span>
                    </button>
                </div>
            </div>

            <!-- 2. CREATE INVOICE VIEW (Grid of Products) -->
            <div id="view-create-invoice" class="view-panel hidden space-y-3">
                <div class="flex justify-between items-center bg-white p-3 rounded-2xl border border-purple-100">
                    <span class="text-xs font-bold text-gray-700">شبكة المواد المتاحة</span>
                    <button onclick="switchTab('inventory')" class="text-[11px] bg-purpleLight text-purpleBrand px-2.5 py-1 rounded-xl font-bold">+ إضافة مادة للمخزن</button>
                </div>

                <!-- Products Grid Container -->
                <div id="products-grid" class="grid grid-cols-2 gap-3">
                    <!-- Cards Injected Here -->
                </div>
            </div>

            <!-- 3. CART & CHECKOUT VIEW -->
            <div id="view-cart" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-3">
                    <h3 class="font-bold text-gray-800 text-sm border-b pb-2">إتمام البيع ونوع الفاتورة</h3>
                    
                    <!-- Sale Type: Cash or Credit -->
                    <div class="space-y-1">
                        <label class="text-[11px] font-bold text-gray-600">نوع البيع</label>
                        <select id="sale-type" class="w-full p-2.5 border rounded-xl text-xs bg-gray-50 font-bold focus:outline-none">
                            <option value="cash">نقداً (كاش)</option>
                            <option value="credit">آجل (دين)</option>
                        </select>
                    </div>

                    <!-- Customer Selection & Auto-fill -->
                    <div class="space-y-2 bg-purple-50/60 p-3 rounded-xl border border-purple-100">
                        <label class="text-[11px] font-bold text-purpleBrand">اختر العميل (تعبئة تلقائية)</label>
                        <select id="cart-customer-select" onchange="autoFillCustomerData()" class="w-full p-2 border rounded-xl text-xs bg-white focus:outline-none">
                            <!-- Injected -->
                        </select>
                        <input type="text" id="cust-phone-filled" readonly placeholder="رقم الهاتف" class="w-full p-2 border rounded-xl text-xs bg-gray-100 text-gray-600">
                        <input type="text" id="cust-address-filled" readonly placeholder="العنوان" class="w-full p-2 border rounded-xl text-xs bg-gray-100 text-gray-600">
                    </div>

                    <!-- Cart Items Summary -->
                    <div class="space-y-1">
                        <label class="text-[11px] font-bold text-gray-600">المواد المحددة الفاتورة</label>
                        <div id="cart-items-container" class="space-y-1.5 max-h-40 overflow-y-auto"></div>
                    </div>

                    <!-- Total Price Card -->
                    <div class="bg-purpleLight p-3 rounded-xl flex justify-between items-center text-xs">
                        <span class="font-bold text-purpleBrand">المجموع الكلي:</span>
                        <span id="cart-total-price" class="text-base font-black text-purpleBrand">0 د.ع</span>
                    </div>

                    <button onclick="finalizeSale()" class="w-full bg-purpleBrand text-white py-3 rounded-xl text-xs font-bold shadow-md hover:bg-purple-800 transition flex items-center justify-center space-x-2 space-x-reverse">
                        <i class="fa-solid fa-print"></i>
                        <span>إتمام البيع وطباعة الفاتورة</span>
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

                    <div id="add-p-form" class="hidden space-y-2 bg-purple-50/50 p-3 rounded-xl border border-purple-100">
                        <input type="text" id="p-name" placeholder="اسم المادة" class="w-full p-2 border rounded-lg text-xs">
                        <input type="number" id="p-price" placeholder="السعر (د.ع)" class="w-full p-2 border rounded-lg text-xs">
                        <input type="number" id="p-qty" placeholder="الكمية المتوفرة" class="w-full p-2 border rounded-lg text-xs">
                        <button onclick="saveProduct()" class="w-full bg-purpleBrand text-white py-2 rounded-lg text-xs font-bold">حفظ المادة بالشبكة</button>
                    </div>

                    <div id="inventory-list" class="space-y-2 max-h-60 overflow-y-auto"></div>
                </div>
            </div>

            <!-- 5. CUSTOMERS VIEW -->
            <div id="view-customers" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-3">
                    <h3 class="font-bold text-gray-800 text-sm border-b pb-2">إضافة وإدارة العملاء</h3>
                    <div class="space-y-2">
                        <input type="text" id="c-name" placeholder="اسم العميل الكامل" class="w-full p-2 border rounded-lg text-xs">
                        <input type="text" id="c-phone" placeholder="رقم الهاتف" class="w-full p-2 border rounded-lg text-xs">
                        <input type="text" id="c-address" placeholder="العنوان / المنطقة" class="w-full p-2 border rounded-lg text-xs">
                        <button onclick="saveCustomer()" class="w-full bg-purpleBrand text-white py-2 rounded-lg text-xs font-bold">حفظ العميل</button>
                    </div>
                    <div id="customers-list" class="space-y-2 max-h-48 overflow-y-auto pt-2"></div>
                </div>
            </div>

            <!-- 6. BONDS VIEW -->
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

            <!-- 7. REPORTS & INVOICES LIST VIEW -->
            <div id="view-invoices-list" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-3">
                    <h3 class="font-bold text-gray-800 text-sm border-b pb-2">سجل الفواتير المباعة</h3>
                    <div id="invoices-history-list" class="space-y-2 max-h-60 overflow-y-auto text-xs"></div>
                </div>
            </div>

            <div id="view-reports" class="view-panel hidden space-y-3">
                <div class="bg-white p-4 rounded-2xl border border-purple-100 space-y-3">
                    <h3 class="font-bold text-gray-800 text-sm border-b pb-2">الإحصائيات العامة والصندوق</h3>
                    <div class="bg-purpleLight p-4 rounded-xl text-center">
                        <span class="text-xs text-purpleBrand font-semibold">إجمالي المبيعات المحققة</span>
                        <h2 id="stats-total" class="text-2xl font-bold text-purpleBrand mt-1">0 د.ع</h2>
                    </div>
                </div>
            </div>

        </main>

        <!-- Bottom Navigation Bar -->
        <nav class="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-100 py-2 px-4 flex justify-around items-center z-40">
            <button onclick="switchTab('dashboard')" class="flex flex-col items-center text-purpleBrand text-[10px] font-bold">
                <i class="fa-solid fa-house text-base"></i>
                <span>الرئيسية</span>
            </button>
            <button onclick="switchTab('create-invoice')" class="flex flex-col items-center text-gray-400 hover:text-purpleBrand text-[10px]">
                <i class="fa-solid fa-table-cells text-base"></i>
                <span>الشبكة</span>
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

        <!-- Login Screen Modal -->
        <div id="login-modal" class="fixed inset-0 bg-purpleBrand/95 z-50 flex items-center justify-center p-4">
            <div class="bg-white p-6 rounded-3xl w-full max-w-xs space-y-4 shadow-2xl text-center">
                <div class="bg-purpleLight text-purpleBrand w-14 h-14 rounded-full flex items-center justify-center mx-auto text-xl font-bold">
                    <i class="fa-solid fa-lock"></i>
                </div>
                <h2 class="text-base font-bold text-gray-800">تسجيل الدخول - ياسر ويب</h2>
                <div class="space-y-2 text-right">
                    <input type="text" id="user-in" placeholder="اسم المستخدم" class="w-full p-2.5 border rounded-xl text-xs">
                    <input type="password" id="pass-in" placeholder="كلمة المرور" class="w-full p-2.5 border rounded-xl text-xs">
                </div>
                <button onclick="auth()" class="w-full bg-purpleBrand text-white py-2.5 rounded-xl font-bold text-xs shadow">دخول</button>
            </div>
        </div>

    </div>

    <script>
        // Completely Zeroed Initial Data (No defaults!)
        let products = JSON.parse(localStorage.getItem('yasser_zero_products')) || [];
        let customers = JSON.parse(localStorage.getItem('yasser_zero_customers')) || [];
        let invoicesHistory = JSON.parse(localStorage.getItem('yasser_zero_invoices')) || [];
        let cart = [];
        let totalSales = parseFloat(localStorage.getItem('yasser_zero_sales')) || 0;

        function auth() {
            let u = document.getElementById('user-in').value;
            let p = document.getElementById('pass-in').value;
            if(u && p) {
                document.getElementById('login-modal').classList.add('hidden');
                localStorage.setItem('yw_auth_logged', '1');
            }
        }

        function logout() {
            localStorage.removeItem('yw_auth_logged');
            document.getElementById('login-modal').classList.remove('hidden');
        }

        function switchTab(viewId) {
            document.querySelectorAll('.view-panel').forEach(el => el.classList.add('hidden'));
            let target = document.getElementById('view-' + viewId);
            if(target) target.classList.remove('hidden');
            if(viewId === 'create-invoice') renderProductsGrid();
        }

        // Render Products Grid (Cards with "+ Add" button)
        function renderProductsGrid() {
            let grid = document.getElementById('products-grid');
            grid.innerHTML = '';

            if(products.length === 0) {
                grid.innerHTML = `<div class="col-span-2 text-center p-6 text-gray-400 text-xs">لا توجد مواد بالمخزن حالياً.<br>أضف مواد جديدة من قسم (المخزن) لتظهر هنا على شكل شبكة.</div>`;
                return;
            }

            products.forEach(p => {
                let inCartObj = cart.find(c => c.id === p.id);
                let countInCart = inCartObj ? inCartObj.cartQty : 0;

                grid.innerHTML += `
                    <div class="bg-white p-3 rounded-2xl border border-purple-100 shadow-sm flex flex-col justify-between space-y-2">
                        <div class="bg-purple-50 p-4 rounded-xl flex items-center justify-center text-purpleBrand relative">
                            <i class="fa-solid fa-box-open text-2xl"></i>
                            ${countInCart > 0 ? `<span class="absolute top-1 right-1 bg-purpleBrand text-white text-[10px] w-5 h-5 rounded-full flex items-center justify-center font-bold">${countInCart}</span>` : ''}
                        </div>
                        <div>
                            <h4 class="font-bold text-xs text-gray-800">${p.name}</h4>
                            <p class="text-[10px] text-gray-400">المتفر: ${p.qty} | السعر: ${p.price.toLocaleString()} د.ع</p>
                        </div>
                        <button onclick="addToCart(${p.id})" class="w-full bg-purpleLight text-purpleBrand py-1.5 rounded-xl text-xs font-bold hover:bg-purpleBrand hover:text-white transition active:scale-95">
                            + إضافة
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
                    if(cartItem.cartQty < item.qty) {
                        cartItem.cartQty++;
                    } else {
                        alert('وصلت للحد الأقصى للكمية المتوفرة بالمعرض!');
                    }
                } else {
                    cart.push({ ...item, cartQty: 1 });
                }
                updateCartBadge();
                renderProductsGrid();
            } else {
                alert('هذه المادة نفدت من المخزن!');
            }
        }

        function updateCartBadge() {
            let totalCount = cart.reduce((acc, i) => acc + i.cartQty, 0);
            document.getElementById('cart-badge').innerText = totalCount;
        }

        function openCartView() {
            let custSelect = document.getElementById('cart-customer-select');
            custSelect.innerHTML = '<option value="">-- اختر العميل --</option>';
            
            customers.forEach((cust, index) => {
                custSelect.innerHTML += `<option value="${index}">${cust.name}</option>`;
            });

            // Render Selected Items
            let container = document.getElementById('cart-items-container');
            container.innerHTML = '';
            
            if(cart.length === 0) {
                container.innerHTML = `<div class="text-center text-gray-400 text-xs py-2">لا توجد مواد مضافة بالسلة</div>`;
            } else {
                cart.forEach(c => {
                    container.innerHTML += `
                        <div class="flex justify-between items-center bg-gray-50 p-2 rounded-xl text-xs">
                            <span>${c.name} (عدد: ${c.cartQty})</span>
                            <span class="font-bold text-purpleBrand">${(c.price * c.cartQty).toLocaleString()} د.ع</span>
                        </div>
                    `;
                });
            }

            let totalPrice = cart.reduce((acc, i) => acc + (i.price * i.cartQty), 0);
            document.getElementById('cart-total-price').innerText = totalPrice.toLocaleString() + ' د.ع';

            switchTab('cart');
        }

        // Auto-fill Customer Info Function
        function autoFillCustomerData() {
            let idx = document.getElementById('cart-customer-select').value;
            if(idx !== "") {
                let cust = customers[idx];
                document.getElementById('cust-phone-filled').value = cust.phone || "غير محدد";
                document.getElementById('cust-address-filled').value = cust.address || "غير محدد";
            } else {
                document.getElementById('cust-phone-filled').value = "";
                document.getElementById('cust-address-filled').value = "";
            }
        }

        function finalizeSale() {
            if(cart.length === 0) {
                alert('السلة فارغة! أضف مواد أولاً.');
                return;
            }

            cart.forEach(cItem => {
                let original = products.find(p => p.id === cItem.id);
                if(original) original.qty -= cItem.cartQty;
            });

            let sum = cart.reduce((acc, i) => acc + (i.price * i.cartQty), 0);
            totalSales += sum;

            invoicesHistory.push({
                id: Date.now(),
                date: new Date().toLocaleTimeString('ar-IQ'),
                total: sum,
                itemsCount: cart.length
            });

            cart = [];
            updateCartBadge();
            saveData();
            renderProductsGrid();
            renderInventory();
            renderInvoicesHistory();
            switchTab('dashboard');
            alert('تمت عملية البيع وطباعة الفاتورة بنجاح!');
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
                document.getElementById('p-name').value = '';
                document.getElementById('p-price').value = '';
                document.getElementById('p-qty').value = '';
                toggleAddProductForm();
            } else {
                alert('يرجى ملء جميع معلومات المادة.');
            }
        }

        function renderInventory() {
            let inv = document.getElementById('inventory-list');
            inv.innerHTML = '';
            if(products.length === 0) {
                inv.innerHTML = `<div class="text-center text-gray-400 text-xs py-2">المخزن فارغ حالياً.</div>`;
                return;
            }
            products.forEach(p => {
                inv.innerHTML += `
                    <div class="flex justify-between items-center bg-gray-50 p-2.5 rounded-xl text-xs">
                        <span class="font-bold text-gray-800">${p.name}</span>
                        <span class="font-bold text-purpleBrand">${p.price.toLocaleString()} د.ع | المتبقي: ${p.qty}</span>
                    </div>
                `;
            });
        }

        function saveCustomer() {
            let name = document.getElementById('c-name').value;
            let phone = document.getElementById('c-phone').value;
            let address = document.getElementById('c-address').value;

            if(name) {
                customers.push({ id: Date.now(), name, phone, address });
                saveData();
                renderCustomers();
                document.getElementById('c-name').value = '';
                document.getElementById('c-phone').value = '';
                document.getElementById('c-address').value = '';
                alert('تم حفظ العميل بنجاح.');
            }
        }

        function renderCustomers() {
            let list = document.getElementById('customers-list');
            list.innerHTML = '';
            if(customers.length === 0) {
                list.innerHTML = `<div class="text-center text-gray-400 text-xs py-2">لا يوجد عملاء مضافين.</div>`;
                return;
            }
            customers.forEach(c => {
                list.innerHTML += `
                    <div class="flex justify-between items-center bg-gray-50 p-2.5 rounded-xl text-xs">
                        <div>
                            <p class="font-bold text-gray-800">${c.name}</p>
                            <p class="text-[10px] text-gray-400">${c.phone} - ${c.address}</p>
                        </div>
                    </div>
                `;
            });
        }

        function renderInvoicesHistory() {
            let div = document.getElementById('invoices-history-list');
            div.innerHTML = '';
            invoicesHistory.forEach(inv => {
                div.innerHTML += `
                    <div class="flex justify-between items-center bg-purple-50/50 p-2.5 rounded-xl border border-purple-100">
                        <span>فاتورة #${inv.id.toString().slice(-4)} (${inv.date})</span>
                        <span class="font-bold text-purpleBrand">${inv.total.toLocaleString()} د.ع</span>
                    </div>
                `;
            });
        }

        function saveData() {
            localStorage.setItem('yasser_zero_products', JSON.stringify(products));
            localStorage.setItem('yasser_zero_customers', JSON.stringify(customers));
            localStorage.setItem('yasser_zero_invoices', JSON.stringify(invoicesHistory));
            localStorage.setItem('yasser_zero_sales', totalSales);
            document.getElementById('stats-total').innerText = totalSales.toLocaleString() + ' د.ع';
        }

        function init() {
            if(localStorage.getItem('yw_auth_logged') === '1') {
                document.getElementById('login-modal').classList.add('hidden');
            }
            renderProductsGrid();
            renderInventory();
            renderCustomers();
            renderInvoicesHistory();
            saveData();
        }

        init();
    </script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=True)
