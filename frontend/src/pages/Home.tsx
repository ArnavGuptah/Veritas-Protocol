import BackgroundGrid from "../components/layout/BackgroundGrid";
import Navbar from "../components/layout/Navbar";
import PageLayout from "../components/layout/PageLayout";

import Hero from "../components/hero/Hero";
import QueryBox from "../components/hero/QueryBox";
import HeroStats from "../components/hero/HeroStats";
import VerificationPipeline from "../components/blockchain/VerificationPipeline";
import SectionDivider from "../components/common/SectionDivider";

export default function Home() {

    return (

        <PageLayout>

            <BackgroundGrid />

            <Navbar />

            <main className="relative z-10 flex min-h-screen flex-col items-center justify-center px-8">

                <Hero />

                <QueryBox />

                <HeroStats />

                <SectionDivider />

                <VerificationPipeline />

            </main>

        </PageLayout>

    );

}