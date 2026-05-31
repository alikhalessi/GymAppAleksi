import "./App.css";

const dashboardItems = [
  {
    label: "My Programs",
    description: "Plan structure placeholder",
  },
  {
    label: "Start Workout",
    description: "Session entry placeholder",
  },
  {
    label: "Exercise Library",
    description: "Movement examples placeholder",
  },
  {
    label: "Progress",
    description: "Analysis placeholder",
  },
];

function App() {
  return (
    <main className="app-shell">
      <header className="top-bar">
        <h1 className="brand">SetPilot</h1>
        <span className="phase-label">Sprint 1 scaffold</span>
      </header>

      <section className="dashboard" aria-labelledby="dashboard-title">
        <div className="intro">
          <h2 id="dashboard-title">Train from a clear plan.</h2>
          <p>
            SetPilot helps gym users follow structured workout programs, review
            movement examples, manage workout timing, and understand progress
            after each session.
          </p>
        </div>

        <div className="actions" aria-label="Dashboard placeholders">
          {dashboardItems.map((item) => (
            <button className="action-button" key={item.label} type="button">
              {item.label}
              <span>{item.description}</span>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
