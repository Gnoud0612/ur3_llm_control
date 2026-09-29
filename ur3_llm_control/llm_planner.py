import json
import os
from openai import OpenAI

class LLMPlanner:
    def __init__(self, api_key: str = "none", base_url: str = "http://localhost:20128/v1", model: str = "oc/muse-spark-1.3-contributor-free"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate_plan(self, user_command: str, student_context: dict) -> dict:
        t_map = student_context["target_mapping"]
        system_prompt = f"""
You are an autonomous Task Planner for a UR3 manipulator.
Translate user natural language instructions into a strictly sequenced JSON execution plan.

Student Info:
- Student ID: {student_context['student_info']['id']}
- Target Placement Mapping (by Student ID):
  * Zone A -> {t_map['zone_a']}
  * Zone B -> {t_map['zone_b']}
  * Zone C -> {t_map['zone_c']}

Available Skills:
1. pick(object)
2. place(object, zone)
3. home()

Rules:
- Directly translate the user's requested object and zone into the plan.
- Each 'pick' must be followed immediately by a 'place'.
- Always finish the entire plan with a 'home' skill.
- If the user asks to arrange objects according to student ID, move each object to its corresponding mapped zone.
- Return ONLY valid raw JSON without markdown fences.

Output Format:
{{
  "plan": [
    {{"skill": "pick", "object": "red_cube"}},
    {{"skill": "place", "object": "red_cube", "zone": "zone_b"}},
    {{"skill": "home"}}
  ]
}}
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_command}
            ],
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.strip("`").replace("json\n", "", 1)
        return json.loads(content)
