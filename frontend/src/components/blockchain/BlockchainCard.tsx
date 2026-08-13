import GlassCard from "../common/GlassCard";

export default function BlockchainCard(){

return(

<GlassCard>

<h3 className="text-2xl font-semibold">

Blockchain

</h3>

<div className="mt-8 space-y-5">

<div>

<p className="text-zinc-500">

Status

</p>

<p className="text-green-400">

Verified ✓

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

Transaction

</p>

<p className="break-all text-cyan-400">

0xf5dfb219565abca2d75123896cd809...

</p>

</div>

</div>

</GlassCard>

)

}