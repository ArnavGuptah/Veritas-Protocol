import GlassCard from "./GlassCard";

export default function AnswerCard(){

return(

<GlassCard>

<h2 className="text-3xl font-bold">
Verified Answer
</h2>

<p className="mt-6 text-zinc-300 leading-8">

WHO officially declared COVID-19 a pandemic
on 11 March 2020.

The statement was issued by
Director-General Dr Tedros Adhanom
Ghebreyesus.

</p>

<div className="mt-8 flex gap-3">

<span className="rounded-full bg-green-500/20 px-4 py-2 text-green-400">

99.4% Confidence

</span>

<span className="rounded-full bg-cyan-500/20 px-4 py-2 text-cyan-400">

Blockchain Verified

</span>

</div>

</GlassCard>

)

}