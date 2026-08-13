import { motion } from "framer-motion";
import {
    Database,
    Search,
    Network,
    ShieldCheck,
    Blocks,
} from "lucide-react";

const steps = [
    {
        icon: Search,
        title: "Retrieval",
    },
    {
        icon: Database,
        title: "Evidence",
    },
    {
        icon: Network,
        title: "Knowledge Graph",
    },
    {
        icon: ShieldCheck,
        title: "Verification",
    },
    {
        icon: Blocks,
        title: "Blockchain",
    },
];

export default function VerificationPipeline() {

    return (

        <div className="mt-24 flex justify-center">

            <div className="flex gap-10">

                {steps.map((step, index) => {

                    const Icon = step.icon;

                    return (

                        <motion.div
                            key={step.title}

                            initial={{
                                opacity: 0,
                                y: 30,
                            }}

                            animate={{
                                opacity: 1,
                                y: 0,
                            }}

                            transition={{
                                delay: index * 0.25,
                            }}

                            className="flex flex-col items-center"
                        >

                            <motion.div

                                animate={{
                                    boxShadow: [
                                        "0 0 0px #22d3ee",
                                        "0 0 30px #22d3ee",
                                        "0 0 0px #22d3ee",
                                    ],
                                }}

                                transition={{
                                    repeat: Infinity,
                                    duration: 2,
                                    delay: index * .3,
                                }}

                                className="flex h-20 w-20 items-center justify-center rounded-full border border-cyan-500 bg-zinc-900"

                            >

                                <Icon
                                    size={32}
                                    className="text-cyan-400"
                                />

                            </motion.div>

                            <p className="mt-4 text-sm text-zinc-300">

                                {step.title}

                            </p>

                        </motion.div>

                    );

                })}

            </div>

        </div>

    );

}