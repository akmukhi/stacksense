from typing import List, Dict, Any, Optional
from database import SessionLocal
from models.saas_tool import SaaSTool, ToolStatus
from models.detection_source import DetectionSource, SourceType
from models.invoice import Invoice, InvoiceSource
from datetime import datetime
import re

class InvoiceDetector:
    """Detect SaaS tools from invoices"""
    
    # Common vendor name patterns
    VENDOR_PATTERNS = {
        r'slack': {'name': 'Slack', 'category': 'Communication', 'vendor': 'Slack Technologies'},
        r'github': {'name': 'GitHub', 'category': 'Development', 'vendor': 'GitHub'},
        r'notion': {'name': 'Notion', 'category': 'Productivity', 'vendor': 'Notion'},
        r'jira|atlassian': {'name': 'Jira', 'category': 'Project Management', 'vendor': 'Atlassian'},
        r'zoom': {'name': 'Zoom', 'category': 'Communication', 'vendor': 'Zoom'},
        r'figma': {'name': 'Figma', 'category': 'Design', 'vendor': 'Figma'},
        r'linear': {'name': 'Linear', 'category': 'Project Management', 'vendor': 'Linear'},
        r'asana': {'name': 'Asana', 'category': 'Project Management', 'vendor': 'Asana'},
        r'trello': {'name': 'Trello', 'category': 'Project Management', 'vendor': 'Atlassian'},
        r'dropbox': {'name': 'Dropbox', 'category': 'Storage', 'vendor': 'Dropbox'},
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def detect_from_invoice_text(self, invoice_text: str, organization_id: int, 
                                      amount: Optional[float] = None, 
                                      invoice_date: Optional[datetime] = None,
                                      source: InvoiceSource = InvoiceSource.UPLOAD) -> List[Dict[str, Any]]:
        """Detect tools from invoice text content"""
        detected_tools = []
        text_lower = invoice_text.lower()
        
        # Try to match vendor patterns
        for pattern, tool_info in self.VENDOR_PATTERNS.items():
            if re.search(pattern, text_lower):
                # Check if tool already exists
                existing_tool = self.db.query(SaaSTool).filter(
                    SaaSTool.name == tool_info['name'],
                    SaaSTool.organization_id == organization_id
                ).first()
                
                if not existing_tool:
                    tool = SaaSTool(
                        name=tool_info['name'],
                        category=tool_info['category'],
                        vendor=tool_info['vendor'],
                        status=ToolStatus.ACTIVE,
                        organization_id=organization_id
                    )
                    self.db.add(tool)
                    self.db.flush()
                    
                    # Create invoice record
                    invoice = Invoice(
                        tool_id=tool.id,
                        amount=amount or 0.0,
                        currency='USD',
                        invoice_date=invoice_date or datetime.utcnow(),
                        source=source
                    )
                    self.db.add(invoice)
                    
                    # Create detection source
                    detection_source = DetectionSource(
                        tool_id=tool.id,
                        source_type=SourceType.INVOICE,
                        source_data={'invoice_text_snippet': invoice_text[:200]}
                    )
                    self.db.add(detection_source)
                    
                    detected_tools.append({
                        'tool_id': tool.id,
                        'name': tool.name,
                        'source': 'invoice',
                        'amount': amount
                    })
                else:
                    from datetime import datetime
                    existing_tool.last_seen_at = datetime.utcnow()
                    
                    # Create invoice record if amount provided
                    if amount:
                        invoice = Invoice(
                            tool_id=existing_tool.id,
                            amount=amount,
                            currency='USD',
                            invoice_date=invoice_date or datetime.utcnow(),
                            source=source
                        )
                        self.db.add(invoice)
                    
                    detected_tools.append({
                        'tool_id': existing_tool.id,
                        'name': existing_tool.name,
                        'source': 'invoice',
                        'amount': amount
                    })
                break  # Only match first pattern found
        
        self.db.commit()
        return detected_tools
    
    async def detect_from_pdf(self, pdf_path: str, organization_id: int) -> List[Dict[str, Any]]:
        """Detect tools from PDF invoice"""
        try:
            import pdfplumber
            
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            return await self.detect_from_invoice_text(
                text, 
                organization_id, 
                source=InvoiceSource.UPLOAD
            )
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return []

