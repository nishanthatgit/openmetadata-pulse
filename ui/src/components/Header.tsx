/**
 * Header component — shows page title and live connection status.
 */
export function Header() {
  return (
    <header className="header">
      <h1 className="header__title">Community Dashboard</h1>
      <div className="header__status">
        <span className="status-dot" />
        <span>Live</span>
      </div>
    </header>
  );
}
