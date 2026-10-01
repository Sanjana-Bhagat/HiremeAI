import json
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
from pypdf import PdfReader


load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client=Groq(api_key=my_api_key)
model = "openai/gpt-oss-20b"

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Experience(BaseModel):
    company:str | None=None
    role: str | None=None
    duration:str | None=None
    description:str | None=None
    skills_used: list[str] | None=None

class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    skills: list[str] | None = None

class Resume(BaseModel):
    name:str 
    email:str | None=None
    phone:str | None=None

    total_experiencce_year:float | None=None

   
    skill:  list[str] 
    experiences: list[Experience] = Field(default_factory=list)
    education:list[str] | None=None
    project:list[str] |None=None
    certification:list[str] | None=None
resume_schema=Resume.model_json_schema()


class ChatRequest(BaseModel):
    question:str

def ask_candidate(question: str, resume: Resume):

    system_prompt = f"""
you are an AI assistent representing a job candidate.

Below is everything you know about the candidate.
{resume.model_dump_json(indent=2)}

Rule:
1. Answer only using this information.
2. Never hallucinate.
3. If information is unavailable,
say
"I dont have enough information to answer that."
4. Be Professional.
5. Answer as if HR is interviewing this candidate.
"""

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        stream=True
    )

    answer = ""

    for chunk in stream:

        content = chunk.choices[0].delta.content

        if content:
            print(content, end="", flush=True)
            answer += content

    return answer
#parsing resume 
def parse_resume(resume_text):
    system_prompt = f"""
    You are an expert resume parser.

    Extract information from the resume based on its meaning,
    not only based on exact section headings.

    Different resumes may use different headings.

    For example:
    - Experience
    - Professional Experience
    - Work History
    - Employment
    - Internships

    These may all contain relevant experience.

    Skills may also appear in the skills section, work experience,
    internships or projects.

    Return ONLY valid JSON matching this schema:

    {resume_schema}

    Important rules:

    1. Do not invent information.
    2. If a value is not available, return null.
    3. If a list has no information, return an empty list.
    4. Include internships inside experiences.
    5. Extract skills mentioned across the entire resume.
    6. Keep each experience description to one concise sentence.
    7. Return only the most relevant 5 experiences, 10 skills, and 5 projects.
    """
    user_prompt = f"""
    Parse the following resume:

    {resume_text}
    """
    message_system={
        "role" : "system",
        "content" : system_prompt
    }
    message_user={
        "role" : "user",
        "content" : user_prompt
    }
    messages=[message_system, message_user]
    response_format={
        "type": "json_object"
    }
    response=client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format,
        max_completion_tokens=4096,
        reasoning_effort="low",
    )
    raw_output = response.choices[0].message.content
    data = json.loads(raw_output)
    resume = Resume(**data)
    return resume

#pfd extraction 
def read_pdf(file_path: Path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


@app.get("/")
 

def home():
    resume_txt=read_pdf(Path("my_resume.pdf"))
    resume=parse_resume(resume_txt)
    print(resume.model_dump_json(indent=2))
    print(resume_txt)
    return {
        "message":" ye home page h ..!"
    }

#youtube.com
#youtube.com /padho with pratyush 
#youtube.com /padho with pratyush/videos
#youtube.com /padho with pratyush/videos/playlists
#chat 
@app.post("/chat")
def chat(request:ChatRequest):
    resume_txt=read_pdf(Path("my_resume.pdf"))
    resume=parse_resume(resume_txt)
    answer=ask_candidate(request.question,resume)
    return{
"answer":answer

    }




