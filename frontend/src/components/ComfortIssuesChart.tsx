import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ComfortIssue } from '../api';

interface Props {
  issues: ComfortIssue[];
}

const COLORS = [
  '#ef4444', // red
  '#f97316', // orange
  '#eab308', // yellow
  '#22c55e', // green
  '#3b82f6', // blue
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
  '#f43f5e', // rose
];

export default function ComfortIssuesChart({ issues }: Props) {
  const chartData = issues.slice(0, 8).map((issue, index) => ({
    name: issue.display_name || issue.issue_type.replace(/_/g, ' '),
    count: issue.count,
    color: COLORS[index % COLORS.length]
  }));

  if (issues.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        No comfort issues found. Run the analyzers to process data.
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <XAxis type="number" />
            <YAxis 
              type="category" 
              dataKey="name" 
              width={100}
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              formatter={(value: number) => [`${value} mentions`, 'Count']}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px'
              }}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="mt-4 grid grid-cols-2 gap-2">
        {chartData.map((item, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: item.color }}
            />
            <span className="text-gray-600 truncate">{item.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
