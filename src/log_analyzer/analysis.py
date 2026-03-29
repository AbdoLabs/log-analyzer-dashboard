import pandas as pd

def logs_to_dataframe(logs):
  df = pd.DataFrame(logs)
  return df

def get_errors_per_hour(df):
    return df[df["level"] == "ERROR"].groupby("hour").size()


def detect_spikes(errors_per_hour):
    avg = errors_per_hour.mean()
    spikes = errors_per_hour[errors_per_hour > avg * 2]
    return spikes, avg