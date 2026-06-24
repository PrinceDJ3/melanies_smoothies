# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customise your smoothie")
st.write("Choose what you want in your smoothie")
name_on_order = st.text_input('Name on smoothie: ')
st.write('The name on your smoothie will be:', name_on_order)

cnx = st.connection('snowflake')
session = cnx.session()

fruit_rows = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME')) \
    .collect()
fruit_names = [row['FRUIT_NAME'] for row in fruit_rows]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    selected_fruit = ingredients_list[0]

    response = requests.get(
        f"https://my.smoothiefroot.com/api/fruit/{selected_fruit.lower()}"
    )

    if response.ok:
        sf_df = pd.json_normalize(response.json())
        st.dataframe(data=sf_df, use_container_width=True)
    else:
        st.error("Could not fetch fruit details from the API.")

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")





    
    
