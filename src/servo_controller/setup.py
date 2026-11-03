from setuptools import find_packages, setup

package_name = 'servo_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='artem',  # або ваше ім'я
    maintainer_email='artem@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    # 👇 ОСЬ СЮДИ ПОТРІБНО ВСТАВИТИ ЦЕЙ БЛОК:
    entry_points={
        'console_scripts': [
            'servo_node = servo_controller.servo_node:main',
        ],
    },
)