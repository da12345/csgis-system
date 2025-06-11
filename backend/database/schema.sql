--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: age_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.age_groups (
    id integer NOT NULL,
    age_group character varying(10) NOT NULL
);


--
-- Name: age_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.age_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: age_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.age_groups_id_seq OWNED BY public.age_groups.id;


--
-- Name: combined_sentiment_analysis; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.combined_sentiment_analysis (
    location_id uuid NOT NULL,
    combined_response text,
    distilbert_sentiment text,
    vader_sentiment text,
    textblob_sentiment jsonb,
    goemotions_sentiment text,
    textblob_sentiment_label character varying,
    roberta_sentiment text,
    bert_sentiment text,
    distilbert_ekman_sentiment text,
    roberta_ekman_sentiment text,
    bert_ekman_sentiment text
);


--
-- Name: free_text_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.free_text_responses (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    location_id uuid,
    question_id integer,
    free_text_response text,
    textblob_sentiment jsonb,
    textblob_sentiment_label character varying,
    vader_sentiment text
);


--
-- Name: free_text_responses_new_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.free_text_responses_new_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: free_text_responses_new_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.free_text_responses_new_id_seq OWNED BY public.free_text_responses.id;


--
-- Name: image_analysis; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.image_analysis (
    location_id uuid NOT NULL,
    image_name text,
    deeplab_gvi numeric(5,2),
    mask2former_gvi numeric(5,2),
    segformer_gvi numeric
);


--
-- Name: location_likert_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.location_likert_stats (
    location_id uuid NOT NULL,
    avg_likert numeric(4,2),
    min_likert smallint,
    max_likert smallint,
    stddev_likert numeric(5,3),
    num_answers integer
);


--
-- Name: locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    date_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    x_coordinate double precision NOT NULL,
    y_coordinate double precision NOT NULL,
    image text,
    email character varying(255),
    agreed boolean DEFAULT false,
    age_group_id integer,
    gender public.gender_enum,
    geom public.geometry(Point,4326),
    user_id text,
    num_trees integer,
    num_cars integer,
    scene_type text,
    actual_scene_type text
);


--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: parameter_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parameter_responses (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    location_id uuid NOT NULL,
    parameter_id integer NOT NULL,
    likert_value smallint,
    CONSTRAINT parameter_responses_likert_value_check CHECK (((likert_value >= 1) AND (likert_value <= 5)))
);


--
-- Name: parameter_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.parameter_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: parameter_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.parameter_responses_id_seq OWNED BY public.parameter_responses.id;


--
-- Name: parameters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parameters (
    id integer NOT NULL,
    short_name character varying(100) NOT NULL
);


--
-- Name: parameters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.parameters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: parameters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.parameters_id_seq OWNED BY public.parameters.id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.questions (
    id integer NOT NULL,
    short_name character varying(50) NOT NULL
);


--
-- Name: questions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.questions_id_seq OWNED BY public.questions.id;


--
-- Name: age_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_groups ALTER COLUMN id SET DEFAULT nextval('public.age_groups_id_seq'::regclass);


--
-- Name: parameters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parameters ALTER COLUMN id SET DEFAULT nextval('public.parameters_id_seq'::regclass);


--
-- Name: questions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions ALTER COLUMN id SET DEFAULT nextval('public.questions_id_seq'::regclass);


--
-- Name: age_groups age_groups_age_group_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_groups
    ADD CONSTRAINT age_groups_age_group_key UNIQUE (age_group);


--
-- Name: age_groups age_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_groups
    ADD CONSTRAINT age_groups_pkey PRIMARY KEY (id);


--
-- Name: free_text_responses free_text_responses_new_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.free_text_responses
    ADD CONSTRAINT free_text_responses_new_pkey PRIMARY KEY (id);


--
-- Name: image_analysis image_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.image_analysis
    ADD CONSTRAINT image_analysis_pkey PRIMARY KEY (location_id);


--
-- Name: location_likert_stats location_likert_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_likert_stats
    ADD CONSTRAINT location_likert_stats_pkey PRIMARY KEY (location_id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: parameters parameters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parameters
    ADD CONSTRAINT parameters_pkey PRIMARY KEY (id);


--
-- Name: combined_sentiment_analysis pk_combined_sentiment_location; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.combined_sentiment_analysis
    ADD CONSTRAINT pk_combined_sentiment_location PRIMARY KEY (location_id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id);


--
-- Name: questions questions_short_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_short_name_key UNIQUE (short_name);


--
-- Name: parameter_responses unique_location_parameter; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parameter_responses
    ADD CONSTRAINT unique_location_parameter UNIQUE (location_id, parameter_id);


--
-- Name: parameters unique_parameter_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parameters
    ADD CONSTRAINT unique_parameter_name UNIQUE (short_name);


--
-- Name: idx_free_text_responses_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_free_text_responses_location_id ON public.free_text_responses USING btree (location_id);


--
-- Name: idx_locations_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_locations_geom ON public.locations USING gist (geom);


--
-- Name: idx_locations_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_locations_user_id ON public.locations USING btree (user_id);


--
-- Name: idx_parameter_responses_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_parameter_responses_location_id ON public.parameter_responses USING btree (location_id);


--
-- Name: idx_parameters_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_parameters_name ON public.parameters USING btree (short_name);


--
-- Name: combined_sentiment_analysis combined_sentiment_analysis_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.combined_sentiment_analysis
    ADD CONSTRAINT combined_sentiment_analysis_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: free_text_responses free_text_responses_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.free_text_responses
    ADD CONSTRAINT free_text_responses_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: image_analysis image_analysis_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.image_analysis
    ADD CONSTRAINT image_analysis_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: location_likert_stats location_likert_stats_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_likert_stats
    ADD CONSTRAINT location_likert_stats_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: locations locations_age_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_age_group_id_fkey FOREIGN KEY (age_group_id) REFERENCES public.age_groups(id);


--
-- Name: parameter_responses parameter_responses_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parameter_responses
    ADD CONSTRAINT parameter_responses_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: parameter_responses parameter_responses_parameter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parameter_responses
    ADD CONSTRAINT parameter_responses_parameter_id_fkey FOREIGN KEY (parameter_id) REFERENCES public.parameters(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

