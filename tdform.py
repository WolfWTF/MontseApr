#################-timedelta FORMATTER-#################
def timedeltaformatter(duration):
  days, seconds = duration.days, duration.seconds
  hours = days * 24 + seconds // 3600
  minutes = (seconds % 3600) // 60
  seconds = seconds % 60
  tiempo =[days,hours,minutes,seconds]
  return tiempo