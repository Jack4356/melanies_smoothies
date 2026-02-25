import streamlit as st
from snowflake.snowpark.functions import col
import requests

# --------------------------------------------------
# App Title & Description
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose up to 5 fruits for your smoothie.")

# --------------------------------------------------
# Name Input
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# --------------------------------------------------
# Snowflake Connection
# --------------------------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# Load Fruit Options from Snowflake
# --------------------------------------------------
fruit_df = (
    session.table("smoothies.public.fruit_options")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

fruit_rows = fruit_df.collect()
fruit_names = [row["FRUIT_NAME"] for row in fruit_rows]
search_map = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in fruit_rows}

# --------------------------------------------------
# Multiselect (Max 5 Fruits)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose ingredients (select in the EXACT order):",
    options=fruit_names,
    max_selections=5
)

# --------------------------------------------------
# Show Nutrition Info
# --------------------------------------------------
if ingredients_list:
    st.subheader("🍓 Fruit Nutrition Details")

    for fruit in ingredients_list:
        search_on = search_map.get(fruit)

        if not search_on:
            st.warning(f"No nutrition data available for {fruit}")
            continue

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}"
        )

        if response.status_code == 200:
            with st.expander(f"🍉 {fruit} Nutrition"):
                st.dataframe(response.json(), use_container_width=True)
        else:
            st.warning(f"No nutrition data available for {fruit}")

# --------------------------------------------------
# Insert Order into Snowflake
# --------------------------------------------------
if ingredients_list and name_on_order:

    # ✅ EXACT formatting required for HASH matching
    ingredients_string = ", ".join(ingredients_list)

    # Kevin orders are NOT filled
    order_filled = False if name_on_order == "Kevin" else True

    insert_sql = """
        INSERT INTO smoothies.public.orders
        (NAME_ON_ORDER, INGREDIENTS, ORDER_FILLED, ORDER_TS)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP())
    """

    if st.button("Submit Order"):
        session.sql(
            insert_sql,
            params=[
                name_on_order,
                ingredients_string,
                order_filled
            ]
        ).collect()

        st.success(f"Your smoothie is ordered, {name_on_order}! ✅")
