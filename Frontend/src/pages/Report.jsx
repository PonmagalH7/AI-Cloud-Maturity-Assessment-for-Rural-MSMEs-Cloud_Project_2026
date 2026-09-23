import { useMemo } from "react";
import { Link } from "react-router-dom";

function Report() {
  const profile = useMemo(() => {
    const saved = localStorage.getItem("msmeProfile");
    return saved ? JSON.parse(saved) : {};
  }, []);

  const storedResult = useMemo(() => {
    const saved = localStorage.getItem("assessmentResult");
    return saved ? JSON.parse(saved) : null;
  }, []);

  const data = storedResult?.data;

  const categoryLabels = {
    infrastructure: "Infrastructure",
    process: "Process",
    people: "People",
    data: "Data",
    security: "Security",
  };

  const categoryScores = data?.categoryScores || {};

  const gaps = data?.gaps || [];

  const recommendation = data?.recommendation || null;

  if (!data) {
    return (
      <div className="page-shell">
        <div className="empty-state">
          <h1>No Assessment Report Available</h1>

          <p>
            Complete the cloud maturity assessment and receive
            your assessment results before viewing the report.
          </p>

          <Link to="/assessment" className="primary-btn">
            Start Assessment
          </Link>
        </div>
      </div>
    );
  }

  const generatedDate = data.createdAt
    ? new Date(data.createdAt).toLocaleDateString()
    : new Date().toLocaleDateString();

  return (
    <div className="page-shell report-page">
      <div className="report-container">

        {/* Header */}
        <div className="report-header">
          <div>
            <p className="eyebrow">
              AI CLOUD MATURITY ASSESSMENT
            </p>

            <h1>MSME Cloud Maturity Report</h1>

            <p>
              A summary of your organization's current cloud
              readiness, maturity level, and improvement areas.
            </p>
          </div>

          <div className="report-date">
            <span>Assessment Date</span>
            <strong>{generatedDate}</strong>
          </div>
        </div>

        {/* Business Profile */}
        <section className="report-section company-summary">
          <div>
            <h2>Business Profile</h2>

            <div className="profile-grid">

              <div>
                <span>Business Name</span>
                <strong>
                  {profile.businessName || "Not provided"}
                </strong>
              </div>

              <div>
                <span>Owner / Manager</span>
                <strong>
                  {profile.ownerName || "Not provided"}
                </strong>
              </div>

              <div>
                <span>Business Type</span>
                <strong>
                  {profile.businessType || "Not provided"}
                </strong>
              </div>

              <div>
                <span>Industry</span>
                <strong>
                  {profile.industry || "Not provided"}
                </strong>
              </div>

              <div>
                <span>Location</span>
                <strong>
                  {profile.location || "Not provided"}
                </strong>
              </div>

              <div>
                <span>Employees</span>
                <strong>
                  {profile.employees || "Not provided"}
                </strong>
              </div>

            </div>
          </div>
        </section>

        {/* Overall Score */}
        <section className="report-section score-summary">

          <div className="score-circle">
            <strong>{data.overallScore}</strong>
            <span>/100</span>
          </div>

          <div>
            <p className="eyebrow">
              OVERALL MATURITY SCORE
            </p>

            <h2>{data.maturityLevel}</h2>

            <p>
              Your organization currently demonstrates a{" "}
              <strong>
                {data.maturityLevel?.toLowerCase()}
              </strong>{" "}
              level of cloud maturity based on the completed
              assessment.
            </p>
          </div>

        </section>

        {/* Category Results */}
        <section className="report-section">

          <div className="section-heading">
            <div>
              <p className="eyebrow">
                ASSESSMENT RESULTS
              </p>

              <h2>Category-wise Maturity</h2>
            </div>
          </div>

          <div className="dimension-report">

            {Object.entries(categoryScores).map(
              ([category, score]) => (
                <div
                  className="dimension-row"
                  key={category}
                >

                  <div className="dimension-info">
                    <strong>
                      {categoryLabels[category] || category}
                    </strong>

                    <span>{score}/100</span>
                  </div>

                  <div className="dimension-progress">
                    <div
                      className="dimension-progress-fill"
                      style={{
                        width: `${Number(score)}%`,
                      }}
                    />
                  </div>

                </div>
              )
            )}

          </div>
        </section>

        {/* Gap Analysis */}
        <section className="report-section">

          <div className="section-heading">
            <div>
              <p className="eyebrow">
                GAP ANALYSIS
              </p>

              <h2>Priority Improvement Areas</h2>
            </div>
          </div>

          {gaps.length > 0 ? (
            <div className="gap-list">

              {gaps.map((gap, index) => (
                <div
                  className="gap-item"
                  key={gap}
                >

                  <div className="gap-number">
                    {index + 1}
                  </div>

                  <div className="gap-content">
                    <strong>
                      {categoryLabels[gap] || gap}
                    </strong>

                    <p>
                      This category has been identified as
                      an area requiring additional attention.
                    </p>
                  </div>

                </div>
              ))}

            </div>
          ) : (
            <div className="success-box">

              <strong>
                No major gaps identified.
              </strong>

              <p>
                Continue maintaining your current digital
                and cloud capabilities and reassess your
                maturity periodically.
              </p>

            </div>
          )}

        </section>

        {/* AI Recommendation */}
        {recommendation && (
          <section className="report-section ai-note">

            <div>
              <p className="eyebrow">
                AI-POWERED ANALYSIS
              </p>

              <h2>Personalized Recommendations</h2>

              <p>
                {recommendation.summary}
              </p>

              {Array.isArray(
                recommendation.priorities
              ) &&
                recommendation.priorities.length > 0 && (
                  <ol>
                    {recommendation.priorities.map(
                      (priority, index) => (
                        <li key={index}>
                          {priority}
                        </li>
                      )
                    )}
                  </ol>
                )}
            </div>

            <Link
              to="/recommendations"
              className="secondary-btn"
            >
              View Recommendations
            </Link>

          </section>
        )}

        {/* Roadmap */}
        <section className="report-section">

          <div className="section-heading">
            <div>
              <p className="eyebrow">
                NEXT STEPS
              </p>

              <h2>Recommended Transformation Roadmap</h2>
            </div>
          </div>

          <div className="roadmap-report">

            <div className="roadmap-step">
              <span>01</span>

              <div>
                <strong>Address Priority Gaps</strong>

                <p>
                  Focus on the categories identified by
                  the assessment as areas for improvement.
                </p>
              </div>
            </div>

            <div className="roadmap-step">
              <span>02</span>

              <div>
                <strong>Implement Recommendations</strong>

                <p>
                  Follow the personalized recommendations
                  provided for your business.
                </p>
              </div>
            </div>

            <div className="roadmap-step">
              <span>03</span>

              <div>
                <strong>Strengthen Cloud Foundations</strong>

                <p>
                  Improve your infrastructure, process,
                  people, data, and security capabilities.
                </p>
              </div>
            </div>

            <div className="roadmap-step">
              <span>04</span>

              <div>
                <strong>Continuously Improve</strong>

                <p>
                  Reassess your maturity periodically and
                  track your progress over time.
                </p>
              </div>
            </div>

          </div>
        </section>

        {/* Actions */}
        <div className="report-actions">

          <Link
            to="/results"
            className="secondary-btn"
          >
            Back to Results
          </Link>

          <button
            className="primary-btn"
            onClick={() => window.print()}
          >
            Print Report
          </button>

        </div>

      </div>
    </div>
  );
}

export default Report;