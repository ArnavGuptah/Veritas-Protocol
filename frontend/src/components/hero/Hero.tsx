import { motion } from "framer-motion";

export default function Hero() {

    return (

        <motion.div

            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}

            transition={{
                duration: 0.8,
            }}

            className="text-center"

        >

            <div className="mb-6 inline-flex rounded-full border border-cyan-500/20 bg-cyan-500/10 px-5 py-2 text-sm text-cyan-300">

                Blockchain-backed AI Verification

            </div>

            <h1 className="mx-auto max-w-5xl text-7xl font-black leading-tight">

                Verify AI Responses

                <br />

                With

                <span className="text-cyan-400">

                    {" "}Cryptographic Proof

                </span>

            </h1>

            <p className="mx-auto mt-8 max-w-3xl text-xl leading-9 text-zinc-400">

                Every response is traceable through retrieval,
                reasoning, graph construction and blockchain
                anchoring.

            </p>

        </motion.div>

    );

}