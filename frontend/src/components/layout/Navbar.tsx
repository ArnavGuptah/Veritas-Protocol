import { ShieldCheck } from "lucide-react";

export default function Navbar() {
    return (
        <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 backdrop-blur-xl bg-black/20">

            <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-10">

                <div className="flex items-center gap-3">

                    <ShieldCheck
                        size={28}
                        className="text-cyan-400"
                    />

                    <span className="text-xl font-semibold tracking-wide">
                        VERITAS
                    </span>

                </div>

                <nav className="flex gap-8 text-zinc-400">

                    <a href="#">Home</a>

                    <a href="#">Blockchain</a>

                    <a href="#">Graph</a>

                    <a href="#">API</a>

                </nav>

            </div>

        </header>
    );
}