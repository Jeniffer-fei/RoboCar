import RPi.GPIO as GPIO
import time
import serial

# Configuração dos pinos GPIO
GPIO.setmode(GPIO.BCM)
IN1_pin = 17
IN2_pin = 27
servo_pin = 22
GPIO.setup(IN1_pin, GPIO.OUT)
GPIO.setup(IN2_pin, GPIO.OUT)
GPIO.setup(servo_pin, GPIO.OUT)

# Configuração do servo
servo = GPIO.PWM(servo_pin, 50)  # 50 Hz
servo.start(0)

# Configuração da comunicação serial
serial_port = serial.Serial("/dev/ttyUSB0", 9600)  # Adapte o nome da porta serial

# Funções para controlar o motor
def frente():
    GPIO.output(IN1_pin, GPIO.HIGH)
    GPIO.output(IN2_pin, GPIO.LOW)

def re():
    GPIO.output(IN1_pin, GPIO.LOW)
    GPIO.output(IN2_pin, GPIO.HIGH)

def parar():
    GPIO.output(IN1_pin, GPIO.HIGH)
    GPIO.output(IN2_pin, GPIO.HIGH)

def set_servo_angle(angle):
    duty_cycle = angle / 18. + 2.5
    servo.ChangeDutyCycle(duty_cycle)

# Loop principal
while True:
    if serial_port.in_waiting > 0:
        comando = serial_port.read().decode('utf-8')
        if comando == 'F':
            frente()
        elif comando == 'B':
            re()
        elif comando == 'S':
            parar()
        elif comando == 'L':
            s1 += 5
            if s1 > 180:
                s1 = 180
            
        elif comando == 'R':
            s1 -= 5
            if s1 > 30:
                s1 = 30
            
        elif comando == 'G':
            s1 += 5
            frente
            if s1 > 180:
                s1 = 180
            
        elif comando == 'I':
            s1 -= 5
            frente
            if s1 > 30:
                s1 = 30
            
        elif comando == 'G':
            s1 += 5
            re()
            if s1 > 180:
                s1 = 180
            
        elif comando == 'I':
            s1 -= 5
            re()
            if s1 > 30:
                s1 = 30
            
    set_servo_angle(s1)