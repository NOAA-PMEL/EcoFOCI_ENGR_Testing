C     Last change: JA 10/22/2015 1:00:44 PM
      program G1TiltCorr
      integer hh,mm,ss,date,r,c,i,lss,n,lhh,lmm,m,n2,ldate,lms
      integer j(200000,5),k,s,e,l(102),m2(102),n1n,n2n,ms,nr,time
      integer filflg,navflg,lmms,lhhs,vflg,fn1,fn2,fn3,fn4,fn5,fn6
      integer ltn,lgn,ptn,rln,hdn,aln
      REAL*8  rsec,avg(102),x(102),mavg(102),std(102)
      real*8 off(8),cal(8),amp(8),sza,sc1,tilt,pi,tlim,spnn1,spnn2
      real*8 dechr,lat,lon,pit,rol,hed,pit1,rol1,cz,dc1,az,alt
      real*8 udat(200000,102),tmp,sfac,pit2,rol2,dc2,cor1,cor2
      real*8 pit3,rol3,dc3,cor3,sc3,hed1,hed2,hed3,sc2
      real*8 dirn, dr,spnd,spnt,spn1,spn2,dir,dircorr
      real*8 spn1corr,spn2corr,spntcorr,spn1dif,spn2dif,spntdif
      CHARACTER*80 dirfil,infil,allfil,outfil,out2,cnffil
      CHARACTER*400 line
      CHARACTER*700 hdr
      LOGICAL OK,ok2

      dirfil='AAF_G1_TiltCorr.dir'
      allfil='AAF_G1_TiltCorr.all'
      cnffil='AAF_G1_TiltCorr.cnf'

      OPEN(UNIT=1,FILE=cnffil,STATUS='old')
      OPEN(UNIT=2,FILE='cnf_read.asc',STATUS='unknown')
      read(1,*) nh
      write(2,3)' NUMBER header lines to skip: ', nh
      read(1,*) nr
      write(2,3)' NUMBER Reals: ', nr
      read(1,*) fn1
      write(2,3)' # SPN Tot: ', fn1
      read(1,*) fn2
      write(2,3)' # SPN Dif: ', fn2
      read(1,*) fn3
      write(2,3)' # Zen Tot1: ', fn3
      read(1,*) fn4
      write(2,3)' # Zen Tot2: ', fn4
      read(1,*) fn5
      write(2,3)' # Nad Tot1: ', fn5
      read(1,*) fn6
      write(2,3)' # Nad Tot2: ', fn6
      read(1,*) ltn
      write(2,3)' # Lat: ', ltn
      read(1,*) lgn
      write(2,3)' # Lon: ', lgn
      read(1,*) ptn
      write(2,3)' # pit: ', ptn
      read(1,*) rln
      write(2,3)' # rol: ', rln
      read(1,*) hdn
      write(2,3)' # hed: ', hdn
      read(1,*) aln
      write(2,3)' # alt: ', aln
      read(1,*) tlim
      write(2,*)'  Tlim=',tlim
      read(1,*) pit1,rol1,hed1
      write(2,2)'  pit1, rol1, hed1 =',pit1,rol1,hed1
      read(1,*) pit2,rol2,hed2
      write(2,2)'  pit2, rol2, hed2 =',pit2,rol2,hed2
      read(1,*) pit3,rol3,hed3
      write(2,2)'  pit3, rol3, hed3 =',pit3,rol3,hed3
      read(1,*)
      read(1,5) hdr
 2    format(a,20f12.4)
 3    format(a,20i8)
cc      pause
      close(unit=1)
      close(unit=2)

      pi=dacos(-1.d0)

 5    format(a,a,a,a,a,a,a,a)

      OPEN(UNIT=9,FILE=allfil,STATUS='unknown')
      WRITE(9,5)'    date  hh  mm       N       Lat      Long     Pitch
     %     Roll     Hding         Alt      tilt      CosZ       SZA
     % SZT1      SZT2     STotT   SZ1Corr   SZ2Corr  STotCorr  SDirCorr
     %    SDiff    SZ1Dif    SZ2Dif   STotDif      Cor1      Cor2
     % Cor3'//hdr


      OPEN(UNIT=1,FILE=dirfil,STATUS='old')
 10   READ(1,11,END=100) infil
 11   FORMAT(a80)
      OK=.true.
      n=0
      n2=0
      m=0

      do i=1,102
        avg(i)=0.0
        mavg(i)=0.0
        l(i)=0
        m2(i)=0
      end do

      do r=1,200000
        do c=1,102
          udat(r,c)=0.0
        end do
        do i=1,5
          j(r,i)=0
        end do
      end do

      i=INDEX(infil,'.')
      outfil=infil(1:i)//'1sec'
      OPEN(UNIT=3,FILE=outfil,STATUS='unknown')

      out2=infil(1:i)//'10Hz'
      OPEN(UNIT=8,FILE=out2,STATUS='unknown')

      WRITE(3,5)'    date  hh  mm  ss       N       Lat      Long     Pi
     %tch      Roll     Hding         Alt      tilt      CosZ       SZA
     %     SZT1      SZT2     STotT   SZ1Corr   SZ2Corr  STotCorr  SDirC
     %orr     SDiff    SZ1Dif    SZ2Dif   STotDif      Cor1      Cor2
     %     Cor3'//hdr


      WRITE(8,5)'    date  hh  mm  ss  Hs       Lat      Long     Pitch
     %     Roll     Hding         Alt      tilt      CosZ       SZA
     % SZT1      SZT2     STotT   SZ1Corr   SZ2Corr  STotCorr  SDirCorr
     %    SDiff    SZ1Dif    SZ2Dif   STotDif      Cor1      Cor2
     % Cor3'//hdr

      r=0

      OPEN(UNIT=2,FILE=infil,STATUS='old')
      WRITE(6,*)'  Opened infile: ',infil

      if(nh.gt.0) then
        do s=1,nh
          read(2,*)
        end do
      endif

 20   READ(2,*,END=50) date,time,ms,(x(i),i=1,nr)
 21   FORMAT(a400)

      hh=time/10000
      mm=(time-hh*10000)/100
      ss=(time-hh*10000-mm*100)

      rsec=ss*1.0+(ms/100.0)
      dechr=hh*1.0+(mm/60.0)+(rsec/(60.0*60.0))

        lat=x(ltn)
        lon=x(lgn)
        pit=x(ptn)
        rol=x(rln)
        hed=x(hdn)
        alt=x(aln)

      if(pit.lt.-900.0.or.rol.lt.-900.0.or.hed.lt.-900.0) then
        ok2=.false.
      else
        ok2=.true.
      endif

      spnn1=x(fn5)
      spnn2=x(fn6)
      spnt=x(fn1)
      spnd=x(fn2)
      spn1=x(fn3)
      spn2=x(fn4)
      dir=spnt-spnd
      IF(dir.lt.0.d0) dir=0.d0


cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
ccccccccc pit1 and rol1 are offsets for shaded SPN  Total cccccc
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
        call aircraft_tilt(date,dechr,0,lat,lon,pit,rol,
     %hed,pit1,rol1,hed1,cz,dc1,az)

        SZA=ACOS(cz)*180.0/pi
        sc1=ACOS(dc1)*180.0/pi
        tilt=sza-sc1
          dirN=(spnt-spnd)/dc1
          IF(dirN.le.0.d0) dirN=0.0001d0
          dr=spnd/dirN
          cor1=(cz+dr)/(dc1+dr)

          IF(spnt.GT.0.0.and.abs(tilt).le.tlim.and.ok2) then
            spntcorr=spnt*cor1
            spntdif=spnt-spntcorr
          else
            spntcorr=-999.0
            spntdif=-999.0
            spnt=-999.0
          endif
          IF(dir.GT.-0.000001d0.and.abs(tilt).le.tlim.and.ok2) then
            dircorr=dir*(cz/dc1)
            IF(dircorr.lt.0.d0) dircorr=0.d0
          else
            dircorr=-999.0
          endif

          if(.not.ok2) then
           SZA=-999.0
           sc1=-999.0
           tilt=-999.0
          endif
      

cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
cccccccccc pit2 and rol2 are offsets for unshaded SPN Zen1 ccccc
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
        call aircraft_tilt(date,dechr,0,lat,lon,pit,rol,
     %hed,pit2,rol2,hed2,cz,dc2,az)
      
        sc2=ACOS(dc2)*180.0/pi
        cor2=(cz+dr)/(dc2+dr)

          IF(spn1.GT.0.0.and.abs(tilt).le.tlim.and.ok2) then
            spn1corr=spn1*cor2
            spn1dif=spn1-spn1corr
          else
            spn1corr=-999.0
            spn1dif=-999.0
            spn1=-999.0
          endif
        
          if(.not.ok2) sc2=-999.0

cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
cccccccccc pit3 and rol3 are offsets for unshaded SPN Zen2 ccccc
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
        call aircraft_tilt(date,dechr,0,lat,lon,pit,rol,
     %hed,pit3,rol3,hed3,cz,dc3,az)
      
        sc3=ACOS(dc3)*180.0/pi

          cor3=(cz+dr)/(dc3+dr)
          IF(spn2.GT.0.0.and.abs(tilt).le.tlim.and.ok2) then
            spn2corr=spn2*cor3
            spn2dif=spn2-spn2corr
          else
            spn2corr=-999.0
            spn2dif=-999.0
            spn2=-999.0
          endif

          if(.not.ok2) sc3=-999.0
          if(.not.ok2) cz=-999.0

      if(pit.gt.40.0.or.pit.lt.-40.0) then
       pit=-999.0
      endif
      if(rol.gt.40.0.or.rol.lt.-40.0) then
       rol=-999.0
      endif
      if(hed.gt.360.0.or.hed.lt.0.0) then
       hed=-999.0
      endif

      if (abs(tilt).gt.Tlim) then
       spnn1=-999.0
       spnn2=-999.0
       spnd=-999.0
      endif

      x(80)=spn1corr
      x(81)=spn2corr
      x(82)=spntcorr
      x(83)=dircorr
      x(84)=spnd
      x(85)=spn1dif
      x(86)=spn2dif
      x(87)=spntdif
      x(88)=cor1
      x(89)=cor2
      x(90)=cor3
      x(91)=cz
      x(92)=sza
      x(93)=sc1
      x(94)=sc2
      x(95)=sc3
      x(96)=lat
      x(97)=lon
      x(98)=pit
      x(99)=rol
      x(100)=hed
      x(101)=alt

      r=r+1
      do c=1,101
        udat(r,c)=x(c)
      end do
        udat(r,102)=tilt
        j(r,1)=date
        j(r,2)=hh
        j(r,3)=mm
        j(r,4)=ss
        j(r,5)=ms

      IF(ok) then
        lms=ms
        lss=ss
        lhh=hh
        lmm=mm
        lhhs=hh
        lmms=mm
        OK=.false.
      endif

      write(8,27)(j(r,c),c=1,5),(udat(r,c),c=96,102),(udat(r,c),c=91,95)
     %,(udat(r,c),c=80,90),(udat(r,c),c=1,nr)


 25     FORMAT(i8,3i4,2f12.5,4f10.2,25f10.5,13f10.2,3f10.5,2i5,2f10.5)
 26     FORMAT(i8,4i4,2f12.5,4f10.2,25f10.5,13f10.2,3f10.5,2i5,20f10.5)

 27     FORMAT(i8,4i4,5f10.4,f12.2,5f10.4,8f10.2,3f10.5,104f12.5)
      GO TO 20

 50   CLOSE(UNIT=2)

ccccccc  do 1-minute averages  cccccccccccccccc
 
      lhh=j(1,2)
      lmm=j(1,3)
      lss=j(1,4)
      lms=j(1,5)
      lhhs=j(1,2)
      lmms=j(1,3)

cc      write(6,*)' after 50, date & time:',(j(1,s),s=1,5)
cc      pause

      m=0
      do i=1,102
        m2(i)=0
        l(i)=0
      end do
      n=0
      n2=0

      do k=1,r
       hh=j(k,2)
       mm=j(k,3)
       ss=j(k,4)
       ms=j(k,5)
       IF(mm.eq.lmm) then
        m=m+1

        if(m.gt.1500) then
          write(6,*)' m>1500',j(k,1),hh,mm,lmm,lhh
          pause
        endif

        do i=1,102
          if(udat(k,i).ge.-900.0) then
            mavg(i)=mavg(i)+udat(k,i)
            m2(i)=m2(i)+1
          endif
        end do
       else
        do i=1,102
          if(m2(i).gt.0) then
            mavg(i)=mavg(i)/m2(i)
          else
            mavg(i)=-999.0
          endif
        end do

      WRITE(9,28)date,lhh,lmm,m,(mavg(s),s=96,102),(mavg(s),s=91,95),
     %(mavg(s),s=80,90),(mavg(s),s=1,nr)
 28     FORMAT(i8,2i4,i8,5f10.4,f12.2,5f10.4,8f10.2,3f10.5,104f12.5)

        do i=1,102
          if(udat(k,i).ge.-900.0) then
            mavg(i)=udat(k,i)
            m2(i)=1
          else
            mavg(i)=0.0
            m2(i)=0
          endif
        end do
        m=1
        lhh=hh
        lmm=mm
       endif


ccccccccccccccccc  do 1-sec averaging  cccccccccccccccc
       IF(ss.eq.lss) then
        n=n+1

        if(n.gt.25) then
          write(6,*)' n>25',j(k,1),hh,mm,ss,lmms,lhhs,lss
          pause
        endif

        do i=1,102
          if(udat(k,i).ge.-900.0) then
            avg(i)=avg(i)+udat(k,i)
            l(i)=l(i)+1
          endif
        end do
       else
        do i=1,102
          if(l(i).gt.0) then
            avg(i)=avg(i)/l(i)
          else
            avg(i)=-999.0
          endif
        end do

      WRITE(3,29)date,lhhs,lmms,lss,n,(avg(s),s=96,102),
     %(avg(s),s=91,95),(avg(s),s=80,90),(avg(s),s=1,nr)
 29     FORMAT(i8,3i4,i8,5f10.4,f12.2,5f10.4,8f10.2,3f10.5,104f12.5)

        do i=1,102
          if(udat(k,i).ge.-900.0) then
            avg(i)=udat(k,i)
            l(i)=1
          else
            avg(i)=0.0
            l(i)=0
          endif
        end do

        n=1
        lss=ss
        lhhs=hh
        lmms=mm
       endif

      end do

      CLOSE(UNIT=3)
      CLOSE(UNIT=8)


 90   GO TO 10

 100  CLOSE(UNIT=1)
      CLOSE(UNIT=9)

      end program
ccccccccccccccccccccccccccccccccccccccccccccccccccccccc

CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C	Program for calculating solar zenith and azimuth angle as well as
C       zenith and azimuth angles of the pyranometer
C	where pyrzenith=0 means that the aircraft (pyranometer) is leveled. 
C       It is important to measure the offset angles between the aircraft 
C       and pyranometer horizon (pitch and roll). These offsets can be 
C       included in the rph2za routine.
C	End product is the cosine of the angle between the sun and 
C       the instrument angular position. When the aircraft (pyranometer)
C	is in level, this angle is just the solar zenith angle.

C	All programs were originally written by Paul Ricchiazzi in IDL
C       Rewritten to FORTRAN 77 by Yan Shi, PNNL, 10/1/2008

      subroutine aircraft_tilt(date,time,local,lat,lon,pit,rol,
     %hed,pit0,rol0,hed0,cz,dc,azimuth)

	integer year,month,day,date,local
	real*8 time,lat,lon,pit,rol,hed,sza,azimuth,cz
	real*8 pit0,rol0,juld,dc,solfac,pyrzenith,pyrazimuth
	real*8 julian_day, muslope,hed0
	real*8 sunrise,sunset,latsun,lonsun

      parameter (pi=3.1415926)
      parameter (dtor=pi/180)

c       convert date to yr/mn/dy
        year=date/10000
        month=(date-(year*10000))/100
        day=date-(year*10000)-month*100

C 	get Julian day
	juld=julian_day(year,month,day)

C         Convert roll, pitch, heading to instrument zenith and azimuth angles
	  call rph2za(pit+pit0,rol+rol0,hed+hed0,pyrzenith,pyrazimuth)

C         Calculate sza and solar azimuth angle
  	  call zensun(juld,time,lat,lon,sza,azimuth,solfac,local,
     &  sunrise,sunset,latsun,lonsun)
          cz=COS(sza*dtor)

C         Get cosine of angle between sun and instrument = cos(sza) if instrument pointing to zenith
 	  dc=muslope(sza,azimuth,pyrzenith,pyrazimuth)

	end

c=========================================================
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C       Function to calculate Julian Day 
C       Yan Shi, PNNL, 2008/10/2
C       Coverted from IDL code
C
	function julian_day(year,month,day)
	real*8 julian_day
	integer year,month,day,s

C       leap year -> s=1:
	s=0
	if (mod(year,4) .eq. 0) then
	  s=1
	  if (mod(year,100) .eq. 0) then
            s=0
	    if (mod(year,400) .eq. 0) then
              s=1
           end if
	  end if
	end if

	if (month .eq. 1) julian_day=day
	if (month .eq. 2) julian_day=day+31
	if (month .eq. 3) julian_day=day+31+28+s
	if (month .eq. 4) julian_day=day+31+28+s+31
	if (month .eq. 5) julian_day=day+31+28+s+31+30
	if (month .eq. 6) julian_day=day+31+28+s+31+30+31
	if (month .eq. 7) julian_day=day+31+28+s+31+30+31+30
	if (month .eq. 8) julian_day=day+31+28+s+31+30+31+30+31
	if (month .eq. 9) julian_day=day+31+28+s+31+30+31+30+31+31
	if (month .eq. 10) julian_day=day+31+28+s+31+30+31+30+31+31+30
      if (month .eq. 11) julian_day=day+31+28+s+31+30+31+30+31+31+30+31
      if (month.eq.12) julian_day=day+31+28+s+31+30+31+30+31+31+30+31+30
	
	end

c==========================================================
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C
C ROUTINE:  muslope
C
C PURPOSE:  compute dot product of surface normal to incomming solar ray
C
C USEAGE:   result=muslope(sunzen,sunaz,nrmzen,nrmaz)
C
C INPUT:    
C   sunzen  solar zenith angle (degrees)
C
C   sunaz   solar azimuth angle (clockwise from due north, degrees) 
C
C   nrmzen  zenith angle of surface normal vector
C           (nrmzen=0 for a horizontal surface)
C
C   nrmaz   azimuth angle of surface normal vector (nrmaz=45 degrees
C           for a surface that slopes down in the north-east direction)
C
C OUTPUT:
C   result  cosine of angle between sun and instrument 
C           = cos(sza) if instrument pointing to zenith
C
C AUTHOR:   Yan Shi, PNNL, 10/2/2008 
C           converted from IDL code by Paul Ricchiazzi
C           Institute for Computational Earth System Science
C           University of California, Santa Barbara
C           paul@icess.ucsb.edu
C
	function muslope(sunzen,sunaz,nrmzen,nrmaz)

	real*8 muslope
	real*8 zs,ys,xs,zv,yv,xv
	real*8 sunzen,sunaz,nrmzen,nrmaz

      parameter (pi=3.1415926)
      parameter (dtor=pi/180)

	zs=cos(sunzen*dtor)
	ys=sin(sunzen*dtor)*cos(sunaz*dtor)
	xs=sin(sunzen*dtor)*sin(sunaz*dtor)
	zv=cos(nrmzen*dtor)
	yv=sin(nrmzen*dtor)*cos(nrmaz*dtor)
	xv=sin(nrmzen*dtor)*sin(nrmaz*dtor)

	muslope=xs*xv+ys*yv+zs*zv

	end


c=========================================================
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C      Converted by Yan Shi, PNNL, 10/2/2008
C      from IDL subroutine by Paul Ricchiazzi, 25 Feb 97 paul@icess.ucsb.edu
C
C      all angles in degrees
C      pitch  : positive values indicate nose up
C      roll   : positive values indicate right wing down
C      azimuth: positive values clockwise, w.r.t. NORTH
C      roll=roll*0.
C      assume aircraft heading north: rotate around roll

	subroutine rph2za(pitch,roll,heading,zenith,azimuth)
	real*8 pi,dtor,uz,ux,uy,vz,vx,vy
	real*8 pitch,roll,heading,zenith,azimuth

      parameter (pi=3.1415926)
      parameter (dtor=pi/180)

 	uz=cos(roll*dtor)*cos(pitch*dtor)
	ux=sin(roll*dtor)
	uy=-cos(roll*dtor)*sin(pitch*dtor)

C      now rotate to correct heading
	vz=uz
	vx=ux*cos(heading*dtor)+uy*sin(heading*dtor)
	vy=uy*cos(heading*dtor)-ux*sin(heading*dtor)

	zenith=acos(vz)/dtor
        IF(vy.eq.0.0) vy=0.00000001
	azimuth=atan2(vx,vy)/dtor
 
       end
c=========================================================
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C	
C	ROUTINE:      zensun
C	
C	PURPOSE:      Compute solar position information as a function of
C	              geographic coordinates, date and time.
C	
C	INPUT:
C	  jday        Julian day
C	              (spring equinox =  80)
C	              (summer solstice= 171)
C	              (fall equinox   = 266)
C	              (winter solstice= 356)
C	
C	  time        Universal Time in hours
C
C	  lat         geographic latitude of point on earth's surface (degrees)
C	
C	  lon         geographic longitude of point on earth's surface (degrees)
C	
C	OUTPUT:
C	
C	  zenith      solar zenith angle (degrees)
C	
C	  azimuth     solar azimuth  (degrees)
C	              Azimuth is measured clockwise from due north
C	
C	  solfac      Solar flux multiplier.  SOLFAC=cosine(ZENITH)/RSUN^2
C	              where rsun is the current earth-sun distance in
C	              astronomical units.
C	
C	              NOTE: SOLFAC is negative when the sun is below the horizon
C	
C	
C	Input parameter:
C	
C	  local       if local=1, TIME is specified as a local time and SUNRISE
C	              and SUNSET are output in terms of local time
C	
C	              NOTE: "local time" is defined as UT + local_offset
C	                    where local_offset is fix((lon+sign(lon)*7.5)/15)
C	                    with -180 < lon < 180
C	
C	                    Be aware, there are no fancy provisions for
C	                    day-light savings time and other such nonsense.
C	
C	Other output parameters:
C	
C	  sunrise     Time of sunrise (hours)
C	  sunset      Time of sunset  (hours)
C	
C	  latsun      the latitude of the sub-solar point (fairly constant over day)
C	              Note that daily_minimum_zenith=abs(latsun-lat)
C	
C	  lonsun      the longitude of the sub-solar point
C	              Note that at 12 noon local time (lon-lonsun)/15. is the
C	              number of minutes by which the sun leads the clock.
C	
C		         Often used           lat,   lon
C	
C	              Santa Barbara:        34.410,-119.727
C	              SGP Cart Site:        36.605,-97.485
C	              North Slope:          69.318,-151.015
C	              Palmer Station:       -64.767,-64.067
C	
C	 AUTHOR:      Yan Shi, PNNL, 2008/10/2
C                     converted from IDL code by Paul Ricchiazzi
C	              Earth Space Research Group,  UCSB
C	
C	PROCEDURE:
C	
C	1.  Calculate the subsolar point latitude and longitude, based on
C	    DAY and TIME. Since each year is 365.25 days long the exact
C	    value of the declination angle changes from year to year.  For
C	    precise values consult THE AMERICAN EPHEMERIS AND NAUTICAL
C	    ALMANAC published yearly by the U.S. govt. printing office.  The
C	    subsolar coordinates used in this code were provided by a
C	    program written by Jeff Dozier.
C	
C	 2. Given the subsolar latitude and longitude, spherical geometry is
C	    used to find the solar zenith, azimuth and flux multiplier.
C	
C	 eqt = equation of time (minutes)  solar longitude correction = -15*eqt
C	 dec = declination angle (degrees) = solar latitude
C	
C	Analemma information from Jeff Dozier
C	    This data is characterized by 74 points
C	
      subroutine zensun(jday,time0,lat,lon,zenith,azimuth,solfac,local,
     &  sunrise,sunset,latsun,lonsun)

	real*8 jday,time,time0,lat,lon,zenith,azimuth,solfac
	real*8 sunrise,sunset,latsun,lonsun
	real*8 nday(74),eqt(74),dec(74),eqtime,decang
	real*8 tt,lonorm,noon,tzone, ut
	real*8 t0,t1,p0,p1,zz,xx,yy,rsun
	integer local
	real*8 angsun,arg,dtime
        REAL tmp

      parameter (pi=3.1415926)
      parameter (dtor=pi/180)
        
        data nday/1.0,6.0,11.0,16.0,21.0,26.0,31.0,36.0,41.0,46.0,
     +	1.0,56.0,61.0,66.0,71.0,76.0,81.0,86.0,91.0,96.0,
     +  101.0,106.0,111.0,116.0,121.0,126.0,131.0,136.0,141.0,146.0,
     +  151.0,156.0,161.0,166.0,171.0,176.0,181.0,186.0,191.0,196.0,
     +  201.0,206.0,211.0,216.0,221.0,226.0,231.0,236.0,241.0,246.0,
     +  251.0,256.0,261.0,266.0,271.0,276.0,281.0,286.0,291.0,296.0,
     +  301.0,306.0,311.0,316.0,321.0,326.0,331.0,336.0,341.0,346.0,
     +  351.0,356.0,361.0,366.0/

	data eqt/-3.23,-5.49,-7.60,-9.48,-11.09,-12.39,-13.34,-13.95,
     +-14.23,-14.19,
     + -13.85,-13.22,-12.35,-11.26,-10.01,-8.64,-7.18,-5.67,-4.16,-2.69,
     + -1.29,-0.02,1.10,2.05,2.80,3.33,3.63,3.68,3.49,3.09,
     + 2.48,1.71,0.79,-0.24,-1.33,-2.41,-3.45,-4.39,-5.20,-5.84,
     + -6.28,-6.49,-6.44,-6.15,-5.60,-4.82,-3.81,-2.60,-1.19,0.36,
     + 2.03,3.76,5.54,7.31,9.04,10.69,12.20,13.53,14.65,15.52,
     + 16.12,16.41,16.36,15.95,15.19,14.09,12.67,10.93,8.93,6.70,
     + 4.32,1.86,-0.62,-3.23/

	data dec/-23.06,-22.57,-21.91,-21.06,-20.05,-18.88,-17.57,
     + -16.13,-14.57,-12.91,
     +  -11.16,-9.34,-7.46,-5.54,-3.59,-1.62,0.36,2.33,4.28,6.19,
     +  8.06,9.88,11.62,13.29,14.87,16.34,17.70,18.94,20.04,21.00,
     +  21.81,22.47,22.95,23.28,23.43,23.40,23.21,22.85,22.32,21.63,
     +  20.79,19.80,18.67,17.42,16.05,14.57,13.00,11.33,9.60,7.80,
     +  5.95,4.06,2.13,0.19,-1.75,-3.69,-5.62,-7.51,-9.36,-11.16,
     +  -12.88,-14.53,-16.07,-17.50,-18.81,-19.98,-20.99,-21.85,-22.52,
     +  -23.02,-23.33,-23.44,-23.35,-23.06/

	time=time0+0.0
C	
C	compute the subsolar coordinates
C	
ccc	tt=mod(jday+time/24-1,365.25)+1  !fractional day number with 12am 1 jan = 1
        tmp= jday+time/24-1
	tt=mod(tmp,365.25)+1  !fractional day number with 12am 1 jan = 1
	call spline_b_val(74,nday,eqt,tt,eqtime)
	eqtime=eqtime/60.

	call spline_b_val(74,nday,dec,tt,decang)
	latsun=decang

	if (local .eq. 1) then
          tmp=lon
          lonorm=mod((tmp + 360 + 180 ),360.0 ) - 180.
	  tzone=int((lonorm+7.5)/15)
	  if (lonorm .lt. 0) tzone=int((lonorm-7.5)/15)
          tmp=time-tzone+24.0
	  ut=mod(tmp,24.0) !universal time
	  noon=tzone+12.-lonorm/15. !local time of noon
	else
	  ut=time
	  noon=12.-lon/15.	!universal time of noon
	end if

	lonsun=-15.*(ut-12.+eqtime)

C	compute solar zenith, azimuth and flux multiplier

	t0=(90.-lat)*dtor              !colatitude of point
	t1=(90.-latsun)*dtor           !colatitude of sun

	p0=lon*dtor                    !longitude of point
	p1=lonsun*dtor                 !longitude of sun

	zz=cos(t0)*cos(t1)+sin(t0)*sin(t1)*cos(p1-p0) !up         
	xx=sin(t1)*sin(p1-p0)	                      !east-west > rotated coor
  	yy=sin(t0)*cos(t1)-cos(t0)*sin(t1)*cos(p1-p0) !north-south 
	
	azimuth=atan2(xx,yy)/dtor      !solar azimuth
	zenith=acos(zz)/dtor           !solar zenith

        rsun=1.-0.01673*cos(.9856*(tt-2.)*dtor) !earth-sun distance in AU
	solfac=zz/rsun**2	!flux multiplier

	angsun=6.96e10/(1.5e13*rsun) !solar disk half-angle
       	arg=-(sin(angsun)+cos(t0)*cos(t1))/(sin(t0)*sin(t1))
	sunrise = arg - arg
	sunset  = arg - arg + 24.
	if (abs(arg) .le. 1) then
          dtime=acos(arg)/(dtor*15)
          sunrise=noon-dtime-eqtime
          sunset=noon+dtime-eqtime
        end if

	end

c==========================================================
        subroutine spline_b_val ( ndata, tdata, ydata, tval, yval )

C*****************************************************************************
C
C! SPLINE_B_VAL evaluates a cubic B spline approximant.
C
C       Discussion:
C
C         The cubic B spline will approximate the data, but is not
C         designed to interpolate it.
C
C         In effect, two "phantom" data values are appended to the data,
C         so that the spline will interpolate the first and last data values.
C
C       Modified:
C
C         Converted from f90 to f77 by Yan Shi, PNNL, 10/3/2008
C       
C         11 February 2004
C
C       Author:
C
C         John Burkardt
C
C       Reference:
C
C         Carl deBoor,
C         A Practical Guide to Splines,
C         Springer, 2001,
C         ISBN: 0387953663.
C
C       Parameters:
C
C         Input, integer NDATA, the number of data values.
C
C         Input, real*8 TDATA(NDATA), the abscissas of the data.
C
C         Input, real*8 YDATA(NDATA), the data values.
C
C         Input, real*8 TVAL, a point at which the spline is
C         to be evaluated.
C
C         Output, real*8 YVAL, the value of the function at TVAL.
C
       implicit none

       integer ndata

       real*8 bval
       integer left
       integer right
       real*8 tdata(ndata)
       real*8 tval
       real*8 u
       real*8 ydata(ndata)
       real*8 yval
C
C       Find the nearest interval [ TDATA(LEFT), TDATA(RIGHT) ] to TVAL.
C
       call r8vec_bracket ( ndata, tdata, tval, left, right )
C
C       Evaluate the 5 nonzero B spline basis functions in the interval,
C       weighted by their corresponding data values.
C
       u = ( tval - tdata(left) ) / ( tdata(right) - tdata(left) )
       yval = 0.0D+00
C
C       B function associated with node LEFT - 1, (or "phantom node"),
C       evaluated in its 4th interval.
C
       bval = ( ( ( - 1.0D+00 
     &                                   * u + 3.0D+00 ) 
     &                                   * u - 3.0D+00 ) 
     &                                   * u + 1.0D+00 ) / 6.0D+00

       if ( 0 < left-1 ) then
              yval = yval + ydata(left-1) * bval
       else
              yval = yval + ( 2.0D+00 * ydata(1) - ydata(2) ) * bval
       end if
C
C       B function associated with node LEFT,
C       evaluated in its third interval.
C
       bval = ( ( ( 3.0D+00        
     &                                   * u - 6.0D+00 ) 
     &                                   * u + 0.0D+00 ) 
     &                                   * u + 4.0D+00 ) / 6.0D+00

       yval = yval + ydata(left) * bval
C
C       B function associated with node RIGHT,
C       evaluated in its second interval.
C
       bval = ( ( ( - 3.0D+00        
     &                                   * u + 3.0D+00 ) 
     &                                   * u + 3.0D+00 ) 
     &                                   * u + 1.0D+00 ) / 6.0D+00

       yval = yval + ydata(right) * bval
C
C       B function associated with node RIGHT+1, (or "phantom node"),
C       evaluated in its first interval.
C
       bval = u**3 / 6.0D+00

       if ( right+1 <= ndata ) then
              yval = yval + ydata(right+1) * bval
       else
              yval = yval + ( 2.0D+00 * ydata(ndata) - ydata(ndata-1) ) * bval
       end if

       return
       end

      subroutine r8vec_bracket ( n, x, xval, left, right )

C*****************************************************************************
C
C! R8VEC_BRACKET searches a sorted R8VEC for successive brackets of a value.
C
C  Discussion:
C
C    An R8VEC is an array of double precision real values.
C
C    If the values in the vector are thought of as defining intervals
C    on the real line, then this routine searches for the interval
C    nearest to or containing the given value.
C
C  Modified:
C
C    Converted from f90 to f77 by Yan Shi, PNNL, 10/3/2008
C
C    06 April 1999
C
C  Author:
C
C    John Burkardt
C
C  Parameters:
C
C    Input, integer N, length of input array.
C
C    Input, real*8 X(N), an array sorted into ascending order.
C
C    Input, real*8 XVAL, a value to be bracketed.
C
C    Output, integer LEFT, RIGHT, the results of the search.
C    Either:
C      XVAL < X(1), when LEFT = 1, RIGHT = 2;
C      X(N) < XVAL, when LEFT = N-1, RIGHT = N;
C    or
C      X(LEFT) <= XVAL <= X(RIGHT).
C
       implicit none

       integer n

       integer i
       integer left
       integer right
       real*8 x(n)
       real*8 xval

       do i = 2, n - 1
         if ( xval < x(i) ) then
           left = i - 1
           right = i
           return
         end if
        end do

       left = n - 1
       right = n

       return

       end
c----------------------------------------------------------------------
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
      subroutine stdev(xarray,num,xavg,xstd)
C     routine for calculating the population standard deviation of n
C      values in Xarray
c     Maximum of 10000 values, assumes all "good" values in Xarray
C     Returns both the Xarray average and population Standard Deviation

      integer num,p
      Real*8 Xarray(10000),xavg,xstd,xsumsq

      xavg=0.0
      xsumsq=0.0
      xstd=0.0

      do p=1,num
        xavg=xavg+Xarray(p)
      enddo

      xavg=xavg/(num*1.0)

      do p=1,num
        xsumsq=xsumsq+(xavg-Xarray(p))**2
      enddo

      xstd=SQRT(xsumsq/(num*1.0))

      RETURN
      END
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
      
