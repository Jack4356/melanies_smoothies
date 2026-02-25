import streamlit as st
import requests

# --------------------------------------------------
# App Title
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie")

# --------------------------------------------------
# Snowflake Connection
# --------------------------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# Name Input
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie")

# --------------------------------------------------
# Load Fruit Options
# --------------------------------------------------
fruit_df = session.table("smoothies.public.fruit_options") \
                  .select("FRUIT_NAME", "SEARCH_ON")

pd_df = fruit_df.to_pandas()

fruit_names = pd_df["FRUIT_NAME"].tolist()

# --------------------------------------------------
# Ingredient Selection (ORDER MATTERS)
# --------------------------------------------------
ingredients = st.multiselect(
    "Choose up to 5 fruits (select in order):",
    fruit_names,
    max_selections=5
)

# --------------------------------------------------
# Build Ingredients String
# --------------------------------------------------
ingredients_string = ""

if ingredients:
    st.subheader("🍓 Nutrition Information")

    for fruit in ingredients:
        ingredients_string += fruit + ","

        # REQUIRED FOR LAB DEBUGGING
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit, "SEARCH_ON"
        ].iloc[0]

        st.write("The search value for", fruit, "is", search_on)

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        if response.status_code == 200:
            with st.expander(f"{fruit} Nutrition"):
                st.dataframe(response.json(), use_container_width=True)

# Remove trailing comma
ingredients_string = ingredients_string.rstrip(",")

# --------------------------------------------------
# CANONICAL FORMAT (THIS MAKES HASH MATCH)
# --------------------------------------------------
canonical_ingredients = ",".join(
    [f.strip().upper() for f in ingredients_string.split(",")]
)

# --------------------------------------------------
# Insert Order (CORRECT SNOWFLAKE SYNTAX)
# --------------------------------------------------
if st.button("Submit Order") and name_on_order and canonical_ingredients:

    insert_sql = f"""
        INSERT INTO smoothies.public.orders
        (NAME_ON_ORDER, INGREDIENTS, INGREDIENTS_HASH)
        SELECT
            '{name_on_order}',
            '{canonical_ingredients}',
            HASH('{canonical_ingredients}')
    """

    session.sql(insert_sql).collect()

    st.success("✅ Smoothie order submitted successfully!")
