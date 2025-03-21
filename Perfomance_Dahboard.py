"""
T20 World Cup Death Overs Performance Dashboard  
-------------------------------------------------
Author: Harjas Bajwa  
Date: February 20, 2025  
License: Nil 
-------------------------------------------------
Description:  
This Streamlit-based dashboard analyzes team and player performances in the  
death overs (16-20) of the T20 World Cup.  

Features:  
- Bowling Performance Analysis: Dot ball progression in last 5 overs, wicket takers comparasion in last 5 overs, split of types of wickets in last 5 overs.  
- Batting Insights: Runs scored Vs Wickets fallen in last 5 overs, phase wise innings progression in in last 5 overs, total runs scored by each batsmen in last 5 overs.  
- Visualizations: Charts - bar,line,pie | heatmaps.  
- Interactive Filtering: Allows filtering by teams.  

This script utilizes Pandas, plotly , sckitlearn and Streamlit for data processing  
and visualization.  
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px


logging.basicConfig(filename='system.log',format='%(asctime)s %(message)s',filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger_success = logging.getLogger()
logger_success.setLevel(logging.INFO)
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
colors = [
    "#FF5733", "#FF8C33", "#FFA533", "#FFC133", "#FFD733",
    "#FF3333", "#FF5733", "#FF6F33", "#FF9933", "#FFB833",
    "#FF4D33", "#FF7033", "#FF8533", "#FFA033", "#FFBE33",
    "#FF3D33", "#FF5E33", "#FF7A33", "#FF9F33", "#FFCD33"
]

 # array of colors for bar chart

team = st.selectbox('Select Team', data['batting_team'].unique())
scaler = MinMaxScaler()

def total_matches_played(team):
    try:
        total_matches = data[((data['batting_team']==team))]
        count_total_matches = len(total_matches['match_id'].unique())
        st.subheader(f"Total Matches Played:{count_total_matches}")
        bowling_stats=data[((data['bowling_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)]
        bowling_death_count = len(bowling_stats['match_id'].unique())
        st.subheader(f"Total Matches Bowled In Death: {bowling_death_count}")
        logger_success.info(f"Succesfully fetched total number of matches played and number of times bowled in death for {team}")
    except:
        logger.error(f"Cannot fetch total number of matches for {team}")
        logger.error(f"Cannot fetch total number of times bowled in death for {team}")

total_matches_played(team)




def total_matches_played_batting(team):
    try:
        batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)]
        total_matches = len(batting_stats['match_id'].unique())
        logger_success.info(f"Succesfully fetched total number of times batted in death for {team}")
        
        return total_matches
    except:
        
        logger.error(f"Error fetching total number of times batted in death for {team}")
        return "No Data Found"

total_matches = total_matches_played_batting(team) #fetches total matches batted in death
st.subheader(f"Total Matches Batted in Death: {total_matches}")

def batting_wickets_fallen(team):
    
    batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)]
    logger.info(f"Data Parsed Succesfully For {team}")
        
    
    return batting_stats
    
        
def batting_runs_scored(team): #method to find runs scored in each over
    try:
        batting_stats=data[((data['batting_team']==team))&(data['ball']>15.0)&(data['ball']<=20.0)]
        batting_stats['ball']=batting_stats['ball'].astype(int)
        batting_stats['total_runs'] = batting_stats['runs_off_bat'] + batting_stats['extras']
        batting_stats=batting_stats[['batting_team','ball','total_runs']]
        batting_stats=batting_stats.groupby('ball').agg({'total_runs':'sum'})
        logger_success.info(f"Succesfully found out out total runs scored in each over {team}")
        return batting_stats
    except:
        logger.error(f"Cannot find specified team {team}")
    
        
try:

    runs_scored=pd.DataFrame(batting_runs_scored(team))
    batsmen_data=pd.DataFrame(batting_wickets_fallen(team))
    
    # Finding out runs scored by each batsmen 

    try:
        batsmen_data['ball']=batsmen_data['ball'].astype(int) #converting ball to int to avoid conflict in groupby
        batsmen_data=batsmen_data[['striker','ball','runs_off_bat']]
        batsmen_data = batsmen_data.groupby(['striker','ball'])['runs_off_bat'].sum().reset_index()
        batsmen_heatmap_data = batsmen_data.pivot(index='striker',columns='ball',values='runs_off_bat').fillna(0)
        logger_success.info(f"data for runs scored by each batsmen parsed successful! for {team}")
        
    except:
        logger.error(f"Error fetching runs scored by each batsmen {team}")

    #finding out total runs in each over by team against wickets fallen
    try:
        batting = pd.DataFrame(batting_wickets_fallen(team))
        batting['ball'] = batting['ball'].astype(int)
        batting_plot = batting[['ball','wicket_type']]
        batting_plot=batting_plot.groupby('ball').agg({'wicket_type':lambda x:x.notnull().sum()})
        batting_plot['runs']=runs_scored['total_runs']
        batting_plot = batting_plot.reset_index()
        logger_success(f"Parsed Data Succesfully for runs scored in each over and wickets fallen for {team}")
        
    except:
        logger.error(f"Error fetching runs scored in each over and wickets fallen for {team}")

    # Finding out AVG in death overs
    try:
        avg_runs_scored = batting_plot[['runs','ball']]
        
        avg_runs_scored['runs'] = avg_runs_scored['runs'] // total_matches
        avg_runs_scored.reset_index()
        logger_success.info("Succesfully found avg runs scored in death overs")
        
        
    except:
        logger.error(f"Error fetching avg runs in death for {team}")
    #Plotting Data
    try:
        fig = px.box(avg_runs_scored,x='ball',y='runs',title="Phase wise Runs")
        batting_plot[['runs','wicket_type']] = scaler.fit_transform(batting_plot[['runs','wicket_type']]) #Normalizing data to fit in scale
        fig = px.box(avg_runs_scored,x='ball',y='runs',title="Phase wise Runs")
        heatmap = px.imshow(batsmen_heatmap_data, labels={'x': 'ball', 'y': 'striker', 'color': 'Runs Off Bat'},
                        color_continuous_scale='YlGnBu',
                        title='Heatmap of Runs Scored by batsmen')
        logger_success.info("Plotting Data Succesfully")
    except:
        logger.error(f"Plotting Failed this might be due to no data available for {team}")




    #DECLARING COLUMN LAYOUT

    col1,col2,=st.columns([50,50])

    with col1: #ALL BATTING VISUALIZATION GOES HERE
        st.write('**Total Wickets Against Total Runs**')
        st.line_chart(batting_plot,x='ball',y=['wicket_type','runs'],x_label='overs',y_label='wickets fallen',color=["#FF0000", "#0000FF"])
        st.write("**This visualization shows how wicket fallen between over 15-20 effcts runs scored**")
        st.plotly_chart(fig,use_container_width=True)
        st.write("**This visualization shows phase wise runs i.e whether in each over runs scored increases or decreases**")
        st.plotly_chart(heatmap,use_container_width=True)
        st.write("**This visualization explain contribution of each batsmen in over 15 - 20**")
    
    def bowling_wickets(team):
        try:
            bowling_stats = data[((data['bowling_team']==team))&(data['ball']>15.0)&(data['ball']<20.0)&(data['wicket_type']!="run out")]
            wickets_taken = bowling_stats.groupby('bowler').agg({'match_id': 'nunique','ball': 'count',
                                                        'runs_off_bat': 'sum','extras': 'sum',
                                                        'wides': 'sum','noballs': 'sum',
                                                        'wicket_type': lambda x: x.notnull().sum()}) 
            wickets_taken = wickets_taken.reset_index()
            total_bowlers = len(wickets_taken['bowler'])
            st.write("**Wickets Taken in Death Overs by Bowlers**")
            st.bar_chart(data = wickets_taken, x = 'bowler',y = 'wicket_type', x_label = "Bowler", y_label = "Total Number Of Wickets Taken",color = colors[total_bowlers-1],use_container_width = True)
            st.write('**This visualization explains contribution of bowlers in death overs in terms of wickets**')
            logger_success.info(f"Data Parsed Successfully for wicket taken by each bowler for {team}")
            
            
        except:
            logger.error(f"No data found for wickets taken by each bowler{team}")
            logger.error("Plotting failed for wicket taken by each bowler(bar chart) for ",team)
    
    def bowling_dot_balls(team):
        #function to find out dot balls bowled and plot the graph for it 
        try:
            bowling_stats = data[((data['bowling_team']==team))&(data['ball']>15.0)&(data['ball']<20.0)&(data['runs_off_bat']==0)&(data['extras']==0)]
            bowling_stats = bowling_stats.reset_index()
            bowling_stats = pd.DataFrame(bowling_stats)
            bowling_stats = bowling_stats[['ball','runs_off_bat']]
            bowling_stats['ball'] = bowling_stats['ball'].astype(int)
            bowling_stats = bowling_stats.groupby('ball').agg({'runs_off_bat':'count'})
            bowling_stats = bowling_stats.reset_index()

            # filling missing data with 0
            if 15 not in bowling_stats['ball'].values:
                bowling_stats.loc[len(bowling_stats.index)] = [15,0]
            if 16 not in bowling_stats['ball'].values:
                bowling_stats.loc[len(bowling_stats.index)] = [16,0]
            if 17 not in bowling_stats['ball'].values:
                bowling_stats.loc[len(bowling_stats.index)] = [17,0]
            if 18 not in bowling_stats['ball'].values:
                bowling_stats.loc[len(bowling_stats.index)] = [18,0] 
            if 19 not in bowling_stats['ball'].values:
                bowling_stats.loc[len(bowling_stats.index)] = [19,0]
            bowling_stats = bowling_stats.sort_values(by = 'ball')
           
            
            bowling_stats = bowling_stats.rename(columns={'runs_off_bat':'dot balls'})
            bowling_stats[['dot balls']] = scaler.fit_transform(bowling_stats[['dot balls']]) #normalizing data to fit the curve
            logger_success.info(f"Succesfuuly found total number of dot balls for {team}")
            logger_success.info(f"Data plotting successful for dot balls for {team}")
            st.write("**Total Number of Dot Balls in Death Overs**")
            st.line_chart(data=bowling_stats, x = 'ball', y='dot balls', use_container_width = True, color = '#78eef5')
            st.write('**This visualization shows dot ball progression in death i.e increasing or decreasing in each phase**')

            
        except:
            logger.error(f"No data found for dot bowls bowled by {team}")
            logger.error(f"Plotting failed for dot ball progression(line chart) for {team}")
    
    def wicket_type_split(team):
        try:
            bowling_stats = data[(data['bowling_team'] == team) & 
                     (data['ball'] > 15.0) & 
                     (data['ball'] < 20.0) & 
                     data['wicket_type'].notnull()]
            logger_success.info(f"Succesfully found split of wickets for {team}")
            bowling_stats = bowling_stats[['wicket_type','player_dismissed']]
            bowling_stats = bowling_stats.reset_index()
            bowling_stats = bowling_stats.groupby('wicket_type').agg({'player_dismissed': 'count'}).reset_index()
            bowling_stats = bowling_stats.rename(columns={'player_dismissed':'count of dissmissal'})
            logger_success.info(f"Data plotting succesful for wicket split for {team}")
            wicket_split = px.pie(bowling_stats, values = 'count of dissmissal', names = 'wicket_type', title = 'Wicket Type Split', hole = 0.3,)
            wicket_split.update_traces(textposition='inside', textinfo='label', marker=dict(line=dict(color="black", width=2)))
            st.plotly_chart(wicket_split,use_container_width = True)
            st.write('**This visualizatio makes you explain split of wicket type, for example if max split is for caught this proves opponent were trying to attack bowlers in death**')

        except:
            logger.error(f"No data found for wickets split of {team}")
            logger.error(f"Plotting failed for wicket split(Pie Chart) of {team}")

    with col2: #ALL BOWLING VISULIZATION GOES HERE
        bowling_wickets(team)
        bowling_dot_balls(team)
        wicket_type_split(team)
        

        
        
except:
    st.write("No Data Available")  # Display a message if no data is available or any syntax error 
    logger.error("Failed to fetch data")

st.page_link("pages/logs.py", label="View Logs")