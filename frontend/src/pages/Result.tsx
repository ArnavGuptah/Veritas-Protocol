import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import AnswerCard from "../components/common/AnswerCard";
import BlockchainCard from "../components/blockchain/BlockchainCard";
import ReplayTimeline from "../components/replay/ReplayTimeline";
import KnowledgeGraphCard from "../components/graph/KnowledgeGraphCard";

import {
  getRecord,
  verifyRecord,
  type ProofRecord,
  type VerificationResponse,
} from "../api/query";

export default function Result() {
  const { id } = useParams<{ id: string }>();

  const [record, setRecord] = useState<ProofRecord | null>(null);
  const [verification, setVerification] =
    useState<VerificationResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;

    const recordId = id;

    async function load() {
      try {
        setLoading(true);

        const [recordData, verificationData] = await Promise.all([
          getRecord(recordId),
          verifyRecord(recordId),
        ]);

        setRecord(recordData);
        setVerification(verificationData);
      } catch (err) {
        console.error(err);
        setError("Unable to load verification proof.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090B] text-white flex items-center justify-center">
        <p className="text-zinc-400">
          Loading verification proof...
        </p>
      </div>
    );
  }

  if (error || !record || !verification) {
    return (
      <div className="min-h-screen bg-[#09090B] text-white flex items-center justify-center">
        <p className="text-red-400">
          {error || "Verification proof unavailable."}
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090B] text-white">
      <div className="mx-auto max-w-7xl p-10">
        <div className="grid grid-cols-12 gap-8">

          <div className="col-span-8 space-y-8">
            <AnswerCard record={record} verification={verification} />
            <ReplayTimeline stages={record.stages} />
          </div>

          <div className="col-span-4 space-y-8">
            <BlockchainCard
              verification={verification}
              rootHash={record.root_hash}
            />

            <KnowledgeGraphCard
              evidence={record.evidence}
            />
          </div>

        </div>
      </div>
    </div>
  );
}