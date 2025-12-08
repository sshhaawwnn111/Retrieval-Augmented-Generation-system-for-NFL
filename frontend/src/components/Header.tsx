const Header = () => {
  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container flex h-16 items-center justify-center">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">FN</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">Football News AI</h1>
            <p className="text-xs text-muted-foreground">NFL Analytics Suite</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;