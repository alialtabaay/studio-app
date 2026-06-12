import streamlit as st
import pandas as pd
import os
import io
import hashlib
import streamlit.components.v1 as components
from datetime import datetime

# ============================================================
# 1. إعدادات الصفحة
# ============================================================
st.set_page_config(page_title="نظام جرد وإعارات الاستوديو", layout="wide", page_icon="🎙️")

# ============================================================
# 2. تنسيق CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    html, body, .stApp {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
    }

    /* القائمة الجانبية */
    [data-testid="stSidebar"] {
        width: 300px !important;
        direction: rtl;
        text-align: right;
        background: linear-gradient(180deg, #0f172a 0%, #1e3a5f 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
        text-align: right !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: #ef4444;
        color: white !important;
        border: none;
        border-radius: 8px;
        width: 100%;
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
    }
    button[aria-label="Collapse sidebar"] { display: none !important; }

    /* التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: #1e3a8a !important;
        color: white !important;
    }

    /* بطاقات الإحصاء */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-top: 4px solid;
    }
    .stat-card.blue  { border-color: #3b82f6; }
    .stat-card.green { border-color: #22c55e; }
    .stat-card.amber { border-color: #f59e0b; }
    .stat-card.red   { border-color: #ef4444; }
    .stat-number { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .stat-label  { font-size: 0.9rem; color: #64748b; margin: 4px 0 0; }

    /* الجداول */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* الأزرار الرئيسية */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        border: none;
        border-radius: 8px;
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
        padding: 10px 24px;
        transition: transform 0.15s;
    }
    .stButton > button[kind="primary"]:hover { transform: translateY(-1px); }

    /* رسالة الطباعة */
    @media print {
        header, footer,
        section[data-testid="stSidebar"],
        .stTabs, .stButton, .stSelectbox,
        h2, [data-testid="stToolbar"] { display: none !important; }
        .print-area { display: block !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. المسارات وملفات البيانات
# ============================================================
DATA_DIR      = "/data/" if os.path.exists("/data/") else ""
DB_FILE       = os.path.join(DATA_DIR, "studio_inventory.xlsx")
USERS_FILE    = os.path.join(DATA_DIR, "studio_users.xlsx")
LOG_FILE      = os.path.join(DATA_DIR, "equipment_loans.xlsx")
CATEGORIES_FILE = os.path.join(DATA_DIR, "studio_categories.xlsx")

# ============================================================
# 4. الدوال المساعدة
# ============================================================
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_excel(DB_FILE, dtype={"المعرف (ID)": str})
        df["المعرف (ID)"] = df["المعرف (ID)"].astype(str).str.strip()
        if "العدد"      not in df.columns: df["العدد"]      = 1
        if "الملاحظات" not in df.columns: df["الملاحظات"] = ""
        return df
    return pd.DataFrame(
        columns=["المعرف (ID)", "اسم المعدة", "التصنيف", "الحالة", "المستلم/الموقع", "العدد", "الملاحظات"])


def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        return pd.read_excel(CATEGORIES_FILE)["التصنيف"].tolist()
    default_cats = ["كاميرات", "عدسات", "إضاءة", "صوتيات", "ملحقات أخرى"]
    pd.DataFrame({"التصنيف": default_cats}).to_excel(CATEGORIES_FILE, index=False)
    return default_cats


def save_categories(categories_list):
    pd.DataFrame({"التصنيف": categories_list}).to_excel(CATEGORIES_FILE, index=False)


def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_excel(USERS_FILE)
    df_admin = pd.DataFrame([{
        "اسم المستخدم": "admin",
        "كلمة السر":    hash_password("1234"),
        "الصلاحية":     "مدير"
    }])
    df_admin.to_excel(USERS_FILE, index=False)
    return df_admin


def load_loans():
    if os.path.exists(LOG_FILE):
        df_l = pd.read_excel(LOG_FILE)
        if "ملاحظات الحركة" not in df_l.columns:
            df_l["ملاحظات الحركة"] = ""
        return df_l
    return pd.DataFrame(columns=[
        "رقم الحركة", "اسم الأوردر", "الموظف المستلم", "المعدات المسحوبة",
        "تاريخ السحب", "تاريخ الإرجاع", "الحالة", "ملاحظات الحركة"
    ])


def save_data(df):   df.to_excel(DB_FILE,    index=False)
def save_users(df):  df.to_excel(USERS_FILE, index=False)
def save_loans(df):  df.to_excel(LOG_FILE,   index=False)


def status_badge(status):
    """إرجاع HTML بادج ملوّن حسب الحالة"""
    colors = {
        "متوفر":    ("#dcfce7", "#166534"),
        "معار":     ("#fef9c3", "#854d0e"),
        "صيانة":    ("#fee2e2", "#991b1b"),
        "خارج":     ("#dbeafe", "#1e40af"),
        "إرجاع":    ("#f0fdf4", "#166534"),
        "جزئي":     ("#fef3c7", "#92400e"),
    }
    for key, (bg, fg) in colors.items():
        if key in str(status):
            return f'<span style="background:{bg};color:{fg};padding:3px 10px;border-radius:20px;font-size:0.8rem;font-weight:600;">{status}</span>'
    return status

# ============================================================
# 5. إدارة جلسة تسجيل الدخول
# ============================================================
for key, val in [("logged_in", False), ("username", ""), ("role", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

users_df = load_users()

# ---- واجهة تسجيل الدخول ----
if not st.session_state["logged_in"]:
    st.markdown("""
    <div style="text-align:center; padding: 60px 0 30px;">
        <div style="font-size:3rem;">🎙️</div>
        <h1 style="color:#1e3a8a; font-family:'Cairo',sans-serif; margin:10px 0 4px;">نظام إدارة الاستوديو</h1>
        <p style="color:#64748b; font-family:'Cairo',sans-serif;">نظام متكامل لإدارة المخزن والإعارات</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align:center; font-family:Cairo,sans-serif; color:#1e3a8a;'>تسجيل الدخول 🔒</h3>", unsafe_allow_html=True)
            username_input = st.text_input("اسم المستخدم", placeholder="ادخل اسم المستخدم...")
            password_input = st.text_input("كلمة السر", type="password", placeholder="ادخل كلمة السر...")
            login_button   = st.form_submit_button("دخول إلى النظام 🔑", use_container_width=True, type="primary")

            if login_button:
                hashed = hash_password(password_input)
                match  = users_df[
                    (users_df["اسم المستخدم"] == username_input) &
                    (users_df["كلمة السر"]    == hashed)
                ]
                if not match.empty:
                    st.session_state["logged_in"] = True
                    st.session_state["username"]  = username_input
                    st.session_state["role"]      = match.iloc[0]["الصلاحية"]
                    st.success("🎉 تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة السر غير صحيحة!")
    st.stop()

# ============================================================
# 6. الواجهة الرئيسية بعد تسجيل الدخول
# ============================================================
st.sidebar.markdown(f"""
<div style="padding: 20px 0 10px; text-align:center;">
    <div style="font-size:2.5rem;">🎙️</div>
    <h3 style="margin:8px 0 4px;">نظام الاستوديو</h3>
</div>
<hr style="border-color:#334155; margin:10px 0;">
<p style="margin:4px 0;">👤 <b>{st.session_state['username']}</b></p>
<p style="margin:4px 0; font-size:0.85rem; color:#94a3b8 !important;">
    🔰 الصلاحية: {st.session_state['role']}
</p>
<hr style="border-color:#334155; margin:10px 0;">
""", unsafe_allow_html=True)

if st.sidebar.button("تسجيل الخروج 🚪"):
    for key in ["logged_in", "username", "role"]:
        st.session_state[key] = "" if key != "logged_in" else False
    st.rerun()

# تحميل البيانات
df             = load_data()
loans_df       = load_loans()
categories_list = load_categories()

# إحصائيات سريعة في الشريط الجانبي
total    = len(df)
avail    = len(df[df["الحالة"].str.contains("متوفر", na=False)])
borrowed = len(df[df["الحالة"].str.contains("معار",  na=False)])
active_orders = len(loans_df[loans_df["الحالة"].isin(["خارج الاستوديو", "إرجاع جزئي"])]) if not loans_df.empty else 0

st.sidebar.markdown(f"""
<div style="background:#1e293b; border-radius:10px; padding:14px; margin-top:10px;">
    <p style="margin:6px 0; font-size:0.85rem;">📦 إجمالي المعدات: <b>{total}</b></p>
    <p style="margin:6px 0; font-size:0.85rem; color:#4ade80 !important;">✅ متوفر: <b>{avail}</b></p>
    <p style="margin:6px 0; font-size:0.85rem; color:#fbbf24 !important;">📤 معار: <b>{borrowed}</b></p>
    <p style="margin:6px 0; font-size:0.85rem; color:#60a5fa !important;">📋 عهد نشطة: <b>{active_orders}</b></p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 7. بناء التبويبات
# ============================================================
is_admin = st.session_state["role"] == "مدير"

if is_admin:
    tabs = st.tabs([
        "🔍 متابعة المخزن",
        "📦 إدارة المواد",
        "📤 سحب جديد",
        "📥 إرجاع ومطابقة",
        "📊 السجل والأرشيف",
        "🖨️ طباعة الوصولات",
        "⚙️ الإعدادات"
    ])
    tab_view, tab_manage, tab_checkout, tab_checkin, tab_archive, tab_print, tab_settings = tabs
else:
    tabs = st.tabs([
        "🔍 متابعة المخزن",
        "📤 سحب جديد",
        "📥 إرجاع ومطابقة",
        "📊 السجل والأرشيف",
        "🖨️ طباعة الوصولات"
    ])
    tab_view, tab_checkout, tab_checkin, tab_archive, tab_print = tabs
    tab_manage   = None
    tab_settings = None


# ============================================================
# TAB 1: متابعة المخزن
# ============================================================
with tab_view:
    st.markdown("## 🔍 شاشة متابعة المخزن")

    # بطاقات الإحصاء
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card blue"><p class="stat-number">{total}</p><p class="stat-label">إجمالي المعدات</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card green"><p class="stat-number">{avail}</p><p class="stat-label">متوفر الآن</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card amber"><p class="stat-number">{borrowed}</p><p class="stat-label">معار حالياً</p></div>', unsafe_allow_html=True)
    with c4:
        maint = len(df[df["الحالة"].str.contains("صيانة", na=False)])
        st.markdown(f'<div class="stat-card red"><p class="stat-number">{maint}</p><p class="stat-label">في الصيانة</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # بحث وتصفية
    col_s, col_f = st.columns([3, 1])
    with col_s:
        search = st.text_input("🔎 بحث سريع...", placeholder="اكتب اسم المعدة أو المعرف...")
    with col_f:
        filter_status = st.selectbox("تصفية الحالة", ["الكل", "متوفر (Available)", "معار (Checked Out)", "في الصيانة (Under Maintenance)"])

    display_df = df.copy()
    if search:
        display_df = display_df[display_df.astype(str).apply(
            lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
    if filter_status != "الكل":
        display_df = display_df[display_df["الحالة"] == filter_status]

    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(f"📊 عرض {len(display_df)} من أصل {len(df)} قطعة")


# ============================================================
# TAB 2: إدارة وتعديل المواد (مدير فقط)
# ============================================================
if tab_manage is not None:
    with tab_manage:
        st.markdown("## 📦 لوحة التحكم بالمخزن (صلاحية مدير)")

        manage_action = st.radio(
            "اختر نوع الإجراء:",
            ["➕ إضافة قطعة جديدة", "📥 رفع من ملف إكسل", "✏️ تعديل أو حذف قطعة"],
            horizontal=True
        )

        # ---- إضافة قطعة ----
        if manage_action == "➕ إضافة قطعة جديدة":
            with st.form("add_item_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_id   = st.text_input("معرف المعدة (ID / Barcode) *").strip()
                    new_name = st.text_input("اسم المعدة *").strip()
                    new_cat  = st.selectbox("التصنيف", categories_list)
                with col2:
                    new_status = st.selectbox("الحالة", ["متوفر (Available)", "في الصيانة (Under Maintenance)"])
                    new_loc    = st.text_input("الموقع", value="الرف الرئيسي").strip()
                    new_qty    = st.number_input("العدد", min_value=1, value=1, step=1)
                new_notes = st.text_area("الملاحظات (اختياري)").strip()

                if st.form_submit_button("إضافة إلى الجرد 💾", type="primary"):
                    if not new_id or not new_name:
                        st.error("⚠️ يرجى ملء حقل المعرف والاسم!")
                    elif not df.empty and new_id in df["المعرف (ID)"].values:
                        st.error("❌ هذا المعرف مسجل مسبقاً!")
                    else:
                        new_row = {
                            "المعرف (ID)": str(new_id), "اسم المعدة": new_name,
                            "التصنيف": new_cat, "الحالة": new_status,
                            "المستلم/الموقع": new_loc, "العدد": new_qty, "الملاحظات": new_notes
                        }
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(df)
                        st.success(f"🎉 تم إضافة ({new_name}) بعدد {new_qty} بنجاح!")
                        st.rerun()

        # ---- رفع من إكسل ----
        elif manage_action == "📥 رفع من ملف إكسل":
            st.markdown("### 📥 رفع وتحديث المخزن من ملف إكسل")

            template_df = pd.DataFrame(columns=[
                "المعرف (ID)", "اسم المعدة", "التصنيف", "الحالة", "المستلم/الموقع", "العدد", "الملاحظات"
            ])
            template_df.loc[0] = ["CAM-01", "كاميرا سوني A7IV", "كاميرات", "متوفر (Available)", "الرف الرئيسي", 1, ""]

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                template_df.to_excel(w, index=False)

            st.download_button(
                label="📥 تحميل النموذج الجاهز",
                data=buf.getvalue(),
                file_name="studio_inventory_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.markdown("---")
            uploaded_file = st.file_uploader("اختر ملف الإكسل:", type=["xlsx"])

            if uploaded_file:
                try:
                    uploaded_df = pd.read_excel(uploaded_file, dtype={"المعرف (ID)": str})
                    uploaded_df["المعرف (ID)"] = uploaded_df["المعرف (ID)"].astype(str).str.strip()
                    required_cols = ["المعرف (ID)", "اسم المعدة", "التصنيف", "الحالة", "المستلم/الموقع"]
                    missing = [c for c in required_cols if c not in uploaded_df.columns]

                    if missing:
                        st.error(f"❌ ينقص الملف هذه الأعمدة: {', '.join(missing)}")
                    else:
                        if "العدد"      not in uploaded_df.columns: uploaded_df["العدد"]      = 1
                        if "الملاحظات" not in uploaded_df.columns: uploaded_df["الملاحظات"] = ""
                        uploaded_df["العدد"]      = uploaded_df["العدد"].fillna(1).astype(int)
                        uploaded_df["الملاحظات"] = uploaded_df["الملاحظات"].fillna("").astype(str)

                        st.markdown("#### 👀 معاينة البيانات:")
                        st.dataframe(uploaded_df, use_container_width=True, hide_index=True)

                        if st.button("تأكيد الدمج في المخزن 💾", type="primary"):
                            uploaded_df = uploaded_df.drop_duplicates(subset=["المعرف (ID)"], keep="last")
                            if not df.empty:
                                df = df[~df["المعرف (ID)"].isin(uploaded_df["المعرف (ID)"])]
                            df = pd.concat([df, uploaded_df], ignore_index=True)
                            save_data(df)
                            st.success(f"🎉 تم استيراد {len(uploaded_df)} قطعة بنجاح!")
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ في معالجة الملف: {str(e)}")

        # ---- تعديل أو حذف ----
        elif manage_action == "✏️ تعديل أو حذف قطعة":
            if df.empty:
                st.info("المخزن فارغ.")
            else:
                item_options    = df["المعرف (ID)"] + " - " + df["اسم المعدة"]
                selected_item   = st.selectbox("اختر القطعة:", item_options)
                selected_id     = selected_item.split(" - ")[0]
                item_data       = df[df["المعرف (ID)"] == selected_id].iloc[0]

                with st.form("edit_item_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name  = st.text_input("اسم المعدة", value=item_data["اسم المعدة"]).strip()
                        edit_cat   = st.selectbox(
                            "التصنيف", categories_list,
                            index=categories_list.index(item_data["التصنيف"]) if item_data["التصنيف"] in categories_list else 0
                        )
                        statuses   = ["متوفر (Available)", "معار (Checked Out)", "في الصيانة (Under Maintenance)"]
                        edit_status = st.selectbox(
                            "الحالة", statuses,
                            index=statuses.index(item_data["الحالة"]) if item_data["الحالة"] in statuses else 0
                        )
                    with col2:
                        edit_loc   = st.text_input("الموقع", value=item_data["المستلم/الموقع"]).strip()
                        edit_qty   = st.number_input("العدد", min_value=1, value=int(item_data.get("العدد", 1)), step=1)
                        edit_notes = st.text_area("الملاحظات", value=str(item_data.get("الملاحظات", ""))).strip()

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        submit_edit   = st.form_submit_button("حفظ التعديلات 💾", type="primary")
                    with col_b2:
                        submit_delete = st.form_submit_button("🗑️ حذف نهائي")

                    if submit_edit:
                        df.loc[df["المعرف (ID)"] == selected_id,
                               ["اسم المعدة", "التصنيف", "الحالة", "المستلم/الموقع", "العدد", "الملاحظات"]
                        ] = [edit_name, edit_cat, edit_status, edit_loc, edit_qty, edit_notes]
                        save_data(df)
                        st.success("✔️ تم تحديث البيانات بنجاح!")
                        st.rerun()

                    if submit_delete:
                        df = df[df["المعرف (ID)"] != selected_id]
                        save_data(df)
                        st.warning("🗑️ تم حذف القطعة.")
                        st.rerun()


# ============================================================
# TAB 3: سحب جديد
# ============================================================
with tab_checkout:
    st.markdown("""
    <div style="background:#eff6ff; border-right:5px solid #1e3a8a; padding:16px; border-radius:8px; margin-bottom:20px;">
        <h3 style="margin:0; color:#1e3a8a; font-family:Cairo,sans-serif;">📤 إصدار عهدة جديدة</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.form("checkout_form"):
        col1, col2 = st.columns(2)
        with col1:
            order_name = st.text_input("🔹 اسم الأوردر / العميل *")
        with col2:
            staff_name = st.text_input("👤 اسم الموظف المسؤول *")

        checkout_notes = st.text_area("📝 ملاحظات")

        available_df    = df[df["الحالة"].str.contains("متوفر", na=False, case=False)].copy()
        available_items = (
            available_df["المعرف (ID)"].astype(str) + " - " +
            available_df["اسم المعدة"].astype(str)
        )

        selected_items = st.multiselect("📦 اختر الأجهزة:", available_items)

        if st.form_submit_button("إصدار العهدة 🚀", type="primary"):
            if not order_name or not staff_name or not selected_items:
                st.error("⚠️ يرجى ملء جميع البيانات واختيار الأجهزة!")
            else:
                selected_ids = [str(item).split(" - ")[0] for item in selected_items]
                loan_id      = f"LN-{len(loans_df) + 1001}"

                new_loan = {
                    "رقم الحركة":      loan_id,
                    "اسم الأوردر":     order_name,
                    "الموظف المستلم":  staff_name,
                    "المعدات المسحوبة": ", ".join(selected_items),
                    "تاريخ السحب":     datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "تاريخ الإرجاع":   "-",
                    "الحالة":          "خارج الاستوديو",
                    "ملاحظات الحركة":  checkout_notes
                }

                loans_df = pd.concat([loans_df, pd.DataFrame([new_loan])], ignore_index=True)
                save_loans(loans_df)

                df.loc[df["المعرف (ID)"].astype(str).isin(selected_ids), "الحالة"] = "معار (Checked Out)"
                save_data(df)

                st.success(f"🎉 تم تسجيل السحب بنجاح! رقم الحركة: **{loan_id}**")
                st.rerun()


# ============================================================
# TAB 4: إرجاع ومطابقة
# ============================================================
with tab_checkin:
    st.markdown("## 📥 نظام مطابقة وإرجاع العهد")

    active_loans = loans_df[loans_df["الحالة"].isin(["خارج الاستوديو", "إرجاع جزئي"])] if not loans_df.empty else pd.DataFrame()

    if active_loans.empty:
        st.success("✅ لا توجد عهد معلقة حالياً.")
    else:
        loan_options     = active_loans["رقم الحركة"] + " | " + active_loans["اسم الأوردر"]
        selected_loan    = st.selectbox("📂 اختر الحركة:", loan_options, key="select_loan_checkin")
        loan_id          = selected_loan.split(" | ")[0]
        row_idx          = active_loans[active_loans["رقم الحركة"] == loan_id].index[0]

        # معلومات الأوردر
        row = loans_df.loc[row_idx]
        st.markdown(f"""
        <div style="background:#f8fafc; border-radius:8px; padding:14px; margin-bottom:16px; border:1px solid #e2e8f0;">
            <b>📋 الأوردر:</b> {row['اسم الأوردر']} &nbsp;|&nbsp;
            <b>👤 الموظف:</b> {row['الموظف المستلم']} &nbsp;|&nbsp;
            <b>📅 تاريخ السحب:</b> {row['تاريخ السحب']}
        </div>
        """, unsafe_allow_html=True)

        current_items = str(loans_df.at[row_idx, "المعدات المسحوبة"]).split(", ")

        st.write("📋 **حدد الأجهزة المستلمة اليوم:**")
        returned_items = []

        with st.container(border=True):
            for item in current_items:
                if "✅ (تم الإرجاع)" not in item:
                    if st.checkbox(f"☑️ {item}", key=f"ret_{loan_id}_{item}"):
                        returned_items.append(item)
                else:
                    st.markdown(f"<span style='color:#16a34a;'>✔️ {item}</span>", unsafe_allow_html=True)

        if st.button("تأكيد الإرجاع 🤝", key="confirm_return_btn", type="primary"):
            if not returned_items:
                st.warning("⚠️ اختر جهازاً واحداً على الأقل!")
            else:
                returned_ids = [str(it.split(" - ")[0]) for it in returned_items]
                df.loc[df["المعرف (ID)"].astype(str).isin(returned_ids), "الحالة"] = "متوفر (Available)"
                save_data(df)

                new_items_list = []
                for item in current_items:
                    if item in returned_items:
                        new_items_list.append(f"{item} ✅ (تم الإرجاع)")
                    else:
                        new_items_list.append(item)

                loans_df.at[row_idx, "المعدات المسحوبة"] = ", ".join(new_items_list)

                if all("✅ (تم الإرجاع)" in it for it in new_items_list):
                    loans_df.at[row_idx, "الحالة"]          = "تم الإرجاع"
                    loans_df.at[row_idx, "تاريخ الإرجاع"]   = datetime.now().strftime("%Y-%m-%d %H:%M")
                else:
                    loans_df.at[row_idx, "الحالة"] = "إرجاع جزئي"

                save_loans(loans_df)
                st.success("🎉 تم تسجيل الإرجاع بنجاح!")
                st.rerun()


# ============================================================
# TAB 5: السجل والأرشيف
# ============================================================
with tab_archive:
    st.markdown("## 📊 سجل الحركات والأرشيف العام")

    if loans_df.empty:
        st.info("لا توجد حركات مسجلة بعد.")
    else:
        # ملخص إحصائي
        c1, c2, c3 = st.columns(3)
        total_l    = len(loans_df)
        done_l     = len(loans_df[loans_df["الحالة"] == "تم الإرجاع"])
        active_l   = len(loans_df[loans_df["الحالة"].isin(["خارج الاستوديو", "إرجاع جزئي"])])
        with c1: st.metric("إجمالي الحركات", total_l)
        with c2: st.metric("مكتملة", done_l)
        with c3: st.metric("نشطة", active_l)

        # فلترة
        status_filter = st.selectbox(
            "تصفية بالحالة:",
            ["الكل", "خارج الاستوديو", "إرجاع جزئي", "تم الإرجاع"]
        )
        show_df = loans_df if status_filter == "الكل" else loans_df[loans_df["الحالة"] == status_filter]
        st.dataframe(show_df, use_container_width=True, hide_index=True)


# ============================================================
# TAB 6: طباعة الوصولات
# ============================================================
with tab_print:
    st.markdown("## 🖨️ نظام استعراض وطباعة وصولات العهدة")

    if loans_df.empty:
        st.info("لا توجد حركات مسجلة.")
    else:
        tab_comp, tab_part, tab_act = st.tabs(["✅ مكتملة", "🔄 إرجاع جزئي", "📦 عهد نشطة"])

        def show_receipt(filtered_df, tab_key):
            if filtered_df.empty:
                st.info("لا توجد حركات في هذه الحالة.")
                return

            display_options = filtered_df["رقم الحركة"].astype(str) + " - " + filtered_df["اسم الأوردر"]
            selected_option = st.selectbox("اختر الحركة:", display_options, key=f"sel_{tab_key}")
            selected_id     = selected_option.split(" - ")[0]
            row             = filtered_df[filtered_df["رقم الحركة"] == selected_id].iloc[0]

            items_list = str(row["المعدات المسحوبة"]).split(", ")
            items_rows = ""
            for i, item in enumerate(items_list, 1):
                part_id   = item.split(" - ")[0]  if " - " in item else "-"
                part_name = item.split(" - ", 1)[1] if " - " in item else item
                items_rows += f"""
                <tr>
                    <td style="padding:10px; text-align:center; border-bottom:1px solid #e2e8f0;">{i}</td>
                    <td style="padding:10px; border-bottom:1px solid #e2e8f0; color:#64748b;">{part_id}</td>
                    <td style="padding:10px; border-bottom:1px solid #e2e8f0; font-weight:600;">{part_name}</td>
                    <td style="padding:10px; border-bottom:1px solid #e2e8f0; min-width:120px;"></td>
                </tr>"""

            notes_block = ""
            if str(row.get("ملاحظات الحركة", "")).strip():
                notes_block = f"<div style='background:#fef3c7; padding:10px; border-radius:6px; margin-bottom:16px;'><b>ملاحظات:</b> {row.get('ملاحظات الحركة','')}</div>"

            # ✅ الوصل + زر الطباعة في نفس الـ iframe → window.print() يطبع الوصل فقط
            full_iframe_html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Cairo', sans-serif; direction: rtl; background: #f8fafc; padding: 16px; }}

  .receipt {{
    border: 2px solid #1e293b; padding: 32px; border-radius: 12px;
    background: #fff; max-width: 780px; margin: auto;
  }}
  .receipt-header {{ text-align: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 20px; }}
  .receipt-header h2 {{ color: #1e293b; font-size: 1.4rem; margin: 8px 0 4px; }}
  .receipt-header p  {{ color: #64748b; font-size: 0.85rem; }}
  .info-grid {{
    background: #f8fafc; border-radius: 8px; padding: 14px; margin-bottom: 18px;
    display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.9rem;
  }}
  .info-grid div {{ min-width: 160px; }}
  .loan-num {{ color: #1e3a8a; font-weight: 700; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
  thead tr {{ background: #1e293b; color: white; }}
  th, td {{ padding: 11px 14px; text-align: right; }}
  th {{ font-size: 0.88rem; }}
  td {{ border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }}
  td:first-child {{ text-align: center; }}
  .sig-row {{ display: flex; justify-content: space-between; padding-top: 20px; border-top: 1px solid #e2e8f0; margin-top: 30px; }}
  .sig-box {{ text-align: center; width: 44%; }}
  .sig-box p {{ color: #64748b; font-size: 0.82rem; margin-bottom: 28px; }}
  .sig-line {{ border-bottom: 1px solid #94a3b8; }}

  /* زر الطباعة - يختفي عند الطباعة */
  .print-btn {{
    display: block; margin: 18px auto 0;
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    color: white; border: none; border-radius: 8px;
    padding: 12px 36px; font-family: 'Cairo', sans-serif;
    font-size: 1rem; font-weight: 700; cursor: pointer;
    box-shadow: 0 4px 12px rgba(30,58,138,0.3);
  }}
  .print-btn:hover {{ opacity: 0.9; }}

  @media print {{
    body {{ background: white; padding: 0; }}
    .receipt {{ border: none; padding: 0; border-radius: 0; }}
    .print-btn {{ display: none !important; }}
  }}
</style>
</head>
<body>
<div class="receipt">

  <div class="receipt-header">
    <div style="font-size:2rem;">🎙️</div>
    <h2>وصل تسليم عهدة</h2>
    <p>نظام إدارة الاستوديو</p>
  </div>

  <div class="info-grid">
    <div><b>رقم الحركة:</b> <span class="loan-num">{row["رقم الحركة"]}</span></div>
    <div><b>العميل / الأوردر:</b> {row["اسم الأوردر"]}</div>
    <div><b>الموظف المستلم:</b> {row["الموظف المستلم"]}</div>
    <div><b>تاريخ السحب:</b> {row["تاريخ السحب"]}</div>
    <div><b>الحالة:</b> {row["الحالة"]}</div>
  </div>

  {notes_block}

  <table>
    <thead>
      <tr>
        <th style="text-align:center; width:40px;">ت</th>
        <th>رقم المعرف</th>
        <th>اسم المعدة</th>
        <th style="min-width:130px;">ملاحظات</th>
      </tr>
    </thead>
    <tbody>{items_rows}</tbody>
  </table>

  <div class="sig-row">
    <div class="sig-box">
      <p>توقيع المستلم</p>
      <div class="sig-line"></div>
    </div>
    <div class="sig-box">
      <p>توقيع المسؤول</p>
      <div class="sig-line"></div>
    </div>
  </div>

</div>

<button class="print-btn" onclick="window.print()">
  🖨️ طباعة وصل {row["رقم الحركة"]}
</button>

</body>
</html>
"""
            components.html(full_iframe_html, height=700, scrolling=True)

        with tab_comp:
            show_receipt(loans_df[loans_df["الحالة"] == "تم الإرجاع"], "complete")
        with tab_part:
            show_receipt(loans_df[loans_df["الحالة"] == "إرجاع جزئي"], "partial")
        with tab_act:
            show_receipt(loans_df[loans_df["الحالة"] == "خارج الاستوديو"], "active")


# ============================================================
# TAB 7: الإعدادات (مدير فقط)
# ============================================================
if tab_settings is not None:
    with tab_settings:
        st.markdown("## ⚙️ إعدادات النظام وإدارة الحسابات")

        # --- إدارة الحسابات ---
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.markdown("### 👤 إنشاء حساب جديد")
            new_user = st.text_input("اسم المستخدم").strip()
            new_pwd  = st.text_input("كلمة السر", type="password").strip()
            user_type = st.selectbox("الصلاحية", ["مستخدم", "مدير"])

            if st.button("إنشاء الحساب 👤", type="primary") and new_user and new_pwd:
                if new_user in users_df["اسم المستخدم"].values:
                    st.error("❌ اسم المستخدم موجود مسبقاً!")
                else:
                    new_row  = {"اسم المستخدم": new_user, "كلمة السر": hash_password(new_pwd), "الصلاحية": user_type}
                    users_df = pd.concat([users_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_users(users_df)
                    st.success("✔️ تم إنشاء الحساب!")
                    st.rerun()

        with col2:
            st.markdown("### 👥 الحسابات الحالية")
            st.dataframe(users_df[["اسم المستخدم", "الصلاحية"]], use_container_width=True, hide_index=True)

        st.markdown("---")

        # --- إدارة التصنيفات ---
        col_c1, col_c2 = st.columns([1, 1.5])
        with col_c1:
            st.markdown("### 🏷️ تصنيفات الأجهزة")
            new_cat = st.text_input("تصنيف جديد:").strip()
            if st.button("إضافة التصنيف 💾") and new_cat:
                if new_cat in categories_list:
                    st.error("❌ التصنيف موجود!")
                else:
                    categories_list.append(new_cat)
                    save_categories(categories_list)
                    st.success(f"✔️ تمت إضافة '{new_cat}'")
                    st.rerun()

            st.markdown("##### حذف تصنيف")
            cat_del = st.selectbox("اختر للحذف:", categories_list)
            if st.button("حذف التصنيف 🗑️"):
                if len(categories_list) <= 1:
                    st.error("⚠️ يجب إبقاء تصنيف واحد!")
                else:
                    categories_list.remove(cat_del)
                    save_categories(categories_list)
                    st.warning(f"تم حذف '{cat_del}'")
                    st.rerun()

        with col_c2:
            st.markdown("### 📊 التصنيفات المتاحة")
            st.dataframe(
                pd.DataFrame({"التصنيفات": categories_list}),
                use_container_width=True, hide_index=True
            )
