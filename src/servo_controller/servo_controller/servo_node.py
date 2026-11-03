import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult

import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit


class MultiServoParamNode(Node):

  def __init__(self):
    super().__init__('multi_servo_param_node')

    # Ініціалізація I2C та PCA9685 (на 16 каналів, використовуємо перші 8)
    i2c = busio.I2C(board.SCL, board.SDA)
    self.kit = ServoKit(channels=16, i2c=i2c)

    # Словник для зберігання кутів та оголошення 8 параметрів
    self.servo_angles = {}
    for i in range(8):
      param_name = f'servo_{i}'
      # За замовчуванням встановлюємо нейтральний кут 90.0 градусів
      self.declare_parameter(param_name, 90.0)
      self.servo_angles[i] = 90.0
      self.kit.servo[i].angle = 90.0

    # Реєструємо колбек на зміну будь-якого з параметрів
    self.add_on_set_parameters_callback(self.param_callback)
    self.get_logger().info(
        'Multi-Servo Parameter Node initialized for 8 servos.'
    )

  def param_callback(self, params):
    for param in params:
      # Перевіряємо, чи параметр відповідає нашим сервоприводам (servo_0 ... servo_7)
      if param.name.startswith('servo_'):
        try:
          servo_idx = int(param.name.split('_')[1])
          if 0 <= servo_idx < 8:
            angle = param.value
            if 0 <= angle <= 180:
              self.kit.servo[servo_idx].angle = float(angle)
              self.servo_angles[servo_idx] = float(angle)
              self.get_logger().info(
                  f'Servo {servo_idx} set to angle: {angle}°'
              )
            else:
              self.get_logger().warn(
                  f'Angle {angle} for servo {servo_idx} out of bounds (0-180).'
              )
        except ValueError:
          pass

    return SetParametersResult(successful=True)


def main(args=None):
  rclpy.init(args=args)
  node = MultiServoParamNode()
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass
  finally:
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
  main()