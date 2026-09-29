import rclpy
from rclpy.action import ActionClient
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, Constraints, JointConstraint, PositionConstraint, OrientationConstraint
from geometry_msgs.msg import PoseStamped
from shape_msgs.msg import SolidPrimitive
import time

class RobotSkills:
    def __init__(self, node, scene_config):
        self.node = node
        self.scene = scene_config.get("scene", scene_config)
        self._action_client = ActionClient(self.node, MoveGroup, "move_action")
        
        self.node.get_logger().info("Đang kết nối tới MoveGroup action server...")
        self.has_real_controller = self._action_client.wait_for_server(timeout_sec=3.0)
        if self.has_real_controller:
            self.node.get_logger().info("-> Đã kết nối thành công với MoveGroup!")
        else:
            self.node.get_logger().warn("Chưa thấy server 'move_action', sẽ chạy ở chế độ mô phỏng lệnh.")

    def _send_pose_goal(self, x, y, z):
        if not self.has_real_controller:
            time.sleep(1.0)
            return "SUCCESS"

        goal_msg = MoveGroup.Goal()
        req = MotionPlanRequest()
        req.group_name = "ur_manipulator"
        # Cấp thêm số vòng dò đường để giải được tọa độ vị trí chính xác tuyệt đối
        req.num_planning_attempts = 50
        req.allowed_planning_time = 15.0
        
        req.max_velocity_scaling_factor = 0.5
        req.max_acceleration_scaling_factor = 0.5

        target_pose = PoseStamped()
        target_pose.header.frame_id = "base_link"
        target_pose.pose.position.x = float(x)
        target_pose.pose.position.y = float(y)
        target_pose.pose.position.z = float(z)
        
        target_pose.pose.orientation.x = 1.0
        target_pose.pose.orientation.y = 0.0
        target_pose.pose.orientation.z = 0.0
        target_pose.pose.orientation.w = 0.0

        constraints = Constraints()
        
        # 1. SIẾT CHẶT DUNG SAI VỊ TRÍ XUỐNG 1CM ĐỂ VƯƠN ĐÚNG TÂM
        pos_constraint = PositionConstraint()
        pos_constraint.header.frame_id = "base_link"
        pos_constraint.link_name = "tool0"
        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.SPHERE
        primitive.dimensions = [0.01] 
        pos_constraint.constraint_region.primitives.append(primitive)
        pos_constraint.constraint_region.primitive_poses.append(target_pose.pose)
        pos_constraint.weight = 1.0
        constraints.position_constraints.append(pos_constraint)

        # 2. SIẾT CHẶT DUNG SAI GÓC QUAY ĐỂ CHỐNG LỆCH TRỤC
        ori_constraint = OrientationConstraint()
        ori_constraint.header.frame_id = "base_link"
        ori_constraint.link_name = "tool0"
        ori_constraint.orientation = target_pose.pose.orientation
        ori_constraint.absolute_x_axis_tolerance = 0.1
        ori_constraint.absolute_y_axis_tolerance = 0.1
        ori_constraint.absolute_z_axis_tolerance = 3.14159
        ori_constraint.weight = 1.0
        constraints.orientation_constraints.append(ori_constraint)

        req.goal_constraints.append(constraints)
        goal_msg.request = req

        future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=10.0)
        goal_handle = future.result()
        if not goal_handle or not goal_handle.accepted:
            return "PLANNING_FAILED"

        res_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self.node, res_future, timeout_sec=120.0)
        result = res_future.result()
        
        if result and result.result.error_code.val == 1:
            return "SUCCESS"
        return "EXECUTION_TIMEOUT"

    def _send_joint_goal(self, joint_angles):
        if not self.has_real_controller:
            time.sleep(1.0)
            return "SUCCESS"

        goal_msg = MoveGroup.Goal()
        req = MotionPlanRequest()
        req.group_name = "ur_manipulator"
        req.num_planning_attempts = 10
        req.allowed_planning_time = 5.0
        req.max_velocity_scaling_factor = 0.5
        req.max_acceleration_scaling_factor = 0.5

        joint_names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", 
                       "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
        
        constraints = Constraints()
        for name, angle in zip(joint_names, joint_angles):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = float(angle)
            jc.tolerance_above = 0.05
            jc.tolerance_below = 0.05
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)

        req.goal_constraints.append(constraints)
        goal_msg.request = req

        future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=10.0)
        goal_handle = future.result()
        if not goal_handle or not goal_handle.accepted:
            return "PLANNING_FAILED"

        res_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self.node, res_future, timeout_sec=120.0)
        result = res_future.result()
        
        if result and result.result.error_code.val == 1:
            return "SUCCESS"
        return "EXECUTION_TIMEOUT"

    def pick(self, object_name: str) -> str:
        coords = self.scene.get("objects", {}).get(object_name)
        if not coords:
            return "OBJECT_NOT_FOUND"
        return self._send_pose_goal(coords[0], coords[1], coords[2])

    def place(self, object_name: str, zone_name: str) -> str:
        coords = self.scene.get("zones", {}).get(zone_name)
        if not coords:
            return "ZONE_NOT_FOUND"
        return self._send_pose_goal(coords[0], coords[1], coords[2])

    def home(self) -> str:
        home_pos = self.scene.get("home_position", [0.0, -1.57, 1.57, -1.57, -1.57, 0.0])
        return self._send_joint_goal(home_pos)
