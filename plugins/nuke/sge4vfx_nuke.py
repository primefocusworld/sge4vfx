#  sge4vfx_nuke.py
#  sge4vfx_nuke
#
#  Created by Stephen Willey on 04/02/2011

import os, nuke, nukescripts, time, shutil, re
from datetime import datetime
from subprocess import Popen,PIPE

# TODO
# Allow user to choose
# - Which write nodes to render
# -- Turn off write notes that had the read file flag set
# - Allow relative paths in the Nuke files (won't work currently because
#   we're copying the nuke script into the SGE directories)
# - Automatic retries?  Part of a larger effort to add max-auto-retries to the
#   DB schema and use exit code 99 to have the epilog re-queue jobs

# Build a date string to save off the SGE submission stuff
def buildDateTime():
	return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


# Write out the Nuke command file
def writeNukeCmdFile(sgePath, nukeCmd):
	nf = open(sgePath + "/nukeCommand.sh", "w")

	nf.write("#!/bin/bash\n\n")
	nf.write("#$ -o " + sgePath + "/logs/o.$TASK_ID\n")
	nf.write("#$ -e " + sgePath + "/logs/e.$TASK_ID\n\n")
	nf.write("> $SGE_STDOUT_PATH\n")
	nf.write("> $SGE_STDERR_PATH\n\n")
	# I put the batch endframe calculation stuff into the script
	# either way.  If it's not a batch job, ENDFRAME will just never
	# be used by the Nuke command on the following lines
	nf.write("let ENDFRAME=${SGE_TASK_ID}+${SGE_TASK_STEPSIZE}-1\n")
	nf.write("if [ ${ENDFRAME} -gt ${SGE_TASK_LAST} ]; then\n")
	nf.write("	ENDFRAME=${SGE_TASK_LAST}\n")
	nf.write("fi\n\n")
	nf.write(nukeCmd + "\n")
	nf.write("\n# Write return code for epilog script\n")
	nf.write("echo $? > /tmp/${JOB_ID}-${SGE_TASK_ID}-return\n")
	nf.close()

	os.chmod(sgePath + "/nukeCommand.sh", 0755)


# Write out the SGE command file
def writeSGECmdFile(sgePath, sgeCmd):
	sf = open(sgePath + "/sgeNuke.sh", "w")

	sf.write("#!/bin/bash\n\n")
	sf.write(sgeCmd + "\n")
	sf.close()

	os.chmod(sgePath + "/sgeNuke.sh", 0755)


def Submit(fullSize, startFrame, endFrame, batchSize,
		slotsPerFrame, whichQueue, previewNode, doesItNeedOcula):
	# Specify where gridsub is
	gridsub = "gridsub" # assumes it's in the path, otherwise put full path

	# Save the script
	if nuke.scriptSave():
		# Get all the job bits
		script_name=nuke.Root().name()
		job_path=os.path.basename(script_name)
		(job_title, extension)=os.path.splitext(job_path)
		dirPath = nukescripts.script_directory();

		dateStr = buildDateTime()
	
		# Create the SGE folder next to the Nuke script if it doesn't
		# exist. It also creates the log folder for the stdout & stderr
		sgePath = dirPath + "/.theQ/" + dateStr
		prepCmd1 = ("if [ ! -d " + sgePath + " ]; then mkdir -p "
			+ sgePath + "/logs; fi")
		os.system(prepCmd1)

		# Check whether to force full size
		if fullSize:
			fullSizeBit = "-f "
		else:
			fullSizeBit = ""

		# If it's a batch job, do batch stuff...
		if int(batchSize) > 1:
			frameRangeBit = "-F ${SGE_TASK_ID}-${ENDFRAME} "
		else:
			frameRangeBit = "-F ${SGE_TASK_ID} "

		# Create the command file
		nukeCmd = ("nuke -x " + fullSizeBit + frameRangeBit + sgePath +
			"/" + job_path)
		writeNukeCmdFile(sgePath, nukeCmd)

		licenseRequirement = ""
		if doesItNeedOcula:
			licenseRequirement = "-l lic_ocula_r=1 "

		# Now the actual gridsub execution thingy
		sgeCmd = (gridsub
			+ " -N " + job_title
			+ " -V -S /bin/bash "
			+ " -pe pe1 " + slotsPerFrame
			+ " -q " + whichQueue
			+ " -t " + startFrame + "-" + endFrame
			+ ":" + batchSize + " "
			+ licenseRequirement
			+ sgePath
			+ "/nukeCommand.sh")
		writeSGECmdFile(sgePath, sgeCmd)

		# Take a snapshot of the Nuke file (useful for resubmission)
		shutil.copyfile(script_name, sgePath + "/" + job_path)

		# Run the SGE submission command
		p1 = Popen(sgePath + "/sgeNuke.sh", stdout=PIPE)
		theJobID = p1.communicate()[0]
		sgeID = theJobID.partition(".")[0]

		# Add the previewNode location to the job_extras table
		jobExtraPreview(sgeID, previewNode, fullSize)
	
		# Tell the user the SGE ID
		nuke.message("Render job submitted\nID is " + sgeID)


# Creates the UI panel that the user sees
# When they click OK, it runs the submit function
def RenderPanel():
	# Set defaults
	startFrame = str(nuke.root().firstFrame())
	endFrame = str(nuke.root().lastFrame())
	batchSize = str(5)
	slotsRequired = str(4)
	renderFullSize = True
	whichQueue = "farm.q"
	notePadBits = ("When you click OK, this will save your script " +
		"in it's current form.\n\nIf you don't want your file " +
		"overwritten now, click Cancel." )
	writeNodes = getWriteNodes()
	doesItNeedOcula = needsOcula()

	if writeNodes == "":
		nuke.message("You don't have any write nodes!")
	else:
		# Create the panel and put the bits on it
		p = nuke.Panel("Render on theQ")
		p.addBooleanCheckBox("Render full size:", renderFullSize)
		p.addSingleLineInput("Start Frame:", startFrame)
		p.addSingleLineInput("End Frame:", endFrame)
		p.addSingleLineInput("Slots per frame:", slotsRequired)
		p.addSingleLineInput("Queue:", whichQueue)
		p.addSingleLineInput("Batch Size:", batchSize)
		p.addEnumerationPulldown("Write node to preview:", writeNodes)
		p.addNotepad("Important:", notePadBits)
		p.addButton("Cancel")
		p.addButton("OK")

		# Show the panel and wait for a button
		result = p.show()

		# Now get all the values and submit if the user clicked OK
		if result == 1:
			renderFullSize = p.value("Render full size:")
			startFrame = p.value("Start Frame:")
			endFrame = p.value("End Frame:")
			slotsPerFrame = p.value("Slots per frame:")
			whichQueue = p.value("Queue:")
			batchSize = p.value("Batch Size:")
			previewNode = p.value("Write node to preview:")

			Submit(renderFullSize,
				startFrame,
				endFrame,
				batchSize,
				slotsPerFrame,
				whichQueue,
				previewNode,
				doesItNeedOcula)


# Gets the list of write nodes for the enumeration plugin
def getWriteNodes():
	returnVal = ""

	writeNodes = nuke.allNodes("Write")
	if writeNodes:
		for wNode in writeNodes:
			returnVal += wNode['name'].value() + " "

	return returnVal


# Check if we need an Ocula license
def needsOcula():
	returnVal = False

	for n in nuke.allNodes():
		if n.knob('thisIsAnOculaPlugin'):
			returnVal = True

	return returnVal


# Add the selected write node as the previewable one for the webUI
def jobExtraPreview(theJobID, previewNode, fullSize):
	theNode = nuke.toNode(previewNode)
	if fullSize:
		location = theNode['file'].value()
	else:
		location = nuke.filename(theNode)

	# Replace %0xd with x number of hashes
	num = re.search("^(.*)(%([0-9]+)d)(.*)$", location)
	if num is not None:
		hashReplace = "#" * int(num.group(3))
		newLocation = (num.group(1) + hashReplace + num.group(4))
	else:
		# Can't find %XXd so look for %d, otherwise, just return orig
		newLocation = re.sub("%d", "#", location)

	# Do the gridextra command to add the output_path info
	previewCmd = ("gridextra " + theJobID + " output_path "
		+ "\"" + newLocation + "\"")
	os.system(previewCmd)
