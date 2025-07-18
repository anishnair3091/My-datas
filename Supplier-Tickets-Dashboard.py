import streamlit as st  
import pandas as pd  
import numpy as np 
import matplotlib.pyplot as plt  
import seaborn as sns; sns.set()
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt 
import matplotlib
from sklearn.preprocessing import LabelEncoder
import datetime
import folium
from streamlit_folium import st_folium
import pickle
from pathlib import Path 
import streamlit_authenticator as stauth


#Page config setup

st.set_page_config('Tickets_Dashboard', layout='wide', initial_sidebar_state= 'collapsed')

st.markdown('''<h3 style= "text-align:left; color:#8C98AF; ">WELCOME TO TICKET DASHBOARD</h3>''', unsafe_allow_html=True)

Home= st.Page('pages/Supplier-Home-page.py', title= 'Home page', icon= '🏡')

if st.sidebar.button('Home', icon= '🏡'):
	st.switch_page(Home)


history_data= pd.read_csv(r'/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/History.csv')


performance_data= history_data[['AMC_Company', 'Ticket_ref', 'Response_time_difference']].groupby(['AMC_Company']).count().reset_index()

performances= performance_data.Response_time_difference/performance_data.Ticket_ref

dfs= performances.to_frame()

perform_data= pd.concat([performance_data, dfs], axis=1)

perform_data.columns= ['AMC_Company', 'Ticket_ref', 'Response_time_difference', 'Performance']

AMC_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/AMC.csv")

times= []
data= history_data[history_data['Status'] == 'Open']
for time in pd.to_datetime(data['Response']):
    current_time = datetime.datetime.now()
    time_diff = time- current_time
    times.append(time_diff.total_seconds())

data['Time_remaining_secs']= times

times1= []
data1= history_data[history_data['Status'] == 'Close']
for time, his in zip(pd.to_datetime(data1['Response']), pd.to_datetime(data1['Actual_Completion_time'])) :
    
    time_diff = time- his
    times1.append(time_diff.total_seconds())

data1['Time_remaining_secs']= times1

history_data = pd.concat([data1, data], axis= 0)

#To distinguish tickets based on SLA status

SLAs = []
for secs in history_data['Time_remaining_secs']:
	if secs > 0:
		SLA= 'SLA met'
		SLAs.append(SLA)
	elif secs <= 0:
		SLA= 'SLA not met'
		SLAs.append(SLA)

history_data['SLA'] = SLAs

dummies = pd.get_dummies(history_data['SLA'])

encoder= LabelEncoder()
encoder.fit(dummies['SLA met'])

history_data['SLA met'] = encoder.transform(dummies['SLA met'])

encoder= LabelEncoder()
encoder.fit(dummies['SLA not met'])
history_data['SLA not met']= encoder.transform(dummies['SLA not met'])

#To extract the integer part from the ticket

ticks= []
for ref in history_data['Ticket_ref']:
    for number in ref.split("/"):
        tick= number
    ticks.append(tick)

history_data['Ticket_num']= ticks

# To extract the week number
week_num= []
for date in pd.to_datetime(history_data['Date']):
    week = date.strftime("%W")
    week_num.append(week)

history_data['Week']= week_num



# To Open & Close columns

dummy_variable = pd.get_dummies(history_data.Status)

encoder= LabelEncoder()
encoder1= LabelEncoder()
encoder.fit(dummy_variable.Close)
encoder1.fit(dummy_variable.Open)
dummy_variable['Close']= encoder.transform(dummy_variable.Close)
dummy_variable['Open']= encoder.transform(dummy_variable.Open)

history_data.Open= dummy_variable.Open
history_data.Close= dummy_variable.Close

Datetime= []
for date, time in zip(history_data['Date'], history_data['Time']):
    my_datetime_str= date + ' ' + time
    my_datetime= pd.to_datetime(my_datetime_str)
    Datetime.append(my_datetime)

history_data['Datetime']= Datetime


team_list= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/BMTS-APP/Service/Team_list.csv", skiprows=1)


user_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/user_data.csv")


option11= st.sidebar.selectbox('Supplier', index= None, options= AMC_data['AMC COMPANY'].unique(), placeholder='Select the supplier name', accept_new_options= True)
# User Authentication

def authentication_status():
    users= []
    user_ids= []
    usertypes= []
    for user, ids, types in zip(user_data.Username, user_data.User_id, user_data.User_type):
        users.append(user)
        user_ids.append(ids)
        usertypes.append(types)

    # Load credentials except passwords

    names= users
    usernames= user_ids
    usertype= usertypes

    # Load passwords

    file_path = Path("/Users/anishmnair/Desktop/Streamlit/My_new_app/BMTS-APP/secrets/hashed_pw.pkl")
    with file_path.open('rb') as file:
        hashed_passwords= pickle.load(file)

    # Transform credentials as a dictionary

    credentials = {"usernames":{}}
    for un, name, pswd, char in zip(usernames, names, hashed_passwords, usertype):   
        user_dict = {"name":name, "password" : pswd, "role":char}
        credentials["usernames"].update({un:user_dict})

    authenticator= stauth.Authenticate(credentials, "", "", cookie_expiry_days=30)
    name, authentication_status, username= authenticator.login('main', 'Login')
    return authentication_status

# Defining name

if authentication_status() == True:
    name= st.session_state["name"]
    st.sidebar.write(f'Welcome **{name}**')
    
def user_type():
    data = user_data[user_data['Username'] == name]
    for user in data.User_type:
        usertype= user
    return usertype

def load_data(nrows):
	data = pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/History.csv")
	if option11 != None:
		data1 = data[data['AMC_Company'] == option11]
		return data1 
	elif option11 == None:
		data1 = data 
		return data1


data = load_data(1000)


def data_table(nrows):
	data_table= data[['AMC_Company', 'Close', 'Open']].groupby(['AMC_Company']).sum().reset_index()
	return data_table


data_table= data_table(100)

def trouble_data(nrows):
	trouble_data= data['Troubles_Name'].value_counts().to_frame().reset_index()
	trouble_data = trouble_data.head(6)
	return trouble_data
	

def project_trouble(nrows):
	project_trouble= data['Project'].value_counts().to_frame().reset_index()
	project_trouble= project_trouble.head(6)
	return project_trouble
	

trouble= trouble_data(13)
project= project_trouble(13)


def handle_action(action):
	st.page_link("pages/BMTS-view tickets.py")




def area_chart():
	hist_sum_person = data[['Date', 'AMC_Company', 'Status']].groupby(['Date', 'AMC_Company']).count().reset_index()
	fig= plt.figure(figsize=(4, 3))
	fig = px.area(hist_sum_person, x = 'Date', y = 'Status', color= 'AMC_Company', line_group= 'AMC_Company')
	return fig 	

def view_data(k):
	view_data= data.iloc[[k]]
	return view_data
	

def top_performer():
	data = perform_data[perform_data['Performance'] == perform_data['Performance'].max()]
	for person in data.AMC_Company:
		performer= person 
	return performer

		
# Facetted Subplots

history_data_total = data[['AMC_Company', 'Status', 'Ticket_ref', 'Weekday', 'Week']].groupby(['AMC_Company', 'Status', 'Week','Weekday']).count().reset_index()

history_data_total_week = history_data_total[history_data_total['Week'] == history_data_total['Week'].max()]

total_tickets= data[['Day', 'Ticket_ref']].groupby(['Day']).count().reset_index()

open_tickets= data[['Day', 'Open']].groupby(['Day']).sum().reset_index()

close_tickets= data[['Day', 'Close']].groupby(['Day']).sum().reset_index()

progress_data= data[data['Status'] == 'In progress']

progress_tickets = progress_data[['Day', 'Status']].groupby(['Day']).count().reset_index()	

#To display SLA status chart and table

SLA_summary= load_data(100)[['AMC_Company', 'Ticket_ref', "Status", 'SLA', 'Day', 'Open', 'Close', 'SLA met', 'SLA not met']].groupby(['AMC_Company', 'Ticket_ref', 'Status', 'SLA']).sum().reset_index()

SLA_table= SLA_summary[['AMC_Company', 'Open', 'Close', 'SLA met', 'SLA not met']].groupby(['AMC_Company']).sum().reset_index()

SLA_chart= SLA_summary[[ 'Open', 'Close', 'Day', 'SLA met', 'SLA not met']].groupby(['Day']).sum().reset_index()

data= load_data(100)
open_data = data[data['Status'] == 'Open']

data1 = open_data.sort_values('Date', ascending=False, axis=0, ignore_index= True)

if st.session_state['authentication_status']:
	if user_type() == 'customer' or user_type() == 'Admin':


		tab1, tab2 = st.tabs(['Dashboard', 'View_tickets'])




		with tab1:

			

			col6, col7, col8, col9, col10, col18 = st.columns(6, gap= 'small', border=True)

			col11, col12, col13 = st.columns([2, 5, 3], gap= 'small', border=True)

			col14, col15, col16, col17 = st.columns(4, gap= 'small', border=True)

			with col11:
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Issue by Category</h6>", unsafe_allow_html=True)
				raw_data= st.checkbox("Raw data")
				if raw_data:
					st.data_editor(
					trouble,
					hide_index= True)
				else:
					fig= px.bar(trouble, x = 'count', y= 'Troubles_Name', text= 'Troubles_Name', orientation= "h", width= 300, height= 350)
					fig.update_layout(barcornerradius= 10, yaxis= {'categoryorder':'total ascending'})
					fig.update_yaxes(showticklabels=False)
					fig.update_traces(textfont_size=12, textfont_weight= 'bold')
					st.plotly_chart(fig, use_container_width=False)
			

			with col12:
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Tickets Details</h6>", unsafe_allow_html=True)
				col1, col2= st.columns(2)
				
				sunburst_chart= col1.checkbox("Sunburst Chart")
				AMC_Company = col2.checkbox("AMC_Company")
			
				if sunburst_chart:
					
					fig = px.sunburst(data, path= ['AMC_Company', 'Month', 'Priority', 'Status'], color = 'AMC_Company')
					st.plotly_chart(fig, use_container_width= False)
				
				elif AMC_Company:
					
					row1= st.columns(1)
					for col in row1:
						container= col.container(border=False)	
						
						selection = container.pills('AMC_Company', options= data.AMC_Company.unique())
						if selection:
							chart_data= data[data['AMC_Company'] == selection]
						else:
							chart_data = data

						col1, col2, col3, col4 = st.columns(4, border=False)
						with col1:
							option1= st.checkbox("Total")
						
						with col2:
							option2= st.checkbox("Open") 

						with col3:
							option3= st.checkbox("Resolved")

						with col4: 
							option4= st.checkbox("In progress")


						if option1:
							
							data_total= chart_data[['Day', 'Ticket_ref']].groupby(['Day']).count().reset_index()
							data_total.columns= ['Day', 'Count']
							data_total_max= data_total[data_total['Count'] == data_total['Count'].max()]
							Day= []
							Count= []
							for day in data_total_max.Day:
								Day= day
							for count in data_total_max['Count']:
								Count= count
							fig= plt.figure(figsize=(6, 3))
							plt.plot(data_total.Day, data_total.Count, color= 'black', linestyle='--')
							plt.bar(data_total.Day, data_total.Count, alpha= 0.2, width=0.5)
							matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
							plt.xlabel('Day')
							plt.ylabel('Ticket Count')
							plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
							plt.annotate('Maximum complaints reported', xy= (Day, Count), va='bottom', ha='left')
							st.plotly_chart(fig, use_container_width=False, height= 100) 
						elif option2:
							data_open= chart_data[['Day', 'Open']].groupby(['Day']).sum().reset_index()
							data_open.columns= ['Day', 'Count']
							data_open_max= data_open[data_open['Count'] == data_open['Count'].max()]
							Day= []
							Count= []
							for day in data_open_max.Day:
								Day= day
							for count in data_open_max['Count']:
								Count= count
							fig= plt.figure(figsize=(6, 3))
							plt.plot(data_open.Day, data_open.Count, color= 'black', linestyle='--')
							plt.bar(data_open.Day, data_open.Count, alpha= 0.2, width=0.5)
							matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
							plt.xlabel('Day')
							plt.ylabel('Ticket Count')
							plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
							plt.annotate('Maximum Unresolved Tickets', xy= (Day, Count), va='bottom', ha='left')
							st.plotly_chart(fig, use_container_width=False, height= 100)
							
						elif option3:
							data_resolved= chart_data[['Day', 'Close']].groupby(['Day']).sum().reset_index()
							data_resolved.columns= ['Day', 'Count']
							data_resolved_max= data_resolved[data_resolved['Count'] == data_resolved['Count'].max()]
							Day= []
							Count= []
							for day in data_resolved_max.Day:
								Day= day
							for count in data_resolved_max['Count']:
								Count= count
							fig= plt.figure(figsize=(6, 3))
							plt.plot(data_resolved.Day, data_resolved.Count, color= 'black', linestyle='--')
							plt.bar(data_resolved.Day, data_resolved.Count, alpha= 0.2, width=0.5)
							matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
							plt.xlabel('Day')
							plt.ylabel('Ticket Count')
							plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
							plt.annotate('Maximum Resolved Tickets', xy= (Day, Count), va='bottom', ha='left')
							st.plotly_chart(fig, use_container_width=False, height= 100)
							
						elif option4:
							data1= chart_data[chart_data['Status'] == 'In progress']
							data_progress= data1[['Day', 'Status']].groupby(['Day']).count().reset_index()
							data_progress.columns= ['Day', 'Count']
							data_progress_max= data_progress[data_progress['Count'] == data_progress['Count'].max()]
							Day= []
							Count= []
							for day in data_progress_max.Day:
								Day= day
							for count in data_progress_max['Count']:
								Count= count
							fig= plt.figure(figsize=(6, 3))
							plt.plot(data_progress.Day, data_progress.Count, color= 'black', linestyle='--')
							plt.bar(data_progress.Day, data_progress.Count, alpha= 0.2, width=0.5)
							matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
							plt.xlabel('Day')
							plt.ylabel('Ticket Count')
							plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
							plt.annotate('Maximum Resolved Tickets', xy= (Day, Count), va='bottom', ha='left')
							st.plotly_chart(fig, use_container_width=False, height= 100)
						 
						else:
							data_total= chart_data[['Day', 'Ticket_ref']].groupby(['Day']).count().reset_index()
							data_total.columns= ['Day', 'Count']
							data_total_max= data_total[data_total['Count'] == data_total['Count'].max()]
							Day= []
							Count= []
							for day in data_total_max.Day:
								Day= day
							for count in data_total_max['Count']:
								Count= count
							fig= plt.figure(figsize=(6, 3))
							plt.plot(data_total.Day, data_total.Count, color= 'black', linestyle='--')
							plt.bar(data_total.Day, data_total.Count, alpha= 0.2, width=0.5)
							matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
							plt.xlabel('Day')
							plt.ylabel('Ticket Count')
							plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
							plt.annotate('Maximum complaints reported', xy= (Day, Count), va='bottom', ha='left')
							st.plotly_chart(fig, use_container_width=False, height= 100)
				else:
					col1, col2, col3, col4 = st.columns(4, border=False)
					with col1:
						option1= st.checkbox("Total")
					
					with col2:
						option2= st.checkbox("Open") 

					with col3:
						option3= st.checkbox("Resolved")

					with col4: 
						option4= st.checkbox("In progress")

					chart_data = data

					if option1:
						
						data_total= chart_data[['Day', 'Ticket_ref']].groupby(['Day']).count().reset_index()
						data_total.columns= ['Day', 'Count']
						data_total_max= data_total[data_total['Count'] == data_total['Count'].max()]
						Day= []
						Count= []
						for day in data_total_max.Day:
							Day= day
						for count in data_total_max['Count']:
							Count= count
						fig= plt.figure(figsize=(6, 3))
						plt.plot(data_total.Day, data_total.Count, color= 'black', linestyle='--')
						plt.bar(data_total.Day, data_total.Count, alpha= 0.2, width=0.5)
						matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
						plt.xlabel('Day')
						plt.ylabel('Ticket Count')
						plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
						plt.annotate('Maximum complaints reported', xy= (Day, Count), va='bottom', ha='left')
						st.plotly_chart(fig, use_container_width=False, height= 100) 
					elif option2:
						data_open= chart_data[['Day', 'Open']].groupby(['Day']).sum().reset_index()
						data_open.columns= ['Day', 'Count']
						data_open_max= data_open[data_open['Count'] == data_open['Count'].max()]
						Day= []
						Count= []
						for day in data_open_max.Day:
							Day= day
						for count in data_open_max['Count']:
							Count= count
						fig= plt.figure(figsize=(6, 3))
						plt.plot(data_open.Day, data_open.Count, color= 'black', linestyle='--')
						plt.bar(data_open.Day, data_open.Count, alpha= 0.2, width=0.5)
						matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
						plt.xlabel('Day')
						plt.ylabel('Ticket Count')
						plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
						plt.annotate('Maximum Unresolved Tickets', xy= (Day, Count), va='bottom', ha='left')
						st.plotly_chart(fig, use_container_width=False, height= 100)
						
					elif option3:
						data_resolved= chart_data[['Day', 'Close']].groupby(['Day']).sum().reset_index()
						data_resolved.columns= ['Day', 'Count']
						data_resolved_max= data_resolved[data_resolved['Count'] == data_resolved['Count'].max()]
						Day= []
						Count= []
						for day in data_resolved_max.Day:
							Day= day
						for count in data_resolved_max['Count']:
							Count= count
						fig= plt.figure(figsize=(6, 3))
						plt.plot(data_resolved.Day, data_resolved.Count, color= 'black', linestyle='--')
						plt.bar(data_resolved.Day, data_resolved.Count, alpha= 0.2, width=0.5)
						matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
						plt.xlabel('Day')
						plt.ylabel('Ticket Count')
						plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
						plt.annotate('Maximum Resolved Tickets', xy= (Day, Count), va='bottom', ha='left')
						st.plotly_chart(fig, use_container_width=False, height= 100)
						
					elif option4:
						data1= chart_data[chart_data['Status'] == 'In progress']
						data_progress= data1[['Day', 'Status']].groupby(['Day']).count().reset_index()
						data_progress.columns= ['Day', 'Count']
						data_progress_max= data_progress[data_progress['Count'] == data_progress['Count'].max()]
						Day= []
						Count= []
						for day in data_progress_max.Day:
							Day= day
						for count in data_progress_max['Count']:
							Count= count
						fig= plt.figure(figsize=(6, 3))
						plt.plot(data_progress.Day, data_progress.Count, color= 'black', linestyle='--')
						plt.bar(data_progress.Day, data_progress.Count, alpha= 0.2, width=0.5)
						matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
						plt.xlabel('Day')
						plt.ylabel('Ticket Count')
						plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
						plt.annotate('Maximum Resolved Tickets', xy= (Day, Count), va='bottom', ha='left')
						st.plotly_chart(fig, use_container_width=False, height= 100)
					 
					else:
						data_total= chart_data[['Day', 'Ticket_ref']].groupby(['Day']).count().reset_index()
						data_total.columns= ['Day', 'Count']
						data_total_max= data_total[data_total['Count'] == data_total['Count'].max()]
						Day= []
						Count= []
						for day in data_total_max.Day:
							Day= day
						for count in data_total_max['Count']:
							Count= count
						fig= plt.figure(figsize=(6, 3))
						plt.plot(data_total.Day, data_total.Count, color= 'black', linestyle='--')
						plt.bar(data_total.Day, data_total.Count, alpha= 0.2, width=0.5)
						matplotlib.rcParams['axes.edgecolor'] = '#8C98AF'
						plt.xlabel('Day')
						plt.ylabel('Ticket Count')
						plt.annotate('', xy= (Day, Count), xytext= (Day, Count), arrowprops=dict(arrowstyle= '->', connectionstyle='arc3', color='blue', lw =2))
						plt.annotate('Maximum complaints reported', xy= (Day, Count), va='bottom', ha='left')
						st.plotly_chart(fig, use_container_width=False, height= 100)
							


				
			with col13:
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>SLA status</h6>", unsafe_allow_html=True)
				st.write(f"`Current Week's Top Performer:` **`{top_performer()}`**")
				sla_table= st.checkbox('Raw data', key= 'sla')
				if sla_table:
					
					st.data_editor(SLA_table, hide_index=True)
					
				else:
					
					st.bar_chart(SLA_summary, y = ['SLA met', 'SLA not met'], x = 'AMC_Company', color= 'SLA', x_label= 'Ticket Count', horizontal= True, height= 350, use_container_width=True)
					
				
				
				

				
				

			with col14:
				col1, col2, col3 = st.columns(3)
				
				table = col1.checkbox('Table', key= 'summary')
				Open = col2.checkbox('Open', key= 'open')
				Close= col3.checkbox('Close', key= 'close')
				if table:
					st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Tickets Summary</h6>", unsafe_allow_html=True)
					st.data_editor(
					data_table,
					hide_index= True)
				
			 
				
				elif Open:
					st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Unresolved Tickets</h6>", unsafe_allow_html=True)
					employee= data_table.AMC_Company.unique()
					ticket_status= data_table.Open
					explode=[]
					for serv in employee:
						explode.append(0.05)
					
					colors= ['#94B5A2', '#ACCAE0', '#DCBCB6', '#5D5D7B', '#E4A1D7', '#6D4A66', '#EA7B78', '#E2EA78']

					#pie chart
					plt.pie(ticket_status, labels= employee, colors= colors, autopct= "%1.1f%%", pctdistance=0.85, explode=explode)

					#center circle
					center_circle= plt.Circle((0, 0), 0.65, fc= 'white')
					fig= plt.gcf()
					fig.gca().add_artist(center_circle)
					st.pyplot(fig)

				
			 
				
				elif Close:
					st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Resolved Tickets</h6>", unsafe_allow_html=True)
					employee= data_table.AMC_Company.unique()
					ticket_status= data_table.Close
					explode= []
					for serv in employee:
						explode.append(0.05)
					colors= ['#94B5A2', '#ACCAE0', '#DCBCB6', '#5D5D7B', '#E4A1D7', '#6D4A66', '#EA7B78', '#E2EA78']

					#pie chart
					plt.pie(ticket_status, labels= employee, colors= colors, autopct= "%1.1f%%", pctdistance=0.85, explode=explode)

					#center circle
					center_circle= plt.Circle((0, 0), 0.65, fc= 'white')
					fig= plt.gcf()
					fig.gca().add_artist(center_circle)
					st.pyplot(fig)

				else:
					st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Unresolved Tickets</h6>", unsafe_allow_html=True)
					employee= data_table.AMC_Company.unique()
					ticket_status= data_table.Open
					explode= []
					for serv in employee:
						explode.append(0.05)
					colors= ['#94B5A2', '#ACCAE0', '#DCBCB6', '#5D5D7B', '#E4A1D7', '#6D4A66', '#EA7B78', '#E2EA78']

					#pie chart
					plt.pie(ticket_status, labels= employee, colors= colors, autopct= "%1.1f%%", pctdistance=0.85, explode=explode)

					#center circle
					center_circle= plt.Circle((0, 0), 0.65, fc= 'white')
					fig= plt.gcf()
					fig.gca().add_artist(center_circle)
					st.pyplot(fig)
			




				
				
				
			with col15:
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Priority</h6>", unsafe_allow_html=True)
				priority_data= history_data[['Priority', 'Open', 'Close']].groupby(['Priority']).sum().reset_index()
				fig= px.bar(priority_data, x = ['Open', 'Close'], y = 'Priority', orientation= "h", height= 300, width=500, text= 'Priority')
				fig.update_yaxes(showticklabels=False)
				fig.update_layout(barcornerradius= 5)
				fig.update_traces(textfont_weight= 'bold')
				st.plotly_chart(fig)

				
				

			with col16:
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Top 6 projects with most Troubles</h6>", unsafe_allow_html=True)
				st.data_editor(
					project,
					hide_index= True)
			

			with col17:
				
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Customer Happiness</h6>", unsafe_allow_html=True)


			with col6:
				row1 = st.columns(1)
				for col in row1:

					col1, col2= st.columns(2, gap= 'small', border=False)
			
					col1.metric('Total tickets', value= history_data['Ticket_ref'].count(), border=False)
					col2.bar_chart(total_tickets, x = 'Day', y = 'Ticket_ref', height= 120, x_label= None, y_label= None, color= '#BACBEC')

			with col7:
				row1= st.columns(1)
				for col in row1:
					col1, col2= st.columns(2, gap= 'small', border=False)
					col1.metric('Open tickets', value= history_data['Open'].sum(), border=False)
					col2.bar_chart(open_tickets, x='Day', y= 'Open', height=120, x_label=None, y_label=None, color= '#BACBEC')

			with col8:
				row1= st.columns(1)
				for col in row1:
					col1, col2= st.columns(2, gap='small', border=False)
					col1.metric('Resolved', value= history_data['Close'].sum(), border=False)
					col2.bar_chart(close_tickets, x = 'Day', y= 'Close', height=120, x_label=None, y_label=None, color= '#BACBEC')

			with col9:
				row1= st.columns(1)
				for col in row1:
					col1, col2= st.columns(2, gap= 'small', border=False)
					col1.metric('In progress', value= progress_data['Status'].count(), border=False)
					col2.bar_chart(progress_tickets, x= 'Day', y= 'Status', height=120, x_label=None, y_label=None, color= '#BACBEC')

			with col10:
				row1= st.columns(1)
				for col in row1:
					col1, col2= st.columns(2, gap= 'small', border=False)
					col1.metric('SLA', value= history_data['SLA met'].sum(), delta= (history_data['SLA met'].sum()- history_data['Ticket_ref'].count()).astype('float') ,border=False)
					col2.bar_chart(SLA_chart, x='Day', y='SLA met', height=120, x_label=None, y_label=None, color= '#BACBEC')


		with tab2:

			data= load_data(100)

			uae_map= folium.Map([23.4241, 53.8478], zoom_start=8)

			for lat, lng, label in zip(data.Site_lat, data.Site_long, data['Project']):
				folium.vector_layers.CircleMarker(
					[lat, lng],
					radius= 15,
					fill= True,
					fill_color='blue',
					color= 'yellow',
					fill_opacity= 0.6,
					popup=label).add_to(uae_map)

			st_folium(uae_map, width= 1500, height= 500)

			

			st.markdown('''<h5 style= "text-align:center; color:white; background-color:#747581;">ALL OPEN TICKETS</h5>''', unsafe_allow_html=True)
			container = st.container(height= 500, border=True)

			
			
			with container:

				col1, col2, col3, col4, col5 = st.columns(5)

				data1 = data.sort_values('Datetime', axis=0, ascending= False, ignore_index=True)

				with col1:

					for k in range(0, (len(data1))//5):
						if data1['Priority'][k] == 'P1':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :red-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')
						
						elif data1['Priority'][k] == 'P2':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :green-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')

						elif data1['Priority'][k] == 'P3':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :blue-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')


				with col2:

					for k in range((len(data1))//5, ((len(data1))//5)+ (len(data1)//5)):
						if data1['Priority'][k] == 'P1':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :red-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')
						
						elif data1['Priority'][k] == 'P2':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :green-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')

						elif data1['Priority'][k] == 'P3':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :blue-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')
				
				
				with col3:

					for k in range(((len(data1)//5)+ (len(data1)//5)), (len(data1) - ((len(data1)//5) + (len(data1)//5)))):
						if data1['Priority'][k] == 'P1':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :red-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')
						
						elif data1['Priority'][k] == 'P2':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :green-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')

						elif data1['Priority'][k] == 'P3':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :blue-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')

				with col4:

					for k in range((len(data1) - ((len(data1)//5) + (len(data1)//5))), (len(data1) - len(data1)//5)):
						if data1['Priority'][k] == 'P1':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :red-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')
						
						elif data1['Priority'][k] == 'P2':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :green-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')

						elif data1['Priority'][k] == 'P3':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :blue-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')

				with col5:

					for k in range((len(data1) - len(data1)//5), len(data1)):
						if data1['Priority'][k] == 'P1':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :red-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')
						
						elif data1['Priority'][k] == 'P2':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :green-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')

						elif data1['Priority'][k] == 'P3':
							option=  st.button(f''':red-background[```{data1.Ticket_ref[k]}```] :blue-background[```{data1.Status[k]}```]\n :blue-badge[**{data1.Priority[k]}**]''', key=k)
							if option:
								history_1 = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								
								df = history_1
								st.session_state.df = df
								st.session_state['keys101'] = history_data[history_data['Ticket_ref'] == data1.Ticket_ref[k]]
								st.switch_page('pages/Customer-view-tickets.py')


			container= st.container(height= 250, border=True)
			
			with container:
				col6, col7 = st.columns(2)

				with col6:

					st.markdown('''<h5 style= "text-align:center; color:white; background-color:#DEADAD;"> ENQUIRIES RESPONSE TIME EXPIRED</h5>''', unsafe_allow_html=True)
					container= st.container(height=220, border=True)
					with container:
						
						row1= st.columns(1)

				with col7:

					st.markdown('''<h5 style= "text-align:center; color:white; background-color:#E6E593;"> ENQUIRIES RESPONSE TIME ABOUT TO EXPIRE</h5>''', unsafe_allow_html=True)
					container= st.container(height=220, border=True)
					with container:
						
						row1= st.columns(1)

		
