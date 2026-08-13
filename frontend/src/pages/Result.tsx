import AnswerCard from "../components/common/AnswerCard.tsx";
import BlockchainCard from "../components/blockchain/BlockchainCard.tsx";
import KnowledgeGraphCard from "../components/graph/KnowledgeGraphCard.tsx";
import ReplayTimeline from "../components/replay/ReplayTimeline.tsx";

export default function Result() {

    return (

        <div className="min-h-screen bg-[#09090B] text-white">

            <div className="mx-auto max-w-7xl p-10">

                <div className="grid grid-cols-12 gap-8">

                    <div className="col-span-8">

                        <AnswerCard />

                        <ReplayTimeline />

                    </div>

                    <div className="col-span-4 space-y-8">

                        <BlockchainCard />

                        <KnowledgeGraphCard />

                    </div>

                </div>

            </div>

        </div>

    );

}