"""
Document Download Routes
Serve generated campaign documents as downloadable files
"""
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
from typing import Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

# In-memory storage for generated documents (for demo)
# In production, use Redis or database
document_store: Dict[str, str] = {}
campaign_store: Dict[str, Dict] = {}  # Store campaign data for HTML rendering


@router.post("/save")
async def save_document(doc_id: str, content: str):
    """Save a document for later retrieval"""
    document_store[doc_id] = content
    return {"success": True, "doc_id": doc_id}


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Get document as plain text/markdown"""
    content = document_store.get(doc_id)
    
    if not content:
        return PlainTextResponse(
            content="Document not found",
            status_code=404
        )
    
    return PlainTextResponse(
        content=content,
        headers={
            "Content-Disposition": f"attachment; filename=campaign_{doc_id}.md"
        }
    )


def _generate_html_website(doc_id: str, markdown_content: str, campaign_data: Dict) -> str:
    """Generate beautiful HTML website for campaign document"""
    
    # Extract data
    product_name = campaign_data.get('product', 'Campaign')
    platforms = campaign_data.get('platforms_strategy', {})
    budget = campaign_data.get('budget', {})
    kpis = campaign_data.get('kpis', [])
    recommendations = campaign_data.get('recommendations', [])
    schedule = campaign_data.get('schedule', {})
    
    duration = schedule.get('duration_days', 30)
    
    html = f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Campaign Plan - {product_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section h3 {{
            color: #764ba2;
            font-size: 1.3rem;
            margin: 20px 0 10px 0;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .card h4 {{
            color: #667eea;
            font-size: 1.1rem;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .card p {{
            color: #666;
            font-size: 0.95rem;
        }}
        
        .stat {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .stat .number {{
            font-size: 2.5rem;
            font-weight: 700;
            display: block;
        }}
        
        .stat .label {{
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        .list {{
            list-style: none;
            padding: 0;
        }}
        
        .list li {{
            background: white;
            padding: 15px 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .list li:before {{
            content: "✓";
            background: #667eea;
            color: white;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin: 10px 10px 10px 0;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-outline {{
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }}
        
        .footer {{
            background: #2d3748;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .footer p {{
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .section {{
                padding: 20px;
            }}
            
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🎯 Marketing Campaign Plan</h1>
            <div class="subtitle">{product_name}</div>
        </div>
        
        <!-- Overview Stats -->
        <div class="content">
            <div class="grid">
                <div class="stat">
                    <span class="number">{duration}</span>
                    <span class="label">Days Duration</span>
                </div>
                <div class="stat">
                    <span class="number">{len(platforms)}</span>
                    <span class="label">Platforms</span>
                </div>
                <div class="stat">
                    <span class="number">{len(kpis)}</span>
                    <span class="label">KPIs Tracked</span>
                </div>
            </div>
            
            <!-- Platform Strategy -->
            <div class="section">
                <h2>🚀 Platform Strategy</h2>
                <div class="grid">
"""
    
    # Add platforms
    platform_icons = {
        "Instagram": "📸",
        "Facebook": "👥",
        "TikTok": "🎵",
        "Tokopedia": "🛍️",
        "Shopee": "🛒",
        "Twitter": "🐦",
        "YouTube": "📺"
    }
    
    for platform, strategy in platforms.items():
        icon = platform_icons.get(platform, "📱")
        html += f"""
                    <div class="card">
                        <h4>{icon} {platform}</h4>
                        <p>{strategy}</p>
                    </div>
"""
    
    html += """
                </div>
            </div>
            
            <!-- KPIs -->
            <div class="section">
                <h2>📈 Key Performance Indicators</h2>
                <ul class="list">
"""
    
    for kpi in kpis:
        html += f"""
                    <li>{kpi}</li>
"""
    
    html += """
                </ul>
            </div>
            
            <!-- Recommendations -->
            <div class="section">
                <h2>💡 Recommendations</h2>
                <ul class="list">
"""
    
    for rec in recommendations:
        html += f"""
                    <li>{rec}</li>
"""
    
    html += f"""
                </ul>
            </div>
            
            <!-- Budget Tracking Table -->
            <div class="section">
                <h2>📊 Budget Tracking Sheet</h2>
                <p>Copy table di bawah ke Google Sheets untuk tracking campaign:</p>
                
                <h3>Platform Budget Allocation</h3>
                <table style="width:100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background: #667eea; color: white;">
                            <th style="padding: 12px; border: 1px solid #ddd;">Platform</th>
                            <th style="padding: 12px; border: 1px solid #ddd;">Percentage</th>
                            <th style="padding: 12px; border: 1px solid #ddd;">Budget</th>
                            <th style="padding: 12px; border: 1px solid #ddd;">Daily Budget</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add budget allocation table
    total_budget = 5000000
    duration = schedule.get('duration_days', 30)
    platform_allocations = {
        "Instagram": 35,
        "Facebook": 25,
        "TikTok": 30,
        "Tokopedia": 10
    }
    
    for platform in platforms.keys():
        if platform in platform_allocations:
            percentage = platform_allocations[platform]
            amount = (total_budget * percentage) / 100
            daily = amount / duration
            html += f"""
                        <tr style="background: white;">
                            <td style="padding: 12px; border: 1px solid #ddd; font-weight: 600;">{platform}</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{percentage}%</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: right;">Rp {amount:,.0f}</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: right;">Rp {daily:,.0f}</td>
                        </tr>
"""
    
    html += f"""
                    </tbody>
                    <tfoot>
                        <tr style="background: #f8f9fa; font-weight: 600;">
                            <td style="padding: 12px; border: 1px solid #ddd;">TOTAL</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">100%</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: right;">Rp {total_budget:,.0f}</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: right;">Rp {total_budget/duration:,.0f}</td>
                        </tr>
                    </tfoot>
                </table>
                
                <h3>Daily Tracking Template</h3>
                <p>Headers untuk copy ke Google Sheets:</p>
                <div style="background: #2d3748; color: #fff; padding: 15px; border-radius: 8px; overflow-x: auto;">
                    <code style="white-space: pre; font-size: 0.9rem;">
Date | Platform | Type | Spent | Impressions | Clicks | CTR% | Conversions | Conv Rate% | CPC | Cost/Conv | Revenue | ROI% | Notes

Formula untuk CTR%: =F2/E2*100
Formula untuk Conv Rate%: =H2/F2*100
Formula untuk CPC: =D2/F2
Formula untuk Cost/Conv: =D2/H2
Formula untuk ROI%: =(L2-D2)/D2*100
                    </code>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div style="text-align: center; margin-top: 40px;">
                <a href="/documents/{doc_id}" download class="btn">📥 Download Markdown</a>
                <a href="https://docs.google.com/spreadsheets/create" target="_blank" class="btn btn-outline">📊 Create Tracking Sheet</a>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>Generated by TrendScout AI Marketing Agent</p>
            <p style="margin-top: 10px; font-size: 0.9rem;">Ready to launch! 🚀</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


@router.get("/{doc_id}/view")
async def view_document(doc_id: str):
    """View document as beautifully formatted HTML website"""
    content = document_store.get(doc_id)
    campaign_data = campaign_store.get(doc_id, {})
    
    if not content:
        return Response(content="Document not found", status_code=404)
    
    # Generate beautiful HTML website
    html_content = _generate_html_website(doc_id, content, campaign_data)
    
    return Response(content=html_content, media_type="text/html")
