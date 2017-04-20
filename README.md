# Notif-Piazza
A Piazza Notification Tool for Relevant Topics based on <a href="https://github.com/hfaran/piazza-api">Unofficial Client for Piazza's Internal API.</a> Ideally it should be run as a cron job on a server.

<h2>Files</h2>

  project.py: the main program.<br />
  prepare.txt: the first line is a comma-separated string that represent the topics
          that the user would like to be <br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;notified about; the second line is the id of the course; the third line is the id of the latest post that the <br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;program has checked, so that in subsequent iterations the program will only look at later posts. <br/>
  log.txt: log file. 


<h2>Installation & Usage</h2>
<pre>
  <code>$ git clone https://github.com/daocunyang/Notif-Piazza.git</code>
  <code>$ cd Notif-Piazza</code>
  <code>$ pip install piazza-api</code>
  <code>$ python project.py</code>
</pre>
