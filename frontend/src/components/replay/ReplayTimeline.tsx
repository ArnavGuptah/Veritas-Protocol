import GlassCard from "../common/GlassCard";

const steps=[

"Query",

"Retrieve",

"Embedding",

"Graph",

"Verification",

"Blockchain"

];

export default function ReplayTimeline(){

return(

<GlassCard>

<h3 className="text-2xl font-semibold">

Pipeline Replay

</h3>

<div className="mt-8 space-y-6">

{steps.map(step=>(

<div
key={step}
className="flex items-center gap-5"
>

<div
className="h-4 w-4 rounded-full bg-cyan-400"
/>

<div>

{step}

</div>

</div>

))}

</div>

</GlassCard>

)

}