"""
FastAPI backend for Quest 3 Comfort Analyzer.

Provides API endpoints for the dashboard to consume analyzed data.
"""

import sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import (
    get_connection, get_accessory_rankings,
    get_comfort_issues_breakdown, get_source_distribution,
    get_accessory_details
)
from backend.models import (
    AccessoryRanking, ComfortIssue, SourceDistribution,
    AccessoryDetail, AccessoryMention, DashboardStats, IssueSolution
)
from analyzer.categorizer import get_issue_solutions

# Create FastAPI app
app = FastAPI(
    title="Quest 3 Comfort Analyzer API",
    description="API for accessing Meta Quest 3 comfort accessory analysis data",
    version="1.0.0"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Quest 3 Comfort Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "/api/stats": "Overall dashboard statistics",
            "/api/rankings": "Accessory rankings by sentiment",
            "/api/issues": "Comfort issues breakdown",
            "/api/sources": "Data source distribution",
            "/api/accessory/{name}": "Detailed accessory information",
            "/api/solutions": "Solutions for comfort issues"
        }
    }


@app.get("/api/stats", response_model=DashboardStats)
async def get_stats():
    """Get overall dashboard statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get total reviews
    cursor.execute("SELECT COUNT(*) as count FROM reviews")
    total_reviews = cursor.fetchone()["count"]
    
    # Get total accessory mentions
    cursor.execute("SELECT COUNT(*) as count FROM accessory_mentions")
    total_mentions = cursor.fetchone()["count"]
    
    # Get total comfort issues
    cursor.execute("SELECT COUNT(*) as count FROM comfort_issues")
    total_issues = cursor.fetchone()["count"]
    
    # Get unique accessories
    cursor.execute("SELECT COUNT(DISTINCT accessory_name) as count FROM accessory_mentions")
    unique_accessories = cursor.fetchone()["count"]
    
    # Get top accessory
    cursor.execute("""
        SELECT accessory_name, AVG(sentiment_score) as avg_sent
        FROM accessory_mentions
        GROUP BY accessory_name
        HAVING COUNT(*) >= 3
        ORDER BY avg_sent DESC
        LIMIT 1
    """)
    top_result = cursor.fetchone()
    top_accessory = top_result["accessory_name"] if top_result else None
    
    # Get most common issue
    cursor.execute("""
        SELECT issue_type, COUNT(*) as count
        FROM comfort_issues
        GROUP BY issue_type
        ORDER BY count DESC
        LIMIT 1
    """)
    issue_result = cursor.fetchone()
    most_common_issue = issue_result["issue_type"] if issue_result else None
    
    conn.close()
    
    return DashboardStats(
        total_reviews=total_reviews,
        total_accessory_mentions=total_mentions,
        total_comfort_issues=total_issues,
        unique_accessories=unique_accessories,
        top_accessory=top_accessory,
        most_common_issue=most_common_issue
    )


@app.get("/api/rankings", response_model=List[AccessoryRanking])
async def get_rankings(
    accessory_type: Optional[str] = Query(None, description="Filter by accessory type"),
    min_mentions: int = Query(1, description="Minimum number of mentions"),
    sort_by: str = Query("sentiment", description="Sort by: sentiment, mentions, positive")
):
    """Get accessory rankings based on sentiment and mentions."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            accessory_name,
            accessory_type,
            COUNT(*) as mention_count,
            AVG(sentiment_score) as avg_sentiment,
            SUM(CASE WHEN sentiment_score > 0.1 THEN 1 ELSE 0 END) as positive_mentions,
            SUM(CASE WHEN sentiment_score < -0.1 THEN 1 ELSE 0 END) as negative_mentions
        FROM accessory_mentions
    """
    
    params = []
    
    if accessory_type:
        query += " WHERE accessory_type = ?"
        params.append(accessory_type)
    
    query += " GROUP BY accessory_name HAVING COUNT(*) >= ?"
    params.append(min_mentions)
    
    if sort_by == "mentions":
        query += " ORDER BY mention_count DESC"
    elif sort_by == "positive":
        query += " ORDER BY positive_mentions DESC"
    else:
        query += " ORDER BY avg_sentiment DESC, mention_count DESC"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    rankings = []
    for row in results:
        # Calculate recommendation score (weighted combination)
        sentiment = row["avg_sentiment"]
        mentions = row["mention_count"]
        positive_ratio = row["positive_mentions"] / mentions if mentions > 0 else 0
        
        # Score formula: sentiment weight + positive ratio + log of mentions for popularity
        import math
        rec_score = (sentiment * 0.4) + (positive_ratio * 0.4) + (math.log10(mentions + 1) * 0.2)
        
        rankings.append(AccessoryRanking(
            accessory_name=row["accessory_name"],
            accessory_type=row["accessory_type"],
            mention_count=row["mention_count"],
            avg_sentiment=round(row["avg_sentiment"], 3),
            positive_mentions=row["positive_mentions"],
            negative_mentions=row["negative_mentions"],
            recommendation_score=round(rec_score, 3)
        ))
    
    return rankings


@app.get("/api/issues", response_model=List[ComfortIssue])
async def get_issues(
    severity: Optional[str] = Query(None, description="Filter by severity: high, medium, low")
):
    """Get breakdown of comfort issues."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if severity:
        cursor.execute("""
            SELECT issue_type, COUNT(*) as count, severity
            FROM comfort_issues
            WHERE severity = ?
            GROUP BY issue_type
            ORDER BY count DESC
        """, (severity,))
    else:
        cursor.execute("""
            SELECT issue_type, COUNT(*) as count, NULL as severity
            FROM comfort_issues
            GROUP BY issue_type
            ORDER BY count DESC
        """)
    
    results = cursor.fetchall()
    conn.close()
    
    issues = []
    for row in results:
        display_name = row["issue_type"].replace("_", " ").title()
        issues.append(ComfortIssue(
            issue_type=row["issue_type"],
            count=row["count"],
            severity=row["severity"],
            display_name=display_name
        ))
    
    return issues


@app.get("/api/issues/by-severity", response_model=List[ComfortIssue])
async def get_issues_by_severity():
    """Get comfort issues grouped by severity."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM comfort_issues
        GROUP BY severity
        ORDER BY 
            CASE severity
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        ComfortIssue(
            issue_type=row["severity"],
            count=row["count"],
            severity=row["severity"],
            display_name=row["severity"].title()
        )
        for row in results
    ]


# Descriptions for each comfort issue
ISSUE_DESCRIPTIONS = {
    "weight": {
        "title": "Weight Distribution Issues",
        "description": "The Quest 3 is front-heavy due to the display and battery being located in the front. This causes neck strain and fatigue during extended sessions.",
        "causes": ["Front-heavy design", "Battery in front housing", "Inadequate counterbalance"],
        "symptoms": ["Neck pain", "Fatigue after 20-30 minutes", "Headset sliding down"]
    },
    "pressure_points": {
        "title": "Pressure Points",
        "description": "The stock face interface creates concentrated pressure on specific areas of the face, particularly cheekbones and forehead, causing pain and red marks.",
        "causes": ["Hard foam padding", "Poor weight distribution", "One-size-fits-all design"],
        "symptoms": ["Red marks on face", "Pain after short sessions", "Numbness in pressure areas"]
    },
    "face_interface": {
        "title": "Face Interface Problems", 
        "description": "The stock foam face cover has issues with light leakage, comfort, hygiene, and fit. Many users find it uncomfortable and inadequate.",
        "causes": ["Cheap foam material", "Poor seal around nose", "Sweat absorption issues"],
        "symptoms": ["Light leaking in", "Uncomfortable fit", "Hygiene concerns", "Fogging lenses"]
    },
    "glasses_compatibility": {
        "title": "Glasses Compatibility",
        "description": "Wearing glasses inside the Quest 3 is problematic - they may not fit, can scratch lenses, and create additional pressure points.",
        "causes": ["Limited space for glasses", "Risk of lens scratching", "Additional pressure on nose"],
        "symptoms": ["Glasses don't fit", "Scratched VR lenses", "Extra discomfort", "Poor focus"]
    },
    "heat_sweating": {
        "title": "Heat & Sweating Issues",
        "description": "The enclosed design traps heat during active games like Beat Saber or VR fitness, causing excessive sweating and lens fogging.",
        "causes": ["Enclosed design", "Processor heat", "Active gameplay", "Poor ventilation"],
        "symptoms": ["Excessive sweating", "Fogged lenses", "Overheating warnings", "Discomfort"]
    },
    "forehead_discomfort": {
        "title": "Forehead Discomfort",
        "description": "Many users experience pain and soreness on the forehead due to improper strap design distributing too much weight to this area.",
        "causes": ["Stock strap design", "Weight concentrated on forehead", "Hard contact surface"],
        "symptoms": ["Forehead pain", "Headaches", "Soreness lasting hours", "Red marks"]
    },
    "strap_quality": {
        "title": "Strap Quality Issues",
        "description": "The stock strap is flimsy and inadequate. Even Meta's Elite Strap has durability issues with cracking and breaking.",
        "causes": ["Cheap materials", "Poor manufacturing QC", "Stress points in design"],
        "symptoms": ["Strap breakage", "Loose fit", "Frequent readjustment needed", "Cracking"]
    },
    "fit_adjustment": {
        "title": "Fit & Adjustment Difficulties",
        "description": "Getting the headset properly positioned and secured can be frustrating. The adjustment mechanisms are finicky.",
        "causes": ["Complex adjustment system", "Strap slippage", "Different head shapes"],
        "symptoms": ["Constant readjustment", "Never feels 'right'", "Slipping during movement"]
    },
    "long_session": {
        "title": "Long Session Fatigue",
        "description": "Extended VR sessions become uncomfortable or impossible due to cumulative discomfort from multiple issues.",
        "causes": ["Combination of all issues", "Weight fatigue", "Heat buildup over time"],
        "symptoms": ["Can't play over 30-60 min", "Increasing discomfort", "Need frequent breaks"]
    },
    "battery_weight": {
        "title": "Battery & Counterweight",
        "description": "Ironically, adding battery weight to the back improves comfort by counterbalancing the front-heavy design.",
        "causes": ["Front-heavy default design", "Need for better balance"],
        "symptoms": ["Actually helps comfort", "Improved weight distribution", "Longer sessions possible"]
    }
}


@app.get("/api/issues/detailed")
async def get_detailed_issues():
    """Get in-depth information about each comfort issue."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get issue counts and severity breakdown
    cursor.execute("""
        SELECT 
            issue_type,
            COUNT(*) as total_count,
            SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_count,
            SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium_count,
            SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low_count
        FROM comfort_issues
        GROUP BY issue_type
        ORDER BY total_count DESC
    """)
    issue_stats = {row["issue_type"]: dict(row) for row in cursor.fetchall()}
    
    # Get example complaints for each issue
    cursor.execute("""
        SELECT ci.issue_type, ci.context_snippet, r.title, s.name as source
        FROM comfort_issues ci
        JOIN reviews r ON ci.review_id = r.id
        JOIN sources s ON r.source_id = s.id
        WHERE ci.context_snippet IS NOT NULL AND ci.context_snippet != ''
        ORDER BY ci.issue_type
    """)
    
    from collections import defaultdict
    examples = defaultdict(list)
    for row in cursor.fetchall():
        if len(examples[row["issue_type"]]) < 5:
            examples[row["issue_type"]].append({
                "quote": row["context_snippet"],
                "title": row["title"][:60] if row["title"] else "",
                "source": row["source"]
            })
    
    # Get recommended solutions for each issue
    cursor.execute("""
        SELECT 
            ci.issue_type,
            am.accessory_name,
            am.accessory_type,
            COUNT(*) as mention_count,
            AVG(am.sentiment_score) as avg_sentiment
        FROM comfort_issues ci
        JOIN accessory_mentions am ON ci.review_id = am.review_id
        WHERE am.sentiment_score > 0.1
        GROUP BY ci.issue_type, am.accessory_name
        HAVING COUNT(*) >= 3
        ORDER BY ci.issue_type, avg_sentiment DESC
    """)
    
    solutions = defaultdict(list)
    for row in cursor.fetchall():
        if len(solutions[row["issue_type"]]) < 5:
            solutions[row["issue_type"]].append({
                "accessory": row["accessory_name"],
                "type": row["accessory_type"],
                "mentions": row["mention_count"],
                "sentiment": round(row["avg_sentiment"], 2)
            })
    
    conn.close()
    
    # Build detailed response
    detailed_issues = []
    for issue_type, stats in issue_stats.items():
        info = ISSUE_DESCRIPTIONS.get(issue_type, {
            "title": issue_type.replace("_", " ").title(),
            "description": f"Issues related to {issue_type.replace('_', ' ')}",
            "causes": [],
            "symptoms": []
        })
        
        detailed_issues.append({
            "issue_type": issue_type,
            "title": info["title"],
            "description": info["description"],
            "causes": info.get("causes", []),
            "symptoms": info.get("symptoms", []),
            "stats": {
                "total": stats["total_count"],
                "high_severity": stats["high_count"],
                "medium_severity": stats["medium_count"],
                "low_severity": stats["low_count"]
            },
            "example_complaints": examples.get(issue_type, []),
            "recommended_solutions": solutions.get(issue_type, [])
        })
    
    return detailed_issues


@app.get("/api/sources", response_model=List[SourceDistribution])
async def get_sources():
    """Get distribution of reviews by source."""
    results = get_source_distribution()
    
    return [
        SourceDistribution(
            source_name=row["source_name"],
            review_count=row["review_count"]
        )
        for row in results
    ]


@app.get("/api/accessory/{name}", response_model=AccessoryDetail)
async def get_accessory(name: str):
    """Get detailed information about a specific accessory."""
    data = get_accessory_details(name)
    
    if not data.get("stats"):
        raise HTTPException(status_code=404, detail=f"Accessory '{name}' not found")
    
    stats = data["stats"]
    mentions = data["mentions"]
    
    # Extract pros and cons from high/low sentiment mentions
    pros = []
    cons = []
    
    for mention in mentions:
        snippet = mention.get("context_snippet", "")
        sentiment = mention.get("sentiment_score", 0)
        
        if sentiment > 0.2 and len(pros) < 5:
            # Extract key positive phrases
            if len(snippet) > 20:
                pros.append(snippet[:200])
        elif sentiment < -0.2 and len(cons) < 5:
            if len(snippet) > 20:
                cons.append(snippet[:200])
    
    return AccessoryDetail(
        accessory_name=stats.get("accessory_name", name),
        accessory_type=stats.get("accessory_type"),
        mention_count=stats.get("mention_count", 0),
        avg_sentiment=round(stats.get("avg_sentiment", 0), 3),
        mentions=[
            AccessoryMention(
                context_snippet=m.get("context_snippet", ""),
                sentiment_score=round(m.get("sentiment_score", 0), 3),
                title=m.get("title"),
                url=m.get("url"),
                source_name=m.get("source_name")
            )
            for m in mentions[:50]  # Limit to 50 mentions
        ],
        pros=pros,
        cons=cons
    )


@app.get("/api/solutions", response_model=List[IssueSolution])
async def get_solutions():
    """Get solutions for common comfort issues."""
    solutions_data = get_issue_solutions()
    
    return [
        IssueSolution(
            issue_type=issue_type,
            display_name=issue_type.replace("_", " ").title(),
            solutions=solutions
        )
        for issue_type, solutions in solutions_data.items()
    ]


@app.get("/api/accessory-types")
async def get_accessory_types():
    """Get list of accessory types and their counts."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT accessory_type, COUNT(DISTINCT accessory_name) as unique_count, COUNT(*) as mention_count
        FROM accessory_mentions
        GROUP BY accessory_type
        ORDER BY mention_count DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "type": row["accessory_type"],
            "display_name": row["accessory_type"].replace("_", " ").title(),
            "unique_accessories": row["unique_count"],
            "total_mentions": row["mention_count"]
        }
        for row in results
    ]


@app.get("/api/search")
async def search_accessories(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum results")
):
    """Search accessories by name."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            accessory_name,
            accessory_type,
            COUNT(*) as mention_count,
            AVG(sentiment_score) as avg_sentiment
        FROM accessory_mentions
        WHERE accessory_name LIKE ?
        GROUP BY accessory_name
        ORDER BY mention_count DESC
        LIMIT ?
    """, (f"%{q}%", limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "name": row["accessory_name"],
            "type": row["accessory_type"],
            "mentions": row["mention_count"],
            "sentiment": round(row["avg_sentiment"], 3)
        }
        for row in results
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
