var mainJobTableRowTemplate = "\
{{#rows}}\
<tr onclick='addJobTab({{ sgeid }});' id='row{{ sgeid }}' class='{{ status }}'>\
	<td>\
		<img class='iconbtn' onclick='deleteJob(event, {{ sgeid }});' src='static/images/delete.png' title='Delete Job' />\
{{#notdone}}<img class='iconbtn' onclick='changePriority(event, {{ sgeid }});' src='static/images/priority.png' title='Change Priority' />{{/notdone}}\
{{#output_path}}<a onclick='event.stopPropagation(); toast(\"RV\",\"Opening RV.  Please wait...\");' href='rvlink://{{ output_path }}'>\
<img class='iconbtn' src='static/images/film.png' title='Preview in RV'>\
</a>{{/output_path}}\
{{#haserrors}}<img class='iconbtn' onclick='retry(event, {{ sgeid }});' src='static/images/retry.png' title='Retry Errors' />{{/haserrors}}\
	</td>\
	<td>{{ sgeid }}</td>\
	<td>{{ jobname }}</td>\
	<td>{{ username }}</td>\
	<td>{{ project }}</td>\
	<td>{{ priority }}</td>\
	<td title='{{ submittimetitle }}'>{{ submittimestr }}</td>\
	<td title='{{ starttimetitle }}' alt='{{ starttimealt }}' class='starttime'>{{ starttimestr }}</td>\
	<td title='{{ endtimetitle }}'>{{ endtimestr }}</td>\
	<td{{#realtimeupdate}} class='rtupdate'{{/realtimeupdate}}>{{ durationstr }}</td>\
	<td>{{ firsttask }}-{{ lasttask }}:{{ chunk }}</td>\
	<td class='percentdone'>{{ pcdone }}% ({{ donetasks }})</td>\
</tr>\
{{/rows}}"

var oneJobRowTemplate = "\
{{#rows}}\
<tr id='row{{ sgeid }}-{{taskno}}' class='{{ status }}'>\
	<td>\
		<img class='iconbtn' onclick='taskInfo({{ sgeid }}, {{ taskno }});' src='static/images/log.png' />\
{{#output_path}}<a onclick='toast(\"RV\",\"Opening RV.  Please wait...\");' href='rvlink://{{ output_path }}'>\
<img class='iconbtn' src='static/images/film.png' title='Preview in RV'>\
</a>{{/output_path}}\
{{#errorRetryIcon}}<img class='iconbtn' onclick='retry(event, \"{{ sgeid }}.{{ taskno }}\")' src='static/images/retry.png' title='Retry' />{{/errorRetryIcon}}\
{{#rescheduleIcon}}<img class='iconbtn' onclick='reschedule(event, \"{{ sgeid }}.{{ taskno }}\")' src='static/images/resched.png' title='Kill and Retry' />{{/rescheduleIcon}}\
	</td>\
	<td>{{ sgeid }}-{{ taskno }}</td>\
	<td title='{{ starttimetitle }}' alt='{{ starttimealt }}' class='starttime'>{{ starttimestr }}</td>\
	<td title='{{ endtimetitle }}'>{{ endtimestr }}</td>\
	<td{{#realtimeupdate}} class='rtupdate'{{/realtimeupdate}}>{{ durationstr }}</td>\
	<td>{{ returncode }}</td>\
	<td>{{ attempts }}</td>\
	<td>{{ rhost }}</td>\
</tr>\
{{/rows}}"

var userQuotaRowTemplate = "\
{{#rows}}\
<tr><td>{{ username }}</td><td>{{ slots_used }}</td></tr>\
{{/rows}}\
"

var farmDivisionTemplate = "\
Total Slots: {{ total }}<br /><br />\
<span class='green'>\
	Good: {{ good }} ({{ goodpc }}%)\
</span><br />\
<span class='red'>\
	Broken: {{ broken }} ({{ brokenpc }}%)\
</span><br />\
<span class='yellow'>\
	Suspended: {{ suspended }} ({{ suspendedpc }}%)\
</span><br /><br />\
Used Slots: {{ used }} ({{ usedpc }}%)<br />\
Available Slots: {{ avail }} ({{ availpc }}%)\
"

var workerTableRowTemplate = "\
{{#rows}}\
<tr class='{{ status }}'>\
<td>{{ hostname }}</td>\
<td>\
	<div class='slotdivcontainer'>\
		<div class='slotinfo'>{{ used }}/{{ total }}</div>\
		<div{{#pcused}} class='percent{{ pcused }} usageindicator'{{/pcused}}>&nbsp;</div>\
	</div>\
</td>\
<td>{{ load_avg }}</td>\
<td>{{ machine_states }}</td>\
</tr>\
{{/rows}}\
"

var logTemplate = "\
<div id='leftlog' class='logpane'>\
	<h3>Stdout</h3>\
	{{{ stdout }}}\
</div>\
<div id='rightlog' class='logpane'>\
	<h3>Stderr</h3>\
	{{{ stderr }}}\
</div>\
<div class='clearboth'></div>\
"
