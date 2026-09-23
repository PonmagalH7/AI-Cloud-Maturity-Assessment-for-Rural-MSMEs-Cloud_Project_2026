import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import assessmentQuestions from "../data/assessmentQuestions";
import { getAssessmentQuestions, submitAssessment } from "../services/assessmentApi";

const answerValues = [0, 1, 2, 3, 4];

function Assessment() {
  const navigate = useNavigate();

  const [questions, setQuestions] = useState(assessmentQuestions);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadQuestions() {
      try {
        const apiQuestions = await getAssessmentQuestions();

        if (Array.isArray(apiQuestions) && apiQuestions.length === 25) {
          setQuestions(apiQuestions);
        } else {
          setQuestions(assessmentQuestions);
        }
      } catch {
        // Backend may not be available yet.
        // Use the exact local 25-question set.
        setQuestions(assessmentQuestions);
      } finally {
        setLoading(false);
      }
    }

    loadQuestions();
  }, []);

  const currentQuestion = questions[currentIndex];

  const answeredCount = Object.keys(answers).length;

  const progress = useMemo(() => {
    if (!questions.length) return 0;

    return Math.round(
      ((currentIndex + 1) / questions.length) * 100
    );
  }, [currentIndex, questions.length]);

  const handleAnswer = (value) => {
    setAnswers((previous) => ({
      ...previous,
      [currentQuestion.id]: value,
    }));
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((previous) => previous + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((previous) => previous - 1);
    }
  };

  const handleSubmit = async () => {
    if (answeredCount !== questions.length) {
      setError("Please answer every question before submitting.");
      return;
    }

    setError("");
    setSubmitting(true);
const savedProfile = JSON.parse(
  localStorage.getItem("msmeProfile") || "{}"
);

const submission = {
  responses: {
    ...answers,
  },
  business_type: savedProfile.businessType || "",
};

    // Keep a local copy for development/testing.
    localStorage.setItem(
      "assessmentSubmission",
      JSON.stringify(submission)
    );

    try {
      const result = await submitAssessment(submission);

      if (result) {
        localStorage.setItem(
          "assessmentResult",
          JSON.stringify(result)
        );
      }
    } catch {
      // Backend may not be connected yet.
      // Keep the local submission so the frontend flow continues.
    } finally {
      setSubmitting(false);
      navigate("/results");
    }
  };

  if (loading) {
    return (
      <div className="page-shell">
        <div className="assessment-container">
          <div className="assessment-card">
            <h2>Loading Assessment...</h2>
            <p>Please wait while the questionnaire is prepared.</p>
          </div>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="page-shell">
        <div className="assessment-container">
          <div className="assessment-card">
            <h2>No Questions Available</h2>
            <p>Unable to load the assessment questionnaire.</p>
          </div>
        </div>
      </div>
    );
  }

  const selectedValue = answers[currentQuestion.id];

  return (
    <div className="page-shell assessment-page">
      <div className="assessment-container">

        {/* Header */}
        <div className="assessment-header">
          <div>
            <p className="eyebrow">CLOUD MATURITY ASSESSMENT</p>

            <h1>Assess Your Business</h1>

            <p>
              Answer all 25 questions using a value from 0 to 4.
            </p>
          </div>

          <div className="assessment-counter">
            <strong>
              {currentIndex + 1}
            </strong>

            <span>
              / {questions.length}
            </span>
          </div>
        </div>

        {/* Progress */}
        <div className="assessment-progress-wrapper">
          <div className="assessment-progress-info">
            <span>
              Question {currentIndex + 1} of {questions.length}
            </span>

            <span>
              {answeredCount} answered
            </span>
          </div>

          <div className="assessment-progress">
            <div
              className="assessment-progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question */}
        <div className="assessment-card">

          <div className="question-meta">
            <span className="question-dimension">
              {currentQuestion.dimension}
            </span>

            <span className="question-id">
              {currentQuestion.id}
            </span>
          </div>

          <h2>
            {currentQuestion.text}
          </h2>

          <p className="answer-instruction">
            Select one value from 0 to 4.
          </p>

          <div className="answer-options">
            {answerValues.map((value) => (
              <button
                key={value}
                type="button"
                className={`answer-option ${
                  selectedValue === value ? "selected" : ""
                }`}
                onClick={() => handleAnswer(value)}
              >
                <span className="answer-number">
                  {value}
                </span>
              </button>
            ))}
          </div>

          <div className="answer-scale">
            <span>0</span>

            <span>1</span>

            <span>2</span>

            <span>3</span>

            <span>4</span>
          </div>

          {error && (
            <div className="assessment-error">
              {error}
            </div>
          )}

          {/* Navigation */}
          <div className="assessment-navigation">

            <button
              type="button"
              className="secondary-btn"
              onClick={handlePrevious}
              disabled={currentIndex === 0}
            >
              ← Previous
            </button>

            {currentIndex < questions.length - 1 ? (
              <button
                type="button"
                className="primary-btn"
                onClick={handleNext}
                disabled={selectedValue === undefined}
              >
                Next →
              </button>
            ) : (
              <button
                type="button"
                className="primary-btn"
                onClick={handleSubmit}
                disabled={
                  selectedValue === undefined || submitting
                }
              >
                {submitting
                  ? "Submitting..."
                  : "Submit Assessment"}
              </button>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}

export default Assessment;