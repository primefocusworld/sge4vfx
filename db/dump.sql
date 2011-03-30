--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'LATIN1';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: sgedb; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE sgedb IS 'GridEngine tracking database';


--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: postgres
--

CREATE PROCEDURAL LANGUAGE plpgsql;


ALTER PROCEDURAL LANGUAGE plpgsql OWNER TO postgres;

SET search_path = public, pg_catalog;

--
-- Name: create_tasks(); Type: FUNCTION; Schema: public; Owner: sge
--

CREATE FUNCTION create_tasks() RETURNS trigger
    LANGUAGE plpgsql
    AS $$    DECLARE
        -- Use the task range to create task entries in the task table
        counter INTEGER = NEW.firsttask;
        last INTEGER = NEW.lasttask;
    BEGIN
        WHILE counter <= last LOOP
            INSERT INTO tasks (sgeid, taskno, starttime, endtime, attempts, returncode, rhost)
            VALUES (NEW.sgeid, counter, NULL, NULL, 0, NULL, NULL);
            counter := counter + 1;
        END LOOP;
        RETURN NEW;
    END;
$$;


ALTER FUNCTION public.create_tasks() OWNER TO sge;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: job_extras; Type: TABLE; Schema: public; Owner: sge; Tablespace: 
--

CREATE TABLE job_extras (
    sgeid integer NOT NULL,
    key character varying(32) NOT NULL,
    value character varying(128)
);


ALTER TABLE public.job_extras OWNER TO sge;

--
-- Name: TABLE job_extras; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON TABLE job_extras IS 'Additional information per job';


--
-- Name: COLUMN job_extras.sgeid; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN job_extras.sgeid IS 'Foreign key into jobs table';


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: sge; Tablespace: 
--

CREATE TABLE jobs (
    sgeid integer NOT NULL,
    jobname character varying(128) NOT NULL,
    username character varying(16) NOT NULL,
    project character varying(16),
    priority real,
    submittime timestamp without time zone NOT NULL,
    starttime timestamp without time zone,
    endtime timestamp without time zone,
    firsttask integer NOT NULL,
    lasttask integer NOT NULL,
    chunk integer NOT NULL,
    status smallint NOT NULL,
    submissionscript character varying(256) NOT NULL,
    donetasks integer DEFAULT 0 NOT NULL,
    stdout character varying(128),
    stderr character varying(128)
);


ALTER TABLE public.jobs OWNER TO sge;

--
-- Name: COLUMN jobs.sgeid; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.sgeid IS 'SGEs ID for the job';


--
-- Name: COLUMN jobs.jobname; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.jobname IS 'User given name for job';


--
-- Name: COLUMN jobs.username; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.username IS 'Username';


--
-- Name: COLUMN jobs.project; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.project IS 'Show or project';


--
-- Name: COLUMN jobs.priority; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.priority IS 'Job Priority';


--
-- Name: COLUMN jobs.submittime; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.submittime IS 'Time the job was actually submitted';


--
-- Name: COLUMN jobs.starttime; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.starttime IS 'Filled in by pre-script of first task';


--
-- Name: COLUMN jobs.endtime; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.endtime IS 'Filled in by a post script';


--
-- Name: COLUMN jobs.firsttask; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.firsttask IS 'Usually first frame';


--
-- Name: COLUMN jobs.lasttask; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.lasttask IS 'Usually last frame';


--
-- Name: COLUMN jobs.chunk; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.chunk IS 'Batch or chunk size';


--
-- Name: COLUMN jobs.status; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.status IS 'Integer based status code';


--
-- Name: COLUMN jobs.submissionscript; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.submissionscript IS 'Path to the qsub submission script';


--
-- Name: COLUMN jobs.donetasks; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.donetasks IS 'How many tasks have been completed';


--
-- Name: COLUMN jobs.stdout; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.stdout IS 'Stdout log location with task ID stripped';


--
-- Name: COLUMN jobs.stderr; Type: COMMENT; Schema: public; Owner: sge
--

COMMENT ON COLUMN jobs.stderr IS 'Stderr log location with task ID stripped';


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tasks (
    sgeid integer NOT NULL,
    taskno integer NOT NULL,
    starttime timestamp without time zone,
    endtime timestamp without time zone,
    attempts smallint NOT NULL,
    returncode smallint,
    rhost character varying(32)
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: COLUMN tasks.returncode; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN tasks.returncode IS 'Return code from task command';


--
-- Name: COLUMN tasks.rhost; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN tasks.rhost IS 'The renderbox the task last ran on';


--
-- Name: job_extras_pkey; Type: CONSTRAINT; Schema: public; Owner: sge; Tablespace: 
--

ALTER TABLE ONLY job_extras
    ADD CONSTRAINT job_extras_pkey PRIMARY KEY (sgeid, key);


--
-- Name: jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: sge; Tablespace: 
--

ALTER TABLE ONLY jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (sgeid);


--
-- Name: tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (sgeid, taskno);


--
-- Name: project; Type: INDEX; Schema: public; Owner: sge; Tablespace: 
--

CREATE INDEX project ON jobs USING btree (project);


--
-- Name: status; Type: INDEX; Schema: public; Owner: sge; Tablespace: 
--

CREATE INDEX status ON jobs USING btree (status);


--
-- Name: username; Type: INDEX; Schema: public; Owner: sge; Tablespace: 
--

CREATE INDEX username ON jobs USING btree (username);


--
-- Name: create_tasks; Type: TRIGGER; Schema: public; Owner: sge
--

CREATE TRIGGER create_tasks
    AFTER INSERT ON jobs
    FOR EACH ROW
    EXECUTE PROCEDURE create_tasks();


--
-- Name: job_extras_sgeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sge
--

ALTER TABLE ONLY job_extras
    ADD CONSTRAINT job_extras_sgeid_fkey FOREIGN KEY (sgeid) REFERENCES jobs(sgeid) ON DELETE CASCADE;


--
-- Name: sgeid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tasks
    ADD CONSTRAINT sgeid FOREIGN KEY (sgeid) REFERENCES jobs(sgeid) ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: jobs; Type: ACL; Schema: public; Owner: sge
--

REVOKE ALL ON TABLE jobs FROM PUBLIC;
REVOKE ALL ON TABLE jobs FROM sge;
GRANT ALL ON TABLE jobs TO sge;
GRANT ALL ON TABLE jobs TO postgres;


--
-- Name: tasks; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE tasks FROM PUBLIC;
REVOKE ALL ON TABLE tasks FROM postgres;
GRANT ALL ON TABLE tasks TO postgres;
GRANT ALL ON TABLE tasks TO sge;


--
-- PostgreSQL database dump complete
--

