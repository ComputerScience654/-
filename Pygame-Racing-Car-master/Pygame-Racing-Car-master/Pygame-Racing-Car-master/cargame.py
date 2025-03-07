import pygame  # นำเข้าไลบรารี Pygame สำหรับการพัฒนาเกม
import random  # นำเข้าไลบรารี Random สำหรับการสุ่มค่า
from sys import exit as sys_exit  # นำเข้า exit จาก sys และตั้งชื่อใหม่เป็น sys_exit

# TODO: Add sound effect, trees graphics
# TODO: Make the movement of the dashed line smoothly transition when level up

pygame.init()  # เริ่มต้น Pygame

pygame.mixer.init()  # เริ่มต้น Pygame Mixer สำหรับการเล่นเสียง

# ใส่เพลง
pygame.mixer.music.load("assets/videoplayback.wav")
pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

class Game:
    FPS = 60  # กำหนดค่า FPS (Frames Per Second) ของเกม

    def __init__(self):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 660  # กำหนดขนาดหน้าจอ
        self.road_w = self.SCREEN_WIDTH // 1.6  # กำหนดความกว้างของถนน
        self.roadmark_w = self.SCREEN_WIDTH // 80  # กำหนดความกว้างของเส้นถนน
        self.leftmost_lane = self.SCREEN_WIDTH / 2 - self.road_w / 2 + self.road_w / 8  # กำหนดตำแหน่งเลนซ้ายสุด
        self.left_lane = self.SCREEN_WIDTH / 2 - self.road_w / 4  # กำหนดตำแหน่งเลนซ้าย
        self.right_lane = self.SCREEN_WIDTH / 2 + self.road_w / 4  # กำหนดตำแหน่งเลนขวา
        self.rightmost_lane = self.SCREEN_WIDTH / 2 + self.road_w / 2 - self.road_w / 8  # กำหนดตำแหน่งเลนขวาสุด
        self.speed = 3  # กำหนดความเร็วเริ่มต้นของรถ
        self.speed_factor = self.SCREEN_HEIGHT / 660  # กำหนดตัวคูณความเร็วของรถศัตรู
        self.car_lane = "R"  # กำหนดเลนเริ่มต้นของรถผู้เล่น
        self.car2_lane = "L"  # กำหนดเลนเริ่มต้นของรถศัตรู

        self.GRASS_COLOR = (60, 220, 0)  # กำหนดสีของหญ้า
        self.DARK_ROAD_COLOR = (50, 50, 50)  # กำหนดสีของถนน
        self.YELLOW_LINE_COLOR = (255, 240, 60)  # กำหนดสีของเส้นเหลือง
        self.WHITE_LINE_COLOR = (255, 255, 255)  # กำหนดสีของเส้นขาว

        self.score = 0  # กำหนดคะแนนเริ่มต้น
        self.level = 0  # กำหนดระดับเริ่มต้น

        self.CLOCK = pygame.time.Clock()  # สร้างนาฬิกา Pygame
        self.event_updater_counter = 0  # ตัวนับสำหรับการอัพเดตเหตุการณ์

        self.SCREEN = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE
        )  # สร้างหน้าจอเกม

        pygame.display.set_caption("2D Car Game")  # ตั้งชื่อหน้าต่างเกม

        self.game_over_font = pygame.font.SysFont("Arial", 60)  # กำหนดฟอนต์สำหรับข้อความเกมโอเวอร์
        self.score_font = pygame.font.Font("assets/fonts/joystix monospace.otf", 30)  # กำหนดฟอนต์สำหรับคะแนน
        self.game_info_font = pygame.font.SysFont("Arial", 40)  # กำหนดฟอนต์สำหรับข้อมูลเกม

        # โหลดเสียงเอฟเฟกต์
        self.car_crash_sound = pygame.mixer.Sound("assets/carCrash.wav")

        # โหลดรูปภาพรถผู้เล่น
        self.original_car = pygame.image.load("assets/cars/car.png")
        self.car = pygame.transform.scale(
            self.original_car,
            (
                int(self.original_car.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_car.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.car_loc = self.car.get_rect()
        self.car_loc.center = (
            self.right_lane,
            self.SCREEN_HEIGHT - self.car_loc.height * 0.5,
        )

        # โหลดรูปภาพรถศัตรู
        self.original_car2 = pygame.image.load("assets/cars/otherCar.png")
        self.car2 = pygame.transform.scale(
            self.original_car2,
            (
                int(self.original_car2.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_car2.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.car2_loc = self.car2.get_rect()
        self.car2_loc.center = self.left_lane, self.SCREEN_HEIGHT * 0.2

        self.scale = self.SCREEN_HEIGHT - self.car2_loc.height

        self.game_state = "MAIN GAME"  # กำหนดสถานะเริ่มต้นของเกม
        self.game_paused = False  # กำหนดสถานะการหยุดเกมเริ่มต้น

        self.has_update_scores = False  # กำหนดสถานะการอัพเดตคะแนนสูงสุด
        self.scores = []  # สร้างลิสต์สำหรับเก็บคะแนนสูงสุด
        self.names = []  # สร้างลิสต์สำหรับเก็บชื่อผู้เล่น

    def main_loop(self):
        while True:
            if self.game_paused:
                self.game_paused_draw()
                self.game_info_draw()
                self.CLOCK.tick(10)
                pygame.display.update()
                self.handle_critical_events()
                continue

            self.event_loop()
            self.event_updater_counter += 1

            if (
                self.event_updater_counter > self.SCREEN_HEIGHT
            ):  # รีเซ็ตตัวนับเมื่อเกินความสูงของหน้าจอ
                self.event_updater_counter = 0

            if self.game_state == "GAME OVER":
                self.game_over_draw()
                self.CLOCK.tick(self.FPS)
                pygame.display.update()
                continue

            # เพิ่มความเร็วและระดับเมื่อคะแนนเกิน 5000
            if self.score % 5000 == 0:
                self.speed += 0.16
                self.level += 1
                print("Level Up!")

            self.car2_loc[1] += (
                self.speed * self.speed_factor
            )  # เพิ่มความเร็วให้กับรถศัตรู

            # เปลี่ยนตำแหน่งรถศัตรูเมื่อออกจากหน้าจอ
            if self.car2_loc[1] > self.SCREEN_HEIGHT:
                lane_choice = random.randint(0, 3)
                if lane_choice == 0:
                    self.car2_loc.center = self.leftmost_lane, -200
                    self.car2_lane = "LM"
                elif lane_choice == 1:
                    self.car2_loc.center = self.left_lane, -200
                    self.car2_lane = "L"
                elif lane_choice == 2:
                    self.car2_loc.center = self.right_lane, -200
                    self.car2_lane = "R"
                else:
                    self.car2_loc.center = self.rightmost_lane, -200
                    self.car2_lane = "RM"

            # ตรวจสอบการชนกันของรถ
            if self.car2_loc.colliderect(self.car_loc):
                self.car_crash_sound.play()
                self.game_state = "GAME OVER"

            self.draw(self.event_updater_counter)
            self.display_score()

            self.score += 1

            self.CLOCK.tick(self.FPS)
            pygame.display.update()

    def handle_critical_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game_paused = False

    def event_loop(self):
        for event in pygame.event.get():  # วนลูปเหตุการณ์
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    if self.car_lane == "RM":
                        self.car_loc = self.car_loc.move([-int(self.road_w / 4), 0])
                        self.car_lane = "R"
                    elif self.car_lane == "R":
                        self.car_loc = self.car_loc.move([-int(self.road_w / 4), 0])
                        self.car_lane = "L"
                    elif self.car_lane == "L":
                        self.car_loc = self.car_loc.move([-int(self.road_w / 4), 0])
                        self.car_lane = "LM"
                if event.key in [pygame.K_d, pygame.K_RIGHT]:
                    if self.car_lane == "LM":
                        self.car_loc = self.car_loc.move([int(self.road_w / 4), 0])
                        self.car_lane = "L"
                    elif self.car_lane == "L":
                        self.car_loc = self.car_loc.move([int(self.road_w / 4), 0])
                        self.car_lane = "R"
                    elif self.car_lane == "R":
                        self.car_loc = self.car_loc.move([int(self.road_w / 4), 0])
                        self.car_lane = "RM"
                if event.key in [pygame.K_w, pygame.K_UP]:
                    self.speed = self.speed + 5
                if event.key in [pygame.K_SPACE, pygame.K_r] and self.game_state == "GAME OVER":
                    self.restart_game()
                if event.key in [pygame.K_SPACE]:
                    if not self.game_paused:
                        self.game_paused = True
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    self.quit_game()
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_UP]:
                    self.speed = self.speed - 5
            if event.type == pygame.VIDEORESIZE:
                self.SCREEN_WIDTH, self.SCREEN_HEIGHT = event.w, event.h
                self.SCREEN = pygame.display.set_mode(
                    (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE
                )

                # อัพเดตตำแหน่งเลน
                self.road_w = int(self.SCREEN_WIDTH / 1.6)
                self.leftmost_lane = self.SCREEN_WIDTH / 2 - self.road_w / 2 + self.road_w / 8
                self.left_lane = self.SCREEN_WIDTH / 2 - self.road_w / 4
                self.right_lane = self.SCREEN_WIDTH / 2 + self.road_w / 4
                self.rightmost_lane = self.SCREEN_WIDTH / 2 + self.road_w / 2 - self.road_w / 8

                # ปรับขนาดรูปภาพรถใหม่
                self.car = pygame.transform.scale(
                    self.original_car,
                    (
                        int(self.original_car.get_width() * (self.SCREEN_WIDTH / 800)),
                        int(
                            self.original_car.get_height() * (self.SCREEN_HEIGHT / 600)
                        ),
                    ),
                )
                self.car2 = pygame.transform.scale(
                    self.original_car2,
                    (
                        int(self.original_car2.get_width() * (self.SCREEN_WIDTH / 800)),
                        int(
                            self.original_car2.get_height() * (self.SCREEN_HEIGHT / 600)
                        ),
                    ),
                )

                # อัพเดตตำแหน่งรถตามตำแหน่งเลนที่อัพเดต
                if self.car_lane == "RM":
                    self.car_loc = self.car.get_rect(
                        center=(self.rightmost_lane, self.SCREEN_HEIGHT * 0.8)
                    )
                elif self.car_lane == "R":
                    self.car_loc = self.car.get_rect(
                        center=(self.right_lane, self.SCREEN_HEIGHT * 0.8)
                    )
                elif self.car_lane == "L":
                    self.car_loc = self.car.get_rect(
                        center=(self.left_lane, self.SCREEN_HEIGHT * 0.8)
                    )
                else:
                    self.car_loc = self.car.get_rect(
                        center=(self.leftmost_lane, self.SCREEN_HEIGHT * 0.8)
                    )

                if self.car2_lane == "RM":
                    self.car2_loc = self.car2.get_rect(
                        center=(self.rightmost_lane, self.car2_loc.center[1])
                    )
                elif self.car2_lane == "R":
                    self.car2_loc = self.car2.get_rect(
                        center=(self.right_lane, self.car2_loc.center[1])
                    )
                elif self.car2_lane == "L":
                    self.car2_loc = self.car2.get_rect(
                        center=(self.left_lane, self.car2_loc.center[1])
                    )

                else:
                    self.car2_loc = self.car2.get_rect(
                        center=(self.leftmost_lane, self.car2_loc.center[1])
                    )

    def draw(self, event_updater_counter):
        """
        ฟังก์ชันนี้ใช้วาดพื้นหลังของเกมและอัพเดตพื้นหลังเมื่อมีการปรับขนาด
        สำหรับการเคลื่อนที่ของเส้นประสีเหลืองบนถนน จะมีการวาดหลาย rect
        และเคลื่อนที่ด้วยตัวแปร event_updater_counter
        เมื่อ event_update_counter ถึง 30 rects จะถูกรีเซ็ตไปยังตำแหน่งเดิม
        """

        # วาดถนนสีดำบนหน้าจอสีเขียว
        self.SCREEN.fill(self.GRASS_COLOR)

        pygame.draw.rect(
            self.SCREEN,
            self.DARK_ROAD_COLOR,
            (
                self.SCREEN_WIDTH / 2 - self.road_w / 2,
                0,
                self.road_w,
                self.SCREEN_HEIGHT,
            ),
        )

        # วาดเส้นประสีเหลืองบนถนนสีดำ
        num_yellow_lines = 11  # 10 + 1 เคลื่อนที่ในขอบของหน้าจอ
        # event_updater_counter ใช้ในการเคลื่อนที่ของเส้นประสีเหลือง
        line_positions = [
            (
                self.SCREEN_WIDTH / 2 - self.roadmark_w / 2,
                # ระวังการเปลี่ยนค่านี้ อาจทำให้เส้นไม่ถูกวาดอย่างถูกต้อง
                # ความเร็วของเส้นคือ 75% ของความเร็วรถศัตรู
                int(
                    (self.SCREEN_HEIGHT / 20
                    + 2 * self.SCREEN_HEIGHT / 20 * num_line
                    + self.speed * self.speed_factor * event_updater_counter * 0.75)
                    % self.SCREEN_HEIGHT / 10 * 11
                    - self.SCREEN_HEIGHT / 20
                ),
                self.roadmark_w,
                self.SCREEN_HEIGHT / 20,
            )
            for num_line in range(num_yellow_lines)
        ]

        for line_position in line_positions:
            pygame.draw.rect(
                self.SCREEN,
                self.YELLOW_LINE_COLOR,
                line_position,
            )

        # วาดเส้นสีขาวด้านซ้ายของถนน
        pygame.draw.rect(
            self.SCREEN,
            self.WHITE_LINE_COLOR,
            (
                self.SCREEN_WIDTH / 2 - self.road_w / 2 + self.roadmark_w * 2,
                0,
                self.roadmark_w,
                self.SCREEN_HEIGHT,
            ),
        )
        # วาดเส้นสีขาวด้านขวาของถนน
        pygame.draw.rect(
            self.SCREEN,
            (255, 255, 255),
            (
                self.SCREEN_WIDTH / 2 + self.road_w / 2 - self.roadmark_w * 3,
                0,
                self.roadmark_w,
                self.SCREEN_HEIGHT,
            ),
        )

        # โหลดรถบนถนน
        self.SCREEN.blit(self.car, self.car_loc)
        self.SCREEN.blit(self.car2, self.car2_loc)

    def display_score(self):
        self.message_display(
            "SCORE ",
            self.score_font,
            (255, 50, 50),
            self.right_lane + self.road_w / 2.5,
            20,
        )
        self.message_display(
            self.score,
            self.score_font,
            (255, 50, 50),
            self.right_lane + self.road_w / 2.5,
            55,
        )

    def game_over_draw(self):
        self.SCREEN.fill((200, 200, 200))
        self.message_display(
            "GAME OVER!", self.game_over_font, (40, 40, 40), self.SCREEN_WIDTH / 2, 330
        )
        self.message_display(
            "FINAL SCORE ",
            self.score_font,
            (80, 80, 80),
            self.SCREEN_WIDTH / 2 - 50,
            230,
        )
        self.message_display(
            self.score, self.score_font, (80, 80, 80), self.SCREEN_WIDTH / 2 + 150, 230
        )

        if not self.has_update_scores:
            # อ่านคะแนนสูงสุดจากไฟล์ txt ซึ่งอยู่ในรูปแบบของตัวเลขที่คั่นด้วยช่องว่าง
            with open("high_scores.txt", "r") as hs_file:
                high_scores = hs_file.read()
                hs_file.close()

            # แปลงข้อมูลคะแนนสูงสุดเป็นลิสต์ของตัวเลขและเพิ่มคะแนนใหม่ลงในข้อมูล
            high_scores = high_scores.split()
            self.scores = [int(high_scores[i]) for i in range(0, len(high_scores), 2)]
            self.names = [high_scores[i] for i in range(1, len(high_scores), 2)]
            self.scores.append(self.score)
            self.names.append(self.get_player_name())

            # เรียงลำดับจากมากไปน้อย แล้วเก็บเฉพาะคะแนนสูงสุด 5 อันดับแรก
            combined_scores = list(zip(self.scores, self.names))
            combined_scores.sort(reverse=True, key=lambda x: x[0])
            combined_scores = combined_scores[:5]
            self.scores, self.names = zip(*combined_scores)

            # จัดรูปแบบคะแนน
            self.scores = self.pad_scores(self.scores) # เติมเลขศูนย์ให้คะแนนแต่ละคะแนนเพื่อให้มีจำนวนหลักเท่ากัน

            # เขียนไฟล์คะแนนสูงสุดใหม่ด้วยคะแนนสูงสุดที่อัพเดต
            with open("high_scores.txt", "w") as hs_file:
                hs_file.write(" ".join([f"{self.scores[i]} {self.names[i]}" for i in range(len(self.scores))])) # เขียนคะแนนสูงสุดลงในไฟล์

            self.has_update_scores = True

        # แสดงคะแนนสูงสุด 5 อันดับแรก
        self.message_display(
            "HIGH SCORES", self.score_font, (100, 100, 100), self.SCREEN_WIDTH / 2, 410
        )

        for idx, (score, name) in enumerate(zip(self.scores, self.names)):
            self.message_display(
                f"{idx + 1}. {score} {name}",
                self.score_font,
                (100, 100, 100),
                self.SCREEN_WIDTH / 2,
                410 + ((idx + 1) * 30),
            ) # แสดงคะแนนสูงสุดแต่ละอันดับบนหน้าจอ
        
        self.message_display(
            "(Space to restart)", self.score_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 600
        ) # แสดงข้อความ "(Space to restart)" บนหน้าจอ

    def game_paused_draw(self):
        self.message_display(
            "PAUSED", self.game_over_font, (0, 0, 100), self.SCREEN_WIDTH / 2, 200
        ) # แสดงข้อความ "PAUSED" บนหน้าจอเมื่อเกมหยุดชั่วคราว

    def game_info_draw(self):
        pygame.draw.rect(self.SCREEN, (0, 0, 0), [self.SCREEN_WIDTH/4 - 3, self.SCREEN_HEIGHT/4 + 65 - 3, self.SCREEN_WIDTH/2 + 6, 300 + 6])
        pygame.draw.rect(self.SCREEN, (200, 200, 200), [self.SCREEN_WIDTH/4, self.SCREEN_HEIGHT/4 + 65, self.SCREEN_WIDTH/2, 300])
        self.message_display(
            "Controls", self.game_info_font, (40, 40, 40), self.SCREEN_WIDTH / 2, 250
        ) # แสดงข้อความ "Controls" บนหน้าจอ
        self.message_display(
            "Left:                 A or \u2190", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 300,
        ) # แสดงข้อความ "Left: A or ←" บนหน้าจอ
        self.message_display(
            "Right:              D or \u2192", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 350,
        ) # แสดงข้อความ "Right: D or →" บนหน้าจอ
        self.message_display(
            "Speed Up:         W or \u2191", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 400,
        ) # แสดงข้อความ "Speed Up: W or ↑" บนหน้าจอ
        self.message_display(
            "Pause:        Space Bar", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 450,
        ) # แสดงข้อความ "Pause: Space Bar" บนหน้าจอ
        self.message_display(
            "Exit:              Q or ESC", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 500,
        ) 

    def restart_game(self):
        self.score = 0 # รีเซ็ตคะแนนเป็น 0
        self.level = 0 # รีเซ็ตระดับเป็น 0
        self.speed = 3 # รีเซ็ตความเร็วเป็น 3
        self.event_updater_counter = 0 # รีเซ็ตตัวนับเหตุการณ์เป็น 0
        self.game_state = "MAIN GAME" # ตั้งค่าสถานะเกมเป็น "MAIN GAME"
        self.has_update_scores = False # ตั้งค่าสถานะการอัพเดตคะแนนสูงสุดเป็น False
        self.scores = [] # ล้างลิสต์คะแนนสูงสุด
        self.car_loc.center = (
            self.right_lane,
            self.SCREEN_HEIGHT - self.car_loc.height * 0.5,
        ) # ตั้งค่าตำแหน่งเริ่มต้นของรถผู้เล่น
        self.car2_loc = self.car2.get_rect()
        self.car2_loc.center = (self.left_lane, self.SCREEN_HEIGHT * 0.2) # ตั้งค่าตำแหน่งเริ่มต้นของรถศัตรู
        self.car_lane = "R" # ตั้งค่าเลนของรถผู้เล่นเป็นเลนขวา
        self.car2_lane = "L" # ตั้งค่าเลนของรถศัตรูเป็นเลนซ้าย
        print("Restart!") # แสดงข้อความ "Restart!" ในคอนโซล

    @staticmethod
    def quit_game():
        sys_exit() # ออกจากโปรแกรม
        quit() # ออกจากโปรแกรม

    def message_display(self, text, font, text_col, x, y, center=True):
        """
        This is a function which displays text with the desired specifications

        param: text: This is the Text to display
        type: str

        param: font: The font that will be used
        type: Font

        param: text_col: The color that the text will be in (R, G, B) format
        type: tuple

        param: x: The x coordinate of the text
        type: int

        param: y: The y coordinate of the text
        type: int

        param: center: Determines if the text is centered
        type: bool
        """
        img = font.render(str(text), True, text_col) # สร้างภาพของข้อความด้วยฟอนต์และสีที่กำหนด
        img = img.convert_alpha() # แปลงภาพให้มีช่องอัลฟา (ความโปร่งใส)

        if center: # ถ้าต้องการให้ข้อความอยู่กึ่งกลาง
            # Adjust x and y to center the text
            x -= img.get_width() / 2 # ปรับตำแหน่ง x ให้ข้อความอยู่กึ่งกลาง
            y -= img.get_height() / 2 # ปรับตำแหน่ง y ให้ข้อความอยู่กึ่งกลาง

        self.SCREEN.blit(img, (x, y)) # วาดภาพข้อความบนหน้าจอที่ตำแหน่งที่กำหนด

    # padding zeroes for high scores to have same digits for alignment
    @staticmethod
    def pad_scores(scores):
        """
        :param: scores : high scores in descending order
        :type: list

        :return: high scores in padded format
        :type: list
        """
        length_of_highest_score = len(str(scores[0])) # หาความยาวของคะแนนสูงสุด
        scores_padded = [str(score).zfill(length_of_highest_score) for score in scores] # เติมเลขศูนย์ให้คะแนนแต่ละคะแนน
        return scores_padded # คืนค่าคะแนนที่เติมเลขศูนย์แล้ว

    def get_player_name(self):
        """
        ฟังก์ชันนี้ใช้รับชื่อผู้เล่นจากผู้ใช้
        """
        name = ""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return name
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
                elif event.type == pygame.QUIT:
                    self.quit_game()
            self.SCREEN.fill((200, 200, 200))
            self.message_display(
                "Enter your name: " + name,
                self.game_info_font,
                (40, 40, 40),
                self.SCREEN_WIDTH / 2,
                self.SCREEN_HEIGHT / 2,
            )
            pygame.display.update()

if __name__ == "__main__":

    game = Game() # สร้างอินสแตนซ์ของคลาส Game

    game.main_loop()

