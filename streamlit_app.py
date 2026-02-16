import streamlit as st
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose up to 5 fruits for your smoothie.")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)
cnx = st.connection("snowflake")
session = cnx.session()
# Load fruit options
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Multiselect
ingredients_list = st.multiselect(
    "Choose ingredients:",
    options=fruit_list,
    max_selections=5
)

if ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)

    insert_sql = """
        INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS)
        VALUES (?, ?)
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(
            insert_sql,
            params=[name_on_order, ingredients_string]
        ).collect()

        st.success(f"Your smoothie is ordered, {name_on_order}! ✅")
        
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
