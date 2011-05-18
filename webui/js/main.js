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
var removeOldOnly = 1;
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
var queueOptions;

// Allows you to call jobsTable cgi script
function getJobs(params) {
	var ampersand = ""
	if (jobsFilters != "") { ampersand = "&"; }
	var AJAXparams = jobsFilters + ampersand + "sortby=" + sortJobsBy +
		"&sortdir=" + sortJobsDir + "&limit=" + perPageVal.toString() +
		"&offset=" + ((pageNumber - 1) * perPageVal).toString() + params;

	// First find out how many pages there are and which one we're on
	$.ajax({
		url: "cgi/count.cgi",
		data: AJAXparams,
		dataType: "json",
		success: function(countData) {
			howManyPages = Math.ceil(countData.count / perPageVal);
			$("#pageno").html(pageNumber.toString() 
					+ "/" + howManyPages.toString());

			// Now get the actual job table data
			$.ajax({
				url: "cgi/jobs.cgi",
				data: AJAXparams,
				type: "GET",
				success: function(data) {
					$("#jobsTable tbody").html(data);
					if (realTimeInverval == null) {
						realTimeInverval = setInterval(
							'updateDurations()', 1000);
					}
				}
			});	
		}
	});
}

// Gets the workers table
function getWorkers(params) {
	var AJAXParams = workerFilters + params;
	
	$.ajax({
		url: "cgi/queueStats.cgi",
		data: AJAXParams,
		type: "GET",
		success: function(data) {
			// Write out the text
			var tempstring = "Total Slots: " + data.total;
			tempstring += "<br /><br />";
			tempstring += "<span class=\"red\">Broken Slots: ";
			tempstring += data.broken + " (" + data.brokenpc + "%)";
			tempstring += "</span><br />";
			tempstring += "<span class=\"green\">Good Slots: ";
			tempstring += data.good + " (" + data.goodpc + "%)";
			tempstring += "</span><br /><br />";
			tempstring += "Used Slots: " + data.used + " (";
			tempstring += data.usedpc + "%)<br />";
			tempstring += "Available Slots: " + data.avail + " (";
			tempstring += data.availpc + "%)<br />";
			$("#queuestattext").html(tempstring);
			
			// Update the guage
			queueData.setValue(0, 0, whichQ);
			queueData.setValue(0, 1, Math.floor(data.usedpc));
			queueChart.draw(queueData, queueOptions);
		}
	});
	
	$.ajax({
		url: "cgi/workers.cgi",
		data: AJAXParams,
		type: "GET",
		success: function(data) {
			$("#workersTable tbody").html(data);
		}
	});
}

// Allows you to call jobTable cgi script
function getJob(params, whichJob) {
	var AJAXparams = "sortby=" + sortJobBy + "&sortdir=" + sortJobDir;
	AJAXparams += "&jobno=" + whichJob + "&limit=" + 
		tasksPerPageVal[whichTaskLookingAt].toString() +
		"&offset=" + ((tPageNumber[whichTaskLookingAt] - 1) *
		tasksPerPageVal[whichTaskLookingAt]).toString() + params;

	// First find out how many pages there are and which one we're on
	$.ajax({
		url: "cgi/countTasks.cgi",
		data: AJAXparams,
		dataType: "json",
		success: function(countData) {
			howManyTPages[whichTaskLookingAt] = Math.ceil(countData.count /
				tasksPerPageVal[whichTaskLookingAt]);
			$("#" + whichJob + "tpageno").html(
					tPageNumber[whichTaskLookingAt].toString() 
					+ "/" + howManyTPages[whichTaskLookingAt].toString());

			$.ajax({
				url: "cgi/oneJob.cgi",
				data: AJAXparams,
				success: function(data) {
					$("#"+whichJob+"tab .jobTable tbody").html(data);
				}
			});
		}
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

function showJobInfo(data, jobNo) {
	tempstring = "<ul>";
	tempstring += "<li>Scriptfile: " + data.scriptFile + "</li>";
	tempstring += "<li>StdOut Path: " + data.stdout + "</li>";
	tempstring += "<li>StdErr Path: " + data.stderr + "</li>";
	tempstring += "</ul>";

	showInfoDialog("SGE Info for " + jobNo, tempstring, 500);
}

// Show stdout/stderr for a task
function taskInfo(jobNo, taskNo) {
	$.ajax({
		url: "cgi/readLog.cgi",
		data: "sgeid=" + jobNo + "&frame=" + taskNo,
		type: "GET",
		dataType: "json",
		success: function(data) {
			content = "<div id=\"leftlog\" class=\"logpane\">\n";
			content += "<h3>Stdout</h3>\n";
			content += data.stdout + "\n";
			content += "</div><div id=\"rightlog\" class=\"logpane\">\n";
			content += "<h3>Stderr</h3>\n";
			content += data.stderr + "\n";
			content += "</div>\n";
			content += "<div class=\"clearboth\"></div>\n";
			showInfoDialog("Logs", content, 1000, 500);
		}
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
		title : "Confirmation Required",
		buttons : {
			"Confirm" : function() {
				$.ajax({
					url: "cgi/retry.cgi",
					data: "sgeid=" + jobNo,
					type: "POST",
					dataType: "json",
					success: function(data) {
						refreshPage();
						$("#multiusedialog")
							.dialog("close");

						var tabName = "#" + data.sgeid + "tab";
						if ($(tabName).length > 0) {
							$("#tabs").tabs("remove", tabName);
						}
					}
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

	$("#multiusedialog")
	.html("Are you sure?")
	.dialog({
		width : 300,
		title : "Confirmation Required",
		buttons : {
			"Confirm" : function() {
				$.ajax({
					url: "cgi/deleteJob.cgi",
					data: "sgeid=" + jobNo,
					type: "POST",
					dataType: "json",
					success: function(data) {
						refreshPage();
						$("#multiusedialog")
							.dialog("close");

						var tabName = "#" + data.sgeid + "tab";
						if ($(tabName).length > 0) {
							$("#tabs").tabs("remove", tabName);
						}
					}
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
function stopTask(jobNo, taskNo) {
	var tempstring = "Are you sure?<br /><br />This will delete the task ";
	tempstring += "from the queue but not from this page.  It'll show up ";
	tempstring += "as purple (other) status";

	$("#multiusedialog")
	.html(tempstring)
	.dialog({
		width : 300,
		title : "Confirmation Required",
		buttons : {
			"Confirm" : function() {
				var AJAXparams = "sgeid=" + jobNo
				AJAXparams += "&taskno=" + taskNo;

				$.ajax({
					url: "cgi/stopTask.cgi",
					data: AJAXparams,
					type: "POST",
					dataType: "json",
					success: function(data) {
						refreshPage();
						$("#multiusedialog")
							.dialog("close");
					}
				});
			},
			"Cancel" : function() {
				$(this).dialog("close");
			}
		}
	});
	$("#multiusedialog").dialog("open");
}

// Remove all errored jobs.  They do need to be removed from queue
function removeErrors() {
	if (usernameVal == "") {
		$("#multiusedialog")
		.html("You need to have a username in the filter box on the left")
		.dialog({
			width : 300,
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
			title : "Confirmation Required",
			buttons : {
				"Confirm" : function() {
					var AJAXparams = "user=" + usernameVal;
					if (removeOldOnly == 1) {
						AJAXparams = AJAXparams + "&old=1";
					}

					$.ajax({
						url: "cgi/deleteErrors.cgi",
						data: AJAXparams,
						type: "POST",
						success: function(data) {
							refreshPage();
							$("#multiusedialog")
								.dialog("close");
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

// Remove all completed jobs.  Don't need to remove from queue because they
// already have been since they're done
function removeComplete() {
	if (usernameVal == "") {
		$("#multiusedialog")
		.html("You need to have a username in the filter box on the left")
		.dialog({
			width : 300,
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
			title : "Confirmation Required",
			buttons : {
				"Confirm" : function() {
					var AJAXparams = "user=" + usernameVal;
					if (removeOldOnly == 1) {
						AJAXparams = AJAXparams + "&old=1";
					}

					$.ajax({
						url: "cgi/deleteComplete.cgi",
						data: AJAXparams,
						type: "POST",
						success: function(data) {
							refreshPage();
							$("#multiusedialog")
								.dialog("close");
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
	}).click(function() { removeOldOnly = 0; removeComplete(); });
	$("#removeOld").button({
		icons: { primary: "ui-icon-closethick" }
	}).click(function() { removeOldOnly = 1; removeComplete(); });
	$("#removeErrors").button({
		icons: { primary: "ui-icon-closethick" }
	}).click(function() { removeOldOnly = 0; removeErrors(); });
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
}

// Set up all the filter functions for the left filter bar
function setupFilterFunctions() {
	$("#jobsFilters input").blur(function() {
		refreshJobsFilters();
		refreshWorkerFilters();
		refreshPage();
	});
	$("#jobsFilters input").bind('keyup', function (e) {
		var key = e.keyCode || e.which;
		if (key === 13) {
			refreshJobsFilters();
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
