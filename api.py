"""
简历分析系统 - FastAPI API 版本
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import tempfile
import os

from core.workflow import app as workflow_app
from util.file_handler import pdf_loader

api_app = FastAPI(
    title="简历分析系统 API",
    description="基于多智能体的简历分析系统",
    version="1.0.0"
)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #允许所有域名
    allow_credentials=True, #允许cookie
    allow_methods=["*"],    #允许所有http方法
    allow_headers=["*"],    #允许所有请求头
)


class ResumeAnalysisRequest(BaseModel):
    job_requirements: Optional[str] = None #选填
    thread_id: str = "default_user"


class ResumeTextRequest(ResumeAnalysisRequest):
    resume_text: str


class AnalysisResult(BaseModel):
    status: str
    data: dict
    message: str


@api_app.get("/")
async def root():
    return {"message": "简历分析系统 API 运行中"}


@api_app.post("/analyze/pdf", response_model=AnalysisResult)
async def analyze_pdf(
    file: UploadFile = File(...),
    job_requirements: Optional[str] = None,
    thread_id: str = "default_user"
):
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            documents = pdf_loader(tmp_path)
            if not documents:
                raise HTTPException(status_code=400, detail="无法读取PDF内容")
            resume_text = "\n".join([doc.page_content for doc in documents])
        finally:
            os.unlink(tmp_path)
        
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {
            "resume_text": resume_text,
            "job_requirements": job_requirements or ""
        }
        
        result = workflow_app.invoke(inputs, config)
        
        return AnalysisResult(
            status="success",
            data=result,
            message="简历分析完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@api_app.post("/analyze/text", response_model=AnalysisResult)
async def analyze_text(request: ResumeTextRequest):
    try:
        if not request.resume_text.strip():
            raise HTTPException(status_code=400, detail="简历内容不能为空")
        
        config = {"configurable": {"thread_id": request.thread_id}}
        inputs = {
            "resume_text": request.resume_text,
            "job_requirements": request.job_requirements or ""
        }
        
        result = workflow_app.invoke(inputs, config)
        
        return AnalysisResult(
            status="success",
            data=result,
            message="简历分析完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@api_app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "resume-analysis-api"}


if __name__ == "__main__":
    uvicorn.run(api_app, host="0.0.0.0", port=8000)
