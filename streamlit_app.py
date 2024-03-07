# Import python packages
import streamlit as st
import requests
import pandas
# Disabled for External Streamlit
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col


# Setup Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get Snowflake data
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Setup API
fruityvice_api = "https://fruityvice.com/api/"

#### Form Headers
st.title("My Parents New Healthy Diner")

st.subheader("Breakfast Menu")
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
    # Get API Data
    for ingredient in ingredients_list:
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == ingredient, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', ingredient,' is ', search_on, '.')
        st.subheader(ingredient + " Nutrition Information")
        fruityvice_response = requests.get(fruityvice_api + "fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
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