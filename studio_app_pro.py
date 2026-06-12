import streamlit as st
import json
import os
import hashlib
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ============================================================
# إعدادات الصفحة
# ============================================================
st.set_page_config(page_title="نظام جرد وإعارات الاستوديو", layout="wide", page_icon="🎙️")

# ============================================================
# تنسيق CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    html, body, .stApp {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
    }

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

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        border: none;
        border-radius: 8px;
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
        padding: 10px 24px;
    }

    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-top: 4px solid #3b82f6;
    }

    .stat-number { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .stat-label  { font-size: 0.9rem; color: #64748b; margin: 4px 0 0; }
    
    .receipt {
        background: white;
        border: 2px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# المسارات وملفات البيانات
# ============================================================
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
LOANS_FILE = os.path.join(DATA_DIR, "loans.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")

# ============================================================
# دوال مساعدة
# ============================================================
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "admin": {
            "password": hash_password("1234"),
            "role": "مدير"
        }
    }

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_inventory(inventory):
    with open(INVENTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

def load_loans():
    if os.path.exists(LOANS_FILE):
        with open(LOANS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_loans(loans):
    with open(LOANS_FILE, 'w', encoding='utf-8') as f:
        json.dump(loans, f, ensure_ascii=False, indent=2)

def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return ["كاميرات", "عدسات", "إضاءة", "صوتيات", "ملحقات أخرى"]

def save_categories(categories):
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

def generate_receipt(loan_id, loan_data, inventory):
    """توليد وصل التسليم"""
    item_name = inventory.get(loan_data.get('item_id'), {}).get('name', 'معدة غير محددة')
    
    html = f"""
    <div class="receipt">
        <div style="text-align:center; margin-bottom:20px;">
            <h2 style="margin:0;">🎙️ وصل تسليم عهدة</h2>
            <p style="color:#64748b;">نظام إدارة الاستوديو</p>
        </div>
        
        <div style="background:#f8fafc; padding:15px; border-radius:8px; margin-bottom:20px;">
            <p><b>رقم الحركة:</b> {loan_id}</p>
            <p><b>العميل/الأوردر:</b> {loan_data.get('customer', 'غير محدد')}</p>
            <p><b>الموظف المستلم:</b> {loan_data.get('employee', 'غير محدد')}</p>
            <p><b>تاريخ السحب:</b> {loan_data.get('date', 'غير محدد')}</p>
            <p><b>تاريخ الإرجاع المتوقع:</b> {loan_data.get('return_date', 'غير محدد')}</p>
        </div>
        
        <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
            <tr style="background:#1e293b; color:white;">
                <th style="padding:10px; text-align:right;">اسم المعدة</th>
                <th style="padding:10px; text-align:right;">المعرف</th>
                <th style="padding:10px; text-align:right;">الحالة</th>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
                <td style="padding:10px;">{item_name}</td>
                <td style="padding:10px;">{loan_data.get('item_id', 'غير محدد')}</td>
                <td style="padding:10px;">{loan_data.get('status', 'نشطة')}</td>
            </tr>
        </table>
        
        <div style="margin-top:30px; border-top:1px solid #e2e8f0; padding-top:20px;">
            <div style="display:flex; justify-content:space-between;">
                <div style="text-align:center; width:45%;">
                    <p style="color:#64748b; margin-bottom:20px;">توقيع المستقبل</p>
                    <div style="border-bottom:1px solid #94a3b8; height:40px;"></div>
                </div>
                <div style="text-align:center; width:45%;">
                    <p style="color:#64748b; margin-bottom:20px;">توقيع المسؤول</p>
                    <div style="border-bottom:1px solid #94a3b8; height:40px;"></div>
                </div>
            </div>
        </div>
    </div>
    """
    return html

# ============================================================
# إدارة الجلسة
# ============================================================
for key, val in [("logged_in", False), ("username", ""), ("role", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

users = load_users()

# ============================================================
# واجهة تسجيل الدخول
# ============================================================
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
            username = st.text_input("اسم المستخدم").strip()
            password = st.text_input("كلمة السر", type="password").strip()
            submit = st.form_submit_button("دخول ✓", use_container_width=True, type="primary")

            if submit:
                if username in users and users[username]["password"] == hash_password(password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = users[username]["role"]
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة السر غير صحيحة!")

else:
    # ============================================================
    # القائمة الجانبية
    # ============================================================
    with st.sidebar:
        st.markdown(f"### 👤 مرحباً {st.session_state['username']}")
        st.markdown(f"**الصلاحية:** {st.session_state['role']}")
        
        if st.button("🚪 تسجيل خروج", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["role"] = ""
            st.rerun()

    # ============================================================
    # التبويبات الرئيسية
    # ============================================================
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 لوحة التحكم",
        "📦 المخزن",
        "📋 الإعارات",
        "📈 التقارير",
        "🔍 البحث",
        "🖨️ الوصولات",
        "⚙️ الإعدادات"
    ])

    # ============================================================
    # TAB 1: لوحة التحكم
    # ============================================================
    with tab1:
        st.markdown("## 📊 لوحة التحكم")
        inventory = load_inventory()
        loans = load_loans()
        
        # الإحصائيات
        total_items = len(inventory)
        active_loans = sum(1 for l in loans.values() if l.get('status') == 'نشطة')
        available_items = sum(1 for i in inventory.values() if i.get('status') == 'متوفر')
        maintenance_items = sum(1 for i in inventory.values() if i.get('status') == 'صيانة')
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total_items}</div>
                <div class="stat-label">إجمالي المعدات</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color:#3b82f6;">{available_items}</div>
                <div class="stat-label">متوفرة</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color:#f59e0b;">{active_loans}</div>
                <div class="stat-label">معارة حالياً</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color:#ef4444;">{maintenance_items}</div>
                <div class="stat-label">قيد الصيانة</div>
            </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # TAB 2: إدارة المخزن
    # ============================================================
    with tab2:
        st.markdown("## 📦 إدارة المخزن")
        inventory = load_inventory()
        categories = load_categories()
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### إضافة معدة جديدة")
            item_id = st.text_input("معرف المعدة (ID)")
            item_name = st.text_input("اسم المعدة")
            item_category = st.selectbox("التصنيف", categories)
            item_status = st.selectbox("الحالة", ["متوفر", "معار", "صيانة", "خارج"])
            item_location = st.text_input("الموقع/المالك")
            item_notes = st.text_area("ملاحظات")
            
            if st.button("حفظ المعدة ✓", use_container_width=True, type="primary"):
                if item_id and item_name:
                    inventory[item_id] = {
                        "name": item_name,
                        "category": item_category,
                        "status": item_status,
                        "location": item_location,
                        "notes": item_notes,
                        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    save_inventory(inventory)
                    st.success("✅ تم حفظ المعدة!")
                    st.rerun()
                else:
                    st.error("❌ يرجى ملء الحقول المطلوبة!")
        
        with col2:
            st.markdown("### إحصائيات المخزن")
            st.metric("إجمالي المعدات", len(inventory))
            st.metric("متوفرة", sum(1 for i in inventory.values() if i.get('status') == 'متوفر'))
            st.metric("معارة", sum(1 for i in inventory.values() if i.get('status') == 'معار'))

        st.markdown("### المعدات المسجلة")
        if inventory:
            for item_id, item_data in inventory.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{item_data['name']}** ({item_id})")
                    st.write(f"📂 {item_data.get('category', 'بدون تصنيف')}")
                with col2:
                    status_color = "🟢" if item_data['status'] == 'متوفر' else "🟡" if item_data['status'] == 'معار' else "🔴"
                    st.write(f"{status_color} {item_data['status']}")
                with col3:
                    if st.button("🗑️ حذف", key=f"del_{item_id}"):
                        del inventory[item_id]
                        save_inventory(inventory)
                        st.rerun()
                st.divider()
        else:
            st.info("لا توجد معدات مسجلة")

    # ============================================================
    # TAB 3: نظام الإعارات
    # ============================================================
    with tab3:
        st.markdown("## 📋 نظام الإعارات")
        loans = load_loans()
        inventory = load_inventory()
        
        tab_checkout, tab_return, tab_active = st.tabs(["📤 سحب معدة", "📥 إرجاع معدة", "📦 الإعارات النشطة"])
        
        with tab_checkout:
            st.markdown("### سحب معدة جديدة")
            if inventory:
                col1, col2 = st.columns(2)
                with col1:
                    item_to_loan = st.selectbox("اختر المعدة", list(inventory.keys()), format_func=lambda x: f"{inventory[x]['name']} ({x})")
                    customer_name = st.text_input("اسم العميل/الأوردر")
                    employee_name = st.text_input("الموظف المستقبل")
                with col2:
                    return_date = st.date_input("تاريخ الإرجاع المتوقع")
                    notes = st.text_area("ملاحظات")
                
                if st.button("تأكيد السحب ✓", use_container_width=True, type="primary"):
                    if customer_name and employee_name:
                        loan_id = f"LOAN-{len(loans)+1:04d}"
                        loans[loan_id] = {
                            "item_id": item_to_loan,
                            "customer": customer_name,
                            "employee": employee_name,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "return_date": return_date.strftime("%Y-%m-%d"),
                            "status": "نشطة",
                            "notes": notes
                        }
                        save_loans(loans)
                        
                        # تحديث حالة المعدة
                        inventory[item_to_loan]['status'] = 'معار'
                        save_inventory(inventory)
                        
                        st.success(f"✅ تم تسجيل الإعارة! (رقم: {loan_id})")
                        st.rerun()
                    else:
                        st.error("❌ يرجى ملء جميع الحقول!")
            else:
                st.info("لا توجد معدات متوفرة للسحب")
        
        with tab_return:
            st.markdown("### إرجاع معدة")
            active_loans = {k: v for k, v in loans.items() if v.get('status') == 'نشطة'}
            if active_loans:
                loan_to_return = st.selectbox("اختر الإعارة", list(active_loans.keys()), format_func=lambda x: f"{x} - {active_loans[x]['customer']}")
                return_notes = st.text_area("ملاحظات الإرجاع")
                
                if st.button("تأكيد الإرجاع ✓", use_container_width=True, type="primary"):
                    item_id = loans[loan_to_return]['item_id']
                    loans[loan_to_return]['status'] = 'مرجعة'
                    loans[loan_to_return]['return_notes'] = return_notes
                    save_loans(loans)
                    
                    # تحديث حالة المعدة
                    inventory[item_id]['status'] = 'متوفر'
                    save_inventory(inventory)
                    
                    st.success("✅ تم تسجيل الإرجاع!")
                    st.rerun()
            else:
                st.info("لا توجد إعارات نشطة")
        
        with tab_active:
            st.markdown("### الإعارات النشطة")
            active_loans = {k: v for k, v in loans.items() if v.get('status') == 'نشطة'}
            if active_loans:
                for loan_id, loan_data in active_loans.items():
                    st.write(f"**{loan_id}** - {loan_data['customer']}")
                    st.write(f"📦 المعدة: {inventory.get(loan_data['item_id'], {}).get('name', 'غير محددة')}")
                    st.write(f"👤 الموظف: {loan_data['employee']}")
                    st.write(f"📅 تاريخ الإرجاع: {loan_data.get('return_date', 'غير محدد')}")
                    st.divider()
            else:
                st.info("لا توجد إعارات نشطة حالياً")

    # ============================================================
    # TAB 4: التقارير والإحصائيات
    # ============================================================
    with tab4:
        st.markdown("## 📈 التقارير والإحصائيات")
        inventory = load_inventory()
        loans = load_loans()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # توزيع الحالات
            statuses = {}
            for item in inventory.values():
                status = item.get('status', 'غير محدد')
                statuses[status] = statuses.get(status, 0) + 1
            
            if statuses:
                fig = go.Figure(data=[go.Pie(
                    labels=list(statuses.keys()),
                    values=list(statuses.values()),
                    hoverinfo='label+percent'
                )])
                fig.update_layout(title="توزيع المعدات حسب الحالة", direction='rtl')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # توزيع التصنيفات
            categories_count = {}
            for item in inventory.values():
                cat = item.get('category', 'بدون تصنيف')
                categories_count[cat] = categories_count.get(cat, 0) + 1
            
            if categories_count:
                fig = go.Figure(data=[go.Bar(
                    x=list(categories_count.keys()),
                    y=list(categories_count.values()),
                    marker_color='#3b82f6'
                )])
                fig.update_layout(title="توزيع المعدات حسب التصنيف", xaxis_title="التصنيف", yaxis_title="العدد", direction='rtl')
                st.plotly_chart(fig, use_container_width=True)
        
        # إحصائيات الإعارات
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي الإعارات", len(loans))
        with col2:
            active = sum(1 for l in loans.values() if l.get('status') == 'نشطة')
            st.metric("إعارات نشطة", active)
        with col3:
            returned = sum(1 for l in loans.values() if l.get('status') == 'مرجعة')
            st.metric("إعارات مرجعة", returned)

    # ============================================================
    # TAB 5: البحث والتتبع
    # ============================================================
    with tab5:
        st.markdown("## 🔍 البحث والتتبع")
        inventory = load_inventory()
        loans = load_loans()
        
        search_term = st.text_input("ابحث عن معدة أو إعارة").strip()
        
        if search_term:
            st.markdown("### نتائج البحث")
            
            # البحث في المعدات
            found_items = {k: v for k, v in inventory.items() if search_term.lower() in k.lower() or search_term.lower() in v['name'].lower()}
            if found_items:
                st.markdown("**المعدات:**")
                for item_id, item_data in found_items.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{item_data['name']}** ({item_id})")
                        st.write(f"التصنيف: {item_data.get('category', 'بدون')}")
                        st.write(f"الموقع: {item_data.get('location', 'غير محدد')}")
                    with col2:
                        status_color = "🟢" if item_data['status'] == 'متوفر' else "🟡" if item_data['status'] == 'معار' else "🔴"
                        st.write(f"{status_color} {item_data['status']}")
                    st.divider()
            
            # البحث في الإعارات
            found_loans = {k: v for k, v in loans.items() if search_term.lower() in k.lower() or search_term.lower() in v['customer'].lower()}
            if found_loans:
                st.markdown("**الإعارات:**")
                for loan_id, loan_data in found_loans.items():
                    st.write(f"**{loan_id}** - {loan_data['customer']}")
                    st.write(f"المعدة: {inventory.get(loan_data['item_id'], {}).get('name', 'غير محددة')}")
                    st.write(f"الحالة: {loan_data['status']}")
                    st.divider()
            
            if not found_items and not found_loans:
                st.info("لم يتم العثور على نتائج")
        else:
            st.info("أدخل كلمة البحث أعلاه")

    # ============================================================
    # TAB 6: طباعة الوصولات
    # ============================================================
    with tab6:
        st.markdown("## 🖨️ طباعة الوصولات")
        loans = load_loans()
        inventory = load_inventory()
        
        if loans:
            loan_id = st.selectbox("اختر الإعارة", list(loans.keys()), format_func=lambda x: f"{x} - {loans[x]['customer']}")
            
            if loan_id:
                loan_data = loans[loan_id]
                
                # عرض الوصل
                st.markdown(generate_receipt(loan_id, loan_data, inventory), unsafe_allow_html=True)
                
                # زر الطباعة
                st.markdown("""
                <script>
                function printReceipt() {
                    window.print();
                }
                </script>
                """, unsafe_allow_html=True)
                
                if st.button("🖨️ طباعة الوصل", use_container_width=True):
                    st.info("استخدم Ctrl+P أو أيقونة الطباعة في المتصفح")
        else:
            st.info("لا توجد إعارات للطباعة")

    # ============================================================
    # TAB 7: الإعدادات (مدير فقط)
    # ============================================================
    if st.session_state["role"] == "مدير":
        with tab7:
            st.markdown("## ⚙️ الإعدادات والحسابات")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### إنشاء حساب جديد")
                new_user = st.text_input("اسم المستخدم الجديد").strip()
                new_pwd = st.text_input("كلمة السر", type="password").strip()
                user_role = st.selectbox("الصلاحية", ["مستخدم", "مدير"])
                
                if st.button("إنشاء الحساب ✓", use_container_width=True, type="primary"):
                    if new_user and new_pwd:
                        if new_user not in users:
                            users[new_user] = {
                                "password": hash_password(new_pwd),
                                "role": user_role
                            }
                            save_users(users)
                            st.success("✅ تم إنشاء الحساب!")
                        else:
                            st.error("❌ اسم المستخدم موجود!")
                    else:
                        st.error("❌ يرجى ملء جميع الحقول!")
            
            with col2:
                st.markdown("### الحسابات الحالية")
                for username, user_data in users.items():
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"👤 **{username}** - {user_data['role']}")
                    with col2:
                        if username != st.session_state['username']:
                            if st.button("🗑️", key=f"del_user_{username}"):
                                del users[username]
                                save_users(users)
                                st.rerun()
            
            st.markdown("---")
            
            # إدارة التصنيفات
            st.markdown("### 🏷️ التصنيفات")
            categories = load_categories()
            
            col1, col2 = st.columns([2, 1])
            with col1:
                new_category = st.text_input("تصنيف جديد")
                if st.button("إضافة تصنيف ✓", use_container_width=True):
                    if new_category and new_category not in categories:
                        categories.append(new_category)
                        save_categories(categories)
                        st.success("✅ تمت الإضافة!")
                        st.rerun()
            
            with col2:
                st.markdown("### التصنيفات الموجودة")
                for i, cat in enumerate(categories):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(cat)
                    with col2:
                        if st.button("🗑️", key=f"del_cat_{i}"):
                            categories.pop(i)
                            save_categories(categories)
                            st.rerun()

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b; font-size:0.8rem;'>نظام إدارة الاستوديو v2.0 | مع دعم التقارير والبحث والوصولات</p>", unsafe_allow_html=True)
