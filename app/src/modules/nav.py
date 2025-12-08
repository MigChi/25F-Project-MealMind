# modules/nav.py
import streamlit as st

def _ensure_auth_or_redirect():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        # Don’t explode on About or Home
        if st.sidebar.button("Back to login"):
            st.switch_page("Home.py")
        return False
    return True


def _home_link():
    st.sidebar.page_link("Home.py", label="Switch User", icon="🔁")


def _about_link():
    st.sidebar.page_link("pages/34_About.py", label="About MealMind", icon="ℹ️")


def _student_links():
    st.sidebar.page_link("pages/00_Ava_Home.py", label="Student Dashboard", icon="🏠")
    st.sidebar.page_link("pages/01_Ava_Fridge.py", label="My Fridge", icon="🧊")
    st.sidebar.page_link("pages/02_Ava_Quick_Recipes.py", label="Quick Recipes", icon="⚡")
    st.sidebar.page_link("pages/03_Ava_Groceries.py", label="Weekly Groceries", icon="🛒")


def _health_links():
    st.sidebar.page_link("pages/10_Jordan_Home.py", label="Health Dashboard", icon="🏠")
    st.sidebar.page_link("pages/11_Jordan_Preferences.py", label="Diet & Budget", icon="🥗")
    st.sidebar.page_link("pages/12_Jordan_MealPlan.py", label="Weekly Meal Plan", icon="📅")
    st.sidebar.page_link("pages/13_Jordan_Budget_Recipes.py", label="Budget Recipes", icon="💸")


def _admin_links():
    st.sidebar.page_link("pages/20_Maya_Home.py", label="Admin Dashboard", icon="🖥️")
    st.sidebar.page_link("pages/21_Maya_Recipe_Management.py", label="Recipe Management", icon="📖")
    st.sidebar.page_link("pages/22_Maya_Data_Quality.py", label="Data Quality", icon="✅")
    st.sidebar.page_link("pages/23_Maya_System_Health.py", label="System Health", icon="📊")


def _analyst_links():
    st.sidebar.page_link("pages/30_Samuel_Home.py", label="Analyst Dashboard", icon="📊")
    st.sidebar.page_link("pages/31_Samuel_Waste_Analytics.py", label="Food Waste Analytics", icon="🥬")
    st.sidebar.page_link("pages/32_Samuel_Recipe_Trends.py", label="Recipe Trends", icon="📈")
    st.sidebar.page_link("pages/33_Samuel_User_Behavior.py", label="User Behavior", icon="👥")


def SideBarLinks(show_home=True):
    # Logo at top (replace with your AI-generated logo file)
    st.sidebar.image("assets/meal_mind.png", width=150)

    if show_home:
        _home_link()

    if not _ensure_auth_or_redirect():
        _about_link()
        return

    role = st.session_state.get("role")
    if role == "student":
        _student_links()
    elif role == "health":
        _health_links()
    elif role == "admin":
        _admin_links()
    elif role == "analyst":
        _analyst_links()

    _about_link()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.switch_page("Home.py")
