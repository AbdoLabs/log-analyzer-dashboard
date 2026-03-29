import sys
import os
import pandas as pd
#print("Python executable:")
#print(sys.executable)
#print(sys.path)

sys.path.append(os.path.abspath("src"))
from log_analyzer.parser import read_log_file, parse_log_line, parse_log_file
from log_analyzer.analysis import logs_to_dataframe
lines = read_log_file("logs/sample_server_logs_5000_lines.log")
print(len(lines))
first_line = lines[0]
parsed= parse_log_line(first_line)
print(parsed)


logs=parse_log_file("logs/sample_logs_with_error_spike.log")
print(len(logs))
print(logs[0])

df = logs_to_dataframe(logs)
print(df.head())
print(df.shape)
print(df.columns)
print("0 ---------------------")
print(df["level"].value_counts())
print("1 ---------------------")
errors=df[df["level"]=="ERROR"]["message"].value_counts()
print(errors)
print("Max 3 error messages:")
print(errors.head(3))
print("the max error:")
print(errors.idxmax())
print(errors.max())
print("2 ---------------------")
errors=df[df["level"]=="ERROR"]
print(errors["message"].value_counts())

print("3 ---------------------")

print("4 ---------------------")
errors=df[df["level"]=="ERROR"]
print(errors)

#-----------------------
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])

df["hour"]=df["datetime"].dt.hour


df["minute"]=df["datetime"].dt.minute
df["second"]=df["datetime"].dt.second
print(df.head(3))

print(df["hour"].value_counts().sort_index())
#print(df["minute"].value_counts())
#print(df["second"].value_counts())

print(df.groupby("hour")["level"].value_counts())

hourly_levels=df.groupby(["hour","level"]).size().unstack()
print(hourly_levels)

#print(df.groupby(["hour","level"]).size())

print(df.groupby("hour")["message"].value_counts())
print(df.groupby(["hour","message"]).size().unstack())

import matplotlib.pyplot as plt

hourly_levels=hourly_levels.fillna(0)
hourly_levels.plot(kind="bar")
plt.title("Log Events by Hour")
plt.xlabel("Hour")
plt.ylabel("Count of Events")
plt.show()


errors_per_hour = df[df["level"]=="ERROR"].groupby("hour").size()
print(errors_per_hour)
avg_errors = errors_per_hour.mean()
print(avg_errors)

spikes = errors_per_hour[errors_per_hour > avg_errors * 2]
print("Detected eError spikes :")
print(spikes)

errors_per_hour.plot(kind="line")

plt.title("Errors per Hour")
plt.xlabel("Hour")
plt.ylabel("Error Count")

plt.show(block=False)
input("Press Enter to continue...")


#print(df["level"] == "ERROR")
#print(df[df["level"] == "ERROR"])