import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co"
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="ياسر بوس - Yasser POS", layout="centered")

# **تصميم مطابق 100% لواجهة تطبيق TOFA وبطابق الألوان البنفسجية**
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #553c9a 0%, #3b2375 100%);
        direction: rtl;
        text-align: right;
        font-family: system-ui, -apple-system, sans-serif;
        color: #ffffff;
    }
    input, select, textarea {
        direction: rtl;
        text-align: right;
        border-radius: 12px !important;
    }
    /* تصميم البطاقات البيضاء المطابقة لـ TOFA */
    .tofa-card {
        background: #ffffff;
        padding: 22px 15px;
        border-radius: 24px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        color: #2d1a4e;
        text-align: center;
        margin-bottom: 15px;
        cursor: pointer;
        border: 1px solid #f0ebf8;
    }
    .tofa-card h3 {
        color: #2d1a4e;
        font-size: 17px;
        margin-bottom: 5px;
        font-weight: 700;
    }
    .tofa-card p {
        color: #8a81ab;
        font-size: 11px;
        margin: 0;
    }
    .stButton > button {
        background-color: #6b46c1;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
        width: 100%;
        margin-top: 8px;
    }
    .stButton > button:hover {
        background-color: #553c9a;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# **تصفير وتهيئة الجلسات بقوائم فارغة تماماً**
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
if "active_page" not in st.session_state:
    st.session_state.active_page = "الرئيسية"

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
                <h2>ياسر بوس - فاتورة طلبية رسمية</h2>
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
            <div class="footer"><p>شكراً لتعاملكم معنا - ياسر بوس</p></div>
        </div>
    </body>
    </html>
    """

# **شاشة تسجيل الدخول**
if not st.session_state.logged_in_user:
    st.markdown("<h2 style='text-align: center; color: white;'>🔐 بوابة الدخول لنظام ياسر بوس</h2>", unsafe_allow_html=True)
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

# **شريط علوي احترافي**
top_c1, top_c2, top_c3 = st.columns([1, 4, 1])
with top_c1:
    if st.session_state.active_page != "الرئيسية":
        if st.button("⬅️ رجوع"):
            st.session_state.active_page = "الرئيسية"
            st.rerun()
with top_c2:
    st.markdown(f"<h3 style='text-align: center; margin: 0;'>ياسر بوس</h3>", unsafe_allow_html=True)
with top_c3:
    if st.button("🚪 خروج"):
        st.session_state.logged_in_user = None
        st.session_state.cart = []
        st.session_state.active_page = "الرئيسية"
        st.rerun()

st.divider()

# ================= الشاشة الرئيسية (مطابقة لـ TOFA) =================
if st.session_state.active_page == "الرئيسية":
    st.markdown("<h4 style='text-align: center; color: #e2d9f3; margin-bottom: 20px;'>إدارة المبيعات والعمليات</h4>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.container(border=True):
            st.markdown("### 📝 إنشاء فاتورة")
            st.write("إصدار الفواتير والطباعة والشبكة")
            if st.button("إصدار فاتورة جديدة", key="card_inv"):
                st.session_state.active_page = "إنشاء فاتورة"
                st.rerun()
                
        with st.container(border=True):
            st.markdown("### 👥 العملاء")
            st.write("إدارة العملاء والديون")
            if st.button("إدارة العملاء", key="card_cust"):
                st.session_state.active_page = "العملاء والديون"
                st.rerun()
                
        with st.container(border=True):
            st.markdown("### 💵 السندات")
            st.write("سندات قبض وصرف ومصاريف")
            if st.button("فتح السندات", key="card_bonds"):
                st.session_state.active_page = "الصندوق والمصاريف"
                st.rerun()

    with col_b:
        with st.container(border=True):
            st.markdown("### 📄 قائمة الفواتير")
            st.write("سجل الفواتير المباعة")
            if st.button("سجل الفواتير", key="card_list"):
                st.session_state.active_page = "قائمة الفواتير"
                st.rerun()
                
        with st.container(border=True):
            st.markdown("### 📦 المخزن")
            st.write("إدارة المشتريات والمخزون")
            if st.button("إدارة المخزن", key="card_store"):
                st.session_state.active_page = "المخزن"
                st.rerun()
                
        with st.container(border=True):
            st.markdown("### 🔄 إرجاع بيع")
            st.write("قائمة المرتجعات")
            if st.button("سجل النشاطات", key="card_return"):
                st.session_state.active_page = "سجل النشاطات"
                st.rerun()

    st.markdown("<br><p style='text-align: center; color: #b794f4; font-size: 12px;'>الإصدار 4.3.0</p>", unsafe_allow_html=True)

# ================= التبويبات الـ 11 المتكاملة بالكامل (فارغة ونظيفة) =================
elif st.session_state.active_page == "إنشاء فاتورة":
    st.subheader("🛒 إنشاء فاتورة جديدة والبيع السريع")
    sub_choice = st.radio("طريقة البيع:", ["شبكة المنتجات السريعة", "مراجعة السلة وإتمام الفاتورة"], horizontal=True)
    
    if sub_choice == "شبكة المنتجات السريعة":
        st.markdown("### 🛍️ المواد المتاحة للبيع السريع")
        try:
            res_grid = supabase.table("products").select("*").eq("username", username).execute()
            grid_items = res_grid.data if res_grid.data else []
        except:
            grid_items = []

        if grid_items:
            g_cols = st.columns(2)
            for idx, item in enumerate(grid_items):
                with g_cols[idx % 2]:
                    with st.container(border=True):
                        st.markdown(f"#### 📦 {item['product_name']}")
                        st.markdown(f"💰 السعر: `{int(item['sell_price']):,}` د.ع")
                        st.markdown(f"🔢 المتوفر: `{item['quantity']}` قطعة")
                        if item['quantity'] > 0:
                            if st.button("➕ إضافة للسلة", key=f"f_add_{item['id']}"):
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
                                        "sell_price": item["sell_price"],
                                        "buy_price": item["buy_price"],
                                        "max_qty": item["quantity"],
                                        "qty": 1
                                    })
                                st.success("تمت الإضافة للسلة!")
                                st.rerun()
                        else:
                            st.error("نفدت الكمية")
        else:
            st.info("لا توجد مواد مضافة في المخزن حالياً.")
    else:
        if st.session_state.cart:
            total_cart_price = 0
            for idx, c_item in enumerate(st.session_state.cart):
                with st.container(border=True):
                    st.write(f"**{c_item['product_name']}**")
                    cols_c = st.columns(3)
                    with cols_c[0]:
                        new_q = st.number_input("العدد", min_value=1, max_value=int(c_item['max_qty']), value=int(c_item['qty']), key=f"c_q_{c_item['id']}")
                        c_item['qty'] = new_q
                    with cols_c[1]:
                        item_sum = c_item['sell_price'] * c_item['qty']
                        total_cart_price += item_sum
                        st.write(f"المجموع: **{int(item_sum):,}**")
                    with cols_c[2]:
                        if st.button("❌ حذف", key=f"rem_{c_item['id']}"):
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
                st.warning("⚠️ يرجى إضافة عميل أولاً من قسم (العملاء والديون).")
                selected_cust_name = ""
            else:
                cust_names = [c["customer_name"] for c in customer_records]
                selected_cust_name = st.selectbox("اسم الزبون:", cust_names)

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

            if st.button("💾 بيع وطباعة الفاتورة", type="primary"):
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
                        log_audit("إتمام بيع", f"فاتورة رقم {inv_code}")
                        st.session_state.cart = []
                        st.success("✅ تمت عملية البيع بنجاح!")
                        st.components.v1.html(generate_html_invoice(inv_data), height=400, scrolling=True)
                        st.balloons()
                    except Exception as ex:
                        st.error(f"خطأ: {ex}")
        else:
            st.info("🛒 السلة فارغة تماماً. اختر مواد من شبكة المنتجات السريعة أولاً.")

elif st.session_state.active_page == "قائمة الفواتير":
    st.subheader("📄 سجل الفواتير الرسمية")
    try:
        res_all_i = supabase.table("invoices").select("*").eq("username", username).execute()
        all_is = res_all_i.data if res_all_i.data else []
    except:
        all_is = []

    if all_is:
        for inv in reversed(all_is):
            with st.container(border=True):
                st.markdown(f"### فاتورة: `{inv['invoice_code']}` | الزبون: **{inv['customer_name']}**")
                st.markdown(f"المبلغ الكلي: `{inv['total_price']:,}` د.ع | المتبقي: `{inv['remaining_amount']:,}` د.ع")
                with st.expander("🖨️ عرض الفاتورة للطباعة"):
                    st.components.v1.html(generate_html_invoice(inv), height=400, scrolling=True)
    else:
        st.info("لا توجد فواتير مسجلة حالياً.")

elif st.session_state.active_page == "المخزن":
    st.subheader("📦 إدارة المخزن والمشتريات")
    m_choice = st.radio("الخيارات:", ["عرض جرد المخزن", "إضافة مادة جديدة", "توريد كميات إضافية"], horizontal=True)
    
    if m_choice == "عرض جرد المخزن":
        try:
            res_inv = supabase.table("products").select("*").eq("username", username).execute()
            inv_data = res_inv.data if res_inv.data else []
        except:
            inv_data = []
        if inv_data:
            st.dataframe(pd.DataFrame(inv_data), use_container_width=True)
        else:
            st.info("المخزن فارغ تماماً.")
    elif m_choice == "إضافة مادة جديدة":
        with st.form("new_prod_form_tab", clear_on_submit=True):
            pn = st.text_input("اسم المادة / المنتج:")
            p_buy = st.text_input("سعر الشراء (د.ع):", "0")
            p_sell = st.text_input("سعر البيع المفرد (د.ع):", "0")
            p_qty = st.text_input("الكمية المتوفرة:", "1")
            p_bar = st.text_input("الباركود (اختياري):", "")
            if st.form_submit_button("حفظ المادة بالمخزن", type="primary"):
                if pn.strip():
                    try:
                        supabase.table("products").insert({
                            "username": str(username),
                            "product_name": str(pn.strip()),
                            "buy_price": float(p_buy),
                            "sell_price": float(p_sell),
                            "quantity": int(p_qty),
                            "barcode": str(p_bar if p_bar else "بدون")
                        }).execute()
                        st.success(f"تمت إضافة ({pn}) بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى إدخال اسم المادة.")
    else:
        try:
            res_all_p = supabase.table("products").select("id, product_name, quantity").eq("username", username).execute()
            existing_prods = res_all_p.data if res_all_p.data else []
        except:
            existing_prods = []
            
        if existing_prods:
            with st.form("restock_form"):
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
                        st.success(f"تم تحديث الكمية بنجاح! الإجمالي الجديد: {new_tot}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
        else:
            st.info("لا توجد مواد مسجلة لتوريد كميات لها.")

elif st.session_state.active_page == "العملاء والديون":
    st.subheader("👥 إدارة العملاء والذمم والديون")
    cust_mode = st.radio("العملية:", ["إضافة عميل جديد", "عرض العملاء وسداد الديون"], horizontal=True)
    
    if cust_mode == "إضافة عميل جديد":
        with st.form("cust_form_tab", clear_on_submit=True):
            cn = st.text_input("اسم العميل (حضرة السيد):")
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
    else:
        try:
            res_c_list = supabase.table("customers").select("*").eq("username", username).execute()
            c_list = res_c_list.data if res_c_list.data else []
        except:
            c_list = []
        if c_list:
            st.dataframe(pd.DataFrame(c_list), use_container_width=True)
            st.markdown("### 💵 تسديد ديون عميل")
            d_names = [c["customer_name"] for c in c_list]
            sel_cust_debt = st.selectbox("اختر العميل لتسديد ديونه:", d_names)
            try:
                res_c_inv = supabase.table("invoices").select("*").eq("username", username).eq("customer_name", sel_cust_debt).execute()
                c_invs = res_c_inv.data if res_c_inv.data else []
            except:
                c_invs = []
            tot_debt = sum(i.get('remaining_amount', 0) for i in c_invs)
            st.markdown(f"إجمالي الدين المتبقي على العميل: **{tot_debt:,} د.ع**")
            
            with st.form("pay_d_form_tab"):
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
                                    n_paid = inv['total_price']
                                    n_rem = 0
                                    n_type = "🟢 نقد بالكامل (كاش)"
                                    rem_p -= curr_r
                                else:
                                    n_paid = inv['paid_amount'] + rem_p
                                    n_rem = curr_r - rem_p
                                    n_type = "🔵 دفعة جزئية (أقساط)"
                                    rem_p = 0
                                supabase.table("invoices").update({"paid_amount": int(n_paid), "remaining_amount": int(n_rem), "payment_type": str(n_type)}).eq("id", inv["id"]).execute()
                        st.success("تم تسديد المبلغ بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
        else:
            st.info("لا يوجد عملاء مسجلين حالياً.")

elif st.session_state.active_page == "الصندوق والمصاريف":
    st.subheader("💰 صندوق الوردية وسندات القبض والصرف")
    with st.form("exp_f_tab", clear_on_submit=True):
        et = st.text_input("بيان السند (مثال: مصاريف إدارية / وقود):")
        ea = st.text_input("المبلغ (د.ع):", "0")
        if st.form_submit_button("تسجيل السند والمصروف"):
            if et:
                st.session_state.expenses_list.append({"البيان": et, "المبلغ": float(ea)})
                st.success("تم تسجيل السند بنجاح!")
                st.rerun()
    if st.session_state.expenses_list:
        st.dataframe(pd.DataFrame(st.session_state.expenses_list), use_container_width=True)
    else:
        st.info("لا توجد سندات أو مصاريف مسجلة اليوم.")

elif st.session_state.active_page == "سجل النشاطات":
    st.subheader("📜 سجل النشاطات والعمليات (Audit Trail)")
    if st.session_state.audit_logs:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.info("لا توجد سجلات نشاط مسجلة حتى الآن.")
