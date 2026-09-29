#!/usr/bin/env python3
import subprocess
import yaml
import os

def spawn_entity(name, x, y, r, g, b, is_zone=False):
    if is_zone:
        # Tấm đánh dấu Zone ban đầu: 16cm x 16cm x 0.5cm
        sx, sy, sz = 0.16, 0.16, 0.005
        z_pos = 0.0025
    else:
        # Khối lập phương ban đầu: 6.5cm x 6.5cm x 6.5cm
        sx, sy, sz = 0.065, 0.065, 0.065
        z_pos = 0.0325

    sdf = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{name}">
    <static>true</static>
    <pose>{x} {y} {z_pos} 0 0 0</pose>
    <link name="link">
      <collision name="col">
        <geometry><box><size>{sx} {sy} {sz}</size></box></geometry>
      </collision>
      <visual name="vis">
        <geometry><box><size>{sx} {sy} {sz}</size></box></geometry>
        <material>
          <ambient>{r} {g} {b} 1.0</ambient>
          <diffuse>{r} {g} {b} 1.0</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>"""
    
    path = f"/tmp/{name}.sdf"
    with open(path, "w") as f:
        f.write(sdf)

    cmd = [
        "ros2", "run", "ros_gz_sim", "create",
        "-world", "empty",
        "-file", path,
        "-name", name,
        "-x", str(x),
        "-y", str(y),
        "-z", str(z_pos)
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"[OK] Đã tạo {name} tại [{x}, {y}]")

def main():
    items = ["yellow_cube", "red_cube", "blue_cube", "zone_a", "zone_b", "zone_c"]
    for item in items:
        subprocess.run([
            "gz", "service", "-s", "/world/empty/remove",
            "--reqtype", "gz.msgs.Entity",
            "--reptype", "gz.msgs.Boolean",
            "--timeout", "500",
            "--req", f'name: "{item}", type: 2'
        ], capture_output=True)

    yaml_path = os.path.expanduser("~/workspaces/ur_gz/src/ur3_llm_control/config/scene.yaml")
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
        
    scene_data = data.get("scene", data)

    colors = {
        "yellow_cube": [1, 1, 0],
        "red_cube": [1, 0, 0],
        "blue_cube": [0, 0, 1],
        "zone_a": [1, 1, 0],
        "zone_b": [1, 0, 0],
        "zone_c": [0, 0, 1]
    }

    print("--- Đang nạp các vùng đích (16cm) ---")
    for name, pos in scene_data.get("zones", {}).items():
        c = colors.get(name, [0.5, 0.5, 0.5])
        spawn_entity(name, pos[0], pos[1], c[0], c[1], c[2], is_zone=True)

    print("--- Đang nạp các khối hộp (6.5cm) ---")
    for name, pos in scene_data.get("objects", {}).items():
        c = colors.get(name, [0.5, 0.5, 0.5])
        spawn_entity(name, pos[0], pos[1], c[0], c[1], c[2], is_zone=False)

if __name__ == "__main__":
    main()
