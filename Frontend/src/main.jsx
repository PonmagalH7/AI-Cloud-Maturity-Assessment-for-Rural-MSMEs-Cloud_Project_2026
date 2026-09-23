import "aws-amplify/auth/enable-oauth-listener";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Amplify } from "aws-amplify";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./AuthContext";

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: "ap-south-1_BQoeXub6X",
      userPoolClientId: "4t9ijroqmv588ee19hvmvf5s22",
      loginWith: {
        oauth: {
          domain: "ap-south-1bqoexub6x.auth.ap-south-1.amazoncognito.com",
          scopes: ["openid", "email"],
          redirectSignIn: ["http://localhost:5173/"],
          redirectSignOut: ["http://localhost:5173/"],
          responseType: "code",
        },
      },
    },
  },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>
);