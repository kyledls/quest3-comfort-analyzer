import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { SourceDistribution } from '../api';

interface Props {
  sources: SourceDistribution[];
}

const COLORS = [
  '#ff4500', // Reddit orange
  '#ff9900', // Amazon orange
  '#ff0000', // YouTube red
  '#0071dc', // Best Buy blue
  '#00a6ff', // UploadVR blue
  '#6366f1', // Road to VR purple
  '#1877f2', // Meta blue
];

const SOURCE_LABELS: Record<string, string> = {
  reddit: 'Reddit',
  amazon: 'Amazon',
  youtube: 'YouTube',
  bestbuy: 'Best Buy',
  uploadvr: 'UploadVR',
  roadtovr: 'Road to VR',
  meta_forums: 'Meta Forums',
};

export default function SourcesChart({ sources }: Props) {
  const chartData = sources
    .filter(s => s.review_count > 0)
    .map((source, index) => ({
      name: SOURCE_LABELS[source.source_name] || source.source_name,
      value: source.review_count,
      color: COLORS[index % COLORS.length]
    }));

  const totalReviews = chartData.reduce((sum, item) => sum + item.value, 0);

  if (chartData.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        No data sources yet. Run the scrapers to collect data.
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={70}
              paddingAngle={2}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value: number) => [
                `${value} reviews (${((value / totalReviews) * 100).toFixed(1)}%)`,
                ''
              ]}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Source List */}
      <div className="mt-2 space-y-2">
        {chartData.map((item, index) => (
          <div key={index} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span className="text-gray-600">{item.name}</span>
            </div>
            <span className="font-medium text-gray-900">
              {item.value.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
