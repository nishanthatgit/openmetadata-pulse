/**
 * Sidebar component — main navigation with Pulse branding.
 */

interface NavItem {
  icon: string;
  label: string;
  active?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { icon: '📊', label: 'Overview', active: true },
  { icon: '🔔', label: 'Events' },
  { icon: '👥', label: 'Ownership' },
  { icon: '✅', label: 'Data Quality' },
  { icon: '⚙️', label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__logo">P</div>
        <span className="sidebar__brand-text">Pulse</span>
      </div>
      <nav className="sidebar__nav">
        {NAV_ITEMS.map((item) => (
          <div
            key={item.label}
            className={`nav-item ${item.active ? 'nav-item--active' : ''}`}
          >
            <span className="nav-item__icon">{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>
    </aside>
  );
}
