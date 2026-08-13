export default function BackgroundGrid() {
    return (
        <div
            className="
                absolute inset-0
                opacity-[0.06]
                bg-[linear-gradient(to_right,#ffffff_1px,transparent_1px),linear-gradient(to_bottom,#ffffff_1px,transparent_1px)]
                bg-[size:60px_60px]
                pointer-events-none
            "
        />
    );
}