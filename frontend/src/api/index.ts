/**
 * API client for Quest 3 Comfort Analyzer backend
 */

const API_BASE = '/api';

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

async function fetchAPI<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export const api = {
  getStats: () => fetchAPI<DashboardStats>('/stats'),
  
  getRankings: (params?: { accessory_type?: string; min_mentions?: number; sort_by?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.accessory_type) searchParams.set('accessory_type', params.accessory_type);
    if (params?.min_mentions) searchParams.set('min_mentions', params.min_mentions.toString());
    if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
    const query = searchParams.toString();
    return fetchAPI<AccessoryRanking[]>(`/rankings${query ? `?${query}` : ''}`);
  },
  
  getIssues: (severity?: string) => {
    const query = severity ? `?severity=${severity}` : '';
    return fetchAPI<ComfortIssue[]>(`/issues${query}`);
  },
  
  getIssuesBySeverity: () => fetchAPI<ComfortIssue[]>('/issues/by-severity'),
  
  getDetailedIssues: () => fetchAPI<DetailedIssue[]>('/issues/detailed'),
  
  getSources: () => fetchAPI<SourceDistribution[]>('/sources'),
  
  getAccessoryDetail: (name: string) => 
    fetchAPI<AccessoryDetail>(`/accessory/${encodeURIComponent(name)}`),
  
  getSolutions: () => fetchAPI<IssueSolution[]>('/solutions'),
  
  getAccessoryTypes: () => fetchAPI<Array<{
    type: string;
    display_name: string;
    unique_accessories: number;
    total_mentions: number;
  }>>('/accessory-types'),
  
  search: (query: string, limit = 10) => 
    fetchAPI<Array<{ name: string; type: string; mentions: number; sentiment: number }>>(
      `/search?q=${encodeURIComponent(query)}&limit=${limit}`
    ),
};
