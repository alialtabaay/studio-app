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
                            
                            st.divider()
                            st.markdown("### 📱 خيارات الإرسال")
                            
                            # إنشاء نص الإيصال
                            receipt_text = f"""
═══════════════════════════════════════
📋 إيصال سحب معدات
═══════════════════════════════════════

🆔 الأوردر: {order_name}
👤 الساحب: {employee_name}
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}

المعدات المسحوبة:
───────────────────────────────────────
"""
                            
                            for idx, item_id in enumerate(selected_items, 1):
                                item = available_items[item_id]
                                receipt_text += f"{idx}. {item_id} - {item['name']}\n"
                            
                            receipt_text += f"""
───────────────────────────────────────
📝 الملاحظات: {loan_notes if loan_notes else 'بدون'}
═══════════════════════════════════════
تم الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                            
                            # خيارات الإرسال
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**📋 نسخ النص:**")
                                if st.button("📋 انسخ للكليب بوارد", use_container_width=True):
                                    st.code(receipt_text)
                                    st.success("✅ تم نسخ النص - الصقه حيث تريد!")
                            
                            with col2:
                                st.write("**💬 إرسال عبر WhatsApp:**")
                                # إنشاء رابط WhatsApp
                                whatsapp_text = receipt_text.replace("\n", "%0A").replace(" ", "%20")
                                whatsapp_link = f"https://wa.me/?text={whatsapp_text}"
                                st.markdown(f"[💬 افتح WhatsApp](https://wa.me/?text={whatsapp_text})", unsafe_allow_html=True)
                                st.caption("سيفتح WhatsApp جاهز للإرسال")
                            
                            with col3:
                                st.write("**💾 تحميل الملف:**")
                                if st.button("📥 حمّل TXT", use_container_width=True):
                                    st.download_button(
                                        label="📥 حمّل النص",
                                        data=receipt_text,
                                        file_name=f"receipt_{order_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                
                else:
                    st.info("⚠️ لا توجد معدات متاحة")
            else:
                st.info("📭 لا توجد معدات")
        
        with tab_return:
            st.markdown("### 📥 إرجاع المعدات")
            
            # البحث عن الأوردر
            active_loans = {k: v for k, v in loans.items() if v.get('status') == 'نشطة'}
            
            if active_loans:
                # الحصول على أسماء الأوردرات الفريدة
                order_names = sorted(set([loan['customer'] for loan in active_loans.values()]))
                
                st.markdown("#### البحث عن الأوردر")
                selected_order = st.selectbox(
                    "اختر الأوردر",
                    order_names,
                    label_visibility="collapsed"
                )
                
                if selected_order:
                    # الحصول على كل المعدات لهذا الأوردر
                    order_items = {}
                    for loan_id, loan in active_loans.items():
                        if loan['customer'] == selected_order:
                            order_items[loan_id] = loan
                    
                    st.divider()
                    st.markdown(f"#### المعدات المستأجرة من أوردر: **{selected_order}**")
                    
                    if order_items:
                        # عرض المعدات
                        st.markdown("**المعدات النشطة:**")
                        items_display = {}
                        for loan_id, loan in order_items.items():
                            display_text = f"{loan['item_name']} ({loan['item_id']})"
                            items_display[loan_id] = display_text
                        
                        # اختيار المعدات للإرجاع (جزئي)
                        selected_loans = st.multiselect(
                            "اختر المعدات للإرجاع",
                            list(order_items.keys()),
                            format_func=lambda x: f"{order_items[x]['item_name']} ({order_items[x]['item_id']})",
                            label_visibility="collapsed"
                        )
                        
                        if selected_loans:
                            st.success(f"✅ اخترت {len(selected_loans)} معدة للإرجاع")
                            
                            st.divider()
                            
                            # حالة المعدات
                            st.markdown("#### حالة المعدات عند الإرجاع")
                            
                            return_condition = st.selectbox(
                                "حالة المعدات",
                                ["ممتازة", "جيدة", "بها أضرار", "غير صالحة"]
                            )
                            
                            return_notes = st.text_area("ملاحظات الإرجاع (اختياري)")
                            
                            st.divider()
                            
                            # الحفظ
                            if st.button("✅ تأكيد الإرجاع", use_container_width=True, type="primary"):
                                returned_items = []
                                
                                for loan_id in selected_loans:
                                    loan = order_items[loan_id]
                                    item_id = loan['item_id']
                                    
                                    # تحديث حالة الإعارة
                                    loans[loan_id]['status'] = 'مرجعة'
                                    loans[loan_id]['return_condition'] = return_condition
                                    loans[loan_id]['return_notes'] = return_notes
                                    loans[loan_id]['actual_return_date'] = datetime.now().strftime("%Y-%m-%d")
                                    
                                    # تحديث حالة المعدة
                                    inventory[item_id]['status'] = 'متوفر'
                                    
                                    returned_items.append({
                                        'id': item_id,
                                        'name': loan['item_name'],
                                        'loan_id': loan_id
                                    })
                                
                                save_loans(loans)
                                save_inventory(inventory)
                                
                                st.success(f"✅ تم إرجاع {len(selected_loans)} معدة بنجاح!")
                                
                                # إيصال الإرجاع
                                st.divider()
                                st.markdown("### 🧾 إيصال الإرجاع")
                                
                                # HTML للطباعة
                                table_html = """
                                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                                    <tr style="background-color:#f0f0f0;">
                                        <th style="border:1px solid #000; padding:10px; text-align:right;">#</th>
                                        <th style="border:1px solid #000; padding:10px; text-align:right;">المعرف</th>
                                        <th style="border:1px solid #000; padding:10px; text-align:right;">الاسم</th>
                                        <th style="border:1px solid #000; padding:10px; text-align:right;">رقم الإعارة</th>
                                    </tr>
                                """
                                
                                for idx, item in enumerate(returned_items, 1):
                                    table_html += f"""
                                    <tr>
                                        <td style="border:1px solid #000; padding:10px; text-align:right;">{idx}</td>
                                        <td style="border:1px solid #000; padding:10px; text-align:right;">{item['id']}</td>
                                        <td style="border:1px solid #000; padding:10px; text-align:right;">{item['name']}</td>
                                        <td style="border:1px solid #000; padding:10px; text-align:right;">{item['loan_id']}</td>
                                    </tr>
                                    """
                                
                                table_html += "</table>"
                                
                                return_html = f"""
                                <html dir="rtl" style="font-family: Arial, sans-serif;">
                                <head>
                                    <title>إيصال إرجاع</title>
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
                                    </style>
                                </head>
                                <body>
                                    <div class="header">
                                        <div class="title">📋 إيصال إرجاع معدات</div>
                                    </div>
                                    
                                    <div class="info">
                                        <div class="info-item">
                                            <strong>الأوردر:</strong> {selected_order}<br>
                                            <strong>التاريخ:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
                                        </div>
                                        <div class="info-item" style="text-align: left;">
                                            <strong>عدد المعدات:</strong> {len(selected_loans)}<br>
                                            <strong>الحالة:</strong> {return_condition}
                                        </div>
                                    </div>
                                    
                                    <div><strong>المعدات المرجعة:</strong></div>
                                    {table_html}
                                    
                                    {'<div class="notes"><strong>ملاحظات:</strong><br>' + return_notes + '</div>' if return_notes else ''}
                                    
                                    <div class="signatures">
                                        <div class="signature">
                                            <div>توقيع المرجع</div>
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
                                
                                st.components.v1.html(return_html, height=800)
                        else:
                            st.info("اختر معدة واحدة على الأقل")
                    else:
                        st.info("لا توجد معدات مستأجرة لهذا الأوردر")
            else:
                st.info("📭 لا توجد إعارات نشطة")
        
        with tab_active:
            st.markdown("### 📦 الإعارات النشطة - التفاصيل الكاملة")
            
            active_loans = {k: v for k, v in loans.items() if v.get('status') == 'نشطة'}
            all_loans = loans.copy()
            
            if active_loans:
                # تجميع حسب الأوردر
                orders = {}
                for loan_id, data in active_loans.items():
                    order_name = data['customer']
                    if order_name not in orders:
                        orders[order_name] = []
                    orders[order_name].append((loan_id, data))
                
                # عرض الأوردرات بالتفصيل
                for order_name in sorted(orders.keys()):
                    active_items = orders[order_name]
                    first_item = active_items[0][1]
                    
                    # الحصول على كل الإعارات لهذا الأوردر (مرجعة + نشطة)
                    all_order_loans = [(k, v) for k, v in all_loans.items() if v['customer'] == order_name]
                    
                    # فصل المعدات حسب الحالة
                    returned_items = [(k, v) for k, v in all_order_loans if v.get('status') == 'مرجعة']
                    active_items_list = [(k, v) for k, v in all_order_loans if v.get('status') == 'نشطة']
                    
                    # حساب أيام الإرجاع
                    days_left = (datetime.strptime(first_item['return_date'], '%Y-%m-%d').date() - datetime.now().date()).days
                    status_color = "🔴" if days_left < 0 else "🟡" if days_left < 3 else "🟢"
                    
                    # عنوان الأوردر
                    st.markdown(f"## {status_color} أوردر: {order_name}")
                    
                    # معلومات الأوردر
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("👤 الساحب", first_item['employee'])
                    with col2:
                        st.metric("📅 تاريخ السحب", first_item['date'][:10])
                    with col3:
                        st.metric("⏰ موعد الإرجاع", first_item['return_date'])
                    with col4:
                        if days_left < 0:
                            st.metric("⚠️ التأخير", f"{abs(days_left)} يوم")
                        else:
                            st.metric("✅ المتبقي", f"{days_left} يوم")
                    
                    # الملاحظات
                    if first_item.get('notes'):
                        st.info(f"📝 **ملاحظات:** {first_item['notes']}")
                    
                    st.divider()
                    
                    # تبويبات التفاصيل
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        tab_all = st.checkbox("📊 الكل", value=True, key=f"all_{order_name}")
                    with col2:
                        tab_active = st.checkbox("📦 النشطة", value=True, key=f"active_{order_name}")
                    with col3:
                        tab_returned = st.checkbox("✅ المرجعة", value=True, key=f"returned_{order_name}")
                    
                    # المعدات الكاملة
                    if tab_all:
                        st.markdown("### 📊 المعدات الكاملة (المسحوبة)")
                        all_data = []
                        for idx, (loan_id, loan_data) in enumerate(all_order_loans, 1):
                            status_emoji = "🟢" if loan_data.get('status') == 'نشطة' else "✅"
                            all_data.append({
                                "#": idx,
                                "الحالة": status_emoji,
                                "المعرف": loan_data['item_id'],
                                "الاسم": loan_data['item_name'],
                                "رقم الإعارة": loan_id
                            })
                        
                        if all_data:
                            df_all = pd.DataFrame(all_data)
                            st.dataframe(df_all, use_container_width=True, hide_index=True)
                        
                        st.divider()
                    
                    # المعدات النشطة
                    if tab_active:
                        st.markdown("### 📦 المعدات النشطة (المتبقية)")
                        active_data = []
                        for idx, (loan_id, loan_data) in enumerate(active_items_list, 1):
                            active_data.append({
                                "#": idx,
                                "المعرف": loan_data['item_id'],
                                "الاسم": loan_data['item_name'],
                                "التصنيف": loan_data.get('category', '-'),
                                "رقم الإعارة": loan_id
                            })
                        
                        if active_data:
                            df_active = pd.DataFrame(active_data)
                            st.dataframe(df_active, use_container_width=True, hide_index=True)
                            st.write(f"**المجموع:** {len(active_items_list)} معدة")
                        else:
                            st.info("لا توجد معدات نشطة (تم إرجاع الكل)")
                        
                        st.divider()
                    
                    # المعدات المرجعة
                    if tab_returned:
                        st.markdown("### ✅ المعدات المرجعة")
                        returned_data = []
                        for idx, (loan_id, loan_data) in enumerate(returned_items, 1):
                            returned_data.append({
                                "#": idx,
                                "المعرف": loan_data['item_id'],
                                "الاسم": loan_data['item_name'],
                                "الحالة": loan_data.get('return_condition', '-'),
                                "تاريخ الإرجاع": loan_data.get('actual_return_date', '-')
                            })
                        
                        if returned_data:
                            df_returned = pd.DataFrame(returned_data)
                            st.dataframe(df_returned, use_container_width=True, hide_index=True)
                            st.write(f"**المجموع:** {len(returned_items)} معدة")
                        else:
                            st.info("لم يتم إرجاع أي معدات بعد")
                        
                        st.divider()
                    
                    # زر الطباعة
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button("📊 تقرير", key=f"report_{order_name}", use_container_width=True):
                            st.session_state[f"show_report_{order_name}"] = True
                    
                    # عرض التقرير المنفصل
                    if st.session_state.get(f"show_report_{order_name}"):
                        st.divider()
                        st.markdown(f"## 📊 تقرير الأوردر: **{order_name}**")
                        
                        # معلومات الأوردر الكاملة
                        st.markdown("### 📋 معلومات الأوردر")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.write(f"**🆔 الأوردر:**\n{order_name}")
                        with col2:
                            st.write(f"**👤 الساحب:**\n{first_item['employee']}")
                        with col3:
                            st.write(f"**📅 التاريخ:**\n{first_item['date']}")
                        with col4:
                            st.write(f"**⏰ موعد الإرجاع:**\n{first_item['return_date']}")
                        
                        st.divider()
                        
                        # جدول المعدات الكاملة
                        st.markdown("### 📊 المعدات الكاملة (المسحوبة)")
                        all_table = []
                        for idx, (loan_id, loan_data) in enumerate(all_order_loans, 1):
                            status = "✅ مرجعة" if loan_data.get('status') == 'مرجعة' else "📦 نشطة"
                            all_table.append({
                                "#": idx,
                                "الحالة": status,
                                "المعرف": loan_data['item_id'],
                                "الاسم": loan_data['item_name'],
                                "التصنيف": loan_data.get('category', '-'),
                                "الموقع": loan_data.get('location', '-')
                            })
                        
                        df_all_report = pd.DataFrame(all_table)
                        st.dataframe(df_all_report, use_container_width=True, hide_index=True)
                        
                        st.divider()
                        
                        # المعدات النشطة
                        if active_items_list:
                            st.markdown("### 📦 المعدات المتبقية (النشطة)")
                            active_table = []
                            for idx, (loan_id, loan_data) in enumerate(active_items_list, 1):
                                active_table.append({
                                    "#": idx,
                                    "المعرف": loan_data['item_id'],
                                    "الاسم": loan_data['item_name'],
                                    "التصنيف": loan_data.get('category', '-'),
                                    "الموقع": loan_data.get('location', '-'),
                                    "رقم الإعارة": loan_id
                                })
                            
                            df_active_report = pd.DataFrame(active_table)
                            st.dataframe(df_active_report, use_container_width=True, hide_index=True)
                            st.warning(f"⚠️ **{len(active_items_list)} معدة متبقية**")
                            
                            st.divider()
                        
                        # المعدات المرجعة
                        if returned_items:
                            st.markdown("### ✅ المعدات المرجعة")
                            returned_table = []
                            for idx, (loan_id, loan_data) in enumerate(returned_items, 1):
                                returned_table.append({
                                    "#": idx,
                                    "المعرف": loan_data['item_id'],
                                    "الاسم": loan_data['item_name'],
                                    "الحالة": loan_data.get('return_condition', '-'),
                                    "تاريخ الإرجاع": loan_data.get('actual_return_date', '-'),
                                    "ملاحظات": loan_data.get('return_notes', '-')[:30] + "..." if loan_data.get('return_notes') else '-'
                                })
                            
                            df_returned_report = pd.DataFrame(returned_table)
                            st.dataframe(df_returned_report, use_container_width=True, hide_index=True)
                            
                            st.divider()
                        
                        # ملخص شامل
                        st.markdown("### 📊 ملخص التقرير")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📦 إجمالي المعدات", len(all_order_loans))
                        with col2:
                            st.metric("📥 المتبقية", len(active_items_list))
                        with col3:
                            st.metric("✅ المرجعة", len(returned_items))
                        with col4:
                            status_pct = int((len(returned_items) / len(all_order_loans) * 100)) if all_order_loans else 0
                            st.metric("📊 نسبة الإرجاع", f"{status_pct}%")
                        
                        st.divider()
                        
                        # الملاحظات
                        if first_item.get('notes'):
                            st.markdown("### 📝 ملاحظات الأوردر")
                            st.info(first_item['notes'])
                        
                        st.divider()
                        
                        # زر الطباعة
                        if st.button("🖨️ طباعة التقرير", use_container_width=True, key=f"print_report_{order_name}"):
                            # HTML التقرير
                            print_html = f"""
                            <html dir="rtl" style="font-family: Arial, sans-serif;">
                            <head>
                                <title>تقرير أوردر</title>
                                <style>
                                    body {{ margin: 20px; direction: rtl; font-size: 14px; }}
                                    .header {{ text-align: center; margin-bottom: 30px; border-bottom: 3px solid #000; padding-bottom: 20px; }}
                                    .title {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                                    .subtitle {{ font-size: 18px; color: #666; }}
                                    .info-box {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin: 20px 0; }}
                                    .info-item {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                                    .info-label {{ font-size: 12px; color: #666; margin-bottom: 5px; }}
                                    .info-value {{ font-size: 16px; font-weight: bold; }}
                                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                                    th {{ background-color: #333; color: white; padding: 12px; text-align: right; font-weight: bold; }}
                                    td {{ border: 1px solid #ddd; padding: 10px; text-align: right; }}
                                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                                    .section-title {{ font-size: 18px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; border-left: 4px solid #333; padding-left: 10px; }}
                                    .summary {{ margin-top: 30px; padding: 20px; background-color: #f0f0f0; border-radius: 5px; }}
                                    .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; }}
                                    .summary-item {{ text-align: center; }}
                                    .notes {{ margin-top: 20px; padding: 15px; background-color: #fffacd; border-left: 4px solid #ffc700; }}
                                    .footer {{ margin-top: 50px; text-align: center; border-top: 1px solid #ddd; padding-top: 20px; color: #666; font-size: 12px; }}
                                    @media print {{ body {{ margin: 0; }} .no-print {{ display: none; }} }}
                                </style>
                            </head>
                            <body>
                                <div class="header">
                                    <div class="title">📊 تقرير الأوردر</div>
                                    <div class="subtitle">تقرير مفصل شامل</div>
                                </div>
                                
                                <div class="info-box">
                                    <div class="info-item">
                                        <div class="info-label">🆔 الأوردر</div>
                                        <div class="info-value">{order_name}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">👤 الساحب</div>
                                        <div class="info-value">{first_item['employee']}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">📅 التاريخ</div>
                                        <div class="info-value">{first_item['date'][:10]}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">⏰ موعد الإرجاع</div>
                                        <div class="info-value">{first_item['return_date']}</div>
                                    </div>
                                </div>
                                
                                <div class="section-title">📊 المعدات الكاملة (المسحوبة)</div>
                                <table>
                                    <tr>
                                        <th>#</th>
                                        <th>الحالة</th>
                                        <th>المعرف</th>
                                        <th>الاسم</th>
                                        <th>التصنيف</th>
                                        <th>الموقع</th>
                                    </tr>
                            """
                            
                            for idx, (loan_id, loan_data) in enumerate(all_order_loans, 1):
                                status = "✅ مرجعة" if loan_data.get('status') == 'مرجعة' else "📦 نشطة"
                                print_html += f"""
                                    <tr>
                                        <td>{idx}</td>
                                        <td>{status}</td>
                                        <td>{loan_data['item_id']}</td>
                                        <td>{loan_data['item_name']}</td>
                                        <td>{loan_data.get('category', '-')}</td>
                                        <td>{loan_data.get('location', '-')}</td>
                                    </tr>
                                """
                            
                            print_html += "</table>"
                            
                            # المعدات النشطة
                            if active_items_list:
                                print_html += """
                                <div class="section-title">📦 المعدات المتبقية (النشطة)</div>
                                <table>
                                    <tr>
                                        <th>#</th>
                                        <th>المعرف</th>
                                        <th>الاسم</th>
                                        <th>التصنيف</th>
                                    </tr>
                                """
                                for idx, (loan_id, loan_data) in enumerate(active_items_list, 1):
                                    print_html += f"""
                                    <tr>
                                        <td>{idx}</td>
                                        <td>{loan_data['item_id']}</td>
                                        <td>{loan_data['item_name']}</td>
                                        <td>{loan_data.get('category', '-')}</td>
                                    </tr>
                                    """
                                print_html += "</table>"
                            
                            # المعدات المرجعة
                            if returned_items:
                                print_html += """
                                <div class="section-title">✅ المعدات المرجعة</div>
                                <table>
                                    <tr>
                                        <th>#</th>
                                        <th>المعرف</th>
                                        <th>الاسم</th>
                                        <th>الحالة</th>
                                        <th>تاريخ الإرجاع</th>
                                    </tr>
                                """
                                for idx, (loan_id, loan_data) in enumerate(returned_items, 1):
                                    print_html += f"""
                                    <tr>
                                        <td>{idx}</td>
                                        <td>{loan_data['item_id']}</td>
                                        <td>{loan_data['item_name']}</td>
                                        <td>{loan_data.get('return_condition', '-')}</td>
                                        <td>{loan_data.get('actual_return_date', '-')}</td>
                                    </tr>
                                    """
                                print_html += "</table>"
                            
                            # الملخص
                            pct = int((len(returned_items) / len(all_order_loans) * 100)) if all_order_loans else 0
                            print_html += f"""
                                <div class="summary">
                                    <div class="section-title" style="margin-top: 0;">📊 ملخص التقرير</div>
                                    <div class="summary-grid">
                                        <div class="summary-item">
                                            <div style="font-size: 24px; font-weight: bold;">{len(all_order_loans)}</div>
                                            <div style="color: #666; font-size: 12px;">إجمالي المعدات</div>
                                        </div>
                                        <div class="summary-item">
                                            <div style="font-size: 24px; font-weight: bold;">{len(active_items_list)}</div>
                                            <div style="color: #666; font-size: 12px;">المتبقية</div>
                                        </div>
                                        <div class="summary-item">
                                            <div style="font-size: 24px; font-weight: bold;">{len(returned_items)}</div>
                                            <div style="color: #666; font-size: 12px;">المرجعة</div>
                                        </div>
                                        <div class="summary-item">
                                            <div style="font-size: 24px; font-weight: bold;">{pct}%</div>
                                            <div style="color: #666; font-size: 12px;">نسبة الإرجاع</div>
                                        </div>
                                    </div>
                                </div>
                            """
                            
                            # الملاحظات
                            if first_item.get('notes'):
                                print_html += f"""
                                <div class="notes">
                                    <strong>📝 ملاحظات الأوردر:</strong><br>
                                    {first_item['notes']}
                                </div>
                                """
                            
                            # التذييل
                            print_html += f"""
                                <div class="footer">
                                    <p>تم إنشاء التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                                    <p>نظام إدارة المعدات والإعارات</p>
                                </div>
                                
                                <script>
                                    window.print();
                                </script>
                            </body>
                            </html>
                            """
                            
                            st.components.v1.html(print_html, height=1000)
                    
                    st.markdown("---")
                    
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
        
        report_type = st.radio("نوع التقرير", ["📊 الإحصائيات", "📋 جرد المعدات", "📦 الإعارات", "📄 تقرير مفصل الأوردر"])
        
        if report_type == "📄 تقرير مفصل الأوردر":
            st.divider()
            st.markdown("### 📄 اختر الأوردر لعرض التقرير المفصل")
            
            # الحصول على قائمة الأوردرات الفريدة
            all_orders = sorted(set([loan['customer'] for loan in loans.values()]))
            
            if all_orders:
                selected_order = st.selectbox(
                    "اختر الأوردر",
                    all_orders,
                    label_visibility="collapsed"
                )
                
                if selected_order:
                    # الحصول على كل الإعارات للأوردر
                    order_loans = {k: v for k, v in loans.items() if v['customer'] == selected_order}
                    
                    if order_loans:
                        # فصل المعدات حسب الحالة
                        active_items = [(k, v) for k, v in order_loans.items() if v.get('status') == 'نشطة']
                        returned_items = [(k, v) for k, v in order_loans.items() if v.get('status') == 'مرجعة']
                        
                        first_loan = list(order_loans.values())[0]
                        
                        st.divider()
                        st.markdown(f"## 📊 تقرير الأوردر: **{selected_order}**")
                        
                        # معلومات الأوردر
                        st.markdown("### 📋 معلومات الأوردر")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("🆔 الأوردر", selected_order)
                        with col2:
                            st.metric("👤 الساحب", first_loan['employee'])
                        with col3:
                            st.metric("📅 التاريخ", first_loan['date'][:10])
                        with col4:
                            st.metric("⏰ موعد الإرجاع", first_loan['return_date'])
                        
                        st.divider()
                        
                        # المعدات الكاملة
                        st.markdown("### 📊 المعدات الكاملة (المسحوبة)")
                        all_data = []
                        for idx, (loan_id, loan_data) in enumerate(order_loans.items(), 1):
                            status_emoji = "📦 نشطة" if loan_data.get('status') == 'نشطة' else "✅ مرجعة"
                            all_data.append({
                                "#": idx,
                                "الحالة": status_emoji,
                                "المعرف": loan_data['item_id'],
                                "الاسم": loan_data['item_name'],
                                "التصنيف": loan_data.get('category', '-'),
                                "الموقع": loan_data.get('location', '-')
                            })
                        
                        df_all = pd.DataFrame(all_data)
                        st.dataframe(df_all, use_container_width=True, hide_index=True)
                        st.caption(f"📊 **الإجمالي: {len(order_loans)} معدة**")
                        
                        st.divider()
                        
                        # المعدات النشطة
                        if active_items:
                            st.markdown("### 📦 المعدات المتبقية (النشطة)")
                            active_data = []
                            for idx, (loan_id, loan_data) in enumerate(active_items, 1):
                                active_data.append({
                                    "#": idx,
                                    "المعرف": loan_data['item_id'],
                                    "الاسم": loan_data['item_name'],
                                    "التصنيف": loan_data.get('category', '-'),
                                    "الموقع": loan_data.get('location', '-'),
                                    "رقم الإعارة": loan_id
                                })
                            
                            df_active = pd.DataFrame(active_data)
                            st.dataframe(df_active, use_container_width=True, hide_index=True)
                            st.warning(f"⚠️ **{len(active_items)} معدة متبقية**")
                            
                            st.divider()
                        
                        # المعدات المرجعة
                        if returned_items:
                            st.markdown("### ✅ المعدات المرجعة")
                            returned_data = []
                            for idx, (loan_id, loan_data) in enumerate(returned_items, 1):
                                returned_data.append({
                                    "#": idx,
                                    "المعرف": loan_data['item_id'],
                                    "الاسم": loan_data['item_name'],
                                    "حالة الرجوع": loan_data.get('return_condition', '-'),
                                    "تاريخ الإرجاع": loan_data.get('actual_return_date', '-'),
                                    "ملاحظات": (loan_data.get('return_notes', '-')[:20] + "...") if loan_data.get('return_notes') else '-'
                                })
                            
                            df_returned = pd.DataFrame(returned_data)
                            st.dataframe(df_returned, use_container_width=True, hide_index=True)
                            
                            st.divider()
                        
                        # الملخص الإحصائي
                        st.markdown("### 📊 ملخص التقرير")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📦 إجمالي المعدات", len(order_loans))
                        with col2:
                            st.metric("📥 المتبقية", len(active_items))
                        with col3:
                            st.metric("✅ المرجعة", len(returned_items))
                        with col4:
                            pct = int((len(returned_items) / len(order_loans) * 100)) if order_loans else 0
                            st.metric("📊 نسبة الإرجاع", f"{pct}%")
                        
                        st.divider()
                        
                        # الملاحظات
                        if first_loan.get('notes'):
                            st.markdown("### 📝 ملاحظات الأوردر")
                            st.info(f"**ملاحظات:** {first_loan['notes']}")
                            st.divider()
                        
                        # زر الطباعة
                        if st.button("🖨️ طباعة التقرير المفصل", use_container_width=True, key=f"print_detailed_{selected_order}"):
                            # HTML للطباعة
                            print_html = f"""
                            <html dir="rtl" style="font-family: Arial, sans-serif;">
                            <head>
                                <title>تقرير الأوردر - {selected_order}</title>
                                <style>
                                    body {{ margin: 20px; direction: rtl; font-size: 13px; }}
                                    .header {{ text-align: center; margin-bottom: 30px; border-bottom: 3px solid #333; padding-bottom: 20px; }}
                                    .title {{ font-size: 32px; font-weight: bold; margin-bottom: 5px; color: #333; }}
                                    .subtitle {{ font-size: 16px; color: #666; }}
                                    .info-section {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; margin: 30px 0; }}
                                    .info-card {{ border: 2px solid #333; padding: 15px; border-radius: 5px; }}
                                    .info-label {{ font-size: 11px; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
                                    .info-value {{ font-size: 18px; font-weight: bold; color: #333; }}
                                    table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
                                    th {{ background-color: #333; color: white; padding: 12px; text-align: right; font-size: 12px; font-weight: bold; }}
                                    td {{ border: 1px solid #ddd; padding: 10px; text-align: right; font-size: 12px; }}
                                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                                    .section-title {{ font-size: 16px; font-weight: bold; margin: 30px 0 15px 0; border-left: 4px solid #333; padding-left: 10px; color: #333; }}
                                    .summary-section {{ margin: 30px 0; padding: 20px; background-color: #f0f0f0; border-radius: 5px; }}
                                    .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; margin-top: 15px; }}
                                    .summary-item {{ text-align: center; padding: 15px; background-color: white; border-radius: 5px; border: 1px solid #ddd; }}
                                    .summary-number {{ font-size: 28px; font-weight: bold; color: #333; }}
                                    .summary-label {{ font-size: 11px; color: #666; margin-top: 5px; }}
                                    .notes-section {{ margin: 30px 0; padding: 15px; background-color: #fffacd; border-left: 4px solid #ffc700; border-radius: 3px; }}
                                    .footer {{ margin-top: 50px; text-align: center; border-top: 1px solid #ddd; padding-top: 15px; color: #666; font-size: 11px; }}
                                    @media print {{ body {{ margin: 0; }} }}
                                </style>
                            </head>
                            <body>
                                <div class="header">
                                    <div class="title">📊 تقرير الأوردر المفصل</div>
                                    <div class="subtitle">تقرير شامل لجميع المعدات والإعارات</div>
                                </div>
                                
                                <div class="info-section">
                                    <div class="info-card">
                                        <div class="info-label">🆔 رقم الأوردر</div>
                                        <div class="info-value">{selected_order}</div>
                                    </div>
                                    <div class="info-card">
                                        <div class="info-label">👤 الشخص الساحب</div>
                                        <div class="info-value">{first_loan['employee']}</div>
                                    </div>
                                    <div class="info-card">
                                        <div class="info-label">📅 تاريخ السحب</div>
                                        <div class="info-value">{first_loan['date'][:10]}</div>
                                    </div>
                                    <div class="info-card">
                                        <div class="info-label">⏰ موعد الإرجاع</div>
                                        <div class="info-value">{first_loan['return_date']}</div>
                                    </div>
                                </div>
                                
                                <div class="section-title">📊 المعدات الكاملة (المسحوبة)</div>
                                <table>
                                    <tr>
                                        <th>#</th>
                                        <th>الحالة</th>
                                        <th>المعرف</th>
                                        <th>الاسم</th>
                                        <th>التصنيف</th>
                                        <th>الموقع</th>
                                    </tr>
                            """
                            
                            for idx, (loan_id, loan_data) in enumerate(order_loans.items(), 1):
                                status = "📦 نشطة" if loan_data.get('status') == 'نشطة' else "✅ مرجعة"
                                print_html += f"""
                                    <tr>
                                        <td>{idx}</td>
                                        <td>{status}</td>
                                        <td>{loan_data['item_id']}</td>
                                        <td>{loan_data['item_name']}</td>
                                        <td>{loan_data.get('category', '-')}</td>
                                        <td>{loan_data.get('location', '-')}</td>
                                    </tr>
                                """
                            
                            print_html += "</table>"
                            
                            # المعدات النشطة
                            if active_items:
                                print_html += """
                                <div class="section-title">📦 المعدات المتبقية (النشطة)</div>
                                <table>
                                    <tr>
                                        <th>#</th>
                                        <th>المعرف</th>
                                        <th>الاسم</th>
                                        <th>التصنيف</th>
                                        <th>الموقع</th>
                                    </tr>
                                """
                                for idx, (loan_id, loan_data) in enumerate(active_items, 1):
                                    print_html += f"""
                                    <tr>
                                        <td>{idx}</td>
                                        <td>{loan_data['item_id']}</td>
                                        <td>{loan_data['item_name']}</td>
                                        <td>{loan_data.get('category', '-')}</td>
                                        <td>{loan_data.get('location', '-')}</td>
                                    </tr>
                                    """
                                print_html += "</table>"
                            
                            # المعدات المرجعة
                            if returned_items:
                                print_html += """
                                <div class="section-title">✅ المعدات المرجعة</div>
                                <table>
                                    <tr>
                                        <th>#</th>
                                        <th>المعرف</th>
                                        <th>الاسم</th>
                                        <th>حالة الرجوع</th>
                                        <th>تاريخ الإرجاع</th>
                                    </tr>
                                """
                                for idx, (loan_id, loan_data) in enumerate(returned_items, 1):
                                    print_html += f"""
                                    <tr>
                                        <td>{idx}</td>
                                        <td>{loan_data['item_id']}</td>
                                        <td>{loan_data['item_name']}</td>
                                        <td>{loan_data.get('return_condition', '-')}</td>
                                        <td>{loan_data.get('actual_return_date', '-')}</td>
                                    </tr>
                                    """
                                print_html += "</table>"
                            
                            # الملخص
                            pct = int((len(returned_items) / len(order_loans) * 100)) if order_loans else 0
                            print_html += f"""
                                <div class="summary-section">
                                    <div class="section-title" style="margin: 0 0 15px 0;">📊 ملخص التقرير الإحصائي</div>
                                    <div class="summary-grid">
                                        <div class="summary-item">
                                            <div class="summary-number">{len(order_loans)}</div>
                                            <div class="summary-label">إجمالي المعدات</div>
                                        </div>
                                        <div class="summary-item">
                                            <div class="summary-number">{len(active_items)}</div>
                                            <div class="summary-label">المعدات المتبقية</div>
                                        </div>
                                        <div class="summary-item">
                                            <div class="summary-number">{len(returned_items)}</div>
                                            <div class="summary-label">المعدات المرجعة</div>
                                        </div>
                                        <div class="summary-item">
                                            <div class="summary-number">{pct}%</div>
                                            <div class="summary-label">نسبة الإرجاع</div>
                                        </div>
                                    </div>
                                </div>
                            """
                            
                            # الملاحظات
                            if first_loan.get('notes'):
                                print_html += f"""
                                <div class="notes-section">
                                    <strong>📝 ملاحظات الأوردر:</strong><br>
                                    {first_loan['notes']}
                                </div>
                                """
                            
                            # التذييل
                            print_html += f"""
                                <div class="footer">
                                    <p><strong>تم إنشاء التقرير:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                                    <p>نظام إدارة المعدات والإعارات - نسخة متقدمة</p>
                                </div>
                                
                                <script>
                                    window.print();
                                </script>
                            </body>
                            </html>
                            """
                            
                            st.components.v1.html(print_html, height=1200)
                    else:
                        st.info("لا توجد إعارات لهذا الأوردر")
            else:
                st.info("لا توجد أوردرات بعد")
        
        elif report_type == "📊 الإحصائيات":
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
            tab_users, tab_categories, tab_backup, tab_delete = st.tabs(["👥 الحسابات", "🏷️ التصنيفات", "💾 النسخ الاحتياطي", "🗑️ حذف البيانات"])
            
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
                st.info("💡 **النسخ الاحتياطية توفر:**\n- حماية البيانات من الفقدان\n- استعادة سهلة في حالة الطوارئ\n- نقل البيانات بين الأنظمة")
                
                backup_tab1, backup_tab2, backup_tab3 = st.tabs(["📥 تصدير نسخة", "📤 استيراد نسخة", "📊 معلومات"])
                
                with backup_tab1:
                    st.markdown("#### 📥 تصدير النسخة الاحتياطية")
                    st.write("**حمّل نسخة من كل البيانات:**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("💾 تصدير كل البيانات", use_container_width=True, type="primary"):
                            backup_data = {
                                "users": users,
                                "inventory": load_inventory(),
                                "loans": load_loans(),
                                "categories": load_categories(),
                                "backup_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "backup_info": {
                                    "total_inventory": len(load_inventory()),
                                    "total_loans": len(load_loans()),
                                    "total_users": len(users)
                                }
                            }
                            
                            backup_json = json.dumps(backup_data, ensure_ascii=False, indent=2)
                            
                            st.success("✅ النسخة جاهزة للتحميل!")
                            st.download_button(
                                label="📥 حمّل النسخة (JSON)",
                                data=backup_json,
                                file_name=f"backup_كامل_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                    
                    with col2:
                        if st.button("💾 تصدير المعدات فقط", use_container_width=True):
                            inventory_backup = load_inventory()
                            st.download_button(
                                label="📥 حمّل المعدات",
                                data=json.dumps(inventory_backup, ensure_ascii=False, indent=2),
                                file_name=f"backup_معدات_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                
                with backup_tab2:
                    st.markdown("#### 📤 استيراد النسخة الاحتياطية")
                    st.warning("⚠️ **تحذير:** استيراد نسخة سيستبدل البيانات الحالية!")
                    
                    uploaded_file = st.file_uploader("اختر ملف النسخة الاحتياطية", type=["json"], label_visibility="collapsed")
                    
                    if uploaded_file is not None:
                        try:
                            # قراءة الملف
                            file_content = uploaded_file.read().decode('utf-8')
                            backup_data = json.loads(file_content)
                            
                            # عرض المحتويات
                            st.info(f"📊 **محتويات النسخة:**\n"
                                   f"- المعدات: {len(backup_data.get('inventory', {}))} عنصر\n"
                                   f"- الإعارات: {len(backup_data.get('loans', {}))} إعارة\n"
                                   f"- المستخدمين: {len(backup_data.get('users', {}))} مستخدم\n"
                                   f"- تاريخ النسخ: {backup_data.get('backup_date', 'غير محدد')}")
                            
                            st.divider()
                            
                            # طلب كلمة السر أولاً
                            st.markdown("**التأكيد الأمني:**")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                confirm = st.checkbox("✅ أنا متأكد من الاستيراد", value=False, key="confirm_import")
                            
                            with col2:
                                password = st.text_input("أدخل كلمة السر", type="password", key="import_password")
                            
                            if st.button("✅ استيراد النسخة الآن", type="primary", use_container_width=True):
                                if not confirm:
                                    st.error("❌ يجب تأكيد الاستيراد أولاً!")
                                elif not password:
                                    st.error("❌ أدخل كلمة السر!")
                                elif hash_password(password) != users[st.session_state["username"]]["password"]:
                                    st.error("❌ كلمة السر غير صحيحة!")
                                else:
                                    try:
                                        import os
                                        os.makedirs('data', exist_ok=True)
                                        
                                        # استيراد البيانات
                                        with open('data/inventory.json', 'w', encoding='utf-8') as f:
                                            json.dump(backup_data.get('inventory', {}), f, ensure_ascii=False, indent=2)
                                        
                                        with open('data/loans.json', 'w', encoding='utf-8') as f:
                                            json.dump(backup_data.get('loans', {}), f, ensure_ascii=False, indent=2)
                                        
                                        if 'categories' in backup_data and backup_data['categories']:
                                            with open('data/categories.json', 'w', encoding='utf-8') as f:
                                                json.dump(backup_data['categories'], f, ensure_ascii=False, indent=2)
                                        
                                        st.success("✅ تم استيراد النسخة بنجاح!")
                                        st.balloons()
                                        st.info("🔄 **الرجاء:** أعد تحميل الصفحة (اضغط F5) لرؤية البيانات الجديدة")
                                    except Exception as e:
                                        st.error(f"❌ خطأ في الاستيراد: {str(e)}")
                                        st.warning(f"📝 التفاصيل: تأكد من أن الملف صحيح وليس تالفاً")
                        
                        except json.JSONDecodeError:
                            st.error("❌ الملف ليس JSON صحيح!")
                            st.info("💡 تأكد من أن الملف تم تصديره من هذا النظام")
                        except Exception as e:
                            st.error(f"❌ خطأ: {str(e)}")
                            st.warning("📝 الملف غير صحيح أو تالف")
                
                with backup_tab3:
                    st.markdown("#### 📊 معلومات النسخ الاحتياطية")
                    
                    inventory = load_inventory()
                    loans_data = load_loans()
                    categories = load_categories()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📦 عدد المعدات", len(inventory))
                    with col2:
                        st.metric("📋 عدد الإعارات", len(loans_data))
                    with col3:
                        st.metric("👥 عدد المستخدمين", len(users))
                    
                    st.divider()
                    
                    st.markdown("**📝 ملخص البيانات:**")
                    
                    # حالة المعدات
                    statuses = {}
                    for item in inventory.values():
                        status = item.get('status')
                        statuses[status] = statuses.get(status, 0) + 1
                    
                    if statuses:
                        st.write("**توزيع حالة المعدات:**")
                        for status, count in statuses.items():
                            st.write(f"  - {status}: {count}")
                    
                    st.divider()
                    
                    # حالة الإعارات
                    loan_statuses = {}
                    for loan in loans_data.values():
                        status = loan.get('status', 'غير محدد')
                        loan_statuses[status] = loan_statuses.get(status, 0) + 1
                    
                    if loan_statuses:
                        st.write("**توزيع حالة الإعارات:**")
                        for status, count in loan_statuses.items():
                            st.write(f"  - {status}: {count}")
                    
                    st.divider()
                    
                    st.markdown("**⏰ آخر تحديث:** الآن")
                    st.markdown(f"**📅 التاريخ الحالي:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                with tab_delete:
                    st.markdown("### 🗑️ حذف البيانات")
                    st.error("⚠️ **تحذير خطير!** هذا الإجراء لا يمكن التراجع عنه!")
                    
                    st.info("💡 **تأكد من:**\n- أخذت نسخة احتياطية\n- أنت متأكد من الحذف\n- لا توجد بيانات مهمة بتحتاجها")
                    
                    delete_tab1, delete_tab2, delete_tab3 = st.tabs(["🗑️ حذف انتقائي", "💥 حذف الكل", "❌ لا تحذف"])
                    
                    with delete_tab1:
                        st.markdown("#### 🗑️ حذف بيانات محددة")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**اختر البيانات للحذف:**")
                            delete_inventory = st.checkbox("🗑️ حذف المعدات فقط", value=False)
                            delete_loans = st.checkbox("🗑️ حذف الإعارات فقط", value=False)
                            delete_categories = st.checkbox("🗑️ حذف التصنيفات فقط", value=False)
                        
                        with col2:
                            if delete_inventory or delete_loans or delete_categories:
                                st.warning("⚠️ سيتم حذف البيانات المختارة!")
                                
                                password = st.text_input("أدخل كلمة السر للتأكيد", type="password", key="delete_partial_password")
                                
                                if st.button("⚠️ أؤكد الحذف الانتقائي", use_container_width=True, type="secondary"):
                                    if password and hash_password(password) == users[st.session_state["username"]]["password"]:
                                        import os
                                        os.makedirs('data', exist_ok=True)
                                        
                                        try:
                                            if delete_inventory:
                                                with open('data/inventory.json', 'w', encoding='utf-8') as f:
                                                    json.dump({}, f, ensure_ascii=False, indent=2)
                                                st.success("✅ تم حذف المعدات!")
                                            
                                            if delete_loans:
                                                with open('data/loans.json', 'w', encoding='utf-8') as f:
                                                    json.dump({}, f, ensure_ascii=False, indent=2)
                                                st.success("✅ تم حذف الإعارات!")
                                            
                                            if delete_categories:
                                                with open('data/categories.json', 'w', encoding='utf-8') as f:
                                                    json.dump(["كاميرا", "عدسات", "إضاءة", "صوتيات"], f, ensure_ascii=False, indent=2)
                                                st.success("✅ تم حذف التصنيفات! (أُعيدت الافتراضية)")
                                            
                                            st.info("🔄 حدّث الصفحة لرؤية التغييرات")
                                        except Exception as e:
                                            st.error(f"❌ خطأ: {str(e)}")
                                    elif password:
                                        st.error("❌ كلمة السر غير صحيحة!")
                            else:
                                st.info("اختر على الأقل بيان واحد للحذف")
                    
                    with delete_tab2:
                        st.markdown("#### 💥 حذف كل البيانات")
                        st.error("🔴 **خطر جداً!** سيحذف:")
                        st.write("""
                        - ❌ كل المعدات
                        - ❌ كل الإعارات
                        - ❌ كل التصنيفات
                        - ✅ لا يحذف الحسابات
                        """)
                        
                        st.divider()
                        
                        # تأكيد الحذف
                        confirm = st.checkbox("✅ أنا متأكد 100% من الحذف", value=False, key="confirm_delete_all")
                        
                        if confirm:
                            password = st.text_input("أدخل كلمة السر للتأكيد الأخير", type="password", key="delete_all_password")
                            
                            if st.button("💥 حذف كل البيانات!", use_container_width=True, type="primary"):
                                if password and hash_password(password) == users[st.session_state["username"]]["password"]:
                                    import os
                                    os.makedirs('data', exist_ok=True)
                                    
                                    try:
                                        # حذف كل شيء
                                        with open('data/inventory.json', 'w', encoding='utf-8') as f:
                                            json.dump({}, f, ensure_ascii=False, indent=2)
                                        
                                        with open('data/loans.json', 'w', encoding='utf-8') as f:
                                            json.dump({}, f, ensure_ascii=False, indent=2)
                                        
                                        with open('data/categories.json', 'w', encoding='utf-8') as f:
                                            json.dump(["كاميرا", "عدسات", "إضاءة", "صوتيات"], f, ensure_ascii=False, indent=2)
                                        
                                        st.success("💥 تم حذف كل البيانات بنجاح!")
                                        st.balloons()
                                        st.info("🔄 النظام نظيف تماماً! حدّث الصفحة للبدء من جديد")
                                    except Exception as e:
                                        st.error(f"❌ خطأ: {str(e)}")
                                elif password:
                                    st.error("❌ كلمة السر غير صحيحة!")
                        else:
                            st.warning("⚠️ يجب تأكيد الحذف أولاً!")
                    
                    with delete_tab3:
                        st.markdown("#### ❌ لا تحذف")
                        st.success("✅ الخيار الآمن!")
                        st.info("👈 اذهب للتبويبات الأخرى للعمل بشكل آمن")
        else:
            st.warning("⚠️ هذه الصفحة متاحة فقط للمديرين")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b; font-size:0.85rem;'>نظام إدارة الاستوديو v3.0 | تطويراً مستمراً ✨</p>", unsafe_allow_html=True)
