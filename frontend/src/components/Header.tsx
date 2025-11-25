import { Button } from "@/components/ui/button";

const Header = () => {
  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">HR</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-foreground">Hopkins NFL AI Agents</h1>
              <p className="text-xs text-muted-foreground">NFL Analytics Suite</p>
            </div>
          </div>
        </div>

        <nav className="hidden md:flex items-center space-x-6">
          {/* <a href="#home" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Home
          </a> */}
          {/* <a href="#dashboard" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Dashboard
          </a>
          <a href="#reports" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            All Reports
          </a> */}
        </nav>

        {/* <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
            Sign In
          </Button>
          <Button size="sm" className="bg-gradient-to-r from-primary to-primary-muted hover:opacity-90">
            Sign Up
          </Button>
        </div> */}
      </div>
    </header>
  );
};

export default Header;