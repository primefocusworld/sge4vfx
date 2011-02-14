// AJAX call to simple helper script that sources the SGE env and runs
// qstat -f -xml

var refreshTimeout;
var refreshInterval = 5000;
var realTimeInverval;
var sortJobsBy = "sgeid";
var sortJobsDir = "DESC";
var sortJobBy = "taskno";
var sortJobDir = "ASC";
var filters = "";
var usernameVal = "";

// Allows you to call jobsTable cgi script
function getJobs(params) {
	var ampersand = ""
	if (filters != "") { ampersand = "&"; }
	var AJAXparams = filters + ampersand + "sortby=" + sortJobsBy +
		"&sortdir=" + sortJobsDir + params;

	$.ajax({
		url: "cgi/jobs.cgi",
		data: AJAXparams,
		success: function(data) {
			$("#jobsTable tbody").html(data);
			if (realTimeInverval == null) {
				realTimeInverval = setInterval(
					'updateDurations()', 1000);
			}
		}
	});
}

// Allows you to call jobTable cgi script
function getJob(params, whichJob) {
	var AJAXparams = "sortby=" + sortJobBy + "&sortdir=" + sortJobDir;
	AJAXparams += "&jobno=" + whichJob + params;

	$.ajax({
		url: "cgi/oneJob.cgi",
		data: AJAXparams,
		success: function(data) {
			$("#"+whichJob+"tab tbody").html(data);
		}
	});
}

// Refresh the jobsTable
function refreshPage() {
	// Figure out which tab is visible and only refresh that one
	if ($("#jobsTable").is(":visible")) { getJobs(""); }
	else if ($(".jobTable").is(":visible")) {
		var tempID = $(".jobTable:visible").attr("id");
		var tempSplit = tempID.split("Table");
		
		getJob("", tempSplit[0]);
	}
	lastUpdated();
	clearTimeout(refreshTimeout);
	refreshTimeout = setTimeout(function() {
					refreshPage();
				}, refreshInterval);
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
	$("#lastrefresh").html("Last refreshed: " + timeString);
}

function showInfoDialog(theTitle, theContent, theWidth) {
	if ( theWidth === undefined ) { theWidth = 300; }
	$("#multiusedialog")
	.html(theContent)
	.dialog({
		width : theWidth,
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
	tempstring = "<ul>"
	tempstring += "<li>Scriptfile: " + data.scriptFile + "</li>"
	tempstring += "<li>StdOut Path: " + data.stdout + "</li>"
	tempstring += "<li>StdErr Path: " + data.stderr + "</li>"
	tempstring += "</ul>"

	showInfoDialog("SGE Info for " + jobNo, tempstring, 500);
}

// Pop up a dialog with info on a particular job
function jobInfo(e, jobNo) {
	// Stop the opening of the job tab
	e.stopPropagation();
	e.preventDefault();

	if ($("#row" + jobNo).hasClass("completed")) {
		showInfoDialog(jobNo + " Info", "No longer in SGE - TODO");
	} else if ($("#row" + jobNo).hasClass("error")) {
		showInfoDialog(jobNo + " Info", "Job has errors - TODO");
	} else {
		$.ajax({
			url: "cgi/getJobInfo.cgi",
			data: "sgeid=" + jobNo,
			type: "POST",
			dataType: "json",
			success: function(data, jobNo) {
				showJobInfo(data, jobNo);
			}
		});
	}
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
					type: "GET",
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
					type: "GET",
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

// Remove all completed jobs.  Don't need to remove from queue because they
// already have been since they're done
function removeAllComplete() {
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

function setupToolbar() {
	$("#removeAllComplete").button({
		icons: { primary: "ui-icon-closethick" }
	}).click(function() { removeAllComplete(); });
	$("#showLegend").button({
		icons: { primary: "ui-icon-info" }
	}).click(function() { showHelpDialog(); });
}

function updateDurations() {
	var rightNow = new Date();
	theYear = rightNow.getFullYear();

	$(".rtupdate").each(function() {
		rowID = $(this).parent().attr("id");
		startTimeTD = $("#" + rowID + " td.starttime");
		startTime = startTimeTD.html();
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

			$(this).html(hours+"h "+minutes+"m "+seconds+"s");
		}
	});
}

// Add a job tab if it's not already there.
function addJobTab(jobNo) {
	var tabID = "#" + jobNo + "tab"

	if ($(tabID).length == 0) {
		$("#tabs").tabs("add", tabID, jobNo)

		var tempString = "<table class=\"jobTable mainTable\" "
		tempString +="id=\"" + jobNo + "Table\">";
		tempString +="<thead><tr><th class=\"narrow2\">Actions";
		tempString +="</th><th class=\"narrow1\">ID</th>";
		tempString +="<th class=\"normalwidth\">Start Time";
		tempString +="</th><th class=\"normalwidth\">End Time";
		tempString +="</th><th class=\"narrow2\">Duration</th>";
		tempString +="<th class=\"narrow2\">Return Code</th>";
		tempString +="<th class=\"narrow2\">Exec Host</th>";
		tempString +="</tr></thead><tbody></tbody></table>";

		$("#" + jobNo + "tab").append(tempString);
	}
	$("#tabs").tabs("select", tabID);

	getJob("", jobNo);
	return false;
}

// Apply the filters set in the left filter bar
function refreshFilters() {
	filters = "";
	usernameVal = $("#username").val();
	if (usernameVal != "") { filters += "username="+usernameVal; }
	var projnameVal = $("#projname").val();
	if (projnameVal != "") {
		var ampersand = "";
		if (filters != "") { ampersand="&"; }
		filters += ampersand + "projname=" + projnameVal;
	}
	if ($("#donestate").is(":checked")) {
		var ampersand = "";
		if (filters != "") { ampersand="&"; }
		filters += ampersand + "done=1";
	}
	if ($("#runningstate").is(":checked")) {
		var ampersand = "";
		if (filters != "") { ampersand="&"; }
		filters += ampersand + "running=1";
	}
	if ($("#waitstate").is(":checked")) {
		var ampersand = "";
		if (filters != "") { ampersand="&"; }
		filters += ampersand + "wait=1";
	}
	if ($("#errorstate").is(":checked")) {
		var ampersand = "";
		if (filters != "") { ampersand="&"; }
		filters += ampersand + "error=1";
	}
	refreshPage();
}

// Set up all the filter functions for the left filter bar
function setupFilterFunctions() {
	$("#username").blur(function() { refreshFilters(); });
	$("#projname").blur(function() { refreshFilters(); });
	$("#waitstate").button({ icons: {primary:'ui-icon-clock'}, text: false });
	$("#donestate").button({ icons: {primary:'ui-icon-check'}, text: false });
	$("#runningstate").button({ icons: {primary:'ui-icon-gear'}, text: false });
	$("#errorstate").button({ icons: {primary:'ui-icon-alert'}, text: false });
	$("#stateboxes input").click(function() { refreshFilters(); });
	
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
	setupToolbar();
	setupFilterFunctions();

	// Setup all the autoRefresh bits
	if ($.cookie("doNOTautoRefresh")) {
		$("#autorefresh INPUT[name=autorefresh]").attr("checked", false);
	} else {
		refreshTimeout = setTimeout(function() {
						refreshPage()
					}, refreshInterval);
	}
	$("#autorefresh input").click( function() {
		var checkbox = $(this).find(":checkbox");
		checkbox.attr('checked', !checkbox.attr('checked'));
		if( $(this).is(":checked") ) {
			$.cookie("doNOTautoRefresh", null);
			refreshTimeout = setTimeout(function() {
							refreshPage();
						}, refreshInterval);
		}
		if( $(this).is(":not(:checked)") ) {
			$.cookie("doNOTautoRefresh", true, { expires: 30 });
			clearTimeout(refreshTimeout);
		}
	});

	// Now populate the jobsTable and set the event handler
	$('#tabs').bind('tabsshow', function(event, ui) {
		if (ui.panel.id == "jobstab") { getJobs(""); }
	});
	getJobs("");

	lastUpdated();
});
