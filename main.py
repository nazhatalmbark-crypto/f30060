import datetime
import urllib.parse
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# إعدادات صفحة Streamlit
st.set_page_config(
    page_title="Yasser Web - نظام المبيعات وإدارة المخزن",
    page_icon="🛍️",
    layout="wide",
)

# ---------------------------------------------------------
# الاتصال بقاعدة بيانات Supabase
# ---------------------------------------------------------
SUPABASE_URL = "https://your-supabase-url.supabase.co"  # ضع رابط مشروعك هنا
SUPABASE_KEY = "your-supabase-anon-key"  # ضع مفتاح الـ Anon هنا


@st.cache_resource
def init_supabase() -> Client:
  return create_client(SUPABASE_URL, SUPABASE_KEY)


try:
  supabase = init_supabase()
except Exception as e:
  st.error(f"فشل الاتصال بقاعدة البيانات: {e}")

# ---------------------------------------------------------
# تهيئة الـ Session State
# ---------------------------------------------------------
if "cart" not in st.session_state:
  st.session_state.cart = []
if "audit_logs" not in st.session_state:
  st.session_state.audit_logs = []
if "expenses_list" not in st.session_state:
  st.session_state.expenses_list = []


def log_audit(action, details):
  st.session_state.audit_logs.insert(
      0, {
          "العملية": action,
          "التفاصيل": details,
          "الوقت": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      }
  )


# دالة لتوليد كود الفاتورة HTML للطباعة
def generate_html_invoice(inv):
  return f"""
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>فاتورة رقم {inv['invoice_code']}</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>فاتورة مبيعات - Yasser Web</h2>
            <p>رقم الفاتورة: {inv['invoice_code']}</p>
            <p>التاريخ: {inv['created_date']}</p>
            <p>الزبون: {inv['customer_name']}</p>
        </div>
        <hr>
        <p><b>المنتجات:</b><br>{inv['products_text']}</p>
        <table>
            <tr>
                <th>المبلغ الإجمالي</th>
                <th>المبلغ الواصل</th>
                <th>المبلغ المتبقي</th>
            </tr>
            <tr>
                <td>{inv['total_price']:,} د.ع</td>
                <td>{inv['paid_amount']:,} د.ع</td>
                <td>{inv['remaining_amount']:,} د.ع</td>
            </tr>
        </table>
        <br><p style="text-align: center;">شكراً لتعاملكم معنا!</p>
    </body>
    </html>
    """


# واجهة المستخدم الرئيسية
st.title("🛍️ Yasser Web - نظام المبيعات وإدارة المخزن والمحاسبة")
username = st.sidebar.text_input("اسم المستخدم (Username):", value="yasser")

# الألسنة الأساسية للنظام
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "➕ إضافة مادة",
    "📦 المخزن والباركود",
    "👥 الزبائن والديون",
    "🛒 نقطة البيع (POS)",
    "💵 تسديد الديون",
    "📊 إدارة المواد",
    "📄 سجل الفواتير والطباعة",
    "💰 المصاريف",
    "📈 التقارير المالية",
    "📜 سجل النشاطات",
    "📖 دليل الاستخدام",
])

# ---------------------------------------------------------
# Tab 1: إضافة مادة
# ---------------------------------------------------------
with tab1:
  st.subheader("➕ إضافة مادة جديدة للمخزن")
  with st.form("add_product_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      p_name = st.text_input("اسم المادة:")
      p_barcode = st.text_input("الباركود (اتركه فارغاً للتوليد التلقائي):")
      p_cost = st.number_input(
          "سعر الشراء (التكلفة):", min_value=0.0, step=500.0
      )
    with col2:
      p_price = st.number_input("سعر البيع:", min_value=0.0, step=500.0)
      p_qty = st.number_input("الكمية الأولية:", min_value=0, step=1)
      p_alert = st.number_input("حد التنبيه لنفاد الكمية:", value=5, step=1)

    submitted = st.form_submit_button("حفظ المادة في المخزن")
    if submitted:
      if p_name.strip():
        if not p_barcode.strip():
          p_barcode = f"BAR-{datetime.datetime.now().strftime('%d%H%M%S')}"
        try:
          data = {
              "username": username,
              "name": p_name,
              "barcode": p_barcode,
              "cost_price": p_cost,
              "selling_price": p_price,
              "quantity": p_qty,
              "alert_limit": p_alert,
          }
          supabase.table("products").insert(data).execute()
          log_audit("إضافة مادة", f"تم إضافة المادة: {p_name} برمز {p_barcode}")
          st.success(f"تمت إضافة المادة بنجاح! الباركود: {p_barcode}")
        except Exception as e:
          st.error(f"حدث خطأ أثناء الحفظ: {e}")
      else:
        st.warning("يرجى إدخال اسم المادة على الأقل.")

# ---------------------------------------------------------
# Tab 2: المخزن والباركود
# ---------------------------------------------------------
with tab2:
  st.subheader("📦 إدارة المخزن والمنتجات المتوفرة")
  try:
    res = (
        supabase.table("products")
        .select("*")
        .eq("username", username)
        .execute()
    )
    products = res.data if res.data else []
  except:
    products = []

  if products:
    df_prod = pd.DataFrame(products)
    st.dataframe(df_prod, use_container_width=True)
  else:
    st.info("لا توجد مواد مسجلة حالياً.")

# ---------------------------------------------------------
# Tab 3: الزبائن والديون
# ---------------------------------------------------------
with tab3:
  st.subheader("👥 إضافة وإدارة الزبائن والديون")
  with st.form("add_customer_form", clear_on_submit=True):
    c_name = st.text_input("اسم الزبون:")
    c_phone = st.text_input("رقم الهاتف:")
    c_address = st.text_input("العنوان:")
    if st.form_submit_button("حفظ الزبون"):
      if c_name.strip():
        try:
          supabase.table("customers").insert({
              "username": username,
              "name": c_name,
              "phone": c_phone,
              "address": c_address,
              "balance": 0.0,
          }).execute()
          log_audit("إضافة زبون", f"تم إضافة الزبون: {c_name}")
          st.success("تم حفظ الزبون بنجاح!")
          st.rerun()
        except Exception as e:
          st.error(f"خطأ: {e}")
      else:
        st.warning("يرجى كتابة اسم الزبون.")

# ---------------------------------------------------------
# Tab 4: نقطة البيع (POS)
# ---------------------------------------------------------
with tab4:
  st.subheader("🛒 نقطة البيع وسلة المشتريات")
  try:
    res_p = (
        supabase.table("products")
        .select("*")
        .eq("username", username)
        .execute()
    )
    available_products = res_p.data if res_p.data else []
  except:
    available_products = []

  if available_products:
    prod_dict = {f"{p['name']} (متوفر: {p['quantity']})": p for p in available_products}
    selected_prod_label = st.selectbox("اختر المادة للبيع:", list(prod_dict.keys()))
    selected_item = prod_dict[selected_prod_label]

    sell_qty = st.number_input("الكمية المطلوبة:", min_value=1, value=1, step=1)
    if st.button("إضافة للسلة"):
      if sell_qty <= selected_item["quantity"]:
        st.session_state.cart.append({
            "id": selected_item["id"],
            "name": selected_item["name"],
            "price": selected_item["selling_price"],
            "cost": selected_item["cost_price"],
            "quantity": sell_qty,
            "total": selected_item["selling_price"] * sell_qty,
        })
        st.success("تمت الإضافة للسلة!")
      else:
        st.error("الكمية المطلوبة غير متوفرة في المخزن!")

    if st.session_state.cart:
      st.markdown("### 🧺 محتويات السلة الحالية")
      df_cart = pd.DataFrame(st.session_state.cart)
      st.dataframe(df_cart, use_container_width=True)

      total_cart_sum = sum(i["total"] for i in st.session_state.cart)
      st.markdown(f"### الإجمالي الكلي: **{total_cart_sum:,} د.ع**")

      # جلب الزبائن لإتمام البيع
      try:
        res_c = (
            supabase.table("customers")
            .select("id, name")
            .eq("username", username)
            .execute()
        )
        customers_list = res_c.data if res_c.data else []
      except:
        customers_list = []

      cust_options = {c["name"]: c["id"] for c in customers_list}
      cust_options["زبون نقدي عام"] = None
      chosen_cust_name = st.selectbox("اختر الزبون:", list(cust_options.keys()))

      payment_mode = st.radio(
          "طريقة الدفع:", ["كاش (نقدي)", "دين (أقساط / آجل)", "مختلط (دفعة + دين)"]
      )
      paid_input = st.number_input(
          "المبلغ الواصل (المستلم):",
          min_value=0.0,
          value=float(total_cart_sum),
          step=500.0,
      )

      if st.button("إتمام عملية البيع وتوليد الفاتورة"):
        rem_amount = max(0.0, total_cart_sum - paid_input)
        products_text_desc = ", ".join(
            [f"{i['name']} (x{i['quantity']})" for i in st.session_state.cart]
        )
        invoice_code = f"INV-{datetime.datetime.now().strftime('%d%H%M%S')}"

        try:
          # حفظ الفاتورة
          supabase.table("invoices").insert({
              "username": username,
              "invoice_code": invoice_code,
              "customer_name": chosen_cust_name,
              "products_text": products_text_desc,
              "total_price": total_cart_sum,
              "paid_amount": paid_input,
              "remaining_amount": rem_amount,
              "payment_type": payment_mode,
              "created_date": datetime.datetime.now().strftime(
                  "%Y-%m-%d %H:%M"
              ),
          }).execute()

          # خصم الكميات من المخزن
          for item in st.session_state.cart:
            res_cur = (
                supabase.table("products")
                .select("quantity")
                .eq("id", item["id"])
                .execute()
            )
            if res_cur.data:
              new_q = res_cur.data[0]["quantity"] - item["quantity"]
              supabase.table("products").update({"quantity": new_q}).eq(
                  "id", item["id"]
              ).execute()

          # تسجيل الدين إذا وجد على الزبون
          if rem_amount > 0 and cust_options[chosen_cust_name] is not None:
            c_id = cust_options[chosen_cust_name]
            res_cust_db = (
                supabase.table("customers")
                .select("balance")
                .eq("id", c_id)
                .execute()
            )
            old_bal = (
                res_cust_db.data[0]["balance"] if res_cust_db.data else 0.0
            )
            supabase.table("customers").update(
                {"balance": old_bal + rem_amount}
            ).eq("id", c_id).execute()

          log_audit(
              "عملية بيع جديدة",
              f"فاتورة رقم {invoice_code} بقيمة {total_cart_sum}",
          )
          st.success(
              f"تم إتمام البيع بنجاح! رقم الفاتورة: {invoice_code} | المتبقي:"
              f" {rem_amount:,} د.ع"
          )
          st.session_state.cart = []
        except Exception as e:
          st.error(f"خطأ أثناء إتمام عملية البيع: {e}")
  else:
    st.info("لا توجد منتجات في المخزن لتتمكن من البيع.")

# ---------------------------------------------------------
# Tab 5: تسديد الديون
# ---------------------------------------------------------
with tab5:
  st.subheader("💵 تسديد ديون وذمم الزبائن")
  try:
    res_debt = (
        supabase.table("customers")
        .select("*")
        .eq("username", username)
        .gt("balance", 0)
        .execute()
    )
    debt_customers = res_debt.data if res_debt.data else []
  except:
    debt_customers = []

  if debt_customers:
    d_dict = {f"{c['name']} (الديون: {c['balance']:,} د.ع)": c for c in debt_customers}
    chosen_debt_label = st.selectbox(
        "اختر الزبون لتسديد الدين:", list(d_dict.keys())
    )
    selected_debt_cust = d_dict[chosen_debt_label]

    pay_amount = st.number_input(
        "المبلغ المسدد الآن:", min_value=0.0, step=500.0
    )
    if st.button("تأكيد التسديد وتحديث الحساب"):
      if pay_amount > 0:
        new_balance = max(
            0.0, selected_debt_cust["balance"] - pay_amount
        )
        try:
          supabase.table("customers").update({"balance": new_balance}).eq(
              "id", selected_debt_cust["id"]
          ).execute()
          log_audit(
              "تسديد دين",
              f"تم تسديد مبلغ {pay_amount} للزبون {selected_debt_cust['name']}",
          )
          st.success(
              "تم تحديث رصيد الزبون بنجاح! الدين المتبقي:"
              f" {new_balance:,} د.ع"
          )
          st.rerun()
        except Exception as e:
          st.error(f"خطأ: {e}")
      else:
        st.warning("يرجى إدخال مبلغ صحيح للتسديد.")
  else:
    st.info("لا توجد ديون مسجلة على الزبائن حالياً.")

# ---------------------------------------------------------
# Tab 6: إدارة المواد
# ---------------------------------------------------------
with tab6:
  st.subheader("📊 إدارة المواد وتعديل الأسعار والمخزون")
  try:
    res_m = (
        supabase.table("products")
        .select("*")
        .eq("username", username)
        .execute()
    )
    all_prods = res_m.data if res_m.data else []
  except:
    all_prods = []

  if all_prods:
    for prod in all_prods:
      with st.expander(
          f"مادة: {prod['name']} | السعر: {prod['selling_price']:,} | المخزون:"
          f" {prod['quantity']}"
      ):
        with st.form(f"update_prod_{prod['id']}"):
          up_name = st.text_input("اسم المادة:", value=prod["name"])
          up_price = st.number_input(
              "سعر البيع:", value=float(prod["selling_price"])
          )
          up_qty = st.number_input("الكمية:", value=int(prod["quantity"]))
          if st.form_submit_button("تحديث البيانات"):
            try:
              supabase.table("products").update({
                  "name": up_name,
                  "selling_price": up_price,
                  "quantity": up_qty,
              }).eq("id", prod["id"]).execute()
              log_audit("تعديل مادة", f"تم تحديث بيانات المادة: {up_name}")
              st.success("تم التحديث بنجاح!")
              st.rerun()
            except Exception as e:
              st.error(f"خطأ: {e}")
  else:
    st.info("لا توجد مواد لإدارتها.")

# ---------------------------------------------------------
# Tab 7: سجل الفواتير، الطباعة المباشرة، وإرسال الواتساب
# ---------------------------------------------------------
with tab7:
  st.subheader("📄 سجل الفواتير، الطباعة المباشرة، وإرسال الفاتورة عبر الواتساب")
  try:
    res_all_inv = (
        supabase.table("invoices")
        .select("*")
        .eq("username", username)
        .order("id", desc=True)
        .execute()
    )
    all_invoices = res_all_inv.data if res_all_inv.data else []
  except:
    all_invoices = []

  if all_invoices:
    for inv in all_invoices:
      with st.expander(
          f"🧾 فاتورة رقم: {inv['invoice_code']} | الزبون:"
          f" {inv['customer_name']} | المبلغ: {inv['total_price']:,} د.ع"
      ):
        st.write(f"📅 **التاريخ:** {inv['created_date']}")
        st.write(f"💳 **طريقة الدفع:** {inv['payment_type']}")
        st.write(f"📦 **المنتجات:** {inv['products_text']}")
        st.markdown(
            f"💰 **المجموع:** {inv['total_price']:,} | **الواصل:**"
            f" {inv['paid_amount']:,} | **المتبقي:**"
            f" `{inv['remaining_amount']:,}` د.ع"
        )

        wa_msg = (
            f"مرحباً {inv['customer_name']},\nإليك تفاصيل فاتورتك"
            f" ({inv['invoice_code']}):\nالمنتجات: {inv['products_text']}\nالمبلغ"
            f" الإجمالي: {inv['total_price']:,} د.ع\nالواصل: {inv['paid_amount']:,}"
            f" د.ع\nالمتبقي: {inv['remaining_amount']:,} د.ع\nشكراً لتعاملكم معنا!"
        )
        encoded_wa = urllib.parse.quote(wa_msg)
        whatsapp_url = f"https://wa.me/?text={encoded_wa}"

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
          st.markdown(
              f'<a href="{whatsapp_url}" target="_blank"><button'
              ' style="background-color:#25D366; color:white; border:none;'
              ' padding:8px 16px; border-radius:5px; cursor:pointer;'
              ' font-weight:bold;">💬 إرسال عبر واتساب</button></a>',
              unsafe_allow_html=True,
          )
        with col_btn2:
          if st.button(
              f"🖨️ طباعة الفاتورة #{inv['invoice_code']}",
              key=f"print_inv_{inv['id']}",
          ):
            html_code = generate_html_invoice(inv)
            st.components.v1.html(
                f"""
                        <script>
                            var win = window.open('', '', 'height=700,width=800');
                            win.document.write(`{html_code}`);
                            win.document.close();
                            win.focus();
                            setTimeout(function(){{ win.print(); }}, 500);
                        </script>
                    """,
                height=0,
            )
  else:
    st.info("لا توجد فواتير مسجلة حتى الآن.")

# ---------------------------------------------------------
# Tab 8: المصاريف
# ---------------------------------------------------------
with tab8:
  st.subheader("💰 صندوق الوردية والمصاريف اليومية")
  with st.form("expenses_form", clear_on_submit=True):
    exp_title = st.text_input("بيان المصروف (مثال: إيجار، خط إنترنت):")
    exp_amount_str = st.text_input("مبلغ المصروف (د.ع):", "0")
    if st.form_submit_button("تسجيل المصروف"):
      if exp_title.strip():
        try:
          exp_val = float(exp_amount_str.strip())
          st.session_state.expenses_list.insert(
              0, {
                  "البيان": str(exp_title.strip()),
                  "المبلغ": float(exp_val),
                  "التاريخ": str(
                      datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                  ),
              }
          )
          log_audit(
              "تسجيل مصروف", f"تم تسجيل مصروف {exp_title} بمبلغ {exp_val}"
          )
          st.success("تم تسجيل المصروف بنجاح!")
          st.rerun()
        except ValueError:
          st.error("يرجى إدخال مبلغ صحيح.")
      else:
        st.warning("يرجى كتابة بيان المصروف.")

  st.divider()
  if st.session_state.expenses_list:
    st.dataframe(
        pd.DataFrame(st.session_state.expenses_list), use_container_width=True
    )
    total_expenses = sum(e["المبلغ"] for e in st.session_state.expenses_list)
    st.markdown(f"### إجمالي المصاريف المسجلة: **{int(total_expenses):,} د.ع**")
  else:
    st.info("لا توجد مصاريف مسجلة في هذه الوردية.")

# ---------------------------------------------------------
# Tab 9: التقارير المالية والرسوم البيانية
# ---------------------------------------------------------
with tab9:
  st.subheader("📊 الرسوم البيانية والتقارير المالية والتحليلية")
  try:
    res_rep_inv = (
        supabase.table("invoices").select("*").eq("username", username).execute()
    )
    rep_invoices = res_rep_inv.data if res_rep_inv.data else []
  except:
    rep_invoices = []

  if rep_invoices:
    df_rep = pd.DataFrame(rep_invoices)
    total_sales_sum = df_rep["total_price"].sum()
    total_cost_sum = (
        df_rep.get("cost_price", pd.Series([0] * len(df_rep))).sum()
    )
    total_profit_sum = total_sales_sum - total_cost_sum

    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("إجمالي المبيعات", f"{int(total_sales_sum):,} د.ع")
    col_r2.metric("إجمالي التكلفة", f"{int(total_cost_sum):,} د.ع")
    col_r3.metric(
        "صافي الأرباح",
        f"{int(total_profit_sum):,} د.ع",
        delta=f"{int(total_profit_sum):,} د.ع",
    )

    st.divider()
    st.markdown("#### 📈 مبيعات الفواتير")
    st.bar_chart(df_rep, x="invoice_code", y="total_price")
  else:
    st.info("لا توجد بيانات كافية لعرض الرسوم البيانية والتقارير.")

# ---------------------------------------------------------
# Tab 10: سجل النشاطات (Audit Trail)
# ---------------------------------------------------------
with tab10:
  st.subheader("📜 سجل النشاطات والعمليات (Audit Trail)")
  if (
      isinstance(st.session_state.audit_logs, list)
      and len(st.session_state.audit_logs) > 0
  ):
    st.dataframe(
        pd.DataFrame(st.session_state.audit_logs), use_container_width=True
    )
  else:
    st.info("لا توجد نشاطات مسجلة حتى الآن في هذه الجلسة.")

# ---------------------------------------------------------
# Tab 11: دليل الاستخدام والمميزات
# ---------------------------------------------------------
with tab11:
  st.subheader("📖 دليل الاستخدام والمميزات والدعم الفني")
  st.markdown("""
    * **إضافة المواد:** تمكنك من إضافة منتجاتك مع تحديد السعر والكمية والباركود التلقائي.
    * **المخزن والباركود:** إدارة المخزون، وتتبع المواد والتنبيه عند نفادها.
    * **إدارة العملاء والديون:** حفظ بيانات العملاء ومتابعة الديون والذمم المالية بدقة.
    * **نظام المبيعات:** سلة بيع متكاملة تدعم الخصم التلقائي من المخزن وتصنيف المبالغ (كاش / آجل).
    * **الواتساب والطباعة:** إرسال الفواتير للعملاء بنقرة واحدة عبر الواتساب أو طباعتها فورياً.
    """)
