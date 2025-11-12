import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useState } from "react";
import { 
  FileText, 
  Activity, 
  DollarSign, 
  TrendingUp, 
  Shield,
  Target,
  BarChart3 
} from "lucide-react";

import bengalsLogo from "@/assets/teams/bengals.png";
import dolphinsLogo from "@/assets/teams/dolphins.png";
import brownsLogo from "@/assets/teams/browns.png";
import commandersLogo from "@/assets/teams/commanders.png";
import jetsLogo from "@/assets/teams/jets.png";
import ramsLogo from "@/assets/teams/rams.png";
import texansLogo from "@/assets/teams/texans.png";
import billsLogo from "@/assets/teams/bills.png";
import ravensLogo from "@/assets/teams/ravens.png";

const teams = [
  { name: "Baltimore Ravens", logo: ravensLogo },
  { name: "Buffalo Bills", logo: billsLogo },
  { name: "Cincinnati Bengals", logo: bengalsLogo },
  { name: "Cleveland Browns", logo: brownsLogo },
  { name: "Houston Texans", logo: texansLogo },
  { name: "Los Angeles Rams", logo: ramsLogo },
  { name: "Miami Dolphins", logo: dolphinsLogo },
  { name: "New York Jets", logo: jetsLogo },
  { name: "Washington Commanders", logo: commandersLogo },
];

const services = [
  {
    icon: FileText,
    title: "Executive Summary Reports",
    description: "Comprehensive executive-level reports with key insights and strategic recommendations.",
    features: ["Weekly Summaries", "Strategic Insights", "Decision Support"],
    status: "Weekly",
    statusColor: "success",
    hasDialog: true
  },
  {
    icon: FileText,
    title: "AI Scouting Reports",
    description: "Comprehensive player analysis with predictive performance metrics and draft recommendations.",
    features: ["Player Rankings", "Performance Predictions", "Injury Risk Assessment"],
    status: "Live Reports",
    statusColor: "success",
    hasDialog: true
  },
  {
    icon: Activity,
    title: "Injury Analytics",
    description: "Advanced injury prediction and recovery timeline analysis using machine learning models.",
    features: ["Risk Modeling", "Recovery Timelines", "Load Management"],
    status: "Daily Updates",
    statusColor: "accent",
    hasDialog: true
  },
  {
    icon: DollarSign,
    title: "Contract Analysis",
    description: "Smart contract evaluation with market value analysis and cap space optimization.",
    features: ["Market Value", "Cap Impact", "Trade Analysis"],
    status: "Real-time",
    statusColor: "success",
    hasDialog: true
  },
  {
    icon: TrendingUp,
    title: "Performance Trends",
    description: "Long-term performance trend analysis with season projection models.",
    features: ["Trend Analysis", "Season Projections", "Comparative Analytics"],
    status: "Live Data",
    statusColor: "success",
    hasDialog: true
  },
  {
    icon: Shield,
    title: "Draft Intelligence",
    description: "Comprehensive draft analysis with player potential and team fit recommendations.",
    features: ["Draft Rankings", "Team Fit Scores", "Value Projections"],
    status: "Draft Season",
    statusColor: "accent",
    hasDialog: true
  },
  {
    icon: Target,
    title: "Game Strategy",
    description: "AI-powered game planning with opponent analysis and tactical recommendations.",
    features: ["Opponent Analysis", "Play Calling", "Strategic Insights"],
    status: "Game Week",
    statusColor: "success",
    hasDialog: true
  },
  {
    icon: BarChart3,
    title: "Advanced Metrics",
    description: "Custom analytics dashboard with proprietary metrics and visualization tools.",
    features: ["Custom Metrics", "Data Visualization", "Export Tools"],
    status: "Always On",
    statusColor: "accent",
    hasDialog: true
  }
];

const ServicesGrid = () => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState("");

  const handleTeamClick = (teamName: string) => {
    if (teamName === "Baltimore Ravens") {
      setSelectedTeam(teamName);
      setIsDialogOpen(false);
      setIsGenerating(true);
      setShowReport(false);
      
      // Simulate report generation
      setTimeout(() => {
        setIsGenerating(false);
        setShowReport(true);
      }, 3000);
    }
  };

  return (
    <section id="services" className="py-20 bg-muted/30">
      <div className="container">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">AI Analytics Suite</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Comprehensive AI-powered tools designed specifically for NFL front office operations and decision-making.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, index) => {
            const IconComponent = service.icon;
            return (
              <Card key={index} className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-card border-border">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                      <IconComponent className="w-5 h-5 text-primary-foreground" />
                    </div>
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${
                        service.statusColor === 'success' ? 'bg-success/10 text-success' :
                        service.statusColor === 'accent' ? 'bg-accent/10 text-accent' :
                        'bg-warning/10 text-warning'
                      }`}
                    >
                      {service.status}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg">{service.title}</CardTitle>
                  <CardDescription className="text-sm">{service.description}</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2 mb-4">
                    {service.features.map((feature, idx) => (
                      <div key={idx} className="flex items-center text-sm text-muted-foreground">
                        <div className="w-1.5 h-1.5 rounded-full bg-accent mr-2"></div>
                        {feature}
                      </div>
                    ))}
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full group-hover:border-accent group-hover:text-accent transition-colors"
                    onClick={() => service.hasDialog && setIsDialogOpen(true)}
                  >
                    View Reports
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-3xl bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-2xl">Executive Summary Reports</DialogTitle>
          </DialogHeader>
          <ScrollArea className="h-[500px] pr-4">
            <div className="grid grid-cols-3 gap-6 p-4">
              {teams.map((team, index) => (
                <button
                  key={index}
                  className="flex flex-col items-center gap-3 p-4 rounded-lg hover:bg-muted/50 transition-colors group"
                  onClick={() => handleTeamClick(team.name)}
                >
                  <div className="w-24 h-24 rounded-full overflow-hidden bg-background border-2 border-border group-hover:border-accent transition-colors flex items-center justify-center p-2">
                    <img 
                      src={team.logo} 
                      alt={team.name} 
                      className="w-full h-full object-contain"
                    />
                  </div>
                  <span className="text-sm font-medium text-center">{team.name}</span>
                </button>
              ))}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>

      {/* Generating Report Dialog */}
      <Dialog open={isGenerating} onOpenChange={setIsGenerating}>
        <DialogContent className="max-w-md bg-card border-border">
          <div className="flex flex-col items-center justify-center py-8 gap-4">
            <div className="w-16 h-16 border-4 border-accent border-t-transparent rounded-full animate-spin"></div>
            <DialogTitle className="text-xl text-center">
              Generating Executive Summary Reports for the {selectedTeam}
            </DialogTitle>
          </div>
        </DialogContent>
      </Dialog>

      {/* Report PDF Dialog */}
      <Dialog open={showReport} onOpenChange={setShowReport}>
        <DialogContent className="max-w-6xl h-[90vh] bg-card border-border p-0">
          <DialogHeader className="p-6 pb-0">
            <DialogTitle className="text-2xl">{selectedTeam} Executive Summary Report</DialogTitle>
          </DialogHeader>
          <div className="flex-1 h-full p-6">
            <iframe
              src="/reports/ravens_report.pdf"
              className="w-full h-full rounded-lg"
              title="Ravens Report"
            />
          </div>
        </DialogContent>
      </Dialog>
    </section>
  );
};

export default ServicesGrid;