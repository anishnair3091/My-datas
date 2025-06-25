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


st.markdown('''<h3 style= "text-align:left; color:#8C98AF; ">ENQUIRIES DASHBOARD</h3>''', unsafe_allow_html=True)

Home= st.Page('pages/Supplier-Home-page.py', title= 'Home page', icon= '🏡')

Enquiry_page = st.Page('pages/Supplier-Enquiries-Dashboard.py', title= 'Sales Dashboard', icon = '📈')

if st.sidebar.button('Home', icon= '🏡'):
	st.switch_page(Home)


enquiry_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/enquiry_data.csv")


group = enquiry_data[['Company', 'SLA met', 'SLA not met']].groupby(['Company']).sum().reset_index()

group1 = enquiry_data[['Company', 'Enquiry_ref']].groupby(['Company']).count().reset_index()

group['Enquiry_count']= group1['Enquiry_ref']

group['SLA marks']= group['SLA met']/group['Enquiry_count']

AMC_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/AMC.csv")


times2= []
data2= enquiry_data[enquiry_data['Enquiry status'] == 'Quoted']
for time, his in zip(pd.to_datetime(data2['Response']), pd.to_datetime(data2['Actual_Completion_time'])) :
    
    time_diff = time- his
    times2.append(time_diff.total_seconds())

data2['Time_remaining_secs']= times2



#To distinguish tickets based on SLA status

SLAs = []
for secs in enquiry_data['Time_remaining_secs']:
	if secs > 0:
		SLA= 'SLA met'
		SLAs.append(SLA)
	elif secs <= 0:
		SLA= 'SLA not met'
		SLAs.append(SLA)

enquiry_data['SLA'] = SLAs

dummy_variable= pd.get_dummies(enquiry_data['Enquiry status'])
encoder1= LabelEncoder()
encoder2= LabelEncoder()
encoder3= LabelEncoder()

encoder1.fit(dummy_variable['Under review'])
encoder2.fit(dummy_variable['Moved for estimation'])
encoder3.fit(dummy_variable['Quoted'])
enquiry_data['Under review']= encoder1.transform(dummy_variable['Under review'])
enquiry_data['Moved for estimation']= encoder2.transform(dummy_variable['Moved for estimation'])
enquiry_data['Quoted'] = encoder3.transform(dummy_variable['Quoted'])

dummy_variable2= pd.get_dummies(enquiry_data['SLA'])
encoder3= LabelEncoder()
encoder4= LabelEncoder()

encoder3.fit(dummy_variable2['SLA met'])
encoder4.fit(dummy_variable2['SLA not met'])
enquiry_data['SLA met'] = encoder3.transform(dummy_variable2['SLA met'])
enquiry_data['SLA not met'] = encoder4.transform(dummy_variable2['SLA not met'])

#To extract the integer part from the ticket

ticks= []
for ref in enquiry_data['Enquiry_ref']:
    for number in ref.split("/"):
        tick= number
    ticks.append(tick)

enquiry_data['Ticket_num']= ticks

# To extract the week number
week_num= []
for date in pd.to_datetime(enquiry_data['Created date']):
    week = date.strftime("%W")
    week_num.append(week)

enquiry_data['Week']= week_num




Datetime= []
for date, time in zip(enquiry_data['Created date'], enquiry_data['Time']):
    my_datetime_str= date + ' ' + time
    my_datetime= pd.to_datetime(my_datetime_str)
    Datetime.append(my_datetime)

enquiry_data['Datetime']= Datetime


team_list= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/BMTS-APP/Service/Team_list.csv", skiprows=1)


user_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/user_data.csv")



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
	data = pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/enquiry_data.csv")
	
	data1 = data[data['Company'] == name]
	return data1 
	


data = load_data(1000)


def data_table(nrows):
	data_table= data[['Company', 'Under review', 'Moved for estimation', 'Quoted']].groupby(['Company']).sum().reset_index()
	return data_table


data_table= data_table(100)

def job_type():
	job_data= data['Job type'].value_counts().to_frame().reset_index()
	return job_data
	

def enq_company():
	enqcompany= data['Company'].value_counts().to_frame().reset_index()
	
	return enqcompany
	

jobtype= job_type()
company= enq_company()


def handle_action(action):
	st.page_link("pages/BMTS-view tickets.py")




def area_chart():
	hist_sum_person = data[['Date', 'Company', 'Status']].groupby(['Date', 'Company']).count().reset_index()
	fig= plt.figure(figsize=(4, 3))
	fig = px.area(hist_sum_person, x = 'Date', y = 'Status', color= 'Company', line_group= 'Company')
	return fig 	

def view_data(k):
	view_data= data.iloc[[k]]
	return view_data
	

def top_performer():
	data = group[group['SLA marks'] == group['SLA marks'].max()]
	for company in data.Company:
		performer= company 
	return performer

		
# Facetted Subplots

enquiry_data_total = data[['Company', 'Enquiry status', 'Enquiry_ref', 'Monthname', 'Month']].groupby(['Company', 'Enquiry status', 'Monthname','Month']).count().reset_index()

enquiry_data_total_month = enquiry_data_total[enquiry_data_total['Month'] == enquiry_data_total['Month'].max()]

total_enquiries= data[['Day', 'Enquiry_ref']].groupby(['Day']).count().reset_index()

awaiting_response= data[['Day', 'Under review']].groupby(['Day']).sum().reset_index()

quote_received= data[['Day', 'Quoted']].groupby(['Day']).sum().reset_index()

progress_data= data[['Day', 'Moved for estimation']].groupby(['Day']).sum().reset_index()

	

#To display SLA status chart and table

SLA_summary= load_data(100)[['Company', 'Enquiry_ref', "Enquiry status", 'SLA', 'Day', 'Under review', 'Moved for estimation', 'Quoted', 'SLA met', 'SLA not met']].groupby(['Company', 'Enquiry_ref', 'Enquiry status', 'SLA']).sum().reset_index()

SLA_table= SLA_summary[['Company', 'Under review', 'Moved for estimation', 'Quoted', 'SLA met', 'SLA not met']].groupby(['Company']).sum().reset_index()

SLA_chart= SLA_summary[[ 'Under review', 'Moved for estimation', 'Quoted', 'Day', 'SLA met', 'SLA not met']].groupby(['Day']).sum().reset_index()

data= load_data(100)
open_data = data[data['Enquiry status'] == 'Under review']

data1 = open_data.sort_values('Created date', ascending=False, axis=0, ignore_index= True)

if st.session_state['authentication_status']:
	if user_type() == 'supplier' or user_type() == 'Admin':


		tab1, tab2 = st.tabs(['Dashboard', 'View_tickets'])




		with tab1:

			

			col6, col7, col8, col9, col10, col18 = st.columns(6, gap= 'small', border=True)

			col11, col12, col13 = st.columns([2, 5, 3], gap= 'small', border=True)

			col14, col15, col16 = st.columns([3, 4, 3], gap= 'small', border=True)

			with col11:
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Job by Category</h6>", unsafe_allow_html=True)
				raw_data= st.checkbox("Raw data")
				if raw_data:
					st.data_editor(
					jobtype,
					hide_index= True)
				else:
					fig= px.bar(jobtype, x = 'count', y= 'Job type', text= 'Job type', orientation= "h", width= 300, height= 350)
					fig.update_layout(barcornerradius= 10, yaxis= {'categoryorder':'total ascending'})
					fig.update_yaxes(showticklabels=False)
					fig.update_traces(textfont_size=12, textfont_weight= 'bold')
					st.plotly_chart(fig, use_container_width=False)
			

			with col12:
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Enquiry Details</h6>", unsafe_allow_html=True)
				col1, col2= st.columns(2)
				
				sunburst_chart= col1.checkbox("Sunburst Chart")
				Company = col2.checkbox("Company")
			
				if sunburst_chart:
					
					fig = px.sunburst(data, path= ['Company', 'Month', 'Job type', 'Enquiry status'], color = 'Company')
					st.plotly_chart(fig, use_container_width= False)
				
				elif Company:
					
					row1= st.columns(1)
					for col in row1:
						container= col.container(border=False)	
						
						selection = container.pills('Company', options= data.Company.unique())
						if selection:
							chart_data= data[data['Company'] == selection]
						else:
							chart_data = data

						col1, col2, col3, col4 = st.columns(4, border=False)
						with col1:
							option1= st.checkbox("Total")
						
						with col2:
							option2= st.checkbox("Awaiting Response") 

						with col3:
							option3= st.checkbox("Quoted")

						with col4: 
							option4= st.checkbox("In progress")


						if option1:
							
							data_total= chart_data[['Day', 'Enquiry_ref']].groupby(['Day']).count().reset_index()
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
							data_open= chart_data[['Day', 'Under review']].groupby(['Day']).sum().reset_index()
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
							plt.annotate('Maximum Unresolved Enquiries', xy= (Day, Count), va='bottom', ha='left')
							st.plotly_chart(fig, use_container_width=False, height= 100)
							
						elif option3:
							data_resolved= chart_data[['Day', 'Quoted']].groupby(['Day']).sum().reset_index()
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
							plt.annotate('Maximum Quoted Enquiries', xy= (Day, Count), va='bottom', ha='left')
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
							data_total= chart_data[['Day', 'Enquiry_ref']].groupby(['Day']).count().reset_index()
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
						
						data_total= chart_data[['Day', 'Enquiry_ref']].groupby(['Day']).count().reset_index()
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
						data_open= chart_data[['Day', 'Under review']].groupby(['Day']).sum().reset_index()
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
						plt.annotate('Maximum non-responded Enquiries', xy= (Day, Count), va='bottom', ha='left')
						st.plotly_chart(fig, use_container_width=False, height= 100)
						
					elif option3:
						data_resolved= chart_data[['Day', 'Quoted']].groupby(['Day']).sum().reset_index()
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
						plt.annotate('Maximum Completed Enquiries', xy= (Day, Count), va='bottom', ha='left')
						st.plotly_chart(fig, use_container_width=False, height= 100)
						
					elif option4:
						data1= chart_data[chart_data['Enquiry status'] == 'Moved for estimation']
						data_progress= data1[['Day', 'Enquiry status']].groupby(['Day']).count().reset_index()
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
						plt.annotate('Maximum Enquiries moved for estimation', xy= (Day, Count), va='bottom', ha='left')
						st.plotly_chart(fig, use_container_width=False, height= 100)
					 
					else:
						data_total= chart_data[['Day', 'Enquiry_ref']].groupby(['Day']).count().reset_index()
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
					
					st.bar_chart(SLA_summary, y = ['SLA met', 'SLA not met'], x = 'Company', color= 'SLA', x_label= 'Ticket Count', horizontal= True, height= 350, use_container_width=True)
					
				
				
				

				
				

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
					st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Enquiries</h6>", unsafe_allow_html=True)
					employee= data_table.Company.unique()
					ticket_status= data_table['Under review']
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
					st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Completed Enquiries</h6>", unsafe_allow_html=True)
					employee= data_table.Company.unique()
					ticket_status= data_table['Quoted']
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
					st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Pending Enquiries</h6>", unsafe_allow_html=True)
					employee= data_table.Company.unique()
					ticket_status= data_table['Under review']
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
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>System</h6>", unsafe_allow_html=True)
				system_data= enquiry_data[['System', 'Under review', 'Quoted']].groupby(['System']).sum().reset_index()
				fig= px.bar(system_data, x = ['Under review', 'Quoted'], y = 'System', orientation= "h", height= 300, width=500, text= 'System')
				fig.update_yaxes(showticklabels=False)
				fig.update_layout(barcornerradius= 5)
				fig.update_traces(textfont_weight= 'bold')
				st.plotly_chart(fig)

				
				

			with col16:
				st.markdown("<h6 style= 'text-align: left; color: 'black'; font-size: 5px'>Companies with most enquiries handled</h6>", unsafe_allow_html=True)
				st.data_editor(
					company,
					hide_index= True)
			

			

			with col6:
				row1 = st.columns(1)
				for col in row1:

					col1, col2= st.columns(2, gap= 'small', border=False)
			
					col1.metric('Total Enquiries', value= data['Enquiry_ref'].count(), border=False)
					col2.bar_chart(total_enquiries, x = 'Day', y = 'Enquiry_ref', height= 120, x_label= None, y_label= None, color= '#BACBEC')

			with col7:
				row1= st.columns(1)
				for col in row1:
					col1, col2= st.columns(2, gap= 'small', border=False)
					col1.metric('Awaiting Response', value= data['Under review'].sum(), border=False)
					col2.bar_chart(awaiting_response, x='Day', y= 'Under review', height=120, x_label=None, y_label=None, color= '#BACBEC')

			with col8:
				row1= st.columns(1)
				for col in row1:
					col1, col2= st.columns(2, gap='small', border=False)
					col1.metric('Completed', value= data['Quoted'].sum(), border=False)
					col2.bar_chart(quote_received, x = 'Day', y= 'Quoted', height=120, x_label=None, y_label=None, color= '#BACBEC')

			with col9:
				row1= st.columns(1)
				for col in row1:
					col1, col2= st.columns(2, gap= 'small', border=False)
					col1.metric('In progress', value= data['Moved for estimation'].sum(), border=False)
					col2.bar_chart(progress_data, x= 'Day', y= 'Moved for estimation', height=120, x_label=None, y_label=None, color= '#BACBEC')


			with col10:
				row1= st.columns(1)
				for col in row1:
					cancelled= data[data['Enquiry status'] == 'Cancelled']
					cancelled_data= cancelled[['Day', 'Enquiry status']].groupby(['Day']).count().reset_index()
					col1, col2= st.columns(2, gap= 'small', border=False)
					col1.metric('Cancelled', value= cancelled['Enquiry status'].count(), border=False)
					col2.bar_chart(cancelled_data, x='Day', y='Enquiry status', height=120, x_label=None, y_label=None, color= '#BACBEC')



			with col18:
				row1= st.columns(1)
				for col in row1:
					col1, col2= st.columns(2, gap= 'small', border=False)
					col1.metric('SLA', value= data['SLA met'].sum(), delta= (data['SLA met'].sum()- data['Enquiry_ref'].count()).astype('float') ,border=False)
					col2.bar_chart(SLA_chart, x='Day', y='SLA met', height=120, x_label=None, y_label=None, color= '#BACBEC')


		with tab2:

			button_data= load_data(1000)

			data= load_data(1000)

			sorted_data= data.sort_values('Datetime', axis= 0, ascending = False, ignore_index= True)

			for sla in sorted_data['SLA']:
				if sla == 'SLA met':
					slas = 'SLA not exceeded' 
					sorted_data['SLA'].replace(sla, slas, inplace=True)

				elif sla == 'SLA not met':
					slas = 'SLA exceeded'
					sorted_data['SLA'].replace(sla, slas, inplace=True)



			container = st.container(height= 800, border= False)
			with container:

				col1, col2, col3 = st.columns(3, gap='small', border=False)

				with col1:
					
					for i in range(0, (len(sorted_data))//3):
						data1= AMC_data[AMC_data['SYSTEM SHORTFORM'] == sorted_data['System'][i]]
						for sys in data1['SYSTEM']:
							systemname = sys
						
					
						containeri = st.container(height=100, border=True)
						with containeri:
							col5, col6= st.columns([.25, .75])

							current_datetime= pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
							time= []
							for datetimes in pd.to_datetime(sorted_data['Datetime']):
								time_diff= (current_datetime- datetimes).total_seconds()
								time.append(time_diff)
							with col5:
								if time[i] < 14400:
									option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
									:blue-badge[New]  
									:orange-badge[View]''', type='tertiary')
									if option:
										enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
										
										df = enquiry_1
										st.session_state.df = df
										st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
										st.switch_page('pages/view_enquiries.py')
								else:
									if sorted_data['Enquiry status'][i] == 'Under review':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:red-badge[Open]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')
									if sorted_data['Enquiry status'][i] == 'Moved for estimation':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:orange-badge[Progress]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')
									if sorted_data['Enquiry status'][i] == 'Quoted':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:green-badge[Done]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')
							with col6:
								st.markdown(f''' {sorted_data['Job type'][i]} -    {sorted_data['Scope'][i]}  
									```{sorted_data['Company'][i]}```   ```{sorted_data['Organization'][i]}```''', unsafe_allow_html= True)
			 
				with col2:
					
					for i in range((len(sorted_data))//3, (len(sorted_data) - (len(sorted_data))//3)):
						data1= AMC_data[AMC_data['SYSTEM SHORTFORM'] == sorted_data['System'][i]]
						for sys in data1['SYSTEM']:
							systemname = sys
						
					
						containeri = st.container(height=100, border=True)
						with containeri:
							col5, col6= st.columns([.25, .75])

							current_datetime= datetime.datetime.now()
							for datetimes in pd.to_datetime(sorted_data['Datetime']):
								time_diff= (current_datetime- datetimes).total_seconds()
							with col5:
								if time_diff < 14400:
									option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
									:blue-badge[New]  
									:orange-badge[View]''', type='tertiary')
									if option:
										enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
										
										df = enquiry_1
										st.session_state.df = df
										st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
										st.switch_page('pages/view_enquiries.py')
								else:
									if sorted_data['Enquiry status'][i] == 'Under review':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:red-badge[Open]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')
									if sorted_data['Enquiry status'][i] == 'Moved for estimation':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:orange-badge[Progress]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')
									if sorted_data['Enquiry status'][i] == 'Quoted':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:green-badge[Done]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')
							with col6:
								st.markdown(f''' {sorted_data['Job type'][i]} -    {sorted_data['Scope'][i]}  
									```{sorted_data['Company'][i]}```   ```{sorted_data['Organization'][i]}```''', unsafe_allow_html= True)
			 
				with col3:
					
					for i in range((len(sorted_data) - (len(sorted_data))//3), len(sorted_data)):
						data1= AMC_data[AMC_data['SYSTEM SHORTFORM'] == sorted_data['System'][i]]
						for sys in data1['SYSTEM']:
							systemname = sys

						containeri = st.container(height=100, border=True)
						with containeri:
							col5, col6= st.columns([.25, .75], gap= 'small')
							current_datetime= datetime.datetime.now()
							for datetimes in pd.to_datetime(sorted_data['Datetime']):
								time_diff= (current_datetime- datetimes).total_seconds()
							with col5:
								if time_diff < 14400:
									option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
									:blue-badge[New]  
									:orange-badge[View]''', type='tertiary')
									if option:
										enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
										
										df = enquiry_1
										st.session_state.df = df
										st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
										st.switch_page('pages/view_enquiries.py')
								else:
									if sorted_data['Enquiry status'][i] == 'Under review':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:red-badge[Open]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')
									if sorted_data['Enquiry status'][i] == 'Moved for estimation':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:orange-badge[Progress]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')
									if sorted_data['Enquiry status'][i] == 'Quoted':
										option= st.button(f'''```{sorted_data['Enquiry_ref'][i]}```  
											:green-badge[Done]  
											:orange-badge[View]''', type='tertiary')
										if option:
											enquiry_1 = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											
											df = enquiry_1
											st.session_state.df = df
											st.session_state['keys101'] = enquiry_data[enquiry_data['Enquiry_ref'] == sorted_data.Enquiry_ref[i]]
											st.switch_page('pages/view_enquiries.py')

							with col6:
								st.markdown(f''' {sorted_data['Job type'][i]} -    {sorted_data['Scope'][i]}  
									```{sorted_data['Company'][i]}```   ```{sorted_data['Organization'][i]}```''', unsafe_allow_html= True)

								


							