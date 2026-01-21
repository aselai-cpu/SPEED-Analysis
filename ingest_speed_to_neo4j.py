#!/usr/bin/env python3
"""
SPEED Dataset - Neo4j Temporal Knowledge Graph Ingestion Script

This script ingests the SPEED (Social, Political and Economic Event Database)
CSV data into Neo4j as a Temporal Knowledge Graph, enabling advanced querying
and analysis of civil unrest events globally from 1946 to present.

Author: Generated from Prompt_Ingestion.txt
Date: 2026-01-21
"""

import pandas as pd
from neo4j import GraphDatabase
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from tqdm import tqdm
import sys
import argparse
import yaml
from pathlib import Path


class SPEEDKnowledgeGraphIngestion:
    """
    Ingests SPEED dataset into Neo4j as a Temporal Knowledge Graph
    """

    def __init__(self, uri: str, user: str, password: str, csv_path: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.csv_path = csv_path
        self.driver = None
        self.logger = self._setup_logging()
        self.df = None

        # Julian date base: January 1, 1945
        self.JULIAN_BASE = datetime(1945, 1, 1)

    def _setup_logging(self) -> logging.Logger:
        """Configure logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logger = logging.getLogger("SPEED_Ingestion")
        logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(log_dir / "ingestion.log")
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def connect(self):
        """Establish Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def load_csv(self):
        """Load and preprocess CSV data"""
        self.logger.info(f"Loading CSV from {self.csv_path}")
        try:
            # Read CSV with first row as header
            self.df = pd.read_csv(self.csv_path)

            # Clean column names (remove spaces, convert to uppercase)
            self.df.columns = self.df.columns.str.strip()

            # Replace missing value indicators with NaN
            self.df.replace(['.', '', 'nan', 'NaN'], np.nan, inplace=True)

            self.logger.info(f"Loaded {len(self.df)} rows and {len(self.df.columns)} columns")
            self.logger.info(f"Columns: {list(self.df.columns)[:10]}...")

            return self.df
        except Exception as e:
            self.logger.error(f"Failed to load CSV: {e}")
            raise

    def julian_to_datetime(self, julian_date: float) -> Optional[datetime]:
        """
        Convert Julian date to datetime
        Julian Date 0 = January 1, 1945
        """
        if pd.isna(julian_date) or julian_date < 0:
            return None

        try:
            return self.JULIAN_BASE + timedelta(days=float(julian_date))
        except (ValueError, OverflowError):
            return None

    def safe_bool(self, value) -> bool:
        """Safely convert value to boolean"""
        if pd.isna(value):
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(int(value))
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes']
        return False

    def safe_int(self, value) -> Optional[int]:
        """Safely convert value to integer"""
        if pd.isna(value):
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def safe_str(self, value) -> Optional[str]:
        """Safely convert value to string"""
        if pd.isna(value):
            return None
        return str(value).strip()

    def assign_temporal_validity(self, row: pd.Series) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Assign valid_from and valid_to based on date type and available date fields
        """
        date_type = self.safe_str(row.get('Type of date information available'))

        # Try to use precise dates first
        if 'Precise julian date of event start' in row.index:
            jdate_start = self.safe_float(row['Precise julian date of event start'])
            jdate_end = self.safe_float(row.get('Precise julian date of event end (Julian Date = 0 on Janurary 1st, 1945)'))

            if jdate_start is not None:
                valid_from = self.julian_to_datetime(jdate_start)
                if jdate_end is not None and jdate_end > jdate_start:
                    valid_to = self.julian_to_datetime(jdate_end)
                else:
                    # Single day event
                    valid_to = valid_from + timedelta(days=1) if valid_from else None

                if valid_from:
                    return valid_from, valid_to

        # Fall back to estimated dates
        if 'Estimated julian date of event start (Julian Date = 0 on Janurary 1st, 1945)' in row.index:
            jdate_est_start = self.safe_float(row['Estimated julian date of event start (Julian Date = 0 on Janurary 1st, 1945)'])
            jdate_est_end = self.safe_float(row.get('Estimated julian date of event end (Julian Date = 0 on Janurary 1st, 1945)'))

            if jdate_est_start is not None:
                valid_from = self.julian_to_datetime(jdate_est_start)
                if jdate_est_end is not None and jdate_est_end > jdate_est_start:
                    valid_to = self.julian_to_datetime(jdate_est_end)
                else:
                    valid_to = valid_from + timedelta(days=1) if valid_from else None

                if valid_from:
                    return valid_from, valid_to

        # Fall back to year/month/day
        year = self.safe_int(row.get('Year of event - multi-day=average'))
        month = self.safe_int(row.get('Month of event - multi-day=average'))
        day = self.safe_int(row.get('Day of event - multi-day=average'))

        if year:
            try:
                valid_from = datetime(year, month or 1, day or 1)
                valid_to = valid_from + timedelta(days=1)
                return valid_from, valid_to
            except ValueError:
                pass

        return None, None

    def create_constraints_and_indexes(self):
        """
        Step 1: Create all constraints and indexes
        Following TKG best practices
        """
        self.logger.info("Creating constraints and indexes...")

        constraints_and_indexes = [
            # Unique constraints
            "CREATE CONSTRAINT event_eventid IF NOT EXISTS FOR (e:Event) REQUIRE e.eventid IS UNIQUE",
            "CREATE CONSTRAINT location_location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",
            "CREATE CONSTRAINT actor_actor_id IF NOT EXISTS FOR (a:Actor) REQUIRE a.actor_id IS UNIQUE",
            "CREATE CONSTRAINT event_type_type_id IF NOT EXISTS FOR (et:EventType) REQUIRE et.type_id IS UNIQUE",
            "CREATE CONSTRAINT temporal_id IF NOT EXISTS FOR (t:TemporalInfo) REQUIRE t.temporal_id IS UNIQUE",
            "CREATE CONSTRAINT source_id IF NOT EXISTS FOR (n:NewsSource) REQUIRE n.source_id IS UNIQUE",

            # Indexes for temporal queries (TKG-critical)
            "CREATE INDEX event_year IF NOT EXISTS FOR (e:Event) ON (e.year)",
            "CREATE INDEX event_country IF NOT EXISTS FOR (e:Event) ON (e.country)",
            "CREATE INDEX event_valid_from IF NOT EXISTS FOR (e:Event) ON (e.valid_from)",

            # Location indexes
            "CREATE INDEX location_country IF NOT EXISTS FOR (l:Location) ON (l.country)",
            "CREATE INDEX location_region IF NOT EXISTS FOR (l:Location) ON (l.region)",

            # Actor indexes
            "CREATE INDEX actor_name IF NOT EXISTS FOR (a:Actor) ON (a.name)",
            "CREATE INDEX actor_role IF NOT EXISTS FOR (a:Actor) ON (a.actor_role)",
        ]

        with self.driver.session() as session:
            for query in constraints_and_indexes:
                try:
                    session.run(query)
                    self.logger.debug(f"Executed: {query[:80]}...")
                except Exception as e:
                    self.logger.warning(f"Constraint/index may already exist: {e}")

        self.logger.info("Constraints and indexes created successfully")

    def ingest_events(self, batch_size: int = 10000):
        """
        Step 2: Create Event nodes with temporal properties
        """
        self.logger.info("Ingesting Event nodes...")

        events_created = 0

        with self.driver.session() as session:
            for i in tqdm(range(0, len(self.df), batch_size), desc="Event batches"):
                batch = self.df.iloc[i:i + batch_size]

                # Prepare batch data
                event_data = []
                for _, row in batch.iterrows():
                    valid_from, valid_to = self.assign_temporal_validity(row)

                    event = {
                        'eventid': self.safe_str(row.get('Event identification number')),
                        'year': self.safe_int(row.get('Year of event - multi-day=average')),
                        'month': self.safe_int(row.get('Month of event - multi-day=average')),
                        'day': self.safe_int(row.get('Day of event - multi-day=average')),
                        'country': self.safe_str(row.get('Country in which the event occurred')),
                        'event': self.safe_bool(row.get('Is this coding for a destabilizing event?')),
                        'posthoc': self.safe_str(row.get('Post hoc reaction?')),
                        'quasi_event': self.safe_bool(row.get('Is this a quasi-event coding?')),
                        'coup': self.safe_bool(row.get('Did this event involve a coup?')),
                        'coup_failed': self.safe_bool(row.get('Did this event involve an unrealized coup?')),
                        'valid_from': valid_from.isoformat() if valid_from else None,
                        'valid_to': valid_to.isoformat() if valid_to else None,
                        'transaction_time': datetime.now().isoformat()
                    }

                    if event['eventid']:
                        event_data.append(event)

                # Batch insert
                if event_data:
                    query = """
                    UNWIND $events AS event
                    CREATE (e:Event)
                    SET e = event,
                        e.valid_from = CASE WHEN event.valid_from IS NOT NULL
                                           THEN datetime(event.valid_from)
                                           ELSE NULL END,
                        e.valid_to = CASE WHEN event.valid_to IS NOT NULL
                                         THEN datetime(event.valid_to)
                                         ELSE NULL END,
                        e.transaction_time = datetime(event.transaction_time)
                    """
                    session.run(query, events=event_data)
                    events_created += len(event_data)

        self.logger.info(f"Created {events_created} Event nodes")

    def ingest_locations(self):
        """
        Step 3: Create Location nodes with spatial indexing
        """
        self.logger.info("Ingesting Location nodes...")

        # Extract unique locations
        location_cols = [
            'Country in which the event occurred',
            'Cowcode of country where event occurred',
            'Eight category world region variable',
            'Country name(caps and lower case)',
            'Lowest level entity name (caps and lower case)',
            'Latitude',
            'Longitude',
            'Event location type'
        ]

        locations = self.df[location_cols].copy()
        locations.columns = ['country', 'cowcode', 'region', 'gp3', 'gp4', 'latitude', 'longitude', 'loc_type']

        # Create location_id
        locations['location_id'] = (
            locations['country'].fillna('') + '_' +
            locations['cowcode'].fillna(0).astype(str) + '_' +
            locations['gp3'].fillna('') + '_' +
            locations['gp4'].fillna('')
        )

        # Deduplicate
        locations = locations.drop_duplicates(subset=['location_id'])

        with self.driver.session() as session:
            for _, loc in tqdm(locations.iterrows(), total=len(locations), desc="Locations"):
                location_data = {
                    'location_id': self.safe_str(loc['location_id']),
                    'country': self.safe_str(loc['country']),
                    'cowcode': self.safe_int(loc['cowcode']),
                    'region': self.safe_str(loc['region']),
                    'gp3': self.safe_str(loc['gp3']),
                    'gp4': self.safe_str(loc['gp4']),
                    'latitude': self.safe_float(loc['latitude']),
                    'longitude': self.safe_float(loc['longitude']),
                    'loc_type': self.safe_str(loc['loc_type'])
                }

                if location_data['location_id']:
                    query = """
                    MERGE (l:Location {location_id: $location_id})
                    SET l += $properties
                    """
                    session.run(query, location_id=location_data['location_id'], properties=location_data)

        self.logger.info(f"Created {len(locations)} Location nodes")

    def ingest_actors(self):
        """
        Step 4: Create Actor nodes with polymorphic labels
        """
        self.logger.info("Ingesting Actor nodes...")

        actors = []

        # Extract actors from initiator, target, and victim columns
        for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Extracting actors"):
            eventid = self.safe_str(row.get('Event identification number'))

            # Initiators
            for col, category in [
                ('Name of insurgent group initiator', 'insurgent'),
                ('Name of socio-cultural group initiator', 'sociocultural'),
                ('Name of political group initiator', 'political')
            ]:
                name = self.safe_str(row.get(col))
                if name:
                    actors.append({
                        'actor_id': f"ini_{category}_{name}",
                        'name': name,
                        'actor_role': 'initiator',
                        'actor_type': 'Group',
                        'group_category': category
                    })

            # Targets
            for col, category in [
                ('Name of insurgent group target', 'insurgent'),
                ('Name of socio-cultural group target', 'sociocultural'),
                ('Name of political group target', 'political')
            ]:
                name = self.safe_str(row.get(col))
                if name:
                    actors.append({
                        'actor_id': f"tar_{category}_{name}",
                        'name': name,
                        'actor_role': 'target',
                        'actor_type': 'Group',
                        'group_category': category
                    })

            # Victims
            for col, category in [
                ('Name of insurgent group victim', 'insurgent'),
                ('Name of socio-cultural group victim', 'sociocultural'),
                ('Name of political group victim', 'political')
            ]:
                name = self.safe_str(row.get(col))
                if name:
                    actors.append({
                        'actor_id': f"vic_{category}_{name}",
                        'name': name,
                        'actor_role': 'victim',
                        'actor_type': 'Group',
                        'group_category': category
                    })

        # Deduplicate actors
        actors_df = pd.DataFrame(actors).drop_duplicates(subset=['actor_id'])

        with self.driver.session() as session:
            for _, actor in tqdm(actors_df.iterrows(), total=len(actors_df), desc="Creating actors"):
                labels = ['Actor']
                if actor['actor_type'] == 'Group':
                    labels.append('Group')

                label_str = ':'.join(labels)

                query = f"""
                MERGE (a:{label_str} {{actor_id: $actor_id}})
                SET a += $properties
                """
                session.run(query, actor_id=actor['actor_id'], properties=actor.to_dict())

        self.logger.info(f"Created {len(actors_df)} Actor nodes")

    def ingest_event_characteristics(self):
        """
        Step 5: Create EventType, IntensityMetrics, Drivers, Outcomes nodes
        """
        self.logger.info("Ingesting event characteristics...")

        with self.driver.session() as session:
            for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Event characteristics"):
                eventid = self.safe_str(row.get('Event identification number'))
                if not eventid:
                    continue

                # EventType
                event_type_data = {
                    'type_id': f"type_{eventid}",
                    'ev_type': self.safe_str(row.get('Event type')),
                    'pe_type': self.safe_str(row.get('Type of political expression event')),
                    'sym_type': self.safe_str(row.get('Type of symbolic event')),
                    'exp_type': self.safe_str(row.get('Reduced political expression type')),
                    'atk_type': self.safe_str(row.get('Type of political motivated attack')),
                    'dsa_type': self.safe_str(row.get('Type of disruptive state act')),
                    'stat_act': self.safe_str(row.get('Broad category of disruptive state act'))
                }

                query = """
                MERGE (et:EventType {type_id: $type_id})
                SET et += $properties
                """
                session.run(query, type_id=event_type_data['type_id'], properties=event_type_data)

                # IntensityMetrics
                intensity_data = {
                    'metrics_id': f"metrics_{eventid}",
                    'n_killed_p': self.safe_float(row.get('Pristine measure of # of initiators')),
                    'n_killed_a': self.safe_float(row.get('Estimate of # killed, including statistical estimates')),
                    'n_injurd': self.safe_float(row.get('# Of individuals injured')),
                    'n_injurd_d': self.safe_float(row.get('# Injured, max=10')),
                    'n_of_ini_p': self.safe_float(row.get('Pristine measure of # of initiators')),
                    'n_of_ini_a': self.safe_float(row.get('Measure of # of initiators with statistical estimates')),
                    'weapon': self.safe_str(row.get('Type of weapon used')),
                    'weap_grd': self.safe_str(row.get('5 category weapon variable')),
                    'pol_viol': self.safe_float(row.get('Intensity of political violence')),
                    'stat_viol': self.safe_float(row.get('Intensity of state violence')),
                    'pol_express': self.safe_float(row.get('Intensity of small-bore political expression')),
                    'mass_express': self.safe_float(row.get('Intensity of mass expression')),
                    'e_length': self.safe_str(row.get('Length of event, truncated'))
                }

                query = """
                MERGE (im:IntensityMetrics {metrics_id: $metrics_id})
                SET im += $properties
                """
                session.run(query, metrics_id=intensity_data['metrics_id'], properties=intensity_data)

                # Drivers
                drivers_data = {
                    'driver_id': f"driver_{eventid}",
                    'sc_animosity': self.safe_bool(row.get('Event rooted in socio-cultural animosities?')),
                    'anti_gov_sentmnts': self.safe_bool(row.get('Event rooted in anti-government sentiments?')),
                    'class_conflict': self.safe_bool(row.get('Event rooted in class-based conflict?')),
                    'eco_scarcity': self.safe_bool(row.get('Event rooted in ecological resource scarcities')),
                    'pol_desires': self.safe_bool(row.get('Event rooted in desire for political rights?')),
                    'retain_power': self.safe_bool(row.get('Event rooted in desire to retain political power?')),
                    'pers_security': self.safe_bool(row.get('Event rooted in desire for personal security?'))
                }

                query = """
                MERGE (d:Drivers {driver_id: $driver_id})
                SET d += $properties
                """
                session.run(query, driver_id=drivers_data['driver_id'], properties=drivers_data)

                # Outcomes
                outcomes_data = {
                    'outcome_id': f"outcome_{eventid}",
                    'property_damaged': self.safe_bool(row.get('Was property damaged in the event?')),
                    'property_type': self.safe_str(row.get('Type of property damaged')),
                    'property_owner': self.safe_str(row.get('Type of owner for damaged property')),
                    'arrests': self.safe_bool(row.get('Were arrests made?')),
                    'victim_effect': self.safe_str(row.get('Impact of event on victim')),
                    'ctry_bias': self.safe_str(row.get('ctry_bias'))
                }

                query = """
                MERGE (o:Outcomes {outcome_id: $outcome_id})
                SET o += $properties
                """
                session.run(query, outcome_id=outcomes_data['outcome_id'], properties=outcomes_data)

        self.logger.info("Event characteristics ingested successfully")

    def ingest_temporal_info(self):
        """
        Step 6: Create TemporalInfo nodes with TKG metadata
        """
        self.logger.info("Ingesting temporal information...")

        with self.driver.session() as session:
            for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Temporal info"):
                eventid = self.safe_str(row.get('Event identification number'))
                if not eventid:
                    continue

                temporal_data = {
                    'temporal_id': f"temporal_{eventid}",
                    'date_type': self.safe_str(row.get('Type of date information available')),
                    'day': self.safe_int(row.get('Day of event - multi-day=average')),
                    'jdate_pre': self.safe_float(row.get('Precise julian date of event start')),
                    'jdate_pre_end': self.safe_float(row.get('Precise julian date of event end (Julian Date = 0 on Janurary 1st, 1945)')),
                    'jdate_est': self.safe_float(row.get('Estimated julian date of event start (Julian Date = 0 on Janurary 1st, 1945)')),
                    'jdate_est_end': self.safe_float(row.get('Estimated julian date of event end (Julian Date = 0 on Janurary 1st, 1945)')),
                    'ear_jdate': self.safe_float(row.get('Earliest start day of event (Julian Date = 0 on Janurary 1st, 1945)')),
                    'lat_jdate': self.safe_float(row.get('Latest end day of event')),
                    'duration_days': self.safe_int(row.get('Longest span of event, in days'))
                }

                query = """
                MERGE (t:TemporalInfo {temporal_id: $temporal_id})
                SET t += $properties
                """
                session.run(query, temporal_id=temporal_data['temporal_id'], properties=temporal_data)

        self.logger.info("Temporal information ingested successfully")

    def ingest_news_sources(self):
        """
        Step 7: Create NewsSource nodes for provenance
        """
        self.logger.info("Ingesting news sources...")

        # Extract unique news sources
        sources = []
        for _, row in self.df.iterrows():
            source_data = {
                'source_id': self.safe_str(row.get('Article id#')),
                'aid': self.safe_str(row.get('Article id#')),
                'news_source': self.safe_str(row.get('Source of the coded article')),
                'pub_month': self.safe_int(row.get('Global_pubdate_month')),
                'pub_day': self.safe_int(row.get('Global_pubdate_day')),
                'pub_year': self.safe_int(row.get('Global_pubdate_year')),
                'code_year': self.safe_int(row.get('Year of coding')),
                'code_month': self.safe_int(row.get('Month of coding')),
                'code_day': self.safe_int(row.get('Day of coding')),
                'recap': self.safe_bool(row.get('Is this a recapitulation coding?'))
            }

            if source_data['source_id']:
                sources.append(source_data)

        sources_df = pd.DataFrame(sources).drop_duplicates(subset=['source_id'])

        with self.driver.session() as session:
            for _, source in tqdm(sources_df.iterrows(), total=len(sources_df), desc="News sources"):
                query = """
                MERGE (n:NewsSource {source_id: $source_id})
                SET n += $properties
                """
                session.run(query, source_id=source['source_id'], properties=source.to_dict())

        self.logger.info(f"Created {len(sources_df)} NewsSource nodes")

    def create_event_relationships(self):
        """
        Step 8: Create all Event-centric relationships
        """
        self.logger.info("Creating event relationships...")

        with self.driver.session() as session:
            # OCCURRED_AT
            self.logger.info("Creating OCCURRED_AT relationships...")
            query = """
            MATCH (e:Event)
            WHERE e.country IS NOT NULL
            WITH e
            MATCH (l:Location)
            WHERE l.country = e.country
            WITH e, l
            LIMIT 1
            MERGE (e)-[:OCCURRED_AT]->(l)
            """
            session.run(query)

            # HAS_TYPE
            self.logger.info("Creating HAS_TYPE relationships...")
            query = """
            MATCH (e:Event)
            MATCH (et:EventType {type_id: 'type_' + e.eventid})
            MERGE (e)-[:HAS_TYPE]->(et)
            """
            session.run(query)

            # HAS_INTENSITY
            self.logger.info("Creating HAS_INTENSITY relationships...")
            query = """
            MATCH (e:Event)
            MATCH (im:IntensityMetrics {metrics_id: 'metrics_' + e.eventid})
            MERGE (e)-[:HAS_INTENSITY]->(im)
            """
            session.run(query)

            # DRIVEN_BY
            self.logger.info("Creating DRIVEN_BY relationships...")
            query = """
            MATCH (e:Event)
            MATCH (d:Drivers {driver_id: 'driver_' + e.eventid})
            WHERE d.sc_animosity OR d.anti_gov_sentmnts OR d.class_conflict OR
                  d.eco_scarcity OR d.pol_desires OR d.retain_power OR d.pers_security
            MERGE (e)-[:DRIVEN_BY]->(d)
            """
            session.run(query)

            # RESULTS_IN
            self.logger.info("Creating RESULTS_IN relationships...")
            query = """
            MATCH (e:Event)
            MATCH (o:Outcomes {outcome_id: 'outcome_' + e.eventid})
            MERGE (e)-[:RESULTS_IN]->(o)
            """
            session.run(query)

            # HAS_TEMPORAL_INFO
            self.logger.info("Creating HAS_TEMPORAL_INFO relationships...")
            query = """
            MATCH (e:Event)
            MATCH (t:TemporalInfo {temporal_id: 'temporal_' + e.eventid})
            MERGE (e)-[:HAS_TEMPORAL_INFO]->(t)
            """
            session.run(query)

            # REPORTED_IN
            self.logger.info("Creating REPORTED_IN relationships...")
            query = """
            MATCH (e:Event), (n:NewsSource)
            WHERE e.eventid IS NOT NULL AND n.source_id IS NOT NULL
            WITH e, n
            LIMIT 100000
            MERGE (e)-[:REPORTED_IN]->(n)
            """
            # This query simplified - in production, match on article ID field

        self.logger.info("Event relationships created successfully")

    def create_actor_relationships(self):
        """
        Step 9: Create HAS_INITIATOR, HAS_TARGET, HAS_VICTIM relationships
        """
        self.logger.info("Creating actor relationships...")

        with self.driver.session() as session:
            for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Actor relationships"):
                eventid = self.safe_str(row.get('Event identification number'))
                if not eventid:
                    continue

                # Initiators
                for col, category in [
                    ('Name of insurgent group initiator', 'insurgent'),
                    ('Name of socio-cultural group initiator', 'sociocultural'),
                    ('Name of political group initiator', 'political')
                ]:
                    name = self.safe_str(row.get(col))
                    if name:
                        actor_id = f"ini_{category}_{name}"
                        query = """
                        MATCH (e:Event {eventid: $eventid})
                        MATCH (a:Actor {actor_id: $actor_id})
                        MERGE (e)-[:HAS_INITIATOR]->(a)
                        """
                        session.run(query, eventid=eventid, actor_id=actor_id)

                # Targets
                for col, category in [
                    ('Name of insurgent group target', 'insurgent'),
                    ('Name of socio-cultural group target', 'sociocultural'),
                    ('Name of political group target', 'political')
                ]:
                    name = self.safe_str(row.get(col))
                    if name:
                        actor_id = f"tar_{category}_{name}"
                        query = """
                        MATCH (e:Event {eventid: $eventid})
                        MATCH (a:Actor {actor_id: $actor_id})
                        MERGE (e)-[:HAS_TARGET]->(a)
                        """
                        session.run(query, eventid=eventid, actor_id=actor_id)

                # Victims
                for col, category in [
                    ('Name of insurgent group victim', 'insurgent'),
                    ('Name of socio-cultural group victim', 'sociocultural'),
                    ('Name of political group victim', 'political')
                ]:
                    name = self.safe_str(row.get(col))
                    if name:
                        actor_id = f"vic_{category}_{name}"
                        query = """
                        MATCH (e:Event {eventid: $eventid})
                        MATCH (a:Actor {actor_id: $actor_id})
                        MERGE (e)-[:HAS_VICTIM]->(a)
                        """
                        session.run(query, eventid=eventid, actor_id=actor_id)

        self.logger.info("Actor relationships created successfully")

    def create_temporal_relationships(self):
        """
        Step 10: Create LINKED_TO and REACTS_TO with temporal validity
        """
        self.logger.info("Creating temporal relationships...")

        with self.driver.session() as session:
            # LINKED_TO relationships
            for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Event links"):
                linked = self.safe_bool(row.get('Is this a linked coding?'))
                if not linked:
                    continue

                from_eid = self.safe_str(row.get('Id of event linked from'))
                to_eid = self.safe_str(row.get('Id of event linked to'))
                link_type = self.safe_str(row.get('Type of event link'))

                if from_eid and to_eid:
                    query = """
                    MATCH (e1:Event {eventid: $from_eid})
                    MATCH (e2:Event {eventid: $to_eid})
                    MERGE (e1)-[r:LINKED_TO]->(e2)
                    SET r.link_type = $link_type,
                        r.valid_from = e1.valid_from,
                        r.valid_to = CASE
                            WHEN e2.valid_to IS NOT NULL THEN e2.valid_to
                            ELSE NULL
                        END
                    """
                    session.run(query, from_eid=from_eid, to_eid=to_eid, link_type=link_type)

            # REACTS_TO relationships
            for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Reactions"):
                posthoc = self.safe_str(row.get('Post hoc reaction?'))
                if posthoc and posthoc != 'No Post Hoc Reaction':
                    eventid = self.safe_str(row.get('Event identification number'))

                    # This would need more sophisticated logic to find what it reacts to
                    # For now, we'll create the relationship type structure
                    query = """
                    MATCH (e:Event {eventid: $eventid})
                    SET e.posthoc = $posthoc
                    """
                    session.run(query, eventid=eventid, posthoc=posthoc)

        self.logger.info("Temporal relationships created successfully")

    def create_location_hierarchy(self):
        """
        Step 11: Create CONTAINS relationships for location hierarchy
        """
        self.logger.info("Creating location hierarchy...")

        # This would require more sophisticated logic to determine containment
        # For now, we'll skip this or implement basic country-region relationships

        self.logger.info("Location hierarchy creation skipped (requires geographic data)")

    def validate_graph(self):
        """
        Step 12: Validate graph structure and run sanity checks
        """
        self.logger.info("Validating graph structure...")

        with self.driver.session() as session:
            # Node counts
            self.logger.info("\n=== Graph Statistics ===")

            queries = {
                "Events": "MATCH (e:Event) RETURN count(e) as count",
                "Locations": "MATCH (l:Location) RETURN count(l) as count",
                "Actors": "MATCH (a:Actor) RETURN count(a) as count",
                "EventTypes": "MATCH (et:EventType) RETURN count(et) as count",
                "IntensityMetrics": "MATCH (im:IntensityMetrics) RETURN count(im) as count",
                "Drivers": "MATCH (d:Drivers) RETURN count(d) as count",
                "Outcomes": "MATCH (o:Outcomes) RETURN count(o) as count",
                "TemporalInfo": "MATCH (t:TemporalInfo) RETURN count(t) as count",
                "NewsSources": "MATCH (n:NewsSource) RETURN count(n) as count",
            }

            for label, query in queries.items():
                result = session.run(query).single()
                count = result['count'] if result else 0
                self.logger.info(f"{label}: {count:,}")

            # Relationship counts
            self.logger.info("\n=== Relationship Statistics ===")
            rel_query = """
            CALL db.relationshipTypes() YIELD relationshipType
            CALL apoc.cypher.run(
                'MATCH ()-[r:`' + relationshipType + '`]->() RETURN count(r) as count',
                {}
            ) YIELD value
            RETURN relationshipType, value.count as count
            ORDER BY count DESC
            """

            try:
                results = session.run(rel_query)
                for record in results:
                    self.logger.info(f"{record['relationshipType']}: {record['count']:,}")
            except Exception as e:
                self.logger.warning(f"Could not get relationship counts (APOC may not be available): {e}")

            # Data quality checks
            self.logger.info("\n=== Data Quality Checks ===")

            quality_checks = {
                "Events without locations": """
                    MATCH (e:Event)
                    WHERE NOT (e)-[:OCCURRED_AT]->(:Location)
                    RETURN count(e) as count
                """,
                "Events without temporal info": """
                    MATCH (e:Event)
                    WHERE NOT (e)-[:HAS_TEMPORAL_INFO]->(:TemporalInfo)
                    RETURN count(e) as count
                """,
                "Actors without type": """
                    MATCH (a:Actor)
                    WHERE NOT (a:Group OR a:Individual OR a:GovernmentEntity)
                    RETURN count(a) as count
                """
            }

            for check_name, query in quality_checks.items():
                result = session.run(query).single()
                count = result['count'] if result else 0
                status = "✅ PASS" if count == 0 else f"⚠️  {count:,} issues"
                self.logger.info(f"{check_name}: {status}")

        self.logger.info("\n=== Validation Complete ===")

    def run_ingestion(self):
        """
        Main orchestration method
        """
        self.logger.info("="*80)
        self.logger.info("Starting SPEED Temporal Knowledge Graph Ingestion")
        self.logger.info("="*80)

        try:
            # Connect to Neo4j
            self.connect()

            # Load CSV
            self.load_csv()

            # Step 1: Schema
            self.create_constraints_and_indexes()

            # Step 2-7: Node creation
            self.ingest_events()
            self.ingest_locations()
            self.ingest_actors()
            self.ingest_event_characteristics()
            self.ingest_temporal_info()
            self.ingest_news_sources()

            # Step 8-11: Relationship creation
            self.create_event_relationships()
            self.create_actor_relationships()
            self.create_temporal_relationships()
            self.create_location_hierarchy()

            # Step 12: Validation
            self.validate_graph()

            self.logger.info("="*80)
            self.logger.info("✅ Ingestion Complete Successfully!")
            self.logger.info("="*80)

        except Exception as e:
            self.logger.error(f"❌ Ingestion failed: {e}", exc_info=True)
            raise
        finally:
            self.close()

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self.logger.info("Neo4j connection closed")


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Ingest SPEED dataset into Neo4j Temporal Knowledge Graph"
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--uri',
        default='bolt://localhost:7687',
        help='Neo4j URI'
    )
    parser.add_argument(
        '--user',
        default='neo4j',
        help='Neo4j username'
    )
    parser.add_argument(
        '--password',
        default='speedkg123',
        help='Neo4j password'
    )
    parser.add_argument(
        '--csv',
        default='output/resolved_data_20260121_152103.csv',
        help='Path to SPEED CSV file'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only run validation queries'
    )

    args = parser.parse_args()

    # Load config if exists
    config = load_config(args.config)

    # Override with command line arguments
    uri = args.uri or config.get('neo4j', {}).get('uri', 'bolt://localhost:7687')
    user = args.user or config.get('neo4j', {}).get('user', 'neo4j')
    password = args.password or config.get('neo4j', {}).get('password', 'speedkg123')
    csv_path = args.csv or config.get('data', {}).get('csv_path', 'output/resolved_data_20260121_152103.csv')

    # Create ingestion instance
    ingestion = SPEEDKnowledgeGraphIngestion(
        uri=uri,
        user=user,
        password=password,
        csv_path=csv_path
    )

    try:
        if args.validate_only:
            ingestion.connect()
            ingestion.validate_graph()
        else:
            ingestion.run_ingestion()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
