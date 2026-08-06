---
name: paper-reading-workflow
description: "End-to-end paper reading pipeline — acquire and parse PDFs (GROBID), three-pass reading with structured notes, and turn papers into interactive agents for exploration."
metadata:
  openclaw:
    emoji: "🔬"
    category: "tools"
    subcategory: "document"
    keywords: ["paper reading", "PDF parsing", "academic paper", "deep reading", "annotation", "GROBID"]
    source: "wentor-research-plugins"
---

# Paper Parse Guide

Perform structured, dual-mode deep reading of academic papers from PDF files or URLs. Mode A provides a rapid overview suitable for screening during literature reviews. Mode B delivers exhaustive section-by-section analysis for papers central to your research.

## Overview

Reading academic papers efficiently is a core research skill, yet the density and conventions of scholarly writing make it time-consuming. A typical researcher reads dozens of papers per week during a literature review phase, requiring different levels of depth for different papers. Some need only a quick scan to determine relevance; others demand line-by-line scrutiny of methods and results.

This skill implements a dual-mode reading system. Mode A (Survey Mode) extracts key metadata, the main argument, methods summary, and key findings in under two minutes of processing time. Mode B (Deep Analysis Mode) performs exhaustive section-by-section analysis including methodology critique, statistical evaluation, figure interpretation, and connection to broader literature.

Both modes begin by parsing the paper's structure from its PDF or HTML source, extracting clean text with section boundaries, figures, tables, equations, and references. The parsing pipeline handles the common challenges of academic PDFs: two-column layouts, footnotes, headers/footers, embedded equations, and supplementary materials.

## Paper Acquisition and Parsing

### Input Sources

| Source | Method | Notes |
|--------|--------|-------|
| Local PDF | Direct file path | Best quality, no network needed |
| DOI | Resolve via CrossRef/Unpaywall | Auto-fetches open access version |
| arXiv ID | `https://arxiv.org/pdf/{id}` | Always available |
| URL | Direct download | May require institutional access |
| OpenAlex ID | OpenAlex API + OA link | Includes metadata |

### PDF Parsing Pipeline

```python
from pathlib import Path
import fitz  # PyMuPDF

def parse_paper(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    sections = []
    current_section = {"title": "Header", "content": []}

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    text = " ".join(span["text"] for span in line["spans"])
                    font_size = max(span["size"] for span in line["spans"])
                    is_bold = any("Bold" in span["font"] for span in line["spans"])

                    # Detect section headings
                    if font_size > 11 and is_bold:
                        if current_section["content"]:
                            sections.append(current_section)
                        current_section = {"title": text.strip(), "content": []}
                    else:
                        current_section["content"].append(text)

    sections.append(current_section)
    return {
        "title": extract_title(doc),
        "authors": extract_authors(doc),
        "sections": sections,
        "references": extract_references(doc),
        "page_count": len(doc)
    }
```

### GROBID Integration

For higher-quality structural parsing, use GROBID (GeneRation Of BIbliographic Data):

```bash
# Start GROBID server
docker run --rm -p 8070:8070 lfoppiano/grobid:0.8.0

# Parse a paper
curl -X POST "http://localhost:8070/api/processFulltextDocument" \
  -F "input=@paper.pdf" \
  -F "consolidateHeader=1" \
  -F "consolidateCitations=1" \
  -H "Accept: application/xml" \
  -o parsed_paper.xml
```

GROBID returns TEI XML with structured sections, author affiliations, parsed references, and figure/table captions. It handles two-column layouts, footnotes, and complex formatting better than simple text extraction.

## Mode A: Survey Reading

Designed for rapid screening. Produces a structured summary in 5 components:

### 1. Identity Card

```
Title:      [Extracted title]
Authors:    [First author et al., year]
Venue:      [Journal/Conference name]
DOI:        [DOI if available]
Pages:      [Page count]
Type:       [Empirical / Theoretical / Review / Methods]
```

### 2. Core Argument (1-2 sentences)

Extract from abstract + introduction: What is the main claim?

### 3. Methods Snapshot

- Study design (experimental, observational, computational, theoretical)
- Sample/dataset description
- Key techniques or models used

### 4. Key Findings (3-5 bullets)

Extract from results section and abstract.

### 5. Relevance Assessment

- Relevance to current research question: High / Medium / Low
- Methodological quality signal: sample size, controls, statistical rigor
- Recommended action: Deep read / Cite only / Skip

## Mode B: Deep Analysis

Exhaustive section-by-section reading with critical evaluation.

### Introduction Analysis

- What gap in the literature does this paper address?
- What is the stated research question or hypothesis?
- How does the framing position the contribution?

### Literature Review Evaluation

- Which theoretical frameworks are invoked?
- Are there notable omissions in cited literature?
- How does the paper position itself relative to competing approaches?

### Methodology Critique

- Is the methodology appropriate for the research question?
- Sample size and power analysis: reported? adequate?
- Threats to internal and external validity
- Reproducibility: are methods described in sufficient detail?
- Statistical tests: appropriate? assumptions met?

### Results Assessment

- Do the results support the claims?
- Effect sizes: reported? meaningful?
- Confidence intervals vs. p-values
- Figures and tables: do they accurately represent the data?
- Any signs of p-hacking or selective reporting?

### Discussion Evaluation

- Are limitations adequately acknowledged?
- Are alternative explanations considered?
- Do the conclusions follow logically from the results?
- Are implications overstated?

### Reference Network

- Extract all cited works with metadata
- Identify seminal references (cited by many papers in this field)
- Flag self-citations
- Map citation clusters by topic

## Output Formats

### Structured Note (Markdown)

```markdown
## [Paper Title] ([Year])

**Authors**: [Authors]
**Venue**: [Venue]
**DOI**: [DOI]

### Summary
[2-3 sentence summary]

### Key Contributions
1. [Contribution 1]
2. [Contribution 2]

### Methodology
[Methods description]

### Strengths
- [Strength 1]
- [Strength 2]

### Weaknesses
- [Weakness 1]
- [Weakness 2]

### Relevance to My Research
[How this paper connects to your work]

### Key Quotes
> "[Notable quote]" (p. X)

### References to Follow
- [Ref 1]: [Why relevant]
- [Ref 2]: [Why relevant]
```

### BibTeX Entry

Automatically extract or generate a BibTeX entry for the parsed paper, including all available fields (author, title, journal, year, volume, pages, doi).

## Batch Processing

For systematic reviews, process multiple papers in sequence:

```python
papers = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]
summaries = []

for pdf in papers:
    parsed = parse_paper(pdf)
    summary = mode_a_survey(parsed)
    summaries.append(summary)

# Generate comparison matrix
comparison = create_comparison_table(summaries,
    columns=["methods", "sample_size", "key_finding", "relevance"])
```

## References

- GROBID: https://github.com/kermitt2/grobid
- PyMuPDF: https://pymupdf.readthedocs.io
- OpenAlex API: https://api.openalex.org
- Unpaywall API: https://unpaywall.org/products/api
- S. Keshav, "How to Read a Paper" (2007): http://ccr.sigcomm.org/online/files/p83-keshavA.pdf

---

## Three-Pass Reading Method

Systematic workflows for reading, annotating, and extracting insights from academic papers, including AI-assisted summarization and critical analysis techniques.

## The Three-Pass Reading Method

Srinivasan Keshav's three-pass approach provides a structured way to read papers at increasing depth:

### Pass 1: Survey (5-10 minutes)

Read only:
1. Title, abstract, and keywords
2. Introduction (first and last paragraph only)
3. Section headings (all of them)
4. Conclusion
5. Glance at figures and tables (read captions)
6. Check the reference list for familiar papers

After Pass 1, you should know:
- **Category**: Is this an empirical study, theoretical contribution, system paper, survey?
- **Context**: What related work does it build on?
- **Correctness**: Do the assumptions and claims seem reasonable?
- **Contributions**: What are the main claimed contributions?
- **Clarity**: Is the paper well-written?

**Decision**: Stop here if the paper is not relevant, or continue to Pass 2.

### Pass 2: Comprehension (30-60 minutes)

Read the full paper, but skip proofs and complex derivations:
1. Examine figures and tables carefully
2. Mark unread references for later
3. Annotate key claims, methods, and results
4. Try to summarize each section in one sentence

After Pass 2, you should be able to:
- Summarize the paper's main contribution to someone else
- Identify the key evidence supporting the claims
- List the paper's strengths and weaknesses

### Pass 3: Recreation (1-4 hours)

For papers you need to deeply understand:
1. Try to mentally re-derive the key results
2. Challenge every assumption
3. Identify implicit assumptions not stated
4. Think about how you would improve the work
5. Compare the approach to alternatives

## Structured Note-Taking Template

Use a consistent template for every paper you read:

```markdown
# Paper Notes: [Short Title]

## Metadata
- **Title**: Full title
- **Authors**: First Author et al. (Year)
- **Venue**: Conference/Journal
- **DOI/URL**: link
- **Date read**: YYYY-MM-DD

## Summary (2-3 sentences)
What does this paper do, and what are the main findings?

## Problem
What problem does this paper address? Why is it important?

## Method
How do they approach the problem? Key technical details.

## Key Results
- Result 1: ...
- Result 2: ...
- Result 3: ...

## Strengths
- Strength 1: ...
- Strength 2: ...

## Weaknesses / Limitations
- Weakness 1: ...
- Weakness 2: ...

## Questions / Things I Don't Understand
- Question 1: ...

## Relevance to My Work
How does this connect to my research? What can I use?

## Key References to Follow Up
- [Author, Year] - Why it seems relevant
```

## AI-Assisted Paper Analysis

### Summarization Prompts

Use structured prompts to extract specific information from papers:

```python
# Prompt template for paper summarization
summarize_prompt = """Read the following academic paper and provide:

1. ONE-SENTENCE SUMMARY: The core contribution in a single sentence.

2. KEY FINDINGS (3-5 bullet points):
   - Finding 1 with specific numbers/results
   - Finding 2 ...

3. METHODOLOGY: Describe the approach in 2-3 sentences.

4. LIMITATIONS: List 2-3 limitations acknowledged or unacknowledged.

5. RELEVANCE: How does this relate to [your research topic]?

Paper text:
{paper_text}
"""

# Prompt for critical analysis
critique_prompt = """Analyze the following paper critically:

1. VALIDITY: Are the experimental design and statistical analyses sound?
   Identify any threats to internal/external validity.

2. NOVELTY: What is genuinely new? What is incremental?

3. REPRODUCIBILITY: Could you replicate this study from the description given?
   What information is missing?

4. ALTERNATIVE EXPLANATIONS: Are there alternative interpretations
   of the results that the authors do not consider?

5. FOLLOW-UP QUESTIONS: What would you want to investigate next?

Paper text:
{paper_text}
"""
```

### PDF Processing Pipeline

```python
import fitz  # PyMuPDF

def extract_paper_text(pdf_path):
    """Extract structured text from an academic paper PDF."""
    doc = fitz.open(pdf_path)
    sections = []
    current_section = {"heading": "Preamble", "text": ""}

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"])
                font_size = max(span["size"] for span in line["spans"])
                is_bold = any("Bold" in span.get("font", "") for span in line["spans"])

                # Heuristic: detect section headings
                if is_bold and font_size > 11 and len(text.strip()) < 80:
                    if current_section["text"].strip():
                        sections.append(current_section)
                    current_section = {"heading": text.strip(), "text": ""}
                else:
                    current_section["text"] += text + " "

    if current_section["text"].strip():
        sections.append(current_section)

    doc.close()
    return sections

# Extract and display
sections = extract_paper_text("paper.pdf")
for s in sections:
    print(f"\n## {s['heading']}")
    print(s['text'][:200] + "...")
```

### Batch Paper Processing

```python
import os
import json

def process_paper_batch(pdf_dir, output_file):
    """Process a batch of papers and save structured notes."""
    results = []

    for filename in os.listdir(pdf_dir):
        if not filename.endswith(".pdf"):
            continue

        pdf_path = os.path.join(pdf_dir, filename)
        sections = extract_paper_text(pdf_path)

        # Find title (usually first bold text or first line)
        title = sections[0]["heading"] if sections else filename

        # Find abstract
        abstract = ""
        for s in sections:
            if "abstract" in s["heading"].lower():
                abstract = s["text"].strip()
                break

        results.append({
            "filename": filename,
            "title": title,
            "abstract": abstract,
            "num_sections": len(sections),
            "total_chars": sum(len(s["text"]) for s in sections)
        })

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    return results
```

## Annotation Tools Comparison

| Tool | Platform | Highlights | PDF Annotation | AI Features | Collaboration |
|------|----------|-----------|---------------|-------------|---------------|
| Zotero + ZotFile | All | Reference management + PDF | Yes | No (plugins available) | Group libraries |
| Paperpile | Web/Chrome | Google Docs integration | Yes | No | Shared folders |
| ReadCube Papers | All | Smart citations | Yes | Recommendations | Shared libraries |
| Semantic Reader | Web | AI-augmented reading | Yes | Inline explanations, TLDRs | No |
| Elicit | Web | AI paper search | No | Automated extraction | Tables |
| Scholarcy | Web | Flashcard summaries | Yes | Auto-summarization | No |

## Reading Strategies by Paper Type

| Paper Type | Focus On | Time Budget |
|-----------|----------|-------------|
| **Seminal paper** | Full three-pass reading, understand every detail | 3-4 hours |
| **Survey/review** | Section headings, taxonomy, open questions | 1-2 hours |
| **Methods paper** | Algorithm/procedure sections, pseudocode, evaluation | 1-2 hours |
| **Results paper** | Figures, tables, statistical tests, effect sizes | 30-60 min |
| **Position paper** | Arguments, assumptions, counterarguments | 30-60 min |
| **Related work (peripheral)** | Abstract + conclusion only (Pass 1) | 5-10 min |

## Building a Paper Reading Habit

1. **Set a regular schedule**: Read 2-3 papers per week during dedicated time blocks.
2. **Maintain a reading log**: Track papers read with dates, ratings, and one-line takeaways.
3. **Use a reference manager**: Add papers to your library as you read them, with tags and notes.
4. **Discuss papers**: Join or start a reading group; explaining papers to others deepens understanding.
5. **Connect to your research**: End every reading session by writing one sentence about how the paper relates to your own work.

---

## Paper-to-Agent Exploration

A skill for transforming published research papers into interactive AI agents that can answer questions, explain methodology, and help replicate findings. Based on Paper2Agent (2K stars), this skill guides the agent through extracting structured knowledge from academic papers and creating conversational interfaces for deep exploration.

## Overview

Traditional paper reading is linear and passive. Paper-to-Agent converts this into an active, queryable experience. By parsing a paper's structure, extracting key claims, methodology details, and results, the agent becomes an expert on that specific paper, ready to answer follow-up questions, explain complex sections, and connect findings to the broader literature.

This approach is especially valuable for interdisciplinary researchers who need to quickly understand papers outside their primary expertise, for journal clubs seeking deeper discussion, and for students learning to critically evaluate published research.

## Paper Parsing Workflow

The agent should follow this structured workflow when converting a paper to an interactive agent:

**Step 1: Structure Extraction**
- Identify the paper's sections (abstract, introduction, methods, results, discussion, references)
- Extract the title, authors, affiliations, and publication venue
- Identify figure and table captions along with their referenced locations
- Note supplementary materials and their availability
- Detect the paper type (empirical, theoretical, review, meta-analysis)

**Step 2: Claim Extraction**
- Identify the primary research question or hypothesis
- Extract all major claims made in the paper
- Map each claim to its supporting evidence (data, citations, arguments)
- Note the strength of evidence for each claim (strong, moderate, suggestive)
- Identify limitations acknowledged by the authors

**Step 3: Methodology Mapping**
- Document the complete experimental or analytical pipeline
- Extract parameter values, dataset descriptions, and evaluation metrics
- Identify software tools and libraries used
- Note any preprocessing or data cleaning steps
- Map the methodology to established frameworks in the field

## Interactive Exploration Capabilities

Once a paper has been parsed, the agent can support these interaction patterns:

**Question-Answering**
- Answer specific questions about the paper's content with source references
- Explain technical terms in context of how the paper uses them
- Compare the paper's approach to common alternatives
- Identify what the paper does and does not address
- Generate summaries at different levels of detail (tweet-length, abstract, detailed)

**Critical Analysis**
- Evaluate the validity of statistical analyses
- Identify potential confounds not addressed by the authors
- Assess whether conclusions follow from the presented evidence
- Compare results to related work in the field
- Suggest follow-up experiments that would strengthen the findings

**Replication Assistance**
- Generate step-by-step replication guides from the methods section
- Identify missing details needed for exact replication
- Suggest parameter ranges for robustness checks
- Create data collection templates based on the paper's design
- List required resources (compute, data, equipment) for replication

## Knowledge Graph Construction

The skill supports building knowledge graphs from processed papers:

- Extract entities (methods, datasets, metrics, tools, concepts)
- Map relationships between entities (uses, extends, contradicts, supports)
- Link to external knowledge bases (OpenAlex, CrossRef, DOI)
- Track citation chains for key claims
- Identify research lineages and methodological evolution

## Multi-Paper Analysis

When multiple papers have been processed, the agent can:

- Compare methodologies across papers addressing similar questions
- Identify consensus findings and areas of disagreement
- Trace the evolution of a research direction over time
- Build synthesis summaries combining evidence from multiple sources
- Detect gaps in the literature that no existing paper addresses

## Integration with Research-Claw

This skill connects with other Research-Claw capabilities:

- Use literature search skills to find papers for processing
- Feed extracted knowledge into writing skills for literature reviews
- Connect methodology details to analysis skills for replication
- Store parsed papers in the local knowledge base for future reference
- Generate citation entries compatible with reference management tools

## Practical Tips

- Start with the abstract and conclusion to determine if full parsing is worthwhile
- Focus deep extraction on methods and results sections for empirical papers
- For theoretical papers, prioritize definitions, theorems, and proof sketches
- Always verify extracted claims against the original text before presenting them
- Flag areas where the paper's writing is ambiguous or inconsistent
- Use the parsed representation to generate discussion questions for journal clubs
