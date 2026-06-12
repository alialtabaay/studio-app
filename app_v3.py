import streamlit as st
import json
import os
import hashlib
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="نظام إدارة الاستوديو", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, .stApp {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
LOANS_FILE = os.path.join(DATA_DIR, "loans.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"admin": {"password": hash_password("1234"), "role": "مدير"}}

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
    return ["كاميرات", "عدسات", "إضاءة", "صوتيات", "ملحقات"]

def save_categories(categories):
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

for key, val in [("logged_in", False), ("username", ""), ("role", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

users = load_users()

if not st.session_state["logged_in"]:
    st.markdown("""
    <div style="text-align:center; padding: 60px 0 30px;">
        <div style="font-size:3.5rem;">🎙️</div>
        <h1 style="color:#1e3a8a; font-family:'Cairo',sans-serif; margin:10px 0;">نظام إدارة الاستوديو</h1>
        <p style="color:#64748b; font-family:'Cairo',sans-serif;">إدارة متطورة للمخزن والإعارات</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form_main"):
            st.markdown("<h3 style='text-align:center; font-family:Cairo,sans-serif; color:#1e3a8a;'>🔒 تسجيل الدخول</h3>", unsafe_allow_html=True)
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
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['username']}")
        st.markdown(f"**الصلاحية:** {st.session_state['role']}")
        st.divider()
        
        if st.button("🚪 تسجيل خروج", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["role"] = ""
            st.rerun()

    tabs = ["📊 لوحة التحكم", "📦 المخزن", "📋 الإعارات", "⚙️ الإعدادات"]
    tab1, tab2, tab3, tab4 = st.tabs(tabs)

    # ============ TAB 1: لوحة التحكم ============
    with tab1:
        st.markdown("## 📊 لوحة التحكم")
        inventory = load_inventory()
        loans = load_loans()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔢 إجمالي المعدات", len(inventory))
        with col2:
            available = sum(1 for i in inventory.values() if i.get('status') == 'متوفر')
            st.metric("🟢 متوفرة", available)
        with col3:
            loaned = sum(1 for i in inventory.values() if i.get('status') == 'معار')
            st.metric("🟡 معارة", loaned)
        with col4:
            maintenance = sum(1 for i in inventory.values() if i.get('status') == 'صيانة')
            st.metric("🔴 صيانة", maintenance)
        
        st.divider()
        
        st.markdown("## 📋 جدول جميع المعدات")
        if inventory:
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 ابحث...")
            with col2:
                filter_status = st.selectbox("تصفية بالحالة", ["الكل", "متوفر", "معار", "صيانة"], key="dash_status")
            with col3:
                categories = load_categories()
                filter_cat = st.selectbox("تصفية بالتصنيف", ["الكل"] + categories, key="dash_cat")
            
            table_data = []
            for item_id, item in inventory.items():
                if search and search.lower() not in item_id.lower() and search.lower() not in item['name'].lower():
                    continue
                if filter_status != "الكل" and item['status'] != filter_status:
                    continue
                if filter_cat != "الكل" and item.get('category') != filter_cat:
                    continue
                
                status_emoji = "🟢" if item['status'] == 'متوفر' else "🟡" if item['status'] == 'معار' else "🔴"
                table_data.append({
                    "🆔 المعرف": item_id,
                    "📦 الاسم": item['name'],
                    "🏷️ التصنيف": item.get('category', '-'),
                    "📍 الموقع": item.get('location', '-'),
                    "📊 الحالة": f"{status_emoji} {item['status']}",
                })
            
            if table_data:
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, height=400, hide_index=True)
        else:
            st.info("📭 لا توجد معدات")

    # ============ TAB 2: المخزن ============
    with tab2:
        st.markdown("## 📦 إدارة المخزن")
        inventory = load_inventory()
        categories = load_categories()
        
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["➕ إضافة", "📊 رفع Excel", "✏️ تعديل"])
        
        # ===== إضافة =====
        with sub_tab1:
            st.markdown("### ➕ إضافة معدة جديدة")
            
            col1, col2 = st.columns(2)
            with col1:
                add_id = st.text_input("🆔 المعرف", placeholder="CAM-001", key="form_id_1")
                add_name = st.text_input("📦 الاسم", placeholder="الاسم", key="form_name_1")
                add_category = st.selectbox("🏷️ التصنيف", categories, key="form_cat_1")
            
            with col2:
                add_status = st.selectbox("📊 الحالة", ["متوفر", "معار", "صيانة"], key="form_stat_1")
                add_location = st.text_input("📍 الموقع", placeholder="الرف", key="form_loc_1")
                add_notes = st.text_area("📝 ملاحظات", height=80, key="form_note_1")
            
            if st.button("💾 حفظ المعدة", use_container_width=True, type="primary", key="btn_save_1"):
                if not add_id or not add_name:
                    st.error("❌ املأ الحقول المطلوبة!")
                elif add_id in inventory:
                    st.error(f"❌ المعرف '{add_id}' موجود!")
                else:
                    inventory[add_id] = {
                        "name": add_name,
                        "category": add_category,
                        "status": add_status,
                        "location": add_location,
                        "notes": add_notes,
                        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    save_inventory(inventory)
                    st.success(f"✅ تم حفظ: **{add_name}**")
                    st.balloons()
        
        # ===== رفع Excel =====
        with sub_tab2:
            st.markdown("### 📊 رفع من Excel/CSV")
            
            col1, col2 = st.columns(2)
            with col1:
                template_data = {"المعرف": ["CAM-001"], "الاسم": ["كاميرا"], "التصنيف": ["كاميرات"], "الحالة": ["متوفر"], "الموقع": ["الرف"], "ملاحظات": ["-"]}
                template_df = pd.DataFrame(template_data)
                st.download_button("📥 تحميل قالب", template_df.to_csv(index=False, encoding='utf-8-sig'), "قالب.csv", "text/csv", use_container_width=True)
            
            with col2:
                uploaded = st.file_uploader("📤 اختر ملف", type=['csv', 'xlsx', 'xls'], key="upload_inv")
            
            if uploaded:
                try:
                    if uploaded.name.endswith('csv'):
                        df = pd.read_csv(uploaded, encoding='utf-8')
                    else:
                        df = pd.read_excel(uploaded)
                    
                    st.dataframe(df, use_container_width=True)
                    
                    cols = df.columns.tolist()
                    st.markdown("### مطابقة الأعمدة")
                    
                    col_map = {}
                    for req in ['المعرف', 'الاسم', 'التصنيف', 'الحالة', 'الموقع', 'ملاحظات']:
                        col_map[req] = st.selectbox(f"اختر {req}", cols, key=f"map_{req}")
                    
                    if st.button("✅ استيراد", use_container_width=True, type="primary", key="btn_import_1"):
                        count = 0
                        for _, row in df.iterrows():
                            item_id = str(row[col_map['المعرف']]).strip()
                            item_name = str(row[col_map['الاسم']]).strip()
                            if item_id and item_name and item_id != 'nan':
                                inventory[item_id] = {
                                    "name": item_name,
                                    "category": str(row[col_map['التصنيف']]) if pd.notna(row[col_map['التصنيف']]) else '-',
                                    "status": str(row[col_map['الحالة']]) if pd.notna(row[col_map['الحالة']]) else 'متوفر',
                                    "location": str(row[col_map['الموقع']]) if pd.notna(row[col_map['الموقع']]) else '-',
                                    "notes": str(row[col_map['ملاحظات']]) if pd.notna(row[col_map['ملاحظات']]) else '-',
                                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                                }
                                count += 1
                        save_inventory(inventory)
                        st.success(f"✅ تم استيراد {count} معدة!")
                except Exception as e:
                    st.error(f"❌ خطأ: {str(e)}")
        
        # ===== تعديل =====
        with sub_tab3:
            st.markdown("### ✏️ تعديل معدة")
            
            if inventory:
                selected = st.selectbox("اختر المعدة", list(inventory.keys()), format_func=lambda x: f"{inventory[x]['name']} ({x})", key="edit_select_1")
                current = inventory[selected]
                
                col1, col2 = st.columns(2)
                with col1:
                    edit_id = st.text_input("🆔 المعرف", value=selected, key="edit_id_1")
                    edit_name = st.text_input("📦 الاسم", value=current['name'], key="edit_name_1")
                    edit_cat = st.selectbox("🏷️ التصنيف", categories, index=categories.index(current.get('category', categories[0])), key="edit_cat_1")
                
                with col2:
                    edit_stat = st.selectbox("📊 الحالة", ["متوفر", "معار", "صيانة"], index=["متوفر", "معار", "صيانة"].index(current.get('status', 'متوفر')), key="edit_stat_1")
                    edit_loc = st.text_input("📍 الموقع", value=current.get('location', ''), key="edit_loc_1")
                    edit_note = st.text_area("📝 ملاحظات", value=current.get('notes', ''), height=80, key="edit_note_1")
                
                if st.button("💾 حفظ التعديلات", use_container_width=True, type="primary", key="btn_edit_1"):
                    if not edit_id or not edit_name:
                        st.error("❌ املأ الحقول!")
                    elif edit_id != selected and edit_id in inventory:
                        st.error(f"❌ المعرف موجود!")
                    else:
                        if edit_id != selected:
                            del inventory[selected]
                        inventory[edit_id] = {
                            "name": edit_name,
                            "category": edit_cat,
                            "status": edit_stat,
                            "location": edit_loc,
                            "notes": edit_note,
                            "date_added": current.get('date_added', datetime.now().strftime("%Y-%m-%d %H:%M"))
                        }
                        save_inventory(inventory)
                        st.success("✅ تم التعديل!")
                        st.rerun()
            else:
                st.info("📭 لا توجد معدات")

    # ============ TAB 3: الإعارات ============
    with tab3:
        st.markdown("## 📋 الإعارات")
        loans = load_loans()
        inventory = load_inventory()
        
        sub_loan1, sub_loan2 = st.tabs(["📤 سحب", "📥 إرجاع"])
        
        with sub_loan1:
            if inventory:
                available = {k: v for k, v in inventory.items() if v['status'] == 'متوفر'}
                if available:
                    col1, col2 = st.columns(2)
                    with col1:
                        item = st.selectbox("اختر المعدة", list(available.keys()), format_func=lambda x: available[x]['name'], key="loan_item_1")
                        customer = st.text_input("اسم العميل", key="loan_cust_1")
                    with col2:
                        employee = st.text_input("الموظف", key="loan_emp_1")
                        ret_date = st.date_input("تاريخ الإرجاع", value=datetime.now().date() + timedelta(days=7), key="loan_date_1")
                    
                    if st.button("✅ تسجيل السحب", use_container_width=True, type="primary", key="btn_loan_1"):
                        if customer and employee:
                            loan_id = f"LOAN-{len(loans)+1:05d}"
                            loans[loan_id] = {
                                "item_id": item,
                                "item_name": available[item]['name'],
                                "customer": customer,
                                "employee": employee,
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "return_date": ret_date.strftime("%Y-%m-%d"),
                                "status": "نشطة"
                            }
                            save_loans(loans)
                            inventory[item]['status'] = 'معار'
                            save_inventory(inventory)
                            st.success(f"✅ {loan_id}")
                        else:
                            st.error("❌ املأ الحقول!")
        
        with sub_loan2:
            active = {k: v for k, v in loans.items() if v['status'] == 'نشطة'}
            if active:
                selected_loan = st.selectbox("اختر الإعارة", list(active.keys()), format_func=lambda x: f"{x} - {active[x]['customer']}", key="return_loan_1")
                
                if st.button("✅ إرجاع", use_container_width=True, type="primary", key="btn_return_1"):
                    loans[selected_loan]['status'] = 'مرجعة'
                    loans[selected_loan]['actual_return_date'] = datetime.now().strftime("%Y-%m-%d")
                    save_loans(loans)
                    item_id = loans[selected_loan]['item_id']
                    inventory[item_id]['status'] = 'متوفر'
                    save_inventory(inventory)
                    st.success("✅ تم الإرجاع!")
                    st.rerun()
            else:
                st.info("✅ لا توجد إعارات نشطة")

    # ============ TAB 4: الإعدادات ============
    with tab4:
        if st.session_state["role"] == "مدير":
            st.markdown("## ⚙️ الإعدادات")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 👥 إنشاء حساب")
                new_user = st.text_input("اسم المستخدم", key="new_user_1")
                new_pwd = st.text_input("كلمة السر", type="password", key="new_pwd_1")
                
                if st.button("➕ إنشاء", use_container_width=True, key="btn_create_user_1"):
                    if new_user and new_pwd:
                        if new_user not in users:
                            users[new_user] = {"password": hash_password(new_pwd), "role": "مستخدم"}
                            save_users(users)
                            st.success(f"✅ تم إنشاء: {new_user}")
                        else:
                            st.error("❌ المستخدم موجود!")
            
            with col2:
                st.markdown("### 👤 الحسابات")
                for username, data in users.items():
                    st.write(f"👤 {username} - {data['role']}")
        else:
            st.warning("⚠️ صلاحيات مدير فقط")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>نظام إدارة الاستوديو v4.0 ✨</p>", unsafe_allow_html=True)
