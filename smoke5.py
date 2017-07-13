#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import smoke_UI
import urllib2
import Image, math
import time, datetime
import smtplib
import logging
import logging.handlers
import argparse
from email.mime.text import MIMEText


class SmokeLevel(QMainWindow, smoke_UI.Ui_MainWindow):

        def __init__(self, parent=None):
                super(SmokeLevel, self).__init__(parent)
                self.setupUi(self)
                self.timer = QTimer()
                self.connect(self.timer, SIGNAL('timeout()'), self.on_timer)
                self.timer.start(5000) #update every 5s
                self.todaysdate = datetime.date.today().strftime('%y%m%d')
                self.outfile = '/data/3m/smokelevels/'+self.todaysdate+'.log'
                try :
                        h = open(self.outfile, 'r')
                        h.close()
                except IOError :
                        h = open(self.outfile, 'w')
                        h.close()
         
                self.sentflag1 = 0
                self.sentflag2 = 0 
                self.lastsenttime1 = 0
                self.lastsenttime2 = 0
                        
        def on_timer(self):

                # This requests a jpg image from the camera and saves it
                u = urllib2.urlopen('http://192.168.1.114/img/snapshot.cgi?size=3&quality=1')
                localFile = open('smoke.jpg', 'w') 
                localFile.write(u.read())
                localFile.close()
        
                # This opens the image, crops it
                im0 = Image.open('smoke.jpg')
                #box = (292, 54, 297, 215) #original santiago calibration crop box
                #box = (292, 62, 297, 223) #axl testing
                box = (292, 54, 297, 215) #doug testing
                im1 = im0.crop(box)
                im2 = im1.load()
                im1.save('test.jpg')


                # figures out which led is lit
                # j iterates vetically starting from top
                # i iterates horizontally, five pixels across
                # s is the sum of all rgb components for all five pixels for a given j
                # if a led is lit
                j, s = 0, 0
                while (s < 2800 and j < 161) :
                        s=0
                        for i in range(5):
                                s += sum(im2[i,j])
                        #print 'j=',j,'s=',s
                        j += 1
                #print j

                smoklev = int(round(20.0*(161.0-j)/161.0))

                if (smoklev >=3 and self.sentflag1 == 0) :
                        me = 'threemeter@sodium.umd.edu'
                        team = ['6088524957@messaging.sprintpcs.com','3016466601@txt.att.net','4102151599@vtext.com','2012330354@tmomail.net']
                        msg = MIMEText('High Bay smoke level reached 3/20')
                        msg['Subject'] = 'High Bay smoke level reached 3/20'
                        msg['From'] = me
                        msg['To'] = ', '.join(team)
                        s = smtplib.SMTP('localhost')
                        s.sendmail(me,team,msg.as_string())
                        self.sentflag1 = 1


                if (smoklev >=8 and self.sentflag2 == 0) :
                        me = 'threemeter@sodium.umd.edu'
                        team = ['6088524957@messaging.sprintpcs.com','3016466601@txt.att.net','4102151599@vtext.com','2012330354@tmomail.net']
                        msg = MIMEText('High Bay smoke level reached 8/20')
                        msg['Subject'] = 'High Bay smoke level reached 8/20'
                        msg['From'] = me
                        msg['To'] = ', '.join(team)
                        s = smtplib.SMTP('localhost')
                        s.sendmail(me,team,msg.as_string())
                        self.sentflag2 = 1
				 # gets the time stamp -> conditional for daylight savings time...
                if time.localtime().tm_isdst == 0:
                        tmp1=time.time()-time.timezone
                if time.localtime().tm_isdst == 1:
                        tmp1=time.time()-time.altzone # seconds (local) since unix epoch
                tmp2= math.floor((tmp1/86400.0))*86400.0 # seconds from epoch to midnight
                tstamp = int(round(tmp1-tmp2))

                self.smokelevel.display(smoklev)
                self.tstamp.display(tstamp)


                h = open(self.outfile, 'a')
                h.write(str(tstamp)+' '+str(smoklev)+'\n')
                h.close()
                #print tstamp, smoklev


        def main(self):
                self.show()


if __name__=='__main__':
        app = QApplication(sys.argv)
        sl = SmokeLevel()
        sl.main()
        app.exec_()


                                        
                                                          