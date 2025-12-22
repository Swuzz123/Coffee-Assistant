# backend/api/services/process_content.py
def normalize_ai_content(content) -> str:
  if isinstance(content, str):
    return content

  if isinstance(content, list):
    return " ".join(
      block.get("text", "")
      for block in content
      if isinstance(block, dict)
    )

  return str(content)
