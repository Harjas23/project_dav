import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('deliveries.csv')

# Streamlit App
st.title("Cricket Team Performance Analysis")

# Dropdown for selecting the team
teams = df['batting_team'].unique()
selected_team = st.selectbox("Select a team:", teams)

st.write(f"Selected Team: {selected_team}")

# Filter data based on the selected team for bowling stats
bowling_stats = df[(df['bowling_team'] == selected_team) & (df['ball'] > 15.0) & (df['ball'] <= 20.0)]

# Ensure 'ball' column is numeric and clean
bowling_stats['ball'] = pd.to_numeric(bowling_stats['ball'], errors='coerce')
bowling_stats = bowling_stats.dropna(subset=['ball'])

# Convert 'ball' to integer for grouping
bowling_stats['int_ball'] = bowling_stats['ball'].astype(int)

# Bowling Stats Aggregation
bowling_agg = bowling_stats.groupby('bowler').agg({
    'match_id': 'nunique',
    'ball': 'count',
    'runs_off_bat': 'sum',
    'extras': 'sum',
    'wides': 'sum',
    'noballs': 'sum',
    'wicket_type': lambda x: x.notnull().sum()
})

bowling_agg['total_runs_conceded'] = bowling_agg['runs_off_bat'] + bowling_agg['extras']
bowling_agg['overs_bowled'] = bowling_agg['ball'] // 6 + (bowling_agg['ball'] % 6) / 10
bowling_agg['economy_rate'] = bowling_agg['total_runs_conceded'] / bowling_agg['overs_bowled']
bowling_agg['average'] = bowling_agg['total_runs_conceded'] / bowling_agg['wicket_type']
bowling_agg['strike_rate'] = bowling_agg['ball'] / bowling_agg['wicket_type']

final_bowling_stats = bowling_agg[['match_id', 'total_runs_conceded', 'overs_bowled', 'economy_rate', 'average', 'strike_rate', 'wicket_type']]

st.subheader("Bowling Performance")
st.dataframe(final_bowling_stats)

# Heatmap for runs conceded
agg_data = bowling_stats.groupby(['bowler', 'int_ball'])['runs_off_bat'].sum().reset_index()
heatmap_data = agg_data.pivot(index='bowler', columns='int_ball', values='runs_off_bat').fillna(0)

st.subheader("Runs Conceded Heatmap")
if not heatmap_data.empty:
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu', fmt='.1f', linewidths=.5, ax=ax)
    ax.set_title('Runs Conceded by Bowlers in Overs 15.0 to 20.0')
    ax.set_xlabel('Over')
    ax.set_ylabel('Bowler')
    st.pyplot(fig)
else:
    st.write("No data available for heatmap.")

# Batting Stats
batting_stats = df[(df['batting_team'] == selected_team) & (df['player_dismissed'].notna())]

wickets_per_over = batting_stats.groupby(batting_stats['ball'].astype(int)).agg({'wicket_type': 'count'}).reset_index()

st.subheader("Wickets Lost by Team in Each Over")
fig, ax = plt.subplots(figsize=(10, 6))
plt.plot(wickets_per_over['ball'], wickets_per_over['wicket_type'], marker='o', linestyle='-', color='b')
plt.title(f"Wickets Lost by {selected_team} in Each Over")
plt.xlabel('Over')
plt.ylabel('Number of Wickets Lost')
plt.grid(True)
st.pyplot(fig)

# Bar Chart: Wickets Taken by Bowlers
bowling_overall = df[(df['bowling_team'] == selected_team) & (df['wicket_type'] != "run out") & (df['wicket_type'] != "retired hurt")]
bowling_overall = bowling_overall.groupby('bowler').agg({'wicket_type': lambda x: x.notnull().sum()}).reset_index()

st.subheader("Wickets Taken by Bowlers")
fig, ax = plt.subplots(figsize=(10, 6))
plt.bar(bowling_overall['bowler'], bowling_overall['wicket_type'], color='green')
plt.xlabel('Bowler')
plt.ylabel('Wickets Taken')
plt.title(f"Wickets Taken by Bowlers of {selected_team}")
plt.xticks(rotation=45)
st.pyplot(fig)
