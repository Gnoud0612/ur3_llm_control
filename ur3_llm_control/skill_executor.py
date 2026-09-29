import os
import sys
import yaml
import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from ur3_llm_control.llm_planner import LLMPlanner
from ur3_llm_control.task_validator import TaskValidator
from ur3_llm_control.robot_skills import RobotSkills

class MainExecutor(Node):
    def __init__(self):
        super().__init__('ur3_llm_executor')

        pkg_dir = get_package_share_directory('ur3_llm_control')
        student_cfg_path = os.path.join(pkg_dir, 'config', 'student_config.yaml')
        scene_cfg_path = os.path.join(pkg_dir, 'config', 'scene.yaml')

        with open(student_cfg_path, 'r') as f:
            self.student_config = yaml.safe_load(f)
        with open(scene_cfg_path, 'r') as f:
            self.scene_config = yaml.safe_load(f)

        self.planner = LLMPlanner()
        self.skills = RobotSkills(self, self.scene_config)

    def run_command(self, user_command: str):
        print(f"\nUSER COMMAND:\n{user_command}\n")

        # 1. LLM Planning
        try:
            plan_dict = self.planner.generate_plan(user_command, self.student_config)
        except Exception as e:
            print(f"Lỗi gọi LLM Planner: {e}\n")
            return

        print("LLM PLAN:")
        for step in plan_dict.get("plan", []):
            if step["skill"] == "home":
                print("home()")
            elif step["skill"] == "pick":
                print(f"pick({step.get('object')})")
            elif step["skill"] == "place":
                print(f"place({step.get('object')}, {step.get('zone')})")
        print()

        # 2. Validation
        valid, reason = TaskValidator.validate(plan_dict)
        if not valid:
            print(f"VALIDATION FAILED: {reason}")
            print("TASK ABORTED\n")
            return

        # 3. Execution
        print("EXECUTION:")
        for step in plan_dict["plan"]:
            skill = step["skill"]
            status = "FAILED"

            if skill == "home":
                status = self.skills.home()
                print(f"home() ................. {status}")
            elif skill == "pick":
                status = self.skills.pick(step["object"])
                print(f"pick({step['object']}) ........ {status}")
            elif skill == "place":
                status = self.skills.place(step["object"], step["zone"])
                print(f"place({step['object']}, {step['zone']}) SUCCESS" if status == "SUCCESS" else f"place({step['object']}, {step['zone']}) {status}")

            if status != "SUCCESS":
                print(f"\nTASK FAILED AT STEP: {skill}\n")
                return

        print("\nTASK SUCCESS\n")

def main(args=None):
    rclpy.init(args=args)
    executor = MainExecutor()

    print("=" * 50)
    print(f" UR3 LLM CONTROLLER - MSSV: {executor.student_config['student_info']['id']}")
    print("=" * 50)

    while rclpy.ok():
        try:
            cmd = input("Nhập câu lệnh (hoặc 'exit' để thoát): ")
            if cmd.strip().lower() in ['exit', 'quit']:
                break
            if cmd.strip():
                executor.run_command(cmd)
        except KeyboardInterrupt:
            break

    executor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
