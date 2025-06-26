import time

class Car:
    def __init__(self, max_speed=100):
        self.state = "SCAN"
        self.speed = 0.0
        self.max_speed = max_speed
        self.last_seen_lane = time.time()
        self.brake_start_time = None  # Nuevo atributo para control de tiempo de frenado
        self.distance_sensor = 10.0  # valor simulado en metros (lejos)
        self.pwm_duty_cycle = 0  # simulación del PWM (0-100%)
        self.steering_angle = 0.0


    def read_distance_sensor(self):
        # Simplemente devuelve el valor simulado
        return self.distance_sensor

    def set_speed_pwm(self, speed):
        # Limitar speed a max_speed
        speed = max(0, min(speed, self.max_speed))
        # Simula cambio de duty cycle proporcional a speed
        self.pwm_duty_cycle = speed / self.max_speed * 100
        self.speed = speed
        print(f"[SIM] Velocidad ajustada a {self.speed:.2f} (PWM {self.pwm_duty_cycle:.1f}%)")

    def stop(self):
        self.set_speed_pwm(0)
        print("[SIM] Parando el coche")

    def update(self, lane_detected, action_brake_slow=None, action_speed=None):
        now = time.time()
        distance_sensor = self.read_distance_sensor()

        if action_speed is not None and action_speed != self.max_speed:
            print("MODIFICANDO VELOCIDAD", action_speed)
            self.max_speed = action_speed
            if self.state in ["CRUISE", "SLOW"]:
                self.set_speed_pwm(self.max_speed)

        # Prioridad 1: BRAKE inmediato si sensor o acción lo indican
        if distance_sensor < 1.0 or (action_brake_slow == "BRAKE"):
            if self.state != "BRAKE":
                self.state = "BRAKE"
                self.brake_start_time = now  # Guardamos el inicio del freno
                self.stop()
            else:
                # Estamos en BRAKE, revisar si ya pasó el tiempo de stop
                if now - self.brake_start_time >= 2.0:  # 2 segundos de frenado
                    self.state = "CRUISE"
                    self.set_speed_pwm(self.max_speed)
                    self.brake_start_time = None
                else:
                    # Aún frenando, no cambiar estado ni velocidad
                    self.stop()
                    return self.state, self.speed
            return self.state, self.speed

        if action_brake_slow == "SLOW":
            self.state = "SLOW"
            self.set_speed_pwm(self.max_speed * 0.5)
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
                self.set_speed_pwm(self.max_speed)  # Asegurar velocidad constante en CRUISE

        elif self.state == "SLOW":
            self.state = "CRUISE"

        return self.state, self.speed


    def cleanup(self):
        self.stop()
        print("[SIM] Cleanup llamado")
