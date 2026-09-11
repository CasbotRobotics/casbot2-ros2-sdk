# UpperJointData.msg - 上半身关节控制（不含灵巧手 kp/kd）

std_msgs/Header header

float32 time_ref
float32 vel_scale

string[] name
float64[] position
float64[] velocity
float64[] effort
float64[] kp
float64[] kd
