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
</tr>;"
