"""
Code analysis module for Tech Health
"""
import os
import tempfile
import subprocess
import json
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from github import Github
import radon.complexity as radon_cc
import radon.metrics as radon_metrics
from radon.raw import analyze
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

router = APIRouter()

class CodeQualityMetrics(BaseModel):
    """Model for code quality metrics"""
    cyclomatic_complexity: float
    maintainability_index: float
    lines_of_code: int
    comment_ratio: float
    test_coverage: Optional[float] = None

class CommitFrequencyMetrics(BaseModel):
    """Model for commit frequency metrics"""
    daily_average: float
    weekly_average: float
    monthly_average: float
    trend: str
    contributors_count: int
    commit_distribution: Dict[str, int]

class TechDebtMetrics(BaseModel):
    """Model for technical debt metrics"""
    debt_ratio: float
    estimated_hours: int
    critical_files: List[str]
    debt_by_category: Dict[str, float]

class SecurityMetrics(BaseModel):
    """Model for security metrics"""
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    security_score: float

class AnalysisResult(BaseModel):
    """Model for complete analysis result"""
    repository_name: str
    analysis_date: str
    code_quality: CodeQualityMetrics
    commit_frequency: CommitFrequencyMetrics
    tech_debt: TechDebtMetrics
    security: Optional[SecurityMetrics] = None
    overall_score: float
    recommendations: List[str]

def calculate_cyclomatic_complexity(code: str) -> float:
    """
    Calculate the average cyclomatic complexity of the code
    """
    try:
        import re
        
        def parse_block(block):
            try:
                results = radon_cc.cc_visit(block)
                return sum(result.complexity for result in results) / len(results) if results else 0.0
            except Exception:
                return 0.0
        
        function_pattern = re.compile(r'^def\s+\w+\s*\(.*\)\s*:', re.MULTILINE)
        function_blocks = function_pattern.split(code)
        complexities = [parse_block(block) for block in function_blocks if block.strip()]
        
        return sum(complexities) / len(complexities) if complexities else 0.0
    
    except Exception as e:
        print(f"Error calculating cyclomatic complexity: {e}")
        return 0.0

def calculate_maintainability_index(code: str) -> float:
    """
    Calculate the maintainability index of the code
    """
    try:
        mi = radon_metrics.mi_visit(code, multi=True)
        return mi if mi else 0.0
    except Exception as e:
        print(f"Error calculating maintainability index: {e}")
        return 0.0

def analyze_code_quality(files: Dict[str, str]) -> CodeQualityMetrics:
    """
    Analyze the quality of code in the provided files
    """
    total_cc = 0.0
    total_mi = 0.0
    total_loc = 0
    total_comments = 0
    total_sloc = 0
    processed_files = 0
    
    for filename, content in files.items():
        if not any(filename.endswith(ext) for ext in ['.py', '.js', '.java', '.cs', '.php', '.rb', '.go']):
            continue
        
        try:
            cc = calculate_cyclomatic_complexity(content)
            mi = calculate_maintainability_index(content)
            
            try:
                raw_metrics = analyze(content)
                loc = raw_metrics.loc
                comments = raw_metrics.comments
                sloc = raw_metrics.sloc
            except Exception as e:
                print(f"Warning: Could not parse {filename}. Error: {e}")
                continue
            
            total_cc += cc
            total_mi += mi
            total_loc += loc
            total_comments += comments
            total_sloc += sloc
            processed_files += 1
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    avg_cc = total_cc / processed_files if processed_files > 0 else 0
    avg_mi = total_mi / processed_files if processed_files > 0 else 0
    comment_ratio = (total_comments / total_sloc * 100) if total_sloc > 0 else 0
    
    #FIXME For this MVP, we're setting a placeholder for test coverage
    #FIXME In a real implementation, you would analyze test files and calculate actual coverage
    test_coverage = 65.0  #placeholder
    
    return CodeQualityMetrics(
        cyclomatic_complexity=round(avg_cc, 2),
        maintainability_index=round(avg_mi, 2),
        lines_of_code=total_loc,
        comment_ratio=round(comment_ratio, 2),
        test_coverage=test_coverage
    )


def analyze_commit_frequency(commits: List[Dict]) -> CommitFrequencyMetrics:
    """
    Analyze commit frequency and patterns
    """
    df = pd.DataFrame(commits)
    
    df['date'] = pd.to_datetime(df['date'])
    
    start_date = df['date'].min()
    end_date = df['date'].max()
    date_range = (end_date - start_date).days + 1
    
    date_range = max(date_range, 1)
    
    daily_commits = df.groupby(df['date'].dt.date).size()
    weekly_commits = df.groupby(pd.Grouper(key='date', freq='W')).size()
    monthly_commits = df.groupby(pd.Grouper(key='date', freq='M')).size()
    
    daily_avg = len(df) / date_range
    weekly_avg = len(df) / (date_range / 7) if date_range >= 7 else daily_avg * 7
    monthly_avg = len(df) / (date_range / 30) if date_range >= 30 else daily_avg * 30
    
    mid_point = start_date + (end_date - start_date) / 2
    recent_commits = df[df['date'] > mid_point].shape[0]
    older_commits = df[df['date'] <= mid_point].shape[0]
    
    if recent_commits > older_commits * 1.2:
        trend = "increasing"
    elif recent_commits < older_commits * 0.8:
        trend = "decreasing"
    else:
        trend = "stable"
    
    contributors = df['author'].unique()
    
    commit_distribution = df['author'].value_counts().to_dict()
    
    return CommitFrequencyMetrics(
        daily_average=round(daily_avg, 2),
        weekly_average=round(weekly_avg, 2),
        monthly_average=round(monthly_avg, 2),
        trend=trend,
        contributors_count=len(contributors),
        commit_distribution=commit_distribution
    )

def estimate_tech_debt(files: Dict[str, str]) -> TechDebtMetrics:
    """
    Estimate technical debt in the codebase
    """
    debt_by_file = {}
    debt_by_category = {
        "code_complexity": 0.0,
        "documentation": 0.0,
        "architecture": 0.0,
        "test_coverage": 0.0
    }
    
    critical_files = []
    total_loc = 0
    
    for filename, content in files.items():
        if not any(filename.endswith(ext) for ext in ['.py', '.js', '.java', '.cs', '.php', '.rb', '.go']):
            continue
        
        raw_metrics = analyze(content)
        loc = raw_metrics.loc
        total_loc += loc
        
        cc = calculate_cyclomatic_complexity(content)
        mi = calculate_maintainability_index(content)
        comment_ratio = (raw_metrics.comments / raw_metrics.sloc * 100) if raw_metrics.sloc > 0 else 0
        
        complexity_debt = min(100, max(0, (cc - 5) * 10)) if cc > 5 else 0
        docs_debt = min(100, max(0, (10 - comment_ratio) * 5)) if comment_ratio < 10 else 0
        
        #FIXME Architecture debt is a placeholder for MVP
        #FIXME  In a real implementation, this would analyze imports, dependencies, etc.
        architecture_debt = min(100, max(0, (100 - mi)))
        
        file_debt = (complexity_debt + docs_debt + architecture_debt) / 3
        debt_by_file[filename] = file_debt
        
        debt_by_category["code_complexity"] += complexity_debt * loc
        debt_by_category["documentation"] += docs_debt * loc
        debt_by_category["architecture"] += architecture_debt * loc
        
        if file_debt > 60 and loc > 100:
            critical_files.append(filename)
    
    for category in debt_by_category:
        debt_by_category[category] = round(debt_by_category[category] / total_loc if total_loc > 0 else 0, 2)
    debt_ratio = sum(debt_by_category.values()) / len(debt_by_category) if debt_by_category else 0
    estimated_hours = int(total_loc / 100 * debt_ratio / 10)
    
    return TechDebtMetrics(
        debt_ratio=round(debt_ratio, 2),
        estimated_hours=estimated_hours,
        critical_files=critical_files[:10],
        debt_by_category=debt_by_category
    )

@router.post("/repository", response_model=AnalysisResult)
async def analyze_repository(owner: str, repo: str, access_token: str):
    """
    Perform full analysis on a repository
    """
    try:
        g = Github(access_token)
        repository = g.get_repo(f"{owner}/{repo}")
        
        contents = repository.get_contents("")
        files = {}
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repository.get_contents(file_content.path))
            else:
                try:
                    if any(file_content.name.endswith(ext) for ext in [
                        '.py', '.js', '.java', '.cs', '.php', '.rb', '.go',
                        '.html', '.css', '.md', '.txt', '.json', '.xml', '.yaml', '.yml'
                    ]):
                        # Decode only if content is not too large
                        if file_content.size < 1_000_000:  # 1MB limit
                            decoded_content = file_content.decoded_content.decode('utf-8', errors='ignore')
                            # Ignore empty or minimal files
                            if len(decoded_content.strip()) > 10:
                                files[file_content.path] = decoded_content
                except Exception as e:
                    print(f"Error processing file {file_content.path}: {e}")
                    continue
        
        commits_data = []
        commits = repository.get_commits()
        for commit in commits:
            commits_data.append({
                "sha": commit.sha,
                "message": commit.commit.message,
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat()
            })
        
        code_quality = analyze_code_quality(files)
        commit_frequency = analyze_commit_frequency(commits_data)
        tech_debt = estimate_tech_debt(files)
        
        try:
            quality_score = 100 - (code_quality.cyclomatic_complexity * 2)
            quality_score += code_quality.maintainability_index / 2
            quality_score += code_quality.comment_ratio / 2
            quality_score = max(0, min(100, quality_score)) * 0.4
            
            commit_score = min(100, commit_frequency.weekly_average * 5) * 0.3
            
            debt_score = (100 - tech_debt.debt_ratio) * 0.3
            
            overall_score = quality_score + commit_score + debt_score
        except Exception as score_error:
            print(f"Error calculating overall score: {score_error}")
            overall_score = 50.0  #default middle score
        
        recommendations = []
        
        if code_quality.cyclomatic_complexity > 10:
            recommendations.append("Reduce code complexity in critical files")
        
        if code_quality.comment_ratio < 10:
            recommendations.append("Improve code documentation and comments")
        
        if tech_debt.debt_ratio > 40:
            recommendations.append("Address technical debt in critical files")
        
        if commit_frequency.trend == "decreasing":
            recommendations.append("Increase development activity")
        
        if len(tech_debt.critical_files) > 0:
            recommendations.append(f"Focus on refactoring these critical files: {', '.join(tech_debt.critical_files[:3])}")
        
        result = AnalysisResult(
            repository_name=f"{owner}/{repo}",
            analysis_date=datetime.now().isoformat(),
            code_quality=code_quality,
            commit_frequency=commit_frequency,
            tech_debt=tech_debt,
            overall_score=round(overall_score, 2),
            recommendations=recommendations
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing repository: {str(e)}"
        )

@router.get("/metrics/compare", response_model=Dict)
async def compare_with_benchmarks(owner: str, repo: str, access_token: str):
    """
    Compare repository metrics with industry benchmarks
    """
    try:
        analysis = await analyze_repository(owner, repo, access_token)
        
        benchmarks = {
            "code_quality": {
                "cyclomatic_complexity": {
                    "excellent": 5.0,
                    "good": 10.0,
                    "average": 15.0,
                    "poor": 25.0
                },
                "maintainability_index": {
                    "excellent": 85.0,
                    "good": 75.0,
                },
                "maintainability_index": {
                    "excellent": 85.0,
                    "good": 75.0,
                    "average": 65.0,
                    "poor": 50.0
                },
                "comment_ratio": {
                    "excellent": 25.0,
                    "good": 15.0,
                    "average": 10.0,
                    "poor": 5.0
                },
                "test_coverage": {
                    "excellent": 80.0,
                    "good": 70.0,
                    "average": 50.0,
                    "poor": 30.0
                }
            },
            "commit_frequency": {
                "weekly_average": {
                    "excellent": 20.0,
                    "good": 10.0,
                    "average": 5.0,
                    "poor": 2.0
                },
                "contributors_count": {
                    "excellent": 10,
                    "good": 5,
                    "average": 3,
                    "poor": 1
                }
            },
            "tech_debt": {
                "debt_ratio": {
                    "excellent": 10.0,
                    "good": 25.0,
                    "average": 40.0,
                    "poor": 60.0
                }
            }
        }
        
        comparison = {
            "code_quality": {},
            "commit_frequency": {},
            "tech_debt": {},
            "overall": {}
        }
        
        for metric in ["cyclomatic_complexity", "maintainability_index", "comment_ratio", "test_coverage"]:
            if hasattr(analysis.code_quality, metric):
                value = getattr(analysis.code_quality, metric)
                benchmark = benchmarks["code_quality"].get(metric, {})
                
                if metric == "cyclomatic_complexity":
                    if value <= benchmark.get("excellent", 0):
                        rating = "excellent"
                    elif value <= benchmark.get("good", 0):
                        rating = "good"
                    elif value <= benchmark.get("average", 0):
                        rating = "average"
                    else:
                        rating = "poor"
                else:
                    # For other metrics, higher is better
                    if value >= benchmark.get("excellent", 0):
                        rating = "excellent"
                    elif value >= benchmark.get("good", 0):
                        rating = "good"
                    elif value >= benchmark.get("average", 0):
                        rating = "average"
                    else:
                        rating = "poor"
                
                comparison["code_quality"][metric] = {
                    "value": value,
                    "benchmarks": benchmark,
                    "rating": rating
                }
        
        for metric in ["weekly_average", "contributors_count"]:
            if hasattr(analysis.commit_frequency, metric):
                value = getattr(analysis.commit_frequency, metric)
                benchmark = benchmarks["commit_frequency"].get(metric, {})
                
                if value >= benchmark.get("excellent", 0):
                    rating = "excellent"
                elif value >= benchmark.get("good", 0):
                    rating = "good"
                elif value >= benchmark.get("average", 0):
                    rating = "average"
                else:
                    rating = "poor"
                
                comparison["commit_frequency"][metric] = {
                    "value": value,
                    "benchmarks": benchmark,
                    "rating": rating
                }
        
        for metric in ["debt_ratio"]:
            if hasattr(analysis.tech_debt, metric):
                value = getattr(analysis.tech_debt, metric)
                benchmark = benchmarks["tech_debt"].get(metric, {})
                
                if value <= benchmark.get("excellent", 0):
                    rating = "excellent"
                elif value <= benchmark.get("good", 0):
                    rating = "good"
                elif value <= benchmark.get("average", 0):
                    rating = "average"
                else:
                    rating = "poor"
                
                comparison["tech_debt"][metric] = {
                    "value": value,
                    "benchmarks": benchmark,
                    "rating": rating
                }
        
        overall_ratings = []
        for category in ["code_quality", "commit_frequency", "tech_debt"]:
            for metric_data in comparison[category].values():
                overall_ratings.append(metric_data["rating"])
        
        rating_counts = {
            "excellent": overall_ratings.count("excellent"),
            "good": overall_ratings.count("good"),
            "average": overall_ratings.count("average"),
            "poor": overall_ratings.count("poor")
        }
        
        total_metrics = len(overall_ratings)
        excellent_good_count = rating_counts["excellent"] + rating_counts["good"]
        percentile = round(excellent_good_count / total_metrics * 100 if total_metrics > 0 else 0)
        
        if percentile >= 75:
            overall_rating = "excellent"
        elif percentile >= 50:
            overall_rating = "good"
        elif percentile >= 25:
            overall_rating = "average"
        else:
            overall_rating = "poor"
        
        comparison["overall"] = {
            "percentile": percentile,
            "rating": overall_rating,
            "rating_distribution": rating_counts
        }
        
        return comparison
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing with benchmarks: {str(e)}"
        )

@router.get("/suggestions", response_model=Dict)
async def get_improvement_suggestions(owner: str, repo: str, access_token: str):
    """
    Get detailed suggestions for improving repository health
    """
    try:
        analysis = await analyze_repository(owner, repo, access_token)
        
        suggestions = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "estimated_effort": {}
        }
        
        if analysis.code_quality.cyclomatic_complexity > 15:
            suggestions["high_priority"].append({
                "category": "code_quality",
                "title": "Reduce code complexity in critical files",
                "description": "High cyclomatic complexity ({}), indicates code that is difficult to understand, test, and maintain. Refactor complex functions into smaller, more manageable pieces.".format(analysis.code_quality.cyclomatic_complexity),
                "impact": "High"
            })
        elif analysis.code_quality.cyclomatic_complexity > 10:
            suggestions["medium_priority"].append({
                "category": "code_quality",
                "title": "Consider reducing code complexity",
                "description": "Moderate cyclomatic complexity ({}), could be improved by refactoring complex methods.".format(analysis.code_quality.cyclomatic_complexity),
                "impact": "Medium"
            })
        
        if analysis.code_quality.maintainability_index < 65:
            suggestions["high_priority"].append({
                "category": "code_quality",
                "title": "Improve code maintainability",
                "description": "Low maintainability index ({}), indicates code that is difficult to maintain. Focus on improving code structure, reducing complexity, and increasing documentation.".format(analysis.code_quality.maintainability_index),
                "impact": "High"
            })
        elif analysis.code_quality.maintainability_index < 75:
            suggestions["medium_priority"].append({
                "category": "code_quality",
                "title": "Enhance code maintainability",
                "description": "Moderate maintainability index ({}), could be improved with better documentation and code structure.".format(analysis.code_quality.maintainability_index),
                "impact": "Medium"
            })
        
        if analysis.code_quality.comment_ratio < 5:
            suggestions["high_priority"].append({
                "category": "code_quality",
                "title": "Significantly increase code documentation",
                "description": "Very low comment ratio ({}%), makes code difficult for new developers to understand. Add meaningful comments to explain complex logic, business rules, and important decisions.".format(analysis.code_quality.comment_ratio),
                "impact": "High"
            })
        elif analysis.code_quality.comment_ratio < 10:
            suggestions["medium_priority"].append({
                "category": "code_quality",
                "title": "Improve code documentation",
                "description": "Low comment ratio ({}%), could be improved to enhance code readability and maintenance.".format(analysis.code_quality.comment_ratio),
                "impact": "Medium"
            })
        
        if analysis.code_quality.test_coverage < 50:
            suggestions["high_priority"].append({
                "category": "testing",
                "title": "Increase test coverage",
                "description": "Low test coverage ({}%), indicates high risk of introducing regressions with new changes. Add unit and integration tests for critical components.".format(analysis.code_quality.test_coverage),
                "impact": "High"
            })
        elif analysis.code_quality.test_coverage < 70:
            suggestions["medium_priority"].append({
                "category": "testing",
                "title": "Improve test coverage",
                "description": "Moderate test coverage ({}%), should be improved to enhance code reliability.".format(analysis.code_quality.test_coverage),
                "impact": "Medium"
            })
        
        if analysis.commit_frequency.trend == "decreasing":
            suggestions["high_priority"].append({
                "category": "development_activity",
                "title": "Address declining development activity",
                "description": "Commit frequency is decreasing, which may indicate reduced development velocity or project health issues.",
                "impact": "High"
            })
        
        if analysis.commit_frequency.weekly_average < 3:
            suggestions["medium_priority"].append({
                "category": "development_activity",
                "title": "Increase development velocity",
                "description": "Low commit frequency (average {} commits per week), may indicate low development activity.".format(analysis.commit_frequency.weekly_average),
                "impact": "Medium"
            })
        
        if analysis.commit_frequency.contributors_count < 2:
            suggestions["high_priority"].append({
                "category": "team",
                "title": "Increase the number of contributors",
                "description": "Having only {} contributor(s) creates a bus factor risk. Onboard additional developers to the project.".format(analysis.commit_frequency.contributors_count),
                "impact": "High"
            })
        elif analysis.commit_frequency.contributors_count < 4:
            suggestions["low_priority"].append({
                "category": "team",
                "title": "Consider expanding the contributor base",
                "description": "Having {} contributors could be improved to distribute knowledge and reduce risk.".format(analysis.commit_frequency.contributors_count),
                "impact": "Low"
            })
        
        if analysis.tech_debt.debt_ratio > 50:
            suggestions["high_priority"].append({
                "category": "tech_debt",
                "title": "Address significant technical debt",
                "description": "High technical debt ratio ({}%), indicates substantial maintenance burden. Address critical files identified in the analysis.".format(analysis.tech_debt.debt_ratio),
                "impact": "High"
            })
        elif analysis.tech_debt.debt_ratio > 30:
            suggestions["medium_priority"].append({
                "category": "tech_debt",
                "title": "Reduce technical debt",
                "description": "Moderate technical debt ratio ({}%), should be addressed to improve maintainability.".format(analysis.tech_debt.debt_ratio),
                "impact": "Medium"
            })
        
        if analysis.tech_debt.critical_files:
            suggestions["high_priority"].append({
                "category": "tech_debt",
                "title": "Refactor critical files",
                "description": "These files have high technical debt and should be prioritized for refactoring: {}".format(", ".join(analysis.tech_debt.critical_files[:3])),
                "impact": "High"
            })
        
        high_count = len(suggestions["high_priority"])
        medium_count = len(suggestions["medium_priority"])
        low_count = len(suggestions["low_priority"])
        
        suggestions["estimated_effort"] = {
            "hours": analysis.tech_debt.estimated_hours,
            "developer_weeks": round(analysis.tech_debt.estimated_hours / 40, 1),
            "approximate_cost": "${:,.0f} - ${:,.0f}".format(
                analysis.tech_debt.estimated_hours * 100,
                analysis.tech_debt.estimated_hours * 150 
            ),
            "suggestion_count": {
                "high_priority": high_count,
                "medium_priority": medium_count,
                "low_priority": low_count,
                "total": high_count + medium_count + low_count
            }
        }
        
        return suggestions
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating suggestions: {str(e)}"
        )