# appointments/services.py
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def extract_resume_info(file_path):
    # Load PDF
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    resume_text = "\n".join([page.page_content for page in pages])
    
    # Set up LLM with OpenRouter
    llm = ChatOpenAI(
        model_name="mistralai/mistral-7b-instruct",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key="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",
        max_tokens=2000,
    )
    
    # Create prompt template
    template = """
    Extract the following information from the resume below. 
    Return ONLY a JSON object with these keys: name, email, phone, skills, education, experience.
    
    Resume:
    {resume_text}
    
    JSON:
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # Create and run chain
    chain = prompt | llm
    result = chain.invoke({"resume_text": resume_text})
    
    return eval(result.content)