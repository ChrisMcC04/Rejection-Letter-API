from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from llama_cpp import Llama
import json

app = FastAPI(title="MOD Rejection Letter API")

# --- 1. PYDANTIC MODELS ---
class FeedbackRow(BaseModel):
    score: str = Field(default="Unknown")
    justification: str

class FailedProjectData(BaseModel):
    project_name: str
    domain: str
    ai_feedback_points: List[FeedbackRow]

class RejectionResponse(BaseModel):
    status: str
    project_name: str
    email_text: str
    full_dfs_text: str

# --- 2. THE TEMPLATES (Easy for future staff to edit) ---
# Notice the {placeholders} where Python will inject the AI's thoughts.
EMAIL_TEMPLATE = """Subject Line: Exploitation Engine Results
 
Dear Project Lead,

This email concerns your application to the Research and Development (R&D) Exploitation Engine (ExE). Thank you for your interest and engagement in the current cycle of R&D Exploitation Engine activity. We have now completed the first stage of our assessment process and are writing to inform you of its outcomes.

Unfortunately, we must inform you that your project, {project_name}, has been unsuccessful in its application and will not advance beyond this stage.  

We value the time and work you put into preparing your application and we are dedicated to keeping our review procedure open and honest. We have therefore compiled a Digestible Feedback Summary (DFS) sheet of our assessment. Please view the Ratings Definitions document that is attached for more information.
 
1. Project Definition/ Purpose: {email_def}
2. Project Benefits: {email_ben}
3. Tech Maturity: {email_tech}
4. Delivery Challenges: {email_del}
 
Thank you once again for your engagement. We hope this helps in taking your project forward.
 
Yours sincerely,
The Exploitation Engine Team
"""

DFS_TEMPLATE = """Digestible Feedback Summary (DFS)
Project: {project_name}

1. Project Definition / Purpose
{dfs_def_bullets}

2. Project Benefits
{dfs_ben_bullets}

3. Tech Maturity
{dfs_tech_bullets}

4. Delivery Challenges
{dfs_del_bullets}
"""

print("Loading Llama 3 Model...")
llm = Llama(model_path="./Llama-3.2-3B-Instruct-Q4_K_M.gguf", n_ctx=2048) 
print("Model Loaded Successfully.")

@app.post("/generate-rejection", response_model=RejectionResponse)
async def generate_rejection(data: FailedProjectData):
    
    formatted_justifications = "\n".join(
        [f"- Score: {item.score} | Justification: {item.justification}" for item in data.ai_feedback_points]
    )

    # --- 3. THE ANALYTICAL PROMPT ---
    # The AI now only does the thinking, not the formatting.
# --- 3. THE ANALYTICAL PROMPT ---
    system_instructions = """
You are a Senior Technical Assessor for the UK Ministry of Defence (MOD).
Analyse the raw assessor notes and evaluate the project across four criteria.
You MUST output a strict JSON object containing exactly 8 keys. Do not add markdown or conversational text.

JSON STRUCTURE REQUIRED:
{
  "email_def": "[1-sentence summary starting with the rating, e.g., 'Limited: The aim is present but lacks relevance.']",
  "email_ben": "[1-sentence summary starting with the rating]",
  "email_tech": "[1-sentence summary starting with the rating]",
  "email_del": "[1-sentence summary starting with the rating]",
  "dfs_def_bullets": ["First explanatory sentence without bullet points.", "Second explanatory sentence."],
  "dfs_ben_bullets": ["First explanatory sentence.", "Second explanatory sentence."],
  "dfs_tech_bullets": ["First explanatory sentence.", "Second explanatory sentence."],
  "dfs_del_bullets": ["First explanatory sentence.", "Second explanatory sentence."]
}

SCORING DEFINITIONS:
- Project Definition: (Insufficient: Problem not well-defined. Limited: Aim present but lacks necessity. Adequate: Reasonable outline. Strong: Well-defined goal, clear defence need).
- Project Benefits: (Insufficient: Ambiguous. Limited: Identified but lacks evidence. Adequate: Reasonable benefits. Strong: Quantifiable, well-supported advantages).
- Tech Maturity: (Insufficient: Early concept. Limited: Early TRL, needs investigation. Adequate: Moderate maturity, needs testing. Strong: Ready for integration in 2 years).
- Delivery Challenges: (Insufficient: No Capability Sponsor. Limited: Lacks detail on risks. Adequate: Plan given but governance needs improvement. Strong: Well-defined milestones).
"""

    final_prompt = (
        f"SYSTEM: {system_instructions}\n\n"
        f"PROJECT NAME: {data.project_name}\n\n"
        f"RAW AI FEEDBACK DATA:\n{formatted_justifications}\n\n"
        f"OUTPUT FORMAT:\n"
        f"Return ONLY a raw JSON object. Do not add markdown backticks.\n\n"
        f"{{\n" 
    )

    try:
        response = llm(
            final_prompt, 
            max_tokens=1000, 
            stop=["\n\n\n"], 
            echo=False
        )
        
        # The Prefill Trick: Adding the bracket back
        ai_generated_text = "{\n" + response['choices'][0]['text'].strip()
        
        # Strip markdown if the AI stubbornly adds it at the end
        if ai_generated_text.endswith("```"):
            ai_generated_text = ai_generated_text[:-3].strip()
            
        try:
            parsed_json = json.loads(ai_generated_text)
        except json.JSONDecodeError:
            print(f"JSON Parse Error. Raw output was: {ai_generated_text}")
            parsed_json = {} # Provide empty dict to prevent total crash

# --- 4. PYTHON STITCHES THE TEMPLATE ---
        # Helper function to safely turn the JSON lists into bulleted text
        def format_bullets(item_list):
            if isinstance(item_list, list):
                return "\n".join([f"- {item}" for item in item_list])
            return f"- {item_list}" # Fallback if it outputs a string instead of a list

        final_email = EMAIL_TEMPLATE.format(
            project_name=data.project_name,
            email_def=parsed_json.get("email_def", "Error generating summary."),
            email_ben=parsed_json.get("email_ben", "Error generating summary."),
            email_tech=parsed_json.get("email_tech", "Error generating summary."),
            email_del=parsed_json.get("email_del", "Error generating summary.")
        )
        
        final_dfs = DFS_TEMPLATE.format(
            project_name=data.project_name,
            dfs_def_bullets=format_bullets(parsed_json.get("dfs_def_bullets", ["Data missing"])),
            dfs_ben_bullets=format_bullets(parsed_json.get("dfs_ben_bullets", ["Data missing"])),
            dfs_tech_bullets=format_bullets(parsed_json.get("dfs_tech_bullets", ["Data missing"])),
            dfs_del_bullets=format_bullets(parsed_json.get("dfs_del_bullets", ["Data missing"]))
        )
        
        return RejectionResponse(
            status="Success",
            project_name=data.project_name,
            email_text=final_email,
            full_dfs_text=final_dfs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))