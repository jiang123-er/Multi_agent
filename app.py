"""
    简历分析系统 - Streamlit 界面
"""
import streamlit as st
import tempfile
import os
from core.workflow import app as workflow_app
from util.file_handler import pdf_loader

st.set_page_config(page_title="简历分析系统", page_icon="📄", layout="wide")

st.title("简历分析系统")

with st.sidebar:
    st.header("设置")
    job_requirements = st.text_input(
        "目标岗位",
        value="",
        placeholder="留空则自动推断"
    )
    thread_id = st.text_input(
        "用户ID",
        value="default_user"
    )
    
    st.markdown("---")
    st.header("上传简历")
    
    uploaded_file = st.file_uploader(
        "拖拽或点击上传PDF简历",
        type=["pdf"],
        help="支持PDF格式"
    )
    
    st.markdown("**或者手动输入：**")
    resume_text_input = st.text_area(
        "简历内容",
        height=200,
        placeholder="请粘贴简历内容...",
        label_visibility="collapsed"
    )

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if "analyzing" not in st.session_state:
        st.session_state["analyzing"] = False
    if "stop_requested" not in st.session_state:
        st.session_state["stop_requested"] = False
    
    resume_text = resume_text_input
    
    if st.session_state.get("analyzing"):
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            stop_clicked = st.button("停止分析", type="secondary", use_container_width=True)
            if stop_clicked:
                st.session_state["stop_requested"] = True
                st.session_state["analyzing"] = False
                st.warning("分析已停止")
                st.rerun()
    else:
        if st.button("开始分析", type="primary", use_container_width=True):
            st.session_state["analyzing"] = True
            st.session_state["stop_requested"] = False
            
            if uploaded_file is not None:
                with st.spinner("读取PDF中..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        documents = pdf_loader(tmp_path)
                        os.unlink(tmp_path)
                        
                        if documents:
                            resume_text = "\n".join([doc.page_content for doc in documents])
                        else:
                            st.error("PDF读取失败，请检查文件")
                    except Exception as e:
                        st.error(f"PDF读取错误: {str(e)}")
            
            if not resume_text.strip():
                st.error("请上传PDF或输入简历内容！")
                st.session_state["analyzing"] = False
            else:
                with st.spinner("分析中，请稍候..."):
                    try:
                        if st.session_state.get("stop_requested"):
                            st.info("分析已停止")
                            st.session_state["analyzing"] = False
                            st.session_state["stop_requested"] = False
                            st.rerun()
                        
                        config = {"configurable": {"thread_id": thread_id}}
                        
                        inputs = {"resume_text": resume_text}
                        if job_requirements:
                            inputs["job_requirements"] = job_requirements
                        
                        result = workflow_app.invoke(inputs, config)
                        
                        if st.session_state.get("stop_requested"):
                            st.info("分析已停止")
                            st.session_state["analyzing"] = False
                            st.session_state["stop_requested"] = False
                            st.rerun()
                        
                        st.markdown("### 解析结果")
                        parsed = result.get("parsed_info", {})
                        if "error" in parsed or "raw_text" in parsed:
                            st.warning("解析失败，显示原始内容")
                            with st.expander("查看原始内容", expanded=False):
                                st.text(parsed.get("raw_text", "")[:1000])
                        else:
                            with st.expander("查看详细信息", expanded=True):
                                st.json(parsed)
                        
                        st.markdown("---")
                        
                        st.markdown("### 评分结果")
                        final_score = result.get("final_score") or result.get("initial_score", {})
                        if "error" in final_score or "raw_text" in final_score:
                            st.warning("评分失败")
                            with st.expander("查看原始内容", expanded=False):
                                st.text(final_score.get("raw_text", "")[:500])
                        else:
                            score_data = final_score.get("score", {})
                            if score_data:
                                cols = st.columns(5)
                                metrics = [
                                    ("教育背景", "education"),
                                    ("技能匹配度", "skill_match"),
                                    ("工作经验", "work_experience"),
                                    ("项目质量", "project_quality"),
                                    ("整体印象", "overall_impression")
                                ]
                                for i, (label, key) in enumerate(metrics):
                                    cols[i].metric(label, f"{score_data.get(key, 0)}分")
                                st.metric("总分", f"{score_data.get('total', 0)}分")
                            
                            suggestions = final_score.get("suggestions", [])
                            if suggestions:
                                with st.expander("优化建议", expanded=True):
                                    for s in suggestions:
                                        st.write(f"- {s}")
                            
                            summary = final_score.get("summary", "")
                            if summary:
                                st.info(f"**总结**: {summary}")
                        
                        st.markdown("---")
                        
                        st.markdown("### 验证结果")
                        verify = result.get("verify_result", {})
                        if "error" in verify or "raw_text" in verify:
                            with st.expander("查看原始内容", expanded=False):
                                st.text(verify.get("raw_text", "")[:500])
                        else:
                            is_valid = verify.get("is_valid", True)
                            risk = verify.get("risk_level", "低")
                            
                            if is_valid:
                                st.success(f"简历有效 | 风险等级：{risk}")
                            else:
                                st.error(f"发现问题 | 风险等级：{risk}")
                            
                            issues = verify.get("issues", [])
                            if issues:
                                with st.expander("发现的问题", expanded=True):
                                    for issue in issues:
                                        st.warning(f"**{issue.get('type', '')}**: {issue.get('description', '')}")
                                        if issue.get('evidence'):
                                            st.caption(f"证据：{issue.get('evidence')}")
                        
                        st.markdown("---")
                        
                        st.markdown("### 面试题")
                        questions = result.get("interview_questions", {})
                        if isinstance(questions, dict):
                            if "error" in questions:
                                st.warning("面试题生成失败")
                                with st.expander("查看原始内容", expanded=False):
                                    st.text(questions.get("raw_text", "")[:500])
                            else:
                                with st.expander("查看面试题", expanded=True):
                                    tech_q = questions.get("technical_questions", [])
                                    if tech_q:
                                        st.markdown("**技术技能题**")
                                        for q in tech_q:
                                            st.markdown(f"- [{q.get('category', '')}] {q.get('question', '')}")
                                            st.caption(f"追问：{q.get('follow_up', '')}")
                                    
                                    proj_q = questions.get("project_questions", [])
                                    if proj_q:
                                        st.markdown("**项目经验题**")
                                        for q in proj_q:
                                            st.markdown(f"- [{q.get('category', '')}] {q.get('question', '')}")
                                            st.caption(f"追问：{q.get('follow_up', '')}")
                                    
                                    behav_q = questions.get("behavioral_questions", [])
                                    if behav_q:
                                        st.markdown("**行为面试题**")
                                        for q in behav_q:
                                            st.markdown(f"- [{q.get('category', '')}] {q.get('question', '')}")
                                            st.caption(f"追问：{q.get('follow_up', '')}")
                                    
                                    verify_q = questions.get("verification_questions", [])
                                    if verify_q:
                                        st.markdown("**验证疑点题**")
                                        for q in verify_q:
                                            st.markdown(f"- [{q.get('target_issue', '')}] {q.get('question', '')}")
                                            st.caption(f"期望回答：{q.get('expected_answer', '')}")
                                    
                                    tips = questions.get("interview_tips", [])
                                    if tips:
                                        st.markdown("**面试官提示**")
                                        for tip in tips:
                                            st.info(tip)
                        elif isinstance(questions, str):
                            with st.expander("查看面试题", expanded=True):
                                st.markdown(questions)
                        else:
                            st.info("暂无面试题")
                            
                    except Exception as e:
                        import traceback
                        st.error(f"分析失败: {str(e)}")
                        with st.expander("查看错误详情"):
                            st.code(traceback.format_exc())
                
                st.session_state["analyzing"] = False
                st.session_state["stop_requested"] = False
    
    st.markdown("---")
