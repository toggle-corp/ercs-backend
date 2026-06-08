PAGE_PROMPT = """
You are analyzing an image of a document page.
Extract all content and return ONLY a valid JSON object with no explanation, no markdown, no backticks.

Use exactly this structure:
{
  "extracted_text": "extracted texts of the page"
  "key_findings": "important phrases separted by a period", 
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
  "summary": "brief summary of the page content including key information from tables and charts",
}

Rules:
- Return ONLY the JSON object, nothing else
- If no tables found, return "tables": []
- If no charts found, return "charts": []
- If no key findings, return "key_findings": "" else express in phrases
- Do not include trailing commas
"""
