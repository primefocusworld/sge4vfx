from handlers.base import BaseHandler

import tornado.web
from tornado import gen
import simplejson as json
import datetime
import urllib
import re

import logging
logger = logging.getLogger('theq2.' + __name__)

class OneJobTable(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        sortBy = self.get_argument("sortby", "sgeid")
        sortDir = self.get_argument("sortdir", "ASC")
        jobNo = self.get_argument("jobno")
        limit = self.get_argument("limit", -1)
        offset = self.get_argument("offset", -1)
        
        # Build the two SQL queries
        [jobQuery, countQuery] = self.buildSQLQuery(sortBy, sortDir,
                                                    jobNo, limit, offset)
        
        # ASync run the two queries and yield while doing it
        jobCursor, countCursor = yield [
            gen.Task(self.db.execute, jobQuery),
            gen.Task(self.db.execute, countQuery)
        ]
        
        # Work out today's date
        today = datetime.date.today()
        todayStr = today.strftime("%d %b")
        
        # Blank the table row
        tableContents = []
        
        # Now for every row in the returned jobTable cursor
        for record in jobCursor:
            [sgeid, taskno, starttime, endtime, attempts,
             returncode, rhost] = record
            sgeid = str(sgeid)
            taskno = str(taskno)
            returncode = str(returncode)
            rhost = str(rhost)
            attempts = str(attempts)
            
            # Sort time the time bits
            [starttimestr, starttimetitle, starttimealt, endtimestr,
             endtimetitle, durationstr,
             realtimeupdate] = self.sortTimeStrings(starttime,
                                                    endtime, todayStr)
            
            # Fill in job status based on start and endtime for now
            status=""
            if ((returncode != "None") and (returncode != "0")):
                status="error"
            elif (returncode == "-1"):
                status="other"
            elif ((starttime is not None) and (endtime is None)):
                status="running"
            elif ((starttime is not None) and (endtime is not None)):
                status="completed"
            
            outputPath = ""
            if endtime is not None and returncode == "0":
                outPathQ = "SELECT value FROM job_extras WHERE sgeid="
                outPathQ += sgeid + " AND key = 'output_path';"
                
                outPathCursor = yield gen.Task(self.db.execute, outPathQ)
                
                for outPathRecord in outPathCursor:
                        [tempStr] = outPathRecord
                        # Replace the padding with the task number
                        tempStr = re.sub("\.(#+)\.",
                                lambda x:".%s."%str(taskno).zfill(
                                        len(x.groups()[0])), tempStr)
                        outputPath = urllib.quote(tempStr)
            
            errorRetryIcon = False
            if returncode != "0" and returncode != "None":
                errorRetryIcon = True
            rescheduleIcon = False
            if returncode == "None" and starttime is not None:
                rescheduleIcon = True
            
            # Now put it all into a JSON serializable list
            toAppend = {"sgeid": sgeid, "taskno": taskno,
                        "output_path": outputPath, "returncode": returncode,
                        "starttimestr": starttimestr,
                        "starttimetitle": starttimetitle,
                        "starttimealt": starttimealt,
                        "endtimestr": endtimestr, "endtimetitle": endtimetitle,
                        "durationstr": durationstr, "status": status,
                        "realtimeupdate": realtimeupdate, "attempts": attempts,
                        "errorRetryIcon": errorRetryIcon,
                        "rescheduleIcon": rescheduleIcon, "rhost": rhost}
            # and append it to the current big fat object
            tableContents.append(toAppend)
        
        # This bit puts a hidden row on the bottom that has the total number
        # of rows.  It's a bit of a hack but means only doing the large SQL
        # query assembly once and saves on another AJAX call
        for record in countCursor:
            [count] = record
        
        # Put the two bits together
        recordsAsDict = {"rows": tableContents, "totalJobCount": count}
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
        
        # Send it back to the browser as JSON
        self.write(json.dumps(recordsAsDict, default=dthandler))
        self.finish()
                
    
    #
    # Sort out the time strings
    #
    def sortTimeStrings(self, starttime, endtime, todayStr):
        if starttime is not None:
            oldDate = ""
            newDate = ":%S"
            if todayStr != starttime.strftime("%d %b"):
                oldDate = "%d %b "
                newDate = ""
            starttimestr = starttime.strftime(oldDate + "%H:%M" + newDate)
            starttimetitle = starttime.strftime("%d %b %H:%M:%S")
            starttimealt = starttime.strftime("%m")
        else:
            starttimestr = "-"
            starttimetitle = ""
            starttimealt = ""
            realtimeupdate = False
        if endtime is not None and starttime is not None:
            oldDate = ""
            newDate = ":%S"
            if todayStr != endtime.strftime("%d %b"):
                oldDate = "%d %b "
                newDate = ""
            endtimestr = endtime.strftime(oldDate + "%H:%M" + newDate)
            endtimetitle = endtime.strftime("%d %b %H:%M:%S")
            duration = endtime - starttime
            s = duration.seconds + (duration.days * 86400)
            hours, remainder = divmod(s, 3600)
            minutes, seconds = divmod(remainder, 60)
            if (hours > 0):
                durationstr = '%sh %sm %ss' % (hours, minutes, seconds)
            elif (minutes > 0):
                durationstr = '%sm %ss' % (minutes, seconds)
            else:
                durationstr = '%ss' % (seconds)
            realtimeupdate = False
        else:
            endtimestr = "-"
            endtimetitle = ""
            durationstr = "-"
            realtimeupdate = True
        return [starttimestr, starttimetitle, starttimealt, endtimestr,
                endtimetitle, durationstr, realtimeupdate]
            
    #
    # This builds the SQL queries that return both the task list
    # and the count for the number of tasks
    #
    def buildSQLQuery(self, sortBy, sortDir, jobNo, limit, offset):
        jobQuery = "SELECT * FROM tasks WHERE sgeid=" + jobNo
        countQuery = "SELECT count(*) FROM tasks WHERE sgeid=" + jobNo + ";"
        sqlQueryEnd = " ORDER BY " + sortBy + " " + sortDir + " "
        
        if limit != -1:
            sqlQueryEnd += "LIMIT " + limit + " "
            if offset != -1:
                sqlQueryEnd += "OFFSET " + offset + " "
        
        jobQuery += sqlQueryEnd + ";"
        
        return [jobQuery, countQuery]