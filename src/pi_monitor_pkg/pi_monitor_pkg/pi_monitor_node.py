import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import psutil

class PiMonitorNode(Node):
    def __init__(self):
        super().__init__('pi_monitor_node')
        
        # Топіки для моніторингу
        self.temp_pub = self.create_publisher(Float32, '/pi5/cpu_temp', 10)
        self.cpu_pub = self.create_publisher(Float32, '/pi5/cpu_usage', 10)
        self.ram_pub = self.create_publisher(Float32, '/pi5/ram_usage', 10)
        
        
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        # 1. Температура CPU (°C)
        msg_temp = Float32()
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                msg_temp.data = float(f.read().strip()) / 1000.0
        except Exception:
            msg_temp.data = 0.0
        self.temp_pub.publish(msg_temp)

      
        msg_cpu = Float32()
        msg_cpu.data = float(psutil.cpu_percent())
        self.cpu_pub.publish(msg_cpu)

      
        msg_ram = Float32()
        msg_ram.data = float(psutil.virtual_memory().percent)
        self.ram_pub.publish(msg_ram)

        self.get_logger().info(
            f'Temp: {msg_temp.data:.1f}°C | CPU: {msg_cpu.data:.1f}% | RAM: {msg_ram.data:.1f}%'
        )

def main(args=None):
    rclpy.init(args=args)
    node = PiMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()