var refreshTimeout;
var refreshInterval = 5000;
var realTimeInverval;
var sortJobsBy = "sgeid";
var sortJobsDir = "DESC";
var sortJobBy = "taskno";
var sortJobDir = "ASC";
var jobsFilters = "";
var workerFilters = "";
var usernameVal = "";
var refreshIcons = ["ui-icon-arrowrefresh-1-n",	"ui-icon-arrowrefresh-1-e",
	"ui-icon-arrowrefresh-1-s", "ui-icon-arrowrefresh-1-w"];
var whichRefreshIcon = 1;
var removeOldOnly = true;
var autoRefresh = true;
var perPageVal = 25;
var pageNumber = 1;
var howManyPages = 1;
var whichTaskLookingAt = 0;
var defaultTasksPerPage = 50;
var tPageNumber = new Array();
var howManyTPages = new Array();
var tasksPerPageVal = new Array();
var defaultQ = "farm.q";
var whichQ = defaultQ;
var queueData;
var queueChart;
var jobsPageGuage;
var queueOptions;

// Allows you to call jobsTable cgi script
function getJobs(params) {
	var ampersand = ""
	if (jobsFilters != "") { ampersand = "&"; }
	var AJAXparams = jobsFilters + ampersand + "sortby=" + sortJobsBy +
		"&sortdir=" + sortJobsDir + "&limit=" + perPageVal.toString() +
		"&offset=" + ((pageNumber - 1) * perPageVal).toString() + params;

	$.getJSON("/jobs", AJAXparams, function(data) {
		//
		// This bit fills in the table rows
		//
		var theHTML = Mustache.to_html(mainJobTableRowTemplate, data);
		$("#jobsTable tbody").html("");
		$("#jobsTable tbody").append(theHTML);
		
		//
		// This bit now does the pagination
		//
		lineCount = data.totalJobCount;
		howManyPages = Math.ceil(lineCount / perPageVal);
		// If there are no results, say there's one page
		if (howManyPages == 0) { howManyPages = 1; }
		// If jobs have cleared and you're on a page that no
		// longer exists, go to the maximum page number and
		// refresh
		if (pageNumber > howManyPages) {
			pageNumber = howManyPages;
			refreshPage();
		} else {
			$("#pageno").html(pageNumber.toString()
				+ "/" + howManyPages.toString());
			// and finally set up the duration counters
			if (realTimeInverval == null) {
				realTimeInverval = setInterval(
					'updateDurations()', 1000);
			}
		}
	});
	
	if( queueData ) {
		$.getJSON("/queueStats", workerFilters, function(data) {			
			// Update the guage
			queueData.setValue(0, 0, whichQ);
			queueData.setValue(0, 1, Math.floor(data.usedpc));
			jobsPageGuage.draw(queueData, queueOptions);
		});
	}
}

// Gets the workers table
function getWorkers(params) {
	var AJAXParams = workerFilters + params;
	
	$.getJSON("/queueStats", workerFilters, function(data) {
		// Write out the text
		var theHTML = Mustache.to_html(farmDivisionTemplate, data);
		$("#queuestattext").html("");
		$("#queuestattext").append(theHTML);
		
		// Update the guage
		queueData.setValue(0, 0, whichQ);
		queueData.setValue(0, 1, Math.floor(data.usedpc));
		queueChart.draw(queueData, queueOptions);
	});
	
	$.getJSON("/workers", AJAXParams, function(data) {
		var theHTML = Mustache.to_html(workerTableRowTemplate, data);
		$("#workersTable tbody").html("");
		$("#workersTable tbody").append(theHTML);
	});

	$.getJSON("/quotas", AJAXParams, function(data) {
		var theHTML = Mustache.to_html(userQuotaRowTemplate, data);
		$("#quotastats tbody").html("");
		$("#quotastats tbody").append(theHTML);
	});
	$.getJSON("/resources", AJAXParams, function(data) {
		var theHTML = Mustache.to_html(resourceRowTemplate, data);
		$("#resourcestats tbody").html("");
		$("#resourcestats tbody").append(theHTML);
	});
}

// Allows you to call jobTable cgi script
function getJob(params, whichJob) {
	var AJAXparams = "sortby=" + sortJobBy + "&sortdir=" + sortJobDir;
	AJAXparams += "&jobno=" + whichJob + "&limit=" + 
		tasksPerPageVal[whichTaskLookingAt].toString() +
		"&offset=" + ((tPageNumber[whichTaskLookingAt] - 1) *
		tasksPerPageVal[whichTaskLookingAt]).toString() + params;
	
	$.getJSON("/oneJob", AJAXparams, function(data) {
		//
		// This bit fills in the table rows
		//
		var theHTML = Mustache.to_html(oneJobRowTemplate, data);
		$("#"+whichJob+"tab .jobTable tbody").html("");
		$("#"+whichJob+"tab .jobTable tbody").append(theHTML);
		
		//
		// This bit now does the pagination
		//
		lineCount = data.totalJobCount;
		howManyTPages[whichTaskLookingAt] = Math.ceil(lineCount /
				tasksPerPageVal[whichTaskLookingAt]);
		// If there are no results, say there's one page
		if (howManyTPages[whichTaskLookingAt] == 0) {
			howManyTPages[whichTaskLookingAt] = 1
		}
		// Otherwise, write in page/total
		$("#" + whichJob + "tpageno").html(
				tPageNumber[whichTaskLookingAt].toString() + "/"
				+ howManyTPages[whichTaskLookingAt].toString());
	});
}

// Refresh the jobsTable
function refreshPage() {
	//alert("Refresh run by " + arguments.callee.caller.toString());
	// Figure out which tab is visible and only refresh that one
	if ($("#jobsTable").is(":visible")) { getJobs(""); }
	if ($("#workersTable").is(":visible")) { getWorkers(""); }
	else if ($(".jobTable").is(":visible")) {
		var tempID = $(".jobTable:visible").attr("id");
		var tempSplit = tempID.split("Table");
		
		var newTaskNo = tempSplit[0];
		if (newTaskNo != whichTaskLookingAt) {
			whichTaskLookingAt = newTaskNo;
		}
		
		getJob("", whichTaskLookingAt);
	}
	lastUpdated();

	if (autoRefresh == true) {
		whichRefreshIcon += 1;
		if (whichRefreshIcon > 3) { whichRefreshIcon = 0; }
		$("#autorefresh").button("option",
			"icons",
			{ primary: refreshIcons[whichRefreshIcon] });

		clearTimeout(refreshTimeout);
		refreshTimeout = setTimeout(function() {
					refreshPage();
				}, refreshInterval);
	}
}

// Refresh the last updated bit top-right
function lastUpdated() {
	rightNow = new Date();
	hours = '' + rightNow.getHours();	// Use "'' +" to make string
	minutes = '' + rightNow.getMinutes();
	seconds = '' + rightNow.getSeconds();

	if (hours.length == 1) { hours = '0' + hours }
	if (minutes.length == 1) { minutes = '0' + minutes }
	if (seconds.length == 1) { seconds = '0' + seconds }

	timeString = hours + ":" + minutes + ":" + seconds;
	$("#lastupdate").html("Last Updated: " + timeString);
}

function showInfoDialog(theTitle, theContent, theWidth, theHeight) {
	if ( theWidth === undefined ) { theWidth = 300; }
	if ( theHeight === undefined ) { theHeight = "auto"; }
	$("#multiusedialog")
	.html(theContent)
	.dialog({
		width : theWidth,
		height : theHeight,
		title : theTitle,
		buttons : {
			"OK" : function() {
				$(this).dialog("close");
			}
		}
	});
	$("#multiusedialog").dialog("open");
}

// Show stdout/stderr for a task
function taskInfo(jobNo, taskNo) {
	var AJAXParams = "sgeid=" + jobNo + "&frame=" + taskNo;
	
	$.getJSON("/readLog", AJAXParams, function(data) {
		var theHTML = Mustache.to_html(logTemplate, data);
		showInfoDialog("Logs", theHTML, 1000, 500);
	});
}

// Retry a job
function retry(e, jobNo) {
	// Stop the opening of the job tab
	e.stopPropagation();
	e.preventDefault();

	$("#multiusedialog")
	.html("Want to retry job " + jobNo.toString() + "?")
	.dialog({
		width : 300,
		height : 200,
		title : "Confirmation Required",
		buttons : {
			"Confirm" : function() {
				$(this).dialog("close");
				
				var AJAXParams = "sgeid=" + jobNo;
				
				$.getJSON("/retry", AJAXParams, function(data) {
					refreshPage();
					toast("Success", "Retrying " + data.sgeid);
				});
			},
			"Cancel" : function() {
				$(this).dialog("close");
			}
		}
	});
	$("#multiusedialog").dialog("open");
}

// Reschedule a task
function reschedule(e, jobNo) {
	// Stop the opening of the job tab
	e.stopPropagation();
	e.preventDefault();

	$("#multiusedialog")
	.html("Sure you want to kill and retry job " + jobNo.toString() + "?")
	.dialog({
		width : 300,
		height : 200,
		title : "Confirmation Required",
		buttons : {
			"Confirm" : function() {
				$(this).dialog("close");
				
				var AJAXParams = "sgeid=" + jobNo;
				
				$.getJSON("/reschedule", AJAXParams, function(data) {
					refreshPage();
					toast("Success", "Rescheduled task " + jobNo);
				});
			},
			"Cancel" : function() {
				$(this).dialog("close");
			}
		}
	});
	$("#multiusedialog").dialog("open");
}

// Remove a single job from both the DB and the SGE queue
function deleteJob(e, jobNo) {
	// Stop the opening of the job tab
	e.stopPropagation();
	e.preventDefault();
	
	jobNo = jobNo.toString();

	$("#multiusedialog")
	.html("Are you sure?")
	.dialog({
		width : 300,
		height : 200,
		title : "Confirmation Required",
		buttons : {
			"Confirm" : function() {
				$(this).dialog("close");
				
				var AJAXParams = "sgeid=" + jobNo;
				
				$.getJSON("/deleteJob", AJAXParams, function(data) {
					refreshPage();
					
					var tabName = "#" + jobNo + "tab";
					if ($(tabName).length > 0) {
						$("#tabs").tabs("remove", tabName);
					}
					
					toast("Success", "Removed job " + jobNo);
				});
			},
			"Cancel" : function() {
				$(this).dialog("close");
			}
		}
	});
	$("#multiusedialog").dialog("open");
}

// Remove a single job from both the DB and the SGE queue
function changePriority(e, jobNo) {
	// Stop the opening of the job tab
	e.stopPropagation();
	e.preventDefault();

	var priorityHTML = "Please select priority level<br /><br />Be aware that"
	priorityHTML += " if this system is abused, it'll be taken away and only"
	priorityHTML += " producers will be able to use this - so <span class=\""
	priorityHTML += "red\">DON'T</span>!"

	$("#multiusedialog")
	.html(priorityHTML)
	.dialog({
		width : 350,
		height : 200,
		title : "Change Priority",
		buttons : {
			"Whenever" : function() {
				changePriorityCallback(jobNo, -600);
				$("#multiusedialog").dialog("close");
			},
			"Low" : function() {
				changePriorityCallback(jobNo, -300);
				$("#multiusedialog").dialog("close");
			},
			"Normal" : function() {
				changePriorityCallback(jobNo, 0);
				$("#multiusedialog").dialog("close");
			},
			"High" : function() {
				changePriorityCallback(jobNo, 300);
				$("#multiusedialog").dialog("close");
			},
			"Highest" : function() {
				changePriorityCallback(jobNo, 600);
				$("#multiusedialog").dialog("close");
			},
		},
		open: function() {
			// This just stops the 'Whenever' button from being highlighted
			$(this).parents('.ui-dialog-buttonpane button:eq(0)').blur();
		}
	});
	$("#multiusedialog").dialog("open");
}

function changePriorityCallback(jobNo, priority) {
	AJAXParams = "sgeid=" + jobNo + "&priority=" + priority;
	
	$.getJSON("/changePriority", AJAXParams, function(data) {
		refreshPage();
		toast("Success", "Changed priority of job " + jobNo);
	});
}

// Remove all errored jobs.  They do need to be removed from queue
function removeErrors() {
	if (usernameVal == "") {
		$("#multiusedialog")
		.html("You need to have a username in the filter box on the left")
		.dialog({
			width : 300,
			height : 200,
			title : "Whoops",
			buttons : {
				"OK" : function() {
					$(this).dialog("close");
				}
			}
		});
	} else {
		$("#multiusedialog")
		.html("Are you sure?")
		.dialog({
			width : 300,
			height : 200,
			title : "Confirmation Required",
			buttons : {
				"Confirm" : function() {
					$(this).dialog("close");
					
					var AJAXparams = "user=" + usernameVal;

					$.getJSON("/deleteErrors", AJAXparams, function(data) {
						refreshPage();
						toast("Success", "Deleted all errored jobs");
					});
				},
				"Cancel" : function() {
					$(this).dialog("close");
				}
			}
		});
	}
	$("#multiusedialog").dialog("open");
}

// Remove all completed jobs.  Don't need to remove from queue because they
// already have been since they're done
function removeComplete() {
	if (usernameVal == "") {
		$("#multiusedialog")
		.html("You need to have a username in the filter box on the left")
		.dialog({
			width : 300,
			height : 200,
			title : "Whoops",
			buttons : {
				"OK" : function() {
					$(this).dialog("close");
				}
			}
		});
	} else {
		$("#multiusedialog")
		.html("Are you sure?")
		.dialog({
			width : 300,
			height : 200,
			title : "Confirmation Required",
			buttons : {
				"Confirm" : function() {
					$(this).dialog("close");
					
					var AJAXparams = "user=" + usernameVal;
					if (removeOldOnly) {
						AJAXparams = AJAXparams + "&old=true";
					}

					$.getJSON("/deleteComplete", AJAXparams, function(data) {
						refreshPage();
						if (removeOldOnly) {
							toast("Success", "Removed old jobs");
						} else {
							toast("Success", "Removed all complete jobs");
						}
					});
				},
				"Cancel" : function() {
					$(this).dialog("close");
				}
			}
		});
	}
	$("#multiusedialog").dialog("open");
}

// Show help dialog
function showHelpDialog() {
	$("#helpdialog").dialog({
		buttons : {
			"OK" : function() {
				$(this).dialog("close");
			}
		}
	});

	$("#helpdialog").dialog("open");
}

function setupToolbars() {
	setupTopToolbar();
	setupJobsToolbar();
	setupWorkersToolbar();
}

function setupTopToolbar() {
	$("#autorefresh").button({
		text: false,
		icons: { primary: "ui-icon-locked" }
	});
	$("#manualRefresh").button({
		text: false,
		icons: { primary: "ui-icon-refresh" }
	}).click(function() { refreshPage(); });
}

function setupJobsToolbar() {
	$("#removeAllComplete").button({
		icons: { primary: "ui-icon-closethick" }
	}).click(function() { removeOldOnly = false; removeComplete(); });
	$("#removeOld").button({
		icons: { primary: "ui-icon-closethick" }
	}).click(function() { removeOldOnly = true; removeComplete(); });
	$("#removeErrors").button({
		icons: { primary: "ui-icon-closethick" }
	}).click(function() { removeOldOnly = false; removeErrors(); });
	$("#showLegend").button({
		icons: { primary: "ui-icon-info" }
	}).click(function() { showHelpDialog(); });
}

function setupWorkersToolbar(){
	$("#something").button({
		icons: { primary: "ui-icon-closethick" }
	}).click(function() { alert("Something"); });
}

function updateDurations() {
	var rightNow = new Date();
	theYear = rightNow.getFullYear();

	$(".rtupdate").each(function() {
		rowID = $(this).parent().attr("id");
		startTimeTD = $("#" + rowID + " td.starttime");
		startTime = startTimeTD.attr("title");
		startTimeMonth = startTimeTD.attr("alt");

		if (startTimeMonth != "") {
			tempArray1 = startTime.split(" ");
			tempArray2 = tempArray1[2].split(":");
			var startDate = new Date(theYear, startTimeMonth-1,
				tempArray1[0], tempArray2[0],
				tempArray2[1], tempArray2[2]);
			var delta = rightNow - startDate;

			delta = Math.floor(delta/1000);
			var hours=Math.floor(delta/3600);
			var minutes=Math.floor(delta/60)-(hours*60); 
			var seconds=delta-(hours*3600)-(minutes*60);

			if (hours > 0) {
				$(this).html(hours+"h "+minutes+"m "+seconds+"s");
			} else if (minutes > 0) {
				$(this).html(minutes+"m "+seconds+"s");
			} else {
				$(this).html(seconds+"s");
			}
		}
	});
}

// Add a job tab if it's not already there.
function addJobTab(jobNo) {
	var tabID = "#" + jobNo + "tab"

	if ($(tabID).length == 0) {
		$("#tabs").tabs("add", tabID, jobNo)

		var outerString = "<table class=\"containerTable\" cellpadding=\"0\" ";
		outerString += "cellspacing=\"0\"><tr><td class=\"leftContainer\">";
		outerString += "<div id=\"" + jobNo + "pagesBox\" class=\"leftBox\">";
		outerString += "<h2>Pages</h2>";
		outerString += "<div class=\"leftBoxInner\">";
		outerString += "Tasks per page<br />";
		outerString += "<div id=\"" + jobNo + "tasksperpage\" ";
		outerString += "class=\"tasksperpage\">";
		outerString += "<input type=\"radio\" id=\"" + jobNo + "tperpage1\" ";
		outerString += "name=\"" + jobNo + "tasksperpage\" checked=\"checked\"";
		outerString += "  /><label for=\"" + jobNo + "tperpage1\">50</label>";
		outerString += "<input type=\"radio\" id=\"" + jobNo + "tperpage2\" ";
		outerString += "name=\"" + jobNo + "tasksperpage\" /><label for=\"";
		outerString += jobNo + "tperpage2\">100</label>";
		outerString += "<input type=\"radio\" id=\"" + jobNo + "tperpage3\" ";
		outerString += "name=\"" + jobNo + "tasksperpage\" /><label for=\"";
		outerString += jobNo + "tperpage3\">400</label>";
		outerString += "</div>";
		outerString += "Navigation";
		outerString += "<div id=\"" + jobNo + "tpagebuttons\" "
		outerString += "class=\"tpagebuttons\">";
		outerString += "<button id=\"" + jobNo + "tprevpage\">Previous Page";
		outerString += "</button>";
		outerString += "<span id=\"" + jobNo + "tpageno\" class=\"tpageno\">";
		outerString += "1/1</span>";
		outerString += "<button id=\"" + jobNo + "tnextpage\">Next Page";
		outerString += "</button>";
		outerString += "</div>";
		outerString += "</div>";
		outerString += "</div>";
		outerString += "</td><td class=\"gutter\">&nbsp;";
		outerString += "</td><td class=\"rightContainer\">";
		// The taskbar.  I'll add this later.  One thing at a time...
		/*outerString += "<div id=\"tasksToolbar\" class=\"ui-widget-header ui-corner-all rightToolbar\">";
		outerString += "<button title=\"Retry Errors\" id=\"retryErrors\">Retry Errors</button>";
		outerString += "</div>";*/

		var tempString = "<table class=\"jobTable mainTable\" ";
		tempString +="id=\"" + jobNo + "Table\">";
		tempString +="<thead><tr><th class=\"narrow2\">Actions";
		tempString +="</th><th class=\"narrow1\">ID</th>";
		tempString +="<th class=\"normalwidth\">Start Time";
		tempString +="</th><th class=\"normalwidth\">End Time";
		tempString +="</th><th class=\"narrow2\">Duration</th>";
		tempString +="<th class=\"narrow2\">Return Code</th>";
		tempString +="<th class=\"narrow2\">Attempts</th>";
		tempString +="<th class=\"narrow2\">Exec Host</th>";
		tempString +="</tr></thead><tbody></tbody></table>";
		
		var endString = "</td></tr></table>";

		$("#" + jobNo + "tab").append(outerString + tempString + endString);
		tPageNumber[jobNo] = 1;
		howManyTPages[jobNo] = 1;
		tasksPerPageVal[jobNo] = defaultTasksPerPage;
		
		$("#" + jobNo + "tasksperpage").buttonset();
		$("#" + jobNo + "tperpage1").click( function() {changeTPageSize(50);});
		$("#" + jobNo + "tperpage2").click( function() {changeTPageSize(100);});
		$("#" + jobNo + "tperpage3").click( function() {changeTPageSize(400);});
		$("#" + jobNo + "tprevpage").button({
			icons: {
				primary:'ui-icon-circle-arrow-w'
			},
			text: false
		}).click( function() {
			tPageNumber[whichTaskLookingAt]--;
			if (tPageNumber[whichTaskLookingAt] < 1) {
				tPageNumber[whichTaskLookingAt] = 1;
			}
			refreshPage();
		});
		$("#" + jobNo + "tnextpage").button({
			icons: {
				primary:'ui-icon-circle-arrow-e'
			},
			text: false
		}).click( function() {
			tPageNumber[whichTaskLookingAt]++;
			if (tPageNumber[whichTaskLookingAt] >
					howManyTPages[whichTaskLookingAt]) {
				tPageNumber[whichTaskLookingAt] =
					howManyTPages[whichTaskLookingAt];
			}
			refreshPage();
		});
	}
	$("#tabs").tabs("select", tabID);

	getJob("", jobNo);
	return false;
}

// Apply the filters set in the left filter bar (Workers)
function refreshWorkerFilters() {
	workerFilters = "";
	var queueVal = $("#queuename").val();
	if (queueVal == "") {
		$("#queuename").val(defaultQ);
		queueVal = defaultQ;
	}
	whichQ = queueVal;
	workerFilters += "queue=" + queueVal;
	// Show/hide delete icons in text views depending on content
	$('span.deleteicon').each(function(index) {
			if ($(this).children("input").val() == "") {
				$(this).children("span").css("width", "0px");
			} else {
				$(this).children("span").css("width", "16px");
			}
		});
}


// Apply the filters set in the left filter bar (Jobs)
function refreshJobsFilters() {
	jobsFilters = "";
	usernameVal = $("#username").val();
	if (usernameVal != "") { jobsFilters += "username="+usernameVal; }
	var projnameVal = $("#projname").val();
	if (projnameVal != "") {
		var ampersand = "";
		if (jobsFilters != "") { ampersand="&"; }
		jobsFilters += ampersand + "projname=" + projnameVal;
	}
	var jobnameVal = $("#jobname").val();
	if (jobnameVal != "") {
		var ampersand = "";
		if (jobsFilters != "") { ampersand="&"; }
		jobsFilters += ampersand + "namesearch=" + jobnameVal;
	}
	if ($("#donestate").is(":checked")) {
		var ampersand = "";
		if (jobsFilters != "") { ampersand="&"; }
		jobsFilters += ampersand + "done=1";
	}
	if ($("#runningstate").is(":checked")) {
		var ampersand = "";
		if (jobsFilters != "") { ampersand="&"; }
		jobsFilters += ampersand + "running=1";
	}
	if ($("#waitstate").is(":checked")) {
		var ampersand = "";
		if (jobsFilters != "") { ampersand="&"; }
		jobsFilters += ampersand + "wait=1";
	}
	if ($("#errorstate").is(":checked")) {
		var ampersand = "";
		if (jobsFilters != "") { ampersand="&"; }
		jobsFilters += ampersand + "error=1";
	}
	// Show/hide delete icons in text views depending on content
	$('span.deleteicon').each(function(index) {
			if ($(this).children("input").val() == "") {
				$(this).children("span").css("width", "0px");
			} else {
				$(this).children("span").css("width", "16px");
			}
		});
	pageNumber = 1;
}

// Set up all the filter functions for the left filter bar
function setupFilterFunctions() {
	$("#jobsFilters input").blur(function() {
		refreshJobsFilters();
		refreshPage();
	});
	$("#jobsFilters input").bind('keyup', function (e) {
		var key = e.keyCode || e.which;
		if (key === 13) {
			refreshJobsFilters();
			refreshPage();
		}
	});
	$("#workerFilters input").blur(function() {
		refreshWorkerFilters();
		refreshPage();
	});
	$("#workerFilters input").bind('keyup', function (e) {
		var key = e.keyCode || e.which;
		if (key === 13) {
			refreshWorkerFilters();
			refreshPage();
		}
	});
	$("#waitstate").button({ icons: {primary:'ui-icon-clock'}, text: false });
	$("#donestate").button({ icons: {primary:'ui-icon-check'}, text: false });
	$("#runningstate").button({ icons: {primary:'ui-icon-gear'}, text: false });
	$("#errorstate").button({ icons: {primary:'ui-icon-alert'}, text: false });
	$("#stateboxes input").click(function() {
		refreshJobsFilters();
		refreshPage();
	});
	$('input.deletable').wrap('<span class="deleteicon" />')
		.after($('<span />'));
	$("span.deleteicon").children("span").click(function() {
			$(this).prev("input").val("").focus();
			refreshJobsFilters();
			refreshWorkerFilters();
			refreshPage();
		});
}

function changePageSize(value) {
	perPageVal = value;
	pageNumber = 1;
	refreshPage();
}

function changeTPageSize(value) {
	tasksPerPageVal[whichTaskLookingAt] = value;
	tPageNumber[whichTaskLookingAt] = 1;
	refreshPage();
}

// Set up the pagination bits on the left side
function setupPagination() {
	$("#rowsperpage").buttonset();
	$("#perpage1").click( function() { changePageSize(25); });
	$("#perpage2").click( function() { changePageSize(100); });
	$("#perpage3").click( function() { changePageSize(400); });
	$("#prevpage").button({
		icons: {
			primary:'ui-icon-circle-arrow-w'
		},
		text: false
	}).click( function() {
		pageNumber--;
		if (pageNumber < 1) { pageNumber = 1; }
		refreshPage();
	});
	$("#nextpage").button({
		icons: {
			primary:'ui-icon-circle-arrow-e'
		},
		text: false
	}).click( function() {
		pageNumber++;
		if (pageNumber > howManyPages) { pageNumber = howManyPages; }
		refreshPage();
	});
}

// Set up autorefresh code
function setupAutoRefresh() {
	// Setup all the autoRefresh bits
	if ($.cookie("doNOTautoRefresh")) {
		$("#autorefresh").button("option",
                                "icons",
                                { primary: "ui-icon-locked" });
		autoRefresh = false;
	} else {
		$("#autorefresh").attr("checked", true);
		refreshTimeout = setTimeout(function() {
						refreshPage()
					}, refreshInterval);
		autoRefresh = true;
	}
	$("#autorefresh").change( function() {
		if( $("#autorefresh").is(":checked") ) {
			$.cookie("doNOTautoRefresh", null);
			autoRefresh = true;
			refreshPage();
		} else {
			$.cookie("doNOTautoRefresh", true, { expires: 30 });
			clearTimeout(refreshTimeout);
			$("#autorefresh").button("option",
				"icons",
				{ primary: "ui-icon-locked" });
			autoRefresh = false;
		}
	});
}

// Setup the toast style notifications
function setupNotifications() {
	$("#notifications").notify();
}

// The actual toast function
function toast(theTitle, theContent) {
	$("#notifications").notify("create", {
		title: theTitle,
		text: theContent
	});
}

// Set up the chart data for the farm gauge
function setupChartData() {
	queueData = new google.visualization.DataTable();
	queueData.addColumn('string', 'Label');
	queueData.addColumn('number', 'Value');
	queueData.addRows(1);
	queueData.setValue(0, 0, defaultQ);
	queueData.setValue(0, 1, 0);
	
	queueChart = new google.visualization.Gauge(
		document.getElementById('queueguage'));
	jobsPageGuage = new google.visualization.Gauge(
		document.getElementById('jobsPageGuage'));
	queueOptions = {width:120, height:120, redFrom:90, redTo:100,
		yellowFrom:75, yellowTo:90, minorTicks:5};
}

// jQuery setup thingy
$(function() {
	// Set up the tabs
	$("#tabs").tabs({closable: true,
			remove: function(event, ui) {
				$("#tabs").tabs("select", "#jobstab");
			}});
	// and the modal dialogs
	$("#multiusedialog").dialog({ autoOpen: false, modal: true });
	$("#helpdialog").dialog({ autoOpen: false, modal: true });
	setupNotifications();
	setupAutoRefresh();
	setupToolbars();
	setupFilterFunctions();
	setupPagination();

	// Now populate the jobsTable and set the event handler
	$('#tabs').bind('tabsshow', function(event, ui) { refreshPage(); })

	// On opening, REMOTE_USER might be set by Apache/Kerberos/whatever and
	// index.html is set to fill in the user filter with it, so run
	// refreshJobsFilters to initially populate the jobs table
	refreshJobsFilters();
	refreshWorkerFilters();
	refreshPage();

	lastUpdated();
});
