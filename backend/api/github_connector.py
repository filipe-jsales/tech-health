"""
GitHub API integration module for Tech Health
"""
import os
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from github import Github, GithubException
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class GitHubCredentials(BaseModel):
    """Model for GitHub credentials"""
    access_token: str

class Repository(BaseModel):
    """Model for repository information"""
    name: str
    owner: str
    url: str
    description: Optional[str] = None
    stars: int
    forks: int
    open_issues: int
    language: Optional[str] = None
    created_at: str
    updated_at: str

class CommitInfo(BaseModel):
    """Model for commit information"""
    sha: str
    message: str
    author: str
    date: str
    additions: Optional[int] = None
    deletions: Optional[int] = None
    files_changed: Optional[int] = None

class BranchInfo(BaseModel):
    """Model for branch information"""
    name: str
    protected: bool
    last_commit: Optional[str] = None

def get_github_client(access_token: str):
    """
    Create a GitHub client using the provided access token
    """
    try:
        return Github(access_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid GitHub credentials: {str(e)}"
        )

@router.post("/connect", response_model=Dict[str, str])
async def connect_to_github(credentials: GitHubCredentials):
    """
    Test GitHub connection with provided credentials
    """
    try:
        g = get_github_client(credentials.access_token)
        user = g.get_user()
        return {
            "status": "connected",
            "username": user.login,
            "message": f"Successfully connected to GitHub as {user.login}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to connect to GitHub: {str(e)}"
        )

@router.get("/repositories", response_model=List[Repository])
async def get_repositories(access_token: str):
    """
    Get list of repositories accessible by the user
    """
    try:
        g = get_github_client(access_token)
        user = g.get_user()
        repos = []
        
        for repo in user.get_repos():
            repos.append(
                Repository(
                    name=repo.name,
                    owner=repo.owner.login,
                    url=repo.html_url,
                    description=repo.description,
                    stars=repo.stargazers_count,
                    forks=repo.forks_count,
                    open_issues=repo.open_issues_count,
                    language=repo.language,
                    created_at=repo.created_at.isoformat(),
                    updated_at=repo.updated_at.isoformat()
                )
            )
        
        return repos
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching repositories: {str(e)}"
        )

@router.get("/repository/{owner}/{repo}", response_model=Repository)
async def get_repository(owner: str, repo: str, access_token: str):
    """
    Get detailed information about a specific repository
    """
    try:
        g = get_github_client(access_token)
        repository = g.get_repo(f"{owner}/{repo}")
        
        return Repository(
            name=repository.name,
            owner=repository.owner.login,
            url=repository.html_url,
            description=repository.description,
            stars=repository.stargazers_count,
            forks=repository.forks_count,
            open_issues=repository.open_issues_count,
            language=repository.language,
            created_at=repository.created_at.isoformat(),
            updated_at=repository.updated_at.isoformat()
        )
    
    except GithubException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {owner}/{repo} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching repository: {str(e)}"
        )

@router.get("/repository/{owner}/{repo}/commits", response_model=List[CommitInfo])
async def get_repository_commits(owner: str, repo: str, access_token: str, limit: int = 100):
    """
    Get commit history for a repository
    """
    try:
        g = get_github_client(access_token)
        repository = g.get_repo(f"{owner}/{repo}")
        commits = []
        
        for commit in repository.get_commits()[:limit]:
            commit_data = CommitInfo(
                sha=commit.sha,
                message=commit.commit.message,
                author=commit.commit.author.name,
                date=commit.commit.author.date.isoformat(),
                additions=commit.stats.additions if hasattr(commit, 'stats') else None,
                deletions=commit.stats.deletions if hasattr(commit, 'stats') else None,
                files_changed=len(commit.files) if hasattr(commit, 'files') else None
            )
            commits.append(commit_data)
        
        return commits
    
    except GithubException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {owner}/{repo} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching commits: {str(e)}"
        )

@router.get("/repository/{owner}/{repo}/branches", response_model=List[BranchInfo])
async def get_repository_branches(owner: str, repo: str, access_token: str):
    """
    Get branches for a repository
    """
    try:
        g = get_github_client(access_token)
        repository = g.get_repo(f"{owner}/{repo}")
        branches = []
        
        for branch in repository.get_branches():
            branch_data = BranchInfo(
                name=branch.name,
                protected=branch.protected,
                last_commit=branch.commit.sha if branch.commit else None
            )
            branches.append(branch_data)
        
        return branches
    
    except GithubException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {owner}/{repo} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching branches: {str(e)}"
        )

@router.get("/repository/{owner}/{repo}/contents", response_model=Dict)
async def get_repository_contents(owner: str, repo: str, access_token: str, path: str = ""):
    """
    Get contents of a repository at a specific path
    """
    try:
        g = get_github_client(access_token)
        repository = g.get_repo(f"{owner}/{repo}")
        contents = repository.get_contents(path)
        
        result = {
            "path": path,
            "files": [],
            "directories": []
        }
        
        if not isinstance(contents, list):
            contents = [contents]
        
        for content in contents:
            if content.type == "file":
                result["files"].append({
                    "name": content.name,
                    "path": content.path,
                    "size": content.size,
                    "type": content.type,
                    "download_url": content.download_url
                })
            elif content.type == "dir":
                result["directories"].append({
                    "name": content.name,
                    "path": content.path,
                    "type": content.type
                })
        
        return result
    
    except GithubException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {owner}/{repo} or path {path} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching repository contents: {str(e)}"
        )

@router.get("/repository/{owner}/{repo}/file", response_model=Dict)
async def get_repository_file_content(owner: str, repo: str, access_token: str, path: str):
    """
    Get content of a specific file in a repository
    """
    try:
        g = get_github_client(access_token)
        repository = g.get_repo(f"{owner}/{repo}")
        file_content = repository.get_contents(path)
        
        if isinstance(file_content, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path {path} is a directory, not a file"
            )
        
        content = file_content.decoded_content.decode('utf-8')
        
        return {
            "name": file_content.name,
            "path": file_content.path,
            "size": file_content.size,
            "content": content
        }
    
    except GithubException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {path} not found in repository {owner}/{repo}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API error: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching file content: {str(e)}"
        )