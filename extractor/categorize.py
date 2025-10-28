import json

def categorize_skills(extracted_skills, category_file="data/categories.json"):
    """
    Categorizes extracted skills into groups using categories.json
    """
    with open(category_file, "r") as f:
        categories = json.load(f)

    categorized = {}
    for category, skill_list in categories.items():
        matched = [skill for skill in extracted_skills if skill.lower() in [s.lower() for s in skill_list]]
        if matched:
            categorized[category] = matched

    return categorized
