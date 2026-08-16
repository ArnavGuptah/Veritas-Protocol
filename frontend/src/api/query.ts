import { api } from "./client";

export interface QueryRequest {question: string;}

export interface QueryResponse {
  status: string;
  record_id: string;
  question: string;
  answer: string;
  confidence_score: number;
  confidence_level: string;
  root_hash: string;
  anchored: boolean;
  tx_hash?: string | null;
  block_number?: number | null;
}

export interface ProofRecord {
  record_id: string;
  question: string;
  created_at: number;

  evidence: Array<{
    chunk_id: string;
    text: string;
    source: string;
    similarity: number;
    bm25_score: number;
    fused_score: number;
    document_hash: string;
  }>;

  generator_answer: string;

  challenges: Array<{
    challenge_id: string;
    target_claim: string;
    objection: string;
    severity: number;
    resolved: boolean;
    resolution_note?: string | null;
  }>;

  fact_checks: Array<{
    claim: string;
    supported: boolean;
    supporting_evidence_ids: string[];
    contradicting_evidence_ids: string[];
    notes: string;
  }>;

  verdict: {
    verdict: string;
    confidence_score: number;
    confidence_level: string;
    rationale: string;
  };

  stages: Array<{
    stage: string;
    started_at: number;
    finished_at: number;
    payload: Record<string, unknown>;
    input_hash: string;
    output_hash: string;
  }>;

  root_hash: string;

  chain_anchor?: {
    status?: string;
    tx_hash?: string;
    transaction_hash?: string;
    block_number?: number | null;
  } | null;
}

export interface VerificationResponse {
  record_id: string;
  status:
    | "fully_verified"
    | "anchor_pending"
    | "valid_local_only"
    | "blockchain_mismatch"
    | "tampered";

  local_proof: {
    valid: boolean;
    stored_root_hash: string;
    computed_root_hash: string;
    tampered_stage: string | null;
    message: string;
  };

  blockchain: {
    anchored: boolean;
    verified: boolean;
    status: string;
    tx_hash: string | null;
    record: {
      proof_id: string;
      root_hash: string;
      timestamp: number;
      verifier_signature: string;
      submitter: string;
    } | null;
  };
}

export async function verifyQuestion(
  question: string,
): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>(
    "/query",
    { question },
  );

  return data;
}

export async function getRecord(
  recordId: string,
): Promise<ProofRecord> {
  const { data } = await api.get<ProofRecord>(
    `/records/${recordId}`,
  );

  return data;
}

export async function verifyRecord(
  recordId: string,
): Promise<VerificationResponse> {
  const { data } = await api.get<VerificationResponse>(
    `/records/${recordId}/verify`,
  );

  return data;
}