import pandas as pandas
import streamlit as st 
import streamlit_authenticator as stauth 
from pathlib import Path  
import pickle


#Page config setup



st.markdown('''<h3 style= "text-align:left; color:#8C98AF; ">WELCOME TO CONTRACTOR PERFORMANCE DASHBOARD</h3>''', unsafe_allow_html=True)

Home= st.Page('pages/Home-page.py', title= 'Home page', icon= '🏡')

if st.sidebar.button('Home', icon= '🏡'):
	st.switch_page(Home)

