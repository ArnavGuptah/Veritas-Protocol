import type { ReactNode } from "react";

interface Props {
    children: ReactNode;
}

export default function PageLayout({ children }: Props) {
    return (
        <div className="relative min-h-screen overflow-hidden bg-[#09090B] text-white">
            {children}
        </div>
    );
}