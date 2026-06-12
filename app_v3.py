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
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stat-number { font-size: 2rem; font-weight: 700; }
    .stat-label { font-size: 0.9rem; opacity: 0.9; }
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
        with st.form("login_form"):
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

    tabs = ["📊 لوحة التحكم", "📦 المخزن", "📋 الإعارات", "🔍 البحث", "📈 التقارير", "⚙️ الإعدادات"]
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tabs)

    # ============ TAB 1: لوحة التحكم ============
    with tab1:
        st.markdown("## 📊 لوحة التحكم")
        inventory = load_inventory()
        loans = load_loans()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(inventory)}</div>
                <div class="stat-label">إجمالي المعدات</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            available = sum(1 for i in inventory.values() if i.get('status') == 'متوفر')
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="stat-number">{available}</div>
                <div class="stat-label">متوفرة</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            loaned = sum(1 for i in inventory.values() if i.get('status') == 'معار')
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="stat-number">{loaned}</div>
                <div class="stat-label">معارة حالياً</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            maintenance = sum(1 for i in inventory.values() if i.get('status') == 'صيانة')
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <div class="stat-number">{maintenance}</div>
                <div class="stat-label">قيد الصيانة</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📅 الإعارات المنتهية صلاحيتها")
            today = datetime.now().date()
            overdue = {k: v for k, v in loans.items() 
                    if v.get('status') == 'نشطة' and datetime.strptime(v.get('return_date', '2099-12-31'), '%Y-%m-%d').date() < today}
            
            if overdue:
                for loan_id, data in overdue.items():
                    st.warning(f"⚠️ **{loan_id}** - {data['customer']}")
                    st.caption(f"كان يجب إرجاعها: {data.get('return_date')}")
            else:
                st.success("✅ لا توجد إعارات متأخرة")
        
        with col2:
            st.markdown("### 🔔 ملخص سريع")
            active_loans = sum(1 for l in loans.values() if l.get('status') == 'نشطة')
            returned_loans = sum(1 for l in loans.values() if l.get('status') == 'مرجعة')
            st.metric("إعارات نشطة", active_loans)
            st.metric("إعارات مرجعة", returned_loans)
        
        st.divider()
        
        # ============ جدول المعدات الشامل ============
        st.markdown("## 📋 جدول جميع المعدات")
        
        if inventory:
            # فلتر
            col1, col2, col3 = st.columns(3)
            with col1:
                search_item = st.text_input("🔍 ابحث بالاسم أو المعرف...")
            with col2:
                filter_status = st.selectbox("تصفية بالحالة", ["الكل", "متوفر", "معار", "صيانة", "خارج الخدمة"])
            with col3:
                filter_category = st.selectbox("تصفية بالتصنيف", ["الكل"] + load_categories())
            
            # إعداد البيانات
            table_data = []
            for item_id, item in inventory.items():
                # تطبيق الفلاتر
                if search_item and search_item.lower() not in item_id.lower() and search_item.lower() not in item['name'].lower():
                    continue
                if filter_status != "الكل" and item['status'] != filter_status:
                    continue
                if filter_category != "الكل" and item.get('category') != filter_category:
                    continue
                
                # أيقونة الحالة
                status_emoji = "🟢" if item['status'] == 'متوفر' else "🟡" if item['status'] == 'معار' else "🔴"
                
                table_data.append({
                    "🆔 المعرف": item_id,
                    "📦 الاسم": item['name'],
                    "🏷️ التصنيف": item.get('category', '-'),
                    "📍 الموقع": item.get('location', '-'),
                    "📊 الحالة": f"{status_emoji} {item['status']}",
                    "📅 تاريخ الإضافة": item.get('date_added', '-'),
                    "📝 ملاحظات": item.get('notes', '-')
                })
            
            if table_data:
                df = pd.DataFrame(table_data)
                
                # عرض الجدول
                st.dataframe(
                    df,
                    use_container_width=True,
                    height=400,
                    hide_index=True,
                    column_config={
                        "🆔 المعرف": st.column_config.TextColumn(width="small"),
                        "📦 الاسم": st.column_config.TextColumn(width="medium"),
                        "📊 الحالة": st.column_config.TextColumn(width="small"),
                    }
                )
                
                # إحصائيات الفلتر
                st.caption(f"✅ عدد المعدات المعروضة: **{len(table_data)}** من **{len(inventory)}**")
                
                # تحميل الجدول
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 تحميل الجدول (CSV)",
                    data=csv,
                    file_name=f"equipment_list_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("❌ لم يتم العثور على معدات تطابق الفلاتر")
        else:
            st.info("📭 لا توجد معدات مسجلة")

    # ============ TAB 2: إدارة المخزن ============
    with tab2:
        st.markdown("## 📦 إدارة المخزن")
        inventory = load_inventory()
        categories = load_categories()
        
        # تبويبات فرعية
        tab_add_manual, tab_add_excel, tab_edit = st.tabs(["➕ إضافة يدوي", "📊 رفع من Excel", "✏️ تعديل المعدات"])
        
        # ============ TAB: إضافة يدوي ============
        with tab_add_manual:
            st.markdown("### ➕ إضافة معدة جديدة")
            
            with st.form("add_item_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    item_id = st.text_input("🆔 معرف المعدة (ID)", placeholder="مثال: CAM-001")
                    item_name = st.text_input("📦 اسم المعدة", placeholder="اسم المعدة")
                    item_category = st.selectbox("🏷️ التصنيف", categories)
                
                with col2:
                    item_status = st.selectbox("📊 الحالة", ["متوفر", "معار", "صيانة", "خارج الخدمة"])
                    item_location = st.text_input("📍 الموقع/المكان", placeholder="مثال: الرف الأول")
                    item_notes = st.text_area("📝 ملاحظات", height=100)
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_btn = st.form_submit_button("💾 حفظ المعدة", use_container_width=True, type="primary")
                with col2:
                    reset_btn = st.form_submit_button("🔄 مسح الحقول", use_container_width=True)
                
                if submit_btn:
                    if not item_id:
                        st.error("❌ يجب إدخال معرف المعدة!")
                    elif not item_name:
                        st.error("❌ يجب إدخال اسم المعدة!")
                    elif item_id in inventory:
                        st.error(f"❌ المعرف '{item_id}' مستخدم بالفعل! اختر معرفاً فريداً")
                    else:
                        inventory[item_id] = {
                            "name": item_name,
                            "category": item_category,
                            "status": item_status,
                            "location": item_location,
                            "notes": item_notes,
                            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        save_inventory(inventory)
                        st.success(f"✅ تم حفظ المعدة: **{item_name}** بمعرف **{item_id}** بنجاح!")
        
        # ============ TAB: رفع من Excel ============
        with tab_add_excel:
            st.markdown("### 📊 رفع معدات من ملف Excel")
            st.info("📋 يجب أن يحتوي الملف على الأعمدة التالية: المعرف، الاسم، التصنيف، الحالة، الموقع، ملاحظات")
            
            # زر تحميل القالب
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📥 1. حمّل القالب أولاً")
                template_data = {
                    "المعرف": ["CAM-001", "LEN-001", "LIT-001"],
                    "الاسم": ["كاميرا Sony", "عدسة 50mm", "إضاءة LED"],
                    "التصنيف": ["كاميرات", "عدسات", "إضاءة"],
                    "الحالة": ["متوفر", "متوفر", "معار"],
                    "الموقع": ["الرف الأول", "الرف الثاني", "الرف الثالث"],
                    "ملاحظات": ["جديدة", "ممتازة", "قيد الاستخدام"]
                }
                
                template_df = pd.DataFrame(template_data)
                csv_template = template_df.to_csv(index=False, encoding='utf-8-sig')
                
                st.download_button(
                    label="📥 تحميل قالب Excel",
                    data=csv_template,
                    file_name="قالب_المعدات.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.caption("💡 احفظ هذا الملف وأضف البيانات فيه")
            
            with col2:
                st.markdown("#### 📤 2. أرفع الملف المعدّل")
                uploaded_file = st.file_uploader("اختر ملف CSV أو Excel", type=['xlsx', 'xls', 'csv'], key="inventory_upload")
            
            if uploaded_file:
                try:
                    # قراءة الملف
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file, encoding='utf-8')
                    else:
                        # محاولة قراءة Excel بدون openpyxl
                        try:
                            df = pd.read_excel(uploaded_file, engine='openpyxl')
                        except:
                            try:
                                df = pd.read_excel(uploaded_file, engine='xlrd')
                            except:
                                # إذا فشل الاثنان، اطلب من المستخدم تحويل الملف لـ CSV
                                st.error("❌ لا يمكن قراءة ملف Excel. يرجى تحويل الملف إلى CSV وإعادة المحاولة")
                                st.info("💡 يمكنك فتح الملف في Excel وحفظه باسم جديد باختيار 'Save As' ثم اختر CSV")
                                st.stop()
                    
                    st.markdown("### 📊 معاينة البيانات")
                    st.dataframe(df, use_container_width=True)
                    
                    df_columns = df.columns.tolist()
                    
                    # محاولة مطابقة الأعمدة تلقائياً
                    column_mapping = {}
                    st.markdown("### 🔄 مطابقة الأعمدة")
                    col1, col2, col3 = st.columns(3)
                    
                    required_columns = ['المعرف', 'الاسم', 'التصنيف', 'الحالة', 'الموقع', 'ملاحظات']
                    
                    with col1:
                        st.write("**أعمدة الملف:**")
                        for col in df_columns:
                            st.write(f"• {col}")
                    
                    with col2:
                        st.write("**الأعمدة المطلوبة:**")
                        for col in required_columns:
                            st.write(f"• {col}")
                    
                    with col3:
                        st.write("**تعيين الأعمدة:**")
                        for req_col in required_columns:
                            selected_col = st.selectbox(
                                f"اختر عمود {req_col}",
                                df_columns,
                                key=f"col_{req_col}"
                            )
                            column_mapping[req_col] = selected_col
                    
                    if st.button("✅ استيراد المعدات", use_container_width=True, type="primary"):
                        count = 0
                        errors = 0
                        
                        for idx, row in df.iterrows():
                            try:
                                item_id = str(row[column_mapping['المعرف']]).strip()
                                item_name = str(row[column_mapping['الاسم']]).strip()
                                
                                if not item_id or not item_name or item_id == 'nan':
                                    errors += 1
                                    continue
                                
                                if item_id in inventory:
                                    st.warning(f"⚠️ المعرف '{item_id}' موجود بالفعل، سيتم تحديثه")
                                
                                inventory[item_id] = {
                                    "name": item_name,
                                    "category": str(row[column_mapping['التصنيف']]).strip() if pd.notna(row[column_mapping['التصنيف']]) else '-',
                                    "status": str(row[column_mapping['الحالة']]).strip() if pd.notna(row[column_mapping['الحالة']]) else 'متوفر',
                                    "location": str(row[column_mapping['الموقع']]).strip() if pd.notna(row[column_mapping['الموقع']]) else '-',
                                    "notes": str(row[column_mapping['ملاحظات']]).strip() if pd.notna(row[column_mapping['ملاحظات']]) else '-',
                                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                                }
                                count += 1
                            except Exception as e:
                                errors += 1
                        
                        save_inventory(inventory)
                        st.success(f"✅ تم استيراد **{count}** معدة بنجاح!")
                        if errors > 0:
                            st.warning(f"⚠️ تم تخطي **{errors}** صفوف (فارغة أو بدون معرف)")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
                    st.info("💡 تجربة: حوّل الملف إلى صيغة CSV وأعد المحاولة")
        
        # ============ TAB: تعديل المعدات ============
        with tab_edit:
            st.markdown("## ✏️ تعديل المعدات")
            inventory = load_inventory()
            categories = load_categories()
            
            if inventory:
                # بحث بسيط - الاسم فقط
                search_name = st.text_input("🔍 ابحث عن الاسم", placeholder="اكتب اسم المعدة...")
                
                # تصفية بناءً على الاسم
                filtered_items = {}
                if search_name:
                    for item_id, item in inventory.items():
                        if search_name.lower() in item['name'].lower():
                            filtered_items[item_id] = item
                else:
                    filtered_items = inventory
                
                if filtered_items:
                    st.caption(f"📊 النتائج: {len(filtered_items)} معدة")
                    
                    # جدول بسيط
                    table_data = []
                    for item_id, item in filtered_items.items():
                        table_data.append({
                            "🆔": item_id,
                            "📦 الاسم": item['name'],
                            "📍 الموقع": item.get('location', '-'),
                            "📊": item.get('status', '-')
                        })
                    
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, height=300, hide_index=True)
                    
                    st.divider()
                    
                    # اختيار المعدة
                    selected_id = st.selectbox(
                        "اختر المعدة",
                        list(filtered_items.keys()),
                        format_func=lambda x: f"{filtered_items[x]['name']} ({x})"
                    )
                    
                    if selected_id:
                        item = filtered_items[selected_id]
                        
                        st.markdown(f"### 📝 {item['name']}")
                        
                        # تعديل بسيط
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_name = st.text_input("📦 الاسم", value=item['name'])
                            new_location = st.text_input("📍 الموقع", value=item.get('location', ''))
                        
                        with col2:
                            new_status = st.selectbox("📊 الحالة", 
                                                      ["متوفر", "معار", "صيانة"],
                                                      index=["متوفر", "معار", "صيانة"].index(item.get('status', 'متوفر')))
                            
                            # التصنيف - معالجة الخطأ
                            default_category = item.get('category', categories[0])
                            try:
                                cat_index = categories.index(default_category)
                            except:
                                cat_index = 0
                            new_category = st.selectbox("🏷️ التصنيف", categories, index=cat_index)
                        
                        new_notes = st.text_area("📝 ملاحظات", value=item.get('notes', ''), height=80)
                        
                        # أزرار الحفظ والحذف
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("💾 حفظ", use_container_width=True, type="primary"):
                                if not new_name:
                                    st.error("❌ الاسم مطلوب!")
                                else:
                                    inventory[selected_id] = {
                                        "name": new_name,
                                        "category": new_category,
                                        "status": new_status,
                                        "location": new_location,
                                        "notes": new_notes,
                                        "date_added": item.get('date_added', datetime.now().strftime("%Y-%m-%d %H:%M"))
                                    }
                                    save_inventory(inventory)
                                    st.success("✅ تم الحفظ!")
                                    st.rerun()
                        
                        with col2:
                            if st.button("🗑️ حذف", use_container_width=True, type="secondary"):
                                password = st.text_input("كلمة السر", type="password")
                                if password:
                                    if hash_password(password) == users[st.session_state["username"]]["password"]:
                                        del inventory[selected_id]
                                        save_inventory(inventory)
                                        st.success("✅ تم الحذف!")
                                        st.rerun()
                                    else:
                                        st.error("❌ كلمة السر خطأ!")
                else:
                    st.info("❌ لم يتم العثور على نتائج")
            else:
                st.info("📭 لا توجد معدات")
        
        st.divider()
        
        # الإحصائيات
        st.markdown("### 📊 إحصائيات المخزن")
        
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
        
        # قائمة المعدات - جدول
        st.markdown("### 📋 جدول المعدات")
        
        if inventory:
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 ابحث بالمعرف أو الاسم...")
            with col2:
                filter_status = st.selectbox("تصفية بالحالة", ["الكل", "متوفر", "معار", "صيانة", "خارج الخدمة"], key="inv_status_filter")
            with col3:
                filter_category = st.selectbox("تصفية بالتصنيف", ["الكل"] + categories, key="inv_cat_filter")
            
            # إعداد البيانات للجدول
            table_data = []
            for item_id_loop, item in inventory.items():
                # تطبيق الفلاتر
                if search and search.lower() not in item_id_loop.lower() and search.lower() not in item['name'].lower():
                    continue
                if filter_status != "الكل" and item['status'] != filter_status:
                    continue
                if filter_category != "الكل" and item.get('category') != filter_category:
                    continue
                
                status_emoji = "🟢" if item['status'] == 'متوفر' else "🟡" if item['status'] == 'معار' else "🔴"
                
                table_data.append({
                    "🆔 المعرف": item_id_loop,
                    "📦 الاسم": item['name'],
                    "🏷️ التصنيف": item.get('category', '-'),
                    "📍 الموقع": item.get('location', '-'),
                    "📊 الحالة": f"{status_emoji} {item['status']}",
                    "📅 التاريخ": item.get('date_added', '-'),
                    "📝 ملاحظات": item.get('notes', '-')[:50] if item.get('notes') else '-'
                })
            
            if table_data:
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, height=400, hide_index=True)
                st.caption(f"✅ عدد المعدات المعروضة: **{len(table_data)}** من **{len(inventory)}**")
                
                st.divider()
                
                # حذف المعدة
                st.markdown("### 🗑️ حذف معدة")
                col1, col2 = st.columns(2)
                
                with col1:
                    item_to_delete = st.selectbox(
                        "اختر المعدة للحذف",
                        list(inventory.keys()),
                        format_func=lambda x: f"{inventory[x]['name']} ({x})",
                        key="delete_selector"
                    )
                
                with col2:
                    password = st.text_input("أدخل كلمة السر للتأكيد", type="password", key="delete_password")
                
                if st.button("🗑️ حذف المعدة", use_container_width=True, type="secondary"):
                    if not password:
                        st.error("❌ يجب إدخال كلمة السر!")
                    elif hash_password(password) != users[st.session_state["username"]]["password"]:
                        st.error("❌ كلمة السر غير صحيحة!")
                    else:
                        item_name = inventory[item_to_delete]['name']
                        del inventory[item_to_delete]
                        save_inventory(inventory)
                        st.success(f"✅ تم حذف المعدة: **{item_name}** بنجاح!")
                        st.rerun()
            else:
                st.info("❌ لم يتم العثور على معدات تطابق الفلاتر")
        else:
            st.info("📭 لا توجد معدات مسجلة")

    # ============ TAB 3: الإعارات ============
    with tab3:
        st.markdown("## 📋 نظام الإعارات")
        loans = load_loans()
        inventory = load_inventory()
        
        tab_checkout, tab_return, tab_active = st.tabs(["📤 سحب", "📥 إرجاع", "📦 نشطة"])
        
        with tab_checkout:
            st.markdown("### 📤 سحب المعدات")
            
            if inventory:
                # البيانات الأساسية
                col1, col2 = st.columns(2)
                with col1:
                    order_name = st.text_input("📋 اسم الأوردر")
                with col2:
                    employee_name = st.text_input("👤 اسم الساحب")
                
                loan_notes = st.text_area("📝 ملاحظات (اختياري)")
                
                st.divider()
                
                # المعدات المتاحة
                available_items = {k: v for k, v in inventory.items() if v.get('status') == 'متوفر'}
                
                if available_items:
                    st.markdown("**اختر المعدات:**")
                    
                    selected_items = st.multiselect(
                        "المعدات",
                        available_items.keys(),
                        format_func=lambda x: f"{x} - {available_items[x]['name']}",
                        label_visibility="collapsed"
                    )
                    
                    if selected_items:
                        st.success(f"✅ اخترت {len(selected_items)} معدة")
                    
                    st.divider()
                    
                    # الحفظ
                    if st.button("💾 حفظ والطباعة", use_container_width=True, type="primary"):
                        if not order_name or not employee_name or not selected_items:
                            st.error("❌ الرجاء ملء جميع الحقول واختيار معدات!")
                        else:
                            # حفظ الإعارات
                            for item_id in selected_items:
                                item = available_items[item_id]
                                loan_id = f"LOAN-{len(loans)+1:05d}"
                                
                                loans[loan_id] = {
                                    "item_id": item_id,
                                    "item_name": item['name'],
                                    "customer": order_name,
                                    "employee": employee_name,
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "return_date": (datetime.now().date() + timedelta(days=7)).strftime("%Y-%m-%d"),
                                    "notes": loan_notes,
                                    "status": "نشطة"
                                }
                                
                                inventory[item_id]['status'] = 'معار'
                            
                            save_loans(loans)
                            save_inventory(inventory)
                            
                            st.success(f"✅ تم حفظ {len(selected_items)} معدة!")
                            
                            # نافذة الطباعة HTML
                            st.divider()
                            st.markdown("### 🖨️ إيصال الاستلام")
                            
                            # إنشاء جدول HTML
                            table_html = """
                            <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                                <tr style="background-color:#f0f0f0;">
                                    <th style="border:1px solid #000; padding:10px; text-align:right;">#</th>
                                    <th style="border:1px solid #000; padding:10px; text-align:right;">المعرف</th>
                                    <th style="border:1px solid #000; padding:10px; text-align:right;">الاسم</th>
                                    <th style="border:1px solid #000; padding:10px; text-align:right;">التصنيف</th>
                                </tr>
                            """
                            
                            for idx, item_id in enumerate(selected_items, 1):
                                item = available_items[item_id]
                                table_html += f"""
                                <tr>
                                    <td style="border:1px solid #000; padding:10px; text-align:right;">{idx}</td>
                                    <td style="border:1px solid #000; padding:10px; text-align:right;">{item_id}</td>
                                    <td style="border:1px solid #000; padding:10px; text-align:right;">{item['name']}</td>
                                    <td style="border:1px solid #000; padding:10px; text-align:right;">{item.get('category', '-')}</td>
                                </tr>
                                """
                            
                            table_html += "</table>"
                            
                            # HTML كامل للطباعة
                            print_html = f"""
                            <html dir="rtl" style="font-family: Arial, sans-serif;">
                            <head>
                                <title>إيصال استلام</title>
                                <style>
                                    body {{ margin: 20px; direction: rtl; }}
                                    .header {{ text-align: center; margin-bottom: 30px; }}
                                    .title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                                    .info {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                                    .info-item {{ width: 45%; }}
                                    .notes {{ margin-top: 20px; padding: 10px; background-color: #f9f9f9; border: 1px solid #ddd; }}
                                    .signatures {{ display: flex; justify-content: space-between; margin-top: 40px; }}
                                    .signature {{ width: 30%; text-align: center; }}
                                    .line {{ border-top: 1px solid #000; margin-top: 50px; padding-top: 10px; }}
                                    @media print {{
                                        body {{ margin: 0; }}
                                    }}
                                </style>
                            </head>
                            <body>
                                <div class="header">
                                    <div class="title">📋 إيصال استلام معدات</div>
                                </div>
                                
                                <div class="info">
                                    <div class="info-item">
                                        <strong>الأوردر:</strong> {order_name}<br>
                                        <strong>التاريخ:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
                                    </div>
                                    <div class="info-item" style="text-align: left;">
                                        <strong>الساحب:</strong> {employee_name}<br>
                                        <strong>العدد:</strong> {len(selected_items)}
                                    </div>
                                </div>
                                
                                <div><strong>المعدات المستأجرة:</strong></div>
                                {table_html}
                                
                                {'<div class="notes"><strong>ملاحظات:</strong><br>' + loan_notes + '</div>' if loan_notes else ''}
                                
                                <div class="signatures">
                                    <div class="signature">
                                        <div>توقيع الساحب</div>
                                        <div class="line"></div>
                                    </div>
                                    <div class="signature">
                                        <div>توقيع المستقبل</div>
                                        <div class="line"></div>
                                    </div>
                                    <div class="signature">
                                        <div>التاريخ</div>
                                        <div class="line"></div>
                                    </div>
                                </div>
                                
                                <script>
                                    window.print();
                                </script>
                            </body>
                            </html>
                            """
                            
                            # عرض الـ HTML
                            st.components.v1.html(print_html, height=800)
                
                else:
                    st.info("⚠️ لا توجد معدات متاحة")
            else:
                st.info("📭 لا توجد معدات")
        
        with tab_return:
            st.markdown("### 📥 إرجاع معدة")
            
            active_loans = {k: v for k, v in loans.items() if v.get('status') == 'نشطة'}
            
            if active_loans:
                loan_id = st.selectbox("اختر الإعارة", list(active_loans.keys()), 
                                    format_func=lambda x: f"{x} - {active_loans[x]['customer']}")
                
                if loan_id:
                    loan_data = active_loans[loan_id]
                    st.info(f"📦 المعدة: **{loan_data['item_name']}** | 👤 العميل: **{loan_data['customer']}**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        return_type = st.radio("نوع الإرجاع", ["🔄 إرجاع كامل", "📦 إرجاع جزئي"])
                    
                    with col2:
                        if return_type == "📦 إرجاع جزئي":
                            partial_quantity = st.number_input("عدد الوحدات المرجعة", min_value=1, value=1, step=1)
                        else:
                            partial_quantity = 1
                    
                    return_condition = st.selectbox("حالة المعدة عند الإرجاع", ["ممتازة", "جيدة", "بها أضرار", "غير صالحة"])
                    return_notes = st.text_area("ملاحظات الإرجاع")
                    
                    if st.button("✅ تأكيد الإرجاع", use_container_width=True, type="primary"):
                        item_id = loan_data['item_id']
                        
                        if return_type == "🔄 إرجاع كامل":
                            loans[loan_id]['status'] = 'مرجعة'
                            inventory[item_id]['status'] = 'متوفر'
                            st.success("✅ تم تسجيل الإرجاع الكامل!")
                        else:
                            loans[loan_id]['status'] = 'جزئية'
                            # في الإرجاع الجزئي، المعدة تبقى معار
                            st.success(f"✅ تم تسجيل إرجاع {int(partial_quantity)} وحدة!")
                        
                        loans[loan_id]['return_condition'] = return_condition
                        loans[loan_id]['return_notes'] = return_notes
                        loans[loan_id]['actual_return_date'] = datetime.now().strftime("%Y-%m-%d")
                        save_loans(loans)
                        save_inventory(inventory)
                        
                        st.rerun()
            else:
                st.info("📭 لا توجد إعارات نشطة")
        
        with tab_active:
            st.markdown("### 📦 الإعارات النشطة")
            
            active_loans = {k: v for k, v in loans.items() if v.get('status') == 'نشطة'}
            
            if active_loans:
                for loan_id, data in active_loans.items():
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{loan_id}** - {data['customer']}")
                            st.caption(f"📦 {data['item_name']} | 👤 {data['employee']} | 📅 {data['return_date']}")
                        
                        with col2:
                            days_left = (datetime.strptime(data['return_date'], '%Y-%m-%d').date() - datetime.now().date()).days
                            if days_left < 0:
                                st.error(f"⚠️ {abs(days_left)} يوم تأخير")
                            else:
                                st.info(f"📅 {days_left} أيام")
                        
                        st.divider()
            else:
                st.info("✅ لا توجد إعارات نشطة")

    # ============ TAB 4: البحث ============
    with tab4:
        st.markdown("## 🔍 البحث والتتبع")
        
        inventory = load_inventory()
        loans = load_loans()
        
        search_type = st.radio("نوع البحث", ["المعدات", "الإعارات", "العميل"])
        search_term = st.text_input("ابحث هنا...").strip()
        
        if search_term:
            if search_type == "المعدات":
                found = {k: v for k, v in inventory.items() 
                        if search_term.lower() in k.lower() or search_term.lower() in v['name'].lower()}
                
                if found:
                    st.success(f"✅ عثرت على **{len(found)}** معدة")
                    for item_id, item in found.items():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{item['name']}** ({item_id})")
                            st.caption(f"التصنيف: {item.get('category')} | الموقع: {item.get('location')}")
                        with col2:
                            emoji = "🟢" if item['status'] == 'متوفر' else "🟡"
                            st.write(f"{emoji} {item['status']}")
                        st.divider()
                else:
                    st.warning("❌ لم يتم العثور على نتائج")
            
            elif search_type == "الإعارات":
                found = {k: v for k, v in loans.items() if search_term.lower() in k.lower()}
                
                if found:
                    for loan_id, loan in found.items():
                        st.write(f"**{loan_id}**")
                        st.info(f"العميل: {loan['customer']} | المعدة: {loan.get('item_name')} | الحالة: {loan['status']}")
                        st.divider()
                else:
                    st.warning("❌ لم يتم العثور على نتائج")
            
            elif search_type == "العميل":
                found = {k: v for k, v in loans.items() if search_term.lower() in v['customer'].lower()}
                
                if found:
                    st.success(f"✅ وجدت **{len(found)}** إعارات")
                    for loan_id, loan in found.items():
                        st.write(f"**{loan_id}** - {loan['customer']}")
                        st.caption(f"المعدة: {loan.get('item_name')} | {loan['status']}")
                        st.divider()
                else:
                    st.warning("❌ لم يتم العثور على نتائج")

    # ============ TAB 5: التقارير ============
    with tab5:
        st.markdown("## 📈 التقارير والإحصائيات")
        
        inventory = load_inventory()
        loans = load_loans()
        
        report_type = st.radio("نوع التقرير", ["📊 الإحصائيات", "📋 جرد المعدات", "📦 الإعارات"])
        
        if report_type == "📊 الإحصائيات":
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### توزيع المعدات حسب الحالة")
                statuses = {}
                for item in inventory.values():
                    status = item.get('status')
                    statuses[status] = statuses.get(status, 0) + 1
                
                if statuses:
                    status_df = pd.DataFrame(list(statuses.items()), columns=['الحالة', 'العدد'])
                    st.bar_chart(status_df.set_index('الحالة'))
            
            with col2:
                st.markdown("### توزيع حسب التصنيف")
                categories_count = {}
                for item in inventory.values():
                    cat = item.get('category', 'بدون تصنيف')
                    categories_count[cat] = categories_count.get(cat, 0) + 1
                
                if categories_count:
                    cat_df = pd.DataFrame(list(categories_count.items()), columns=['التصنيف', 'العدد'])
                    st.bar_chart(cat_df.set_index('التصنيف'))
            
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي المعدات", len(inventory))
            with col2:
                st.metric("إجمالي الإعارات", len(loans))
            with col3:
                active = sum(1 for l in loans.values() if l.get('status') == 'نشطة')
                st.metric("إعارات نشطة", active)
        
        elif report_type == "📋 جرد المعدات":
            st.markdown("## 📋 تقرير جرد المعدات الشامل")
            st.caption(f"📅 تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            if inventory:
                # ملخص
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("إجمالي المعدات", len(inventory))
                with col2:
                    available = sum(1 for i in inventory.values() if i.get('status') == 'متوفر')
                    st.metric("متوفرة", available)
                with col3:
                    loaned = sum(1 for i in inventory.values() if i.get('status') == 'معار')
                    st.metric("معارة", loaned)
                with col4:
                    maintenance = sum(1 for i in inventory.values() if i.get('status') == 'صيانة')
                    st.metric("صيانة", maintenance)
                
                st.divider()
                
                # جدول تفصيلي
                st.markdown("### 📊 تفاصيل المعدات")
                
                report_data = []
                for item_id, item in inventory.items():
                    report_data.append({
                        "المعرف": item_id,
                        "الاسم": item['name'],
                        "التصنيف": item.get('category', '-'),
                        "الحالة": item['status'],
                        "الموقع": item.get('location', '-'),
                        "تاريخ الإضافة": item.get('date_added', '-'),
                        "ملاحظات": item.get('notes', '-')
                    })
                
                df = pd.DataFrame(report_data)
                st.dataframe(df, use_container_width=True)
                
                # تحميل التقرير
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 تحميل التقرير (CSV)",
                    data=csv_data,
                    file_name=f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # التقسيم حسب الحالة
                st.markdown("### 📌 التفصيل حسب الحالة")
                
                statuses = set(item['status'] for item in inventory.values())
                for status in sorted(statuses):
                    items_by_status = {k: v for k, v in inventory.items() if v['status'] == status}
                    
                    with st.expander(f"{status} ({len(items_by_status)})"):
                        for item_id, item in items_by_status.items():
                            st.write(f"**{item['name']}** ({item_id})")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.caption(f"📂 التصنيف: {item.get('category')}")
                                st.caption(f"📍 الموقع: {item.get('location')}")
                            with col2:
                                st.caption(f"📅 التاريخ: {item.get('date_added')}")
                                if item.get('notes'):
                                    st.caption(f"📝 ملاحظات: {item['notes']}")
            else:
                st.info("📭 لا توجد معدات لعرضها")
        
        elif report_type == "📦 الإعارات":
            st.markdown("## 📦 تقرير الإعارات")
            st.caption(f"📅 تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            if loans:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("إجمالي الإعارات", len(loans))
                with col2:
                    active = sum(1 for l in loans.values() if l.get('status') == 'نشطة')
                    st.metric("نشطة", active)
                with col3:
                    returned = sum(1 for l in loans.values() if l.get('status') == 'مرجعة')
                    st.metric("مرجعة", returned)
                
                st.divider()
                
                report_data = []
                for loan_id, loan in loans.items():
                    report_data.append({
                        "رقم الإعارة": loan_id,
                        "المعدة": loan.get('item_name', '-'),
                        "العميل": loan['customer'],
                        "الموظف": loan['employee'],
                        "تاريخ السحب": loan['date'],
                        "تاريخ الإرجاع": loan['return_date'],
                        "الحالة": loan['status'],
                        "ملاحظات": loan.get('notes', '-')
                    })
                
                df = pd.DataFrame(report_data)
                st.dataframe(df, use_container_width=True)
                
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 تحميل التقرير (CSV)",
                    data=csv_data,
                    file_name=f"loans_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("📭 لا توجد إعارات لعرضها")

    # ============ TAB 6: الإعدادات ============
    with tab6:
        st.markdown("## ⚙️ الإعدادات")
        
        if st.session_state["role"] == "مدير":
            tab_users, tab_categories, tab_backup = st.tabs(["👥 الحسابات", "🏷️ التصنيفات", "💾 النسخ الاحتياطي"])
            
            with tab_users:
                st.markdown("### إنشاء حساب جديد")
                col1, col2 = st.columns(2)
                
                with col1:
                    new_user = st.text_input("اسم المستخدم الجديد")
                    new_pwd = st.text_input("كلمة السر", type="password")
                
                with col2:
                    new_role = st.selectbox("الصلاحية", ["مستخدم", "مدير"])
                    
                    if st.button("➕ إنشاء حساب", use_container_width=True):
                        if new_user and new_pwd:
                            if new_user not in users:
                                users[new_user] = {"password": hash_password(new_pwd), "role": new_role}
                                save_users(users)
                                st.success(f"✅ تم إنشاء حساب {new_user}")
                                st.rerun()
                            else:
                                st.error("❌ المستخدم موجود بالفعل!")
                        else:
                            st.error("❌ يرجى ملء جميع الحقول!")
                
                st.divider()
                st.markdown("### الحسابات الموجودة")
                
                for username, user_data in users.items():
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"👤 **{username}** - {user_data['role']}")
                    
                    with col2:
                        if username != st.session_state['username']:
                            if st.button("🗑️ حذف", key=f"del_user_{username}"):
                                del users[username]
                                save_users(users)
                                st.success("✅ تم الحذف")
                                st.rerun()
            
            with tab_categories:
                st.markdown("### إدارة التصنيفات")
                categories = load_categories()
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    new_cat = st.text_input("تصنيف جديد")
                    if st.button("➕ إضافة", use_container_width=True):
                        if new_cat and new_cat not in categories:
                            categories.append(new_cat)
                            save_categories(categories)
                            st.success("✅ تمت الإضافة!")
                            st.rerun()
                
                st.divider()
                st.markdown("### التصنيفات الموجودة")
                for i, cat in enumerate(categories):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"🏷️ {cat}")
                    with col2:
                        if st.button("🗑️", key=f"del_cat_{i}"):
                            categories.pop(i)
                            save_categories(categories)
                            st.rerun()
            
            with tab_backup:
                st.markdown("### 💾 النسخ الاحتياطي")
                st.info("📊 حفظ النسخ الاحتياطية من البيانات")
                
                if st.button("📥 تحميل نسخة احتياطية من البيانات"):
                    backup_data = {
                        "users": users,
                        "inventory": load_inventory(),
                        "loans": load_loans(),
                        "categories": categories
                    }
                    st.download_button(
                        label="📥 حمّل البيانات (JSON)",
                        data=json.dumps(backup_data, ensure_ascii=False, indent=2),
                        file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.warning("⚠️ هذه الصفحة متاحة فقط للمديرين")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b; font-size:0.85rem;'>نظام إدارة الاستوديو v3.0 | تطويراً مستمراً ✨</p>", unsafe_allow_html=True)
