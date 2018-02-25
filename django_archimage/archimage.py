#!python2
import serial
import ephem
import numpy as np
import io, re, random, time, binascii, json, numpy
from datetime import datetime
from threading import Thread

class archimage():
    def __init__(self,live=True):
        '''
        I added critical stuff to the init.  Things like comms, basic  settings required for propper alignment.... etc.
        '''
        self.debug_flag = False

        # location:
        self.lat = 39
        self.lon = -83
        self.alt = 316

        # astronomy stuff:
        self.sidereal_rate = 15.041 # arcseconds/second

        # Serial Comm Stuff
        self.live_comm = live # use for debugging without comms hooked up
        self.port = 'COM3'
        self.baudrate= 9600
        self.timeout= 0.1
        self.counter = 0

        # virtual mount:
        self.virtual_abort = False # Kills slew operations when True
        self.virtual_ra = 0 # degrees...?
        self.virtual_dec = 0 # degrees
        self.virtual_speed = 10 # degrees/second
        self.virtual_ra_rate = 10 # degrees/second
        self.virtual_dec_rate = 10 # degrees /seconds

        # initializing comm
        if self.live_comm : # open serial port
            self.ser = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout
                    )

            self.ser.isOpen()
            self.send("")

            # ensure scope position is updated
            # Should probably get rid of this... silently changes scope settings.
            # self.sidereal_time()
            # self.set_latitude(self.lat)

        print "ARCHIMAGE __INIT__: INITIALIZED COM INTERFACE!"

    '''
    -----------------------------------------------------------------
    /////////////////  High-Level Mount Operations  \\\\\\\\\\\\\\\\\
    -----------------------------------------------------------------
    '''

    def set_virtual_dec(self,dec_dd):
        print "setting virtual dec to:", dec_dd
        self.virtual_dec = float(dec_dd)
        return 'virtual dec set'

    def set_virtual_ra(self,ra_dd):
        print "setting virtual ra to:", ra_dd
        self.virtual_ra = float(ra_dd)/15
        return 'virtual ra set'

    def connect(self):
        '''
        Establish serial comms
        '''
        print "connected!"
        return "connected!"

    def disconnect(self):
        '''
        Break serial comms
        '''
        print "disconnected!"
        return "disconnected!"

    def get_all(self):
        '''
        Returns all "get-able" parameters
        '''
        data = {
                'pointing': {
                    'ra': self.get_pointing_ra(),
                    'ha': self.get_pointing_ha(),
                    'dec': self.get_pointing_dec(),
                    'az': self.get_pointing_az(),
                    'alt': self.get_pointing_alt()
                    },
                'tracking': {
                    'track_ha': self.get_ha_rate(),
                    'track_dec': self.get_dec_rate()
                    },
                'target': {
                    'object_ra': self.get_object_ra(),
                    'object_dec': self.get_object_dec(),
                    'object_alt': self.get_object_alt(),
                    'object_az': self.get_object_az()
                    },
                'status': 'test'
                }

        print json.dumps(data,indent=4)

        return data

    def get_status(self):
        return self.send("satus")

    def get_object(self):
        '''
        Returns current target parameters (the GOTO assignment)
        '''
        data = {
                'target': {
                    'object_ra': self.get_object_ra(),
                    'object_dec': self.get_object_dec(),
                    'object_alt': self.get_object_alt(),
                    'object_az': self.get_object_az()
                    }
                }

        print json.dumps(data,indent=4)

        return data

    def get_tracking(self):
        '''
        Returns tracking rates in deg/s
        '''
        data = {
                'tracking': {
                    'track_ha': self.get_ha_rate(),
                    'track_dec': self.get_dec_rate()
                    }
                }

        print json.dumps(data,indent=4)

        return data

    def get_pointing(self):
        '''
        Returns all pointing parameters
        '''
        data = {
                'pointing': {
                    'ra': self.get_pointing_ra(),
                    'ha': self.get_pointing_ha(),
                    'dec': self.get_pointing_dec(),
                    'az': self.get_pointing_az(),
                    'alt': self.get_pointing_alt()
                    }
                }

        print json.dumps(data,indent=4)

        return data

    def set_location(self,lat_dd,lon_dd):
        '''
        Sets latitude and sidereal time.  Input lat,lon in decimal degrees.
        '''
        sidereal_time = compute_sidereal_time(lon_dd)
        self.set_sidereal(sidereal_time)
        self.set_latitude(lat_dd)


    def sidereal_time(self):
        '''
        Returns the current sidereal time, and set's the scopes sidereal time
        '''
        sidereal_time = compute_sidereal_time(self.lon)
        return self.set_sidereal(sidereal_time)

    def point_radec(self,ra_deg,dec_deg):
        '''
        Set's object position and executes a goto
        '''
        if not self.live_comm:
            thread = Thread(target=self.simulated_radec_slew,args=(ra_deg,dec_deg,))
            thread.start()
        self.set_object_ra(ra_deg)
        self.set_object_dec(dec_deg)
        self.goto()

    def simulated_radec_slew(self,ra_deg,dec_deg):
        '''
        This is sloppy... but it allowed verification of ASCOM driver in TheSkyX
        '''
        # determine distance traveled in degrees:
        delta = GreatCircleDelta(self.virtual_ra,self.virtual_dec,ra_deg*15,dec_deg)

        # slew step size:
        resolution = 0.5 # degrees

        # number of steps to use during slew operation
        steps = int(numpy.ceil(delta/resolution))

        # compute ra/dec values (converting hours to degrees):
        ra_vals = numpy.linspace(self.virtual_ra*15,ra_deg,steps) # ra is in degrees
        dec_vals = numpy.linspace(self.virtual_dec,dec_deg,steps) # dec is degrees

        # compute update rate based on on slew speed:
        delay = resolution / self.virtual_speed


        for r,d in zip(ra_vals,dec_vals):
            # see if abort was issued:
            if self.virtual_abort:
                break
            # else update position:
            self.virtual_ra = r/15 # store the ra in decimal hours
            self.virtual_dec = d # store the dec in degrees
            time.sleep(delay)
        return

    def point_altaz(self,alt_deg,az_deg):
        '''
        Executes an Az/el goto
        Use north azimuth (0 degrees is north...)
        I'm not sure what this does that altaz_goto doesn't do....
        '''
        if self.live_comm:
            self.altaz_goto(alt_deg,az_deg)
        else: # if we're simulated:
            # get pointing in ra/dec (degrees):
            ra_deg,dec_deg = AzEl2RaDec(datetime.now(),az_deg,alt_deg,self.lat,self.lon)
            # simulate slew:
            thread = Thread(target=self.simulated_radec_slew,args=(ra_deg,dec_deg,))
            thread.start()

    def init_align(self):
        '''
        Initializes mount pointing when pointed south at zero degrees elevation
        '''
        lat = self.get_latitude()
        dec = -1.0*(90.0-lat)
        self.set_pointing_dec(dec)
        self.set_pointing_ha(0.0)

        return "aligned south, at zero degrees elevation!"

    def clear_track_rates(self):
        '''
        Sets both axes rates to zero.
        '''
        self.set_ha_rate(0)
        self.set_dec_rate(0)
        return "Set HA and DEC rates to zero deg/sec!"


    '''
    ---------------------------------------------------------------
    /////////////////  Low-Level Mount Functions  \\\\\\\\\\\\\\\\\
    ---------------------------------------------------------------
        Low-level mount functions are listed here in the following categories:

    1) Mount Flags
    2) Configuration
    3) Alignment and Pointing
    4) Home Stuff
    5) Tracking
    6) Target Specification
    7) Paddle

    '''

    '''
    -------------------------
    1) Mount Flags
    -------------------------

    The mount has several fags (bits) that are use to enable/disable
    features of the mount.  They are outlined below.  I provided a single command
    for each set/clear option.  None of the below commands is checked for compatiability
    with the remaining flags (for instance, enabling the german equatorial mode while configured as
    an alt/az mount).  Such validation should occur at a higher level.

    Breakdown of flags based on sniffing commmands from MCC Scope:
    _____________________________________________________________
    | Flag |    Name    |                Description            |
    -------------------------------------------------------------
    |   4  | Equatorial | Equatorial vs. Alt/Az                 |
    -------------------------------------------------------------
    |  20  |  Horrizon  | Impose an Elevaiton Limit             |
    -------------------------------------------------------------
    |  23  |    PEC     | Periodic Error Correction             |
    -------------------------------------------------------------
    |  16  |    IECA    | Integrated Error Correction Algorithm |
    -----------------------------------------------------------
    |   0  |  Tracking  | Toggle Tracking                       |
    -------------------------------------------------------------
    |  21  |   German   | German Equatorial                     |
    -------------------------------------------------------------
    '''

    def enable_track(self):
        # turn on tracking
        return self.send("set flag[0]=1")

    def disable_track(self):
        # turn off tracking
        return self.send("set flag[0]=0")

    def set_equatorial(self):
        return self.send("set flag[4]=1")

    def set_altaz(self):
        return self.send("set flag[4]=0")

    def enable_german_equatorial(self):
        return self.send("set flag[21]=1")

    def disable_german_equatorial(self):
        return self.send("set flag[21]=0")

    def enable_horrizon_limit(self):
        return self.send("set flag[20]=1")

    def disable_horrizon_limit(self):
        return self.send("set flag[20]=0")

    def enable_pec(self):
        return self.send("set flag[23]=1")

    def disable_pec(self):
        return self.send("set flag[23]=0")

    def enable_ieca(self):
        return self.send("set flag[16]=1")

    def disable_ieca(self):
        return self.send("set flag[16]=0")

    '''
    -------------------------
    2) Configuration
    -------------------------

    These commands configure the mount's latitude and sidereal time (longitude).

    '''
    def set_sidereal(self,decimal_hour_angle):
        '''
            Set the local apparent sidereal time.
            Specify the decimal hour angle.
        '''
        command = "set sidereal=" + "{:.6f}".format(decimal_hour_angle) + "h"
        return self.send(command)

    def get_sidereal(self):
        '''
            Return sideral time from the mount as degrees
        '''
        command = "get sidereal"
        resp = self.send(command)
        if self.live_comm:
            return hms2dd(resp['payload'])
        else:
            return random.uniform(0.000,360.000)

    def set_latitude(self,decimal_latitude_degrees):
        command = "set latitude=" + "{:.6f}".format(decimal_latitude_degrees) + "d"
        return self.send(command)

    def get_latitude(self):
        '''
            Return mount latitude as degrees
        '''
        command = "get latitude"
        resp = self.send(command)
        if self.live_comm:
            return dms2dd(resp['payload'])
        else:
            return random.uniform(-90.000,90.000)

    '''
    -------------------------
    3) Alignment and Pointing
    -------------------------
    Depending on if it's configured as equatorial or alt/az, you can specify the current
    pointing at any time. The commands below set the current pointing in each frame.  They
    do not check the mounts configuration as equatorial or alt/az.  In equatorial pointing
    is defined in local hour hangle (ha, South is 0 degrees and declination (dec).
    In alt/az pointing is defned in azimuth (az, North is 0 degrees) and elevation.

    Always handle angles in decimal degrees, however konw that this API translates them to either
    degrees-minutes-seconds or hour angle depending on the parameter being used:

    alt/az pointing is communicated in DMS

    ra pointing is communicated in HMS

    dec pointing is communicated in DMS

    '''

    # Equatorial Pointing:
    def get_pointing_ra(self):
        '''
        Get pointing right acension in decimal hours
        ASCOM and TheSkyX require RA in decimal hours (not ddd)
        '''
        command = "get ra"
        resp = self.send(command)
        if self.live_comm:
            return hms2dh(resp['payload'])
        else:
            #return random.uniform(0.000,360.000)
            return self.virtual_ra

    def get_pointing_ha(self):
        '''
        Get pointing hour angle in decimal hours
        ASCOM and TheSkyX require RA in decimal hours (not ddd)
        '''
        command = "get ha"
        resp = self.send(command)
        if self.live_comm:
            return hms2dh(resp['payload'])
        else:
            ha = (self.virtual_ra - compute_sidereal_time(self.lon))*15
            return ha

    def get_pointing_dec(self):
        '''
        Get pointing declination in decimal degrees
        '''
        command = "get dec"
        resp = self.send(command)
        if self.live_comm:
            return dms2dd(resp['payload'])
        else:
            #return random.uniform(-90.000,90.000)
            return self.virtual_dec

    def set_pointing_ha(self,ha_dd):
        '''
        Specify pointing hour angle in decimal degrees
        '''
        command = "set ha=" + dd2hms(ha_dd)
        return self.send(command)

    def set_pointing_dec(self,dec_dd):
        '''
        Specify pointing declination in decimal degrees
        '''
        command = "set dec=" + dd2dms(dec_dd)
        return self.send(command)

    # Alt/Az Pointing:
    def get_pointing_az(self):
        '''
        Get pointing north azimuth in decimal degrees
        '''
        command = "get az"
        resp = self.send(command)
        if self.live_comm:
            az_deg = dms2dd(resp['payload'])
            # modify for south azimuth:
            az_deg = (az_deg+180)%360
            return dms2dd(az_deg)
        else:
            # return simulated az/el
            az_deg,alt_deg = RaDec2AzEl(datetime.now(),self.virtual_ra*15,self.virtual_dec,self.lat,self.lon)
            return az_deg

    def get_pointing_alt(self):
        '''
        Get pointing altitude (elevation) in decimal degrees
        '''
        command = "get alt"
        resp = self.send(command)
        if self.live_comm:
            return dms2dd(resp['payload'])
        else:
            # return simulated az/el
            az_deg,alt_deg = RaDec2AzEl(datetime.now(),self.virtual_ra*15,self.virtual_dec,self.lat,self.lon)
            return alt_deg

    def set_pointing_az(self,az_deg):
        '''
        Specify pointing north azimuth in decimal degrees

        '''
        # modify for south azimuth:
        az_deg = (az_deg - 180)%360
        command = "set az=" + dd2dms(az_deg)
        return self.send(command)

    def set_pointing_alt(self,alt_dd):
        '''
        Specify pointing altitude (elevation) in decimal degrees
        '''
        command = "set alt=" + dd2dms(alt_dd)
        return self.send(command)

    '''
    -------------------------
    4) Home Stuff
    -------------------------

    These commands configure the mount's home position
    '''
    def find_home(self):
        '''
        Find the home position
        '''
        return self.send("home find")
    def home_setup(self):
        '''
        Setup from the home position... don't know what this does.
        '''
        return self.send("home setup")
    def park(self):
        '''
        Park the mount
        '''
        return self.send("home park")
    def set_park(self):
        '''
        Set the mount park position
        '''
        return self.send("home x_parkset")

    '''
    -------------------------
    5) Tracking
    -------------------------

    These commands allow configuration of the tracking rate for each axis.  Axes rates
    are commanded in units of degrees/second.

    '''
    def get_ha_rate(self):
        '''
        Get the current hour-angle tracking rate in degrees/second
        '''
        command = "get trackha"
        resp = self.send(command)
        if self.live_comm:
            return float(dms2dd(resp['payload']))
        else:
            return random.uniform(0.000,4.000)

    def get_dec_rate(self):
        '''
        Get the current declination tracking rate in degrees/second
        '''
        command = "get trackdec"
        resp = self.send(command)
        if self.live_comm:
            return float(dms2dd(resp['payload']))
        else:
            return random.uniform(0.000,4.000)

    def set_ha_rate(self,rate_ds):
        '''
        Specifcy ha tracking rate in deg/s
        set trackha=+0.047314d
        '''
        command = "set trackha=" +  "{:.5f}".format(rate_ds) + "d"
        return self.send(command)

    def set_dec_rate(self,rate_ds):
        '''
        Specifcy dec tracking rate in deg/s
        set trackdec=-0.115978d
        '''
        command = "set trackdec=" + "{:.5f}".format(rate_ds) + "d"
        return self.send(command)

    '''
    -------------------------
    6) Target Specification
    -------------------------

    These commands are used to aquire targets in ra/dec or az/el coordinates

    '''

    # set/get target parameters

    def set_object_ra(self,hour_angle_dd):
        '''
        Set the target object hour angle in decimal degrees
        '''
        command = "set objectra=" + "{:.5f}".format(hour_angle_dd/15) + "h"
        return self.send(command)

    def get_object_ra(self):
        '''
        Get the target object hour angle in decimal hours
        '''
        command = "get objectra"
        resp = self.send(command)
        if self.live_comm:
            return hms2dh(resp['payload'])
        else:
            return random.uniform(0.000,359.999)

    def set_object_dec(self,declination_dd):
        '''
        Set the target object declination angle in decimal degrees
        '''
        command = "set objectdec=" + "{:.5f}".format(declination_dd) + "d"
        return self.send(command)

    def get_object_dec(self):
        '''
        Get the target object declination angle in decimal degrees
        '''
        command = "get objectdec"
        resp = self.send(command)
        if self.live_comm:
            return dms2dd(resp['payload'])
        else:
            return random.uniform(-90.000,90.000)

    def get_object_az(self):
        '''
        Get the target object north azimuth in decimal degrees
        '''
        command = "get objectaz"
        resp = self.send(command)
        if self.live_comm:
            az_deg = dms2dd(resp['payload'])
            # modify for south azimuth:
            az_deg = (az_deg + 180)%360
            return az_deg
        else:
            return random.uniform(0.000,360.000)

    def get_object_alt(self):
        '''
        Get the target object altitude (elevation) in decimal degrees
        '''
        command = "get objectalt"
        resp = self.send(command)
        if self.live_comm:
            return dms2dd(resp['payload'])
        else:
            return random.uniform(-90.000,90.000)

    def goto(self):
        '''
        Execute a GOTO for the current target
        '''
        return self.send("goto")

    def altaz_goto(self,alt_deg,az_deg):
        '''
        Slew to an alt/az target
        Input north azimuth (0 degrees is North)
        '''
        # modify for south azimuth:
        az_deg = (az_deg - 180)%360
        return self.send("goto objectaz="+dd2dms(az_deg)+" objectalt="+dd2dms(alt_deg))
    '''
    -------------------------
    7) Paddle
    -------------------------

    These commands are built in for jogging the mount.

    '''
    def set_speed(self,slew_speed_ds):
        '''
        Set jog speed in degrees/second
        '''
        command = "set speed=" + "{:.5f}".format(slew_speed_ds) + "d"
        return self.send(command)

    def move_north(self):
        '''
        Jog North
        '''
        return self.send("move north")

    def stop_north(self):
        '''
        Stop jogging North
        '''
        return self.send("stop north")

    def move_east(self):
        '''
        Jog East
        '''
        return self.send("move east")

    def stop_east(self):
        '''
        Stop jogging East
        '''
        return self.send("stop east")

    def move_south(self):
        '''
        Jog South
        '''
        return self.send("move south")

    def stop_south(self):
        '''
        Stop jogging South
        '''
        return self.send("stop south")

    def move_west(self):
        '''
        Jog West
        '''
        return self.send("move west")

    def stop_west(self):
        '''
        Stop jogging West
        '''
        return self.send("stop west")

    def stop(self):
        '''
        Stop all movement
        '''
        if self.live_comm:
            return self.send("stop")
        else:
            self.virtual_abort = True
            time.sleep(1)
            self.virtual_abort = False

    '''
    -----------------------------------------------------------
    /////////////////  Serial Comm functions  \\\\\\\\\\\\\\\\\
    -----------------------------------------------------------
    '''

    def send(self,payload,verbose=True):
        '''
        This accepts command strings as readable text (ascii).
        It creates a packet by adding header, footer, counter, check bytes.
        It then fires it off to the serial port (configured by the archimage class)

        TODO:
        1) Add a blocking read to catch the reponse after each message.
        '''
        if verbose:
            print "[TX_SEND]", payload

        if self.live_comm :
            # Serial Purge:
            # I noticed this while sniffing the CSAT serial comms.  Seems to help.
            while self.ser.out_waiting > 0 :
                self.ser.reset_input_buffer()
            self.ser.write(binascii.unhexlify("08000000"))
            # format the packet
            dbug(self.debug_flag,'-----------------------')
            dbug(self.debug_flag,'Payload: ' + payload)
            hex_payload = prepare(payload,self.counter)
            dbug(self.debug_flag,'Hex: ' + hex_payload)
            bytes = binascii.unhexlify(hex_payload)
            # send the packet
            self.ser.write(bytes)
            # up the counter
            self.counter = countup(self.counter)
            dbug(self.debug_flag,'Counter: ' + str(self.counter))
            response = unpack(self.ser.read(1000))
            #check for "ok" or "err"
            rx_payload = ''
            if response[0:2] == 'ok':
                status = "success"
                error_flag = False
                parsed = re.findall(r'ok (.*?)\r',response,re.DOTALL)
                if parsed:
                    rx_payload = rx_payload + parsed[0]
            elif response[0:5] == 'error':
                status = "error"
                error_flag = True
                parsed = re.findall(r'(.*?)\r',response,re.DOTALL)
                if parsed:
                    rx_payload = rx_payload + parsed[0]
            else:
                status = "unknown"
                error_flag = False
                rx_payload = rx_payload + response

        else: # not live
            rx_payload = 'DEAD REPLY...'
            error_flag = False
            status = "success"
            response = "no bytes fool"

        if verbose:
            print '[RX_STATUS]', status
            print '[RX_RESPONSE]', rx_payload

        reply = {}
        reply['error'] = error_flag
        reply['status'] = status
        reply['payload'] = str(rx_payload.decode("utf8"))
        reply['raw'] = response
        return reply


'''
-----------------------------------------------
/////////////////  Utilities  \\\\\\\\\\\\\\\\\
-----------------------------------------------
'''

def dd2dms(degrees):
    '''
    given angle as degree (some kind of number...) return signed dms string
    '''
    a = ephem.degrees(str(degrees))
    dms = str(a).replace(':','d',1)
    dms = dms.replace(':','m')+'s'
    if a >= 0:
        dms = "+" + dms
    return dms

def dd2hms(degrees):
    '''
    given angle as degree (some kind of number...) return signed hms string
    '''
    a = ephem.hours(ephem.degrees(str(degrees)))
    hms = str(a).replace(':','h',1)
    hms = hms.replace(':','m')+'s'
    if a >= 0:
        hms = "+" + hms
    return hms

def dms2dd(dms):
    '''
    given signed dms string return float degrees
    '''
    dms = dms.strip()
    dms = dms.replace('d',':')
    dms = dms.replace('m',':')
    dms = dms.replace('s','')
    a = ephem.degrees(dms)
    dd = a*180/ephem.pi
    return dd

def hms2dd(hms):
    '''
    given signed hms string return float degrees
    '''
    hms = hms.strip()
    hms = hms.replace('h',':')
    hms = hms.replace('m',':')
    hms = hms.replace('s','')
    a = ephem.hours(hms)
    dd = a*180/ephem.pi
    return dd

def hms2dh(hms):
    '''
    given signed hms string return float hours
    '''
    dh = hms2dd(hms)/15
    return dh

def RaDec2AzEl(DateTime,Ra,Dec,Lat,Lon,Alt=0,display=False):
    '''
    Given ra/dec pointing and an observation lat(deg),lon(deg),alt(m) at a UTC time
    convert to az/el angles.  All inputs and outputs in degrees.
    '''
    # We need to create a "Body" in pyephem, which represents the coordinate
    # http://stackoverflow.com/questions/11169523/how-to-compute-alt-az-for-given-galactic-coordinate-glon-glat-with-pyephem
    body = ephem.FixedBody()
    body._ra = np.radians(Ra)
    body._dec = np.radians(Dec)
    # Set observer parameters
    obs = ephem.Observer()
    obs.lon = np.radians(Lon)
    obs.lat = np.radians(Lat)
    obs.elevation = Alt
    obs.date = DateTime
    # Turn refraction off by setting pressure to zero
    obs.pressure = 0
    # Compute alt / az of the body for that observer
    body.compute(obs)
    az, alt = np.degrees([body.az, body.alt])
    return az, alt

def AzEl2RaDec(DateTime,Az,El,Lat,Lon,Alt=0,display=False):
    '''
    Given az/el pointing and an observation lat(deg),lon(deg),alt(m) at a UTC time
    convert to rad/dec angles.  All inputs and outputs in degrees.
    '''
    # convert to radians
    az = np.radians(Az)
    el = np.radians(El)
    lon = np.radians(Lon)
    lat = np.radians(Lat)
    alt = Alt
    # Define an observer:
    observer = ephem.Observer()
    observer.lon = lon
    observer.lat = lat
    observer.elevation = alt
    observer.date = DateTime
    # Compute ra,dec
    ra,dec = observer.radec_of(az, el)
    if display:
        print "Time: " + datetime.strftime(DateTime,'%d-%m-%Y %H:%M:%S.%f')
        print "RA: " + str(np.degrees(ra))
        print "DEC: " + str(np.degrees(dec))
    # return output
    return np.degrees(ra),np.degrees(dec)
def GreatCircleDelta(az1,el1,az2,el2):
	'''
	Return sthe central angle between two az/el coordinates (great circle distance)
	Input/Output in degrees
	'''
	lam1 = np.deg2rad(az1)
	phi1 = np.deg2rad(el1)
	lam2 = np.deg2rad(az2)
	phi2 = np.deg2rad(el2)
	dlam = lam2-lam1
	if abs(dlam) < 0.00001:
		delta = 0
	else:
		sigma = np.arccos( (np.sin(phi1)*np.sin(phi2)) + (np.cos(phi1)*np.cos(phi2)*np.cos(dlam)) )
		delta = abs(np.rad2deg(sigma))
	return delta

def dbug(flag,text):
    if flag:
        print "[DBUG]: ",text

def countup(counter):
    '''
    The following increments in the counter in DECIMAL.
    I based this counting scheme on what I observed during comms capture
    '''
    if counter == 0:
        counter = 17
        return counter
    else:
        counter = counter + 16;
        if counter > 255:
            counter = 1
        return counter

def prepare(payload,Counter):
    Payload = payload.encode('hex')
    Header = '1002'
    SOH = '01'
    Counter = '{:02x}'.format(Counter)
    Filler = checkbytes(fletcher_16(SOH+Counter+Payload))
    Footer = '1003'
    return Header+SOH+Counter+Payload+Filler+Footer

def unpack(hex_response):
    # Get rid of the first 4 bytes:
    # hex_payload = hex_response[4:-4]
    hex_payload = bytearray(hex_response)
    return hex_payload[4:-4]

def fletcher_16(hex_string, modulus=255):
	'''
	Calculate the Fletcher-16 checksum of *data*, default modulus 255.

	Returns an upper case, zero-filled hex string with no prefix such as
	``0A1B``.

	>>> fletcher_16("hello,world")
	'6C62'
	>>> fletcher_16("hello,world", 256)
	'6848'
	'''

	numbers = bytearray.fromhex(hex_string)

	a = b = 0
	for number in numbers:
		a += number
		b += a
	a %= modulus
	b %= modulus
	fletch = hex((a << 8) | b)[2:].upper().zfill(4)
	return fletch

def checkbytes(f16, modulus=255):
	'''
	 Accepts an upper case, zero-filled hex string with no prefix.
	 Assumes a 2-byte fletcher checksum is given...
	'''
	c0 = int(f16[:2],16)
	c1 = int(f16[-2:],16)
	cb0 = modulus - ((c0 + c1)%modulus)
	cb1 = modulus - ((c0 + cb0)%modulus)
	hex_string = '{0:02x}'.format(cb0)+'{0:02x}'.format(cb1)
	return hex_string.upper()

def compute_sidereal_time(lon,lat=0,alt=0,t=datetime.utcnow()):
    '''
    Return local apparent sidereal time in decimal hours:

    Inputs [required]
    lon - (float) longitude in decimal degrees

    Inputs [optional]
    lat - (float, default=0) latitude in decimal degrees
    alt - (float, default=0) altitude in meteres
    time - (float, default=now) datetime object

    Output
    sidereal_time - (float) local apparent sidereal time in decimal hours
    '''
    ovr = ephem.Observer()
    ovr.lon = lon * ephem.degree
    ovr.lat = lat * ephem.degree
    ovr.elevation = alt
    ovr.date = t
    st = ovr.sidereal_time()
    st_hours = (st/ephem.degree)/15 # convert time in radians to decimal hours
    return st_hours

'''
----------------------------------------------------------
/////////////////  Command Line Console  \\\\\\\\\\\\\\\\\
----------------------------------------------------------
'''
def Console(live=True):
    '''
    Provides console interface to talk to the mount.  Takes care of command formatting.
    Type "exit" to end.
    '''
    print "-------------------------------------------------------------"
    print "           Archimage Telescope Command Console"
    print "-------------------------------------------------------------"
    print " + Type commands and press <enter> to send.\n + Responses will be displayed after each command.\n + Type 'exit' and press <enter> to quit."
    print "-------------------------------------------------------------"

    # instantiate mount, set live/testing
    mount = archimage(live=live)

    while True:
        print "Enter command:"
        p = raw_input(">> ")
        if p == 'exit':
            print "-------------------------------------------------------------"
            print "                          Bye."
            print "-------------------------------------------------------------"
            exit()
        else:
            mount.send(p)

if __name__ == "__main__":
    Console(live=True)
