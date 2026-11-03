# ROS 2 Mobile Robot Navigation & Control Workspace

Робочий простір ROS 2 для мобільного робота на базі лідара Slamtec C1, навігаційного стека Nav2, SLAM Toolbox та micro-ROS.

## 📁 Структура проєкту

* `fake_base.py` — симуляційна одометрія (диференціальна кінематика) та публікація TF (`odom -> base_link` та статичний `base_link -> laser`) із вбудованим watchdog таймером.
* `nav2_params.yaml` — конфігураційні параметри для стека Nav2 (AMCL, Controller Server, Planner, Costmaps, Collision Monitor, Velocity Smoother).
* `slam_params.yaml` — параметри картографування для `slam_toolbox`.
* `ros2.repos` — список зовнішніх залежностей (Slamtec C1 драйвер, micro-ROS).
* `src/`:
  * `servo_controller/` — вузол керування сервоприводами.
  * `pi_monitor_pkg/` — моніторинг стану Raspberry Pi (температура, ресурси тощо).
  * `my_f_pkg/` — допоміжний пакет розробки.
  * `micro_ros_setup/`, `uros/` — мікро-ROS для зв'язку з мікроконтролером приводу.

## 🚀 Встановлення та збірка

1. Клонування залежностей:
   ```bash
   vcs import < ros2.repos
   ```

2. Встановлення ROS-залежностей:
   ```bash
   rosdep install --from-paths src --ignore-src -r -y
   ```

3. Збірка робочого простору:
   ```bash
   colcon build --symlink-install
   source install/setup.bash
   ```

## 🛠 Запуск

* **Фейкова база та TF:**
  ```bash
  ./fake_base.py
  ```

* **Навігація (Nav2):**
  ```bash
  ros2 launch nav2_bringup bringup_launch.py params_file:=./nav2_params.yaml
  ```

