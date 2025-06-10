import cv2
import mediapipe as mp
import math

# Inicializa Pose e Hands
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
hands = mp_hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.8
)  # Rastreando a mão e o braço com uma distancia de confiança minima

cap = cv2.VideoCapture(0)  # Abre a camera


def distancia(p1, p2):  # Distancia entre dois pontos (norma euclidiana)
    return math.hypot(p2.x - p1.x, p2.y - p1.y)


# A biblioteca fornece 21 pontos referentes a mão
def mao_direita_fechada(landmarks):
    punho = landmarks[0]
    dedos_tips = [8, 12, 16, 20]  # 4 dedos principais
    dedos_fechados = 0
    for tip_id in dedos_tips:
        ponta = landmarks[tip_id]
        dist = distancia(punho, ponta)
        if dist < 0.13:
            dedos_fechados += 1
    return (
        dedos_fechados >= 4
    )  # Se os 4 dedos tiverem uma distancia do punho menor que 0.13 a mão é considerada fechada


while cap.isOpened():
    ret, frame = cap.read()  # Verifica se a camera esta conectada
    if not ret:
        break

    # FLIP horizontal para que direita na vida real = direita na tela
    frame = cv2.flip(frame, 1)

    image = frame.copy()
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pose_results = pose.process(image_rgb)
    hands_results = hands.process(image_rgb)

    h, w, _ = image.shape  # Captura a altura e a largura da imagem

    # Mira com braço direito (após flip, usamos landmarks do braço ESQUERDO)
    if pose_results.pose_landmarks:  # Verifica se a detecção esta correta
        lms = pose_results.pose_landmarks.landmark
        ombro = lms[mp_pose.PoseLandmark.LEFT_SHOULDER]
        cotovelo = lms[mp_pose.PoseLandmark.LEFT_ELBOW]
        punho = lms[mp_pose.PoseLandmark.LEFT_WRIST]

        # Para desenhar precisamos converter para as dimensões das imagens

        ombro_p = (int(ombro.x * w), int(ombro.y * h))
        cotovelo_p = (int(cotovelo.x * w), int(cotovelo.y * h))
        punho_p = (int(punho.x * w), int(punho.y * h))

        # Desenha as linhas
        cv2.line(image, ombro_p, cotovelo_p, (0, 255, 0), 4)
        cv2.line(image, cotovelo_p, punho_p, (0, 255, 0), 4)
        cv2.circle(image, ombro_p, 6, (255, 0, 0), -1)
        cv2.circle(image, cotovelo_p, 6, (0, 0, 255), -1)
        cv2.circle(image, punho_p, 6, (0, 255, 255), -1)

        # Vetor posição
        dx = punho_p[0] - ombro_p[0]
        dy = ombro_p[1] - punho_p[1]

        # Escreve na tela as coordendas do vetor posição
        cv2.putText(
            image,
            f"Mira X: {dx}  Y: {dy}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 255),
            2,
        )

    # Disparo com mão direita real
    if hands_results.multi_hand_landmarks and hands_results.multi_handedness:
        for hand_landmarks, hand_handedness in zip(
            hands_results.multi_hand_landmarks, hands_results.multi_handedness
        ):
            label = hand_handedness.classification[0].label

            if label == "Right":
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                if mao_direita_fechada(hand_landmarks.landmark):
                    cv2.putText(
                        image,
                        "DISPARAR",
                        (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 0, 255),
                        3,
                    )

    cv2.imshow("Controle de Mira com Disparo", image)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
