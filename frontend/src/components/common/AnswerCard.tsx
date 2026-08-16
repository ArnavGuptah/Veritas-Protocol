import GlassCard from "./GlassCard";
import type {
  ProofRecord,
  VerificationResponse,
} from "../../api/query";

interface Props {
  record: ProofRecord;
  verification: VerificationResponse;
}

function verdictLabel(status: VerificationResponse["status"]) {
  switch (status) {
    case "fully_verified":
      return "FULLY VERIFIED";
    case "anchor_pending":
      return "ANCHOR PENDING";
    case "valid_local_only":
      return "LOCALLY VERIFIED";
    case "tampered":
      return "TAMPERED";
    case "blockchain_mismatch":
      return "BLOCKCHAIN MISMATCH";
    default:
      return "VERIFICATION RESULT";
  }
}

export default function AnswerCard({
  record,
  verification,
}: Props) {
  return (
    <GlassCard>
      <div className="flex items-start justify-between gap-6">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-zinc-500">
            Verification
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {verdictLabel(verification.status)}
          </h2>
        </div>

        <div className="rounded-full bg-cyan-400/10 px-4 py-2 text-cyan-300">
          {(record.verdict.confidence_score * 100).toFixed(0)}% confidence
        </div>
      </div>

      <div className="mt-8">
        <p className="mb-3 text-sm uppercase tracking-[0.15em] text-zinc-500">
          Question
        </p>

        <p className="text-lg text-zinc-300">
          {record.question}
        </p>
      </div>

      <div className="mt-8">
        <p className="mb-3 text-sm uppercase tracking-[0.15em] text-zinc-500">
          Answer
        </p>

        <p className="text-xl leading-8 text-zinc-100">
          {record.generator_answer}
        </p>
      </div>

      <div className="mt-10">
        <p className="mb-4 text-sm uppercase tracking-[0.15em] text-zinc-500">
          Claims
        </p>

        <div className="space-y-3">
          {record.fact_checks.map((factCheck) => (
            <div
              key={factCheck.claim}
              className="rounded-xl border border-white/10 bg-white/[0.03] p-4"
            >
              <div className="flex gap-3">
                <span
                  className={
                    factCheck.supported
                      ? "text-green-400"
                      : "text-red-400"
                  }
                >
                  {factCheck.supported ? "✓" : "✕"}
                </span>

                <p className="text-zinc-300">
                  {factCheck.claim}
                </p>
              </div>

              {factCheck.supporting_evidence_ids.length > 0 && (
                <p className="mt-2 text-xs text-zinc-500">
                  Evidence:{" "}
                  {factCheck.supporting_evidence_ids.join(", ")}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </GlassCard>
  );
}