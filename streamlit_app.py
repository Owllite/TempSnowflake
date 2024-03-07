# Import python packages
import streamlit as st
import requests
# Disabled for External Streamlit
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col


# Setup Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get Snowflake data
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Get API Data
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(fruityvice_response.json())
fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)


#### Form Headers
st.title("My Parents New Healthy Diner")

st.write("Breakfast Menu")
st.write("Omega 3 & Blueberry Oatmeal")
st.write("Kale, Spinach & Rocket Smoothie")
st.write("Hard-Boiled Free-Range Egg")

st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

#### Main Form Start
customer_name = st.text_input('Name', placeholder='Type your name here')
st.write('Your name is ',customer_name)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections = 5
)

if ingredients_list:
    st.session_state['submit_is_disabled'] = False
    st.write(' '.join(ingredients_list))
else:
    st.session_state['submit_is_disabled'] = True

    
submit_button = st.button('Submit Order', 'submitorder',  disabled=st.session_state['submit_is_disabled'])

if submit_button:
    if ingredients_list:

        orders_insert = \
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS" + \
        " (name_on_order, ingredients)   VALUES (?, ?)"
        query_params = [customer_name, ' '.join(ingredients_list)]
        
        session.sql(orders_insert,params=query_params).collect()

        st.success('Your Smoothie is ordered, ' + customer_name + '!', icon="✅")