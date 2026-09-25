import streamlit as st
import pandas as pd
import datetime
import json
import urllib.parse
import barcode
from barcode.writer import ImageWriter
import io

st.set_page_config(page_title="نظام ياسر ويب - الإدارة المتكاملة", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    input, select, textarea {
        direction: rtl;
        text-align: right;
    }
    /* تنسيق الإطارات الذهبية الفخمة للدليل */
    .gold-frame-container {
        border: 3px solid #FFD700;
        border-radius: 15px;
        padding: 25px;
        background: linear-gradient(135deg, #fffcf0 0%, #fff8e1 100%);
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        margin-bottom: 25px;
    }
    .gold-tab-box {
        border: 2px solid #DAA520;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(218, 165, 32, 0.15);
    }
    </style>
    
    <!-- محرك أصوات البيب التفاعلي -->
    <script>
    function playBeepSound() {
        try {
            var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            var oscillator = audioCtx.createOscillator();
            var gainNode = audioCtx.createGain();
            
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(880, audioCtx.currentTime);
            gainNode.gain.setValueAtTime(0.15, audioCtx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.15);
            
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + 0.15);
        } catch(e) {
            console.log("Audio not allowed yet");
        }
    }
    </script>
""", unsafe_allow_html=True)

def trigger_beep():
    if st.session_state.get("enable_audio", False):
        st.components.v1.html("""
            <script>
                if (typeof playBeepSound === 'function') {
                    playBeepSound();
                }
            </script>
        """, height=0)

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "user_role" not in st.session_state:
    st.session_state.user_role = "مدير عام"

if "enable_audio" not in st.session_state:
    st.session_state.enable_audio = True

if "suppliers_list" not in st.session_state or isinstance(st.session_state.suppliers_list, pd.DataFrame):
    st.session_state.suppliers_list = []

if "cart" not in st.session_state or isinstance(st.session_state.cart, pd.DataFrame):
    st.session_state.cart = []

if "expenses_list" not in st.session_state or isinstance(st.session_state.expenses_list, pd.DataFrame):
    st.session_state.expenses_list = []

if "audit_logs" not in st.session_state or isinstance(st.session_state.audit_logs, pd.DataFrame):
    st.session_state.audit_logs = []

if "memory_customers" not in st.session_state:
    st.session_state.memory_customers = []

if "memory_products" not in st.session_state:
    st.session_state.memory_products = []

if "memory_invoices" not in st.session_state:
    st.session_state.memory_invoices = []

if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None

def log_audit(action, details):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = st.session_state.logged_in_user or "زائر"
    role = st.session_state.user_role
    if isinstance(st.session_state.audit_logs, pd.DataFrame):
        st.session_state.audit_logs = []
    st.session_state.audit_logs.insert(0, {
        "التاريخ والوقت": str(timestamp),
        "المستخدم": str(user),
        "الصلاحية": str(role),
        "العملية": str(action),
        "التفاصيل": str(details)
    })

def generate_html_invoice(inv):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {inv['invoice_code']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #ccc; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); background: #fff; border-radius: 8px; }}
            .header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ margin-bottom: 20px; font-size: 15px; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: right; font-size: 14px; }}
            th {{ background-color: #f8f9fa; color: #2c3e50; }}
            .totals {{ font-size: 16px; font-weight: bold; text-align: left; margin-top: 15px; line-height: 1.8; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 13px; color: #666; border-top: 1px dashed #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <h2>نظام ياسر ويب - فاتورة بيع رسمية</h2>
                <p>تاريخ الإصدار: {inv['created_date']}</p>
            </div>
            <div class="info">
                <p><strong>رقم الفاتورة:</strong> {inv['invoice_code']}</p>
                <p><strong>اسم العميل / المحل:</strong> {inv['customer_name']}</p>
                <p><strong>حالة وطريقة الدفع:</strong> {inv['payment_type']}</p>
            </div>
            <table>
                <tr>
                    <th>تفاصيل المنتجات والمواد المطلوبة</th>
                </tr>
                <tr>
                    <td>{inv['products_text']}</td>
                </tr>
            </table>
            <div class="totals">
                <p>المبلغ الإجمالي: {int(inv['total_price']):,} دينار عراقي</p>
                <p>المبلغ الواصل: {int(inv['paid_amount']):,} دينار عراقي</p>
                <p>المتبقي (الدين): {int(inv['remaining_amount']):,} دينار عراقي</p>
            </div>
            <div class="footer">
                <p>شكراً لتعاملكم معنا - جميع الحقوق محفوظة</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def generate_html_receipt(rec):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>سند قبض - {rec['customer_name']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; }}
            .receipt-box {{ max-width: 600px; margin: auto; padding: 30px; border: 2px dashed #2c3e50; background: #fff; border-radius: 8px; }}
            .header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ font-size: 16px; line-height: 2.0; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 14px; border-top: 1px solid #ddd; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="receipt-box">
            <div class="header">
                <h2>نظام ياسر ويب - سند قبض نقدي رسمي</h2>
                <p>التاريخ والوقت: {rec['date']}</p>
            </div>
            <div class="info">
                <p><strong>اسم العميل:</strong> {rec['customer_name']}</p>
                <p><strong>المبلغ المستلم:</strong> {int(rec['amount']):,} دينار عراقي</p>
                <p><strong>البيان:</strong> استلمنا من السيد المذكور أعلاه المبلغ وتثبيته كدفعة تسديد لحسابه الجاري.</p>
            </div>
            <div class="footer">
                <p>توقيع أمين الصندوق / الإدارة: ........................</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

if not st.session_state.logged_in_user:
    st.title("🔐 بوابة تسجيل الدخول لنظام ياسر ويب")
    with st.form("login_form"):
        login_user = st.text_input("اسم المستخدم أو اسم المحل:")
        login_role = st.selectbox("اختر الصلاحية:", ["مدير عام", "مشرف مبيعات", "كاشير رئيسي"])
        login_submitted = st.form_submit_button("دخول للنظام", type="primary")
        
        if login_submitted:
            if login_user.strip():
                st.session_state.logged_in_user = str(login_user.strip())
                st.session_state.user_role = str(login_role)
                log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {login_user.strip()} بصلاحية {login_role}")
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى إدخال اسم المستخدم.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

st.sidebar.title("🛍️ نظام ياسر ويب")
st.sidebar.write(f"👤 المستخدم: **{username}**")
st.sidebar.write(f"📌 الصلاحية: **{user_role}**")
st.sidebar.divider()

audio_toggle = st.sidebar.checkbox("🔊 تفعيل أصوات البيب التفاعلية", value=st.session_state.enable_audio)
if audio_toggle != st.session_state.enable_audio:
    st.session_state.enable_audio = audio_toggle
    trigger_beep()

st.sidebar.divider()

cart_count_badge = sum(int(item['qty']) for item in st.session_state.cart)
st.sidebar.info(f"🛒 المنتجات بالسلة: **{cart_count_badge}**")
st.sidebar.divider()

st.sidebar.subheader("📂 القائمة الرئيسية")
menu_options = ["نقطة البيع (POS)", "المخزن وجرد البضائع", "إضافة مادة جديدة", "توليد الباركود", "العملاء والديون", "سندات القبض", "الموردين", "سجل الفواتير", "صندوق الوردية والمصروفات"]

if user_role in ["مدير عام", "مشرف مبيعات"]:
    menu_options.extend(["تقارير الأرباح", "سجل النشاطات الرقابي", "الدليل وشرح الاستخدام"])
else:
    menu_options.append("الدليل وشرح الاستخدام")

selected_menu = st.sidebar.radio("اختر القسم المطلوب:", menu_options)

st.sidebar.divider()
st.sidebar.subheader("🔄 النسخ الاحتياطي")
backup_data = {
    "username": str(username),
    "customers": st.session_state.memory_customers,
    "suppliers": list(st.session_state.suppliers_list),
    "invoices": st.session_state.memory_invoices,
    "expenses": list(st.session_state.expenses_list),
    "audit_logs": list(st.session_state.audit_logs),
    "export_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
}
backup_json = json.dumps(backup_data, ensure_ascii=False, indent=4, default=str)
st.sidebar.download_button(
    label="📥 تحميل نسخة احتياطية",
    data=backup_json,
    file_name=f"yasser_web_backup_{username}.json",
    mime="application/json"
)

if st.sidebar.button("تسجيل الخروج"):
    log_audit("تسجيل خروج", f"تم تسجيل الخروج للمستخدم {username}")
    st.session_state.logged_in_user = None
    st.session_state.cart = []
    st.rerun()

if selected_menu == "نقطة البيع (POS)":
    st.subheader("🛒 نقطة البيع السريعة وإتمام الفاتورة")
    if st.session_state.cart:
        total_cart_price = 0.0
        for idx, c_item in enumerate(st.session_state.cart):
            cols_cart = st.columns([3, 2, 2, 1])
            with cols_cart[0]:
                st.write(f"**{c_item['product_name']}** ({c_item['color']} / {c_item['size']})")
            with cols_cart[1]:
                new_q = st.number_input(f"الكمية", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_q_{c_item['id']}")
                c_item['qty'] = new_q
            with cols_cart[2]:
                item_total = float(c_item['sell_price']) * float(c_item['qty'])
                total_cart_price += item_total
                st.write(f"المجموع: **{int(item_total):,}** د.ع")
            with cols_cart[3]:
                if st.button("❌", key=f"del_cart_{c_item['id']}"):
                    st.session_state.cart.pop(idx)
                    trigger_beep()
                    st.rerun()
                
        st.divider()
        st.markdown(f"### 💵 المجموع الكلي المطلوب: **{int(total_cart_price):,} د.ع**")
        
        cust_names_list = [c["customer_name"] for c in st.session_state.memory_customers]
        if not cust_names_list:
            st.warning("⚠️ تنبيه: يرجى إضافة عميل من قسم (العملاء والديون) أولاً لتتمكن من إصدار الفاتورة باسمه!")
            selected_customer_name = ""
        else:
            selected_customer_name = st.selectbox("اختر اسم العميل المرتبط بالفاتورة:", cust_names_list)
        
        paid_input_str = st.text_input("المبلغ المدفوع حالياً (د.ع - اكتب 0 إذا كانت آجلة بالكامل):", value="0")
        try:
            paid_amount = float(paid_input_str.strip() if paid_input_str.strip() else "0")
            if paid_amount < 0: paid_amount = 0.0
            if paid_amount > total_cart_price: paid_amount = float(total_cart_price)
        except ValueError:
            paid_amount = 0.0
            
        remaining_amount = float(total_cart_price) - float(paid_amount)
        if paid_amount >= total_cart_price:
            auto_pay_type = "🟢 نقد بالكامل (كاش)"
        elif paid_amount == 0.0:
            auto_pay_type = "🔴 دين كامل (آجل)"
        else:
            auto_pay_type = "🔵 دفعة جزئية (أقساط)"

        st.info(f"حالة الدفع: {auto_pay_type} | الواصل بالصندوق: {int(paid_amount):,} د.ع | المتبقي الذمي: {int(remaining_amount):,} د.ع")

        if st.button("💾 إتمام البيع وحفظ الفاتورة رسمياً", type="primary"):
            if not selected_customer_name:
                st.error("❌ يرجى اختيار عميل مسجل لإتمام الفاتورة.")
            else:
                try:
                    prod_names_str = []
                    total_buy_cost_of_invoice = 0.0
                    for c_item in st.session_state.cart:
                        prod_names_str.append(f"{c_item['product_name']} ({c_item['color']}) [العدد: {c_item['qty']}]")
                        total_buy_cost_of_invoice += (float(c_item['buy_price']) * float(c_item['qty']))
                        for p_item in st.session_state.memory_products:
                            if p_item["id"] == c_item["id"]:
                                p_item["quantity"] = max(0, int(p_item["quantity"]) - int(c_item['qty']))
                    
                    inv_id = len(st.session_state.memory_invoices) + 1
                    inv_code = f"INV-{inv_id:03d}"
                    st.session_state.memory_invoices.insert(0, {
                        "id": inv_id,
                        "username": str(username),
                        "invoice_code": str(inv_code),
                        "customer_name": str(selected_customer_name),
                        "products_text": str(" ، ".join(prod_names_str)),
                        "total_price": float(total_cart_price),
                        "cost_price": float(total_buy_cost_of_invoice),
                        "paid_amount": float(paid_amount),
                        "remaining_amount": float(remaining_amount),
                        "payment_type": str(auto_pay_type),
                        "created_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    })
                    log_audit("إتمام بيع", f"فاتورة جديدة {inv_code} للعميل {selected_customer_name}")
                    st.session_state.cart = []
                    trigger_beep()
                    st.success("✅ تمت عملية البيع وحفظ الفاتورة بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ أثناء الحفظ: {e}")
    else:
        st.info("🛒 سلة المبيعات فارغة. توجه للمخزن لإضافة مواد.")

elif selected_menu == "المخزن وجرد البضائع":
    st.subheader("📦 إدارة المخزن وجرد البضائع")
    search_prod_term = st.text_input("🔍 بحث عن مادة في المخزن:", "")
    all_products = st.session_state.memory_products
    if all_products:
        filtered_products = all_products
        if search_prod_term:
            filtered_products = [p for p in filtered_products if search_prod_term.lower() in p['product_name'].lower() or search_prod_term.lower() in p.get('barcode','').lower()]

        cols = st.columns(3)
        for idx, item in enumerate(filtered_products):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### 📦 {item['product_name']}")
                    st.markdown(f"🎨 **اللون:** `{item.get('color', 'عام')}` | 📏 **القياس:** `{item.get('size', 'عام')}`")
                    st.markdown(f"🏷️ **الباركود:** `{item.get('barcode', 'بدون')}`")
                    st.markdown(f"💰 **الشراء:** `{int(item['buy_price']):,}` | **البيع:** `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🔢 **الكمية المتاحة:** `{int(item['quantity'])}` قطعة")

                    if item['quantity'] > 0:
                        if st.button(f"🛒 إضافة للسلة", key=f"add_cart_{item['id']}"):
                            found = False
                            for ci in st.session_state.cart:
                                if ci["id"] == item["id"]:
                                    if ci["qty"] < item["quantity"]:
                                        ci["qty"] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({
                                    "id": item["id"],
                                    "product_name": item["product_name"],
                                    "color": item.get('color', ''),
                                    "size": item.get('size', ''),
                                    "sell_price": item["sell_price"],
                                    "buy_price": item["buy_price"],
                                    "max_qty": item["quantity"],
                                    "qty": 1
                                })
                            trigger_beep()
                            st.toast("تمت الإضافة للسلة بنجاح!", icon="🛒")
                            st.rerun()
                    else:
                        st.warning("⚠️ الكمية نافذة")
    else:
        st.info("المخزن فارغ. قم بإضافة بضائع من قسم (إضافة مادة جديدة).")

elif selected_menu == "إضافة مادة جديدة":
    st.subheader("➕ إضافة مادة أو جهاز جديد للمخزن")
    with st.form("add_product_form", clear_on_submit=True):
        p_name = st.text_input("اسم المادة / المنتج *:")
        c_col, c_sz = st.columns(2)
        with c_col:
            p_color = st.text_input("اللون / المواصفات:", "عام")
        with c_sz:
            p_size = st.text_input("القياس / السعة:", "عام")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p_buy_str = st.text_input("سعر الشراء (د.ع):", "0")
        with c2:
            p_sell_str = st.text_input("سعر البيع (د.ع):", "0")
        with c3:
            p_qty_str = st.text_input("الكمية:", "1")
        with c4:
            p_barcode = st.text_input("رمز الباركود:", "")
        
        submitted = st.form_submit_button("حفظ المادة بالنظام", type="primary")
        if submitted:
            if p_name.strip():
                try:
                    p_buy = float(p_buy_str.strip())
                    p_sell = float(p_sell_str.strip())
                    p_qty = int(p_qty_str.strip())
                    new_prod_id = len(st.session_state.memory_products) + 1
                    generated_bc = str(p_barcode.strip() if p_barcode else f"PRD{new_prod_id:04d}")
                    
                    st.session_state.memory_products.append({
                        "id": new_prod_id,
                        "username": str(username),
                        "product_name": str(p_name.strip()),
                        "color": str(p_color.strip() if p_color else "عام"),
                        "size": str(p_size.strip() if p_size else "عام"),
                        "buy_price": float(p_buy),
                        "sell_price": float(p_sell),
                        "quantity": int(p_qty),
                        "barcode": generated_bc
                    })
                    log_audit("إضافة منتج", f"تمت إضافة المنتج {p_name.strip()}")
                    trigger_beep()
                    st.success(f"تمت إضافة المادة ({p_name}) بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("❌ يرجى إدخال قيم رقمية صحيحة بالأسعار والكميات.")
            else:
                st.warning("يرجى كتابة اسم المادة.")

elif selected_menu == "توليد الباركود":
    st.subheader("🏷️ توليد وطباعة باركود المواد")
    all_products_bc = st.session_state.memory_products
    if all_products_bc:
        for item in all_products_bc:
            with st.container(border=True):
                st.markdown(f"### 📦 المادة: {item['product_name']}")
                b_code_val = item.get('barcode', f"PRD{item['id']}")
                try:
                    rv = barcode.get('code128', str(b_code_val), writer=ImageWriter())
                    buffer_bc = io.BytesIO()
                    rv.write(buffer_bc)
                    st.image(buffer_bc.getvalue(), caption=f"باركود: {b_code_val}", width=230)
                except Exception as ex:
                    st.error(f"تعذر توليد الباركود: {ex}")
    else:
        st.info("لا توجد مواد مسجلة لتوليد الباركود.")

elif selected_menu == "العملاء والديون":
    st.subheader("👥 إدارة العملاء والديون المترتبة")
    with st.form("add_cust_form", clear_on_submit=True):
        c_name = st.text_input("اسم الزبون أو المحل *:")
        c_phone = st.text_input("رقم الهاتف (واتساب) *:")
        c_address = st.text_input("العنوان (مثال: البصرة):", "البصرة")
        if st.form_submit_button("حفظ العميل"):
            if c_name.strip() and c_phone.strip():
                st.session_state.memory_customers.append({
                    "customer_name": str(c_name.strip()),
                    "phone": str(c_phone.strip()),
                    "address": str(c_address.strip()),
                    "notes": ""
                })
                log_audit("إضافة عميل", f"تم تسجيل العميل {c_name}")
                trigger_beep()
                st.success("تم تسجيل العميل بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى إدخال الاسم ورقم الهاتف.")

    st.divider()
    if st.session_state.memory_customers:
        cust_display_data = []
        for cust in st.session_state.memory_customers:
            c_invs = [inv for inv in st.session_state.memory_invoices if inv['customer_name'] == cust['customer_name']]
            c_total_debt = sum(float(inv.get('remaining_amount', 0)) for inv in c_invs)
            cust_display_data.append({
                "اسم الزبون": cust['customer_name'],
                "رقم الهاتف": cust['phone'],
                "العنوان": cust['address'],
                "إجمالي الديون (د.ع)": int(c_total_debt)
            })
        st.dataframe(pd.DataFrame(cust_display_data), use_container_width=True)
    else:
        st.info("لا يوجد عملاء مسجلين.")

elif selected_menu == "سندات القبض":
    st.subheader("💵 نظام سداد الديون وإصدار سندات القبض")
    debt_cust_list = [c["customer_name"] for c in st.session_state.memory_customers]
    if not debt_cust_list:
        st.info("لا توجد عملاء مسجلين لإدارة ديونهم.")
    else:
        selected_debt_customer = st.selectbox("اختر اسم العميل:", debt_cust_list)
        customer_invoices = [inv for inv in st.session_state.memory_invoices if inv['customer_name'] == selected_debt_customer]
        total_customer_debt = sum(float(inv.get('remaining_amount', 0)) for inv in customer_invoices)
        st.markdown(f"### الدين المتبقي على العميل: **{int(total_customer_debt):,} د.ع**")
        
        with st.form("pay_debt_form"):
            payment_input_str = st.text_input("المبلغ المسدد نقداً (د.ع):", "0")
            if st.form_submit_button("إتمام التسديد وتوليد السند", type="primary"):
                try:
                    payment_val = float(payment_input_str.strip() if payment_input_str.strip() else "0")
                    if payment_val > total_customer_debt:
                        st.error("المبلغ المدخل أكبر من إجمالي الديون المطلوبة!")
                    else:
                        remaining_payment = payment_val
                        for cinv in customer_invoices:
                            if remaining_payment <= 0: break
                            curr_rem = float(cinv.get('remaining_amount', 0))
                            if curr_rem > 0:
                                if remaining_payment >= curr_rem:
                                    new_paid = float(cinv['total_price'])
                                    new_rem = 0.0
                                    new_type = "🟢 تسديد نقدي تام"
                                    remaining_payment -= curr_rem
                                else:
                                    new_paid = float(cinv['paid_amount']) + remaining_payment
                                    new_rem = curr_rem - remaining_payment
                                    new_type = "🔵 تسديد جزئي"
                                    remaining_payment = 0.0
                                cinv['paid_amount'] = float(new_paid)
                                cinv['remaining_amount'] = float(new_rem)
                                cinv['payment_type'] = str(new_type)
                        
                        st.session_state.last_receipt = {
                            "customer_name": str(selected_debt_customer),
                            "amount": float(payment_val),
                            "date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                        }
                        log_audit("سداد ديون", f"تسديد مبلغ {payment_val:,} للعميل {selected_debt_customer}")
                        trigger_beep()
                        st.success("تم استلام المبلغ وتحديث الحساب بنجاح!")
                        st.rerun()
                except ValueError:
                    st.error("يرجى إدخال رقم صحيح.")

        if st.session_state.get('last_receipt'):
            rec = st.session_state.last_receipt
            st.divider()
            with st.container(border=True):
                st.write(f"👤 **العميل:** {rec['customer_name']} | 💵 **المبلغ:** **{int(rec['amount']):,} د.ع**")
                html_rec_data = generate_html_receipt(rec)
                st.download_button("🖨️ تحميل سند القبض (HTML)", data=html_rec_data, file_name=f"receipt_{rec['customer_name']}.html", mime="text/html")

elif selected_menu == "الموردين":
    st.subheader("🏭 إدارة الموردين")
    with st.form("add_supplier_form", clear_on_submit=True):
        sup_name = st.text_input("اسم المورد / الشركة:")
        sup_phone = st.text_input("رقم الهاتف:")
        if st.form_submit_button("إضافة المورد"):
            if sup_name.strip():
                st.session_state.suppliers_list.append({"اسم المورد": sup_name, "رقم الهاتف": sup_phone})
                trigger_beep()
                st.success("تم إضافة المورد بنجاح!")
                st.rerun()
            else:
                st.warning("أدخل اسم المورد.")
    if st.session_state.suppliers_list:
        st.dataframe(pd.DataFrame(st.session_state.suppliers_list), use_container_width=True)
    else:
        st.info("لا يوجد موردين.")

elif selected_menu == "سجل الفواتير":
    st.subheader("📄 سجل الفواتير والمشاركة عبر واتساب")
    invoices_list = st.session_state.memory_invoices
    if invoices_list:
        for inv in invoices_list:
            with st.expander(f"فاتورة: {inv['invoice_code']} | الزبون: {inv['customer_name']} | المجموع: {int(inv['total_price']):,} د.ع"):
                st.write(f"📅 التاريخ: {inv['created_date']}")
                st.write(f"🛍️ المنتجات: {inv['products_text']}")
                st.write(f"💵 المجموع: {int(inv['total_price']):,} | الواصل: {int(inv['paid_amount']):,} | المتبقي: `{int(inv['remaining_amount']):,}` د.ع")
                
                html_inv = generate_html_invoice(inv)
                st.download_button("📥 تحميل الفاتورة الرسمية (HTML)", data=html_inv, file_name=f"invoice_{inv['invoice_code']}.html", mime="text/html", key=f"dl_{inv['id']}")

                cust_ph = ""
                for c in st.session_state.memory_customers:
                    if c["customer_name"] == inv['customer_name']:
                        cust_ph = c["phone"]
                        break
                if cust_ph:
                    wa_msg = f"مرحباً أستاذ {inv['customer_name']}\nإليك تفاصيل فاتورتك برقم {inv['invoice_code']}:\nالمبلغ الإجمالي: {int(inv['total_price']):,} د.ع\nالمتبقي الذمي: {int(inv['remaining_amount']):,} د.ع"
                    encoded_msg = urllib.parse.quote(wa_msg)
                    st.markdown(f"📱 [إرسال الفاتورة للعميل عبر واتساب](https://wa.me/{cust_ph}?text={encoded_msg})", unsafe_allow_html=True)
    else:
        st.info("لا توجد فواتير مسجلة.")

elif selected_menu == "صندوق الوردية والمصروفات":
    st.subheader("💰 صندوق الوردية والمصروفات النقدية")
    with st.form("add_expense_form", clear_on_submit=True):
        exp_title = st.text_input("بيان المصروف (مثال: أجور نقل، صيانة، إيجار):")
        exp_amount_str = st.text_input("المبلغ (د.ع):", "0")
        if st.form_submit_button("تسجيل المصروف", type="primary"):
            if exp_title.strip():
                try:
                    exp_val = float(exp_amount_str.strip())
                    st.session_state.expenses_list.insert(0, {"البيان": exp_title, "المبلغ": exp_val, "التاريخ": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})
                    log_audit("تسجيل مصروف", f"مصروف {exp_title} بقيمة {exp_val}")
                    trigger_beep()
                    st.success("تم تسجيل المصروف!")
                    st.rerun()
                except ValueError:
                    st.error("أدخل مبلغ صحيح.")
            else:
                st.warning("أدخل بيان المصروف.")

    total_sales_cash = sum(float(inv.get('paid_amount', 0)) for inv in st.session_state.memory_invoices)
    total_expenses = sum(float(ex.get('المبلغ', 0)) for ex in st.session_state.expenses_list)
    net_box = total_sales_cash - total_expenses

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.metric("الواصل النقدي بالصندوق", f"{int(total_sales_cash):,} د.ع")
    with col_b2:
        st.metric("المصروفات المسجلة", f"{int(total_expenses):,} د.ع")
    with col_b3:
        st.metric("صافي رصيد الصندوق", f"{int(net_box):,} د.ع")

    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)

elif selected_menu == "تقارير الأرباح":
    if user_role not in ["مدير عام", "مشرف مبيعات"]:
        st.error("⛔ عذراً، ليس لديك صلاحية الوصول إلى تقارير الأرباح (خاص بالمدير والمشرف فقط).")
    else:
        st.subheader("📊 تقارير الأرباح وتحليلات المبيعات العامة")
        invoices_report = st.session_state.memory_invoices
        total_revenue = sum(float(inv['total_price']) for inv in invoices_report)
        total_cost = sum(float(inv.get('cost_price', 0)) for inv in invoices_report)
        total_net_profit = total_revenue - total_cost
        total_debts = sum(float(inv.get('remaining_amount', 0)) for inv in invoices_report)

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("إجمالي المبيعات", f"{int(total_revenue):,} د.ع")
        with col_r2:
            st.metric("صافي أرباح البضائع", f"{int(total_net_profit):,} د.ع")
        with col_r3:
            st.metric("إجمالي الديون المعلقة", f"{int(total_debts):,} د.ع")

        if invoices_report:
            df_inv_report = pd.DataFrame(invoices_report)
            st.bar_chart(df_inv_report, x="invoice_code", y="total_price")
        else:
            st.info("لا توجد بيانات كافية للرسم البياني.")

elif selected_menu == "سجل النشاطات الرقابي":
    if user_role not in ["مدير عام", "مشرف مبيعات"]:
        st.error("⛔ عذراً، هذا القسم مخصص لمدير النظام والمشرفين فقط.")
    else:
        st.subheader("📜 سجل النشاطات والعمليات الرقابي")
        if st.session_state.audit_logs:
            st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
        else:
            st.info("لا توجد نشاطات مسجلة.")

elif selected_menu == "الدليل وشرح الاستخدام":
    # الدليل الشامل والمفصل مع الإطار الذهبي وتنسيق حساب الانستغرام الفخم
    st.markdown("""
    <div class="gold-frame-container">
        <h2 style="text-align: center; color: #b8860b; margin-bottom: 20px;">📖 الدليل الشامل وشرح مميزات نظام ياسر ويب المتقدم</h2>
        <p style="text-align: center; font-size: 16px; color: #444; margin-bottom: 25px;">
            أهلاً بك في الدليل الرسمي للنظام. تم تصميم هذا المرشد خصيصاً لمساعدتك على استثمار كافة إمكانيات <b>نظام ياسر ويب - الإدارة المتكاملة</b> بكفاءة واحترافية عالية.
        </p>
        
        <div class="gold-tab-box">
            <h4 style="color: #8b6508;">🛒 1. نقطة البيع السريعة (POS) وإتمام الفاتورة</h4>
            <p>قسم مخصص لتجميع المواد المختارة من المخزن في سلة المبيعات مع إمكانية تعديل الكميات أو حذفها بضغطة زر. يقوم النظام بحساب المجاميع تلقائياً، والتعرف على اسم العميل، وتحديد نوع الدفع (نقدي تام، دين آجل، أو دفعة جزئية) مع إمكانية إصدار وحفظ الفاتورة رسمياً.</p>
        </div>

        <div class="gold-tab-box">
            <h4 style="color: #8b6508;">📦 2. إدارة المخزن وجرد البضائع</h4>
            <p>نافذة عرض تفصيلية لجميع المواد والأجهزة المسجلة في المخزن مع بيان الألوان، القياسات، الباركود، أسعار الشراء والبيع، والكميات المتوفرة. يتضمن محرك بحث سريع وفوري للعثور على أي مادة بلحظات.</p>
        </div>

        <div class="gold-tab-box">
            <h4 style="color: #8b6508;">➕ 3. إضافة مادة جديدة وتوليد الباركود</h4>
            <p>تتيح لك إدخال بضائع جديدة للمخزن وتحديد أسعار الشراء والبيع والكميات بدقة. كما يضم النظام قسماً خاصاً لتوليد وطباعة رموز الباركود لكل مادة بصيغة Code128 المعيارية.</p>
        </div>

        <div class="gold-tab-box">
            <h4 style="color: #8b6508;">👥 4. العملاء والديون وسندات القبض</h4>
            <p>لتسجيل بيانات الزبائن ومعلومات التواصل الخاصة بهم ومتابعة حركة الديون المرتبطة بفواتيرهم. يتيح نظام سندات القبض إدخال الدفعات النقدية المسددة وتحديث رصيد العميل وتوليد سند قبض رسمي بصيغة HTML.</p>
        </div>

        <div class="gold-tab-box">
            <h4 style="color: #8b6508;">💰 5. صندوق الوردية والمصروفات النقدية</h4>
            <p>مخصص لتسجيل النثريات والمصروفات اليومية (مثل أجور النقل، الصيانة، والإيجار) لحساب صافي رصيد الصندوق النقدي الفعلي بدقة ومقارنته مع إجمالي المقبوضات.</p>
        </div>

        <div class="gold-tab-box">
            <h4 style="color: #8b6508;">📊 6. تقارير الأرباح والسجل الرقابي</h4>
            <p>أقسام استراتيجية مخصصة لمدير النظام والمشرفين تعرض تحليلات مالية دقيقة لإجمالي المبيعات، صافي أرباح البضائع، الديون المعلقة، بالإضافة إلى سجل رقابي متكامل يوثق جميع عمليات المستخدمين بدقة.</p>
        </div>

        <div style="text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px dashed #DAA520;">
            <p style="font-size: 15px; color: #555; font-weight: bold;">
                ✨ تصميم وبرمجة: <b>نظام ياسر ويب</b> | جميع الحقوق محفوظة للإدارة المتكاملة 2026
            </p>
            <p style="font-size: 14px; color: #b8860b; margin-top: 5px;">
                📸 تابعنا على منصة انستغرام لمزيد من التحديثات والدعم الفني: <b>@yasser_web</b>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
