import GlassCard from "../common/GlassCard";

interface Evidence {
  chunk_id: string;
  source: string;
  text: string;
  fused_score: number;
}

interface Props {
  evidence: Evidence[];
}

export default function KnowledgeGraphCard({
  evidence,
}: Props) {
  return (
    <GlassCard>
      <h3 className="text-2xl font-semibold">
        Evidence
      </h3>

      <div className="mt-6 space-y-4">
        {evidence.slice(0, 5).map((item) => (
          <div
            key={item.chunk_id}
            className="rounded-xl border border-white/10 bg-white/[0.03] p-4"
          >
            <p className="text-sm text-cyan-300">
              {item.source}
            </p>

            <p className="mt-2 text-sm leading-6 text-zinc-400">
              {item.text}
            </p>

            <p className="mt-3 text-xs text-zinc-600">
              {item.chunk_id} · relevance{" "}
              {(item.fused_score * 100).toFixed(1)}%
            </p>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}