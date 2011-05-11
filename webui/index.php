<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>theQ</title>
	<link rel="stylesheet" type="text/css" media="screen" href="css/custom-theme/jquery-ui-1.8.7.custom.css">
	<link rel="stylesheet" type="text/css" media="screen" href="css/ui.notify.css">
	<link rel="stylesheet" type="text/css" media="screen" href="css/main.css">
	<script type="text/javascript" src="js/jquery-1.4.4.min.js"></script>
	<script type="text/javascript" src="js/jquery-ui-1.8.7.custom.min.js"></script>
	<script type="text/javascript" src="js/ui.tabs.closable.js"></script>
	<script type="text/javascript" src="js/jquery.notify.js"></script>
	<script type="text/javascript" src="js/jquery.cookie.js"></script>
	<script type="text/javascript" src="js/main.js"></script>
</head>
<body>
<div id="header">
	<h1>theQ</h1>
	<div id="topToolbar" class="ui-widget-header ui-corner-all">
		<button id="showLegend">Help</button>
		<button id="manualRefresh" title="Manual Refresh">Refresh</button>
		<input type="checkbox" id="autorefresh" name="autorefresh"><label for="autorefresh">Auto Refresh</label>
	</div>
</div>
<div id="tabs">
	<ul>
		<li class="tab-no-close"><a href="#jobstab"><span>Jobs</span></a></li>
		<li class="tab-no-close"><a href="#workerstab"><span>Workers</span></a></li>
	</ul>
	<div id="jobstab">
		<table class="containerTable" cellpadding="0" cellspacing="0">
		<tr><td class="leftContainer">
			<div class="filtersContainer">
				<h2>Filters</h2>
				<div id="jobsFilters" class="filters">
					Username
<?php $ruser = preg_replace('/\@.*$/', '', getenv("REMOTE_USER")); ?>
					<input type="text" name="username" value="<?php echo $ruser; ?>" id="username" class="text ui-widget-content ui-corner-all deletable"/>
					Project
					<input type="text" name="projname" id="projname" class="text ui-widget-content ui-corner-all deletable" />
					State<br />
					<div id="stateboxes">
						<input type="checkbox" id="waitstate" class="checkbox" checked /><label for="waitstate">Waiting</label>
						<input type="checkbox" id="donestate" class="checkbox" checked /><label for="donestate">Done</label>
						<input type="checkbox" id="runningstate" class="checkbox" checked /><label for="runningstate">Running</label>
						<input type="checkbox" id="errorstate" class="checkbox" checked /><label for="errorstate">Error</label>
					</div>
				</div>
			</div>
		</td><td class="gutter">&nbsp;
		</td><td class="rightContainer">
			<div id="jobsToolbar" class="ui-widget-header ui-corner-all rightToolbar">
				<button title="Remove all successfully completed jobs" id="removeAllComplete">Remove Done</button>
				<button title="Remove jobs older than start of yesterday" id="removeOld">Remove Old</button>
				<button title="Remove jobs with errors" id="removeErrors">Remove Errored</button>
			</div>
			<table id="jobsTable" class="mainTable">
				<thead>
				<tr>
					<th class="narrow2">Actions</th>
					<th class="narrow1">ID</th>
					<th class="normalwidth">Job Name</th>
					<th class="narrow1">Username</th>
					<th class="narrow1">Project</th>
					<th class="narrow1">Priority</th>
					<th class="narrow2">Submit Time</th>
					<th class="narrow2">Start Time</th>
					<th class="narrow2">End Time</th>
					<th class="narrow1">Duration</th>
					<th class="narrow2">Range</th>
					<th class="narrow2">% Done</th>
				</tr>
				</thead>
				<tbody></tbody>
			</table>
		</td></tr>
		</table>
	</div>
	<div id="workerstab">
		<table class="containerTable" cellpadding="0" cellspacing="0">
		<tr><td class="leftContainer">
			<div class="filtersContainer">
				<h2>Filters</h2>
				<div id="workerFilters" class="filters">
					Queue
					<input type="text" name="queuename" id="queuename" class="text ui-widget-content ui-corner-all deletable" />
				</div>
			</div>
		</td><td class="gutter">&nbsp;
		</td><td class="rightContainer">
			<div id="workersToolbar" class="ui-widget-header ui-corner-all rightToolbar">
				<button title="Something" id="something">Something</button>
			</div>
			<table id="workersTable" class="mainTable">
				<thead>
				<tr>
					<th class="normalwidth">Name</th>
					<th class="normalwidth">Slots Used/Total</th>
					<th class="normalwidth">Load Avg.</th>
					<th class="narrow1">Status Codes</th>
				</tr>
				</thead>
				<tbody></tbody>
			</table>
		</td></tr>
		</table>
	</div>
</div>
<div id="multiusedialog" class="popupdialog"></div>
<div id="helpdialog" title="Help" class="popupdialog">
	<h3>Colours in the tables</h3>
	<div class="greybg colourbar">Pending</div>
	<div class="greenbg colourbar">Running</div>
	<div class="bluebg colourbar">Completed</div>
	<div class="redbg colourbar">Error</div>
	<div class="purplebg colourbar">Other</div>
</div>
<div id="notifications">
	<div id="basic-notification">
		<a class="ui-notify-close" href="#"><span class="ui-icon ui-icon-close" style="float:right"></span></a>
		<h1>#{title}</h1>
		<p>#{text}</p>
	</div>
</div>
<div id="lastupdate">Last Updated: Never</div>
</body>
</html>

