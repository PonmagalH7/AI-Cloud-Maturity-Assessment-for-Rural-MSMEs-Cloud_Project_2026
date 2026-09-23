import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

function Results() {
  const storedResult = JSON.parse(
    localStorage.getItem("assessmentResult") || "null"
  );

  const results = useMemo(() => {
    if (!storedResult?.data) {
      return null;
    }

    const data = storedResult.data;

    const categoryScores = data.categoryScores || {};

    const categoryLabels = {
      infrastructure: "Infrastructure",
      process: "Process",
      people: "People",
      data: "Data",
      security: "Security",
    };

    const categoryData = Object.entries(categoryScores).map(
      ([category, score]) => ({
        name: categoryLabels[category] || category,
        score: Number(score),
      })
    );

    return {
      assessmentId: data.assessmentId,
      overallScore: Number(data.overallScore),
      maturityLevel: data.maturityLevel,
      categoryScores,
      categoryData,
      gaps: data.gaps || [],
      recommendation: data.recommendation || null,
      createdAt: data.createdAt,
    };
  }, [storedResult]);

  if (!results) {
    return (
      <div className="results-page">
        <div className="results-container empty-results">
          <h1>No Assessment Results</h1>

          <p>
            Please complete the cloud maturity assessment
            before viewing your results.
          </p>

          <Link to="/assessment" className="primary-button">
            Start Assessment →
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="results-page">
      <div className="results-container">

        {/* Header */}
        <div className="results-header">
          <div>
            <p className="assessment-label">
              CLOUD MATURITY RESULTS
            </p>

            <h1>Your Cloud Maturity Results</h1>

            <p>
              Your assessment results provide an overview of
              your organization's current cloud maturity.
            </p>
          </div>

          <Link to="/assessment" className="secondary-button">
            Retake Assessment
          </Link>
        </div>

        {/* Score Section */}
        <div className="results-overview">

          <div className="overall-score-card">
            <p>OVERALL MATURITY SCORE</p>

            <div className="large-score">
              {results.overallScore}
              <span>/100</span>
            </div>

            <div className="maturity-level">
              {results.maturityLevel}
            </div>

            <p className="score-description">
              This score represents the overall maturity of
              your business across the assessed cloud
              dimensions.
            </p>
          </div>

          <div className="summary-card">
            <h2>Assessment Summary</h2>

            <div className="summary-item">
              <span>Categories assessed</span>
              <strong>5</strong>
            </div>

            <div className="summary-item">
              <span>Questions answered</span>
              <strong>25</strong>
            </div>

            <div className="summary-item">
              <span>Maturity level</span>
              <strong>{results.maturityLevel}</strong>
            </div>
          </div>

        </div>

        {/* Category Scores */}
        <section className="results-section">

          <div className="section-heading">
            <p className="assessment-label">
              CATEGORY ANALYSIS
            </p>

            <h2>Cloud Maturity by Category</h2>

            <p>
              See how your business performed across each
              cloud maturity category.
            </p>
          </div>

          <div className="chart-card">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={results.categoryData}
                layout="vertical"
                margin={{
                  top: 10,
                  right: 30,
                  left: 20,
                  bottom: 10,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis
                  type="number"
                  domain={[0, 100]}
                />

                <YAxis
                  type="category"
                  dataKey="name"
                  width={140}
                />

                <Tooltip />

                <Bar
                  dataKey="score"
                  fill="#6366f1"
                  radius={[0, 8, 8, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

        </section>

        {/* Gaps */}
        <section className="results-section">

          <div className="section-heading">
            <p className="assessment-label">
              AREAS TO IMPROVE
            </p>

            <h2>Focus Areas</h2>

            <p>
              These categories have been identified as areas
              that may need additional attention.
            </p>
          </div>

          {results.gaps.length > 0 ? (
            <div className="focus-grid">

              {results.gaps.map((gap) => {
                const score =
                  results.categoryScores[gap];

                const displayName =
                  gap.charAt(0).toUpperCase() +
                  gap.slice(1);

                return (
                  <div className="focus-card" key={gap}>

                    <div className="focus-score">
                      {score}
                      <span>/100</span>
                    </div>

                    <h3>{displayName}</h3>

                    <p>
                      This category may benefit from
                      additional improvement and targeted
                      cloud adoption actions.
                    </p>

                  </div>
                );
              })}

            </div>
          ) : (
            <div className="summary-card">
              <h3>No major gaps identified</h3>
              <p>
                Your assessment did not identify categories
                below the current gap threshold.
              </p>
            </div>
          )}

        </section>

        {/* Recommendation Preview */}
        {results.recommendation && (
          <section className="results-section">

            <div className="section-heading">
              <p className="assessment-label">
                AI RECOMMENDATION
              </p>

              <h2>Recommended Next Steps</h2>
            </div>

            <div className="summary-card">

              <p>
                {results.recommendation.summary}
              </p>

              {Array.isArray(
                results.recommendation.priorities
              ) &&
                results.recommendation.priorities.length > 0 && (
                  <ol>
                    {results.recommendation.priorities.map(
                      (priority, index) => (
                        <li key={index}>
                          {priority}
                        </li>
                      )
                    )}
                  </ol>
                )}

            </div>

          </section>
        )}

        {/* Actions */}
        <section className="results-actions">

          <h2>What's Next?</h2>

          <p>
            Continue to the recommendations section to
            explore improvement actions for your business.
          </p>

          <div className="action-buttons">

            <Link
              to="/recommendations"
              className="primary-button"
            >
              View Recommendations →
            </Link>

            <Link
              to="/report"
              className="secondary-button"
            >
              View Report
            </Link>

          </div>

        </section>

      </div>
    </div>
  );
}

export default Results;