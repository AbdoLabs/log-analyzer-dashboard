def read_log_file(filepath):
  with open(filepath,"r") as file:
    lines = file.readlines()
    return lines
  
  
def parse_log_line(line):
  parts = line.strip().split(" ")
  if len(parts)<4:
    return None

  log_entry={
    "date": parts[0],
    "time": parts[1],
    "level": parts[2],
    "message": " ".join(parts[3:])
  }
  return log_entry

def parse_log_file(filepath):
  logs=[]
  lines = read_log_file(filepath)
  for line in lines:
    parsed = parse_log_line(line)
    if parsed is not None:
      logs.append(parsed)
      
  return logs
