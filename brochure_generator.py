"""
Local Ollama Brochure Generator
Converted from Ed Donner notebook.
Requires:
pip install openai requests beautifulsoup4
ollama serve
"""

import json
from openai import OpenAI
from scraper import fetch_website_links, fetch_website_contents

MODEL="qwen3:4b"

client=OpenAI(base_url="http://localhost:11434/v1",api_key="ollama")

link_system_prompt="""
You are provided with a list of links found on a webpage.
Choose the links most useful for a company brochure.
Return JSON:
{"links":[{"type":"about","url":"https://..."}]}
"""

brochure_system_prompt="""
You analyze company webpages and create a concise markdown brochure for customers, investors and recruits.
Include company overview, products, culture and careers when available.
Return markdown only.
"""

def get_links_user_prompt(url:str)->str:
    links=fetch_website_links(url)
    return f"""Website: {url}

Choose only useful links (About, Company, Careers, Products, Blog if relevant).
Ignore privacy, terms, login, mailto.

Links:
{chr(10).join(links)}
"""

def select_relevant_links(url):
    print(f"Selecting relevant links from {url}...")
    r=client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system","content":link_system_prompt},
            {"role":"user","content":get_links_user_prompt(url)}
        ],
        response_format={"type":"json_object"}
    )
    return json.loads(r.choices[0].message.content)

def fetch_page_and_all_relevant_links(url):
    text="## Landing Page\n\n"+fetch_website_contents(url)+"\n\n"
    links=select_relevant_links(url)
    text+="## Relevant Pages\n"
    for link in links["links"]:
        print("Fetching:",link["url"])
        text+=f"\n### {link['type']}\n"
        text+=fetch_website_contents(link["url"])+"\n"
    return text

def get_brochure_user_prompt(company,url):
    prompt=f"You are creating a brochure for {company}.\n\n"
    prompt+=fetch_page_and_all_relevant_links(url)
    return prompt[:5000]

def create_brochure(company,url):
    r=client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system","content":brochure_system_prompt},
            {"role":"user","content":get_brochure_user_prompt(company,url)}
        ]
    )
    return r.choices[0].message.content

def stream_brochure(company,url):
    stream=client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system","content":brochure_system_prompt},
            {"role":"user","content":get_brochure_user_prompt(company,url)}
        ],
        stream=True
    )
    print("\nGenerating brochure...\n")
    for chunk in stream:
        delta=chunk.choices[0].delta.content or ""
        print(delta,end="",flush=True)
    print()

def main():
    print("=== Local Ollama Brochure Generator ===")
    company=input("Company name: ").strip()
    url=input("Website URL: ").strip()
    mode=input("Stream output? (y/n): ").lower()
    if mode=="y":
        stream_brochure(company,url)
    else:
        print(create_brochure(company,url))

if __name__=="__main__":
    main()
