import streamlit as str_lit
import pandas as pd
from supabase import create_client, Client
import datetime
import json
import urllib.parse

SUPABASE_URL = "https://mdffzniutjcjnytuoakb.supabase.co" 
SUPABASE_KEY = "sb_publishable_PjzQyJU_n-4pFdLZV7os6w_gLt78fLp"

@str_lit.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

str_lit.set_page_config(page_title="Yasser Web - النظام الشامل لإدارة المحلات", page_icon="🛍️", layout="wide")

str_lit.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; }
    input, select, textarea { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

defaults = {
    "lang": "العربية",
    "logged_in_user": None,
    "user_role": "مشرف النظام",
    "customer_list": [],
    "suppliers_list": [],
    "invoices_list": [],
    "cart": [],
    "expenses_list": [],
    "payments_receipts": [],
    "audit_logs": [],
    "is_vip": False
}

for key, val in defaults.items():
    if key not in str_lit.session_state:
        str_lit.session_state[key] = val

def log_audit(action, details):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = str_lit.session_state.logged_in_user or "زائر"
    role = str_lit.session_state.user_role
    if not isinstance(str_lit.session_state.audit_logs, list):
        str_lit.session_state.audit_logs = []
    str_lit.session_state.audit_logs.insert(0, {
        "التاريخ والوقت": str(timestamp),
        "المستخدم": str(user),
        "الصلاحية": str(role),
        "العملية": str(action),
        "التفاصيل": str(details)
    })

# دالة لتوليد كود HTML جاهز للطباعة والحفظ كـ PDF من المتصفح مباشرة (بدون مشاكل اللغة العربية)
def get_printable_invoice_html(inv):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {inv['رقم الفاتورة']}</title>
        <style>
            body {{ font-family: 'Tahoma', Arial, sans-serif; padding: 20px; color: #333; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); border-radius: 8px; }}
            .header {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 10px; }}
            .info-table {{ width: 100%; margin-bottom: 20px; border-collapse: collapse; }}
            .info-table td {{ padding: 8px; vertical-align: top; }}
            .products-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            .products-table th, .products-table td {{ border: 1px solid #ddd; padding: 10px; text-align: right; }}
            .products-table th {{ background-color: #f2f2f2; }}
            .totals {{ float: left; width: 300px; }}
            .totals table {{ width: 100%; border-collapse: collapse; }}
            .totals td {{ padding: 6px; border-bottom: 1px solid #eee; }}
            .footer {{ clear: both; text-align: center; margin-top: 40px; font-size: 14px; color: #777; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="invoice-box">
            <div class="header">
                <h2>YASSER WEB - فاتورة طلبية توصيل</h2>
                <p>التاريخ: {inv['التاريخ']}</p>
            </div>
            <table class="info-table">
                <tr>
                    <td><strong>رقم الفاتورة:</strong> {inv['رقم الفاتورة']}</td>
                    <td><strong>اسم الزبون:</strong> {inv['الزبون']}</td>
                </tr>
                <tr>
                    <td><strong>نوع الدفع:</strong> {inv['نوع الدفع']}</td>
                    <td><strong>الحالة:</strong> {inv['حالة الفاتورة واللون']}</td>
                </tr>
            </table>
            <table class="products-table">
                <tr>
                    <th>توصيف المواد والمنتجات المطلوبة</th>
                </tr>
                <tr>
                    <td>{inv['المنتجات'].replace(' , ', '<br>')}</td>
                </tr>
            </table>
            <div class="totals">
                <table>
                    <tr><td><strong>المبلغ الكلي:</strong></td><td>{inv['المبلغ الكلي']:,} د.ع</td></tr>
                    <tr><td><strong>المبلغ الواصل:</strong></td><td>{inv['الواصل']:,} د.ع</td></tr>
                    <tr><td><strong>المتبقي (الدين):</strong></td><td>{inv['المتبقي (الدين)']:,} د.ع</td></tr>
                    <tr><td><strong>تكلفة البنزين (pbf):</strong></td><td>{inv.get('pbf', 0):,} د.ع</td></tr>
                </table>
            </div>
            <div class="footer">
                <p>شكراً لتعاملكم مع نظام Yasser Web لإدارة المبيعات والمخزن!</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

str_lit.title("🛍️ نظام Yasser Web الشامل لإدارة المبيعات والمخزون")

if not str_lit.session_state.logged_in_user:
    str_lit.subheader("🔐 بوابة الدخول لحسابات المحلات والنظام")
    auth_tab1, auth_tab2 = str_lit.tabs(["🔑 تسجيل الدخول", "✨ إنشاء حساب جديد"])
    
    with auth_tab1:
        with str_lit.form("login_form_fixed"):
            login_user = str_lit.text_input("اسم المستخدم أو اسم المحل:")
            login_role = str_lit.selectbox("حدد الصلاحية عند الدخول:", ["مشرف النظام", "كاشير", "مسؤول مبيعات"])
            if str_lit.form_submit_button("تسجيل الدخول", type="primary"):
                if login_user.strip():
                    try:
                        res = supabase.table("users").select("*").eq("username", login_user.strip()).execute()
                        if res.data:
                            user_info = res.data[0]
                            str_lit.session_state.logged_in_user = str(user_info["username"])
                            str_lit.session_state.user_role = str(login_role)
                            str_lit.session_state.is_vip = bool(user_info.get("is_paid", False))
                            log_audit("تسجيل دخول", f"تم تسجيل الدخول بواسطة {user_info['username']}")
                            str_lit.success("تم تسجيل الدخول بنجاح!")
                            str_lit.rerun()
                        else:
                            str_lit.error("❌ اسم المستخدم غير موجود، أنشئ حساباً جديداً.")
                    except Exception as e:
                        str_lit.error(f"خطأ في الاتصال: {e}")
                else:
                    str_lit.warning("أدخل اسم المستخدم.")
                    
    with auth_tab2:
        with str_lit.form("signup_form_fixed"):
            new_user = str_lit.text_input("اختر اسم المستخدم أو اسم المحل الجديد:")
            signup_role = str_lit.selectbox("حدد الصلاحية للحساب الجديد:", ["مشرف النظام", "كاشير", "مسؤول مبيعات"])
            if str_lit.form_submit_button("إنشاء الحساب الآن", type="primary"):
                if new_user.strip():
                    try:
                        check_res = supabase.table("users").select("*").eq("username", new_user.strip()).execute()
                        if check_res.data:
                            str_lit.error("❌ اسم المستخدم مستخدم مسبقاً.")
                        else:
                            supabase.table("users").insert({"username": new_user.strip(), "is_paid": False}).execute()
                            str_lit.session_state.logged_in_user = str(new_user.strip())
                            str_lit.session_state.user_role = str(signup_role)
                            str_lit.session_state.is_vip = False
                            log_audit("إنشاء حساب جديد", f"تم إنشاء حساب {new_user.strip()}")
                            str_lit.success("🎉 تم إنشاء الحساب بنجاح!")
                            str_lit.rerun()
                    except Exception as e:
                        str_lit.error(f"خطأ: {e}")
                else:
                    str_lit.warning("أدخل اسم المستخدم.")
    str_lit.stop()

username = str_lit.session_state.logged_in_user
user_role = str_lit.session_state.user_role

str_lit.sidebar.title("⚙️ الإعدادات والنسخ الاحتياطي")
str_lit.sidebar.write(f"👤 المستخدم: **{username}**")
str_lit.sidebar.write(f"👤 الصلاحية: **{user_role}**")

cart_count = sum(int(i['qty']) for i in str_lit.session_state.cart)
str_lit.sidebar.info(f"🛒 المواد بالسلة: **{cart_count}**")

str_lit.sidebar.divider()
backup_data = {
    "username": str(username),
    "customers": list(str_lit.session_state.customer_list),
    "suppliers": list(str_lit.session_state.suppliers_list),
    "invoices": list(str_lit.session_state.invoices_list),
    "expenses": list(str_lit.session_state.expenses_list),
    "payments_receipts": list(str_lit.session_state.payments_receipts),
    "audit_logs": list(str_lit.session_state.audit_logs)
}
str_lit.sidebar.download_button(
    label="📥 تحميل نسخة احتياطية (JSON)",
    data=json.dumps(backup_data, ensure_ascii=False, indent=4, default=str),
    file_name=f"backup_{username}_{datetime.datetime.now().strftime('%Y%m%d')}.json",
    mime="application/json"
)

uploaded_backup = str_lit.sidebar.file_uploader("📂 استعادة البيانات من ملف سابق", type=["json"])
if uploaded_backup is not None:
    try:
        rb = json.load(uploaded_backup)
        if "customers" in rb and "invoices" in rb:
            str_lit.session_state.customer_list = rb.get("customers", [])
            str_lit.session_state.suppliers_list = rb.get("suppliers", [])
            str_lit.session_state.invoices_list = rb.get("invoices", [])
            str_lit.session_state.expenses_list = rb.get("expenses", [])
            str_lit.session_state.payments_receipts = rb.get("payments_receipts", [])
            str_lit.session_state.audit_logs = rb.get("audit_logs", [])
            str_lit.sidebar.success("✅ تمت الاستعادة بنجاح!")
            str_lit.rerun()
    except Exception as e:
        str_lit.sidebar.error(f"خطأ: {e}")

str_lit.sidebar.divider()
if not str_lit.session_state.is_vip:
    vip_code = str_lit.sidebar.text_input("كود النسخة المدفوعة (VIP):", type="password")
    if str_lit.sidebar.button("تفعيل النسخة المدفوعة"):
        if vip_code.strip() == "YASSER2026":
            str_lit.session_state.is_vip = True
            try:
                supabase.table("users").update({"is_paid": True}).eq("username", username).execute()
            except:
                pass
            str_lit.sidebar.success("تم التفعيل بنجاح! 🎉")
            str_lit.rerun()
        else:
            str_lit.sidebar.error("الكود غير صحيح!")
else:
    str_lit.sidebar.success("🌟 النسخة المدفوعة مفعلة")

if str_lit.sidebar.button("تسجيل الخروج"):
    str_lit.session_state.logged_in_user = None
    str_lit.session_state.is_vip = False
    str_lit.session_state.cart = []
    str_lit.rerun()

str_lit.divider()

tab_names = [
    "➕ إضافة مادة جديدة", 
    "📦 جرد المخزن والباركود", 
    "👥 إدارة العملاء والديون", 
    "🏭 إدارة الموردين",
    "🛒 إتمام البيع والفواتير", 
    "📄 سجل الفواتير والسداد وواتساب", 
    "💵 صندوق سداد", 
    "📊 الرسوم البيانية والتقارير",
    "📜 سجل النشاطات",
    "📖 دليل الاستخدام والدعم"
]
tabs = str_lit.tabs(tab_names)

with tabs[0]:
    str_lit.subheader("➕ واجهة إضافة مادة أو بضاعة جديدة للمخزن")
    if user_role == "كاشير":
        str_lit.warning("⚠️ حساب الكاشير لا يمتلك صلاحية إضافة المواد.")
    else:
        try:
            res_c = supabase.table("products").select("id").eq("username", username).execute()
            ccount = len(res_c.data) if res_c.data else 0
        except:
            ccount = 0
            
        if not str_lit.session_state.is_vip and ccount >= 5:
            str_lit.warning("⚠️ وصلت للحد الأقصى للنسخة المجانية (5 منتجات). فعّل النسخة المدفوعة لإضافة مواد بلا حدود!")
        else:
            with str_lit.form("add_prod_form_f", clear_on_submit=True):
                p_name = str_lit.text_input("اسم المادة / المنتج:")
                c_col, c_sz = str_lit.columns(2)
                with c_col:
                    p_color = str_lit.text_input("اللون / المواصفات:", "عام")
                with c_sz:
                    p_size = str_lit.text_input("القياس / الحجم:", "عام")
                
                c1, c2, c3, c4 = str_lit.columns(4)
                with c1:
                    p_buy = str_lit.text_input("سعر الشراء (د.ع):", "0")
                with c2:
                    p_sell = str_lit.text_input("سعر البيع (د.ع):", "0")
                with c3:
                    p_qty = str_lit.text_input("الكمية المتوفرة:", "1")
                with c4:
                    p_barcode = str_lit.text_input("رمز الباركود:", "")
                
                if str_lit.form_submit_button("حفظ المادة في المخزن", type="primary"):
                    if p_name.strip():
                        try:
                            supabase.table("products").insert({
                                "username": str(username),
                                "product_name": str(p_name.strip()),
                                "color": str(p_color.strip()),
                                "size": str(p_size.strip()),
                                "buy_price": float(p_buy.strip()),
                                "sell_price": float(p_sell.strip()),
                                "quantity": int(p_qty.strip()),
                                "barcode": str(p_barcode.strip() if p_barcode else "بدون")
                            }).execute()
                            str_lit.success(f"تمت إضافة ({p_name}) بنجاح!")
                            str_lit.rerun()
                        except Exception as e:
                            str_lit.error(f"خطأ في الحفظ: {e}")
                    else:
                        str_lit.warning("أدخل اسم المادة.")

with tabs[1]:
    str_lit.subheader("📦 جرد المخزن الشامل مع الباركود وتوليد الأرباح")
    try:
        all_products = supabase.table("products").select("*").eq("username", username).execute().data or []
    except:
        all_products = []

    if all_products:
        cols = str_lit.columns(3)
        for idx, item in enumerate(all_products):
            with cols[idx % 3]:
                with str_lit.container(border=True):
                    str_lit.markdown(f"### 📦 {item['product_name']}")
                    str_lit.write(f"🎨 اللون: `{item.get('color','عام')}` | 📏 القياس: `{item.get('size','عام')}`")
                    str_lit.write(f"💰 شراء: `{int(item['buy_price']):,}` | بيع: `{int(item['sell_price']):,}` د.ع")
                    str_lit.write(f"🔢 الكمية: `{int(item['quantity'])}` قطعة")
                    
                    if item['quantity'] > 0:
                        if str_lit.button("🛒 إضافة للسلة", key=f"c_add_{item['id']}"):
                            found = False
                            for ci in str_lit.session_state.cart:
                                if ci["id"] == item["id"]:
                                    if ci["qty"] < item["quantity"]:
                                        ci["qty"] += 1
                                    found = True
                                    break
                            if not found:
                                str_lit.session_state.cart.append({
                                    "id": item["id"],
                                    "product_name": item["product_name"],
                                    "color": item.get('color',''),
                                    "size": item.get('size',''),
                                    "sell_price": item["sell_price"],
                                    "buy_price": item["buy_price"],
                                    "max_qty": item["quantity"],
                                    "qty": 1
                                })
                            str_lit.toast("تمت الإضافة للسلة!", icon="🛍️")
                            str_lit.rerun()
    else:
        str_lit.info("المخزن فارغ.")

with tabs[2]:
    str_lit.subheader("👥 إدارة العملاء والديون")
    iraq_govs = ["بغداد", "البصرة", "نينوى", "أربيل", "النجف", "كربلاء", "ذي قار", "بابل", "الأنبار", "ديالى", "كركوك", "صلاح الدين", "المثنى", "ميسان", "القادسية", "واسط", "دهوك", "السليمانية"]
    
    with str_lit.form("add_cust_f_fixed_final", clear_on_submit=True):
        c1, c2, c3 = str_lit.columns(3)
        with c1: c_name = str_lit.text_input("اسم العميل الجديد:")
        with c2: c_phone = str_lit.text_input("رقم الهاتف (مثلاً 9647...):")
        with c3: c_gov = str_lit.selectbox("المحافظة:", iraq_govs)
        
        if str_lit.form_submit_button("تسجيل وحفظ بيانات العميل", type="primary"):
            if c_name.strip() and c_phone.strip():
                str_lit.session_state.customer_list.append({
                    "اسم العميل": str(c_name.strip()), 
                    "رقم الهاتف": str(c_phone.strip()), 
                    "المحافظة": str(c_gov)
                })
                str_lit.success(f"تم تسجيل العميل ({c_name}) بنجاح!")
                str_lit.rerun()
            else:
                str_lit.warning("⚠️ يرجى إدخال اسم العميل ورقم الهاتف بصورة صحيحة.")
                
    if str_lit.session_state.customer_list:
        str_lit.write("### قائمة العملاء المسجلين حالياً:")
        str_lit.dataframe(pd.DataFrame(str_lit.session_state.customer_list), use_container_width=True)
    else:
        str_lit.info("لا يوجد عملاء مسجلون حالياً. استخدم النموذج أعلاه لإضافة عميل.")

with tabs[3]:
    str_lit.subheader("🏭 إدارة الموردين")
    with str_lit.form("sup_form_clean", clear_on_submit=True):
        s_name = str_lit.text_input("اسم المورد:")
        s_phone = str_lit.text_input("رقم الهاتف:")
        if str_lit.form_submit_button("إضافة المورد"):
            if s_name.strip():
                str_lit.session_state.suppliers_list.append({"اسم المورد": s_name, "رقم الهاتف": s_phone})
                str_lit.success("تمت الإضافة بنجاح!")
                str_lit.rerun()
    if str_lit.session_state.suppliers_list:
        str_lit.dataframe(pd.DataFrame(str_lit.session_state.suppliers_list), use_container_width=True)

with tabs[4]:
    str_lit.subheader("🛒 سلة المبيعات وإصدار الفواتير")
    if str_lit.session_state.cart:
        total_price = 0
        for idx, ci in enumerate(str_lit.session_state.cart):
            c_cols = str_lit.columns([3, 2, 2, 1])
            with c_cols[0]: str_lit.write(f"**{ci['product_name']}** ({ci['sell_price']:,} د.ع)")
            with c_cols[1]: ci['qty'] = str_lit.number_input("الكمية", 1, int(ci['max_qty']), int(ci['qty']), key=f"sq_{ci['id']}")
            with c_cols[2]:
                it_tot = ci['sell_price'] * ci['qty']
                total_price += it_tot
                str_lit.write(f"المجموع: **{int(it_tot):,}**")
            with c_cols[3]:
                if str_lit.button("حذف", key=f"s_del_{ci['id']}"):
                    str_lit.session_state.cart.pop(idx)
                    str_lit.rerun()
                    
        str_lit.markdown(f"### المجموع الكلي: **{int(total_price):,} د.ع**")
        
        c_opts = [c["اسم العميل"] for c in str_lit.session_state.customer_list] if str_lit.session_state.customer_list else ["لا توجد عملاء"]
        cust_sel = str_lit.selectbox("اختر الزبون:", c_opts)
        pay_t = str_lit.radio("نوع الدفع:", ["نقد (كاش)", "آجل (دين)", "دفعة جزئية"], horizontal=True)
        
        paid_val = total_price if pay_t == "نقد (كاش)" else (0 if pay_t == "آجل (دين)" else float(str_lit.text_input("المبلغ الواصل:", "0") or 0))
        rem_val = total_price - paid_val
        pbf_val = float(str_lit.text_input("تكلفة البنزين والتوصيل (pbf):", "0") or 0)

        if str_lit.button("💾 إتمام البيع وحفظ الفاتورة", type="primary"):
            if c_opts == ["لا توجد عملاء"] or not str_lit.session_state.customer_list:
                str_lit.error("❌ اختر عميلاً مسجلاً أولاً من تبويب إدارة العملاء!")
            else:
                try:
                    p_str_list = []
                    tot_cost = 0
                    for ci in str_lit.session_state.cart:
                        p_str_list.append(f"{ci['product_name']} - الكمية: {ci['qty']}")
                        tot_cost += (ci['buy_price'] * ci['qty'])
                        
                        db_q = supabase.table("products").select("quantity").eq("id", ci["id"]).execute().data[0]["quantity"]
                        supabase.table("products").update({"quantity": max(0, db_q - ci['qty'])}).eq("id", ci["id"]).execute()
                        
                    inv_code = f"INV-{len(str_lit.session_state.invoices_list) + 1:03d}"
                    str_lit.session_state.invoices_list.append({
                        "رقم الفاتورة": inv_code,
                        "الزبون": cust_sel,
                        "المنتجات": " , ".join(p_str_list),
                        "المبلغ الكلي": int(total_price),
                        "تكلفتها": int(tot_cost),
                        "الواصل": int(paid_val),
                        "المتبقي (الدين)": int(rem_val),
                        "pbf": int(pbf_val),
                        "نوع الدفع": pay_t,
                        "حالة الفاتورة واللون": "🟢 مسددة" if rem_val == 0 else "🟡 آجل",
                        "التاريخ": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    })
                    str_lit.session_state.cart = []
                    str_lit.success("✅ تمت العملية بنجاح!")
                    str_lit.rerun()
                except Exception as e:
                    str_lit.error(f"خطأ: {e}")
    else:
        str_lit.info("السلة فارغة.")

with tabs[5]:
    str_lit.subheader("📄 سجل الفواتير، سداد الديون، طباعة الفواتير، وواتساب")
    
    if str_lit.session_state.invoices_list:
        table_display_data = []
        for inv in str_lit.session_state.invoices_list:
            table_display_data.append({
                "رقم الفاتورة": inv["رقم الفاتورة"],
                "التاريخ": inv["التاريخ"],
                "الزبون": inv["الزبون"],
                "المبلغ الكلي": f"{inv['المبلغ الكلي']:,} د.ع",
                "الواصل": f"{inv['الواصل']:,} د.ع",
                "المتبقي": f"{inv['المتبقي (الدين)']:,} د.ع",
                "بنزين (pbf)": f"{inv.get('pbf', 0):,} د.ع",
                "الحالة": inv["حالة الفاتورة واللون"]
            })
        str_lit.dataframe(pd.DataFrame(table_display_data), use_container_width=True)
        str_lit.divider()

        for idx_i, inv in enumerate(reversed(str_lit.session_state.invoices_list)):
            with str_lit.container(border=True):
                c_i1, c_i2, c_i3 = str_lit.columns([2, 2, 2])
                with c_i1:
                    str_lit.markdown(f"#### {inv['رقم الفاتورة']} | الزبون: {inv['الزبون']}")
                    str_lit.write(f"الحالة: {inv['حالة الفاتورة واللون']} | المجموع: **{inv['المبلغ الكلي']:,}** د.ع")
                    str_lit.write(f"المتبقي (دين): **{inv['المتبقي (الدين)']:,}** د.ع | بنزين (pbf): **{inv.get('pbf', 0):,}** د.ع")
                    str_lit.write(f"المنتجات: {inv['المنتجات']}")
                with c_i2:
                    if inv['المتبقي (الدين)'] > 0:
                        pay_more = str_lit.text_input("سداد مبلغ إضافي:", "0", key=f"pm_{idx_i}")
                        if str_lit.button("تأكيد السداد", key=f"bp_{idx_i}"):
                            try:
                                val = float(pay_more)
                                if 0 < val <= inv['المتبقي (الدين)']:
                                    inv['الواصل'] += val
                                    inv['المتبقي (الدين)'] -= val
                                    if inv['المتبقي (الدين)'] == 0: 
                                        inv['حالة الفاتورة واللون'] = "🟢 مسددة"
                                    str_lit.success("تم السداد بنجاح!")
                                    str_lit.rerun()
                            except: 
                                pass
                with c_i3:
                    # زر طباعة وتصدير PDF دقيق عبر المتصفح بدون مشاكل الحروف المقلوبة
                    html_code = get_printable_invoice_html(inv)
                    str_lit.download_button(
                        label="🖨️ طباعة / حفظ فاتورة PDF",
                        data=html_code,
                        file_name=f"Invoice_{inv['رقم الفاتورة']}.html",
                        mime="text/html",
                        key=f"print_html_{idx_i}"
                    )
                    str_lit.caption("💡 ملاحظة: ملف الـ HTML يفتح بمتصفحك واضغط (Ctrl+P) ثم اختر حفظ كـ PDF ليظهر بشكل عربي مرتب 100%.")
                    
                    matched_cust = next((c for c in str_lit.session_state.customer_list if c['اسم العميل'] == inv['الزبون']), None)
                    default_phone = matched_cust['رقم الهاتف'] if matched_cust and 'رقم الهاتف' in matched_cust else ""
                    
                    w_phone = str_lit.text_input(f"رقم هاتف الواتساب لـ {inv['الزبون']}:", value=default_phone, key=f"wphone_{idx_i}")
                    
                    if w_phone.strip():
                        msg = urllib.parse.quote(f"مرحباً بك يا أستاذ {inv['الزبون']},\n\nإليك تفاصيل فاتورتك ({inv['رقم الفاتورة']}):\n- المنتجات: {inv['المنتجات']}\n- المبلغ الكلي: {inv['المبلغ الكلي']:,} د.ع\n- الواصل: {inv['الواصل']:,} د.ع\n- المتبقي (الدين): {inv['المتبقي (الدين)']:,} د.ع\n- تكلفة النقل/البنزين (pbf): {inv.get('pbf', 0):,} د.ع\n\nشكراً لتعاملكم معنا في نظام Yasser Web!")
                        str_lit.markdown(f"[💬 اضغط هنا للإرسال عبر واتساب مباشرة](https://wa.me/{w_phone.strip()}?text={msg})", unsafe_allow_html=True)
                    else:
                        str_lit.warning("⚠️ أدخل رقم الهاتف لتفعيل رابط واتساب.")
    else:
        str_lit.info("لا توجد فواتير مسجلة.")

with tabs[6]:
    str_lit.subheader("💵 صندوق سداد والوصولات")
    with str_lit.form("rec_form", clear_on_submit=True):
        c_opts_r = [c["اسم العميل"] for c in str_lit.session_state.customer_list] if str_lit.session_state.customer_list else ["لا يوجد عملاء"]
        rcust = str_lit.selectbox("الزبون:", c_opts_r)
        ramt = str_lit.text_input("المبلغ المسدد:", "0")
        if str_lit.form_submit_button("إصدار وصل سداد"):
            if c_opts_r != ["لا يوجد عملاء"]:
                str_lit.session_state.payments_receipts.insert(0, {
                    "رقم الوصل": f"REC-{len(str_lit.session_state.payments_receipts)+1:03d}",
                    "اسم الزبون": rcust, "المبلغ": float(ramt or 0), "التاريخ": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                str_lit.success("تم إصدار الوصل بنجاح!")
                str_lit.rerun()
    if str_lit.session_state.payments_receipts:
        str_lit.dataframe(pd.DataFrame(str_lit.session_state.payments_receipts), use_container_width=True)

with tabs[7]:
    str_lit.subheader("📊 التقارير والأرباح")
    tot_rev = sum(i['المبلغ الكلي'] for i in str_lit.session_state.invoices_list)
    tot_cost = sum(i.get('تكلفتها', 0) for i in str_lit.session_state.invoices_list)
    tot_pbf = sum(i.get('pbf', 0) for i in str_lit.session_state.invoices_list)
    str_lit.metric("إجمالي الإيرادات", f"{tot_rev:,} د.ع")
    str_lit.metric("إجمالي مصاريف البنزين (pbf)", f"{tot_pbf:,} د.ع")
    str_lit.metric("صافي الأرباح (بعد خصم التكلفة والبنزين)", f"{tot_rev - tot_cost - tot_pbf:,} د.ع")

with tabs[8]:
    str_lit.subheader("📜 سجل النشاطات والعمليات")
    if str_lit.session_state.audit_logs:
        str_lit.dataframe(pd.DataFrame(str_lit.session_state.audit_logs), use_container_width=True)
    else:
        str_lit.info("لا توجد نشاطات مسجلة.")

with tabs[9]:
    str_lit.subheader("📖 الدعم الفني")
    str_lit.markdown("النظام جاهز ومحدث بالكامل. لتفعيل النسخة الكاملة استخدم الكود: `YASSER2026`")
