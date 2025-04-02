--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Homebrew)
-- Dumped by pg_dump version 17.0

-- Started on 2025-04-02 09:40:01 -03

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 6 (class 2615 OID 22098)
-- Name: heartbeat; Type: SCHEMA; Schema: -; Owner: felixmiranda
--

CREATE SCHEMA heartbeat;


ALTER SCHEMA heartbeat OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 212 (class 1259 OID 22126)
-- Name: appointment; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.appointment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid NOT NULL,
    date timestamp without time zone NOT NULL,
    professional character varying(255),
    procedure character varying(255),
    health_insurance character varying(255),
    insurance_plan character varying(255),
    external_guide_number character varying(50),
    registration_number character varying(50),
    requester character varying(255),
    observations text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE heartbeat.appointment OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 22205)
-- Name: custom_option; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.custom_option (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    category_id uuid NOT NULL,
    shortcut_key character varying(5) NOT NULL,
    text text NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE heartbeat.custom_option OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 22190)
-- Name: custom_option_category; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.custom_option_category (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    order_index integer DEFAULT 0 NOT NULL
);


ALTER TABLE heartbeat.custom_option_category OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 22267)
-- Name: measurement_type; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.measurement_type (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    unit character varying(20) NOT NULL,
    is_calculated boolean DEFAULT false,
    reference_min numeric(10,2),
    reference_max numeric(10,2),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT measurement_type_unit_check CHECK (((unit)::text = ANY ((ARRAY['mm'::character varying, 'cm'::character varying, 'ml'::character varying, 'ml/m²'::character varying, 'mm/m²'::character varying, 'mm/m'::character varying, 'g'::character varying, 'g/m²'::character varying, 'g/m'::character varying, '%'::character varying, 'L/min'::character varying, '-'::character varying])::text[])))
);


ALTER TABLE heartbeat.measurement_type OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 22115)
-- Name: patient; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.patient (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    birth_date date NOT NULL,
    gender character varying(10) NOT NULL,
    social_name character varying(255),
    height numeric(5,2),
    weight numeric(5,2),
    cpf character(11),
    contact text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT patient_gender_check CHECK (((gender)::text = ANY ((ARRAY['male'::character varying, 'female'::character varying, 'other'::character varying])::text[])))
);


ALTER TABLE heartbeat.patient OWNER TO postgres;

--
-- TOC entry 213 (class 1259 OID 22141)
-- Name: report; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.report (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    appointment_id uuid NOT NULL,
    patient_id uuid NOT NULL,
    pdf_path text,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT report_status_check CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'finalized'::character varying])::text[])))
);


ALTER TABLE heartbeat.report OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 22175)
-- Name: report_block; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.report_block (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    report_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    order_index integer NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE heartbeat.report_block OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 22282)
-- Name: report_measurement; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.report_measurement (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    report_id uuid NOT NULL,
    measurement_type_id uuid NOT NULL,
    value numeric(10,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE heartbeat.report_measurement OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 22220)
-- Name: sync_log; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat.sync_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    action character varying(50),
    entity character varying(50),
    entity_id uuid,
    "timestamp" timestamp without time zone DEFAULT now(),
    status character varying(20),
    error_message text,
    CONSTRAINT sync_log_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'success'::character varying, 'error'::character varying])::text[])))
);


ALTER TABLE heartbeat.sync_log OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 22099)
-- Name: user; Type: TABLE; Schema: heartbeat; Owner: felixmiranda
--

CREATE TABLE heartbeat."user" (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    cpf character(11) NOT NULL,
    phone character varying(15) NOT NULL,
    email character varying(255),
    password character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE heartbeat."user" OWNER TO postgres;

--
-- TOC entry 3580 (class 2606 OID 22135)
-- Name: appointment appointment_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.appointment
    ADD CONSTRAINT appointment_pkey PRIMARY KEY (id);


--
-- TOC entry 3586 (class 2606 OID 22199)
-- Name: custom_option_category custom_option_category_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.custom_option_category
    ADD CONSTRAINT custom_option_category_pkey PRIMARY KEY (id);


--
-- TOC entry 3588 (class 2606 OID 22214)
-- Name: custom_option custom_option_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.custom_option
    ADD CONSTRAINT custom_option_pkey PRIMARY KEY (id);


--
-- TOC entry 3592 (class 2606 OID 22280)
-- Name: measurement_type measurement_type_name_key; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.measurement_type
    ADD CONSTRAINT measurement_type_name_key UNIQUE (name);


--
-- TOC entry 3594 (class 2606 OID 22278)
-- Name: measurement_type measurement_type_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.measurement_type
    ADD CONSTRAINT measurement_type_pkey PRIMARY KEY (id);


--
-- TOC entry 3578 (class 2606 OID 22125)
-- Name: patient patient_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.patient
    ADD CONSTRAINT patient_pkey PRIMARY KEY (id);


--
-- TOC entry 3584 (class 2606 OID 22184)
-- Name: report_block report_block_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.report_block
    ADD CONSTRAINT report_block_pkey PRIMARY KEY (id);


--
-- TOC entry 3596 (class 2606 OID 22289)
-- Name: report_measurement report_measurement_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.report_measurement
    ADD CONSTRAINT report_measurement_pkey PRIMARY KEY (id);


--
-- TOC entry 3582 (class 2606 OID 22151)
-- Name: report report_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.report
    ADD CONSTRAINT report_pkey PRIMARY KEY (id);


--
-- TOC entry 3590 (class 2606 OID 22229)
-- Name: sync_log sync_log_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.sync_log
    ADD CONSTRAINT sync_log_pkey PRIMARY KEY (id);


--
-- TOC entry 3570 (class 2606 OID 22110)
-- Name: user user_cpf_key; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat."user"
    ADD CONSTRAINT user_cpf_key UNIQUE (cpf);


--
-- TOC entry 3572 (class 2606 OID 22114)
-- Name: user user_email_key; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- TOC entry 3574 (class 2606 OID 22112)
-- Name: user user_phone_key; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat."user"
    ADD CONSTRAINT user_phone_key UNIQUE (phone);


--
-- TOC entry 3576 (class 2606 OID 22108)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 3597 (class 2606 OID 22136)
-- Name: appointment appointment_patient_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.appointment
    ADD CONSTRAINT appointment_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES heartbeat.patient(id) ON DELETE CASCADE;


--
-- TOC entry 3602 (class 2606 OID 22215)
-- Name: custom_option custom_option_category_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.custom_option
    ADD CONSTRAINT custom_option_category_id_fkey FOREIGN KEY (category_id) REFERENCES heartbeat.custom_option_category(id) ON DELETE CASCADE;


--
-- TOC entry 3601 (class 2606 OID 22200)
-- Name: custom_option_category custom_option_category_user_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.custom_option_category
    ADD CONSTRAINT custom_option_category_user_id_fkey FOREIGN KEY (user_id) REFERENCES heartbeat."user"(id) ON DELETE CASCADE;


--
-- TOC entry 3598 (class 2606 OID 22152)
-- Name: report report_appointment_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.report
    ADD CONSTRAINT report_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES heartbeat.appointment(id) ON DELETE CASCADE;


--
-- TOC entry 3600 (class 2606 OID 22185)
-- Name: report_block report_block_report_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.report_block
    ADD CONSTRAINT report_block_report_id_fkey FOREIGN KEY (report_id) REFERENCES heartbeat.report(id) ON DELETE CASCADE;


--
-- TOC entry 3604 (class 2606 OID 22295)
-- Name: report_measurement report_measurement_measurement_type_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.report_measurement
    ADD CONSTRAINT report_measurement_measurement_type_id_fkey FOREIGN KEY (measurement_type_id) REFERENCES heartbeat.measurement_type(id) ON DELETE CASCADE;


--
-- TOC entry 3605 (class 2606 OID 22290)
-- Name: report_measurement report_measurement_report_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.report_measurement
    ADD CONSTRAINT report_measurement_report_id_fkey FOREIGN KEY (report_id) REFERENCES heartbeat.report(id) ON DELETE CASCADE;


--
-- TOC entry 3599 (class 2606 OID 22157)
-- Name: report report_patient_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.report
    ADD CONSTRAINT report_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES heartbeat.patient(id) ON DELETE CASCADE;


--
-- TOC entry 3603 (class 2606 OID 22230)
-- Name: sync_log sync_log_user_id_fkey; Type: FK CONSTRAINT; Schema: heartbeat; Owner: felixmiranda
--

ALTER TABLE ONLY heartbeat.sync_log
    ADD CONSTRAINT sync_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES heartbeat."user"(id) ON DELETE CASCADE;


-- Completed on 2025-04-02 09:40:01 -03

--
-- PostgreSQL database dump complete
--
