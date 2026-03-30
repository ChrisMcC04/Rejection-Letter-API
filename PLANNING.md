# Project Tranches (Action Plan)

## Tranche 1: Core Infrastructure [COMPLETED]
- [x] Set up Python virtual environment.
- [x] Configure Git and `.gitignore`.
- [x] Push baseline code to GitHub.

## Tranche 2: The API Engine [COMPLETED]
- [x] Build FastAPI routing.
- [x] Integrate local Llama 3 engine via `llama-cpp-python`.
- [x] Write Dockerfile, compile C++ tools, and run container.

## Tranche 3: Prompt Engineering [IN PROGRESS]
- [x] Establish "System Persona" for British English and MOD tone.
- [ ] Sanitise human-written rejection templates.
- [ ] Implement "Few-Shot" handrail logic based on project domain.

## Tranche 4: Data Standardisation [UP NEXT]
- [ ] Update Pydantic models to accept external JSON scoring data.
- [ ] Force the AI to output structured JSON instead of a conversational chat.

## Tranche 5: Testing & Handover
- [ ] End-to-end payload test.
- [ ] Finalise API documentation for the deployment team.

## Appendix: Thought Experiments & Future State Testing

### The Manager's Comparative Report (A/B Testing Matrix)
To satisfy management reporting, the API's output quality will be evaluated through three distinct testing phases:
1. **Phase 1 (The Baseline):** Feed the API with *AI-generated* scoring justifications. Compare the resulting AI Rejection Letter against the historical Human Rejection Letter.
2. **Phase 2 (The Variable Isolation):** Feed the API with *Human-generated* scoring justifications. Does the AI produce a better letter when the input data is of a higher standard?
3. **Phase 3 (The Semantic Correction):** If the AI letter is structurally sound but lacks the specific "MOD flavour" the human team prefers, introduce the historical Human Rejection Letter into the API's system prompt as an 'ideal' template (Few-Shot Prompting) to force stylistic consistency.

### System Resilience
- **Data Agnosticism:** The API is designed to accept messy legacy data (e.g., ai schema dumps with unpredictable ID columns) by isolating and extracting only the `justification` field, ignoring all other variables to prevent runtime crashes.


## Future Roadmap / Frontend

Template Modularity: All email and DFS templates must be stored as separate text variables/files, completely isolated from the AI prompt. This allows non-technical staff to update the wording without touching the AI logic.

Tone Segmentation (Audience Tailoring): Develop a toggle system for the final UI. Users can select "Direct/Data-Focused" (STEM audience) or "Empathetic/Softer" (Standard audience). The backend will route the request to the corresponding system_instructions prompt.

Meeting Value-Add: The generated DFS is not just a send-off document; it is designed to be a visual aid for internal meetings to quickly highlight exact project failure points.