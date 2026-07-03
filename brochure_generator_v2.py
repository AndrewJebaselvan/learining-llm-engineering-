


import time
from urllib.parse import urljoin

from openai import OpenAI
from scraper import fetch_website_links, fetch_website_contents


MODEL = "qwen3:4b"
BASE_URL = "http://localhost:11434/v1"
MAX_LINKS = 10
MAX_CONTEXT = 3500

client = OpenAI(
    base_url=BASE_URL,
    api_key="ollama"
)

brochure_system_prompt = """
You are an expert technical marketing writer.

Create a professional brochure in Markdown.

Only use the supplied webpage information.

Include, when available:

# Company Overview
# Products & Services
# Industries Served
# Why Choose Us
# Careers
# Contact

Never invent facts.
If information is unavailable, omit that section.
"""

KEYWORDS = [
    "about",
    "company",
    "service",
    "services",
    "solution",
    "solutions",
    "product",
    "products",
    "career",
    "careers",
    "team",
    "contact",
    "project",
    "projects"
]


def select_relevant_links(url):
    print("\nDownloading homepage links...")

    links = fetch_website_links(url)

    links = list(dict.fromkeys(links))

    useful = []

    for link in links:

        if not link:
            continue

        lower = link.lower()

        if lower.startswith("mailto:"):
            continue

        if lower.startswith("javascript"):
            continue

        if lower.startswith("#"):
            continue

        full = urljoin(url, link)

        if any(k in full.lower() for k in KEYWORDS):
            useful.append(full)

    useful = list(dict.fromkeys(useful))

    print(f"Found {len(links)} links")
    print(f"Keeping {min(len(useful), MAX_LINKS)} useful links")

    return useful[:MAX_LINKS]


def fetch_company_information(url):

    text = "# LANDING PAGE\n\n"
    text += fetch_website_contents(url)
    text += "\n\n"

    pages = select_relevant_links(url)

    for page in pages:
        try:
            print(f"Fetching {page}")

            content = fetch_website_contents(page)

            if len(content) > 100:
                text += "\n\n"
                text += "=" * 70
                text += "\n"
                text += page
                text += "\n"
                text += "=" * 70
                text += "\n\n"
                text += content

        except Exception as e:
            print(f"Skipping {page}")
            print(e)

    return text[:MAX_CONTEXT]


def generate_brochure(company, url, stream=True):

    prompt = f"""
Create a professional brochure for:

Company:
{company}

Website information:

{fetch_company_information(url)}
"""

    if stream:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": brochure_system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        print("\nGenerating brochure...\n")

        full_text = ""

        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            full_text += delta

        print()

        return full_text

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": brochure_system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def main():

    print("=" * 50)
    print(" LOCAL OLLAMA BROCHURE GENERATOR V2 ")
    print("=" * 50)

    company = input("Company Name : ").strip()
    url = input("Website URL  : ").strip()

    stream = input("Stream output? (y/n): ").lower().startswith("y")

    start = time.time()

    brochure = generate_brochure(company, url, stream)

    with open("brochure.md", "w", encoding="utf-8") as f:
        f.write(brochure)

    elapsed = time.time() - start

    print("\nSaved as brochure.md")
    print(f"Finished in {elapsed:.1f} seconds")


if __name__ == "__main__":
    main()
