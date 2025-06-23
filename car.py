import time

class Car:
    def __init__(self):
        self.state = "SCAN"
        self.speed = 0.0
        self.max_speed = 1.0
        self.last_seen_lane = time.time()

    def update(self, detections, lane_detected):
        now = time.time()

        if self.state == "SCAN":
            if lane_detected:
                self.state = "CRUISE"
                self.speed = self.max_speed

        elif self.state == "CRUISE":
            if not lane_detected:
                if now - self.last_seen_lane > 2:
                    self.state = "SCAN"
                    self.speed = 0
            else:
                self.last_seen_lane = now
            for det in detections:
                if det['class'] == 'stop_sign':
                    self.state = "BRAKE"
                    self.speed = 0
                    break

        elif self.state == "BRAKE":
            if not any(d['class'] == 'stop_sign' for d in detections):
                self.state = "CRUISE"
                self.speed = self.max_speed

        return self.state, self.speed
