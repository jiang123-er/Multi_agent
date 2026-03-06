# 多智能体简历评测系统

基于 LangGraph 实现的多智能体协作系统，用于简历解析、评分、真实性验证和面试题生成。

## 功能特性

- 🤖 **多智能体架构**：ParserAgent、5个评分Agent、ScoreAgent、VerifyAgent、InterviewAgent 协作
- ⚡ **并行评分**：5个评分Agent并行执行，性能提升约60%
- 📊 **智能评分**：100分制评分，涵盖教育背景、技能匹配度、工作经验、项目质量、整体印象
- 🔍 **真实性验证**：检测技能夸大、时间线问题、描述模糊等风险
- 📝 **面试题生成**：基于简历内容生成针对性面试题
- 🧠 **RAG 增强**：支持向量检索，生成更精准的面试题
- 🚀 **FastAPI 接口**：提供 RESTful API，支持 PDF 和文本输入

## 性能对比

| 版本 | 评分阶段耗时 | 总耗时 | 提升 |
|------|-------------|--------|------|
| 旧版（串行评分） | ~32秒 | ~3分44秒 | - |
| 新版（并行评分） | ~16秒 | ~1分55秒 | **约48%** |

> 使用 LangGraph 的 `Send` 实现 fan-out 并行，5个评分Agent同时执行

## 技术栈

- **核心框架**：Python + LangGraph
- **向量数据库**：ChromaDB
- **Web 框架**：FastAPI
- **模型**：NVIDIA NIM (GLM-4.7) / Ollama
- **PDF 处理**：PyPDF2

## 快速开始

### 1. 环境要求

- Python 3.10+
- NVIDIA API Key 或 Ollama 本地模型

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

**方式1：系统环境变量（推荐）**

```powershell
# Windows
[Environment]::SetEnvironmentVariable("NVIDIA_API_KEY", "nvapi-你的密钥", "User")
```

**方式2：.env 文件**

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

**方式3：配置文件**

```bash
cp config/rag.example.yml config/rag.yml
# 编辑 config/rag.yml，填入你的配置
```

### 4. 启动服务

```bash
python api.py
```

访问 http://localhost:8000/docs 查看 API 文档

### 5. 使用示例

**分析 PDF 简历**

```bash
curl -X POST "http://localhost:8000/analyze/pdf" \
  -F "file=@resume.pdf" \
  -F "job_requirements=Python后端开发"
```

**分析文本简历**

```bash
curl -X POST "http://localhost:8000/analyze/text" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "姓名：张三...",
    "job_requirements": "Python后端开发"
  }'
```

## 项目结构

```
Multi_agent/
├── api.py                 # FastAPI 主应用
├── app.py                 # Streamlit 界面
├── config/                # 配置文件
│   ├── chroma.yml         # ChromaDB 配置
│   ├── prompts.yml        # 提示词配置
│   └── rag.yml           # RAG 配置
├── core/                  # 核心模块
│   ├── agents.py          # 智能体实现
│   └── workflow.py        # LangGraph 工作流编排
├── data/                  # 数据目录
│   ├── knowledge/         # 知识库文档
│   └── resumes/           # 示例简历
├── model/                 # 模型工厂
│   └── factory.py        # 模型实例化
├── prompts/               # 提示词模板
│   ├── score/             # 各维度评分提示词
│   │   ├── education.txt
│   │   ├── skill_match.txt
│   │   ├── experience.txt
│   │   ├── project.txt
│   │   └── overall.txt
│   ├── parse_prompt.txt
│   ├── scoer_prompt.txt   # 评分汇总
│   ├── verify_prompt.txt
│   └── interview_prompt.txt
├── rag/                   # RAG 模块
│   └── retriever.py      # 向量检索
├── util/                  # 工具模块
│   ├── config_handler.py  # 配置加载
│   ├── file_handler.py    # 文件处理
│   ├── logger_handler.py  # 日志处理
│   ├── path_tool.py       # 路径工具
│   └── prompt_loader.py   # 提示词加载
└── requirements.txt       # 依赖列表
```

## 工作流程

```
START → ParserAgent 解析简历
          ↓
       5个Agent并行评分（EducationAgent、SkillMatchAgent、ExperienceAgent、ProjectAgent、OverallAgent）
          ↓
       ScoreAgent 汇总分数
          ↓
       VerifyAgent 验证真实性
          ↓
    ┌─────────────────────────────┐
    │ 有问题                      │ 无问题
    ↓                             ↓
5个Agent并行复评              InterviewAgent 生成面试题
    ↓                             ↓
ScoreAgent 复评汇总            END
    ↓
InterviewAgent 生成面试题
    ↓
   END
```

## API 文档

启动服务后访问 http://localhost:8000/docs

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/analyze/pdf` | POST | 分析 PDF 简历 |
| `/analyze/text` | POST | 分析文本简历 |
| `/health` | GET | 健康检查 |

## 配置说明

### 模型配置

**使用 NVIDIA NIM（推荐）**

```yaml
model_type: openai
chat_model_name: meta/llama3-70b-instruct
embedding_model_name: nvidia/nv-embedqa-e5-v5
base_url: https://integrate.api.nvidia.com/v1
```

**使用 Ollama 本地模型**

```yaml
model_type: ollama
chat_model_name: qwen2.5:7b
embedding_model_name: qwen3-embedding:0.6b
```

### 获取 NVIDIA API Key

访问 https://build.nvidia.com/ 注册并获取 API Key

## 常见问题

**Q: 评分不准确？**  
A: 调整 `prompts/score/` 目录下各维度评分提示词

**Q: 面试题不相关？**  
A: 检查 `data/knowledge/` 目录下的知识库文档是否完整

**Q: 如何添加新的岗位知识？**  
A: 在 `data/knowledge/` 添加对应的 txt 文件，系统会自动加载

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- GitHub Issues: https://github.com/你的用户名/multi-agent-resume-analysis/issues
