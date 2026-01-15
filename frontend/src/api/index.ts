/**
 * API client for Quest 3 Comfort Analyzer
 * Uses static JSON files for deployment
 */

const DATA_BASE = '/data';

export interface DashboardStats {
  total_reviews: number;
  total_accessory_mentions: number;
  total_comfort_issues: number;
  unique_accessories: number;
  top_accessory: string | null;
  most_common_issue: string | null;
}

export interface AccessoryRanking {
  accessory_name: string;
  accessory_type: string;
  mention_count: number;
  avg_sentiment: number;
  positive_mentions: number;
  negative_mentions: number;
  recommendation_score: number;
}

export interface ComfortIssue {
  issue_type: string;
  count: number;
  severity: string | null;
  display_name: string;
}

export interface SourceDistribution {
  source_name: string;
  review_count: number;
}

export interface AccessoryMention {
  context_snippet: string;
  sentiment_score: number;
  title: string | null;
  url: string | null;
  source_name: string | null;
}

export interface AccessoryDetail {
  accessory_name: string;
  accessory_type: string | null;
  mention_count: number;
  avg_sentiment: number;
  mentions: AccessoryMention[];
  pros: string[];
  cons: string[];
}

export interface IssueSolution {
  issue_type: string;
  display_name: string;
  solutions: string[];
}

export interface DetailedIssue {
  issue_type: string;
  title: string;
  description: string;
  causes: string[];
  symptoms: string[];
  stats: {
    total: number;
    high_severity: number;
    medium_severity: number;
    low_severity: number;
  };
  example_complaints: Array<{
    quote: string;
    title: string;
    source: string;
  }>;
  recommended_solutions: Array<{
    accessory: string;
    type: string;
    mentions: number;
    sentiment: number;
  }>;
}

async function fetchJSON<T>(filename: string): Promise<T> {
  const response = await fetch(`${DATA_BASE}/${filename}`);
  if (!response.ok) {
    throw new Error(`Failed to load ${filename}: ${response.status}`);
  }
  return response.json();
}

// Cache for loaded data
let statsCache: DashboardStats | null = null;
let rankingsCache: AccessoryRanking[] | null = null;
let issuesCache: ComfortIssue[] | null = null;
let sourcesCache: SourceDistribution[] | null = null;

export const api = {
  getStats: async () => {
    if (!statsCache) {
      statsCache = await fetchJSON<DashboardStats>('stats.json');
    }
    return statsCache;
  },
  
  getRankings: async (params?: { accessory_type?: string; min_mentions?: number; sort_by?: string }) => {
    if (!rankingsCache) {
      rankingsCache = await fetchJSON<AccessoryRanking[]>('rankings.json');
    }
    let results = [...rankingsCache];
    
    // Apply filters
    if (params?.accessory_type) {
      results = results.filter(r => r.accessory_type === params.accessory_type);
    }
    if (params?.min_mentions) {
      results = results.filter(r => r.mention_count >= params.min_mentions!);
    }
    if (params?.sort_by === 'mentions') {
      results.sort((a, b) => b.mention_count - a.mention_count);
    } else if (params?.sort_by === 'positive') {
      results.sort((a, b) => b.positive_mentions - a.positive_mentions);
    }
    
    return results;
  },
  
  getIssues: async (severity?: string) => {
    if (!issuesCache) {
      issuesCache = await fetchJSON<ComfortIssue[]>('issues.json');
    }
    if (severity) {
      return issuesCache.filter(i => i.severity === severity);
    }
    return issuesCache;
  },
  
  getIssuesBySeverity: async () => {
    // Return empty for static version
    return [] as ComfortIssue[];
  },
  
  getDetailedIssues: async () => {
    // Return empty for static version
    return [] as DetailedIssue[];
  },
  
  getSources: async () => {
    if (!sourcesCache) {
      sourcesCache = await fetchJSON<SourceDistribution[]>('sources.json');
    }
    return sourcesCache;
  },
  
  getAccessoryDetail: async (name: string): Promise<AccessoryDetail> => {
    if (!rankingsCache) {
      rankingsCache = await fetchJSON<AccessoryRanking[]>('rankings.json');
    }
    const ranking = rankingsCache.find(r => r.accessory_name === name);
    if (!ranking) {
      throw new Error(`Accessory '${name}' not found`);
    }
    return {
      accessory_name: ranking.accessory_name,
      accessory_type: ranking.accessory_type,
      mention_count: ranking.mention_count,
      avg_sentiment: ranking.avg_sentiment,
      mentions: [],
      pros: [],
      cons: []
    };
  },
  
  getSolutions: async () => {
    // Return empty for static version
    return [] as IssueSolution[];
  },
  
  getAccessoryTypes: async () => {
    if (!rankingsCache) {
      rankingsCache = await fetchJSON<AccessoryRanking[]>('rankings.json');
    }
    const typeMap = new Map<string, { count: number; mentions: number }>();
    for (const r of rankingsCache) {
      const existing = typeMap.get(r.accessory_type) || { count: 0, mentions: 0 };
      typeMap.set(r.accessory_type, {
        count: existing.count + 1,
        mentions: existing.mentions + r.mention_count
      });
    }
    return Array.from(typeMap.entries()).map(([type, data]) => ({
      type,
      display_name: type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      unique_accessories: data.count,
      total_mentions: data.mentions
    })).sort((a, b) => b.total_mentions - a.total_mentions);
  },
  
  search: async (query: string, limit = 10) => {
    if (!rankingsCache) {
      rankingsCache = await fetchJSON<AccessoryRanking[]>('rankings.json');
    }
    const q = query.toLowerCase();
    return rankingsCache
      .filter(r => r.accessory_name.toLowerCase().includes(q))
      .slice(0, limit)
      .map(r => ({
        name: r.accessory_name,
        type: r.accessory_type,
        mentions: r.mention_count,
        sentiment: r.avg_sentiment
      }));
  },
};
