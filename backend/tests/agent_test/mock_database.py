class MockDatabase:
    """Mock database for testing agents without real database connection"""
    
    def __init__(self, sample_data):
        self.sample_data = sample_data
    
    def query(self, query, params=None):
        """Mock database query that returns sample data"""
        if 'injuries' in query.lower():
            return self._mock_injury_query(params)
        elif 'contracts' in query.lower():
            return self._mock_contract_query(params)
        elif 'player_stats' in query.lower():
            return self._mock_stats_query(params)
        else:
            return []
    
    def _mock_injury_query(self, params):
        """Mock injury data query"""
        if params and len(params) >= 2:
            player_name, team = params[0], params[1]
            # Find matching injury in sample data
            for team_data in self.sample_data.values():
                for injury in team_data['injuries']:
                    if injury['player'].lower() in player_name.lower():
                        return [injury]
        return []
    
    def _mock_contract_query(self, params):
        """Mock contract data query"""
        # Return mock contract data
        return [{
            'player': 'Lamar Jackson',
            'contract_value': '$120,000,000',
            'years': '4',
            'guarantees': '$80,000,000'
        }]
    
    def _mock_stats_query(self, params):
        """Mock stats data query"""
        return [{
            'player': 'Lamar Jackson',
            'passing_yards': '1,200',
            'touchdowns': '8',
            'interceptions': '2'
        }]