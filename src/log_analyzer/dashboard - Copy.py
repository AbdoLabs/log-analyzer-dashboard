import sys
import os

sys.path.append(os.path.abspath("src"))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from log_analyzer.parser import parse_log_line
from log_analyzer.analysis import get_errors_per_hour, detect_spikes

st.set_page_config(layout="wide")
st.title("Log Monitoring Dashboard")


col1, col2, col3 = st.columns(3)
with col1:
    uploaded_file = st.file_uploader("Upload a log file", type=["log", "txt"])
if uploaded_file is not None:

      content = uploaded_file.read().decode("utf-8").splitlines()

      logs = []

      for line in content:
          parsed = parse_log_line(line)
          if parsed:
              logs.append(parsed)

      df = pd.DataFrame(logs)

      df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
      df["hour"] = df["datetime"].dt.hour

      # Global Metric
      col1, col2, col3, col4 = st.columns(4)
      col1.metric("Total Logs", len(df))
      col2.metric("Info", len(df[df["level"] == "INFO"]))
      col3.metric("Errors", len(df[df["level"] == "ERROR"]))
      col4.metric("Warnings", len(df[df["level"] == "WARNING"]))
      st.divider()
      col1, col2, col3, col4 = st.columns(4)        
      with col1:
        
          level_filter = st.selectbox(
          "Select Log Level",
          ["ALL", "INFO", "WARNING", "ERROR"]
          )
        
      hour_range = st.slider(
      "Select Hour Range",
      0,
      23,
      (0, 23)
      )
      
      hour_text = f"Hours: {hour_range[0]} → {hour_range[1]}"

      filtered_df = df

      if level_filter != "ALL":
          filtered_df = filtered_df[filtered_df["level"] == level_filter]

      filtered_df = filtered_df[
          (filtered_df["hour"] >= hour_range[0]) &
          (filtered_df["hour"] <= hour_range[1])
      ]
      
      error_df = df[
      (df["hour"] >= hour_range[0]) &
      (df["hour"] <= hour_range[1])
      ]
          
      #st.divider()
      
      col1, col2, col3, col4,col5 = st.columns(5)
      with col1:
        st.write("Logs after filtering:", len(filtered_df))
      col2.metric("Total Logs", len(filtered_df))
      if level_filter == "ALL":
          col3.metric("info", len(filtered_df[filtered_df["level"]=="INFO"]))
          col4.metric("Errors", len(filtered_df[filtered_df["level"]=="ERROR"]))
          col5.metric("Warnings", len(filtered_df[filtered_df["level"]=="WARNING"]))
          
      else:
          col3.metric(level_filter, len(filtered_df[filtered_df["level"] == level_filter]))


      

      #st.divider()
      col1, col2 = st.columns(2)

      with col1:
          st.subheader("Log Level Distribution" +" (" + hour_text + ")")
              
          #st.bar_chart(df["level"].value_counts())
          #st.bar_chart(filtered_df["level"].value_counts())
          
          #level_counts = df["level"].value_counts()
          level_counts = filtered_df["level"].value_counts()
          colors = {
              "INFO": "blue",
              "WARNING": "orange",
              "ERROR": "red"
          }

          fig, ax = plt.subplots()

          ax.bar(
              level_counts.index,
              level_counts.values,
              color=[colors.get(x, "gray") for x in level_counts.index]
          )

          ax.set_title("Log Level Distribution")

          st.pyplot(fig)
          
          

      with col2:
          st.subheader("Events by Hour" +" (" + hour_text + ")")
          st.caption(hour_text)
          events_per_hour = filtered_df.groupby("hour").size()
          st.line_chart(events_per_hour)

      st.divider()

      st.subheader("Error Analysis")

      st.subheader("Errors per Hour" +" (" + hour_text + ")")
      errors_per_hour = get_errors_per_hour(error_df)

      spikes, avg_errors = detect_spikes(errors_per_hour)

      if not spikes.empty:
          spike_hour = spikes.idxmax()
          spike_value = spikes.max()

          st.error(f"High error rate detected at hour {spike_hour} (errors = {spike_value})")
      else:
          st.success("No abnormal error spikes detected")

      st.divider()
      #st.line_chart(errors_per_hour)

      fig, ax = plt.subplots()

      ax.plot(errors_per_hour.index, errors_per_hour.values, color="red", marker="o")

      ax.set_title("Errors per Hour")
      ax.set_xlabel("Hour")
      ax.set_ylabel("Count")

      st.pyplot(fig)

      st.divider()

      st.subheader("Top Error Messages" +" (" + hour_text + ")")
      errors = error_df[error_df["level"] == "ERROR"]
      top_errors = errors["message"].value_counts().head(10)
      #st.dataframe(top_errors)
        
      top_errors = top_errors.rename_axis("Error Message").reset_index(name="Count")
      st.dataframe(
          top_errors,
          column_config={
              "Error Message": st.column_config.TextColumn(width="large"),
              "Count": st.column_config.NumberColumn(width="small")
          },
          use_container_width=True
      )






      st.subheader("Error Heatmap (Hourly)" +" (" + hour_text + ")")

      import matplotlib.pyplot as plt

      error_heatmap = (
          error_df[error_df["level"] == "ERROR"]
          .groupby("hour")
          .size()
          .reindex(range(24), fill_value=0)
      )

      fig, ax = plt.subplots()

      cax = ax.imshow([error_heatmap.values], cmap="Reds", aspect="auto")

      ax.set_xticks(range(24))
      ax.set_xticklabels(range(24))

      ax.set_yticks([])
      ax.set_xlabel("Hour")
      ax.set_title("Error Intensity by Hour")

      fig.colorbar(cax)

      st.pyplot(fig)








      st.subheader("Log Heatmap (Hour vs Level)" +" (" + hour_text + ")")

      heatmap_data = error_df.groupby(["hour","level"]).size().unstack().fillna(0)

      st.dataframe(heatmap_data)
      fig, ax = plt.subplots()

      ax.imshow(heatmap_data, aspect="auto", cmap="Reds")
      #ax.imshow(heatmap_data, aspect="auto", cmap="coolwarm")

      ax.set_xticks(range(len(heatmap_data.columns)))
      ax.set_xticklabels(heatmap_data.columns)

      ax.set_yticks(range(len(heatmap_data.index)))
      ax.set_yticklabels(heatmap_data.index)

      ax.set_xlabel("Log Level")
      ax.set_ylabel("Hour")

      st.pyplot(fig)

      #--------- updated heat map
      st.subheader("Error Heatmap2" +" (" + hour_text + ")")

      error_heatmap = (
        error_df[error_df["level"] == "ERROR"]
        .groupby("hour")
        .size()
        .reindex(range(24), fill_value=0)
      )

      fig, ax = plt.subplots()

      bars = ax.bar(error_heatmap.index, error_heatmap.values, color="red")

      ax.set_title("Error Distribution by Hour")
      ax.set_xlabel("Hour")
      ax.set_ylabel("Errors")

      st.pyplot(fig)
        





      #---------------------------------------
      ## Save filtered data to a CSV automatically
      #filtered_df.to_csv("filtedred.csv", index=False)



      download_option = st.selectbox(
          "Download Data",
          ["Filtered Logs", "Error Logs", "All Logs"]
      )
      
      
      if download_option == "Filtered Logs":
          data_to_download = filtered_df
          file_name = "filtered_logs.csv"

      elif download_option == "Error Logs":
          data_to_download = error_df[error_df["level"] == "ERROR"]
          file_name = "error_logs.csv"

      elif download_option == "All Logs":
          data_to_download = df
          file_name = "all_logs.csv"
    
      st.write(f"Rows to download: {len(data_to_download)}")
      #download filtered data
      csv_data = data_to_download.to_csv(index=False).encode("utf-8")
      
      st.download_button(
      label="Download CSV",
      data=csv_data,
      file_name=file_name,
      mime="text/csv"
      )
      
      ratio = len(filtered_df) / len(df) * 100
      st.metric(f"{level_filter} %", f"{ratio:.2f}%")
      
      st.metric("Selected Logs", len(filtered_df))
      st.metric("Total Logs", len(df))
    
      st.metric("Selected Logs", len(filtered_df))


      peak_hour = events_per_hour.idxmax()