import { Database, Shield, Boxes } from "lucide-react";

const stats = [
    {
        icon: Shield,
        title: "Tamper Proof",
        value: "Blockchain Verified",
    },
    {
        icon: Database,
        title: "Knowledge Graph",
        value: "Multi-hop Reasoning",
    },
    {
        icon: Boxes,
        title: "Evidence",
        value: "Replayable Pipeline",
    },
];

export default function HeroStats() {

    return (

        <div className="mt-16 grid grid-cols-3 gap-6">

            {stats.map((s) => (

                <div
                    key={s.title}
                    className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md"
                >

                    <s.icon
                        className="mb-4 text-cyan-400"
                    />

                    <h3 className="font-semibold">

                        {s.title}

                    </h3>

                    <p className="mt-2 text-sm text-zinc-400">

                        {s.value}

                    </p>

                </div>

            ))}

        </div>

    );

}