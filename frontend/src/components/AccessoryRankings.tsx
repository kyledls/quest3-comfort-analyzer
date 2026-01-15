import { useState } from 'react';
import { ChevronRight, Star, ThumbsUp, ThumbsDown } from 'lucide-react';
import { AccessoryRanking } from '../api';

interface Props {
  rankings: AccessoryRanking[];
  onSelectAccessory: (name: string) => void;
  getSentimentColor: (sentiment: number) => string;
  getSentimentBg: (sentiment: number) => string;
}

export default function AccessoryRankings({ 
  rankings, 
  onSelectAccessory,
  getSentimentColor,
  getSentimentBg
}: Props) {
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'sentiment' | 'mentions' | 'score'>('score');

  const accessoryTypes = [...new Set(rankings.map(r => r.accessory_type))];
  
  const filteredRankings = rankings
    .filter(r => filter === 'all' || r.accessory_type === filter)
    .sort((a, b) => {
      if (sortBy === 'sentiment') return b.avg_sentiment - a.avg_sentiment;
      if (sortBy === 'mentions') return b.mention_count - a.mention_count;
      return b.recommendation_score - a.recommendation_score;
    });

  function formatType(type: string): string {
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  function getSentimentLabel(sentiment: number): string {
    if (sentiment > 0.3) return 'Very Positive';
    if (sentiment > 0.1) return 'Positive';
    if (sentiment > -0.1) return 'Neutral';
    if (sentiment > -0.3) return 'Negative';
    return 'Very Negative';
  }

  return (
    <div>
      {/* Filters */}
      <div className="p-4 border-b border-gray-100 flex flex-wrap gap-2">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-quest-500"
        >
          <option value="all">All Types</option>
          {accessoryTypes.map(type => (
            <option key={type} value={type}>{formatType(type)}</option>
          ))}
        </select>
        
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-quest-500"
        >
          <option value="score">By Score</option>
          <option value="sentiment">By Sentiment</option>
          <option value="mentions">By Mentions</option>
        </select>
      </div>

      {/* Rankings List */}
      <div className="divide-y divide-gray-100">
        {filteredRankings.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No accessories found. Run the scrapers to collect data.
          </div>
        ) : (
          filteredRankings.slice(0, 20).map((ranking, index) => (
            <button
              key={ranking.accessory_name}
              onClick={() => onSelectAccessory(ranking.accessory_name)}
              className="w-full p-4 hover:bg-gray-50 transition flex items-center gap-4 text-left"
            >
              {/* Rank Badge */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                ${index === 0 ? 'bg-yellow-100 text-yellow-700' : 
                  index === 1 ? 'bg-gray-200 text-gray-700' :
                  index === 2 ? 'bg-orange-100 text-orange-700' :
                  'bg-gray-100 text-gray-600'}`}
              >
                {index + 1}
              </div>

              {/* Main Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-gray-900 truncate">
                    {ranking.accessory_name}
                  </h3>
                  <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">
                    {formatType(ranking.accessory_type)}
                  </span>
                </div>
                
                <div className="flex items-center gap-4 mt-1 text-sm">
                  <span className="text-gray-500">
                    {ranking.mention_count} mentions
                  </span>
                  <span className="flex items-center gap-1 text-green-600">
                    <ThumbsUp className="h-3 w-3" />
                    {ranking.positive_mentions}
                  </span>
                  <span className="flex items-center gap-1 text-red-600">
                    <ThumbsDown className="h-3 w-3" />
                    {ranking.negative_mentions}
                  </span>
                </div>
              </div>

              {/* Sentiment Score */}
              <div className="text-right">
                <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg ${getSentimentBg(ranking.avg_sentiment)}`}>
                  <Star className={`h-4 w-4 ${getSentimentColor(ranking.avg_sentiment)}`} />
                  <span className={`font-semibold ${getSentimentColor(ranking.avg_sentiment)}`}>
                    {ranking.avg_sentiment > 0 ? '+' : ''}{ranking.avg_sentiment.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {getSentimentLabel(ranking.avg_sentiment)}
                </p>
              </div>

              <ChevronRight className="h-5 w-5 text-gray-400" />
            </button>
          ))
        )}
      </div>
    </div>
  );
}
