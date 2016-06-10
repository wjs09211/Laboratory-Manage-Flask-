import datetime

date1 = datetime.date(2016, 8, 30)
date2 = datetime.date(2018, 8, 31)
d = datetime.datetime.now()
print type(getattr(d, "year"))