import { Link } from "react-router-dom";

function Recommendations() {
  const storedResult = JSON.parse(
    localStorage.getItem("assessmentResult") || "null"
  );

  const data = storedResult?.data;
  const recommendation = data?.recommendation;

  if (!data || !recommendation) {
    return (
      <div className="recommendations-page">
        <div className="recommendations-container empty-results">
          <h1>No Recommendations Available</h1>

          <p>
            Complete an assessment and receive your assessment
            results before viewing personalized recommendations.
          </p>

          <Link to="/results" className="primary-button">
            ← Back to Results
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="recommendations-page">
      <div className="recommendations-container">

        {/* Header */}
        <div className="recommendations-header">
          <div>
            <p className="assessment-label">
              AI-POWERED RECOMMENDATIONS
            </p>

            <h1>Improve Your Cloud Maturity</h1>

            <p>
              Explore practical next steps based on your
              assessment results.
            </p>
          </div>

          <Link
            to="/results"
            className="secondary-button"
          >
            ← Back to Results
          </Link>
        </div>

        {/* AI Recommendation */}
        <div className="ai-recommendation-banner">
          <div className="ai-icon">🤖</div>

          <div>
            <h3>Personalized Recommendation</h3>

            <p>
              {recommendation.summary}
            </p>

            {recommendation.source && (
              <small>
                Recommendation source: {recommendation.source}
              </small>
            )}
          </div>
        </div>

        {/* Priority Actions */}
        <section className="recommendations-section">

          <div className="section-heading">
            <p className="assessment-label">
              RECOMMENDED ACTIONS
            </p>

            <h2>Priority Improvement Areas</h2>

            <p>
              These are the recommended next steps based on
              your assessment.
            </p>
          </div>

          <div className="recommendations-grid">

            {Array.isArray(recommendation.priorities) &&
              recommendation.priorities.map(
                (priority, index) => (
                  <div
                    className="recommendation-card"
                    key={`${priority}-${index}`}
                  >

                    <div className="recommendation-top">
                      <span className="recommendation-dimension">
                        Priority {index + 1}
                      </span>

                      <span className="priority-badge high">
                        Recommended
                      </span>
                    </div>

                    <h3>
                      Step {index + 1}
                    </h3>

                    <p className="recommendation-description">
                      {priority}
                    </p>

                  </div>
                )
              )}

          </div>
        </section>

        {/* Roadmap */}
        <section className="roadmap-section">

          <div className="section-heading">
            <p className="assessment-label">
              CLOUD MATURITY ROADMAP
            </p>

            <h2>Suggested Next Steps</h2>
          </div>

          <div className="roadmap">

            <div className="roadmap-step">
              <div className="roadmap-number">1</div>

              <div>
                <h3>Assess</h3>
                <p>
                  Understand your current cloud maturity and
                  identify areas that need attention.
                </p>
              </div>
            </div>

            <div className="roadmap-line"></div>

            <div className="roadmap-step">
              <div className="roadmap-number">2</div>

              <div>
                <h3>Prioritize</h3>
                <p>
                  Focus on the recommended improvement actions
                  identified from your assessment.
                </p>
              </div>
            </div>

            <div className="roadmap-line"></div>

            <div className="roadmap-step">
              <div className="roadmap-number">3</div>

              <div>
                <h3>Implement</h3>
                <p>
                  Introduce improvements in manageable stages
                  according to your business needs.
                </p>
              </div>
            </div>

            <div className="roadmap-line"></div>

            <div className="roadmap-step">
              <div className="roadmap-number">4</div>

              <div>
                <h3>Improve</h3>
                <p>
                  Reassess your maturity periodically and
                  continue improving your digital capabilities.
                </p>
              </div>
            </div>

          </div>
        </section>

        {/* Actions */}
        <div className="recommendation-actions">

          <Link
            to="/assessment"
            className="secondary-button"
          >
            Retake Assessment
          </Link>

          <Link
            to="/report"
            className="primary-button"
          >
            Generate Report →
          </Link>

        </div>

      </div>
    </div>
  );
}

export default Recommendations;