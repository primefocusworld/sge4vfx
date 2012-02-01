import os, shutil, re
import maya.cmds as mc
from datetime import datetime
from subprocess import Popen,PIPE

class renderDialog:
	priorities = { "Normal" : "0", "Low" : "-300", "Whenever" : "-600" }
	gridsub = "gridsub"		# Assumes it's in the path, otherwise put full path
	renderCmd = "mayarender"	# The actual Maya render binary
	whichQueue = "farm.q"
	licenseRequirement = ""

	def __init__(self):
		# Load the QT Designer UI file
		relPath = os.path.dirname(os.path.realpath(__file__))
		self.UIElements = {}
		self.UIElements["window"] = mc.loadUI(uiFile = relPath + '/dialog.ui')
		
		# Fill in the start and end frames along with the batch number
		mc.textField("startFrameLineEdit", edit=True, text=
			str(int(mc.getAttr('defaultRenderGlobals.startFrame'))))
		mc.textField("endFrameLineEdit", edit=True, text=
			str(int(mc.getAttr('defaultRenderGlobals.endFrame'))))
		mc.textField("batchSizeLineEdit", edit=True, text="1")
		
		# Show the window
		mc.showWindow(self.UIElements["window"])
	
	# Build a date string to save off the SGE submission stuff
	def buildDateTime(self):
		return datetime.now().strftime("%Y%m%d-%H%M%S")
	
	# Write out the Maya command file
	def writeMayaCmdFile(self, sgePath, mayaCmd):
		mf = open(sgePath + "/mayaCommand.sh", "w")
		
		mf.write("#!/bin/bash\n\n")
		mf.write("#$ -o " + sgePath + "/logs/o.$TASK_ID\n")
		mf.write("#$ -e " + sgePath + "/logs/e.$TASK_ID\n\n")
		mf.write("> $SGE_STDOUT_PATH\n")
		mf.write("> $SGE_STDERR_PATH\n\n")
		# I put the batch endframe calculation stuff into the script
		# either way.  If it's not a batch job, ENDFRAME will just never
		# be used by the Maya command on the following lines
		mf.write("let ENDFRAME=${SGE_TASK_ID}+${SGE_TASK_STEPSIZE}-1\n")
		mf.write("if [ ${ENDFRAME} -gt ${SGE_TASK_LAST} ]; then\n")
		mf.write("	ENDFRAME=${SGE_TASK_LAST}\n")
		mf.write("fi\n\n")
		mf.write(mayaCmd + "\n")
		mf.write("\n# Write return code for epilog script\n")
		mf.write("echo $? > /tmp/${JOB_ID}-${SGE_TASK_ID}-return\n")
		mf.close()
		
		os.chmod(sgePath + "/mayaCommand.sh", 0755)
	
	# Write out the SGE command file
	def writeSGECmdFile(self, sgePath, sgeCmd):
		sf = open(sgePath + "/sgeMaya.sh", "w")
		
		sf.write("#!/bin/bash\n\n")
		sf.write(sgeCmd + "\n")
		sf.close()
		
		os.chmod(sgePath + "/sgeMaya.sh", 0755)
	
	# Dump the shell environment
	def writeEnvFile(self, sgePath):
		ef = open(sgePath + "/theEnv", "w")
		
		for param in os.environ.keys():
			if os.environ[param].find('*') == -1:
				ef.write("%s=%s\n" % (param,os.environ[param]))
		ef.close()
	
	# If it's been set, send a mail
	def jobExtraEMail(self, theJobID):
		# Do the gridextra command to add the output_path info
        	previewCmd = ("gridextra " + theJobID + " email yes")
	        os.system(previewCmd)
	
	# Run this if OK is pressed
	def ok(self):	
		# Check if the file's been saved yet.  If not, close and let the user know
		if (mc.file(q=True, sceneName=True) == ""):
			mc.confirmDialog(title='Not Saved Yet',
				message='Please save your scene before sending it to the farm',
				button=['OK'],
				defaultButton='OK')
			return
		# Now save it and make sure it saves properly
		fullPath = mc.file(q=True, sceneName=True)
		if (mc.file(save=True) == fullPath):
			# Get the various bits of the filename
			dirPath = os.path.dirname(fullPath)
			fileName = os.path.basename(fullPath)
			(jobTitle, extension)=os.path.splitext(fileName)
			
			# Read all the useful stuff off the panel
			startFrame = mc.textField("startFrameLineEdit", q=True, text=True)
			endFrame = mc.textField("endFrameLineEdit", q=True, text=True)
			batchSize = mc.textField("batchSizeLineEdit", q=True, text=True)
			priority = mc.optionMenu("priorityComboBox", q=True, v=True)
			emailNotify = mc.checkBox("eMailNotificationCheckBox", q=True, v=True)
			slotsPerFrame = mc.textField("slotsLineEdit", q=True, text=True)
			dateStr = self.buildDateTime()
			
			# Create the SGE folder next to the Maya scene if it doesn't
			# exist. It also creates the log folder for the stdout & stderr
			sgePath = dirPath + "/.theQ/" + dateStr
			prepCmd1 = ("if [ ! -d " + sgePath + " ]; then mkdir -p "
				+ sgePath + "/logs; fi")
			os.system(prepCmd1)
			
			# If it's a batch job, do batch stuff...
			if int(batchSize) > 1:
				frameRangeBit = "-s ${SGE_TASK_ID} -e ${ENDFRAME} "
			else:
				frameRangeBit = "-s ${SGE_TASK_ID} -e ${SGE_TASK_ID} "

			# Create the command file
			mayaCmd = (self.renderCmd
				+ " " + frameRangeBit
				+ " " + sgePath + "/" + fileName)
			self.writeMayaCmdFile(sgePath, mayaCmd)
			
			# Now the actual gridsub execution thingy
			sgeCmd = (self.gridsub
				+ " -N " + jobTitle
				+ " -V -S /bin/bash "
				+ " -pe pe1 " + slotsPerFrame
				+ " -p " + self.priorities[priority]
				+ " -q " + self.whichQueue
				+ " -t " + startFrame + "-" + endFrame
				+ ":" + batchSize + " "
				+ self.licenseRequirement
				+ sgePath
				+ "/mayaCommand.sh")
			self.writeSGECmdFile(sgePath, sgeCmd)
			self.writeEnvFile(sgePath)
			
			# Take a snapshot of the Maya file (useful for resubmission)
			shutil.copyfile(fullPath, sgePath + "/" + fileName)
			
			# Run the SGE submission command
			p1 = Popen(sgePath + "/sgeMaya.sh", stdout=PIPE)
			theJobID = p1.communicate()[0]
			sgeID = theJobID.partition(".")[0]
			print "Done the submission"
			
			if emailNotify:
				self.jobExtraEMail(sgeID)
			
			# Tell the user the SGE ID
			mc.confirmDialog(title='Job ID',
				message='Your job ID is: ' + sgeID,
				button=['OK'],
				defaultButton='OK')
			return
		# File didn't save properly so let the user know and close
		else:
			mc.confirmDialog(title='Problem Saving',
				message='Not sure what went wrong, but Maya wouldn\'t save the file',
				button=['OK'],
				defaultButton='OK')
			return
