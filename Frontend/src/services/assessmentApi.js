import { apiRequest } from "./api";

export async function getAssessmentQuestions() {
  return apiRequest("/questions");
}

export async function submitAssessment(responses) {
  return apiRequest("/api/assessments", {
    method: "POST",
    body: JSON.stringify({
      responses,
    }),
  });
}

export async function getAssessmentResult(assessmentId) {
  return apiRequest(`/api/assessments/${assessmentId}`);
}