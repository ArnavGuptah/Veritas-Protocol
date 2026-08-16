import GlassCard from "../common/GlassCard";
import type { VerificationResponse } from "../../api/query";

interface Props {
  verification: VerificationResponse;
  rootHash: string;
}

export default function BlockchainCard({
  verification,
  rootHash,
}: Props) {
  const blockchain = verification.blockchain;

  return (
    <GlassCard>
      <h3 className="text-2xl font-semibold">
        Proof Verification
      </h3>

      <div className="mt-8 space-y-5">

        <div>
          <p className="text-zinc-500">
            Local proof
          </p>

          <p className="text-green-400">
            {verification.local_proof.valid
              ? "Valid ✓"
              : "Tampered ✕"}
          </p>
        </div>

        <div>
          <p className="text-zinc-500">
            Blockchain
          </p>

          <p
            className={
              blockchain.verified
                ? "text-green-400"
                : blockchain.status === "pending"
                ? "text-yellow-400"
                : "text-zinc-400"
            }
          >
            {blockchain.verified
              ? "Confirmed ✓"
              : blockchain.status === "pending"
              ? "Pending"
              : "Not anchored"}
          </p>
        </div>

        <div>
          <p className="text-zinc-500">
            Network
          </p>

          <p>
            Ethereum Sepolia
          </p>
        </div>

        <div>
          <p className="text-zinc-500">
            Root hash
          </p>

          <p className="break-all text-xs text-zinc-300">
            {rootHash}
          </p>
        </div>

        {blockchain.tx_hash && (
          <div>
            <p className="text-zinc-500">
              Transaction
            </p>

            <p className="break-all text-xs text-cyan-400">
              {blockchain.tx_hash}
            </p>
          </div>
        )}

        {blockchain.record && (
          <div>
            <p className="text-zinc-500">
              Block
            </p>

            <p className="text-zinc-200">
              On-chain proof confirmed
            </p>
          </div>
        )}

      </div>
    </GlassCard>
  );
}