import ephem
from datetime import datetime, timedelta
from time import sleep
# for printing pretty pass tables:
from tabulate import tabulate

def ParseTleFile(file):
	# create a list of TLEs:
	tle_list = []
	tle = {}
	count = 0
	with open(file,'r') as f:
		for lines in f:
			if lines[0] == "1":
				count = count + 1
				tle["line1"] = VerifyChecksum(lines.replace("\n",""))
				tle["ssc"] = tle["line1"]
			if lines[0] == "2":
				tle["line2"] = VerifyChecksum(lines.replace("\n",""))
				tle_list.append(tle)
				tle = {}
	# create a list of pyephem objects:
	sat_list= []
	for tle in tle_list:
		 sat_list.append(ephem.readtle(tle['ssc'],tle['line1'],tle['line2']))
 	return sat_list

def VerifyChecksum(line):
	xsum = 0
	for c in line[0:68]:
		if c == '-':
			xsum = xsum + 1
		elif c.isdigit():
			xsum = xsum + int(c)
	xsum = xsum % 10
	line = line[0:68] + str(xsum)
	return line

def CalculatePasses(observer,object_list,future=1):
	# loop through objects, compute next rise:
	table = []
	headers = ['SSC #','Rise Time (UTC)','Rise Az (deg)','Peak Time (UTC)','Peak El (deg)','Set Time (UTC)', 'Set Az (deg)']
	for sat in object_list:
		for a in range(0,future):
			info = observer.next_pass(sat)
			table.append([sat.catalog_number,
						  info[0].datetime(),
						  info[1]*180/ephem.pi,
						  info[2].datetime(),
						  info[3]*180/ephem.pi,
						  info[4].datetime(),
						  info[5]*180/ephem.pi])

	print(tabulate(table,headers=headers))

def GetPointing(observer,sat,sample_time,dt):
	'''
		sample_time: a valid datetime object
		         dt: float or integer number of seconds used to when
		             differentiating the angles to produce a rate
	'''
	t_before = sample_time + timedelta(seconds=-dt)
	t_after = sample_time + timedelta(seconds=dt)
	# before
	observer.date = t_before
	sat.compute(observer)
	az_0 = sat.az
	alt_0 = sat.alt
	ra_0,dec_0 = observer.radec_of(az_0,alt_0)
	# current
	observer.date = sample_time
	sat.compute(observer)
	az_1 = sat.az
	alt_1 = sat.alt
	ra_1,dec_1 = observer.radec_of(az_1,alt_1)
	# after
	observer.date = t_after
	sat.compute(observer)
	az_2 = sat.az
	alt_2 = sat.alt
	ra_2,dec_2 = observer.radec_of(az_2,alt_2)
	# compute rates:
	dalt = CalculateRates(alt_0,alt_1,alt_2,dt)*180/ephem.pi
	daz = CalculateRates(az_0,az_1,az_2,dt)*180/ephem.pi
	dra = CalculateRates(ra_0,ra_1,ra_2,dt)*180/ephem.pi
	ddec = CalculateRates(dec_0,dec_1,dec_2,dt)*180/ephem.pi
	# output
	observer.date = sample_time
	ra,dec = observer.radec_of(sat.az,sat.alt)
	print observer.date,sat.az*180/ephem.pi,sat.alt*180/ephem.pi,ra*180/ephem.pi,dec*180/ephem.pi,daz,dalt,dra,ddec

def CalculateRates(a,b,c,dt):
	m1 = (b-a)/dt
	m2 = (c-b)/dt
	m = (m1+m2)/2
	return m

def TrackObject(observer,sat):
	print "-------------------------------------------------------"
	print "      Tracking Routine for", sat.catalog_number
	print "-------------------------------------------------------"
	# Determine the current position of the object
	observer.date = datetime.now()
	sat.compute(observer)
	print "Current Azimuth:",sat.az*180/ephem.pi," deg"
	print "Current Elevation:", sat.alt*180/ephem.pi," deg"
	if sat.alt <= 0:
		print "\nNext Pass Data:\n" 
		CalculatePasses(observer,[sat])
	else:
		pass
	print "\nBegin Tracking:\n"
	while True:
		GetPointing(observer,sat,datetime.now(),0.1)
		sleep(0.5)


def work(file):
	# parse the TLE:
	object_list = ParseTleFile(file)
	# observer postion
	observer = ephem.Observer()
	observer.lat = '40.59' # string
	observer.lon = '-113.0' # string
	# elevation limit
	observer.horizon = ephem.degrees(0)
	# Track an object
	TrackObject(observer,object_list[0])

if __name__ == "__main__":
	work("iridium.tle")