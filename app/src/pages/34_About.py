import streamlit as st
from modules.nav import SideBarLinks


SideBarLinks(show_home=True)

st.title("About MealMind")

st.write("""
MealMind is a simple, student-friendly meal planning app made for anyone who’s tired of staring into their fridge not knowing what to cook.
Instead of making you scroll through endless recipes, MealMind looks at the ingredients you already have and suggests quick meals based on
your tastes, dietary needs, and what’s close to expiring. It keeps things easy and practical, helping you answer the everyday question:
“What can I make right now?”
""")

st.write("""
This app matters because most meal-planning tools are way too complicated or require too much manual work. A lot of us buy groceries we
forget to use or do not know how to put together. MealMind solves that by tracking your ingredients, helping reduce food waste, and giving
you simple recipe recommendations. It is made for busy students, young adults living on their own, beginner cooks who want more confidence,
and the people behind the scenes who keep everything running smoothly. With features like personalized recipes, ingredient tracking,
food-waste reminders, and a dashboard showing what people waste most often, MealMind makes cooking and planning meals much less stressful.
""")

st.write("""
MealMind is also a prototype built for **CS 3200** to explore:
- Realistic **relational schema** for ingredients, recipes, inventories, profiles, and analytics
- A REST API in Flask with multiple Blueprints
- A Streamlit front-end that supports **4 personas**:
  - **Ava** – Busy student cook
  - **Jordan** – Health-focused professional
  - **Maya** – System administrator
  - **Samuel** – Data analyst
""")

st.write("""
**Technical highlights:**

- Uses MySQL in Docker (`db` service) with schema and mock data loaded from the SQL initialization files
- Flask API (`api` service) using Blueprints for inventory, recipes, profiles, meal plans, ingredients, and analytics
- Streamlit app (`app` service) calling the API at `http://api:4000`
- UI demonstrates **GET, POST, PUT, and DELETE** routes wired to real user flows for each persona
""")


