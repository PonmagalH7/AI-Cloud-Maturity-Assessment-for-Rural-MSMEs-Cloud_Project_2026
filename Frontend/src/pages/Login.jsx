import { useState } from "react";
import { signInWithRedirect, signOut } from "aws-amplify/auth";
import { Link } from "react-router-dom";

function Login() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
  setError("");
  setLoading(true);

  try {
    await signOut();
    await signInWithRedirect();
  } catch (err) {
    console.error("Cognito login failed:", err);
    setError(
      err?.message ||
        "Unable to start Cognito sign-in. Check the browser console."
    );
    setLoading(false);
  }
};
  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <p className="eyebrow">AI CLOUD MATURITY ASSESSMENT</p>
          <h1>Welcome Back</h1>
          <p>
            Sign in to continue your MSME cloud maturity assessment.
          </p>
        </div>

        <button
          type="button"
          className="primary-btn auth-submit"
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? "Connecting to AWS Cognito..." : "Sign in with AWS Cognito"}
        </button>

        {error && (
          <p role="alert" style={{ color: "red", marginTop: "12px" }}>
            {error}
          </p>
        )}

        <div className="auth-divider">
          <span>SECURE AUTHENTICATION</span>
        </div>

        <p className="auth-footer">
          Don't have an account?{" "}
          <Link to="/register">Create an account</Link>
        </p>

        <Link to="/" className="auth-back">
          ← Back to Home
        </Link>
      </div>
    </div>
  );
}

export default Login;