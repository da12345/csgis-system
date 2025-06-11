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

--
-- Data for Name: age_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.age_groups (id, age_group) FROM stdin;
1	18-30
2	31-45
3	46-60
4	61-79
5	80+
\.


--
-- Data for Name: parameters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.parameters (id, short_name) FROM stdin;
1	personal_connection
2	sense_of_belonging
3	openness_and_accessibility
4	meet_share_connect
5	well_designed_for_activities
6	involvement_inspiration
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.questions (id, short_name) FROM stdin;
\.


--
-- Name: age_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.age_groups_id_seq', 5, true);


--
-- Name: parameters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.parameters_id_seq', 6, true);


--
-- Name: questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.questions_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

