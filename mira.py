import cv2
import mediapipe as mp
import math
import time
import serial
import sys
import threading  # <<< IMPORTANTE

# --- Constantes e Variáveis Globais ---
FONT = cv2.FONT_HERSHEY_SIMPLEX

mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.8)

# Mira
mira_x_prev = None
mira_y_prev = None
alpha = 0.15

tempo_inicio_fechada = None
disparar = False

# Comunicação serial
arduino = None
try:
    arduino = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2)
    print("Conexão com Arduino estabelecida.")
except serial.SerialException as e:
    print(f"Erro ao conectar ao Arduino: {e}")
    print("A mira funcionará, mas sem controle do Arduino.")

# Variáveis compartilhadas com a thread
angulo_x_global = 90
angulo_y_global = 90
lock = threading.Lock()

# --- Thread para envio dos ângulos suavizados ao Arduino ---
def enviar_para_arduino_thread():
    global angulo_x_global, angulo_y_global
    while True:
        if arduino and arduino.is_open:
            try:
                with lock:
                    msg = f"{angulo_x_global},{angulo_y_global}\n"
                arduino.write(msg.encode())
                resposta = arduino.readline().decode().strip()
                print("Arduino respondeu:", resposta)
            except serial.SerialException as e:
                print(f"Erro ao enviar dados ao Arduino: {e}")
        time.sleep(0.05)  # Delay de 50 ms entre envios

# Inicia a thread após conectar
if arduino and arduino.is_open:
    thread_arduino = threading.Thread(target=enviar_para_arduino_thread, daemon=True)
    thread_arduino.start()

# --- Funções auxiliares ---
def distancia(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def calcular_angulo(a, b, c):
    ab = [a.x - b.x, a.y - b.y]
    cb = [c.x - b.x, c.y - b.y]
    dot = ab[0] * cb[0] + ab[1] * cb[1]
    norm_ab = math.hypot(*ab)
    norm_cb = math.hypot(*cb)
    if norm_ab * norm_cb == 0:
        return 180.0
    angle = math.acos(dot / (norm_ab * norm_cb))
    return math.degrees(angle)

def mao_direita_fechada(landmarks):
    punho = landmarks[0]
    dedos_tips = [8, 12, 16, 20]
    dedos_fechados = 0
    for tip_id in dedos_tips:
        ponta = landmarks[tip_id]
        dist = distancia(punho, ponta)
        if dist < 0.2:
            dedos_fechados += 1
    return dedos_fechados >= 4

# --- Função principal ---
def rodar_mira_jogo(frame_input, video_width, video_height):
    global mira_x_prev, mira_y_prev, tempo_inicio_fechada, disparar, angulo_x_global, angulo_y_global

    image = cv2.flip(frame_input.copy(), 1)
    image = cv2.resize(image, (video_width, video_height))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pose_results = pose.process(image_rgb)
    hands_results = hands.process(image_rgb)

    h, w, _ = image.shape

    angulo_x = 90
    angulo_y = 90
    disparar_status_text = "PRONTO"

    if pose_results.pose_landmarks:
        lms = pose_results.pose_landmarks.landmark

        try:
            ombro = lms[mp_pose.PoseLandmark.LEFT_SHOULDER]
            cotovelo = lms[mp_pose.PoseLandmark.LEFT_ELBOW]
            punho = lms[mp_pose.PoseLandmark.LEFT_WRIST]

            angulo = calcular_angulo(ombro, cotovelo, punho)

            ombro_p = (int(ombro.x * w), int(ombro.y * h))
            cotovelo_p = (int(cotovelo.x * w), int(cotovelo.y * h))
            punho_p = (int(punho.x * w), int(punho.y * h))

            cv2.line(image, ombro_p, cotovelo_p, (255, 255, 0), 3)
            cv2.line(image, punho_p, cotovelo_p, (0, 255, 255), 3)
            cv2.circle(image, cotovelo_p, 6, (0, 0, 255), -1)

            dx = punho.x - cotovelo.x
            dy = punho.y - cotovelo.y
            norm = math.hypot(dx, dy)
            if norm != 0:
                dx /= norm
                dy /= norm

            cx, cy = int(cotovelo.x * w), int(cotovelo.y * h)
            t = 1000
            proj_x = int(cx + dx * t)
            proj_y = int(cy + dy * t)

            mira_x = max(0, min(w - 1, proj_x))
            mira_y = max(0, min(h - 1, proj_y))

            if mira_x_prev is None:
                mira_x_prev, mira_y_prev = mira_x, mira_y
            else:
                mira_x_prev = int((1 - alpha) * mira_x_prev + alpha * mira_x)
                mira_y_prev = int((1 - alpha) * mira_y_prev + alpha * mira_y)

            cv2.circle(image, (mira_x_prev, mira_y_prev), 20, (0, 0, 255), -1)
            cv2.line(image, cotovelo_p, (mira_x_prev, mira_y_prev), (0, 0, 255), 2)
            cv2.line(image, (0, h // 2), (w, h // 2), (100, 100, 100), 1)

            def mapear_para_servo(valor, valor_min, valor_max, angulo_min=0, angulo_max=180):
                return int(
                    angulo_min + (valor - valor_min) * (angulo_max - angulo_min) / (valor_max - valor_min)
                )

            angulo_x = mapear_para_servo(mira_x_prev, 0, w, 180, 0)
            angulo_y = mapear_para_servo(mira_y_prev, 0, h, 120, 85)

            # Atualiza as variáveis que a thread irá enviar ao Arduino
            with lock:
                angulo_x_global = angulo_x
                angulo_y_global = angulo_y

        except IndexError:
            mira_x_prev, mira_y_prev = w // 2, h // 2
            angulo_x = 90
            angulo_y = 90
        except AttributeError:
            mira_x_prev, mira_y_prev = w // 2, h // 2
            angulo_x = 90
            angulo_y = 90
    else:
        mira_x_prev, mira_y_prev = w // 2, h // 2
        angulo_x = 90
        angulo_y = 90

    if hands_results.multi_hand_landmarks and hands_results.multi_handedness:
        for hand_landmarks, hand_handedness in zip(
            hands_results.multi_hand_landmarks, hands_results.multi_handedness
        ):
            if hand_handedness.classification[0].label == "Right":
                if mao_direita_fechada(hand_landmarks.landmark):
                    if tempo_inicio_fechada is None:
                        tempo_inicio_fechada = time.time()
                    elif time.time() - tempo_inicio_fechada >= 2.0:
                        disparar = True
                else:
                    tempo_inicio_fechada = None
                    disparar = False
                break
    else:
        tempo_inicio_fechada = None
        disparar = False

    if disparar:
        disparar_status_text = "DISPARAR!"
        print("Disparar")
    else:
        disparar_status_text = "PRONTO"

    return image, angulo_x, angulo_y, disparar_status_text
