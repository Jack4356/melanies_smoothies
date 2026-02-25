import streamlit as st
from snowflake.snowpark.functions import col, hash as sf_hash
import requests

# --------------------------------------------------
# App Title
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose up to 5 fruits for your smoothie.")

# --------------------------------------------------
# Name Input
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie")

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

pd_df = fruit_df.to_pandas()

fruit_names = pd_df["FRUIT_NAME"].tolist()

# --------------------------------------------------
# Ingredient Selection (ORDER MATTERS)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose ingredients (select in EXACT order):",
    options=fruit_names,
    max_selections=5
)

# --------------------------------------------------
# Nutrition Info + Ingredient String
# --------------------------------------------------
ingredients_string = ""

if ingredients_list:
    st.subheader("🍓 Fruit Nutrition Details")

    for fruit in ingredients_list:
        ingredients_string += fruit.strip() + ","

        # REQUIRED LINE (YES — KEEP THIS)
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit, "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for",
            fruit,
            "is",
            search_on
        )

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        if response.status_code == 200:
            with st.expander(f"{fruit} Nutrition Information"):
                st.dataframe(response.json(), use_container_width=True)

# Remove trailing comma
ingredients_string = ingredients_string.rstrip(",")

# --------------------------------------------------
# Normalize for HASHING (THIS IS THE KEY)
# --------------------------------------------------
canonical_ingredients = ",".join(
    [f.strip().upper() for f in ingredients_string.split(",")]
)

# --------------------------------------------------
# Insert Order
# --------------------------------------------------
if st.button("Submit Order") and name_on_order and canonical_ingredients:

    insert_sql = f"""
        INSERT INTO smoothies.public.orders
        (NAME_ON_ORDER, INGREDIENTS, INGREDIENTS_HASH)
        VALUES (
            '{name_on_order}',
            '{canonical_ingredients}',
            HASH('{canonical_ingredients}')
        )
    """

    session.sql(insert_sql).collect()

    st.success(f"✅ Smoothie order placed for {name_on_order}")
