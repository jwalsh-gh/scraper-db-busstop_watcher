#!/usr/bin/python

import argparse
import string

import lxml, lxml.html
import re

from datetime import datetime
import time

import subprocess
import platform


# Some Global Constants
scrapetimeformat='%H:%M'
pattern = re.compile(r'\s\s+')

#We want to highlight any bus that will arrive within the threshold time
#There are man solutions on the link below, I have choosen a very simple one.
#http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Print as a warning
def print_coloured_time_remaining(remaining_time,threshold,colour=None):
    if remaining_time <= threshold and colour != None:
        return colour + str(remaining_time) + bcolors.ENDC
    #else return a string without highlighting
    return(str(remaining_time))

def clear_vt100_screen():
    subprocess.Popen( "cls" if platform.system() == "Windows" else "clear", shell=True)


def string_hour_min_to_tuple(instr):
    hour_str,min_str=instr.split(':')
    return int(hour_str),int(min_str)


# Calculate the number of minutes between a start time and end time
# Inputs are in 'hour:min' format. 
# Assume that if the end_time hour is less than start hour, then it refers to the next day
#
def time_delta(start_time,end_time):
    (start_time_hour,start_time_min)=string_hour_min_to_tuple(start_time)
    (end_time_hour,end_time_min)=string_hour_min_to_tuple(end_time)
    # e.g 00:08 < 23:16 (end time is next day)
    if (end_time_hour < start_time_hour):
       end_time_hour=end_time_hour+24
    delta=((end_time_hour*60)+end_time_min) - ((start_time_hour*60)+start_time_min)
    return(delta)


#Ensure no one is trying to inject illegal characters
def sanitise_buslist(instr):
    valid_chars=",%s%s" % (string.ascii_letters, string.digits)
    outstr=''.join(c for c in instr if c in valid_chars)
    return outstr

class DBBusStop:
      def __init__(self, stopnum, bus_filter_list, bus_alarm_threshold):
         self.stopnum = stopnum
         self.filter = bus_filter_list
         self.bus_alarm_threshold = bus_alarm_threshold
         self.filtered_results=self.__parseBusStop__(stopnum,bus_filter_list,bus_alarm_threshold)
       

# I will need to add some exceptions (especially to deal with problems in retrieving the HTML)
      def __parseBusStop__(self,stopnum,busfilter_list=[],alarm_threshold=60):
        pageurl = 'http://www.dublinbus.ie/en/RTPI/Sources-of-Real-Time-Information/?searchtype=view&searchquery='+str(stopnum)
        htmltree = lxml.html.parse(pageurl)
        # Extract the HTML data and replace extrenuous whitespace
        mylist = [ re.sub(pattern,'',listitem) for listitem in htmltree.xpath('/html/body//*/table[@id="rtpi-results"]/tr/td/text()') ]
        # Remove those field that are now empty strings
        mylist = [ x for x in mylist if x != '']
        bus_list = []
    
        time_now_str = datetime.now().strftime(scrapetimeformat)
        chunks=[mylist[x:x+3] for x in xrange(0,len(mylist),3)]
        for chunkbit in chunks:
            if len(chunkbit) == 3:
                bus=chunkbit[0]   
                bus_time=chunkbit[2]
                if bus in busfilter_list or not (busfilter_list):
                    if bus_time.lower() == 'due':
                       bus_time=time_now_str
                    bus_delta=time_delta(time_now_str,bus_time)
		    this_bus=(bus,bus_time, chunkbit[1], bus_delta) 
                    bus_list.append(this_bus)
        return bus_list

      def printbuses(self,highlight=True):
          print('-'*80)
          for bus in self.filtered_results:
            out_string=bus[0] + "\t" + bus[1] + "\t" + print_coloured_time_remaining(bus[3],self.bus_alarm_threshold,bcolors.FAIL)
            print(out_string)



def parseProgramArgs():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stopnum', nargs=1,type=int,help="Bus Stop Number [Integer]",required=True)
    parser.add_argument('--busfilter', nargs=1,type=str,help="List of Buses to filter",required=False)
    parser.add_argument('--alarm', nargs=1,type=int,default=60,help="Alarm threshold in Minutes",required=False)
    args=parser.parse_args()
    if args.busfilter:
      bus_list=sanitise_buslist(args.busfilter[0]).split(',')
    else:
      bus_list=[]
    if args.alarm and isinstance(args.alarm,int): 
      print(args.alarm, str(args.alarm))
    if args.alarm and isinstance(args.alarm,list): 
      alarm_threshold=int(args.alarm[0])
    else:
      alarm_threshold=60
    return (int(args.stopnum[0]),bus_list,alarm_threshold)
    


if __name__ == '__main__':
    myStopNum=parseProgramArgs()
    while True:
        clear_vt100_screen()
        x=DBBusStop(myStopNum[0],myStopNum[1],myStopNum[2])
	x.printbuses()

        time.sleep(10)
    
    
    
