from typing import List, Dict, Any
from database import SessionLocal
from models.saas_tool import SaaSTool, ToolStatus
from difflib import SequenceMatcher

class DuplicateDetector:
    """Detect suspected duplicate SaaS tools"""
    
    SIMILARITY_THRESHOLD = 0.85  # 85% similarity threshold
    
    def __init__(self, db_session):
        self.db = db_session
    
    def detect_duplicates(self, organization_id: int) -> List[Dict[str, Any]]:
        """Detect suspected duplicate tools for an organization"""
        tools = self.db.query(SaaSTool).filter(
            SaaSTool.organization_id == organization_id
        ).all()
        
        duplicates = []
        processed = set()
        
        for i, tool1 in enumerate(tools):
            if tool1.id in processed:
                continue
            
            similar_tools = []
            for j, tool2 in enumerate(tools[i+1:], start=i+1):
                if tool2.id in processed:
                    continue
                
                similarity = self._calculate_similarity(tool1.name, tool2.name)
                if similarity >= self.SIMILARITY_THRESHOLD:
                    similar_tools.append(tool2)
                    processed.add(tool2.id)
            
            if similar_tools:
                # Mark all as suspected duplicates
                tool1.status = ToolStatus.SUSPECTED_DUPLICATE
                self.db.add(tool1)
                
                for tool2 in similar_tools:
                    tool2.status = ToolStatus.SUSPECTED_DUPLICATE
                    self.db.add(tool2)
                
                duplicates.append({
                    'primary_tool': {
                        'id': tool1.id,
                        'name': tool1.name
                    },
                    'duplicates': [
                        {'id': t.id, 'name': t.name} for t in similar_tools
                    ]
                })
                processed.add(tool1.id)
        
        self.db.commit()
        return duplicates
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two tool names"""
        name1_lower = name1.lower().strip()
        name2_lower = name2.lower().strip()
        
        # Exact match
        if name1_lower == name2_lower:
            return 1.0
        
        # Check if one contains the other
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return 0.9
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, name1_lower, name2_lower).ratio()
    
    def merge_duplicates(self, primary_tool_id: int, duplicate_tool_ids: List[int]) -> bool:
        """Merge duplicate tools into primary tool"""
        try:
            primary_tool = self.db.query(SaaSTool).filter(SaaSTool.id == primary_tool_id).first()
            if not primary_tool:
                return False
            
            # Merge detection sources and other data
            for dup_id in duplicate_tool_ids:
                dup_tool = self.db.query(SaaSTool).filter(SaaSTool.id == dup_id).first()
                if dup_tool:
                    # Move detection sources
                    from models.detection_source import DetectionSource
                    sources = self.db.query(DetectionSource).filter(
                        DetectionSource.tool_id == dup_id
                    ).all()
                    for source in sources:
                        source.tool_id = primary_tool_id
                    
                    # Delete duplicate tool
                    self.db.delete(dup_tool)
            
            # Mark primary as active
            primary_tool.status = ToolStatus.ACTIVE
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

