import { api } from "./client";

export interface QueryRequest {
  question: string;
}

export interface QueryResponse {
  record_id: string;
}

export async function verifyQuestion(question: string) {
  const { data } = await api.post<QueryResponse>(
    "/query",
    {
      question,
    }
  );

  return data;
}