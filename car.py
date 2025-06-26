import time
import RPi.GPIO as GPIO

class Car:
    def __init__(self, max_speed=100):
        self.state = "SCAN"
        self.speed = 0.0
        self.max_speed = max_speed
        self.last_seen_lane = time.time()
        self.brake_start_time = 0.0
        self.steering_angle = 0.0

        # Pines motores (modo BOARD)
        self.E1, self.M1 = 35, 37
        self.E2, self.M2 = 31, 33

        # Pines sensor distancia (modo BCM)
        self.trig_pin = 40
        self.echo_pin = 38

        # Setup GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.E1, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        GPIO.setup(self.E2, GPIO.OUT)
        GPIO.setup(self.M2, GPIO.OUT)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

        # PWM
        self.pwm1 = GPIO.PWM(self.E1, 10000)
        self.pwm2 = GPIO.PWM(self.E2, 10000)
        self.pwm1.start(0)
        self.pwm2.start(0)

        GPIO.output(self.trig_pin, False)
        time.sleep(0.05)

    def read_distance_sensor(self):
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()
        while GPIO.input(self.echo_pin) == 1:
            end_time = time.time()

        duration = end_time - start_time
        distance_cm = duration * 17150
        distance_m = round((distance_cm + 1.15) / 100.0, 2)
        return distance_m

    def set_speed(self, speed, steering_angle=0.0):
        # Guardamos valores
        self.speed = speed
        self.steering_angle = steering_angle

        # Saturamos y convertimos a PWM
        base_pwm = max(0, min(abs(speed) / self.max_speed * 100, 100))

        # Dirección base: adelante
        dir_left = GPIO.LOW
        dir_right = GPIO.LOW

        # Giro in-place si hay ángulo
        if steering_angle > 15:
            # Gira a la derecha (izquierda adelante, derecha atrás)
            dir_left = GPIO.LOW
            dir_right = GPIO.HIGH
        elif steering_angle < -15:
            # Gira a la izquierda (derecha adelante, izquierda atrás)
            dir_left = GPIO.HIGH
            dir_right = GPIO.LOW

        # Aplicamos
        GPIO.output(self.M1, dir_left)
        GPIO.output(self.M2, dir_right)
        self.pwm1.ChangeDutyCycle(base_pwm)
        self.pwm2.ChangeDutyCycle(base_pwm)

    def stop(self):
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(0)

    def update(self, lane_detected, action_brake_slow=None, action_speed=None, steering_angle=0.0):
        now = time.time()
        distance_sensor = self.read_distance_sensor()

        if action_speed is not None and action_speed != self.max_speed:
            self.max_speed = action_speed
            if self.state in ["CRUISE", "SLOW"]:
                self.set_speed(self.max_speed, steering_angle)

        if distance_sensor < 1.0 or (action_brake_slow == "BRAKE"):
            if self.state != "BRAKE":
                self.state = "BRAKE"
                self.brake_start_time = now
                self.stop()
            else:
                self.stop()
            return self.state, self.speed

        # Si coche esta frenado y ha pasado el tiempo
        # y no tiene nada delante (hubiera entrado en el if previo)
        # poner modo CRUISe y seguir circulando
        
        if self.state == "BRAKE":
            if now - self.brake_start_time >= 2.0:
                self.state = "CRUISE"
                self.set_speed(self.max_speed, steering_angle)
                self.brake_start_time = 0.0
                
            return self.state, self.speed

        if action_brake_slow == "SLOW":
            self.state = "SLOW"
            self.set_speed(self.max_speed * 0.5, steering_angle)
            return self.state, self.speed

        if self.state == "SCAN":
            self.stop()
            if lane_detected:
                self.state = "CRUISE"
                self.set_speed(self.max_speed, steering_angle)

        elif self.state == "CRUISE":
            if not lane_detected:
                if now - self.last_seen_lane > 2:
                    self.state = "SCAN"
                    self.stop()
            else:
                self.last_seen_lane = now
                self.set_speed(self.max_speed, steering_angle)

        elif self.state == "SLOW":
            self.state = "CRUISE"

        return self.state, self.speed

    def cleanup(self):
        self.stop()
        self.pwm1.stop()
        self.pwm2.stop()
        GPIO.cleanup()
