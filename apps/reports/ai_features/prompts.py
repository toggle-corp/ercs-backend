PAGE_PROMPT = """
You are analyzing an image of a document page.
Extract all content and return ONLY a valid JSON object with no explanation, no markdown, no backticks.

Use exactly this structure:
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
  "summary": "brief summary of the page content including key information from tables and charts under 200 words.",
}

Rules:
- Return ONLY the JSON object, nothing else
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

        Return only a concise abstractive summary in 2–4 paragraphs,
        formatted exactly as a JSON object with the single key "doc_summary".
    """
