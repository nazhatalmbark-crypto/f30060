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
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Yasser Web POS", layout="wide")

# **التصميم البنفسجي الحديث وواجهة الموبايل**
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

# **جلسات النظام الأساسية**
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "مشرف النظام"
if "current_view" not in st.session_state:
    st.session_state.current_view = "dashboard"
if "suppliers_list" not in st.session_state:
    st.session_state.suppliers_list = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "expenses_list" not in st.session_state:
    st.session_state.expenses_list = []
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

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

# **شاشة تسجيل الدخول**
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
                    try:
                        res = supabase.table("users").select("*").eq("username", login_user.strip()).execute()
                        if res.data:
                            user_info = res.data[0]
                            st.session_state.logged_in_user = str(user_info["username"])
                            st.session_state.user_role = str(login_role)
                            st.session_state.is_vip = bool(user_info.get("is_paid", False))
                            log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {user_info['username']}")
                            st.success("تم تسجيل الدخول بنجاح!")
                            st.rerun()
                        else:
                            supabase.table("users").insert({"username": login_user.strip(), "is_paid": False}).execute()
                            st.session_state.logged_in_user = str(login_user.strip())
                            st.session_state.user_role = str(login_role)
                            st.success("تم إنشاء الحساب وتسجيل الدخول بنجاح!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
                else:
                    st.warning("يرجى إدخال اسم المستخدم.")
    st.stop()

username = st.session_state.logged_in_user
user_role = st.session_state.user_role

# **شريط الإعدادات الجانبي**
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

# **التبويبات الـ 11 كاملة**
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
    try:
        res_grid = supabase.table("products").select("*").eq("username", username).execute()
        grid_items = res_grid.data if res_grid.data else []
    except:
        grid_items = []

    if grid_items:
        g_cols = st.columns(3)
        for idx, item in enumerate(grid_items):
            with g_cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"#### 📦 {item['product_name']}")
                    st.markdown(f"💰 السعر المفرد: `{int(item['sell_price']):,}` د.ع")
                    st.markdown(f"🔢 المتوفر بالمخزن: `{item['quantity']}` قطعة")
                    if item['quantity'] > 0:
                        if st.button("➕ إضافة للسلة", key=f"fast_add_{item['id']}"):
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
                new_q = st.number_input("العدد", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"cart_qty_{c_item['id']}")
                c_item['qty'] = new_q
            with cols_c[2]:
                item_sum = c_item['sell_price'] * c_item['qty']
                total_cart_price += item_sum
                st.write(f"المجموع: **{int(item_sum):,}** د.ع")
            with cols_c[3]:
                if st.button("❌", key=f"remove_c_{c_item['id']}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()

        st.divider()
        st.markdown(f"### 💵 المجموع الكلي: **{int(total_cart_price):,} د.ع**")

        try:
            res_custs = supabase.table("customers").select("*").eq("username", username).execute()
            customer_records = res_custs.data if res_custs.data else []
        except:
            customer_records = []

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
                        
                        res_p_q = supabase.table("products").select("quantity").eq("id", c_item["id"]).execute()
                        if res_p_q.data:
                            curr_q = res_p_q.data[0]["quantity"]
                            new_q = max(0, curr_q - c_item['qty'])
                            supabase.table("products").update({"quantity": new_q}).eq("id", c_item["id"]).execute()

                    res_inv_len = supabase.table("invoices").select("id").eq("username", username).execute()
                    inv_seq = len(res_inv_len.data) + 1 if res_inv_len.data else 1
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

                    supabase.table("invoices").insert(inv_data).execute()
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
    try:
        res_all_p = supabase.table("products").select("id, product_name, quantity, sell_price").eq("username", username).execute()
        existing_prods = res_all_p.data if res_all_p.data else []
    except:
        existing_prods = []

    mode = st.radio("اختر العملية:", ["إضافة مادة جديدة بالكامل", "توريد وزيادة كمية لمادة موجودة مسبقاً"], horizontal=True)

    if mode == "توريد وزيادة كمية لمادة موجودة مسبقاً" and existing_prods:
        with st.form("restock_form_tab"):
            p_opts = {f"{p['product_name']} (المتوفر: {p['quantity']})": p['id'] for p in existing_prods}
            chosen_p = st.selectbox("اختر المادة لتوريد كمية فوقها:", list(p_opts.keys()))
            add_q_str = st.text_input("الكمية المراد إضافتها:", "1")
            if st.form_submit_button("تحديث وزيادة الكمية", type="primary"):
                try:
                    add_amt = int(add_q_str.strip())
                    pid = p_opts[chosen_p]
                    item_obj = next(x for x in existing_prods if x['id'] == pid)
                    new_tot = item_obj['quantity'] + add_amt
                    supabase.table("products").update({"quantity": new_tot}).eq("id", pid).execute()
                    log_audit("توريد", f"توريد {add_amt} للمنتج {item_obj['product_name']}")
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
                            supabase.table("products").insert({
                                "username": str(username),
                                "product_name": str(pn.strip()),
                                "color": str(pcol),
                                "size": str(psize),
                                "buy_price": float(p_buy),
                                "sell_price": float(p_sell),
                                "quantity": int(p_qty),
                                "barcode": str(p_bar if p_bar else "بدون")
                            }).execute()
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
    try:
        res_inv = supabase.table("products").select("*").eq("username", username).execute()
        inv_data = res_inv.data if res_inv.data else []
    except:
        inv_data = []

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
                    supabase.table("customers").insert({
                        "username": str(username),
                        "customer_name": str(cn.strip()),
                        "phone": str(cp.strip()),
                        "address": str(ca.strip() if ca else "غير محدد"),
                        "created_at": str(datetime.datetime.now().strftime('%Y-%m-%d'))
                    }).execute()
                    st.success(f"تم حفظ العميل {cn} بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
            else:
                st.warning("أدخل اسم العميل ورقم الهاتف.")

    try:
        res_c_list = supabase.table("customers").select("*").eq("username", username).execute()
        c_list = res_c_list.data if res_c_list.data else []
    except:
        c_list = []
    if c_list:
        st.dataframe(pd.DataFrame(c_list), use_container_width=True)

# ================= TAB 6: سداد الديون =================
elif selected_tab == "💵 سداد الديون":
    st.subheader("💵 نظام سداد ديون العملاء")
    try:
        res_dc = supabase.table("customers").select("customer_name").eq("username", username).execute()
        d_names = [x["customer_name"] for x in res_dc.data] if res_dc.data else []
    except:
        d_names = []

    if d_names:
        sel_cust_debt = st.selectbox("اختر العميل لتسديد ديونه:", d_names)
        try:
            res_c_inv
