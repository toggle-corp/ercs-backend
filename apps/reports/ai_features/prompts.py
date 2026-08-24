PAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "extracted_text": {"type": "string"},
        "key_findings": {"type": "string"},
        "tables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "headers": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                },
                "required": ["title", "headers", "rows"],
            },
        },
        "charts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["type", "title", "description"],
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["extracted_text", "key_findings", "tables", "charts", "summary"],
}

DOC_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "doc_summary": {"type": "string"},
        "doc_summary_short": {"type": "string"},
    },
}

PAGE_PROMPT = """
You are analyzing an image(scan) of a document page.
Extract all content and return ONLY a valid JSON object based on page schema
with no explanation, no markdown, no backticks.

Use this exact structure:
{
  "extracted_text": "extracted texts of the page"
  "key_findings": "important phrases separated by a period",
  "tables": [
    {
      "title": "table title if present",
      "headers": ["col1", "col2"],
      "rows": [["val1", "val2"]]
    }
  ],
  "charts": [
    {
      "type": "bar/line/pie etc",
      "title": "chart title if present",
      "description": "extract key information and describe what the chart shows"
    }
  ],
  "summary": "brief summary of the extracted texts including key information from tables and charts under 200 words.",
}

Rules:
- Return ONLY the valid JSON object following the schema
- If no tables found, return "tables": []
- If no charts found, return "charts": []
- If no key findings, return "key_findings": "" else express in phrases
- Do not include trailing commas
"""


def get_doc_summary_prompt(page_summaries: list[str]):
    return f"""
        You are an expert document analyst.

        You will be given summaries extracted from individual pages of a document.

        Your task is to create a single, coherent summary by:
        1. Combining information from all pages.
        2. Removing duplicate or repetitive information.
        3. Preserving important facts, findings, statistics, dates, and conclusions.
        4. Identifying the main themes discussed throughout the document.
        5. Highlighting key findings and recommendations where applicable.
        6. Maintaining factual accuracy and avoiding information that is not present in the provided summaries.

        Writing style:
        - Write the summary as a direct description of the subject matter,
          not of the document itself.
        - Do NOT begin with phrases such as "This document...",
          "The document...", "This report...", "The report...",
          "This presentation...", or similar meta-references.
        - Start immediately with the primary topic or subject.
          For example, write "The disaster response..."
          instead of "This document provides an overview of disaster response."
        - Use an informative, objective, and concise tone.
        - Do not mention page numbers, sections, or that the information
          was extracted from multiple pages.

        Page Summaries:

        {chr(10).join(f"Page {i + 1}: {summary}" for i, summary in enumerate(page_summaries))}

        Return two things as a JSON object with the specified keys:
        1. a concise abstractive summary in 2–4 paragraphs in the key "doc_summary".
        2. a concise and very short summary in 15-20 words, specifying what this document
        is all about including the year of the report published(if available) in the key "doc_summary_short".
    """
