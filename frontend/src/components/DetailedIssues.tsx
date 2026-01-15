/**
 * Detailed Comfort Issues component
 * Shows in-depth information about each comfort problem
 */

import { useState, useEffect } from 'react';
import { api, DetailedIssue } from '../api';

interface DetailedIssuesProps {
  onAccessoryClick?: (name: string) => void;
}

const severityColors = {
  high: 'bg-red-100 text-red-800 border-red-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  low: 'bg-green-100 text-green-800 border-green-200',
};

const issueIcons: Record<string, string> = {
  weight: '⚖️',
  pressure_points: '🎯',
  face_interface: '😷',
  glasses_compatibility: '👓',
  heat_sweating: '🌡️',
  forehead_discomfort: '🤕',
  strap_quality: '🔗',
  fit_adjustment: '🔧',
  long_session: '⏱️',
  battery_weight: '🔋',
};

export function DetailedIssues({ onAccessoryClick }: DetailedIssuesProps) {
  const [issues, setIssues] = useState<DetailedIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedIssue, setExpandedIssue] = useState<string | null>(null);

  useEffect(() => {
    api.getDetailedIssues()
      .then(setIssues)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-24 bg-gray-100 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <svg className="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Comfort Issues Explained
      </h2>

      <div className="space-y-4">
        {issues.map((issue) => (
          <div 
            key={issue.issue_type}
            className="border border-gray-200 rounded-lg overflow-hidden hover:border-gray-300 transition-colors"
          >
            {/* Issue Header - Always visible */}
            <button
              onClick={() => setExpandedIssue(expandedIssue === issue.issue_type ? null : issue.issue_type)}
              className="w-full p-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{issueIcons[issue.issue_type] || '❓'}</span>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900">{issue.title}</h3>
                  <p className="text-sm text-gray-600">{issue.stats.total} mentions</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                {/* Severity indicators */}
                <div className="flex gap-2 text-xs">
                  {issue.stats.high_severity > 0 && (
                    <span className={`px-2 py-1 rounded-full ${severityColors.high}`}>
                      {issue.stats.high_severity} high
                    </span>
                  )}
                  {issue.stats.medium_severity > 0 && (
                    <span className={`px-2 py-1 rounded-full ${severityColors.medium}`}>
                      {issue.stats.medium_severity} med
                    </span>
                  )}
                  {issue.stats.low_severity > 0 && (
                    <span className={`px-2 py-1 rounded-full ${severityColors.low}`}>
                      {issue.stats.low_severity} low
                    </span>
                  )}
                </div>
                {/* Expand icon */}
                <svg 
                  className={`w-5 h-5 text-gray-500 transition-transform ${expandedIssue === issue.issue_type ? 'rotate-180' : ''}`}
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            {/* Expanded Content */}
            {expandedIssue === issue.issue_type && (
              <div className="p-4 bg-white space-y-4">
                {/* Description */}
                <div>
                  <p className="text-gray-700">{issue.description}</p>
                </div>

                {/* Causes & Symptoms */}
                <div className="grid md:grid-cols-2 gap-4">
                  {issue.causes.length > 0 && (
                    <div className="bg-red-50 rounded-lg p-4">
                      <h4 className="font-semibold text-red-800 mb-2 flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Causes
                      </h4>
                      <ul className="text-sm text-red-700 space-y-1">
                        {issue.causes.map((cause, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-red-400">•</span>
                            {cause}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {issue.symptoms.length > 0 && (
                    <div className="bg-orange-50 rounded-lg p-4">
                      <h4 className="font-semibold text-orange-800 mb-2 flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Symptoms
                      </h4>
                      <ul className="text-sm text-orange-700 space-y-1">
                        {issue.symptoms.map((symptom, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-orange-400">•</span>
                            {symptom}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Example Complaints */}
                {issue.example_complaints.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      What Users Are Saying
                    </h4>
                    <div className="space-y-3">
                      {issue.example_complaints.slice(0, 3).map((complaint, i) => (
                        <blockquote key={i} className="border-l-3 border-gray-300 pl-3 py-1">
                          <p className="text-sm text-gray-700 italic">"{complaint.quote}"</p>
                          <footer className="text-xs text-gray-500 mt-1">
                            — {complaint.source}
                          </footer>
                        </blockquote>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommended Solutions */}
                {issue.recommended_solutions.length > 0 && (
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-semibold text-green-800 mb-3 flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Recommended Solutions
                    </h4>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
                      {issue.recommended_solutions.map((solution, i) => (
                        <button
                          key={i}
                          onClick={() => onAccessoryClick?.(solution.accessory)}
                          className="flex items-center justify-between bg-white rounded-lg px-3 py-2 border border-green-200 hover:border-green-400 hover:shadow-sm transition-all text-left"
                        >
                          <div>
                            <span className="text-sm font-medium text-gray-900">{solution.accessory}</span>
                            <span className="text-xs text-gray-500 block">{solution.type}</span>
                          </div>
                          <div className="text-right">
                            <span className={`text-sm font-semibold ${solution.sentiment >= 0.5 ? 'text-green-600' : solution.sentiment >= 0.2 ? 'text-green-500' : 'text-gray-600'}`}>
                              +{solution.sentiment.toFixed(2)}
                            </span>
                            <span className="text-xs text-gray-400 block">{solution.mentions} mentions</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
