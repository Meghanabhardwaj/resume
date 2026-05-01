#!/usr/bin/env python3

import json
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "resume.yaml"
SECTIONS_DIR = ROOT / "sections"
GENERATED_DIR = ROOT / "generated"


def load_resume_data() -> dict:
    if shutil.which("yq") is None:
        raise RuntimeError("yq is required to parse resume.yaml. Install yq and rerun make generate.")

    result = subprocess.run(
        ["yq", "-o=json", str(SOURCE)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_git(args: list[str]) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def source_last_modified() -> str:
    diff_exit = subprocess.run(
        ["git", "diff", "--quiet", "--", str(SOURCE.name)],
        cwd=ROOT,
        check=False,
    ).returncode
    if diff_exit == 1:
        return date.today().isoformat()

    commit_date = run_git(["log", "-1", "--format=%cs", "--", SOURCE.name])
    if commit_date:
        return commit_date

    return date.today().isoformat()


def tex_escape(value: str) -> str:
    replacements = OrderedDict(
        [
            ("\\", r"\textbackslash{}"),
            ("&", r"\&"),
            ("%", r"\%"),
            ("$", r"\$"),
            ("#", r"\#"),
            ("_", r"\_"),
            ("{", r"\{"),
            ("}", r"\}"),
            ("~", r"\textasciitilde{}"),
            ("^", r"\textasciicircum{}"),
        ]
    )
    escaped = value
    for old, new in replacements.items():
        escaped = escaped.replace(old, new)
    return escaped


INLINE_TOKEN_RE = re.compile(
    r"(\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|_([^_]+)_)"
)


def render_inline_markup(value: str) -> str:
    parts: list[str] = []
    cursor = 0
    for match in INLINE_TOKEN_RE.finditer(value):
        start, end = match.span()
        if start > cursor:
            parts.append(tex_escape(value[cursor:start]))

        link_label = match.group(2)
        link_url = match.group(3)
        bold_text = match.group(4)
        italic_text = match.group(5)

        if link_label is not None and link_url is not None:
            parts.append(rf"\projectlink{{{link_url}}}{{{tex_escape(link_label)}}}")
        elif bold_text is not None:
            parts.append(rf"\textbf{{{tex_escape(bold_text)}}}")
        elif italic_text is not None:
            parts.append(rf"\textit{{{tex_escape(italic_text)}}}")

        cursor = end

    if cursor < len(value):
        parts.append(tex_escape(value[cursor:]))

    return "".join(parts)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_header(data: dict) -> str:
    basics = data["basics"]
    location = tex_escape(basics["location"]["display"])
    email = basics["email"]
    phone = basics["phone"]

    # Current header layout keeps profile links on the same centered line as the
    # primary contact info. This works better for resumes with only one or two links.
    parts = [
        location,
        rf"\href{{mailto:{email}}}{{{tex_escape(email)}}}",
        rf"\href{{{phone['url']}}}{{{tex_escape(phone['display'])}}}",
    ]
    profiles = [
        rf"\href{{{profile['url']}}}{{\color{{RoyalBlue}}{tex_escape(profile['label'])}}}"
        for profile in basics["profiles"]
    ]
    parts.extend(profiles)
    contact = " | ".join(
        [
            part for part in parts if part
        ]
    )

    # Previous split-line behavior kept profile links on a separate centered line.
    # Keep this reference here so switching back is a small edit:
    #
    # contact = " | ".join(
    #     [
    #         location,
    #         rf"\href{{mailto:{email}}}{{{tex_escape(email)}}}",
    #         rf"\href{{{phone['url']}}}{{{tex_escape(phone['display'])}}}",
    #     ]
    # )
    # profiles = " | ".join(
    #     rf"\href{{{profile['url']}}}{{{tex_escape(profile['label'])}}}"
    #     for profile in basics["profiles"]
    # )
    # return "\n".join(
    #     [
    #         "% Generated from resume.yaml. Do not edit directly.",
    #         rf"\resumeName{{{tex_escape(basics['name'])}}}",
    #         rf"\resumeContactLine{{{contact}}}",
    #         rf"\resumeProfileLinks{{{profiles}}}",
    #     ]
    # )

    return "\n".join(
        [
            "% Generated from resume.yaml. Do not edit directly.",
            rf"\resumeName{{{tex_escape(basics['name'])}}}",
            rf"\resumeContactLine{{{contact}}}",
        ]
    )


def render_experience(data: dict) -> str:
    lines = ["% Generated from resume.yaml. Do not edit directly.", r"\resumesection{EXPERIENCE}", ""]
    for item in data["experience"]:
        date_display = f"{item['start_display']} -- {item['end_display']}"
        lines.append(
            rf"\experienceentry{{{tex_escape(item['company'])}}}{{{tex_escape(item['location']['display'])}}}{{{tex_escape(item['position'])}}}{{{tex_escape(date_display)}}}"
        )
        for bullet in item["bullets"]:
            lines.append(f"  \\item {render_inline_markup(bullet)}")
        lines.extend([r"\experienceentryend", ""])
    return "\n".join(lines)


def render_skills(data: dict) -> str:
    skills = data["skills"]
    lines = ["% Generated from resume.yaml. Do not edit directly.", r"\resumesection{SKILLS}"]
    for index, skill in enumerate(skills):
        label = tex_escape(skill["name"])
        keywords = tex_escape(", ".join(skill["keywords"]))
        if index < len(skills) - 1:
            lines.append(rf"\skillline{{{label}}}{{{keywords}}}")
            lines.append(r"\vspace{2pt}")
        else:
            lines.append(rf"\textbf{{{label}:}} {keywords}")
    return "\n".join(lines)


def render_projects(data: dict) -> str:
    lines = ["% Generated from resume.yaml. Do not edit directly.", r"\resumesection{PROJECTS}", ""]
    for item in data["projects"]:
        tech_stack = tex_escape(", ".join(item["keywords"]))
        lines.append(
            rf"\projectentry{{{tex_escape(item['name'])}}}{{{tech_stack}}}{{{item['url']}}}{{{tex_escape(item['link_label'])}}}"
        )
        for bullet in item["bullets"]:
            lines.append(f"  \\item {render_inline_markup(bullet)}")
        lines.extend([r"\projectentryend", ""])
    return "\n".join(lines)


def render_education(data: dict) -> str:
    item = data["education"][0]
    return "\n".join(
        [
            "% Generated from resume.yaml. Do not edit directly.",
            r"\resumesection{EDUCATION}",
            rf"\educationentry{{{tex_escape(item['institution'])}}}{{{tex_escape(item['short_study_type'])} in {tex_escape(item['area'])}}}{{{tex_escape(item['display'])}}}",
        ]
    )


def render_achievements(data: dict) -> str:
    lines = [
        "% Generated from resume.yaml. Do not edit directly.",
        r"\resumesection{ACHIEVEMENTS}",
        r"\begin{itemize}",
    ]
    for item in data["achievements"]:
        lines.append(f"  \\item {render_inline_markup(item)}")
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


def render_metadata(data: dict) -> str:
    basics = data["basics"]
    pdf = data["pdf"]
    meta = data["meta"]
    keywords = ",\n    ".join(tex_escape(keyword) for keyword in pdf["keywords"])
    name = tex_escape(basics["name"])
    address = tex_escape(basics["location"]["pdf_display"])
    license_url = meta["license_url"]
    return "\n".join(
        [
            "% Generated from resume.yaml. Do not edit directly.",
            rf"\newcommand{{\ResumeOwnerName}}{{{name}}}",
            rf"\newcommand{{\ResumeSchemaDescription}}{{Schema.org structured data - {name}}}",
            rf"\newcommand{{\ResumeJsonDescription}}{{JSON Resume - {name}}}",
            "",
            r"\hypersetup{",
            rf"  pdftitle={{{name}}},",
            rf"  pdfauthor={{{name}}},",
            rf"  pdfauthortitle={{{tex_escape(basics['label'])}}},",
            rf"  pdfsubject={{{tex_escape(pdf['subject'])}}},",
            "  pdfkeywords={",
            f"    {keywords}",
            "  },",
            rf"  pdfcreator={{{tex_escape(pdf['creator'])}}},",
            rf"  pdfproducer={{{tex_escape(pdf['producer'])}}},",
            rf"  pdflang={{{pdf['lang']}}},",
            rf"  pdfmetalang={{{pdf['lang']}}},",
            rf"  pdfcontactaddress={{{address}}},",
            rf"  pdfcontactemail={{{basics['email']}}},",
            rf"  pdfcontacturl={{{basics['website']}}},",
            rf"  pdfcopyright={{Copyright \the\year\ {name}. Licensed under Apache-2.0.}},",
            rf"  pdflicenseurl={{{license_url}}},",
            rf"  pdfurl={{{basics['website']}}},",
            rf"  pdfpubtype={{{pdf['pubtype']}}},",
            r"}",
        ]
    )


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def build_resume_json(data: dict, last_modified: str) -> dict:
    basics = data["basics"]
    resume = {
        "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
        "basics": {
            "name": basics["name"],
            "label": basics["label"],
            "email": basics["email"],
            "url": basics["website"],
            "summary": basics["summary"],
            "location": {
                "city": basics["location"]["city"],
                "region": basics["location"]["region"],
                "countryCode": basics["location"]["country_code"],
            },
            "profiles": [
                {
                    "network": profile["network"],
                    "username": profile["username"],
                    "url": profile["url"],
                }
                for profile in basics["profiles"]
                if profile["network"] != "Portfolio"
            ],
        },
        "work": [],
        "education": [],
        "skills": [],
        "projects": [],
        "meta": {
            "canonical": data["meta"]["canonical"],
            "version": data["meta"]["version"],
            "lastModified": last_modified,
        },
    }

    for item in data["experience"]:
        work = {
            "name": item["company"],
            "position": item["position"],
            "startDate": item["start_date"],
            "location": f"{item['location']['city']}, {item['location']['region']}, {item['location']['country']}",
        }
        if item.get("url"):
            work["url"] = item["url"]
        if item.get("end_date"):
            work["endDate"] = item["end_date"]
        resume["work"].append(work)

    for item in data["education"]:
        education = {
            "institution": item["institution"],
            "area": item["area"],
            "studyType": item["study_type"],
            "score": item["score"],
            "startDate": item["start_date"],
            "endDate": item["end_date"],
        }
        if item.get("url"):
            education["url"] = item["url"]
        resume["education"].append(education)

    for item in data["skills"]:
        resume["skills"].append({"name": item["name"], "keywords": item["keywords"]})

    for item in data["projects"]:
        resume["projects"].append(
            {
                "name": item["name"],
                "url": item["url"],
                "roles": item["roles"],
                "keywords": item["keywords"],
            }
        )

    return resume


def build_schema_json(data: dict, last_modified: str) -> dict:
    basics = data["basics"]
    meta = data["meta"]
    schema = data["schema"]
    skills = data["skills"]
    modified_year = last_modified[:4]
    knows_about = unique(
        [keyword for skill in skills for keyword in skill["keywords"]] + schema["additional_knows_about"]
    )

    occupations = []
    for item in data["experience"]:
        occupation = {
            "@type": "Occupation",
            "name": item["position"],
            "alternateName": item["alternate_names"],
            "occupationLocation": {
                "@type": "City",
                "name": item["location"]["city"],
            },
            "hiringOrganization": {
                "@type": "Organization",
                "name": item["company"],
            },
            "startDate": item["start_date"],
        }
        if item.get("url"):
            occupation["hiringOrganization"]["url"] = item["url"]
        if item.get("end_date"):
            occupation["endDate"] = item["end_date"]
        occupations.append(occupation)

    work_examples = [
        {
            "@type": "SoftwareSourceCode",
            "name": item["name"],
            "url": item["url"],
            "programmingLanguage": item["keywords"],
        }
        for item in data["projects"]
    ]

    skill_items = [
        {
            "@type": "ListItem",
            "position": index,
            "name": f"{item['name']}: {', '.join(item['keywords'])}",
        }
        for index, item in enumerate(skills, start=1)
    ]

    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "@id": schema["person_id"],
                "name": basics["name"],
                "jobTitle": basics["label"],
                "email": basics["email"],
                "url": basics["website"],
                "sameAs": [profile["url"] for profile in basics["profiles"]],
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": basics["location"]["city"],
                    "addressRegion": basics["location"]["region"],
                    "addressCountry": basics["location"]["country_code"],
                },
                "alumniOf": {
                    "@type": "CollegeOrUniversity",
                    "name": data["education"][0]["institution"],
                },
                "knowsAbout": knows_about,
                "hasOccupation": occupations,
                "workExample": work_examples,
                "copyrightYear": meta["created_year"],
                "dateCreated": str(meta["created_year"]),
                "dateModified": modified_year,
                "copyrightHolder": {
                    "@type": "Person",
                    "name": basics["name"],
                },
                "license": meta["license_url"],
            },
            {
                "@type": "CreativeWork",
                "@id": schema["resume_id"],
                "name": f"{basics['name']} - Resume",
                "alternateName": [
                    f"{basics['name']} - CV",
                    f"{basics['name']} - Curriculum Vitae",
                ],
                "about": {
                    "@id": schema["person_id"],
                },
                "hasPart": [
                    {
                        "@type": "ItemList",
                        "name": "Work Experience",
                        "alternateName": [
                            "Experience",
                            "Employment History",
                            "Professional Experience",
                            "Career History",
                        ],
                        "itemListElement": [
                            {
                                "@type": "ListItem",
                                "position": index,
                                "name": f"{item['position']} at {item['company']}",
                            }
                            for index, item in enumerate(data["experience"], start=1)
                        ],
                    },
                    {
                        "@type": "ItemList",
                        "name": "Education",
                        "alternateName": [
                            "Academic Background",
                            "Qualifications",
                            "Academic History",
                        ],
                        "itemListElement": [
                            {
                                "@type": "ListItem",
                                "position": 1,
                                "name": f"{data['education'][0]['short_study_type']} {data['education'][0]['area']} - {data['education'][0]['institution']}",
                            }
                        ],
                    },
                    {
                        "@type": "ItemList",
                        "name": "Technical Skills",
                        "alternateName": [
                            "Skills",
                            "Core Competencies",
                            "Technologies",
                            "Tech Stack",
                            "Expertise",
                        ],
                        "itemListElement": skill_items,
                    },
                    {
                        "@type": "ItemList",
                        "name": "Projects",
                        "alternateName": [
                            "Personal Projects",
                            "Portfolio",
                            "Open Source Work",
                            "Side Projects",
                        ],
                        "itemListElement": [
                            {
                                "@type": "ListItem",
                                "position": index,
                                "name": item["name"],
                            }
                            for index, item in enumerate(data["projects"], start=1)
                        ],
                    },
                ],
            },
        ]
    }


def main() -> int:
    data = load_resume_data()
    last_modified = source_last_modified()

    write_file(SECTIONS_DIR / "header.tex", render_header(data))
    write_file(SECTIONS_DIR / "experience.tex", render_experience(data))
    write_file(SECTIONS_DIR / "skills.tex", render_skills(data))
    write_file(SECTIONS_DIR / "projects.tex", render_projects(data))
    write_file(SECTIONS_DIR / "education.tex", render_education(data))
    write_file(SECTIONS_DIR / "achievements.tex", render_achievements(data))
    write_file(GENERATED_DIR / "metadata.tex", render_metadata(data))
    write_file(ROOT / "resume.json", json.dumps(build_resume_json(data, last_modified), indent=2))
    write_file(ROOT / "schema.json", json.dumps(build_schema_json(data, last_modified), indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
