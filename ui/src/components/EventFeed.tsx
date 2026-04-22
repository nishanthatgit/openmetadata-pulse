/**
 * EventFeed — real-time event list (placeholder data).
 */

interface EventItem {
  id: number;
  type: 'created' | 'updated' | 'deleted';
  entity: string;
  time: string;
}

const MOCK_EVENTS: EventItem[] = [
  { id: 1, type: 'created', entity: 'analytics_warehouse.analytics_db.raw.page_views', time: '2 min ago' },
  { id: 2, type: 'updated', entity: 'customer_platform.customers_db.public.users', time: '5 min ago' },
  { id: 3, type: 'deleted', entity: 'finance_system.finance_db.reporting.temp_report', time: '12 min ago' },
  { id: 4, type: 'created', entity: 'analytics_warehouse.analytics_db.curated.daily_active_users', time: '18 min ago' },
  { id: 5, type: 'updated', entity: 'customer_platform.customers_db.public.payments', time: '25 min ago' },
];

const TYPE_LABELS = {
  created: { icon: '+', label: 'Created' },
  updated: { icon: '~', label: 'Updated' },
  deleted: { icon: '×', label: 'Deleted' },
};

export function EventFeed() {
  return (
    <div className="event-feed">
      <h3 className="event-feed__title">🔔 Recent Events</h3>
      {MOCK_EVENTS.map((evt) => (
        <div key={evt.id} className="event-item">
          <div className={`event-item__icon event-item__icon--${evt.type}`}>
            {TYPE_LABELS[evt.type].icon}
          </div>
          <div className="event-item__content">
            <div className="event-item__text">
              <strong>{TYPE_LABELS[evt.type].label}</strong>{' '}
              <code style={{ fontSize: '0.8rem', color: '#9CA3AF' }}>{evt.entity}</code>
            </div>
            <div className="event-item__time">{evt.time}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
