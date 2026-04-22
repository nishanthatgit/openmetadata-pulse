/**
 * StatCard — single KPI metric card.
 */
interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
}

export function StatCard({ title, value, icon }: StatCardProps) {
  return (
    <div className="card">
      <div className="card__title">
        {icon} {title}
      </div>
      <div className="card__value">{value}</div>
    </div>
  );
}
