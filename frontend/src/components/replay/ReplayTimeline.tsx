import GlassCard from "../common/GlassCard";

interface Stage {
  stage: string;
  started_at: number;
  finished_at: number;
}

interface Props {
  stages: Stage[];
}

export default function ReplayTimeline({ stages }: Props) {
  return (
    <GlassCard>
      <h3 className="text-2xl font-semibold">
        Proof Replay
      </h3>

      <div className="mt-8 space-y-5">
        {stages.map((stage, index) => (
          <div
            key={`${stage.stage}-${index}`}
            className="flex items-center gap-4"
          >
            <div className="h-3 w-3 rounded-full bg-cyan-400" />

            <div className="flex-1">
              <p className="capitalize text-zinc-200">
                {stage.stage.replace("_", " ")}
              </p>

              <p className="text-xs text-zinc-500">
                {(
                  stage.finished_at - stage.started_at
                ).toFixed(3)}s
              </p>
            </div>

            <span className="text-xs text-green-400">
              ✓
            </span>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}