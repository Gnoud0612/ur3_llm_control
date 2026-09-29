import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'ur3_llm_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sinh vien UET',
    maintainer_email='23020732@vnu.edu.vn',
    description='UR3 LLM Skill-based control',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'executor = ur3_llm_control.skill_executor:main',
        ],
    },
)
