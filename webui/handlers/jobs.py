from handlers.base import BaseHandler

import tornado.web
from tornado import gen
import simplejson as json
import datetime
import urllib

import logging
logger = logging.getLogger('theq2.' + __name__)

statuses = { 1: "running",
             2: "error",
             3: "completed" }
priorities = { None: 'Normal',
               -600: 'Whenever',
               -300: 'Low',
               0: 'Normal',
               300: 'High',
               600: 'Highest'}

class MainJobTable(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        sortby = self.get_argument("sortby", "sgeid")
        sortdir = self.get_argument("sortdir", "ASC")
        username = self.get_argument("username", "")
        projname = self.get_argument("projname", "")
        done = self.get_argument("done", False)
        running = self.get_argument("running", False)
        error = self.get_argument("error", False)
        wait = self.get_argument("wait", False)
        limit = self.get_argument("limit", -1)
        offset = self.get_argument("offset", -1)
        namesearch = self.get_argument("namesearch", "")
        
        # Build the two SQL queries
        [jobQuery, countQuery] = self.buildMainJobsSQLQuery(sortby, sortdir,
                      username, projname, done, running, error, wait, limit,
                      offset, namesearch)
        
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
            # Get the data from the DB
            [sgeid, jobname, username, project, priority, submittime,
                starttime, endtime, firsttask, lasttask, chunk, status,
                submissionscript, donetasks, stdout, stderr] = record
                
            # Munge the date bits to make things easier for the client
            [submittimestr, submittimetitle, starttimestr, starttimetitle,
                starttimealt, endtimestr, endtimetitle, durationstr,
                realtimeupdate] = self.sortTimeStrings(submittime, starttime,
                                                       endtime, todayStr)
                                                       
            # Tidy up a couple of little bits to keep templating easy
            statusstr = statuses.get(status, "")
            priorstr = priorities.get(priority, "")
            percentdone = (float(donetasks) / 
                           (float(lasttask) - float(firsttask) + 1.0)) * 100.0
            pcdone = "%3.0f" % percentdone
            if status == 3:
                notdone = False
            else:
                notdone = True
            
            outputPath = ""
            if donetasks > 0 and status != 2:
                outPathQ = "SELECT value FROM job_extras WHERE sgeid="
                outPathQ += str(sgeid) + " AND key = 'output_path';"
                
                outPathCursor = yield gen.Task(self.db.execute, outPathQ)
                
                for outPathRecord in outPathCursor:
                        [tempStr] = outPathRecord
                        outputPath = urllib.quote(tempStr)
            
            # Now put it all into a JSON serializable list
            toAppend = {"sgeid": sgeid, "jobname": jobname,
                "username": username, "project": project, "priority": priorstr,
                "submittimestr": submittimestr, "starttimestr": starttimestr,
                "endtimestr": endtimestr, "submittimetitle": submittimetitle,
                "starttimetitle": starttimetitle, "endtimetitle": endtimetitle,
                "starttimealt": starttimealt, "durationstr": durationstr,
                "realtimeupdate": realtimeupdate, "firsttask": firsttask,
                "lasttask": lasttask, "chunk": chunk, "status": statusstr,
                "submissionscript": submissionscript, "donetasks": donetasks,
                "pcdone": pcdone, "notdone": notdone, "output_path": outputPath}
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
    def sortTimeStrings(self, submittime, starttime, endtime, todayStr):
        # Sort of submit time
        oldDate = ""
        newDate = ":%S"
        if todayStr != submittime.strftime("%d %b"):
            oldDate = "%d %b "
            newDate = ""
        submittimestr = submittime.strftime(oldDate + "%H:%M" + newDate)
        submittimetitle = submittime.strftime("%d %b %H:%M:%S")
        # Sort out start time
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
        # Sort out end time
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
        return [submittimestr, submittimetitle, starttimestr, starttimetitle,
                starttimealt, endtimestr, endtimetitle, durationstr,
                realtimeupdate]
    
    #
    # This function's pretty horrible, but it's ultimately just an SQL
    # query builder that takes the various GET arguments and builds two queries
    #
    def buildMainJobsSQLQuery(self, sortby, sortdir, username, projname, done,
                      running, error, wait, limit, offset, namesearch):
        gotawherealready=False
        gotastatusalready=False
        psqlcommand = ""
        if username != "":
            psqlcommand += "WHERE username='" + username + "' "
            gotawherealready = True
        if projname != "":
            if gotawherealready:
                psqlcommand += "AND project='" + projname + "' "
            else:
                psqlcommand += "WHERE project='" + projname + "' "
            gotawherealready = True
        if namesearch != "":
            if gotawherealready:
                psqlcommand += "AND jobname LIKE '%" + namesearch + "%' "
            else:
                psqlcommand += "WHERE jobname LIKE '%" + namesearch + "%' "
            gotawherealready = True
        if done:
            if gotawherealready:
                psqlcommand += "AND (status=3 "
            else:
                psqlcommand += "WHERE (status=3"
            gotawherealready = True
            gotastatusalready = True
        if running:
            if gotastatusalready:
                psqlcommand += "OR status=1 "
            else:
                if gotawherealready:
                    psqlcommand += "AND (status=1 "
                else:
                    psqlcommand += "WHERE (status=1"
            gotawherealready = True
            gotastatusalready = True
        if wait:
            if gotastatusalready:
                psqlcommand += "OR status=0 "
            else:
                if gotawherealready:
                    psqlcommand += "AND (status=0 "
                else:
                    psqlcommand += "WHERE (status=0"
            gotawherealready = True
            gotastatusalready = True
        if error:
            if gotastatusalready:
                psqlcommand += "OR status=2 "
            else:
                if gotawherealready:
                    psqlcommand += "AND (status=2 "
                else:
                    psqlcommand += "WHERE (status=2 "
            gotawherealready = True
            gotastatusalready = True
        if gotastatusalready:
            psqlcommand += ") "
        psqlcommand_end = "ORDER BY " + sortby + " " + sortdir + " "
        if limit != -1:
            psqlcommand_end += "LIMIT " + limit + " "
            if offset != -1:
                psqlcommand_end += "OFFSET " + offset + " "
        jobQuery = "SELECT * FROM jobs " + psqlcommand + psqlcommand_end + ";"
        countQuery = "SELECT count(*) FROM jobs " + psqlcommand + ";"
        
        return [jobQuery, countQuery]
