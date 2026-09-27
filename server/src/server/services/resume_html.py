from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from server.schemas.tailored_resume import ResumeStyle, TailoredResume
from server.services.resume_normalize import education_status_label

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "resume"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)
_env.filters["edu_status"] = education_status_label


def render_resume_html(resume: TailoredResume, style: ResumeStyle) -> str:
    """Fill the HTML template for the given style with tailored resume data."""
    template = _env.get_template(f"{style.value}.html")
    return template.render(resume=resume, style=style.value)
