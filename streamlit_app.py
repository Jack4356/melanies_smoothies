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
fruit_df = session.table("smoothies.public.fruit_options") \
                  .select(col("FRUIT_NAME"))

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# --------------------------------------------------
# Multiselect (Max 5 Fruits)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose ingredients:",
    options=fruit_list,
    max_selections=5
)

# --------------------------------------------------
# Show Nutrition Info for Each Selected Fruit
# --------------------------------------------------
if ingredients_list:
    st.subheader("🍓 Fruit Nutrition Details")

    for fruit in ingredients_list:
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}"
        )

        if response.status_code == 200:
            with st.expander(f"🍉 {fruit.capitalize()} Nutrition"):
                st.dataframe(
                    response.json(),
                    use_container_width=True
                )
        else:
            st.warning(f"No nutrition data available for {fruit}")

# --------------------------------------------------
# Insert Order into Snowflake
# --------------------------------------------------
if ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)

    insert_sql = """
        INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS)
        VALUES (?, ?)
    """

    if st.button("Submit Order"):
        session.sql(
            insert_sql,
            params=[name_on_order, ingredients_string]
        ).collect()

        st.success(f"Your smoothie is ordered, {name_on_order}! ✅")
