import { useState } from "react";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import TeamsGrid from "@/components/TeamsGrid";
import AIChatbot from "@/components/AIChatbot";
import PinEntry from "@/components/PinEntry";

const Index = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  if (!isAuthenticated) {
    return <PinEntry onSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <HeroSection />
        <TeamsGrid />
      </main>
      <AIChatbot />
    </div>
  );
};

export default Index;
