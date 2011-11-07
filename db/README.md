#DB Setup

##Postgres

I've gone with a Postgres database using the postgres 8.4 RPMs for CentOS
In this directory you'll find the structure dump.  I'm very very new to postgres and I'm pretty sure I'm making bad choices when it comes to priveleges and perms hence the TODO

1. Create a passwordless user called 'sge'
2. Create a db called 'sgedb'
3. Apply the dump script

You'll need the psql client on your workstations and renderboxes

This I really know almost nothing about so if someone can help here it'd be much
appreciated.

##Table Descriptions

* jobs contains what SGE calls jobs.  They're made up of tasks.  The task table is populated when a job is created.
* tasks contains what SGE calls tasks from array jobs.  This table has a foreign key constraint against the Jobs table so when the job is removed, all tasks are deleted.
* job_Extras contains key/value pairs that can be used to record extra information useful for a job.  This is currently used for output_path information and e-mail notification.

##TODO

Sort out permissions/priveleges/users/pg_hba stuff
