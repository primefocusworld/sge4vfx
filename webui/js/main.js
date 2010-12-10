// SGE bitmask states
var JHELD = 0x10
var JQUEUED = 0x40
var JWAITING = 0x800
var JRUNNING = 0x80
var JSUSPENDED = 0x100
var JSUSPENDED_ON_THRESHOLD = 0x10000
var JERROR = 0x8000

var refreshTimeout;
var refreshInterval = 3000;
var currentJob;

// These are here for now for testing - for now it needs a username
// TODO: Put a username box handled by cookies/kerberos
testParam = "user=PUT_USERNAME_HERE";

// AJAX call to simple helper script that sources the SGE env and runs qstat -f -xml
function getQStat(params, callback) {
	$.ajax({
		type: "GET",
		url: "./cgi/getqstat.cgi",
		data: params,
		dataType: "xml",
		success: callback
	});
}

function bitmaskToStates(bitmask) {
	var taskStatus = new Array();
	
	if ( bitmask & JHELD ) taskStatus.push("Held");
	if ( bitmask & JQUEUED ) taskStatus.push("Queued");
	if ( bitmask & JWAITING ) taskStatus.push("Waiting");
	if ( bitmask & JRUNNING ) taskStatus.push("Running");
	if ( bitmask & JSUSPENDED ) taskStatus.push("Suspended");
	if ( bitmask & JSUSPENDED_ON_THRESHOLD ) taskStatus.push("Suspended on threshold");
	if ( bitmask & JERROR ) taskStatus.push("Error");

	return taskStatus.join(",");
}

// Parses the return from qstat and creates the job table
function createJobTable(xml) {
	// Firstly, make sure it's showing after emptying the table
	$("#jobsTable tbody tr.jobtr").remove();
	$("#tasksTable").hide(); $("#jobsTable").show();
	$("#parents").html("Root");

	// For every job in the XML
	var uniqJobs = new Array();
	$(xml).find("job_list").each(function() {
		job = $(this);
		jobNo = job.find("JB_job_number").text();
		// If the job's not already in the uniqJobs array, add a line
		if ( $.inArray(jobNo, uniqJobs) == -1 ) {
			uniqJobs.push(jobNo);
			jobName = job.find("JB_name").text();

			$("#jobsTable tbody").append("\t\t<tr class=\"jobtr\" id=\"" + jobNo + "\" onclick=\"$.history.load('job" + jobNo + "');\">\n"
							+ "\t\t\t<td>" + jobNo + "</td>\n"
							+ "\t\t\t<td>" + jobName + "</td>\n"
							+ "\t\t\t<td>" + job.find("JB_owner").text() + "</td>\n"
							+ "\t\t\t<td>" + job.find("JAT_prio").text() + "</td>\n"
							+ "\t\t\t<td> </td>\n"
							+ "\t\t\t<td> </td>\n"
							+ "\t\t\t<td class=\"running\"></td>\n"
							+ "\t\t\t<td class=\"pending\"></td>\n"
							+ "\t\t\t<td class=\"chunksize\"></td>\n"
							+ "\t\t\t<td class=\"startTime\"> </td>\n"
						+ "\t\t</tr>\n");
			switch (job.attr("state")) {
				case "running":
					$("#jobsTable tr#" + jobNo).addClass('running');
					// If job is running, look for the start time
					// then make it prettier and put it in the start time column
					jobStartTime = job.find("JAT_start_time").text();
					tempArray = jobStartTime.split("T");
					jobStartTime = tempArray[1] + " | " + tempArray[0];
					$("#jobsTable tr#" + jobNo + " .startTime").html(jobStartTime);
					break;
				case "pending":
					$("#jobsTable tr#" + jobNo).addClass('pending');
					break;
				default:
					break;
			}
		}
		if (job.attr("state") == "running") {
			// Look at the task number and add it to running field
			taskNo = job.find("tasks").text();
			var sep = "";
			if ($("#jobsTable tr#" + jobNo + " .running").html() != "") { sep = "," }
			$("#jobsTable tr#" + jobNo + " .running").append(sep + taskNo);
		}
		if (job.attr("state") == "pending") {
			// Look at the task number and add it to pending field
			taskNo = job.find("tasks").text();
			tempArray = taskNo.split(":");
			$("#jobsTable tr#" + jobNo + " .pending").append(tempArray[0]);
			$("#jobsTable tr#" + jobNo + " .chunksize").append(tempArray[1]);
		}
	});
	$('#jobsTable tbody tr.running:odd').addClass('runninge');
	$('#jobsTable tbody tr.pending:odd').addClass('pendinge');
}

// Show all the jobs
function returnToRoot() {
	// Add a URL to the history and update the title
	$.history.load("");
	document.title = "theQ";

	// Now go get the data and create the table
	getQStat(testParam, createJobTable);
}

// Show the tasks that make up a job
function showJob(jobNo) {
	// Add a URL to the history and update the title
	document.title = "Job " + jobNo;
	currentJob = jobNo;

	// Now go get the data and create the table
	getQStat(testParam + "&jobNo=" + jobNo,
		function(xml) { createTaskTable(xml, jobNo); }
	);
}

// Shows the tasks in a job
function createTaskTable(xml, jobNo) {
	jobName = $(xml).find("JB_job_name").text();
	$("#parents").html("<a href=\"\" onclick=\"returnToRoot(); return false;\">Root</a> &gt; " + jobName + " (" + jobNo + ")");
	$("#jobsTable").hide(); $("#tasksTable").show();
	$("#tasksTable tbody tr.tasktr").remove();

	// For every task in the XML
	minTask = parseInt($(xml).find("RN_min").text());
	maxTask = parseInt($(xml).find("RN_max").text());
	owner = $(xml).find("JB_owner").text();
	runningTasks = $(xml).find("JB_ja_tasks");

	for (var i = minTask; i <= maxTask; i++) {
		$("#tasksTable tbody").append("\t\t<tr class=\"tasktr\" id=\"task" + i + "\">\n"
						+ "\t\t\t<td>" + i + "</td>\n"
						+ "\t\t\t<td>" + owner + "</td>\n"
						+ "\t\t\t<td class=\"taskstate\"> </td>\n"
						+ "\t\t\t<td> </td>\n"
						+ "\t\t\t<td> </td>\n"
						+ "\t\t\t<td> </td>\n"
						+ "\t\t\t<td> </td>\n"
						+ "\t\t\t<td> </td>\n"
						+ "\t\t\t<td> </td>\n"
					+ "\t\t</tr>\n");
	}

	// Now go through the tasks qstat knows about and render some extra info
	$(xml).find("ulong_sublist").each( function() {
		task = $(this);
		taskNo = task.find("JAT_task_number").text();
		taskState = task.find("JAT_status").text();

		taskStateTD = $("#task" + taskNo + " td.taskstate");
		taskStateTD.html(bitmaskToStates(taskState));

		if ( taskStateTD.text().indexOf("Running") > -1 ) { $("#task" + taskNo).addClass('running'); }
		if ( taskStateTD.text().indexOf("Queued") > -1 ) { $("#task" + taskNo).addClass('pending'); }
	});

	$('#tasksTable tbody tr:odd').addClass('unknowne');
	$('#tasksTable tbody tr.running, #tasksTable tbody tr.running').removeClass('unknowne');
	$('#tasksTable tbody tr.running:odd').addClass('runninge');
	$('#tasksTable tbody tr.pending:odd').addClass('pendinge');
}

function returnToRightPlace(url) {
	// Parse the URL and compose the right page
	// Jobs table (root)
	if (url == "root") { returnToRoot(); }

	// Tasks table for a given job
	if (url.indexOf("job") > -1) {
		var reg = /\d+/;
		var regOut = reg.exec(url);
		showJob(regOut[0]);
	}
}

function refreshPage() {
	if ($("#jobsTable").is(":visible")) { returnToRoot(); }
	else if ($("#tasksTable").is(":visible")) { showJob(currentJob); }
	refreshTimeout = setTimeout(function() { refreshPage(); }, refreshInterval);
}

// Runs when the page is rendered
$(document).ready(function() {
	if ($.cookie("autoRefresh")) {
		$("#autorefresh INPUT[name=autorefresh]").attr("checked", true);
		refreshTimeout = setTimeout(function() { refreshPage() }, refreshInterval);
	}

	$("#autorefresh input").click( function() {
		var checkbox = $(this).find(":checkbox");
		checkbox.attr('checked', !checkbox.attr('checked'));

		if( $(this).is(":checked") ) {
			$.cookie("autoRefresh", true, { expires: 30 });
			refreshTimeout = setTimeout(function() { refreshPage(); }, refreshInterval);
		}
		if( $(this).is(":not(:checked)") ) {
			$.cookie("autoRefresh", null);
			clearTimeout(refreshTimeout);
		}
	});

	// JQuery history plugin manages URL hashes
	$.history.init(function(url) {
		returnToRightPlace(url == "" ? "root" : url);
	});
});
