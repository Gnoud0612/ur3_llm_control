class TaskValidator:
    VALID_SKILLS = {"pick", "place", "home"}
    VALID_OBJECTS = {"red_cube", "yellow_cube", "blue_cube"}
    VALID_ZONES = {"zone_a", "zone_b", "zone_c", "temp_zone"}

    @staticmethod
    def validate(plan_data: dict) -> tuple[bool, str]:
        if not isinstance(plan_data, dict) or "plan" not in plan_data:
            return False, "Thiếu trường 'plan' trong dữ liệu JSON."

        plan = plan_data["plan"]
        if not isinstance(plan, list) or len(plan) == 0:
            return False, "Kế hoạch rỗng."

        if len(plan) == 1 and plan[0].get("skill") == "home":
            return False, "Kế hoạch không hợp lệ: Không có hành động gắp/thả nào được thực hiện."

        holding = False
        for i, step in enumerate(plan):
            skill = step.get("skill")
            if skill not in TaskValidator.VALID_SKILLS:
                return False, f"Bước {i+1}: Skill '{skill}' không hợp lệ."

            if skill == "pick":
                if holding:
                    return False, f"Bước {i+1}: Robot đang gắp một vật khác, không thể gắp tiếp."
                obj = step.get("object")
                if obj not in TaskValidator.VALID_OBJECTS:
                    return False, f"Bước {i+1}: Vật thể '{obj}' không tồn tại."
                holding = True

            elif skill == "place":
                if not holding:
                    return False, f"Bước {i+1}: Robot chưa gắp vật thể nào để đặt."
                zone = step.get("zone")
                if zone not in TaskValidator.VALID_ZONES:
                    return False, f"Bước {i+1}: Vùng đích '{zone}' không tồn tại trong hệ thống."
                holding = False

        if plan[-1].get("skill") != "home":
            return False, "Bước cuối cùng của kế hoạch bắt buộc phải là 'home'."

        return True, "Kế hoạch hợp lệ."
