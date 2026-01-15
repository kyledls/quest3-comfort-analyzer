import { X, ExternalLink, ThumbsUp, ThumbsDown, Star } from 'lucide-react';
import { AccessoryDetail } from '../api';

interface Props {
  accessory: AccessoryDetail;
  onClose: () => void;
  getSentimentColor: (sentiment: number) => string;
}

export default function DetailedView({ accessory, onClose, getSentimentColor }: Props) {
  function formatType(type: string | null): string {
    if (!type) return 'Unknown';
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  function getSentimentEmoji(sentiment: number): string {
    if (sentiment > 0.3) return '😊';
    if (sentiment > 0.1) return '🙂';
    if (sentiment > -0.1) return '😐';
    if (sentiment > -0.3) return '😕';
    return '😞';
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-100 flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {accessory.accessory_name}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {formatType(accessory.accessory_type)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Stats */}
        <div className="p-6 bg-gray-50 grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-gray-900">
              {accessory.mention_count}
            </p>
            <p className="text-sm text-gray-500">Mentions</p>
          </div>
          <div className="text-center">
            <p className={`text-3xl font-bold ${getSentimentColor(accessory.avg_sentiment)}`}>
              {accessory.avg_sentiment > 0 ? '+' : ''}{accessory.avg_sentiment.toFixed(2)}
            </p>
            <p className="text-sm text-gray-500">Sentiment Score</p>
          </div>
          <div className="text-center">
            <p className="text-3xl">
              {getSentimentEmoji(accessory.avg_sentiment)}
            </p>
            <p className="text-sm text-gray-500">Overall Rating</p>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Pros & Cons */}
          {(accessory.pros.length > 0 || accessory.cons.length > 0) && (
            <div className="grid grid-cols-2 gap-6 mb-6">
              {accessory.pros.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <ThumbsUp className="h-4 w-4 text-green-600" />
                    What People Like
                  </h3>
                  <ul className="space-y-2">
                    {accessory.pros.slice(0, 3).map((pro, i) => (
                      <li key={i} className="text-sm text-gray-600 bg-green-50 p-3 rounded-lg">
                        "{pro}"
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {accessory.cons.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <ThumbsDown className="h-4 w-4 text-red-600" />
                    What People Dislike
                  </h3>
                  <ul className="space-y-2">
                    {accessory.cons.slice(0, 3).map((con, i) => (
                      <li key={i} className="text-sm text-gray-600 bg-red-50 p-3 rounded-lg">
                        "{con}"
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Recent Mentions */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">
              Recent Mentions ({accessory.mentions.length})
            </h3>
            <div className="space-y-3">
              {accessory.mentions.slice(0, 10).map((mention, i) => (
                <div 
                  key={i} 
                  className="p-4 bg-gray-50 rounded-lg border border-gray-100"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      {mention.title && (
                        <p className="font-medium text-gray-900 text-sm mb-1">
                          {mention.title}
                        </p>
                      )}
                      <p className="text-sm text-gray-600">
                        "{mention.context_snippet}"
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Star className={`h-4 w-4 ${getSentimentColor(mention.sentiment_score)}`} />
                      <span className={`text-sm font-medium ${getSentimentColor(mention.sentiment_score)}`}>
                        {mention.sentiment_score > 0 ? '+' : ''}{mention.sentiment_score.toFixed(2)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                    {mention.source_name && (
                      <span className="capitalize">{mention.source_name}</span>
                    )}
                    {mention.url && (
                      <a
                        href={mention.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-quest-600 hover:text-quest-700"
                      >
                        View Source
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-100 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
