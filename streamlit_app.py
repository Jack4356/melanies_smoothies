import streamlit as st
from snowflake.snowpark.functions import col
import requests

# --------------------------------------------------
# App Title
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose up to 5 fruits for your smoothie.")

# --------------------------------------------------
# Name Input
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")

# --------------------------------------------------
# Snowflake Connection
# --------------------------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# Load Fruit Options
# --------------------------------------------------
fruit_df = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

fruit_rows = fruit_df.collect()

fruit_names = [row["FRUIT_NAME"] for row in fruit_rows]
search_map = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in fruit_rows}

# --------------------------------------------------
# Ingredient Selection (ORDER MATTERS)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose ingredients (select in EXACT order):",
    options=fruit_names,
    max_selections=5
)

# --------------------------------------------------
# Nutrition Info + Ingredient String (LAB METHOD)
# --------------------------------------------------
ingredients_string = ""

if ingredients_list:
    st.subheader("🍓 Fruit Nutrition Details")

    for fruit in ingredients_list:
        # ✅ BUILD STRING IN LOOP (DO NOT SORT)
        ingredients_string += fruit + ", "

        search_on = search_map.get(fruit)

        if search_on:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            if response.status_code == 200:
                with st.expander(f"{fruit} Nutrition Information"):
                    st.dataframe(response.json(), use_container_width=True)

# ✅ REMOVE TRAILING COMMA + SPACE
ingredients_string = ingredients_string.rstrip(", ")

# --------------------------------------------------
# Insert Order (NO ORDER_FILLED HERE)
# --------------------------------------------------
if st.button("Submit Order") and name_on_order and ingredients_string:

    insert_sql = """
        INSERT INTO smoothies.public.orders
        (NAME_ON_ORDER, INGREDIENTS, ORDER_TS)
        VALUES (?, ?, CURRENT_TIMESTAMP())
    """

    session.sql(
        insert_sql,
        params=[name_on_order, ingredients_string]
    ).collect()

    st.success(f"Smoothie order placed for {name_on_order} ✅")
