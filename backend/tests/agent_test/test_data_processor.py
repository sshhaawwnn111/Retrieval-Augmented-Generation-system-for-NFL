import re
import json
from typing import Dict, List

class TestDataProcessor:
    def __init__(self):
        self.processed_data = {}
    
    def process_sample_report(self, report_content: str) -> Dict:
        """Extract structured data from the sample report"""
        
        # Extract team sections
        team_sections = self._extract_team_sections(report_content)
        
        for team, section in team_sections.items():
            self.processed_data[team] = {
                'injuries': self._extract_injuries(section),
                'over_performers': self._extract_over_performers(section),
                'under_performers': self._extract_under_performers(section),
                'suspended': self._extract_suspended(section),
                'summary': self._extract_summary(section)
            }
        
        return self.processed_data
    
    def _extract_team_sections(self, content: str) -> Dict[str, str]:
        """Extract individual team sections from the report"""
        teams = {}
        
        # Look for team headers like "## Baltimore Ravens"
        team_pattern = r'##\s*(.*? Ravens|.*? Bills)\s*\n(.*?)(?=##|\Z)'
        matches = re.finditer(team_pattern, content, re.DOTALL)
        
        for match in matches:
            team_name = match.group(1).strip()
            team_content = match.group(2).strip()
            teams[team_name] = team_content
        
        return teams
    
    def _extract_injuries(self, section: str) -> List[Dict]:
        """Extract injury information from team section"""
        injuries = []
        
        # Look for "Injured:" lines
        injured_pattern = r'Injured:\s*(.*?)(?=\n\*\*|\n\n|\Z)'
        match = re.search(injured_pattern, section, re.DOTALL)
        
        if match:
            injured_text = match.group(1)
            # Split by commas and parse individual injuries
            injury_entries = [entry.strip() for entry in injured_text.split(',')]
            
            for entry in injury_entries:
                if entry and not entry.startswith('**'):
                    # Parse player and injury info
                    player_match = re.match(r'([^(]+)\s*\(([^)]+)\)', entry)
                    if player_match:
                        player_name = player_match.group(1).strip()
                        injury_info = player_match.group(2).strip()
                        
                        # Separate position and injury
                        if '–' in injury_info:
                            position, injury = injury_info.split('–', 1)
                        else:
                            position, injury = 'Unknown', injury_info
                        
                        injuries.append({
                            'player': player_name,
                            'position': position.strip(),
                            'injury': injury.strip(),
                            'team': 'Baltimore Ravens' if 'Ravens' in section else 'Buffalo Bills'
                        })
        
        return injuries
    
    def _extract_over_performers(self, section: str) -> List[Dict]:
        """Extract over performers from team section"""
        return self._extract_performers(section, 'Over Performers')
    
    def _extract_under_performers(self, section: str) -> List[Dict]:
        """Extract under performers from team section"""
        return self._extract_performers(section, 'Under Performers')
    
    def _extract_performers(self, section: str, performer_type: str) -> List[Dict]:
        """Extract performers (over or under) from team section"""
        performers = []
        
        pattern = rf'{performer_type}:\s*(.*?)(?=\n\*\*|\n\n|\Z)'
        match = re.search(pattern, section, re.DOTALL)
        
        if match:
            performers_text = match.group(1)
            # Split and clean up performer entries
            performer_entries = [entry.strip() for entry in performers_text.split(',')]
            
            for entry in performer_entries:
                if entry and not entry.startswith('**'):
                    # Try to extract player and reason
                    if '(' in entry and ')' in entry:
                        player_match = re.match(r'([^(]+)\s*\(([^)]+)\)', entry)
                        if player_match:
                            performers.append({
                                'player': player_match.group(1).strip(),
                                'reason': player_match.group(2).strip(),
                                'type': performer_type.lower().replace(' ', '_'),
                                'team': 'Baltimore Ravens' if 'Ravens' in section else 'Buffalo Bills'
                            })
                    else:
                        performers.append({
                            'player': entry,
                            'reason': 'Performance noted in report',
                            'type': performer_type.lower().replace(' ', '_'),
                            'team': 'Baltimore Ravens' if 'Ravens' in section else 'Buffalo Bills'
                        })
        
        return performers
    
    def _extract_suspended(self, section: str) -> List[Dict]:
        """Extract suspended players from team section"""
        suspended = []
        
        suspended_pattern = r'Suspended:\s*(.*?)(?=\n\*\*|\n\n|\Z)'
        match = re.search(suspended_pattern, section, re.DOTALL)
        
        if match:
            suspended_text = match.group(1)
            suspended_entries = [entry.strip() for entry in suspended_text.split(',')]
            
            for entry in suspended_entries:
                if entry:
                    suspended.append({
                        'player': entry,
                        'team': 'Baltimore Ravens' if 'Ravens' in section else 'Buffalo Bills',
                        'status': 'suspended'
                    })
        
        return suspended
    
    def _extract_summary(self, section: str) -> str:
        """Extract the summary text from team section"""
        # Find the paragraph after all the bullet points
        lines = section.split('\n')
        summary_start = False
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Start collecting after the last bullet point section
            if not line.startswith('**') and not summary_start:
                summary_start = True
            
            if summary_start:
                summary_lines.append(line)
        
        return ' '.join(summary_lines)