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

interface IssueDetailedData {
  total: number;
  high: number;
  medium: number;
  low: number;
  examples: Array<{ quote: string; title: string; source: string }>;
}

// Issue descriptions
const ISSUE_DESCRIPTIONS: Record<string, { title: string; description: string; causes: string[]; symptoms: string[] }> = {
  weight: {
    title: "Weight Distribution Issues",
    description: "The Quest 3 is front-heavy due to the display and battery being located in the front.",
    causes: ["Front-heavy design", "Battery in front housing", "Inadequate counterbalance"],
    symptoms: ["Neck pain", "Fatigue after 20-30 minutes", "Headset sliding down"]
  },
  pressure_points: {
    title: "Pressure Points",
    description: "The stock face interface creates concentrated pressure on specific areas of the face.",
    causes: ["Hard foam padding", "Poor weight distribution", "One-size-fits-all design"],
    symptoms: ["Red marks on face", "Pain after short sessions", "Numbness in pressure areas"]
  },
  face_interface: {
    title: "Face Interface Problems",
    description: "The stock foam face cover has issues with light leakage, comfort, and fit.",
    causes: ["Cheap foam material", "Poor seal around nose", "Sweat absorption issues"],
    symptoms: ["Light leaking in", "Uncomfortable fit", "Hygiene concerns"]
  },
  glasses_compatibility: {
    title: "Glasses Compatibility",
    description: "Wearing glasses inside the Quest 3 is problematic.",
    causes: ["Limited space for glasses", "Risk of lens scratching", "Additional pressure on nose"],
    symptoms: ["Glasses don't fit", "Scratched VR lenses", "Extra discomfort"]
  },
  heat_sweating: {
    title: "Heat & Sweating Issues",
    description: "The enclosed design traps heat during active games.",
    causes: ["Enclosed design", "Processor heat", "Active gameplay", "Poor ventilation"],
    symptoms: ["Excessive sweating", "Fogged lenses", "Overheating warnings"]
  },
  forehead_discomfort: {
    title: "Forehead Discomfort",
    description: "Many users experience pain and soreness on the forehead.",
    causes: ["Stock strap design", "Weight concentrated on forehead", "Hard contact surface"],
    symptoms: ["Forehead pain", "Headaches", "Soreness lasting hours"]
  },
  strap_quality: {
    title: "Strap Quality Issues",
    description: "The stock strap is flimsy and inadequate.",
    causes: ["Cheap materials", "Poor manufacturing QC", "Stress points in design"],
    symptoms: ["Strap breakage", "Loose fit", "Frequent readjustment needed"]
  },
  fit_adjustment: {
    title: "Fit & Adjustment Difficulties",
    description: "Getting the headset properly positioned can be frustrating.",
    causes: ["Complex adjustment system", "Strap slippage", "Different head shapes"],
    symptoms: ["Constant readjustment", "Never feels 'right'", "Slipping during movement"]
  },
  long_session: {
    title: "Long Session Fatigue",
    description: "Extended VR sessions become uncomfortable due to cumulative discomfort.",
    causes: ["Combination of all issues", "Weight fatigue", "Heat buildup over time"],
    symptoms: ["Can't play over 30-60 min", "Increasing discomfort", "Need frequent breaks"]
  },
  battery_weight: {
    title: "Battery & Counterweight",
    description: "Adding battery weight to the back improves comfort by counterbalancing.",
    causes: ["Front-heavy default design", "Need for better balance"],
    symptoms: ["Actually helps comfort", "Improved weight distribution"]
  }
};

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
let accessoriesDetailedCache: Record<string, AccessoryDetail> | null = null;
let issuesDetailedCache: Record<string, IssueDetailedData> | null = null;

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
    if (!issuesDetailedCache) {
      issuesDetailedCache = await fetchJSON<Record<string, IssueDetailedData>>('issues_detailed.json');
    }
    const severityCounts = { high: 0, medium: 0, low: 0 };
    for (const data of Object.values(issuesDetailedCache)) {
      severityCounts.high += data.high;
      severityCounts.medium += data.medium;
      severityCounts.low += data.low;
    }
    return [
      { issue_type: 'high', count: severityCounts.high, severity: 'high', display_name: 'High' },
      { issue_type: 'medium', count: severityCounts.medium, severity: 'medium', display_name: 'Medium' },
      { issue_type: 'low', count: severityCounts.low, severity: 'low', display_name: 'Low' },
    ] as ComfortIssue[];
  },
  
  getDetailedIssues: async (): Promise<DetailedIssue[]> => {
    if (!issuesDetailedCache) {
      issuesDetailedCache = await fetchJSON<Record<string, IssueDetailedData>>('issues_detailed.json');
    }
    
    return Object.entries(issuesDetailedCache).map(([issueType, data]) => {
      const desc = ISSUE_DESCRIPTIONS[issueType] || {
        title: issueType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        description: `Issues related to ${issueType.replace(/_/g, ' ')}`,
        causes: [],
        symptoms: []
      };
      
      return {
        issue_type: issueType,
        title: desc.title,
        description: desc.description,
        causes: desc.causes,
        symptoms: desc.symptoms,
        stats: {
          total: data.total,
          high_severity: data.high,
          medium_severity: data.medium,
          low_severity: data.low
        },
        example_complaints: data.examples,
        recommended_solutions: []
      };
    }).sort((a, b) => b.stats.total - a.stats.total);
  },
  
  getSources: async () => {
    if (!sourcesCache) {
      sourcesCache = await fetchJSON<SourceDistribution[]>('sources.json');
    }
    return sourcesCache;
  },
  
  getAccessoryDetail: async (name: string): Promise<AccessoryDetail> => {
    if (!accessoriesDetailedCache) {
      accessoriesDetailedCache = await fetchJSON<Record<string, AccessoryDetail>>('accessories_detailed.json');
    }
    const detail = accessoriesDetailedCache[name];
    if (!detail) {
      throw new Error(`Accessory '${name}' not found`);
    }
    return detail;
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
