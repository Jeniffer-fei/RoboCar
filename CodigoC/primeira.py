from machine import Pin
from machine import PWM
from time import sleep
import RPi.GPIO as GPIO
import serial


# =============== Função map()===================== 
def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# =============== Função map()=====================


# ================ Classe Servo ====================
class Servo:
    
    # Construtor
    def __init__(self):
        self.FREQ = 50
        self.pulse_min = 2000 # 0º ~ 0.61 ms
        self.pulse_max = 7800 # 180º ~ 2.38 ms
        self.duty = self.pulse_min + (self.pulse_max - self.pulse_min) #90º
    
    # Configura o pino e inicia o PWM a 90º
    def attach(self, pino):
        self.pin = Pin(pino)
        self.pwm = PWM(self.pin)
        self.pwm.freq(self.FREQ)
        self.pwm.duty_u16(self.duty)
    
    # Converte o angulo em pulso
    def convert(self, angulo):
        if angulo <= 0:
            return self.pulse_min
        if angulo >= 180:
            return self.pulse_max
        
        pulso = self.pulse_min + int( (angulo / 180) * (self.pulse_max - self.pulse_min) )
        return pulso
    
    # Recebe o angulo e controla o servo
    def write(self, angulo):
        self.duty = self.convert(angulo)
        self.pwm.duty_u16(self.duty)
        
# ================ Classe Servo ====================

# =============== Configuração  ====================

GPIO.setmode(GPIO.BCM)
IN1_pin = 17
IN2_pin = 27
GPIO.setup(IN1_pin, GPIO.OUT)
GPIO.setup(IN2_pin, GPIO.OUT)
Volante = Servo()
Volante.attach(2) #Angulo inicial 90 e configurado na porta 2
pos = 90

# Configuração da comunicação serial
serial_port = serial.Serial("/dev/ttyUSB0", 9600)  

# =============== Configuração  ====================


# ========= Funções para controlar o motor ==========
def frente():
    GPIO.output(IN1_pin, GPIO.HIGH)
    GPIO.output(IN2_pin, GPIO.LOW)

def re():
    GPIO.output(IN1_pin, GPIO.LOW)
    GPIO.output(IN2_pin, GPIO.HIGH)

def parar():
    GPIO.output(IN1_pin, GPIO.HIGH)
    GPIO.output(IN2_pin, GPIO.HIGH)
# ========= Funções para controlar o motor ==========


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
            pos += 5
            if pos > 180:
                pos = 180
            
        elif comando == 'R':
            pos -= 5
            if pos > 30:
                pos = 30
            
        elif comando == 'G':
            pos += 5
            frente ()
            if pos > 180:
                pos = 180
            
        elif comando == 'I':
            pos -= 5
            frente ()
            if pos > 30:
                pos = 30
            
        elif comando == 'H':
            re ()
            pos += 5
            if pos > 180:
                pos = 180
            
        elif comando == 'J':
            pos -= 5
            re ()
            if pos > 30:
                pos = 30            
    Volante.write(pos)