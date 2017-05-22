DESIGNED for 2015 ARCTIC OER Mooring

Processing routine (oer_processing.py) currently only converts and outputs .csv into a cleaner format 
 and applies calibration calculations

General Notes:
==============

Tilt, SWR and SPN1 are on same timestamp (make sure SPN1 is first dataline - delete others if necessary)

There have been a couple of locations in the provided documentation that don't provide the necessary details
regarding units/powers of 10 (some of this is due to inconsistency in the database of calibration coef - e.g. microvolts vs volts) )

SPN1 is digital and outputs directly to data stream in engineering units.  Only characterization calibration would be necessary.
SW

Concerns:
=========

Zooming in on demo timeseries look as if PSP lags the SPN1 by one timestep (~5s)
~1% difference in solar instruments (PSP, SPN1) in the morning but increases to close to 10% by afternoon
(may be due to location of initial testing which is by building 32 garbage containers)

Description of datafeed and conversion equations:
=================================================

This information initially comes from Scott Stalin

SHORTWAVE , LONG WAVE RADIATION and SPN-1 SENSORS.
The short wave radiation sensor is an Eppley PSP.
The long wave radiation sensor is an Eppley PIR.

All of these sensors are controlled by a pic board designed at PMEL. They all have these common characteristics: 

OVERVIEW
Their power is on continuously.
Each draws less than a milliamp.
Each samples its respective sensor every second and keep a running sum and number of samples.
When queried for its data, the pic sends the sums and count and restarts its sampling.
These sensors do not have rs232 on the picboards; rather they communicate using a pulse width modulation scheme.  

PWM ON THE PIC SENSORS
The pwm has a bit frequency of 128 hz. 
Every bit starts with a rising edge.
0 bits are 61 microseconds long; this is 2 cycles of a 32768 hz oscillator.
1 bits are 183 microseconds long; this is 6 cycles of a 32768 hz oscillator.
The data request command consists of a minimum 16 millisecond high pulse on the data line. 
The data will then be put out on the data line. 
MSB is output first.


SHORT WAVE RADIATION DATA FORMAT

The SWR samples its sensor every second.
Maximum data request interval is 5 minutes.
For this project we are sampling every 5 seconds.
The first byte = the sum of squares of the samples.
The second byte = the sum of samples.
The third byte=  the count of samples summed.

SWR,02/26/2015,14:06:40, 3125, 125,   5,312.7,+06.3,-000.5     
“Header  Date Time byte1 byte2 byte3 byte4 byte5 byte6”

<cr> = 0x0D
<cr>SWR = message ID
Date = date of sample
Time = time of sample
Byte1 = sum of squares of the samples
Byte2 = sum of samples
Byte3 = the count of samples summed
Byte4 = compass heading
Byte5 = compass pitch
Byte6 = compass roll


SWR CALCULATIONS
SHORTWAVE RADIATION in W/m2
A0 is a the sensor factory calibration coefficient.
A1 is the pic board offset
A2 is the pic board slope
A3 is not used
A4 is not used
Converting from counts to scientific units:
SWR = (m * A2) / A0

The internal PMEL PIC board provides a sum, s, sum of squares, d, and count of samples, n, from which the mean, m, and standard deviation, sd are calculated.  The results are in counts.
Converting from counts to scientific units:
SD = sd * A2 / A0

LONG WAVE RADIATION
The LWR samples its sensors every second.
Maximum data request interval is 5 minutes.
For this project we are sampling every 5 seconds.
The first byte = sum of squares of the samples.
The next byte = the sum of samples.
The next byte = the count of sensor samples.
The next byte = the sum of the dome thermistor.
The next byte = the number of dome thermistor samples.
The next byte = the sum of the case thermistor.
The next byte = number of case thermistor samples.
LWR,02/26/2015,14:06:42, 35956, 424,   5,8272,   5,8272,   5,313.4,+06.2,-000.5
“Header  Date Time byte1 byte2 byte3 byte4 byte5 byte6, byte7, byte8, byte9, byte10”

<cr> = 0x0D
<cr>LWR = message ID
Date = date of sample
Time = time of sample
Byte1 = sum of squares of the samples
Byte2 = sum of samples
Byte3 = the count of samples summed
Byte4 = sum of the dome thermistor
Byte5 = number of dome thermistor samples
Byte6 = the sum of the case thermistor
Byte7 = number of case thermistor samples
Byte8 = compass heading
Byte9 = compass pitch
Byte10 = compass roll


LWR CALCULATIONS
LONGWAVE RADIATION in W/m2
A0 is a scaling factor from Epply calibration
A1 is always 3.5
A2 is always 0
A3 is the pic board offset (* 10^-6 if A0 is of order e-6 and A3 is not)
A4 is the pic board slope (* 10^-6 if A0 is of order e-6 and A4 is not)

The internal PMEL PIC board provides a sum , s, sum of squares, d, count of samples, n, from which the mean, m, and standard deviation, sd are calculated in counts.  

Converting from counts to scientific units:
LWR = ((m * A4 + A3) / A0 ) 
SD = sd * A4 / A0

LONGWAVE TEMPERATURES Case and Dome in °C
A0 is always 1.028742E-03
A1 is always 5.508331E-04
A2 is always 1.906367E-06
A3 is the sensor offset
A4 is the sensor slope

The internal PMEL PIC board of the longwave radiation sensor also provides a sum and number of counts for a case temperature, and a dome temperature.  These are cs, cn, ds, dn respectively.  

Mean values for case temperature, ct and dome temperature, dt are:
ct = cs / cn
dt = ds / dn

The Steinhart – Hart equation is used as follows:
cr = A3 + A4 * (1 /( ct+2500.0))
cx = log10(cr)
CT = 1 / ( A0 + A1 * cx + A2 * cx * cx * cx)
Dome temperature is calculated using the same equations, with the dome coefficients.





SPN-1
SPN,02/26/2015,14:06:55,     5.4,    4.1,1,312.9,+06.3,-000.4                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
 “Header  Date Time byte1 byte2 byte3 byte4 byte5 byte6”

<cr> = 0x0D
<cr>SPN = message ID
Date = date of sample
Time = time of sample
Byte1 = total
Byte2 = diffuse
Byte3 = sunshine presence  0 or 1
Byte4 = compass heading
Byte5 = compass pitch
Byte6 = compass roll

