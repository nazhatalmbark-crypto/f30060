import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from supabase import create_client, Client
import datetime
import json
import urllib.parse
import barcode
from barcode.writer import ImageWriter
import io

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co"
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web POS", layout="wide")

# **تنسيق التصميم البنفسجي الحديث وواجهة الموبايل**
st.markdown("""
    <style>
    .stApp {
        background-color: #553c9a;
        direction: rtl;
        text-align: right;
        font-family: system-ui, -apple-system, sans-serif;
    }
    input, select, textarea {
        direction: rtl;
        text-align: right;
    }
    .hide-scroll::-webkit-scrollbar { display: none; }
    </style>
""", unsafe_allow_html=True)

# **جلسات النظام الأساسية والذاكرة المحلية البديلة (Fallback)**
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "مشرف النظام"
if "suppliers_list" not in st.session_state:
    st.session_state.suppliers_list = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "expenses_list" not in st.session_state:
    st.session_state.expenses_list = []
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []
if "local_products" not in st.session_state:
    st.session_state.local_products = []
if "local_customers" not in st.session_state:
    st.session_state.local_customers = []
if "local_invoices" not in st.session_state:
    st.session_state.local_invoices = []

def log_audit(action, details):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = st.session_state.logged_in_user or "زائر"
    role = st.session_state.user_role
    st.session_state.audit_logs.insert(0, {
        "التاريخ والوقت": str(timestamp),
        "المستخدم": str(user),
        "الصلاحية": str(role),
        "العملية": str(action),
        "التفاصيل": str(details)
    })

def generate_html_invoice(inv):
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {inv['invoice_code']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); background: #fff; }}
            .header {{ text-align: center; border-bottom: 2px solid #6b46c1; padding-bottom: 10px; margin-bottom: 20px; }}
            .info {{ margin-bottom: 20px; font-size: 15px; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; font-size: 14px; }}
            th {{ background-color: #f3e8ff; color: #6b46c1; }}
            .totals {{ font-size: 16px; font-weight: bold; text-align: left; margin-top: 15px; line-height: 1.8; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 13px; color: #777; border-top: 1px dashed #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <h2>YASSER WEB - فاتورة طلبية رسمية</h2>
                <p>التاريخ والوقت: {inv['created_date']}</p>
            </div>
            <div class="info">
                <p><strong>رقم الفاتورة:</strong> {inv['invoice_code']}</p>
                <p><strong>اسم الزبون:</strong> {inv['customer_name']}</p>
                <p><strong>طريقة وحالة الدفع:</strong> {inv['payment_type']}</p>
            </div>
            <table>
                <tr><th>تفاصيل المنتجات والمواد المطلوبة</th></tr>
                <tr><td>{inv['products_text']}</td></tr>
            </table>
            <div class="totals">
                <p>المبلغ الكلي: {inv['total_price']:,} د.ع</p>
                <p>المبلغ الواصل: {inv['paid_amount']:,} د.ع</p>
                <p>المتبقي (الدين): {inv['remaining_amount']:,} د.ع</p>
            </div>
            <div class="footer"><p>شكراً لتعاملكم معنا - Yasser Web POS</p></div>
        </div>
    </body>
    </html>
    """

# إذا حصل خطأ اتصال، النظام سيستمر بالعمل عبر الذاكرة المحلية بسلاسة تامة
if not supabase:
    st.sidebar.warning("⚠️ تنبيه: تم التحويل إلى وضع التشغيل المحلي (Offline/Memory Mode) بسبب عطل مؤقت في الـ DNS السحابي.")

# **شاشة تسجيل الدخول الأنيقة**
if not st.session_state.logged_in_user:
    st.markdown("<h2 style='text-align: center; color: white;'>🔐 بوابة الدخول لحسابات المحلات والنظام</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_modern_form"):
            login_user = st.text_input("اسم المستخدم أو اسم المحل:")
            login_role = st.selectbox("حدد الصلاحية عند الدخول:", ["مشرف النظام", "كاشير", "مسؤول مبيعات"])
            sub_log = st.form_submit_button("تسجيل الدخول", type="primary")
            if sub_log:
                if login_user.strip():
                    st.session_state.logged_in_user = str(login_user.strip())
                    st.session_state.user_role = str(login_role)
                    log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {login_user.strip()}")
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

# **شريط الإعدادات الجانبي (Sidebar)**
st.sidebar.title("⚙️ إعدادات الحساب")
st.sidebar.write(f"👤 المستخدم: **{username}**")
st.sidebar.write(f"👤 الصلاحية: **{user_role}**")
cart_total_count = sum(int(item['qty']) for item in st.session_state.cart)
st.sidebar.info(f"🛒 المواد بالسلة: **{cart_total_count}**")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in_user = None
    st.session_state.cart = []
    st.rerun()

st.divider()

# **قائمة التبويبات الـ 11 الكاملة مدعومة بالتصميم المبتكر**
tab_titles = [
    "🏠 الرئيسية والشبكة",
    "🛒 سلة البيع وإتمام الفاتورة",
    "➕ إضافة وتوريد كميات", 
    "📦 جرد المخزن", 
    "👥 إدارة العملاء والديون", 
    "💵 سداد الديون",
    "🏭 إدارة الموردين",
    "📄 سجل الفواتير وواتساب", 
    "💰 الصندوق والمصاريف", 
    "📊 التقارير والأرباح",
    "📜 سجل النشاطات"
]

selected_tab = st.radio("القائمة الرئيسية:", tab_titles, horizontal=True)

st.divider()

# ================= TAB 1: الرئيسية وشبكة المبيعات =================
if selected_tab == "🏠 الرئيسية والشبكة":
    st.markdown("### 🛍️ شبكة المواد المتاحة للبيع السريع")
    grid_items = st.session_state.local_products

    if grid_items:
        g_cols = st.columns(3)
        for idx, item in enumerate(grid_items):
            with g_cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"#### 📦 {item['product_name']}")
                    st.markdown(f"💰 السعر المفرد: `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🔢 المتوفر بالمخزن: `{item['quantity']}` قطعة")
                    if item['quantity'] > 0:
                        if st.button("➕ إضافة للسلة", key=f"fast_add_{idx}"):
                            found = False
                            for ci in st.session_state.cart:
                                if ci["product_name"] == item["product_name"]:
                                    if ci["qty"] < item["quantity"]:
                                        ci["qty"] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({
                                    "product_name": item["product_name"],
                                    "color": item.get('color', ''),
                                    "size": item.get('size', ''),
                                    "sell_price": item["sell_price"],
                                    "buy_price": item["buy_price"],
                                    "max_qty": item["quantity"],
                                    "qty": 1
                                })
                            st.toast("✅ تمت الإضافة للسلة بنجاح!", icon="🛒")
                            st.rerun()
                    else:
                        st.error("نفدت الكمية")
    else:
        st.info("لا توجد مواد في المخزن. توجه إلى تبويب (إضافة وتوريد كميات) لإضافة بضاعة جديدة.")

# ================= TAB 2: سلة البيع وإتمام الفاتورة =================
elif selected_tab == "🛒 سلة البيع وإتمام الفاتورة":
    st.markdown("### 🛒 مراجعة السلة وإتمام الفاتورة (مع التعبئة التلقائية للعميل)")
    if st.session_state.cart:
        total_cart_price = 0
        for idx, c_item in enumerate(st.session_state.cart):
            cols_c = st.columns([3, 2, 2, 1])
            with cols_c[0]:
                st.write(f"**{c_item['product_name']}**")
            with cols_c[1]:
                new_q = st.number_input("العدد", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_qty_{idx}")
                c_item['qty'] = new_q
            with cols_c[2]:
                item_sum = c_item['sell_price'] * c_item['qty']
                total_cart_price += item_sum
                st.write(f"المجموع: **{int(item_sum):,}** د.ع")
            with cols_c[3]:
                if st.button("❌", key=f"remove_c_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()

        st.divider()
        st.markdown(f"### 💵 المجموع الكلي: **{int(total_cart_price):,} د.ع**")

        customer_records = st.session_state.local_customers

        if not customer_records:
            st.warning("⚠️ تنبيه: يرجى إضافة عميل أولاً من تبويب (إدارة العملاء والديون) لتتمكن من إتمام الفاتورة!")
            selected_cust_name = ""
        else:
            cust_names = [c["customer_name"] for c in customer_records]
            selected_cust_name = st.selectbox("اختر اسم الزبون (للتعبئة التلقائية لرقمه وعنوانه):", cust_names)
            
            selected_cust_obj = next((c for c in customer_records if c["customer_name"] == selected_cust_name), None)
            if selected_cust_obj:
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.text_input("رقم الهاتف (تلقائي):", value=selected_cust_obj.get("phone", ""), disabled=True)
                with col_f2:
                    st.text_input("العنوان (تلقائي):", value=selected_cust_obj.get("address", ""), disabled=True)

        paid_str = st.text_input("المبلغ الواصل من الزبون (د.ع):", value=str(int(total_cart_price)))
        try:
            paid_val = float(paid_str.strip())
            if paid_val < 0: paid_val = 0
            if paid_val > total_cart_price: paid_val = total_cart_price
        except:
            paid_val = 0
        rem_val = total_cart_price - paid_val

        if paid_val >= total_cart_price:
            pay_status = "🟢 نقد بالكامل (كاش)"
        elif paid_val == 0:
            pay_status = "🔴 دين كامل (آجل)"
        else:
            pay_status = "🔵 دفعة جزئية (أقساط)"

        st.info(f"💡 حالة الدفع: {pay_status} | الواصل: **{int(paid_val):,} د.ع** | المتبقي (الدين): **{int(rem_val):,} د.ع**")

        if st.button("💾 إتمام البيع، خصم المخزن، وطباعة الفاتورة", type="primary"):
            if not selected_cust_name:
                st.error("يرجى اختيار عميل صالح.")
            else:
                try:
                    prod_str_list = []
                    total_cost_inv = 0
                    for c_item in st.session_state.cart:
                        prod_str_list.append(f"{c_item['product_name']} [العدد: {c_item['qty']}]")
                        total_cost_inv += (c_item['buy_price'] * c_item['qty'])
                        
                        # خصم المخزن المحلي
                        for p in st.session_state.local_products:
                            if p["product_name"] == c_item["product_name"]:
                                p["quantity"] = max(0, p["quantity"] - c_item['qty'])

                    inv_seq = len(st.session_state.local_invoices) + 1
                    inv_code = f"INV-{inv_seq:03d}"

                    inv_data = {
                        "username": str(username),
                        "invoice_code": str(inv_code),
                        "customer_name": str(selected_cust_name),
                        "products_text": str(" ، ".join(prod_str_list)),
                        "total_price": int(total_cart_price),
                        "cost_price": int(total_cost_inv),
                        "paid_amount": int(paid_val),
                        "remaining_amount": int(rem_val),
                        "payment_type": str(pay_status),
                        "created_date": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
                    }

                    st.session_state.local_invoices.append(inv_data)
                    log_audit("إتمام بيع", f"فاتورة رقم {inv_code} للزبون {selected_cust_name}")
                    st.session_state.cart = []
                    st.success("✅ تمت عملية البيع وحفظ الفاتورة بنجاح!")
                    
                    st.markdown("### 📄 معاينة الفاتورة للطباعة:")
                    st.components.v1.html(generate_html_invoice(inv_data), height=450, scrolling=True)
                    st.balloons()
                except Exception as ex:
                    st.error(f"خطأ: {ex}")
    else:
        st.info("🛒 السلة فارغة. اختر مواد من تبويب (الرئيسية والشبكة).")

# ================= TAB 3: إضافة وتوريد الكميات =================
elif selected_tab == "➕ إضافة وتوريد كميات":
    st.subheader("➕ إضافة مادة جديدة أو توريد كميات إضافية فوق المخزون")
    existing_prods = st.session_state.local_products

    mode = st.radio("اختر العملية:", ["إضافة مادة جديدة بالكامل", "توريد وزيادة كمية لمادة موجودة مسبقاً"], horizontal=True)

    if mode == "توريد وزيادة كمية لمادة موجودة مسبقاً" and existing_prods:
        with st.form("restock_form_tab"):
            p_opts = {f"{p['product_name']} (المتوفر: {p['quantity']})": p['product_name'] for p in existing_prods}
            chosen_p = st.selectbox("اختر المادة لتوريد كمية فوقها:", list(p_opts.keys()))
            add_q_str = st.text_input("الكمية المراد إضافتها:", "1")
            if st.form_submit_button("تحديث وزيادة الكمية", type="primary"):
                try:
                    add_amt = int(add_q_str.strip())
                    p_name_target = p_opts[chosen_p]
                    for item_obj in existing_prods:
                        if item_obj['product_name'] == p_name_target:
                            item_obj['quantity'] += add_amt
                            new_tot = item_obj['quantity']
                            log_audit("توريد", f"توريد {add_amt} للمنتج {p_name_target}")
                            st.success(f"🎉 تم تحديث كمية المادة بنجاح! الإجمالي الجديد: {new_tot}")
                            st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
    else:
        if mode == "توريد وزيادة كمية لمادة موجودة مسبقاً":
            st.info("لا توجد مواد مسجلة لتوريد كميات لها.")
        else:
            with st.form("new_product_form", clear_on_submit=True):
                pn = st.text_input("اسم المادة / المنتج:")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    pcol = st.text_input("اللون / المواصفات:", "عام")
                with col_p2:
                    psize = st.text_input("القياس / الحجم:", "عام")
                
                c_1, c_2, c_3, c_4 = st.columns(4)
                with c_1:
                    p_buy = st.text_input("سعر الشراء (د.ع):", "0")
                with c_2:
                    p_sell = st.text_input("سعر القطعة المفرد (د.ع):", "0")
                with c_3:
                    p_qty = st.text_input("الكمية المتوفرة:", "1")
                with c_4:
                    p_bar = st.text_input("باركود:", "")

                if st.form_submit_button("حفظ المادة بالمخزن", type="primary"):
                    if pn.strip():
                        try:
                            st.session_state.local_products.append({
                                "username": str(username),
                                "product_name": str(pn.strip()),
                                "color": str(pcol),
                                "size": str(psize),
                                "buy_price": float(p_buy),
                                "sell_price": float(p_sell),
                                "quantity": int(p_qty),
                                "barcode": str(p_bar if p_bar else "بدون")
                            })
                            log_audit("إضافة منتج", f"تمت إضافة المنتج {pn}")
                            st.success(f"تمت إضافة ({pn}) بنجاح!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"خطأ: {e}")
                    else:
                        st.warning("أدخل اسم المادة.")

# ================= TAB 4: جرد المخزن =================
elif selected_tab == "📦 جرد المخزن":
    st.subheader("📦 جرد المخزن الشامل")
    inv_data = st.session_state.local_products

    if inv_data:
        df_inv = pd.DataFrame(inv_data)
        st.dataframe(df_inv, use_container_width=True)
    else:
        st.info("المخزن فارغ.")

# ================= TAB 5: إدارة العملاء والديون =================
elif selected_tab == "👥 إدارة العملاء والديون":
    st.subheader("👥 إدارة العملاء والديون والذمم")
    with st.form("cust_form", clear_on_submit=True):
        cn = st.text_input("اسم العميل:")
        cp = st.text_input("رقم الهاتف:")
        ca = st.text_input("العنوان / المنطقة:")
        if st.form_submit_button("حفظ العميل"):
            if cn and cp:
                try:
                    st.session_state.local_customers.append({
                        "username": str(username),
                        "customer_name": str(cn.strip()),
                        "phone": str(cp.strip()),
                        "address": str(ca.strip() if ca else "غير محدد"),
                        "created_at": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                    })
                    st.success(f"تم حفظ العميل {cn} بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
            else:
                st.warning("أدخل اسم العميل ورقم الهاتف.")

    c_list = st.session_state.local_customers
    if c_list:
        st.dataframe(pd.DataFrame(c_list), use_container_width=True)

# ================= TAB 6: سداد الديون =================
elif selected_tab == "💵 سداد الديون":
    st.subheader("💵 نظام سداد ديون العملاء")
    d_names = [x["customer_name"] for x in st.session_state.local_customers]

    if d_names:
        sel_cust_debt = st.selectbox("اختر العميل لتسديد ديونه:", d_names)
        c_invs = [i for i in st.session_state.local_invoices if i['customer_name'] == sel_cust_debt]

        tot_debt = sum(i.get('remaining_amount', 0) for i in c_invs)
        st.markdown(f"### إجمالي الدين المتبقي على العميل: **{tot_debt:,} د.ع**")

        with st.form("pay_d_form"):
            pay_amt_str = st.text_input("المبلغ المسدد (د.ع):", "0")
            if st.form_submit_button("إتمام التسديد"):
                try:
                    p_val = float(pay_amt_str.strip())
                    rem_p = p_val
                    for inv in c_invs:
                        if rem_p <= 0: break
                        curr_r = inv.get('remaining_amount', 0)
                        if curr_r > 0:
                            if rem_p >= curr_r:
                                inv['paid_amount'] = inv['total_price']
                                inv['remaining_amount'] = 0
                                inv['payment_type'] = "🟢 نقد بالكامل (كاش)"
                                rem_p -= curr_r
                            else:
                                inv['paid_amount'] += rem_p
                                inv['remaining_amount'] = curr_r - rem_p
                                inv['payment_type'] = "🔵 دفعة جزئية (أقساط)"
                                rem_p = 0
                    st.success("تم تسديد المبلغ بنجاح وتحديث الحساب!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
    else:
        st.info("لا توجد عملاء مسجلين.")

# ================= TAB 7: إدارة الموردين =================
elif selected_tab == "🏭 إدارة الموردين":
    st.subheader("🏭 إدارة الموردين")
    with st.form("sup_f", clear_on_submit=True):
        sn = st.text_input("اسم المورد:")
        sphone = st.text_input("رقم الهاتف:")
        if st.form_submit_button("إضافة المورد"):
            if sn:
                st.session_state.suppliers_list.append({"اسم المورد": sn, "الهاتف": sphone})
                st.success("تمت الإضافة بنجاح!")
                st.rerun()
    if st.session_state.suppliers_list:
        st.dataframe(pd.DataFrame(st.session_state.suppliers_list), use_container_width=True)

# ================= TAB 8: سجل الفواتير وواتساب =================
elif selected_tab == "📄 سجل الفواتير وواتساب":
    st.subheader("📄 سجل الفواتير الرسمية وإرسالها عبر الواتساب")
    all_is = st.session_state.local_invoices

    if all_is:
        for inv in reversed(all_is):
            with st.container(border=True):
                st.markdown(f"### فاتورة: `{inv['invoice_code']}` | الزبون: **{inv['customer_name']}**")
                st.markdown(f"المبلغ الكلي: `{inv['total_price']:,}` د.ع | المتبقي (الدين): `{inv['remaining_amount']:,}` د.ع")
                with st.expander("🖨️ عرض الفاتورة للطباعة"):
                    st.components.v1.html(generate_html_invoice(inv), height=400, scrolling=True)
    else:
        st.info("لا توجد فواتير مسجلة.")

# ================= TAB 9: الصندوق والمصاريف =================
elif selected_tab == "💰 الصندوق والمصاريف":
    st.subheader("💰 صندوق الوردية والمصاريف اليومية")
    with st.form("exp_f", clear_on_submit=True):
        et = st.text_input("بيان المصروف:")
        ea = st.text_input("المبلغ (د.ع):", "0")
        if st.form_submit_button("تسجيل المصروف"):
            if et:
                st.session_state.expenses_list.append({"البيان": et, "المبلغ": float(ea)})
                st.success("تم تسجيل المصروف!")
                st.rerun()
    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)

# ================= TAB 10: التقارير والأرباح =================
elif selected_tab == "📊 التقارير والأرباح":
    st.subheader("📊 التقارير المالية وحساب صافي الأرباح")
    reps = st.session_state.local_invoices

    if reps:
        tot_sales = sum(i['total_price'] for i in reps)
        tot_cost = sum(i.get('cost_price', 0) for i in reps)
        tot_profit = tot_sales - tot_cost
        tot_debt_rem = sum(i['remaining_amount'] for i in reps)

        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المبيعات", f"{tot_sales:,.0f} د.ع")
        c2.metric("صافي الأرباح", f"{tot_profit:,.0f} د.ع")
        c3.metric("إجمالي الديون المتبقية", f"{tot_debt_rem:,.0f} د.ع")
    else:
        st.info("لا توجد بيانات كافية للتقارير.")

# ================= TAB 11: سجل النشاطات =================
elif selected_tab == "📜 سجل النشاطات":
    st.subheader("📜 سجل النشاطات (Audit Trail)")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد سجلات نشاط حتى الآن.")
