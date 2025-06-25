import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import pickle
from pathlib import Path

user_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/user_data.csv")


usernames= []
user_ids= []
passwords = []
usertypes= []
for user, ids, paswrd, types in zip(user_data.Username, user_data.User_id, user_data.Password, user_data.User_type):
    usernames.append(user)
    user_ids.append(ids)
    passwords.append(paswrd)
    usertypes.append(types)



names= usernames
user_id= user_ids
password= passwords	
role= usertypes
hashed_passwords= stauth.Hasher(password).generate()
file_path= Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
	pickle.dump(hashed_passwords, file)