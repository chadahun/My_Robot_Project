#include <rclcpp/rclcpp.hpp>

#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <std_msgs/msg/float32.hpp>

#include <chrono>
#include <cmath>
#include <algorithm>
#include <memory>

enum class DriveMode{
    STOP,
    LEADER_FOLLOW,
    LANE_FOLLOW,
    IDLE
};

class FollowerNode: public rclcpp::Node{
    public:
        FollowerNode():Node("follower_node"){
            this->declare_parameter("kp_angular", 0.005);
            this->declare_parameter("base_linear_velocity", 0.2);

            callback_group_ = this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);

            auto sub_options = rclcpp::SubscriptionOptions();
            sub_options.callback_group = callback_group_;

            yolo_sub_ = this->create_subscription<std_msgs::msg::Float32>(
                "/my_robot/yolo_error", 10, [this](const std_msgs::msg::Float32::SharedPtr msg){
                    this->yolo_callback(msg);
                },
                sub_options
            );

            cmd_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("/my_robot/diff_drive_controller/cmd_vel_unstamped", 10);

            lidar_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
                "/my_robot/scan", rclcpp::SensorDataQoS().keep_last(1),
                [this](const sensor_msgs::msg::LaserScan::SharedPtr msg){
                    this->scan_callback(msg);
                },
                sub_options
            );

            lane_sub_ = this->create_subscription<std_msgs::msg::Float32>(
                "/my_robot/lane_error", 10,
                [this](const std_msgs::msg::Float32::SharedPtr msg){
                    lane_error_ = msg->data;
                    lane_detected_ = (msg->data != 0.0f);
                },
                sub_options
            );

            timer_ = this->create_wall_timer(
                std::chrono::milliseconds(50), [this](){
                    this->control_loop();
                },
                callback_group_
            );

            last_yolo_time_ = this->now();

            RCLCPP_INFO(this->get_logger(), "Starting autonomous driving");
        }
    private:
        rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
        rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr lidar_sub_;
        rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr lane_sub_;
        rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr yolo_sub_;
        rclcpp::TimerBase::SharedPtr timer_;
        rclcpp::CallbackGroup::SharedPtr callback_group_;

        float current_dist_{100.0f};
        float last_yolo_error_{0.0f};
        rclcpp::Time last_yolo_time_;
        bool is_leader_detected_{false};
        float min_dist_{10.0f};

        float error_sum_{0.0f};
        float last_error_{0.0f};

        float lane_error_{0.0f};
        bool lane_detected_{false};

        float target_distance_{0.6f};
        float p_gain_{1.0f};
        float i_gain_{0.01f};
        float d_gain_{0.5f};
        float dt_{0.1f};

        void yolo_callback(const std_msgs::msg::Float32::SharedPtr msg){
            last_yolo_error_ = msg->data;
            last_yolo_time_ = this->now();
            is_leader_detected_ = true;
        }

        void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg){
            if(msg->header.frame_id != "my_robot/laser_link"){
                return;
            }

            int front_idx{static_cast<int>(std::round((0.0 - msg->angle_min) / msg->angle_increment))};
            float min_val{100.0f};
            int window{20};

            for(int i=front_idx - window; i<=front_idx + window; ++i){
                if(i>=0 && i<(int)msg->ranges.size()){
                    float val = msg->ranges[i];
                    if(std::isfinite(val) && val >  msg->range_min && val < min_val){
                        min_val = val;
                    }
                }
            }
            current_dist_ = min_val;
        }

        void control_loop(){
            auto cmd_msg{geometry_msgs::msg::Twist{}};
            DriveMode mode{determine_mode()};

            switch (mode){
            case DriveMode::STOP:
                cmd_msg.linear.x = 0.0;
                cmd_msg.angular.z = 0.0;
                RCLCPP_WARN(this->get_logger(), "MODE: STOP");
                break;

            case DriveMode::LEADER_FOLLOW:
                cmd_msg.linear.x = calculate_velocity();
                cmd_msg.angular.z = -this->get_parameter("kp_angular").as_double() * last_yolo_error_;
                RCLCPP_INFO(this->get_logger(), "MODE: Following Leader");
                break;

            case DriveMode::LANE_FOLLOW:
                cmd_msg.linear.x = 0.2;
                cmd_msg.angular.z = std::clamp(lane_error_ * 0.005f, -0.5f, 0.5f);
                RCLCPP_INFO(get_logger(), "MODE: Lane Following");
                break;

            default:
                cmd_msg.linear.x = 0.0;
                cmd_msg.angular.z = 0.0;
                break;
            }
            cmd_pub_->publish(cmd_msg);
        }

        DriveMode determine_mode(){
            double yolo_dt{(this->now() - last_yolo_time_).seconds()};

            if(current_dist_ < 0.4) return DriveMode::STOP;
            if(is_leader_detected_ && yolo_dt < 0.5) return DriveMode::LEADER_FOLLOW;
            if(lane_detected_) return DriveMode::LANE_FOLLOW;
            return DriveMode::IDLE;
        }

        float calculate_velocity(){
            float error{current_dist_ - target_distance_};
            error_sum_ += (error * dt_);
            float error_diff{(error - last_error_) / dt_};
            last_error_ = error;
            float vel{(error * 1.0f) + (0.01f * error_sum_) + (0.5f * error_diff)};
            return std::clamp(vel, -0.3f, 0.5f);
        }

};

int main(int argc, char *argv[]){
    rclcpp::init(argc, argv);
    auto node{std::make_shared<FollowerNode>()};

    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(node);
    executor.spin();

    rclcpp::shutdown();
    return 0;
}

// if(current_dist <= 1.2){
//                 float error = current_dist - target_distance_;

//                 error_sum_ += (error * dt_);
//                 float error_diff = (error - last_error_) / dt_;
//                 float linear_velocity = (error * p_gain_) + (i_gain_ * error_sum_) + (d_gain_ * error_diff);

//                 last_error_ = error;

//                 linear_velocity = std::clamp(linear_velocity, -0.3f, 0.5f);

//                 cmd_msg.linear.x = linear_velocity;

//                 RCLCPP_INFO(this->get_logger(), "[ACC Mode] Dist: %.2f | Err: %.2f | Vel: %.2f", current_dist, error, linear_velocity);
//             }
//             else{
//                 cmd_msg.linear.x = 0.2;
//                 error_sum_ = 0.0;
//                 last_error_ = 0.0;

//                 RCLCPP_INFO(this->get_logger(), "[Cruise Mode] Road is clear. Cruising at 0.2 m/s");
//             }

//             if(lane_detected_){
//                 float raw_angular = lane_error_ * 0.005;
//                 cmd_msg.angular.z = std::clamp(raw_angular, -0.5f, 0.5f);
//             }
//             else{
//                 cmd_msg.angular.z = 0.0;
            // }