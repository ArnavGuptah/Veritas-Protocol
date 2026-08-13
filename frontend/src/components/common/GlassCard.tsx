import type { ReactNode } from "react";

interface Props{
    children:ReactNode;
}

export default function GlassCard({children}:Props){

    return(

        <div
            className="
            rounded-3xl
            border
            border-white/10
            bg-white/[0.04]
            backdrop-blur-xl
            shadow-2xl
            p-8
            "
        >

            {children}

        </div>

    )

}