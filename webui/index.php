<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>theQ</title>
	<link rel="stylesheet" type="text/css" media="screen" href="css/custom-theme/jquery-ui-1.8.7.custom.css">
	<link rel="stylesheet" type="text/css" media="screen" href="css/main.css">
	<script type="text/javascript" src="js/jquery-1.4.4.min.js"></script>
	<script type="text/javascript" src="js/jquery-ui-1.8.7.custom.min.js"></script>
	<script type="text/javascript" src="js/ui.tabs.closable.js"></script>
	<script type="text/javascript" src="js/jquery.cookie.js"></script>
	<script type="text/javascript" src="js/main.js"></script>
</head>
<body>
<div id="header">
	<h1>theQ</h1>
	<div id="topToolbar" class="ui-widget-header ui-corner-all">
		<button id="showLegend">Help</button>
		<input type="checkbox" id="autorefresh" name="autorefresh" checked><label for="autorefresh">Auto Refresh</label>
	</div>
</div>
<div id="tabs">
	<ul>
		<li class="tab-no-close"><a href="#jobstab"><span>Jobs</span></a></li>
		<li class="tab-no-close"><a href="#workerstab">Workers</a></li>
	</ul>
	<div id="jobstab">
		<table id="containerTable" cellpadding="0" cellspacing="0">
		<tr><td id="leftContainer">
			<div id="filtersContainer">
				<h2>Filters</h2>
				<div id="filters">
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
		</td><td id="gutter">&nbsp;
		</td><td id="rightContainer">
			<div id="jobsToolbar" class="ui-widget-header ui-corner-all">
				<button title="Remove all successfully completed jobs" id="removeAllComplete">Remove Done</button>
				<button title="Remove jobs older than start of yesterday" id="removeOld">Remove Old</button>
			</div>
			<table id="jobsTable" class="mainTable">
				<thead>
				<tr>
					<th class="narrow2">Actions</th>
					<th class="narrow1">ID</th>
					<th class="normalwidth">Job Name</th>
					<th class="narrow1">Username</th>
					<th class="narrow2">Project</th>
					<th class="narrow1">Priority</th>
					<th class="narrow2">Submit Time</th>
					<th class="narrow2">Start Time</th>
					<th class="narrow2">End Time</th>
					<th class="narrow1">Duration</th>
					<th class="narrow1">Range</th>
					<th class="narrow2">% Done</th>
				</tr>
				</thead>
				<tbody></tbody>
			</table></div>
		</td></tr>
		</table>
	<div id="workerstab">
		<p>Some other stuff</p>
	</div>
</div>
<div id="multiusedialog"></div>
<div id="helpdialog" title="Help">
	<h3>Colours in the tables</h3>
	<div class="greybg colourbar">Pending</div>
	<div class="greenbg colourbar">Running</div>
	<div class="bluebg colourbar">Completed</div>
	<div class="redbg colourbar">Error</div>
	<div class="purplebg colourbar">Other</div>
</div>
<div id="lastupdate">Last Updated: Never</div>
</body>
</html>

