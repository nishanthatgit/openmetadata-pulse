import './App.css';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { StatCard } from './components/StatCard';
import { PlaceholderChart } from './components/PlaceholderChart';
import { EventFeed } from './components/EventFeed';

function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <Header />
      <main className="main-content">
        <div className="page-content">
          <h2 className="page-title">Overview</h2>

          {/* KPI Stats */}
          <div className="stats-grid">
            <StatCard icon="📋" title="Total Tables" value={54} />
            <StatCard icon="👤" title="Ownership" value="76%" />
            <StatCard icon="✅" title="DQ Pass Rate" value="92%" />
            <StatCard icon="🔔" title="Events Today" value={23} />
          </div>

          {/* Charts */}
          <PlaceholderChart />

          {/* Event Feed */}
          <EventFeed />
        </div>
      </main>
    </div>
  );
}

export default App;
