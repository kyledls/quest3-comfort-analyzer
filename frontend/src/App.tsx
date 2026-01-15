import { useState, useEffect } from 'react';
import { 
  Activity, Award, AlertTriangle, Database,
  TrendingUp, ChevronRight, Search, X
} from 'lucide-react';
import { api, DashboardStats, AccessoryRanking, ComfortIssue, SourceDistribution, AccessoryDetail } from './api';
import AccessoryRankings from './components/AccessoryRankings';
import ComfortIssuesChart from './components/ComfortIssuesChart';
import DetailedView from './components/DetailedView';
import SourcesChart from './components/SourcesChart';
import { DetailedIssues } from './components/DetailedIssues';

function App() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [rankings, setRankings] = useState<AccessoryRanking[]>([]);
  const [issues, setIssues] = useState<ComfortIssue[]>([]);
  const [sources, setSources] = useState<SourceDistribution[]>([]);
  const [selectedAccessory, setSelectedAccessory] = useState<string | null>(null);
  const [accessoryDetail, setAccessoryDetail] = useState<AccessoryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Array<{ name: string; type: string; mentions: number; sentiment: number }>>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (selectedAccessory) {
      loadAccessoryDetail(selectedAccessory);
    }
  }, [selectedAccessory]);

  useEffect(() => {
    const debounce = setTimeout(() => {
      if (searchQuery.length >= 2) {
        api.search(searchQuery).then(setSearchResults).catch(console.error);
      } else {
        setSearchResults([]);
      }
    }, 300);
    return () => clearTimeout(debounce);
  }, [searchQuery]);

  async function loadDashboardData() {
    setLoading(true);
    setError(null);
    try {
      const [statsData, rankingsData, issuesData, sourcesData] = await Promise.all([
        api.getStats(),
        api.getRankings({ min_mentions: 2 }),
        api.getIssues(),
        api.getSources()
      ]);
      setStats(statsData);
      setRankings(rankingsData);
      setIssues(issuesData);
      setSources(sourcesData);
    } catch (err) {
      setError('Failed to load dashboard data. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function loadAccessoryDetail(name: string) {
    try {
      const detail = await api.getAccessoryDetail(name);
      setAccessoryDetail(detail);
    } catch (err) {
      console.error('Failed to load accessory detail:', err);
    }
  }

  function getSentimentColor(sentiment: number): string {
    if (sentiment > 0.2) return 'text-green-600';
    if (sentiment < -0.2) return 'text-red-600';
    return 'text-gray-600';
  }

  function getSentimentBg(sentiment: number): string {
    if (sentiment > 0.2) return 'bg-green-100';
    if (sentiment < -0.2) return 'bg-red-100';
    return 'bg-gray-100';
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-quest-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Data</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="px-4 py-2 bg-quest-600 text-white rounded-lg hover:bg-quest-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Quest 3 Comfort Analyzer
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Find the best accessories for your Meta Quest 3
              </p>
            </div>
            
            {/* Search */}
            <div className="relative">
              <div className="flex items-center">
                <Search className="absolute left-3 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search accessories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-quest-500 focus:border-transparent w-64"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3"
                  >
                    <X className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                  </button>
                )}
              </div>
              
              {/* Search Results Dropdown */}
              {searchResults.length > 0 && (
                <div className="absolute top-full mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                  {searchResults.map((result) => (
                    <button
                      key={result.name}
                      onClick={() => {
                        setSelectedAccessory(result.name);
                        setSearchQuery('');
                        setSearchResults([]);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center justify-between"
                    >
                      <span className="font-medium">{result.name}</span>
                      <span className={`text-sm ${getSentimentColor(result.sentiment)}`}>
                        {result.sentiment > 0 ? '+' : ''}{result.sentiment.toFixed(2)}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center">
                <div className="p-2 bg-quest-100 rounded-lg">
                  <Database className="h-6 w-6 text-quest-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Reviews</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_reviews.toLocaleString()}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Activity className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Accessory Mentions</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_accessory_mentions.toLocaleString()}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <AlertTriangle className="h-6 w-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Comfort Issues</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_comfort_issues.toLocaleString()}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Award className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Top Rated</p>
                  <p className="text-lg font-bold text-gray-900 truncate" title={stats.top_accessory || 'N/A'}>
                    {stats.top_accessory || 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Rankings - Takes 2 columns */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    <TrendingUp className="inline-block h-5 w-5 mr-2 text-quest-600" />
                    Accessory Rankings
                  </h2>
                </div>
              </div>
              <AccessoryRankings 
                rankings={rankings} 
                onSelectAccessory={setSelectedAccessory}
                getSentimentColor={getSentimentColor}
                getSentimentBg={getSentimentBg}
              />
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Comfort Issues */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">
                  <AlertTriangle className="inline-block h-5 w-5 mr-2 text-yellow-600" />
                  Common Issues
                </h2>
              </div>
              <ComfortIssuesChart issues={issues} />
            </div>

            {/* Sources */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">
                  <Database className="inline-block h-5 w-5 mr-2 text-blue-600" />
                  Data Sources
                </h2>
              </div>
              <SourcesChart sources={sources} />
            </div>
          </div>
        </div>

        {/* Detailed Issues Section */}
        <div className="mt-8">
          <DetailedIssues onAccessoryClick={setSelectedAccessory} />
        </div>

        {/* Detailed View Modal */}
        {selectedAccessory && accessoryDetail && (
          <DetailedView
            accessory={accessoryDetail}
            onClose={() => {
              setSelectedAccessory(null);
              setAccessoryDetail(null);
            }}
            getSentimentColor={getSentimentColor}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Quest 3 Comfort Analyzer - Data aggregated from Reddit, Amazon, YouTube, and VR forums
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
