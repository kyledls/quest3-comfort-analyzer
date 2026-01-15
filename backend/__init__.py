"""Quest 3 Comfort Analyzer - Backend Module"""

from .database import (
    init_database, get_connection, insert_review,
    insert_accessory_mention, insert_comfort_issue,
    get_all_reviews, get_accessory_rankings,
    get_comfort_issues_breakdown, get_source_distribution,
    get_accessory_details
)

__all__ = [
    'init_database', 'get_connection', 'insert_review',
    'insert_accessory_mention', 'insert_comfort_issue',
    'get_all_reviews', 'get_accessory_rankings',
    'get_comfort_issues_breakdown', 'get_source_distribution',
    'get_accessory_details'
]
