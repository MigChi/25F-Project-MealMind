import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks(show_home=True)

st.title("About MealMind")

st.write("""
MealMind is a prototype built for **CS 3200** to explore:

- Realistic **relational schema** for ingredients, recipes, inventories, and analytics  
- A REST API in Flask with multiple Blueprints  
- A Streamlit front-end that supports **4 personas**:
  - 🧑‍🎓 **Ava** – Busy student cook
  - 💪 **Jordan** – Health-focused professional
  - 🛠️ **Maya** – System administrator
  - 📊 **Samuel** – Data analyst
""")

st.write("""
**Technical highlights:**

- Uses MySQL in Docker (`db` service) with schema + mock data from `01_mealmind_db.sql` and `02_mock_data.sql`
- Flask API (`api` service) using Blueprints for inventory, recipes, profiles, meal plans, and analytics
- Streamlit app (`app` service) calling the API at `http://api:4000`
- UI demonstrates **GET, POST, PUT, and DELETE** routes wired to real user flows
""")

st.caption("This app is not production-ready; it’s a course project designed to demonstrate full-stack thinking.")
