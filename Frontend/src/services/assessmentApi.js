
import assessmentQuestions from "../data/assessmentQuestions";
import { apiRequest } from "./api";

export async function getAssessmentQuestions() {
  return assessmentQuestions;
}

export async function submitAssessment(submission) {
  return apiRequest("/api/assessments", {
    method: "POST",
    body: JSON.stringify(submission),
  });
}

export async function getAssessmentResult(assessmentId) {
  return apiRequest(`/api/assessments/${assessmentId}`);
}
