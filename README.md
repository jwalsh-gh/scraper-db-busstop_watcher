# scraper-db-busstop_watcher
A very simple python program to scrape the Dublin Bus website 
real-time information to extract just the relevent text showing available buses and times.

The current implementation allow the user to periodically display selected buses at a given bus-stop.
An optional alarm threshold allows the user to highlight the arrival of a bus within a given number of minutes. 

e.g.
python watch_DB_bus.py  --stopnum=495  --busfilter=7,66,757 --alarm=10


The ultimte aim is to develop a framework that will allow the user to chain a combination of 
buses and bus stops, and then present those available options.
For example, rather than waiting 40 minutes for bus X, the user might be able to take buses {A..M,X} to a certain point 
in the route, do something productive other than waiting around (e.g daily shopping), and then take the 
later bus X. Another scenario may be that taking an alternative route allows you to connect to another service serving the same location -- waiting on a direct bus may take longer than using a non-direct + an alternative direct combination of buses.
