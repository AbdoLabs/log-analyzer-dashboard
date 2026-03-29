
import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath("src"))

from log_analyzer.parser import parse_log_file
from log_analyzer.analysis import logs_to_dataframe

st.title("Log Monitoring Dashboard")
log_file = "logs/sample_logs_with_error_spike.log"

logs = parse_log_file(log_file)
df = logs_to_dataframe(logs)
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
df["hour"] = df["datetime"].dt.hour

st.subheader("Log Level Distribution")
st.bar_chart(df["level"].value_counts())

st.subheader("Events by Hour")
events_per_hour = df.groupby("hour").size()
st.line_chart(events_per_hour)

st.subheader("Errors per Hour")
errors_per_hour = df[df["level"] == "ERROR"].groupby("hour").size()
st.line_chart(errors_per_hour)