import streamlit as st
import json
import os
import hashlib
from datetime import datetime

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

for key, val in [("logged_in", False), ("username", ""), ("role", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

users = load_users()

if not st.session_state["logged_in"]:
    st.markdown("""
    <div style="text-align:center; padding: 60px 0 30px;">
        <div style="font-size:3rem;">🎙️</div>
        <h1 style="color:#1e3a8a; font-family:'Cairo',sans-serif;">نظام إدارة الاستوديو</h1>
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
    with st.sidebar:
        st.markdown(f"### 👤 مرحباً {st.session_state['username']}")
        st.markdown(f"**الصلاحية:** {st.session_state['role']}")
        
        if st.button("🚪 تسجيل خروج", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["role"] = ""
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📊 لوحة التحكم", "📦 المخزن", "📋 الإعارات", "⚙️ الإعدادات"])

    with tab1:
        st.markdown("## 📊 لوحة التحكم")
        inventory = load_inventory()
        loans = load_loans()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("إجمالي المعدات", len(inventory))
        with col2:
            st.metric("متوفرة", sum(1 for i in inventory.values() if i.get('status') == 'متوفر'))
        with col3:
            st.metric("معارة", sum(1 for i in inventory.values() if i.get('status') == 'معار'))
        with col4:
            st.metric("إعارات نشطة", sum(1 for l in loans.values() if l.get('status') == 'نشطة'))

    with tab2:
        st.markdown("## 📦 إدارة المخزن")
        inventory = load_inventory()
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### إضافة معدة جديدة")
            item_id = st.text_input("معرف المعدة (ID)")
            item_name = st.text_input("اسم المعدة")
            item_status = st.selectbox("الحالة", ["متوفر", "معار", "صيانة"])
            
            if st.button("حفظ المعدة ✓", use_container_width=True, type="primary"):
                if item_id and item_name:
                    inventory[item_id] = {
                        "name": item_name,
                        "status": item_status,
                        "date_added": datetime.now().strftime("%Y-%m-%d")
                    }
                    save_inventory(inventory)
                    st.success("✅ تم حفظ المعدة!")
                    st.rerun()
        
        with col2:
            st.markdown("### إحصائيات")
            st.metric("إجمالي", len(inventory))
            st.metric("متوفرة", sum(1 for i in inventory.values() if i.get('status') == 'متوفر'))

        st.markdown("### المعدات المسجلة")
        if inventory:
            for item_id, item_data in inventory.items():
                st.write(f"**{item_data['name']}** ({item_id}) - {item_data['status']}")
        else:
            st.info("لا توجد معدات مسجلة")

    with tab3:
        st.markdown("## 📋 نظام الإعارات")
        loans = load_loans()
        inventory = load_inventory()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### سحب معدة")
            if inventory:
                item_to_loan = st.selectbox("اختر المعدة", list(inventory.keys()), format_func=lambda x: inventory[x]['name'])
                customer = st.text_input("اسم العميل")
                
                if st.button("تأكيد السحب ✓", use_container_width=True, type="primary"):
                    if customer:
                        loan_id = f"LOAN-{len(loans)+1:04d}"
                        loans[loan_id] = {
                            "item_id": item_to_loan,
                            "customer": customer,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "status": "نشطة"
                        }
                        save_loans(loans)
                        inventory[item_to_loan]['status'] = 'معار'
                        save_inventory(inventory)
                        st.success(f"✅ تم السحب! ({loan_id})")
                        st.rerun()
        
        with col2:
            st.markdown("### الإعارات النشطة")
            active = {k: v for k, v in loans.items() if v.get('status') == 'نشطة'}
            if active:
                for loan_id, data in active.items():
                    st.write(f"**{loan_id}** - {data['customer']}")
            else:
                st.info("لا توجد إعارات نشطة")

    if st.session_state["role"] == "مدير":
        with tab4:
            st.markdown("## ⚙️ الإعدادات")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### إنشاء حساب جديد")
                new_user = st.text_input("اسم المستخدم")
                new_pwd = st.text_input("كلمة السر", type="password")
                
                if st.button("إنشاء ✓", use_container_width=True):
                    if new_user and new_pwd:
                        if new_user not in users:
                            users[new_user] = {"password": hash_password(new_pwd), "role": "مستخدم"}
                            save_users(users)
                            st.success("✅ تم الإنشاء!")
                        else:
                            st.error("❌ المستخدم موجود!")
            
            with col2:
                st.markdown("### الحسابات")
                for user, data in users.items():
                    st.write(f"👤 {user} - {data['role']}")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>نظام إدارة الاستوديو v2.0</p>", unsafe_allow_html=True)
