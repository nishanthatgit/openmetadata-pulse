/**
 * PlaceholderChart — sample Recharts area chart for ownership coverage.
 */
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const SAMPLE_DATA = [
  { day: 'Mon', coverage: 62 },
  { day: 'Tue', coverage: 65 },
  { day: 'Wed', coverage: 68 },
  { day: 'Thu', coverage: 71 },
  { day: 'Fri', coverage: 74 },
  { day: 'Sat', coverage: 73 },
  { day: 'Sun', coverage: 76 },
];

export function PlaceholderChart() {
  return (
    <div className="chart-container">
      <h3 className="chart-container__title">Ownership Coverage Trend</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={SAMPLE_DATA}>
          <defs>
            <linearGradient id="colorCoverage" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#7147E8" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#7147E8" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="day" stroke="#6B7280" fontSize={12} />
          <YAxis stroke="#6B7280" fontSize={12} domain={[0, 100]} unit="%" />
          <Tooltip
            contentStyle={{
              background: '#1C1F2E',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              color: '#F0F0F5',
            }}
          />
          <Area
            type="monotone"
            dataKey="coverage"
            stroke="#7147E8"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorCoverage)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
