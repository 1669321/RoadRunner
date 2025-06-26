import time

class Car:
    def __init__(self, max_speed=100):
        self.state = "SCAN"
        self.speed = 0.0
        self.max_speed = max_speed
        self.last_seen_lane = time.time()
        self.brake_start_time = 0.0
        self.distance_sensor = 10.0  # valor simulado en metros
        self.pwm_duty_cycle = 0.0  # % de PWM simulado
        self.steering_angle = 0.0

    def read_distance_sensor(self):
        # Retorna el valor simulado (puedes modificarlo desde fuera)
        return self.distance_sensor

    def set_speed(self, speed, steering_angle=0.0):
        # Guarda valores
        self.speed = max(0.0, min(speed, self.max_speed))  # clamp speed
        self.steering_angle = steering_angle
        self.pwm_duty_cycle = self.speed / self.max_speed * 100
        print(f"[SIM] Velocidad = {self.speed:.2f}, Ángulo = {steering_angle:.2f}°, PWM = {self.pwm_duty_cycle:.1f}%")

    def stop(self):
        self.set_speed(0.0, self.steering_angle)
        print("[SIM] Coche detenido")

    def update(self, lane_detected, action_brake_slow=None, action_speed=None, steering_angle=0.0):
        now = time.time()
        distance_sensor = self.read_distance_sensor()

        if action_speed is not None and action_speed != self.max_speed:
            self.max_speed = action_speed
            if self.state in ["CRUISE", "SLOW"]:
                self.set_speed(self.max_speed, steering_angle)

        # BRAKE state
        if distance_sensor < 1.0 or action_brake_slow == "BRAKE":
            print("BRAKE TIME: ", self.brake_start_time)
            if self.state != "BRAKE":
                self.state = "BRAKE"
                self.brake_start_time = now
                self.stop()
            elif now - self.brake_start_time >= 2.0:
                self.state = "CRUISE"
                self.set_speed(self.max_speed, steering_angle)
                self.brake_start_time = 0.0
            else:
                self.stop()
            return self.state, self.speed

        if self.state == "BRAKE":
            if now - self.brake_start_time >= 2.0:
                self.state = "CRUISE"
                self.set_speed(self.max_speed, steering_angle)
                self.brake_start_time = 0.0
                
            return self.state, self.speed

        # SLOW state
        if action_brake_slow == "SLOW":
            self.state = "SLOW"
            self.set_speed(self.max_speed * 0.5, steering_angle)
            return self.state, self.speed

        # SCAN → CRUISE
        if self.state == "SCAN":
            self.stop()
            if lane_detected:
                self.state = "CRUISE"
                self.set_speed(self.max_speed, steering_angle)

        # CRUISE behavior
        elif self.state == "CRUISE":
            if not lane_detected:
                if now - self.last_seen_lane > 2.0:
                    self.state = "SCAN"
                    self.stop()
            else:
                self.last_seen_lane = now
                self.set_speed(self.max_speed, steering_angle)

        # SLOW → CRUISE
        elif self.state == "SLOW":
            self.state = "CRUISE"

        return self.state, self.speed

    def cleanup(self):
        self.stop()
        print("[SIM] Cleanup ejecutado")
