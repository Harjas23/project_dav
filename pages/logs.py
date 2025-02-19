import streamlit as st

# Path to your log file
log_file_path = "system.log"

st.title("Log File Viewer")

# Read and display log content
with open(log_file_path, "r") as file:
    log_data = file.read()

st.text_area("Logs", log_data, height=400)