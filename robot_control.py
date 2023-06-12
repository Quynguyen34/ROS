#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float64
import RPi.GPIO as GPIO
import spidev

SPI_SPEED_HZ = 10000000
SPI_DEVICE = 0
SPI_CS_PIN = 8

UP = 22
DOWN = 5
LEFT = 6
RIGHT = 13

turn_on = 19
turn_off = 26

auto = 20
manuel = 21

led1 = 12
led2 = 16
# Khởi tạo biến msg_left và msg_right từ thông điệp Float64
msg_left = Float64()
msg_right = Float64()

# Mảng chứa dữ liệu để hiển thị các biểu tượng trên LED
DUNG = [0x00, 0x00, 0x24, 0x7E, 0x7E, 0x24, 0x00, 0x00]
LEN = [0x08, 0x0c, 0xfe, 0xff, 0xff, 0xfe, 0x0c, 0x08]
XUONG = [0x10, 0x30, 0x7f, 0xff, 0xff, 0x7f, 0x30, 0x10]
PHAI = [0x18, 0x3c, 0x7e, 0xff, 0x3c, 0x3c, 0x3c, 0x3c]
TRAI = [0x3c, 0x3c, 0x3c, 0x3c, 0xff, 0x7e, 0x3c, 0x18]

# Khởi tạo đối tượng SPI
spi = spidev.SpiDev()
spi.open(SPI_DEVICE, 0)
spi.max_speed_hz = SPI_SPEED_HZ
spi.mode = 0b00

# Hàm gửi dữ liệu qua SPI
def send_data(address, data):
    spi.xfer2([address, data])

# Gửi dữ liệu để khởi tạo LED
send_data(0x09, 0x00)
send_data(0x0A, 0x09)
send_data(0x0A, 0x01)
send_data(0x0B, 0x07)
send_data(0x0C, 0x01)
send_data(0x0F, 0x00)

# Thiết lập chế độ chân GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(UP, GPIO.IN)
GPIO.setup(DOWN, GPIO.IN)
GPIO.setup(LEFT, GPIO.IN)
GPIO.setup(RIGHT, GPIO.IN)
GPIO.setup(turn_on, GPIO.IN)
GPIO.setup(turn_off, GPIO.IN)
GPIO.setup(auto, GPIO.IN)
GPIO.setup(manuel, GPIO.IN)
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)

# Biến để theo dõi trạng thái chương trình
program_active = False
auto_mode = False

# Thiết lập callback cho các nút bấm
def button_callback_up(channel):
    if program_active:
        # Khởi tạo lại biến msg_left và msg_right
        msg_left = Float64()
        msg_right = Float64()
        state = not GPIO.input(channel)
        if state:
            # Đặt giá trị tốc độ trái và phải
            msg_left.data = 7.0
            msg_right.data = -7.0
            left_publisher.publish(msg_left)
            right_publisher.publish(msg_right)
            rospy.loginfo("Button UP")
            # Gửi dữ liệu để hiển thị biểu tượng di chuyển lên
            for j in range(8):
                send_data(j + 1, LEN[7 - j])
        else:
            # Đặt giá trị tốc độ trái và phải về 0
            msg_left.data = 0.0
            msg_right.data = 0.0
            left_publisher.publish(msg_left)
            right_publisher.publish(msg_right)
            rospy.loginfo("STOP")
            # Gửi dữ liệu để hiển thị biểu tượng dừng
            for j in range(8):
                send_data(j + 1, DUNG[7 - j])

def button_callback_down(channel):
    if program_active:
        msg_left = Float64()
        msg_right = Float64()
        state = not GPIO.input(channel)
        if state:
            msg_left.data = -8.0
            msg_right.data = 8.0
            left_publisher.publish(msg_left)
            right_publisher.publish(msg_right)
            rospy.loginfo("Button DOWN")
            for j in range(8):
                send_data(j + 1, XUONG[7 - j])
        else:
            msg_left.data = 0.0
            msg_right.data = 0.0
            left_publisher.publish(msg_left)
            right_publisher.publish(msg_right)
            rospy.loginfo("STOP")
            for j in range(8):
                send_data(j + 1, DUNG[7 - j])

def button_callback_left(channel):
    if program_active:
        msg_left = Float64()
        msg_right = Float64()
        state = not GPIO.input(channel)
        if state:
            msg_left.data = 3.0
            msg_right.data = -7.0
            left_publisher.publish(msg_left)
            right_publisher.publish(msg_right)
            rospy.loginfo("Button LEFT")
            for j in range(8):
                send_data(j + 1, TRAI[7 - j])
        else:
            msg_left.data = 0.0
            msg_right.data = 0.0
            left_publisher.publish(msg_left)
            right_publisher.publish(msg_right)
            rospy.loginfo("STOP")
            for j in range(8):
                send_data(j + 1, DUNG[7 - j])

def button_callback_right(channel):
    if program_active:
        msg_left = Float64()
        msg_right = Float64()
        state = not GPIO.input(channel)
        if state:
            msg_left.data = 7.0
            msg_right.data = -3.0
            left_publisher.publish(msg_left)
            right_publisher.publish(msg_right)
            rospy.loginfo("Button RIGHT")
            for j in range(8):
                send_data(j + 1, PHAI[7 - j])
        else:
            msg_left.data = 0.0
            msg_right.data = 0.0
            left_publisher.publish(msg_left)
            right_publisher.publish(msg_right)
            rospy.loginfo("STOP")
            for j in range(8):
                send_data(j + 1, DUNG[7 - j])

def button_callback_turn_on(channel):
    global program_active
    if not program_active:
        program_active = True
        rospy.loginfo("MỞ BỘ ĐIỀU KHIỂN")
        # Thêm code để đảm bảo LED 1 sáng và LED 2 tắt
        GPIO.output(led1, GPIO.HIGH)
        GPIO.output(led2, GPIO.LOW)

def button_callback_turn_off(channel):
    global program_active
    if program_active:
        program_active = False
        rospy.loginfo("TẮT BỘ ĐIỀU KHIỂN")
        # Thêm code để đảm bảo LED 2 sáng và LED 1 tắt
        GPIO.output(led1, GPIO.LOW)
        GPIO.output(led2, GPIO.HIGH)

# Thiết lập callback cho sự kiện nhấn nút
GPIO.add_event_detect(UP, GPIO.BOTH, callback=button_callback_up)
GPIO.add_event_detect(DOWN, GPIO.BOTH, callback=button_callback_down)
GPIO.add_event_detect(LEFT, GPIO.BOTH, callback=button_callback_left)
GPIO.add_event_detect(RIGHT, GPIO.BOTH, callback=button_callback_right)
GPIO.add_event_detect(turn_on, GPIO.FALLING, callback=button_callback_turn_on)
GPIO.add_event_detect(turn_off, GPIO.FALLING, callback=button_callback_turn_off)

# Khởi tạo node "publish"
rospy.init_node('publish')
left_publisher = rospy.Publisher('/my_diffbot/joint1_Velocity_controller/command', Float64, queue_size=10)
right_publisher = rospy.Publisher('/my_diffbot/joint2_Velocity_controller/command', Float64, queue_size=10)

rospy.spin()
