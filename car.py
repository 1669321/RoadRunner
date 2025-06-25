import time
import RPi.GPIO as GPIO

class Car:
    def __init__(self, pwm_pin=18, dir_pin=23, max_speed=100):
        self.state = "SCAN"
        self.speed = 0.0
        self.max_speed = max_speed
        self.last_seen_lane = time.time()

        # Pines GPIO
        self.pwm_pin = pwm_pin
        self.dir_pin = dir_pin

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pwm_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

        # PWM para velocidad
        self.pwm = GPIO.PWM(self.pwm_pin, 100)
        self.pwm.start(0)  # velocidad inicial 0%

        # Dirección adelante (puedes ajustar si es necesario)
        GPIO.output(self.dir_pin, GPIO.HIGH)

    def set_speed_pwm(self, speed):
        duty_cycle = max(0, min(speed / self.max_speed * 100, 100))
        self.pwm.ChangeDutyCycle(duty_cycle)
        self.speed = speed

    def stop(self):
        # Simplemente dejar de acelerar (0% duty cycle)
        self.set_speed_pwm(0)

    def update(self, detections, lane_detected, distance_sensor=None):
        now = time.time()

        # Chequeo sensor: si detecta objeto a menos de 1 metro, frena YA
        if distance_sensor is not None and distance_sensor < 1.0:
            self.state = "BRAKE"
            self.stop()
            return self.state, self.speed

        if self.state == "SCAN":
            self.stop()
            if lane_detected:
                self.state = "CRUISE"
                self.set_speed_pwm(self.max_speed)

        elif self.state == "CRUISE":
            if not lane_detected:
                if now - self.last_seen_lane > 2:
                    self.state = "SCAN"
                    self.stop()
            else:
                self.last_seen_lane = now
            for det in detections:
                if det['class'] == 'stop_sign':
                    self.state = "BRAKE"
                    self.stop()
                    break

        elif self.state == "BRAKE":
            # Solo vuelve a CRUISE si no hay stop_sign ni obstáculo cercano
            if not any(d['class'] == 'stop_sign' for d in detections):
                if distance_sensor is None or distance_sensor >= 1.0:
                    self.state = "CRUISE"
                    self.set_speed_pwm(self.max_speed)

        return self.state, self.speed

    def cleanup(self):
        self.stop()
        self.pwm.stop()
        GPIO.cleanup()
