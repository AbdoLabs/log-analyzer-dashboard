


import sys
import os
sys.path.append(os.path.abspath("src"))
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Log Analyzer Dashboard")


st.markdown("""
<style>
.block-container {
    padding-top: 1.3rem;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Log Analyzer Dashboard")
st.caption("Interactive log monitoring system with filtering, visualization, and anomaly detection")
#st.markdown("## Log Monitoring Dashboard")


def style_chart(ax):
    # Title
    if ax.get_title():
        ax.set_title(ax.get_title(), fontsize=6)
    # Axis labels
    if ax.get_xlabel():
        ax.set_xlabel(ax.get_xlabel(), fontsize=5)
    if ax.get_ylabel():
        ax.set_ylabel(ax.get_ylabel(), fontsize=5)
    # Tick values 
    ax.tick_params(axis='both', labelsize=5)
    ax.figure.tight_layout()

colors = {
  "INFO": "blue",
  "WARNING": "orange",
  "ERROR": "red"
  }

def colored_metric(col, label, value):
    color = colors.get(label, "black")
    col.markdown(f"""
    <div style="text-align:center;">
        <div style="font-size:28px; color:{color};">{label}</div>
        <div style="font-size:28px; color:{color}; font-weight:bold;">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)
from log_analyzer.parser import parse_log_line
from log_analyzer.analysis import get_errors_per_hour, detect_spikes

col1_main,col2_main = st.columns([1, 1], gap="small")
with col1_main:
    uploaded_file = st.file_uploader("Upload a log file", type=["log", "txt"])
    
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8").splitlines()
    else:
        st.info("Using demo data (upload your own file to replace it)")
        
        with open("data/sample.log", "r") as f:
            content = f.readlines()

logs = []
for line in content:
    parsed = parse_log_line(line)
    if parsed:
        logs.append(parsed)
df = pd.DataFrame(logs)
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
df["hour"] = df["datetime"].dt.hour
with col2_main:
  st.markdown(
  "<h4 style='text-align:center; color:black;'>Log Level Distribution (All Data)</h4>",
  unsafe_allow_html=True
  )
  c1, c2, c3, c4 = st.columns(4)
  colored_metric(c1, "Total Logs", len(df))
  colored_metric(c2, "INFO", len(df[df["level"] == "INFO"]))
  colored_metric(c3, "WARNING", len(df[df["level"] == "WARNING"]))
  colored_metric(c4, "ERROR", len(df[df["level"] == "ERROR"]))
  st.markdown("<hr style='margin:0px 0; height:3px; background-color:#ccc; border:none;'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,1,1], gap="small")
with col1:
      st.markdown("#### Overview of log counts per hour")
      log_data = (
          df.groupby(["hour", "level"])
          .size()
          .unstack()
          .fillna(0)
          .sort_index()
      )
      desired_cols = ["INFO", "WARNING", "ERROR"]
      log_data = log_data.reindex(columns=desired_cols, fill_value=0)
      st.dataframe(log_data, height=180)
      #-------------------------
with col2:
  #  figure (1)
      level_counts = df["level"].value_counts()
      colors = {
          "INFO": "blue",
          "WARNING": "orange",
          "ERROR": "red"
      }
      fig, ax = plt.subplots(figsize=(2.5, 2))
      ax.set_title("Log Level Distribution")
      ax.bar(
          level_counts.index,
          level_counts.values,
          color=[colors.get(x, "gray") for x in level_counts.index]
      )
      #ax.set_title("Log Level Distribution")
      style_chart(ax)
      #fig.tight_layout()
      st.pyplot(fig)
      
with col3:

      #--------  figure (2)  ----------
        import plotly.graph_objects as go
        colors = {
            "INFO": "blue",
            "WARNING": "orange",
            "ERROR": "red"
        }
        level_hourly = (
            df.groupby(["hour", "level"])
            .size()
            .unstack(fill_value=0)
            .sort_index()
        )

        fig = go.Figure()
      
        for level in ["INFO", "WARNING", "ERROR"]:
            if level in level_hourly.columns:
                fig.add_trace(go.Scatter(
                    x=level_hourly.index,
                    y=level_hourly[level],
                    mode='lines+markers',
                    name=level,
                    line=dict(color=colors[level], width=2),
                    marker=dict(size=6)
                ))
      
        fig.update_layout(
        title=dict(text="Log Levels Over Time", x=0.2),
        xaxis=dict(showline=True, linewidth=1, linecolor='black', mirror=True),
        yaxis=dict(showline=True, linewidth=1, linecolor='black', mirror=True),
        xaxis_title="Hour",
        yaxis_title="Count",

        height=250,
        width=320,   # 👈 التحكم الحقيقي

        font=dict(color="black"),
        plot_bgcolor="white",
        paper_bgcolor="white",

        margin=dict(l=10, r=10, t=30, b=60),  # 👈 قلل اليمين

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="black"),
            bgcolor="rgba(240,240,240,0.8)",
            bordercolor="black",
            borderwidth=1
        )
        )
        #fig.update_layout(width=350) ###
        st.plotly_chart(fig, use_container_width=False)

#st.divider() 
st.markdown("<hr style='margin:0px 0; height:3px; background-color:#ccc; border:none;'>", unsafe_allow_html=True)
    #--------------------------- 
col1, col2, col3, col4 = st.columns(4)        
with col1:
  
    level_filter = st.selectbox(
    "Select Log Level",
    ["ALL", "INFO", "WARNING", "ERROR"]
    )
  
hour_range = st.slider("Select Hour Range", 0, 23, (0, 23))

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

events_per_hour = filtered_df.groupby("hour").size()
# Filtered Metric
col1, col2, col3, col4,col5 = st.columns(5)
#with col1:
  #st.markdown(f"#### Logs after filtering: {len(error_df)}")
colored_metric(col1, "Logs after filtering", len(error_df))  
#col2.metric("Total Logs", len(error_df))
peak_hour = events_per_hour.idxmax() if not events_per_hour.empty else None
colored_metric(col2, "Peak Hour", peak_hour)
#colored_metric(col2, "Total Logs", len(error_df))
if level_filter == "ALL":
    colored_metric(col3, "INFO", len(filtered_df[filtered_df["level"] == "INFO"]))
    colored_metric(col4, "WARNING", len(filtered_df[filtered_df["level"] == "WARNING"]))
    colored_metric(col5, "ERROR", len(filtered_df[filtered_df["level"] == "ERROR"]))
else:
    #col3.metric(level_filter, len(filtered_df[filtered_df["level"] == level_filter]))
    colored_metric(col3,level_filter, len(filtered_df[filtered_df["level"] == level_filter]))
    ratio = len(filtered_df) / len(error_df) * 100
    colored_metric(col4,level_filter+" %",f"{ratio:.2f}" )

#st.divider()
col1, col2 = st.columns(2)

with col1:
    #--------  figure (3)  ----------
    st.markdown("##### Log Level Distribution" +" (" + hour_text + ")")
        
    level_counts = filtered_df["level"].value_counts()
    colors = {
        "INFO": "blue",
        "WARNING": "orange",
        "ERROR": "red"
    }
    fig, ax = plt.subplots(figsize=(2.5, 1.5))
    ax.bar(
        level_counts.index,
        level_counts.values,
        color=[colors.get(x, "gray") for x in level_counts.index]
    )
    style_chart(ax)
    st.pyplot(fig)
    #st.subheader(f"{level_filter} Trend Over Time" +" (" + hour_text + ")")
    #---------------------------------------
with col2:
    st.markdown("##### " + level_filter + " Log Activity Over Time" +" (" + hour_text + ")" )
    #--------  figure (4)  ----------
    import plotly.graph_objects as go
    colors = {
        "INFO": "blue",
        "WARNING": "orange",
        "ERROR": "red"
    }
    color = colors.get(level_filter, "black")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=events_per_hour.index,
        y=events_per_hour.values,
        mode='lines+markers',   
        line=dict(color=color, width=2),
        marker=dict(size=6),
        name=level_filter
    ))

    fig.update_layout(
        #title=f"Events by Hour ",
        xaxis_title="Hour",
        yaxis_title="Count",
        height=300,
        width=500,
        font=dict(color="black"),
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig.update_yaxes(
        range=[0, max(events_per_hour.values) + 5],
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        tickfont=dict(color="black"),
        title_font=dict(color="black")
    )

    fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        tickfont=dict(color="black"),
        title_font=dict(color="black")
    )
    
    st.plotly_chart(fig, use_container_width=False)

#st.divider()
st.markdown("<hr style='margin:0px 0; height:3px; background-color:#ccc; border:none;'>", unsafe_allow_html=True)
#---------------------------

st.markdown("#### Error Analysis" +" (" + hour_text + ")")

errors_per_hour = get_errors_per_hour(error_df)

spikes, avg_errors = detect_spikes(errors_per_hour)
if not spikes.empty:
    spike_hour = spikes.idxmax()
    spike_value = spikes.max()

    st.error(f"High error rate detected at hour {spike_hour} (errors = {spike_value})")
else:
    st.success("No abnormal error spikes detected")

col1_error, col2_error = st.columns(2)
with col1_error:

    st.markdown("#### Top Error Messages" +" (" + hour_text + ")")

    errors = error_df[error_df["level"] == "ERROR"]
    top_errors = errors["message"].value_counts().head(10)
        
    top_errors = top_errors.rename_axis("Error Message").reset_index(name="Count")
    st.dataframe(
        top_errors,
        column_config={
            "Error Message": st.column_config.TextColumn(width="large"),
            "Count": st.column_config.NumberColumn(width="small")
        },
        use_container_width=True
    )
    
with col2_error:
    top_errors = error_df[error_df["level"] == "ERROR"]["message"].value_counts().head(5).index
  
    #--------  figure (5)  ----------
    import plotly.graph_objects as go

    fig = go.Figure()

    colors = ["blue", "orange", "green", "red", "purple"]

    for i, msg in enumerate(top_errors):
        msg_data = error_df[error_df["message"] == msg]
        trend = msg_data.groupby("hour").size()

        fig.add_trace(go.Scatter(
            x=trend.index,
            y=trend.values,
            mode='lines+markers',
            name=msg[:30],
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=6)
        ))


    max_y = max([max(trace.y) for trace in fig.data])
    y_values = list(range(2, int(max_y)+2, int(max_y/8)))

    fig.update_layout(
        title="Top Error Trends"+" (" + hour_text + ")",
        xaxis_title="Hour",
        yaxis_title="Count",
        height=300,
        width=500,
        font=dict(color="black"),
        margin=dict(l=40, r=20, t=40, b=60),


        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(
              size=12,
              color="black"  
            ),
            bgcolor="rgba(240,240,240,0.8)",  
            bordercolor="black",
            borderwidth=1
        )
    )


  
    fig.update_xaxes(
        title_standoff=5, 
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        tickfont=dict(color="black"),   
        title_font=dict(color="black")
    )

    fig.update_yaxes(
        title_standoff=5,
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        tickfont=dict(color="black"),   
        title_font=dict(color="black"),
        tickmode='array',
        tickvals=y_values,
        showgrid=True,
        gridcolor='lightgray'
    )

    st.plotly_chart(fig, use_container_width=False)
  
st.markdown("<hr style='margin:0px 0; height:3px; background-color:#ccc; border:none;'>", unsafe_allow_html=True)
    
ca1,ca2 = st.columns(2)

with ca1:
  #--------  figure (6)  ----------
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.plot(errors_per_hour.index, errors_per_hour.values, color="red", marker="o")
    ax.set_title("Errors per Hour")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Count")
    style_chart(ax)
    st.pyplot(fig)

st.markdown("<hr style='margin:0px 0; height:3px; background-color:#ccc; border:none;'>", unsafe_allow_html=True)
    #---------------------------
    #st.subheader("Error Heatmap2" +" (" + hour_text + ")")
with ca2:
    error_heatmap = (
      error_df[error_df["level"] == "ERROR"]
      .groupby("hour")
      .size()
      .reindex(range(24), fill_value=0)
    )
  #--------  figure (7)  ----------
    fig, ax = plt.subplots(figsize=(3,2))

    bars = ax.bar(error_heatmap.index, error_heatmap.values, color="red")

    ax.set_title("Error Distribution by Hour")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Errors")
    style_chart(ax)

    st.pyplot(fig)          

#-----------------------------------------------------------
st.markdown("#### Log Heatmap (Hour vs Level)" +" (" + hour_text + ")")
cb1, cb2 = st.columns([1, 1.5])

with cb1:
    #st.subheader("Log Heatmap (Hour vs Level)" +" (" + hour_text + ")")
    
    heatmap_data = error_df.groupby(["hour","level"]).size().unstack().fillna(0).sort_index()

    desired_cols = ["INFO", "WARNING", "ERROR"]
    heatmap_data = heatmap_data.reindex(columns=desired_cols, fill_value=0)
    st.dataframe(heatmap_data,height=250)
    #------------------------------
    desired_cols = ["INFO", "WARNING", "ERROR"]
    heatmap_data = heatmap_data.reindex(columns=desired_cols, fill_value=0)
    #-------------------------
with cb2:

    fig, axes = plt.subplots(1, 3, figsize=(9, 3))

    levels = ["INFO", "WARNING", "ERROR"]
    cmaps = ["Blues", "Oranges", "Reds"]

    for i, level in enumerate(levels):
        data = heatmap_data[[level]].values  

        im = axes[i].imshow(data, aspect="auto", cmap=cmaps[i])

        axes[i].set_title(level, fontsize=10)

        axes[i].set_xticks([0])
        axes[i].set_xticklabels([level], fontsize=8)

        axes[i].set_yticks(range(len(heatmap_data.index)))
        axes[i].set_yticklabels(heatmap_data.index, fontsize=8)

        # colorbar 
        fig.colorbar(im, ax=axes[i], fraction=0.046, pad=0.04)

    plt.tight_layout()
    st.pyplot(fig)
#---------------------------------------
## Save data to CSV file
col1,col2 = st.columns([1,3])
with col1:
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
      
      #------------------------------------------------------------
      st.markdown("---")
st.markdown("Built by Abdelmenem | GitHub: AbdoLabs")