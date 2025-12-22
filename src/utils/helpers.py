# utils/helpers.py
import re
import unicodedata

class QueryClassifier:
  """
  Classifies customer queries into menu-related intents for a coffee shop
  assistant, supporting Vietnamese and English inputs.

  The classifier detects whether a query refers to:
  - a specific menu item
  - a sub-category
  - a main category
  - or an unknown intent

  Matching is accent-insensitive and case-insensitive to ensure robust
  handling of natural language queries.
  """
  def __init__(self, mappings):
    """
    Initialize the QueryClassifier with menu mappings.
    
    Args:
      mappings(dict): A hierarchical menu structure in the form:
                      {
                        "Main Category": {
                          "Sub Category": ["Item 1", "Item 2", ...]
                        }
                      }
    """
    self.mappings = mappings
    self.main_cats, self.sub_cats, self.items = self.build_lookup_tables()
  
  # ----------------------------------------------------------------------------
  def normalize_text(self, text):
    """
    Normalize text by removing Vietnamese accents, converting to lowercase,
    and trimming whitespace.

    This enables accent-insensitive and case-insensitive matching.

    Args: 
      text(str): Input text to normalize.

    Returns:
      str: Normalized text.
    """
    # Convert Vietnamese to accent-free + lowercase for robust matching
    text = unicodedata.normalize('NFD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    return text.lower().strip()

  # ----------------------------------------------------------------------------
  def build_lookup_tables(self):
    """
    Extract and cache all main categories, sub-categories, and items from the 
    menu mappings.

    Returns:
      tuple: A tuple of sets (main_categories, sub_categories, items).
    """
    main_cats, sub_cats, items = set(), set(), set()
    for main_cat, subs in self.mappings.items():
      main_cats.add(main_cat)
      for sub_cat, drinks in subs.items():
        if sub_cat:
          sub_cats.add(sub_cat)
        for drink in drinks:
          items.add(drink)
    return main_cats, sub_cats, items

  # ----------------------------------------------------------------------------
  def classify_query(self, query):
    """
    Classify a user query into the most specific menu-related intent.

    Matching priority:
    1. Item
    2. Sub-category
    3. Main category

    Args:
      query(str): User input query.

    Returns:
      dict: Classification result with the following structure:
            {
              "type": "item" | "sub_category" | "main_category" | "unknown",
              "keyword": str | None
            }
    """
    query_norm = self.normalize_text(query)

    # Normalize all names for comparison
    norm_main = {self.normalize_text(c): c for c in self.main_cats}
    norm_sub = {self.normalize_text(c): c for c in self.sub_cats}
    norm_items = {self.normalize_text(i): i for i in self.items}

    # Exact beverage (title) match
    for norm_name, original in norm_items.items():
      if norm_name in query_norm:
        return {"type": "item", "keyword": original}

    # Sub-category match
    for norm_name, original in norm_sub.items():
      if re.search(rf"\b{re.escape(norm_name)}\b", query_norm):
        return {"type": "sub_category", "keyword": original}

    # Main category match
    for norm_name, original in norm_main.items():
      if re.search(rf"\b{re.escape(norm_name)}\b", query_norm):
        return {"type": "main_category", "keyword": original}

    return {"type": "unknown", "keyword": None}

# # TODO: Implement rotate key mechanism and check status code to have key to use when exhausted
# class APIKeyManager:
#   def __init__(self):
#     pass