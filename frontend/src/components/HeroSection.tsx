import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import heroImage from "@/assets/nfl-field-hero.jpg";

const HeroSection = () => {
  return (
    <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <img 
          src={heroImage} 
          alt="NFL Analytics Command Center" 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-primary/90 via-primary/70 to-accent/60"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 container text-center text-white">
        <Badge variant="secondary" className="mb-6 bg-white/10 text-white border-white/20 hover:bg-white/20">
          Powered by Rotowire Data
        </Badge>
        
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 bg-gradient-to-r from-white to-accent-muted bg-clip-text text-transparent">
          Football News AI
        </h1>
        
        <p className="text-xl md:text-2xl mb-4 text-white/90 max-w-3xl mx-auto">
          AI-Powered Sports Analytics Suite
        </p>
        
        <p className="text-lg mb-8 text-white/80 max-w-2xl mx-auto">
          Revolutionizing NFL front office operations with intelligent reports, 
          injury analysis, contract evaluation, and data-driven insights.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button size="lg" className="bg-white text-primary hover:bg-white/90 font-semibold px-8">
            Explore Analytics Suite
          </Button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;