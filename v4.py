import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px

logging.basicConfig(filename='system.log',format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

st.set_page_config(page_title="Perfomance Dashboard",layout='wide')
def load_data():
    try:
        data = pd.read_csv('deliveries.csv')
        return data
    except:
        logger.error("Cannot find specified path")
        

st.title("**T20 World Death Over Perfomance**")   
# Load the data from the CSV file

data = load_data() #displaying data
data = pd.DataFrame(data)

team = st.selectbox('Select Team', data['batting_team'].unique())
scaler = MinMaxScaler()
def total_matches_played(team):
    try:
        batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)]
        total_matches = len(batting_stats['match_id'].unique())
        return total_matches
    except:
        logger.error("Cannot find specified team")
        return "No Data Found"

total_matches = total_matches_played(team) #fetches total matches played by each team
st.write(f"Total Matches Played: {total_matches}")

def batting_wickets_fallen(team):
    
    batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)]
    logger.info("Data Parsed Succesfully")
        
    #wickets_fallen=batting_stats.agg({'wicket_type':lambda x:x.notnull()})
    #st.write(wickets_fallen)
    return batting_stats
    
        
def batting_runs_scored(team): #method to find runs scored in each over
    batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)]
    batting_stats['ball']=batting_stats['ball'].astype(int)
    batting_stats['total_runs'] = batting_stats['runs_off_bat'] + batting_stats['extras']
    batting_stats=batting_stats[['batting_team','ball','total_runs']]
    batting_stats=batting_stats.groupby('ball').agg({'total_runs':'sum'})
    #wickets_fallen=batting_stats.agg({'wicket_type':lambda x:x.notnull()})
    #st.write(wickets_fallen)
    return batting_stats
try:
    runs_scored=pd.DataFrame(batting_runs_scored(team))
    batsmen_data=pd.DataFrame(batting_wickets_fallen(team))
    
    # Finding out runs scored by each batsmen 

    batsmen_data['ball']=batsmen_data['ball'].astype(int) #converting ball to int to avoid conflict in groupby
    batsmen_data=batsmen_data[['striker','ball','runs_off_bat']]
    batsmen_data = batsmen_data.groupby(['striker','ball'])['runs_off_bat'].sum().reset_index()
    batsmen_heatmap_data = batsmen_data.pivot(index='striker',columns='ball',values='runs_off_bat').fillna(0)
    st.write(runs_scored)
    st.write(batsmen_data)

    #finding out total runs in each over by team
    batting = pd.DataFrame(batting_wickets_fallen(team))
    batting['ball'] = batting['ball'].astype(int)
    batting_plot = batting[['ball','wicket_type']]
    st.write(batting_plot)
    batting_plot=batting_plot.groupby('ball').agg({'wicket_type':lambda x:x.notnull().sum()})
    st.write(batting_plot)
    batting_plot['runs']=runs_scored['total_runs']
    batting_plot = batting_plot.reset_index()

    # Finding out AVG in death overs
    avg_runs_scored = batting_plot[['runs','ball']]
    st.write(avg_runs_scored)
    avg_runs_scored['runs'] = avg_runs_scored['runs'] // total_matches
    avg_runs_scored.reset_index()
    st.write(avg_runs_scored)
    #Plooting Data
    fig = px.box(avg_runs_scored,x='ball',y='runs',title="Phase wise Runs")
    batting_plot[['runs','wicket_type']] = scaler.fit_transform(batting_plot[['runs','wicket_type']]) #Normalizing data to fit in scale
    fig = px.box(avg_runs_scored,x='ball',y='runs',title="Phase wise Runs")
    heatmap = px.imshow(batsmen_heatmap_data, labels={'x': 'ball', 'y': 'striker', 'color': 'Runs Off Bat'},
                    color_continuous_scale='YlGnBu',
                    title='Heatmap of Runs Scored by batsmen')




    #DECLARING COLUMN LAYOUT

    col1,col2,=st.columns([50,50])

    with col1: #ALL BATTING VISUALIZATION GOES HERE
        st.write('**Total Wickets Fallen**')
        st.line_chart(batting_plot,x='ball',y=['wicket_type','runs'],x_label='overs',y_label='wickets fallen',color=["#FF0000", "#0000FF"])
        st.plotly_chart(fig,use_container_width=True)
        st.plotly_chart(heatmap,use_container_width=True)

        
        # st.write("**Total Runs Scored**")
        #st.line_chart(runs_scored,x='ball',y='total_runs',x_label='overs',y_label='wickets fallen',color='#FF0000')
except:
    st.write("No Data Available")  # Display a message if no data is available
    logger.error("Failed to fetch data")