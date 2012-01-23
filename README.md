#SGE4VFX

An attempt to make SGE more usable for VFX houses.

This is far from finished and is currently undergoing a rewrite but has been successfully used at Prime Focus Film (London) to render in excess of 100,000 array jobs and probably between 10m and 20m individual tasks.

The WebUI uses Tornado.

##Install

This doesn't cover doing the actual SGE install but there are a couple of bits that need to be set up in order for these scripts to work.  Have a look at Sun/Oracle/whoever owns it this week's website for that.

##Queues

I've created queues called:

    farm.q
    testing.q

The testing.q points to my private code repo so I can test different prolog/epilog scripts before deploying them to the main farm.q directory.

and a parallel environment associated with all those queues called:

    pe1

This is used to allow jobs to request multiple slots on a machine

##Checkpointing

You need to create a checkpointing object with the following settings:
<table>
<tr><td>Name</td><td>relocate_on_suspend</td></tr>
<tr><td>Interface</td><td>USER_DEFINED</td></tr>
<tr><td>All commands</td><td>NONE</td></tr>
<tr><td>Checkpoint When</td><td>On Shutdown of Execd, On Job Suspend and On Reschedule</td></tr>
<tr><td>Checkpoint Signal</td><td>NONE</td></tr>
</table>
This needs to be added to the referenced checkpoint objects on all the queues
At the moment, gridsub submits all jobs with this checkpoint config.  Maybe that's bad.  Needs to be thought about more..

##Prolog and Epilog

As written in the scripts README, you'll need to add the prolog and epilog scripts to those queues

##Load Sensors

For workstation rendering, in the scripts folders you'll find logged_in.sh
In the cluster config, this must be added as a load sensor script for all the machines you want to use for desktop rendering.  It checks whether anyone's logged into X.
Add xlogin as a complex resource as follows:

    xlogin xlogin INT >= NO NO 0 0

Under the farm.q, add the desktop machines and set a suspend threshold of 1 for xlogin.  I've set the jobs suspended per interval to 30 because that's a higher number than we have cores in any of our machines.

##Other

Other SGE settings I've chosen to modify include:

* Setting up a share tree priority configuration for projects
* Set functional priority for individuals as follows:
    * enforce_user auto
    * auto_user_fshare 100
* Setting reschedule_unknown to 00:02:00 and max_unheard to 00:02:00
* Setting rerun jobs on farm.q (I'll probably set this on all queues)
* Create a project called no_project
* Set no_project as auto_user_default_project

Once SGE's set up...
Go through the steps in the db/README then webui/README and once you're done, use scripts/gridsub to submit stuff (as described in scripts/README)
