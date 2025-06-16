# mira.py
import cv2
import mediapipe as mp
import math
import time

FONT = cv2.FONT_HERSHEY_SIMPLEX

mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
hands = mp_hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.8
)

# Estados
mira_x_prev = None
mira_y_prev = None
alpha = 0.15

tempo_inicio_fechada = None
disparar = False


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
        if dist < 0.13:
            dedos_fechados += 1
    return dedos_fechados >= 4


def rodar_mira_jogo(frame):
    global mira_x_prev, mira_y_prev, tempo_inicio_fechada, disparar

    image = cv2.flip(frame.copy(), 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pose_results = pose.process(image_rgb)
    hands_results = hands.process(image_rgb)

    h, w, _ = image.shape
    mira_x, mira_y = w // 2, h // 2

    if pose_results.pose_landmarks:
        lms = pose_results.pose_landmarks.landmark
        ombro = lms[mp_pose.PoseLandmark.LEFT_SHOULDER]
        cotovelo = lms[mp_pose.PoseLandmark.LEFT_ELBOW]
        punho = lms[mp_pose.PoseLandmark.LEFT_WRIST]

        angulo = calcular_angulo(ombro, cotovelo, punho)

        ombro_p = (int(ombro.x * w), int(ombro.y * h))
        cotovelo_p = (int(cotovelo.x * w), int(cotovelo.y * h))
        punho_p = (int(punho.x * w), int(punho.y * h))

        # Linhas do braço
        cv2.line(image, ombro_p, cotovelo_p, (255, 255, 0), 3)
        cv2.line(image, punho_p, cotovelo_p, (0, 255, 255), 3)
        cv2.circle(image, cotovelo_p, 6, (0, 0, 255), -1)

        # Vetor cotovelo → punho
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

        rel_x = mira_x_prev - w // 2
        rel_y = h // 2 - mira_y_prev

        # Info
        # cv2.putText(
        #     image, f"Coord: ({rel_x}, {rel_y})", (10, 30), FONT, 0.8, (255, 255, 0), 2
        # )
        # cv2.putText(
        #     image, f"Angulo: {int(angulo)}", (10, 60), FONT, 0.8, (0, 255, 255), 2
        # )

        # Mira
        cv2.circle(image, (mira_x_prev, mira_y_prev), 20, (0, 0, 255), -1)
        cv2.line(image, cotovelo_p, (mira_x_prev, mira_y_prev), (0, 0, 255), 2)
        cv2.line(image, (0, h // 2), (w, h // 2), (100, 100, 100), 1)

    # Verifica disparo
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
        cv2.putText(image, "DISPARAR", (10, 100), FONT, 1.2, (0, 0, 255), 3)

    return image
