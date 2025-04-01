"""
Report generator module for Tech Health
"""
import os
import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
import jinja2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from analyzer.code_analyzer import analyze_repository, compare_with_benchmarks, get_improvement_suggestions

router = APIRouter()

class ReportRequest(BaseModel):
    """Model for report generation request"""
    owner: str
    repo: str
    access_token: str
    company_name: Optional[str] = None
    include_benchmarks: bool = True
    include_suggestions: bool = True
    format: str = "html"

class ReportMetadata(BaseModel):
    """Model for report metadata"""
    id: str
    repository: str
    generated_at: str
    format: str
    url: Optional[str] = None

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

os.makedirs(template_dir, exist_ok=True)

def create_pdf_report(template_data, report_path):
    """
    Create a PDF report using ReportLab with more robust error handling
    """
    try:
        doc = SimpleDocTemplate(report_path, pagesize=letter, 
                                rightMargin=72, leftMargin=72, 
                                topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        
        title_style = ParagraphStyle(
            'CustomTitle', 
            parent=styles['Title'], 
            fontSize=16,
            textColor=Color(0.16, 0.24, 0.31, 1),
            alignment=TA_CENTER
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle', 
            parent=styles['Normal'], 
            fontSize=10,
            textColor=Color(0.5, 0.5, 0.5, 1),
            alignment=TA_CENTER
        )
        
        content = []
        
        content.append(Paragraph("Tech Health Report", title_style))
        content.append(Spacer(1, 12))
        
        content.append(Paragraph(f"Repository: {template_data.get('repository_name', 'Unknown Repository')}", subtitle_style))
        content.append(Paragraph(f"Generated on {template_data.get('generated_at', 'Unknown Date')}", subtitle_style))
        content.append(Spacer(1, 12))
        
        content.append(Paragraph("Executive Summary", styles['Heading2']))
        overall_score = template_data.get('overall_score', 'N/A')
        content.append(Paragraph(f"Overall Health Score: {overall_score}/100", styles['Normal']))
        
        def safe_get_attr(obj, attr, default='N/A'):
            try:
                return getattr(obj, attr, default)
            except Exception:
                return default
        
        code_quality = template_data.get('code_quality', {})
        commit_frequency = template_data.get('commit_frequency', {})
        tech_debt = template_data.get('tech_debt', {})
        
        content.append(Paragraph("Code Quality Analysis", styles['Heading2']))
        
        code_quality_data = [
            ['Metric', 'Value', 'Rating'],
            ['Cyclomatic Complexity', 
             str(safe_get_attr(code_quality, 'cyclomatic_complexity', 'N/A')), 
             'Good' if (safe_get_attr(code_quality, 'cyclomatic_complexity', 0) <= 10) else 'Poor'],
            ['Maintainability Index', 
             str(safe_get_attr(code_quality, 'maintainability_index', 'N/A')), 
             'Good' if (safe_get_attr(code_quality, 'maintainability_index', 0) >= 70) else 'Poor'],
            ['Test Coverage', 
             f"{safe_get_attr(code_quality, 'test_coverage', 'N/A')}%", 
             'Good' if (safe_get_attr(code_quality, 'test_coverage', 0) >= 70) else 'Poor']
        ]
        
        code_quality_table = Table(code_quality_data, colWidths=[200, 100, 100])
        code_quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        content.append(code_quality_table)
        
        content.append(Paragraph("Technical Debt Analysis", styles['Heading2']))
        content.append(Paragraph(f"Debt Ratio: {safe_get_attr(tech_debt, 'debt_ratio', 'N/A')}%", styles['Normal']))
        
        recommendations = template_data.get('recommendations', [])
        if recommendations:
            content.append(Paragraph("Recommendations", styles['Heading2']))
            recommendation_list = []
            for rec in recommendations:
                recommendation_list.append(Paragraph(rec, styles['Normal']))
            content.extend(recommendation_list)
        
        doc.build(content)
    
    except Exception as e:
        print(f"Error creating PDF report: {e}")
        import traceback
        traceback.print_exc()
        
        doc = SimpleDocTemplate(report_path, pagesize=letter)
        content = [
            Paragraph("Error Generating Report", styles['Heading1']),
            Paragraph(f"An error occurred: {str(e)}", styles['Normal'])
        ]
        doc.build(content)


@router.post("/generate", response_model=ReportMetadata)
async def generate_report(request: ReportRequest):
    """
    Generate a tech health report for a GitHub repository
    """
    try:
        
        try:
            analysis = await analyze_repository(
                owner=request.owner,
                repo=request.repo,
                access_token=request.access_token
            )
        except Exception as analysis_error:
            print(f"Analysis error: {analysis_error}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error analyzing repository"
            )
        
        benchmarks = None
        if request.include_benchmarks:
            try:
                benchmarks = await compare_with_benchmarks(
                    owner=request.owner,
                    repo=request.repo,
                    access_token=request.access_token
                )
            except Exception as benchmark_error:
                print(f"Benchmark error: {benchmark_error}")
                import traceback
                traceback.print_exc()
        
        suggestions = None
        if request.include_suggestions:
            try:
                suggestions = await get_improvement_suggestions(
                    owner=request.owner,
                    repo=request.repo,
                    access_token=request.access_token
                )
            except Exception as suggestion_error:
                print(f"Suggestion error: {suggestion_error}")
                import traceback
                traceback.print_exc()
        
        generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        template_data = {
            "repository_name": f"{request.owner}/{request.repo}",
            "company_name": request.company_name,
            "generated_at": generated_at,
            "overall_score": analysis.overall_score,
            "code_quality": analysis.code_quality,
            "commit_frequency": analysis.commit_frequency,
            "tech_debt": analysis.tech_debt,
            "recommendations": analysis.recommendations,
            "include_benchmarks": request.include_benchmarks,
            "include_suggestions": request.include_suggestions,
            "benchmarks": benchmarks,
            "suggestions": suggestions
        }
        
        report_id = f"{request.owner}-{request.repo}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        reports_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        if request.format == "html":
            template = jinja_env.get_template("report_template.html")
            report_content = template.render(**template_data)
            
            report_path = os.path.join(reports_dir, f"{report_id}.html")
            with open(report_path, "w") as f:
                f.write(report_content)
            
            return ReportMetadata(
                id=report_id,
                repository=f"{request.owner}/{request.repo}",
                generated_at=generated_at,
                format="html",
                # url=f"/api/report/download/{report_id}.html"
                url=f"http://localhost:8000/api/report/download/{report_id}.html"
                # FIXME: in real world applications we must set this to env variable
            )
        
        elif request.format == "pdf":
            report_path = os.path.join(reports_dir, f"{report_id}.pdf")
            create_pdf_report(template_data, report_path)
            
            return ReportMetadata(
                id=report_id,
                repository=f"{request.owner}/{request.repo}",
                generated_at=generated_at,
                format="pdf",
                url=f"http://localhost:8000/api/report/download/{report_id}.html"
                # FIXME: in real world applications we must set this to env variable
            )
        
        elif request.format == "markdown":
            template = jinja_env.get_template("report_template.md")
            report_content = template.render(**template_data)
            
            report_path = os.path.join(reports_dir, f"{report_id}.md")
            with open(report_path, "w") as f:
                f.write(report_content)
            
            return ReportMetadata(
                id=report_id,
                repository=f"{request.owner}/{request.repo}",
                generated_at=generated_at,
                format="markdown",
                # url=f"/api/report/download/{report_id}.md"
                url=f"http://localhost:8000/api/report/download/{report_id}.md"
                # FIXME: in real world applications we must set this to env variable
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {request.format}"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )

@router.get("/download/{filename}", response_class=FileResponse)
async def download_report(filename: str):
    """
    Download a generated report
    """
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    file_path = os.path.join(reports_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {filename} not found"
        )
    
    if filename.endswith(".html"):
        media_type = "text/html"
    elif filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".md"):
        media_type = "text/markdown"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

@router.get("/list", response_model=List[ReportMetadata])
async def list_reports():
    """
    List all generated reports
    """
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    reports = []
    for filename in os.listdir(reports_dir):
        if "." in filename:
            report_id, format_ext = filename.rsplit(".", 1)
            
            parts = report_id.split("-")
            if len(parts) >= 3:
                owner = parts[0]
                repo = parts[1]
                repository = f"{owner}/{repo}"
                timestamp_str = "-".join(parts[2:])
                
                try:
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                    generated_at = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    generated_at = "Unknown"
                
                reports.append(
                    ReportMetadata(
                        id=report_id,
                        repository=repository,
                        generated_at=generated_at,
                        format=format_ext,
                        # url=f"/api/report/download/{filename}"
                        url=f"http://localhost:8000/api/report/download/{filename}"
                        # FIXME: in real world applications we must set this to env variable
                    )
                )
    
    reports.sort(key=lambda x: x.generated_at, reverse=True)
    
    return reports