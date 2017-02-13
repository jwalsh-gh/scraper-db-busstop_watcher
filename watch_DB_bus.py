#!/usr/bin/python

import argparse
import string

import lxml, lxml.html
import requests
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
def print_coloured_time_remaining(in_str,threshold,remaining_time):
    if remaining_time <= threshold:
        return bcolors.FAIL + in_str + bcolors.ENDC
    return(in_str)

def clear_vt100_screen():
    subprocess.Popen( "cls" if platform.system() == "Windows" else "clear", shell=True)


def string_hour_min_to_tuple(instr):
    hour_str,min_str=instr.split(':')
    return int(hour_str),int(min_str)


def time_delta(start_time,end_time):
    (start_time_hour,start_time_min)=string_hour_min_to_tuple(start_time)
    (end_time_hour,end_time_min)=string_hour_min_to_tuple(end_time)

#    (start_time_hour,start_time_min)=(int(start_time_hour),int(start_time_min))
#    (end_time_hour,end_time_min)=(int(end_time_hour),int(end_time_min))

# e.g 00:08 < 23:16
    if (end_time_hour < start_time_hour):
       end_time_hour=end_time_hour+24
    delta=((end_time_hour*60)+end_time_min) - ((start_time_hour*60)+start_time_min)
    return(delta)


def parseBusStop(stopnum,busfilter_list=[],alarm_threshold=60):
    
    pageurl = 'http://www.dublinbus.ie/en/RTPI/Sources-of-Real-Time-Information/?searchtype=view&searchquery='+str(stopnum)

    htmltree = lxml.html.parse(pageurl)
    mylist = [ re.sub(pattern,'',listitem) for listitem in htmltree.xpath('/html/body//*/table[@id="rtpi-results"]/tr/td/text()') ]
    mylist = [ x for x in mylist if x != '']

    chunks=[mylist[x:x+3] for x in xrange(0,len(mylist),3)]

    time_now_str = datetime.now().strftime(scrapetimeformat)

    for chunkbit in chunks:
        if len(chunkbit) == 3:
            bus=chunkbit[0]   
            bus_time=chunkbit[2]
            if bus in busfilter_list or not (busfilter_list):
                if bus_time.lower() == 'due':
                   bus_time=time_now_str
#                   if int(bus_time.split(':')[0]) < int(time_now_str.split(':')[0]):
                bus_delta=time_delta(time_now_str,bus_time)
#                bus_delta=datetime.strptime(bus_time, scrapetimeformat) - datetime.strptime(time_now_str,scrapetimeformat)
                print bus + "\t" + bus_time + "\t" + print_coloured_time_remaining(str(bus_delta),alarm_threshold,bus_delta)
        else:
            print("Chunkbits =",len(chunkbit))

def sanitise_buslist(instr):
    valid_chars=",%s%s" % (string.ascii_letters, string.digits)
    outstr=''.join(c for c in instr if c in valid_chars)
    return outstr


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
    if args.alarm:
      alarm_threshold=int(args.alarm[0])
    return (int(args.stopnum[0]),bus_list,alarm_threshold)
    


if __name__ == '__main__':
    myStopNum=parseProgramArgs()
    while True:
        clear_vt100_screen()
        parseBusStop(myStopNum[0],myStopNum[1],myStopNum[2])
        time.sleep(10)
    
    
    
