from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from llama_cpp import Llama

# 1. Start the receptionist
app = FastAPI()

# 2. Load the AI brain (This points to the file you downloaded last night)
llm = Llama(model_path="./Llama-3.2-3B-Instruct-Q4_K_M.gguf", n_ctx=2048)

# 3. Define the shape of the incoming data
class FailedProjectData(BaseModel):
    scores: List[str]
    justifications: List[str]

# 4. Create the door to receive the data
@app.post("/generate-rejection")
async def generate_rejection_letter(data: FailedProjectData):
    
    # Combine the bullet points into one text block
    feedback_text = "\n".join(data.justifications)
    
    # Write the instructions for the AI
    prompt = f"Write a professional, polite project rejection letter based on this feedback:\n{feedback_text}\n\nDear Applicant,"
    
    # Send it to the AI to generate a response (up to 300 words)
    output = llm(prompt, max_tokens=300)
    
    # Extract the actual letter from the AI's data output
    generated_letter = output['choices'][0]['text']
    
    # Send the finished letter back to the browser
    return {
        "status": "Success",
        "drafted_letter": "Dear Applicant," + generated_letter
    }