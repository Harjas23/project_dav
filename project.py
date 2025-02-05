import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import matplotlib.pyplot as plt

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
try:
    team = st.selectbox('Select Team', data['batting_team'].unique())
    scaler = MinMaxScaler()

    def total_matches_played():
        batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)&(data['wicket_type'].notna())]

    def batting_wickets_fallen(team):
        batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)&(data['wicket_type'].notna())]
        print(batting_stats)
        #wickets_fallen=batting_stats.agg({'wicket_type':lambda x:x.notnull()})
        #st.write(wickets_fallen)
        return batting_stats
    def batting_runs_scored(team):
        batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)]
        batting_stats['ball']=batting_stats['ball'].astype(int)
        batting_stats['total_runs'] = batting_stats['runs_off_bat'] + batting_stats['extras']
        batting_stats=batting_stats[['batting_team','ball','total_runs']]
        batting_stats=batting_stats.groupby('ball').agg({'total_runs':'sum'})
        #wickets_fallen=batting_stats.agg({'wicket_type':lambda x:x.notnull()})
        #st.write(wickets_fallen)
        return batting_stats
    runs_scored=pd.DataFrame(batting_runs_scored(team))
    st.write(runs_scored)
    batting = pd.DataFrame(batting_wickets_fallen(team))
    batting['ball'] = batting['ball'].astype(int)
    batting_plot = batting[['ball','wicket_type']]
    
    batting_plot=batting_plot.groupby('ball').agg({'wicket_type':'count'})
    
    st.write(batting_plot)
    batting_plot['runs']=runs_scored['total_runs']
    batting_plot = batting_plot.reset_index()
    box_plot = batting_plot[['runs','ball']]
    box_plot=box_plot.reset_index()
    st.write(box_plot)
    batting_plot[['runs','wicket_type']] = scaler.fit_transform(batting_plot[['runs','wicket_type']])
   

    #batting_plot = batting_plot.reset_index()
    #fig = px.box(box_plot,x='ball',y='runs',title="Phase wise Runs")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxenplot(x="ball", y="runs", data=box_plot, palette="coolwarm", ax=ax)
    col1,col2,=st.columns([50,50])
    
    with col1:
        st.write('**Total Wickets Fallen**')
        st.line_chart(batting_plot,x='ball',y=['wicket_type','runs'],x_label='overs',y_label='wickets fallen',color=["#FF0000", "#0000FF"])
        st.write('**Phase wise Runs**')
        st.bar_chart(box_plot,x='ball',y='runs',x_label='overs',y_label='runs')
       # st.write("**Total Runs Scored**")
        #st.line_chart(runs_scored,x='ball',y='total_runs',x_label='overs',y_label='wickets fallen',color='#FF0000')
except:
    st.write("No Data Available")
    logger.error("ERROR 404 not found")