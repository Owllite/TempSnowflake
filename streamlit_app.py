# Import python packages
import streamlit as st
import requests
# Disabled for External Streamlit
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
# Write directly to the app
# st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

# Get API Data
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(fruityvice_response.json())
fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

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

#option = st.selectbox(
#    'What is your favourite fruit?',
#    ('Banana', 'Strawberries', 'Peaches'))

#st.write('Your favourite fruit is:', option)

session = cnx.session()

customer_name = st.text_input('Name', placeholder='Type your name here')
st.write('Your name is ',customer_name)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)
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

#if 'submit_is_disabled' not in st.session_state:
#    st.write('True')
#    st.session_state['submit_is_disabled'] = True
    
submit_button = st.button('Submit Order', 'submitorder',  disabled=st.session_state['submit_is_disabled'])

if submit_button:
    if ingredients_list:

        orders_insert = \
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS" + \
        " (name_on_order, ingredients)   VALUES (?, ?)"
        query_params = [customer_name, ' '.join(ingredients_list)]
        
        session.sql(orders_insert,params=query_params).collect()

        st.success('Your Smoothie is ordered, ' + customer_name + '!', icon="✅")