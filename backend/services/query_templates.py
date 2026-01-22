"""Pre-built Cypher query templates for SPEED Knowledge Graph"""

QUERY_TEMPLATES = {
    "event_escalation_chain": """
        MATCH path = (e1:Event)-[:LINKED_TO*1..5]->(e2:Event)
        WHERE e1.country = $country AND e1.year = $year
        WITH path, length(path) as chain_length
        RETURN
            [node in nodes(path) | node] as events,
            chain_length,
            [rel in relationships(path) | type(rel)] as link_types
        ORDER BY chain_length DESC
        LIMIT $limit
    """,

    "temporal_intensity_trend": """
        MATCH (e:Event)-[:HAS_INTENSITY]->(im:IntensityMetrics)
        WHERE e.year >= $start_year AND e.year <= $end_year
        AND ($country IS NULL OR e.country = $country)
        RETURN
            e.year as year,
            e.month as month,
            avg(im.pol_viol) as avg_political_violence,
            avg(im.stat_viol) as avg_state_violence,
            avg(im.pol_express) as avg_political_expression,
            count(e) as event_count,
            sum(CASE WHEN im.n_killed_a IS NOT NULL THEN im.n_killed_a ELSE 0 END) as total_casualties
        ORDER BY e.year, e.month
    """,

    "actor_network": """
        MATCH (e:Event)-[:HAS_INITIATOR]->(a1:Actor)
        MATCH (e)-[:HAS_TARGET]->(a2:Actor)
        WHERE ($country IS NULL OR e.country = $country)
        AND ($year IS NULL OR e.year = $year)
        WITH a1, a2, count(e) as interaction_count, collect(e.eventid)[..10] as event_samples
        WHERE interaction_count >= $min_interactions
        RETURN
            a1.name as initiator,
            a1.actor_id as initiator_id,
            a2.name as target,
            a2.actor_id as target_id,
            interaction_count,
            event_samples
        ORDER BY interaction_count DESC
        LIMIT $limit
    """,

    "driver_distribution": """
        MATCH (e:Event)-[:DRIVEN_BY]->(d:Drivers)
        WHERE ($year IS NULL OR e.year = $year)
        AND ($country IS NULL OR e.country = $country)
        RETURN
            sum(CASE WHEN d.anti_gov_sentmnts THEN 1 ELSE 0 END) as anti_government,
            sum(CASE WHEN d.sc_animosity THEN 1 ELSE 0 END) as sociocultural,
            sum(CASE WHEN d.class_conflict THEN 1 ELSE 0 END) as class_based,
            sum(CASE WHEN d.eco_scarcity THEN 1 ELSE 0 END) as economic,
            sum(CASE WHEN d.pol_desires THEN 1 ELSE 0 END) as political_rights,
            sum(CASE WHEN d.retain_power THEN 1 ELSE 0 END) as retain_power,
            sum(CASE WHEN d.pers_security THEN 1 ELSE 0 END) as personal_security,
            count(e) as total_events
    """,

    "geographic_distribution": """
        MATCH (e:Event)-[:OCCURRED_AT]->(l:Location)
        WHERE ($year IS NULL OR e.year = $year)
        AND ($region IS NULL OR l.region = $region)
        RETURN
            l.country as country,
            l.region as region,
            l.latitude as lat,
            l.longitude as lon,
            count(e) as event_count,
            avg(CASE WHEN (e)-[:HAS_INTENSITY]->(:IntensityMetrics)
                THEN 1 ELSE 0 END) as has_intensity_data
        ORDER BY event_count DESC
        LIMIT $limit
    """,

    "precursor_events": """
        MATCH (small:Event)-[:HAS_TYPE]->(et:EventType)
        WHERE et.ev_type = 'Political Expression'
        AND ($country IS NULL OR small.country = $country)
        MATCH path = (small)-[:LINKED_TO*1..5]->(major:Event)
        MATCH (major)-[:HAS_INTENSITY]->(im:IntensityMetrics)
        WHERE im.n_killed_a > $casualty_threshold
        RETURN
            small.eventid as precursor_id,
            small.year as precursor_year,
            small.country as country,
            major.eventid as major_event_id,
            major.year as major_event_year,
            im.n_killed_a as casualties,
            length(path) as chain_length
        ORDER BY casualties DESC
        LIMIT $limit
    """,

    "intensity_by_event_type": """
        MATCH (e:Event)-[:HAS_TYPE]->(et:EventType)
        MATCH (e)-[:HAS_INTENSITY]->(im:IntensityMetrics)
        WHERE ($year IS NULL OR e.year = $year)
        AND ($country IS NULL OR e.country = $country)
        RETURN
            et.ev_type as event_type,
            count(e) as event_count,
            avg(im.pol_viol) as avg_violence,
            sum(CASE WHEN im.n_killed_a IS NOT NULL THEN im.n_killed_a ELSE 0 END) as total_casualties,
            max(im.pol_viol) as max_violence
        ORDER BY event_count DESC
    """,

    "temporal_event_distribution": """
        MATCH (e:Event)
        WHERE e.year >= $start_year AND e.year <= $end_year
        AND ($country IS NULL OR e.country = $country)
        RETURN
            e.year as year,
            count(e) as event_count,
            collect(DISTINCT e.country)[..10] as countries
        ORDER BY e.year
    """,

    "actor_involvement_by_role": """
        MATCH (e:Event)-[r]->(a:Actor)
        WHERE type(r) IN ['HAS_INITIATOR', 'HAS_TARGET', 'HAS_VICTIM']
        AND ($year IS NULL OR e.year = $year)
        AND ($country IS NULL OR e.country = $country)
        RETURN
            a.name as actor_name,
            a.actor_type as actor_type,
            type(r) as role,
            count(e) as involvement_count
        ORDER BY involvement_count DESC
        LIMIT $limit
    """,

    "recent_events": """
        MATCH (e:Event)
        WHERE e.year IS NOT NULL
        WITH e
        ORDER BY e.year DESC, e.month DESC, e.day DESC
        LIMIT $limit
        OPTIONAL MATCH (e)-[:OCCURRED_AT]->(l:Location)
        OPTIONAL MATCH (e)-[:HAS_INTENSITY]->(im:IntensityMetrics)
        RETURN
            e.eventid as eventid,
            e.year as year,
            e.month as month,
            e.day as day,
            e.country as country,
            l.region as region,
            im.pol_viol as intensity,
            im.n_killed_a as casualties
    """,

    "event_outcomes_analysis": """
        MATCH (e:Event)-[:RESULTS_IN]->(o:Outcomes)
        WHERE ($year IS NULL OR e.year = $year)
        AND ($country IS NULL OR e.country = $country)
        RETURN
            sum(CASE WHEN o.property_damaged THEN 1 ELSE 0 END) as property_damaged_count,
            sum(CASE WHEN o.arrests THEN 1 ELSE 0 END) as arrests_count,
            count(e) as total_events,
            o.victim_effect as victim_effects,
            count(*) as effect_count
        ORDER BY effect_count DESC
    """
}


# Default parameters for query templates
DEFAULT_PARAMETERS = {
    "limit": 50,
    "min_interactions": 2,
    "casualty_threshold": 10,
    "start_year": 2000,
    "end_year": 2020,
    "country": None,
    "year": None,
    "region": None
}


def get_query_template(template_name: str) -> str:
    """Get a query template by name"""
    return QUERY_TEMPLATES.get(template_name, "")


def get_default_parameters() -> dict:
    """Get default query parameters"""
    return DEFAULT_PARAMETERS.copy()
