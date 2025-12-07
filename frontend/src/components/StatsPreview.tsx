import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { TrendingUp, TrendingDown, Activity, Target } from "lucide-react";

const StatsPreview = () => {
  const reports = [
    {
      title: "Weekly Injury Report",
      description: "Advanced injury risk assessment",
      lastUpdated: "2 hours ago",
      metrics: [
        { label: "High Risk Players", value: 8, trend: "up", color: "warning" },
        { label: "Recovery Timeline Accuracy", value: 94, trend: "up", color: "success" },
        { label: "Load Management Alerts", value: 12, trend: "down", color: "accent" }
      ]
    },
    {
      title: "Contract Analysis Dashboard",
      description: "Real-time contract value optimization",
      lastUpdated: "1 hour ago",
      metrics: [
        { label: "Cap Space Efficiency", value: 87, trend: "up", color: "success" },
        { label: "Market Value Accuracy", value: 92, trend: "up", color: "success" },
        { label: "Trade Opportunities", value: 5, trend: "up", color: "accent" }
      ]
    }
  ];

  const topPerformers = [
    { name: "Josh Allen", position: "QB", team: "BUF", score: 98, change: "+2.4" },
    { name: "Cooper Kupp", position: "WR", team: "LAR", score: 95, change: "+1.8" },
    { name: "Jonathan Taylor", position: "RB", team: "IND", score: 93, change: "-0.5" },
    { name: "T.J. Watt", position: "OLB", team: "PIT", score: 97, change: "+3.1" }
  ];

  return (
    <section className="py-20 bg-background">
      <div className="container">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Live Analytics Preview</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Real-time insights and analytics reports updated continuously with the latest NFL data.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {reports.map((report, index) => (
            <Card key={index} className="border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl">{report.title}</CardTitle>
                    <CardDescription>{report.description}</CardDescription>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {report.lastUpdated}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {report.metrics.map((metric, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium">{metric.label}</span>
                        {metric.trend === "up" ? (
                          <TrendingUp className={`w-4 h-4 ${
                            metric.color === 'success' ? 'text-success' :
                            metric.color === 'warning' ? 'text-warning' : 'text-accent'
                          }`} />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-muted-foreground" />
                        )}
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl font-bold">{metric.value}</span>
                        {typeof metric.value === 'number' && metric.value <= 100 && (
                          <Progress value={metric.value} className="w-16" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Top Performers */}
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-accent" />
              <span>Top Performance Index</span>
            </CardTitle>
            <CardDescription>Performance rankings updated daily</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topPerformers.map((player, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center text-primary-foreground font-bold text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <div className="font-semibold">{player.name}</div>
                      <div className="text-sm text-muted-foreground">{player.position} • {player.team}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-2xl font-bold">{player.score}</div>
                      <div className={`text-sm ${
                        player.change.startsWith('+') ? 'text-success' : 'text-muted-foreground'
                      }`}>
                        {player.change}
                      </div>
                    </div>
                    <Activity className="w-5 h-5 text-accent" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default StatsPreview;