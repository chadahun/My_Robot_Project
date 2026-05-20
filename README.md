# Multi-Robot Differential Drive
## 프로젝트 개요
  - 목표
    - ROS 2 환경에서 2륜 차동 주행 로봇의 멀티 환경 통합 제어 시스템 구현
  - 주요기능
    - ros2_control 기반 하드웨어 추상화 및 제어기 매핑
    - frame_id 기반의 센서 데이터 필터링을 통한 추종 제어 안정화
## 시연영상
  https://github.com/user-attachments/assets/70629f6d-4a97-407c-b250-836e18ead968
## 기술 스택
  - OS: Ubuntu 22.04 (WSL2)
  - Framework: ROS 2 Humble
  - Tools: Gazebo, RViz2, Xacro, ros2_control
  - Language: C++, Python
## 실행방법
  - 의존성 설치
    - ```bash
      rosdep install --from-paths src --ignore-src -r -y
  - 빌드
    - ```bash
      colcon build --symlink-install
    - ```bash
      source install/setup.bash
  - 통합 런치파일 실행
    - ```bash
      ros2 launch my_robot_bringup bringup.launch.py
## 핵심 트러블슈팅
  - Gazebo 플러그인 네임스페이스 충돌: 플러그인 간 데이터 간섭 문제를 해결하기 위해, 수신 노드에서 frame_id 검사를 통한 C++ 필터링 로직 구현
## 향후 로드맵
  - [ ] 타겟 소실 시 탐색(Search) 로직 고도화
  - [ ] 후방 추종 및 양방향 주행 제어 로직 추가
