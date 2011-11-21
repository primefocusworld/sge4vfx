var mainJobTableRowTemplate = "\
{{#rows}}\
<tr onclick='addJobTab({{ sgeid }});' id='row{{ sgeid }}' class='{{ status }}'>\
	<td>\
		<img class='iconbtn' onclick='deleteJob(event, {{ sgeid }});' src='static/images/delete.png' title='Delete Job' />\
{{#notdone}}<img class='iconbtn' onclick='changePriority(event, {{ sgeid }});' src='static/images/priority.png' title='Change Priority' />{{/notdone}}\
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
{{/rows}}\
<tr class='hiddencountrow'>\
	<td id='hiddencount'>{{ totalJobCount }}</td>\
</tr>"

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