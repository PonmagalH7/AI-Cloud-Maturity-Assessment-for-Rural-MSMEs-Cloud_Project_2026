import { signInWithRedirect } from "aws-amplify/auth";
import { Link } from "react-router-dom";

function Login() {
  const handleLogin = async () => {
    try {
      await signInWithRedirect();
    } catch (error) {
      console.error("Cognito login failed:", error);
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
        >
          Sign in with AWS Cognito
        </button>

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