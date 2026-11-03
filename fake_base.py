#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster


class FakeBaseC1(Node):
    def __init__(self):
        super().__init__('fake_base')

        # Оголошення параметрів із значеннями за замовчуванням
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('laser_frame', 'laser')
        self.declare_parameter('laser_z_offset', 0.18)
        self.declare_parameter('cmd_timeout', 0.5)

        self.odom_frame = self.get_parameter('odom_frame').get_parameter_value().string_value
        self.base_frame = self.get_parameter('base_frame').get_parameter_value().string_value
        self.laser_frame = self.get_parameter('laser_frame').get_parameter_value().string_value
        self.laser_z_offset = self.get_parameter('laser_z_offset').get_parameter_value().double_value
        self.cmd_timeout = self.get_parameter('cmd_timeout').get_parameter_value().double_value

        # Топіки (відносні імена для підтримки неймспейсів)
        self.subscription = self.create_subscription(
            Twist, 'cmd_vel', self.cmd_vel_callback, 10
        )
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)

        # Публікуємо статичний TF base_link -> laser для лідара Slamtec C1
        self.publish_static_laser_tf()

        self.x, self.y, self.th = 0.0, 0.0, 0.0
        self.vx, self.vth = 0.0, 0.0
        self.last_time = self.get_clock().now()
        self.last_cmd_time = self.get_clock().now()

        # Періодичне оновлення стану (20 Гц)
        self.timer = self.create_timer(0.05, self.update)
        self.get_logger().info(
            f'Fake Base + Static TF ({self.base_frame} -> {self.laser_frame}) для C1 запущено'
        )

    def publish_static_laser_tf(self):
        static_tf = TransformStamped()
        static_tf.header.stamp = self.get_clock().now().to_msg()
        static_tf.header.frame_id = self.base_frame
        static_tf.child_frame_id = self.laser_frame
        static_tf.transform.translation.x = 0.0
        static_tf.transform.translation.y = 0.0
        static_tf.transform.translation.z = self.laser_z_offset
        static_tf.transform.rotation.x = 0.0
        static_tf.transform.rotation.y = 0.0
        static_tf.transform.rotation.z = 0.0
        static_tf.transform.rotation.w = 1.0
        self.static_tf_broadcaster.sendTransform(static_tf)

    def cmd_vel_callback(self, msg: Twist):
        self.vx = msg.linear.x
        self.vth = msg.angular.z
        self.last_cmd_time = self.get_clock().now()

    def update(self):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time

        # Watchdog: зупинка робота у разі відсутності команд довше cmd_timeout
        if (current_time - self.last_cmd_time).nanoseconds / 1e9 > self.cmd_timeout:
            self.vx = 0.0
            self.vth = 0.0

        # Розрахунок координат (Unicycle/Differential drive кінематика)
        self.x += (self.vx * math.cos(self.th)) * dt
        self.y += (self.vx * math.sin(self.th)) * dt
        self.th += self.vth * dt

        qz = math.sin(self.th / 2.0)
        qw = math.cos(self.th / 2.0)

        # Публікація динамічного TF odom -> base_link
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(t)

        # Публікація одометрії
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.x = 0.0
        odom.pose.pose.orientation.y = 0.0
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        # Базова коваріація (діагональ)
        odom.pose.covariance[0] = 0.001   # x
        odom.pose.covariance[7] = 0.001   # y
        odom.pose.covariance[14] = 1.0e6  # z (плоский робот)
        odom.pose.covariance[21] = 1.0e6  # roll
        odom.pose.covariance[28] = 1.0e6  # pitch
        odom.pose.covariance[35] = 0.001  # yaw

        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.linear.z = 0.0
        odom.twist.twist.angular.x = 0.0
        odom.twist.twist.angular.y = 0.0
        odom.twist.twist.angular.z = self.vth

        odom.twist.covariance[0] = 0.001
        odom.twist.covariance[7] = 0.001
        odom.twist.covariance[14] = 1.0e6
        odom.twist.covariance[21] = 1.0e6
        odom.twist.covariance[28] = 1.0e6
        odom.twist.covariance[35] = 0.001

        self.odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = FakeBaseC1()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

