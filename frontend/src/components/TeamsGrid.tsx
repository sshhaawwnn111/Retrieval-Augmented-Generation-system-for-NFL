import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Activity, User, AlertCircle, CheckCircle, Clock } from "lucide-react";

import bengalsLogo from "@/assets/teams/bengals.png";
import dolphinsLogo from "@/assets/teams/dolphins.png";
import brownsLogo from "@/assets/teams/browns.png";
import commandersLogo from "@/assets/teams/commanders.png";
import jetsLogo from "@/assets/teams/jets.png";
import ramsLogo from "@/assets/teams/rams.png";
import texansLogo from "@/assets/teams/texans.png";
import billsLogo from "@/assets/teams/bills.png";
import ravensLogo from "@/assets/teams/ravens.png";
import patriotsLogo from "@/assets/teams/patriots.png";
import steelersLogo from "@/assets/teams/steelers.png";
import coltsLogo from "@/assets/teams/colts.png";
import jaguarsLogo from "@/assets/teams/jaguars.jpg";
import titansLogo from "@/assets/teams/titans.jpg";
import chiefsLogo from "@/assets/teams/chiefs.png";
import broncosLogo from "@/assets/teams/broncos.jpg";
import raidersLogo from "@/assets/teams/raiders.png";
import chargersLogo from "@/assets/teams/chargers.png";
import cowboysLogo from "@/assets/teams/cowboys.png";
import eaglesLogo from "@/assets/teams/eagles.png";
import giantsLogo from "@/assets/teams/giants.jpg";
import packersLogo from "@/assets/teams/packers.png";
import bearsLogo from "@/assets/teams/bears.png";
import vikingsLogo from "@/assets/teams/vikings.png";
import lionsLogo from "@/assets/teams/lions.jpg";
import buccaneersLogo from "@/assets/teams/buccaneers.png";
import saintsLogo from "@/assets/teams/saints.png";
import falconsLogo from "@/assets/teams/falcons.jpg";
import panthersLogo from "@/assets/teams/panthers.png";
import ninersLogo from "@/assets/teams/49ers.png";
import seahawksLogo from "@/assets/teams/seahawks.png";
import cardinalsLogo from "@/assets/teams/cardinals.png";

// Team data with players
const teamsData: Record<string, { name: string; city: string; players: string[] }> = {
  "Buffalo Bills": { name: "Bills", city: "Buffalo", players: ["Josh Allen", "James Cook", "Khalil Shakir"] },
  "Miami Dolphins": { name: "Dolphins", city: "Miami", players: ["Tua Tagovailoa", "De'Von Achane", "Jaylen Waddle"] },
  "New England Patriots": { name: "Patriots", city: "New England", players: ["Drake Maye", "TreVeyon Henderson", "Stefon Diggs"] },
  "New York Jets": { name: "Jets", city: "New York", players: ["Tyrod Taylor", "Breece Hall", "John Metchie III"] },
  "Baltimore Ravens": { name: "Ravens", city: "Baltimore", players: [] }, // Ravens uses full roster
  "Cincinnati Bengals": { name: "Bengals", city: "Cincinnati", players: ["Joe Burrow", "Chase Brown", "Ja'Marr Chase"] },
  "Cleveland Browns": { name: "Browns", city: "Cleveland", players: ["Shedeur Sanders", "Quinshon Judkins", "Jerry Jeudy"] },
  "Pittsburgh Steelers": { name: "Steelers", city: "Pittsburgh", players: ["Aaron Rodgers", "Jaylen Warren", "DK Metcalf"] },
  "Houston Texans": { name: "Texans", city: "Houston", players: ["C.J. Stroud", "Woody Marks", "Nico Collins"] },
  "Indianapolis Colts": { name: "Colts", city: "Indianapolis", players: ["Daniel Jones", "Jonathan Taylor", "Michael Pittman Jr."] },
  "Jacksonville Jaguars": { name: "Jaguars", city: "Jacksonville", players: ["Trevor Lawrence", "Travis Etienne", "Brian Thomas Jr."] },
  "Tennessee Titans": { name: "Titans", city: "Tennessee", players: ["Cam Ward", "Tony Pollard", "Elic Ayomanor"] },
  "Kansas City Chiefs": { name: "Chiefs", city: "Kansas City", players: ["Patrick Mahomes", "Kareem Hunt", "Rashee Rice"] },
  "Denver Broncos": { name: "Broncos", city: "Denver", players: ["Bo Nix", "RJ Harvey", "Courtland Sutton"] },
  "Las Vegas Raiders": { name: "Raiders", city: "Las Vegas", players: ["Geno Smith", "Ashton Jeanty", "Tre Tucker"] },
  "Los Angeles Chargers": { name: "Chargers", city: "Los Angeles", players: ["Justin Herbert", "Kimani Vidal", "Ladd McConkey"] },
  "Dallas Cowboys": { name: "Cowboys", city: "Dallas", players: ["Dak Prescott", "Javonte Williams", "CeeDee Lamb"] },
  "Philadelphia Eagles": { name: "Eagles", city: "Philadelphia", players: ["Jalen Hurts", "Saquon Barkley", "A.J. Brown"] },
  "New York Giants": { name: "Giants", city: "New York", players: ["Jaxson Dart", "Tyrone Tracy Jr.", "Wan'Dale Robinson"] },
  "Washington Commanders": { name: "Commanders", city: "Washington", players: ["Jayden Daniels", "Chris Rodriguez Jr.", "Terry McLaurin"] },
  "Green Bay Packers": { name: "Packers", city: "Green Bay", players: ["Jordan Love", "Josh Jacobs", "Christian Watson"] },
  "Chicago Bears": { name: "Bears", city: "Chicago", players: ["Caleb Williams", "D'Andre Swift", "DJ Moore"] },
  "Minnesota Vikings": { name: "Vikings", city: "Minnesota", players: ["J.J. McCarthy", "Aaron Jones Sr.", "Justin Jefferson"] },
  "Detroit Lions": { name: "Lions", city: "Detroit", players: ["Jared Goff", "Jahmyr Gibbs", "Amon-Ra St. Brown"] },
  "Tampa Bay Buccaneers": { name: "Buccaneers", city: "Tampa Bay", players: ["Baker Mayfield", "Bucky Irving", "Emeka Egbuka"] },
  "New Orleans Saints": { name: "Saints", city: "New Orleans", players: ["Tyler Shough", "Alvin Kamara", "Chris Olave"] },
  "Atlanta Falcons": { name: "Falcons", city: "Atlanta", players: ["Kirk Cousins", "Bijan Robinson", "Drake London"] },
  "Carolina Panthers": { name: "Panthers", city: "Carolina", players: ["Bryce Young", "Rico Dowdle", "Tetairoa McMillan"] },
  "Los Angeles Rams": { name: "Rams", city: "Los Angeles", players: ["Matthew Stafford", "Kyren Williams", "Puka Nacua"] },
  "San Francisco 49ers": { name: "49ers", city: "San Francisco", players: ["Brock Purdy", "Christian McCaffrey", "Jauan Jennings"] },
  "Seattle Seahawks": { name: "Seahawks", city: "Seattle", players: ["Sam Darnold", "Kenneth Walker III", "Jaxon Smith-Njigba"] },
  "Arizona Cardinals": { name: "Cardinals", city: "Arizona", players: ["Jacoby Brissett", "Bam Knight", "Marvin Harrison Jr."] },
};

// Teams reordered - Ravens placed in middle (no highlight)
const teams = [
  { name: "Buffalo Bills", logo: billsLogo },
  { name: "Miami Dolphins", logo: dolphinsLogo },
  { name: "New England Patriots", logo: patriotsLogo },
  { name: "New York Jets", logo: jetsLogo },
  { name: "Cincinnati Bengals", logo: bengalsLogo },
  { name: "Cleveland Browns", logo: brownsLogo },
  { name: "Pittsburgh Steelers", logo: steelersLogo },
  { name: "Houston Texans", logo: texansLogo },
  { name: "Indianapolis Colts", logo: coltsLogo },
  { name: "Jacksonville Jaguars", logo: jaguarsLogo },
  { name: "Tennessee Titans", logo: titansLogo },
  { name: "Kansas City Chiefs", logo: chiefsLogo },
  { name: "Denver Broncos", logo: broncosLogo },
  { name: "Las Vegas Raiders", logo: raidersLogo },
  { name: "Los Angeles Chargers", logo: chargersLogo },
  { name: "Baltimore Ravens", logo: ravensLogo },
  { name: "Dallas Cowboys", logo: cowboysLogo },
  { name: "Philadelphia Eagles", logo: eaglesLogo },
  { name: "New York Giants", logo: giantsLogo },
  { name: "Washington Commanders", logo: commandersLogo },
  { name: "Green Bay Packers", logo: packersLogo },
  { name: "Chicago Bears", logo: bearsLogo },
  { name: "Minnesota Vikings", logo: vikingsLogo },
  { name: "Detroit Lions", logo: lionsLogo },
  { name: "Tampa Bay Buccaneers", logo: buccaneersLogo },
  { name: "New Orleans Saints", logo: saintsLogo },
  { name: "Atlanta Falcons", logo: falconsLogo },
  { name: "Carolina Panthers", logo: panthersLogo },
  { name: "Los Angeles Rams", logo: ramsLogo },
  { name: "San Francisco 49ers", logo: ninersLogo },
  { name: "Seattle Seahawks", logo: seahawksLogo },
  { name: "Arizona Cardinals", logo: cardinalsLogo },
];

// Only Injury Agent - other agents commented out
const agents = [
  {
    icon: Activity,
    title: "Injury Agent",
    description: "Injury prediction and prevention system that monitors player health, identifies risk factors, and optimizes recovery protocols.",
    features: ["Real-time Risk Assessment", "Recovery Optimization", "Injury Prevention Protocols"],
    status: "24/7 Active",
    statusColor: "success",
    isInteractive: true
  },
  /*
  {
    icon: TrendingUp,
    title: "Performance Agent",
    description: "Advanced performance tracking and optimization using machine learning to analyze player metrics, identify improvement areas, and maximize on-field output.",
    features: ["Performance Metrics", "Training Optimization", "Game-day Readiness"],
    status: "Live Tracking",
    statusColor: "success",
    isInteractive: false
  },
  {
    icon: Activity,
    title: "Injury Analytics",
    description: "Advanced injury prediction and recovery timeline analysis using machine learning models.",
    features: ["Risk Modeling", "Recovery Timelines", "Load Management"],
    status: "Daily Updates",
    statusColor: "accent",
    isInteractive: false
  },
  {
    icon: DollarSign,
    title: "Contract Analysis",
    description: "Smart contract evaluation with market value analysis and cap space optimization.",
    features: ["Market Value", "Cap Impact", "Trade Analysis"],
    status: "Real-time",
    statusColor: "success",
    isInteractive: false
  },
  {
    icon: TrendingUp,
    title: "Performance Trends",
    description: "Long-term performance trend analysis with season projection models.",
    features: ["Trend Analysis", "Season Projections", "Comparative Analytics"],
    status: "Live Data",
    statusColor: "success",
    isInteractive: false
  },
  {
    icon: Shield,
    title: "Draft Intelligence",
    description: "Comprehensive draft analysis with player potential and team fit recommendations.",
    features: ["Draft Rankings", "Team Fit Scores", "Value Projections"],
    status: "Draft Season",
    statusColor: "accent",
    isInteractive: false
  },
  {
    icon: Target,
    title: "Game Strategy",
    description: "Game planning with opponent analysis and tactical recommendations.",
    features: ["Opponent Analysis", "Play Calling", "Strategic Insights"],
    status: "Game Week",
    statusColor: "success",
    isInteractive: false
  },
  {
    icon: BarChart3,
    title: "Advanced Metrics",
    description: "Custom analytics dashboard with proprietary metrics and visualization tools.",
    features: ["Custom Metrics", "Data Visualization", "Export Tools"],
    status: "Always On",
    statusColor: "accent",
    isInteractive: false
  }
  */
];

const ravensRoster = {
  offense: [
    { no: 5, name: "Tyler Huntley", pos: "QB" },
    { no: 8, name: "Lamar Jackson", pos: "QB" },
    { no: 15, name: "Cooper Rush", pos: "QB" },
    { no: 26, name: "Rasheen Ali", pos: "RB" },
    { no: 22, name: "Derrick Henry", pos: "RB" },
    { no: 34, name: "Keaton Mitchell", pos: "RB" },
    { no: 42, name: "Patrick Ricard", pos: "FB" },
    { no: 7, name: "Rashod Bateman", pos: "WR" },
    { no: 4, name: "Zay Flowers", pos: "WR" },
    { no: 10, name: "DeAndre Hopkins", pos: "WR" },
    { no: 81, name: "Devontez Walker", pos: "WR" },
    { no: 16, name: "Tylan Wallace", pos: "WR" },
    { no: 83, name: "LaJohntay Wester", pos: "WR" },
    { no: 89, name: "Mark Andrews", pos: "TE" },
    { no: 88, name: "Charlie Kolar", pos: "TE" },
    { no: 80, name: "Isaiah Likely", pos: "TE" },
    { no: 64, name: "Tyler Linderbaum", pos: "C" },
    { no: 67, name: "Corey Bullock", pos: "OT" },
    { no: 51, name: "Emery Jones Jr.", pos: "OT" },
    { no: 68, name: "Joe Noteboom", pos: "OT" },
    { no: 70, name: "Roger Rosengarten", pos: "OT" },
    { no: 79, name: "Ronnie Stanley", pos: "OT" },
    { no: 71, name: "Carson Vinson", pos: "OT" },
    { no: 72, name: "Andrew Vorhees", pos: "OG" },
    { no: 66, name: "Ben Cleveland", pos: "G" },
    { no: 77, name: "Daniel Faalele", pos: "G" },
  ],
  defense: [
    { no: 41, name: "Dre'Mont Jones", pos: "DE" },
    { no: 97, name: "Brent Urban", pos: "DE" },
    { no: 94, name: "John Jenkins", pos: "DT" },
    { no: 98, name: "Travis Jones", pos: "DT" },
    { no: 91, name: "Basil Okoye", pos: "DT" },
    { no: 93, name: "Aeneas Peebles", pos: "DT" },
    { no: 0, name: "Roquan Smith", pos: "ILB" },
    { no: 53, name: "Kyle Van Noy", pos: "MLB" },
    { no: 40, name: "Teddye Buchanan", pos: "LB" },
    { no: 45, name: "Mike Green", pos: "LB" },
    { no: 35, name: "Jake Hummel", pos: "LB" },
    { no: 90, name: "David Ojabo", pos: "LB" },
    { no: 32, name: "Trenton Simpson", pos: "LB" },
    { no: 3, name: "Chidobe Awuzie", pos: "CB" },
    { no: 44, name: "Marlon Humphrey", pos: "CB" },
    { no: 38, name: "Keyon Martin", pos: "CB" },
    { no: 27, name: "T.J. Tampa", pos: "CB" },
    { no: 2, name: "Nate Wiggins", pos: "CB" },
    { no: 12, name: "Alohi Gilman", pos: "SAF" },
    { no: 14, name: "Kyle Hamilton", pos: "SAF" },
    { no: 39, name: "Keondre Jackson", pos: "SAF" },
    { no: 24, name: "Malaki Starks", pos: "SAF" },
  ],
  specialTeams: [
    { no: 33, name: "Tyler Loop", pos: "K" },
    { no: 11, name: "Jordan Stout", pos: "P" },
    { no: 46, name: "Nick Moore", pos: "LS" },
  ]
};

// Generate injury report based on player
const generateInjuryReport = (playerName: string, teamName: string) => {
  const week = 11;
  return {
    player: playerName,
    team: teamName,
    week: week,
    status: "success",
    currentStatus: `${playerName} has avoided injury designation on November 6th, indicating he is healthy enough to play in Week ${week}. He was not on the injury report for the previous weeks, suggesting he has been managing his workload and avoiding any significant issues.`,
    medicalAnalysis: `Given the lack of specific injury details, it's challenging to pinpoint the exact nature of any potential concern. However, considering ${playerName}'s playing style and position demands, monitoring for minor strains or tweaks is standard protocol. A typical recovery period for such issues can range from 1-4 weeks, depending on severity. Re-injury risk assessment is ongoing.`,
    impactAssessment: `${playerName}'s absence or limited participation in practice could impact the ${teamName}'s offense/defense. His skills and abilities are crucial to the team's success, and any limited involvement could lead to adjustments in overall team strategy and performance.`,
    returnProjection: `Assuming ${playerName} avoids any significant setbacks, he is projected to be available for Week ${week}. However, workload and playing time may be managed based on ongoing health assessments and game situations.`
  };
};

const getTeamInitials = (teamName: string) => {
  const words = teamName.split(" ");
  if (words.length >= 2) {
    return words[words.length - 1].substring(0, 3).toUpperCase();
  }
  return teamName.substring(0, 3).toUpperCase();
};

const TeamsGrid = () => {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [showAgents, setShowAgents] = useState(false);
  const [showPlayers, setShowPlayers] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState<string | null>(null);

  const handleTeamClick = (teamName: string) => {
    setSelectedTeam(teamName);
    setShowAgents(true);
  };

  const handleAgentClick = (agentTitle: string, isInteractive: boolean) => {
    if (agentTitle === "Injury Agent" && isInteractive) {
      setShowAgents(false);
      setShowPlayers(true);
    }
  };

  const handlePlayerClick = (playerName: string) => {
    setSelectedPlayer(playerName);
    setShowPlayers(false);
    setShowReport(true);
  };

  const handleCloseAll = () => {
    setShowAgents(false);
    setShowPlayers(false);
    setShowReport(false);
    setSelectedTeam(null);
    setSelectedPlayer(null);
  };

  const injuryReport = selectedPlayer && selectedTeam 
    ? generateInjuryReport(selectedPlayer, selectedTeam) 
    : null;

  const isRavens = selectedTeam === "Baltimore Ravens";
  const currentTeamPlayers = selectedTeam && teamsData[selectedTeam] ? teamsData[selectedTeam].players : [];

  return (
    <section className="py-20 bg-muted/30">
      <div className="container">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Select Your Team</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Choose an NFL team to access analytics and agent reports.
          </p>
        </div>

        <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4 justify-items-center">
          {teams.map((team, index) => (
            <button
              key={index}
              onClick={() => handleTeamClick(team.name)}
              className="flex flex-col items-center gap-2 p-3 rounded-lg transition-all duration-300 group hover:bg-muted/50"
            >
              <div className="w-16 h-16 md:w-20 md:h-20 rounded-full overflow-hidden bg-background border-2 flex items-center justify-center transition-all duration-300 border-border group-hover:border-accent">
                {team.logo ? (
                  <img 
                    src={team.logo} 
                    alt={team.name} 
                    className="w-full h-full object-contain p-2"
                  />
                ) : (
                  <span className="text-xs md:text-sm font-bold text-muted-foreground">
                    {getTeamInitials(team.name)}
                  </span>
                )}
              </div>
              <span className="text-[10px] md:text-xs font-medium text-center leading-tight">{team.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Agents Dialog */}
      <Dialog open={showAgents} onOpenChange={(open) => !open && handleCloseAll()}>
        <DialogContent className="max-w-md bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-2xl">{selectedTeam} - Agents</DialogTitle>
          </DialogHeader>
          <ScrollArea className="h-auto max-h-[400px] pr-4">
            <div className="space-y-4 p-2">
              {agents.map((agent, index) => {
                const IconComponent = agent.icon;
                const isClickable = agent.isInteractive;
                return (
                  <Card 
                    key={index} 
                    className={`bg-card border-border transition-all duration-300 ${
                      isClickable ? "hover:shadow-lg hover:-translate-y-1 cursor-pointer" : "opacity-70"
                    }`}
                    onClick={() => handleAgentClick(agent.title, agent.isInteractive)}
                  >
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between mb-2">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                          <IconComponent className="w-5 h-5 text-primary-foreground" />
                        </div>
                        <Badge 
                          variant="secondary" 
                          className={`text-xs ${
                            agent.statusColor === 'success' ? 'bg-success/10 text-success' :
                            'bg-accent/10 text-accent'
                          }`}
                        >
                          {agent.status}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg">{agent.title}</CardTitle>
                      <CardDescription className="text-sm">{agent.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-1">
                        {agent.features.map((feature, idx) => (
                          <div key={idx} className="flex items-center text-sm text-muted-foreground">
                            <div className="w-1.5 h-1.5 rounded-full bg-accent mr-2"></div>
                            {feature}
                          </div>
                        ))}
                      </div>
                      {!isClickable && (
                        <p className="text-xs text-muted-foreground mt-3 italic">Coming soon...</p>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>

      {/* Players Dialog */}
      <Dialog open={showPlayers} onOpenChange={(open) => !open && handleCloseAll()}>
        <DialogContent className="max-w-4xl bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-2xl">{selectedTeam} - Injury Agent</DialogTitle>
            <p className="text-muted-foreground">Select a player to view injury report</p>
          </DialogHeader>
          <ScrollArea className="h-[500px] pr-4">
            {isRavens ? (
              <div className="space-y-6 p-2">
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-accent">Offense</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {ravensRoster.offense.map((player, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        className="justify-start h-auto py-2 px-3 hover:border-accent hover:text-accent"
                        onClick={() => handlePlayerClick(player.name)}
                      >
                        <span className="text-xs text-muted-foreground mr-2">#{player.no}</span>
                        <span className="truncate">{player.name}</span>
                        <span className="text-xs text-muted-foreground ml-auto">{player.pos}</span>
                      </Button>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-accent">Defense</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {ravensRoster.defense.map((player, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        className="justify-start h-auto py-2 px-3 hover:border-accent hover:text-accent"
                        onClick={() => handlePlayerClick(player.name)}
                      >
                        <span className="text-xs text-muted-foreground mr-2">#{player.no}</span>
                        <span className="truncate">{player.name}</span>
                        <span className="text-xs text-muted-foreground ml-auto">{player.pos}</span>
                      </Button>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-accent">Special Teams</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {ravensRoster.specialTeams.map((player, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        className="justify-start h-auto py-2 px-3 hover:border-accent hover:text-accent"
                        onClick={() => handlePlayerClick(player.name)}
                      >
                        <span className="text-xs text-muted-foreground mr-2">#{player.no}</span>
                        <span className="truncate">{player.name}</span>
                        <span className="text-xs text-muted-foreground ml-auto">{player.pos}</span>
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-2">
                <h3 className="text-lg font-semibold mb-3 text-accent">Key Players</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {currentTeamPlayers.map((player, idx) => (
                    <Button
                      key={idx}
                      variant="outline"
                      className="justify-center h-auto py-4 px-4 hover:border-accent hover:text-accent text-base"
                      onClick={() => handlePlayerClick(player)}
                    >
                      <User className="w-4 h-4 mr-2" />
                      {player}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>

      {/* Injury Report Dialog */}
      <Dialog open={showReport} onOpenChange={(open) => !open && handleCloseAll()}>
        <DialogContent className="max-w-3xl bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-2xl flex items-center gap-2">
              <Activity className="w-6 h-6 text-accent" />
              Injury Report - {selectedPlayer}
            </DialogTitle>
          </DialogHeader>
          {injuryReport && (
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-6 p-2">
                {/* Header Info */}
                <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                  <div>
                    <p className="text-sm text-muted-foreground">Player</p>
                    <p className="text-xl font-bold">{injuryReport.player}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Team</p>
                    <p className="text-lg font-semibold">{injuryReport.team}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Week</p>
                    <p className="text-lg font-semibold">{injuryReport.week}</p>
                  </div>
                  <Badge className="bg-success/20 text-success border-success">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    {injuryReport.status}
                  </Badge>
                </div>

                {/* Current Status */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-success" />
                    <h3 className="text-lg font-semibold">Current Status</h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed pl-7">
                    {injuryReport.currentStatus}
                  </p>
                </div>

                {/* Medical Analysis */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-accent" />
                    <h3 className="text-lg font-semibold">Medical Analysis</h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed pl-7">
                    {injuryReport.medicalAnalysis}
                  </p>
                </div>

                {/* Impact Assessment */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-warning" />
                    <h3 className="text-lg font-semibold">Impact Assessment</h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed pl-7">
                    {injuryReport.impactAssessment}
                  </p>
                </div>

                {/* Return Projection */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-primary" />
                    <h3 className="text-lg font-semibold">Return Projection</h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed pl-7">
                    {injuryReport.returnProjection}
                  </p>
                </div>

                {/* Footer */}
                <div className="pt-4 border-t border-border">
                  <p className="text-xs text-muted-foreground text-center">
                    Generated by Injury Agent • Data as of Week {injuryReport.week}
                  </p>
                </div>
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </section>
  );
};

export default TeamsGrid;
