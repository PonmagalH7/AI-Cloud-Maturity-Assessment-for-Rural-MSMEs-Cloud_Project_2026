import { fetchAuthSession } from "aws-amplify/auth";

const API_BASE_URL = "http://localhost:3000";

async function apiRequest(endpoint, options = {}) {
  const session = await fetchAuthSession();

  const accessToken = session.tokens?.accessToken?.toString();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken
        ? {
            Authorization: `Bearer ${accessToken}`,
          }
        : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `API request failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}

export { API_BASE_URL, apiRequest };