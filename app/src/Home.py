import streamlit as st

st.set_page_config(page_title="MealMind", page_icon="🥗")

# --- Mock users per persona (these user_ids should exist in your mock data if possible) ---
STUDENT_USERS = [
    {"id": 1, "first_name": "Ava", "full_name": "Ava Torres"},
    {"id": 2, "first_name": "Liam", "full_name": "Liam Chen"},
]

HEALTH_USERS = [
    {"id": 3, "first_name": "Jordan", "full_name": "Jordan Patel"},
    {"id": 4, "first_name": "Riley", "full_name": "Riley Gomez"},
]

ADMIN_USERS = [
    {"id": 10, "first_name": "Maya", "full_name": "Maya Rodriguez"},
]

ANALYST_USERS = [
    {"id": 20, "first_name": "Samuel", "full_name": "Samuel Lee"},
]

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["user"] = None

st.title("🥗 MealMind")
st.write("Smart meal planning and food-waste reduction — pick a role to explore the app.")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.subheader("🧑‍🎓 Student Cook (Ava)")
    student_choice = st.selectbox(
        "Student users",
        STUDENT_USERS,
        format_func=lambda u: u["full_name"],
        key="student_select",
    )
    if st.button("Login as Student", key="login_student", use_container_width=True):
        st.session_state["authenticated"] = True
        st.session_state["role"] = "student"
        st.session_state["user"] = student_choice
        st.switch_page("pages/00_Ava_Home.py")

with col2:
    st.subheader("💪 Health-Focused Professional (Jordan)")
    health_choice = st.selectbox(
        "Health users",
        HEALTH_USERS,
        format_func=lambda u: u["full_name"],
        key="health_select",
    )
    if st.button("Login as Health User", key="login_health", use_container_width=True):
        st.session_state["authenticated"] = True
        st.session_state["role"] = "health"
        st.session_state["user"] = health_choice
        st.switch_page("pages/10_Jordan_Home.py")

with col3:
    st.subheader("🛠️ System Administrator (Maya)")
    admin_choice = st.selectbox(
        "Admin users",
        ADMIN_USERS,
        format_func=lambda u: u["full_name"],
        key="admin_select",
    )
    if st.button("Login as Admin", key="login_admin", use_container_width=True):
        st.session_state["authenticated"] = True
        st.session_state["role"] = "admin"
        st.session_state["user"] = admin_choice
        st.switch_page("pages/20_Maya_Home.py")

with col4:
    st.subheader("📊 Data Analyst (Samuel)")
    analyst_choice = st.selectbox(
        "Analyst users",
        ANALYST_USERS,
        format_func=lambda u: u["full_name"],
        key="analyst_select",
    )
    if st.button("Login as Analyst", key="login_analyst", use_container_width=True):
        st.session_state["authenticated"] = True
        st.session_state["role"] = "analyst"
        st.session_state["user"] = analyst_choice
        st.switch_page("pages/30_Samuel_Home.py")

st.write("---")
st.caption("No real authentication is implemented. This is just persona switching for the demo.")
