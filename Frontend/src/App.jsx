import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Assessment from "./pages/Assessment";
import Results from "./pages/Results";
import Recommendations from "./pages/Recommendations";
import Profile from "./pages/Profile";
import Register from "./pages/Register";
import Login from "./pages/Login";
import ProtectedRoute from "./ProtectedRoute";
import Report from "./pages/Report";
import "./App.css";

function Home() {
  return (
    <div className="app">
      <nav className="navbar">
        <h2>CloudMaturity</h2>

        <div className="nav-links">
          <Link to="/login">Login</Link>

          <Link to="/register" className="register-btn">
            Register
          </Link>
        </div>
      </nav>

      <main className="hero">
        <div className="hero-content">
          <p className="tag">AI-POWERED CLOUD ASSESSMENT</p>

          <h1>
            Discover Your
            <br />
            <span>Cloud Maturity</span>
          </h1>

          <p className="description">
            Assess your MSME's cloud readiness, identify digital
            gaps, and receive personalized recommendations for
            successful cloud adoption.
          </p>

          <div className="hero-buttons">
            <Link to="/register" className="primary-btn">
              Start Assessment →
            </Link>

            <Link to="/login" className="secondary-btn">
              Already registered?
            </Link>
          </div>
        </div>

        <div className="score-card">
          <h3>Cloud Maturity</h3>

          <div className="score-circle">
            <span>?</span>
            <small>/ 100</small>
          </div>

          <p>
            Complete the assessment to discover your
            current cloud maturity level.
          </p>
        </div>
      </main>

      <section className="features">
        <div className="feature-card">
          <div className="feature-icon">📊</div>

          <h3>Assess</h3>

          <p>
            Evaluate your business's cloud readiness across
            multiple dimensions.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🤖</div>

          <h3>Analyze</h3>

          <p>
            AI-powered analysis identifies digital and
            cloud adoption gaps.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🚀</div>

          <h3>Improve</h3>

          <p>
            Receive practical recommendations and a roadmap
            for cloud adoption.
          </p>
        </div>
      </section>
    </div>
  );
}



function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />

        <Route path="/login" element={<Login />} />

        <Route path="/register" element={<Register />} />

        <Route
  path="/profile"
  element={
    <ProtectedRoute>
      <Profile />
    </ProtectedRoute>
  }
/>

<Route
  path="/assessment"
  element={
    <ProtectedRoute>
      <Assessment />
    </ProtectedRoute>
  }
/>

<Route
  path="/results"
  element={
    <ProtectedRoute>
      <Results />
    </ProtectedRoute>
  }
/>

<Route
  path="/recommendations"
  element={
    <ProtectedRoute>
      <Recommendations />
    </ProtectedRoute>
  }
/>

        <Route path="/report" element={<Report />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;