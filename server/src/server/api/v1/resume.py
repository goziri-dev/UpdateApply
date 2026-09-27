from fastapi import APIRouter

from server.schemas.tailor_resume_request import TailorResumeRequest
from server.schemas.tailor_resume_response import TailorResumeResponse
from server.schemas.tailored_resume import TailoredResume
from server.services.agent import Task, create_agent
from server.services.resume_html import render_resume_html
from server.services.resume_normalize import normalize_tailored_resume

resume_router = APIRouter(prefix="/resume")

_TAILOR_PROMPT = """\
You rewrite a candidate's CV into a tailored resume for one job posting.

Follow the Headless Headhunter resume rules:
- Past tense everywhere, including current roles.
- Each work/internship role: one summary bullet plus 2-7 What/How/Result bullets (3-8 total).
- Each bullet: roughly one sentence, one period, max ~3 lines; show HOW the keyword was used and the result/reason.
- Pack qualifications from the job into bullets; aim to surface most keywords early.
- Order by relevance to the job, then recency; include at most ~12 years of experience.
- Keep unpaid/volunteer organization roles in work_history (do not move them to projects).
- Job titles: Title Case only (never ALL CAPS). Use a common market title a recruiter would recognize in 15 seconds.
- Prefer a title close to the target job's title when the candidate's duties genuinely match; otherwise pick the nearest standard title for that work (e.g. Customer Service Assistant, Operations Assistant, Quality Assurance Associate).
- Never invent seniority, employers, dates, degrees, or metrics. Renaming the label is allowed; inventing duties is not.
- Do not put (Volunteer), (VOLUNTEER), or similar downgrading tags in the title — leave kind/context in bullets if needed.
- Avoid internal mashup titles (e.g. "Customer & Operations Assistant", "Quality & Customer Experience Evaluator").
- Projects: unpaid personal/academic projects only; no dates; summary plus up to 2 more bullets (3 max total).
- summary field: only for industry change, relocation, or visa/sponsorship; otherwise null.
- Education: keep field/institution/graduation, but degree MUST be abbreviated (B.A., B.S., M.A., M.S., PhD, MBA) — never "Bachelor of Science" / "Master of Arts".
- Preserve certificates and contact fields from the candidate.
- List keywords_used as the job qualifications you actually wove into the resume.

The user message is JSON with "candidate" and "job" objects.
"""


@resume_router.post("/tailor")
async def tailor_resume(body: TailorResumeRequest) -> TailorResumeResponse:
    agent = create_agent(
        Task.TAILOR_RESUME,
        system_prompt=_TAILOR_PROMPT,
        structured_output=TailoredResume,
    )
    prompt = body.model_dump_json(
        include={"candidate", "job"},
    )
    tailored = normalize_tailored_resume(await agent.invoke(prompt))
    html = render_resume_html(tailored, body.style)
    return TailorResumeResponse(resume=tailored, html=html, style=body.style)
