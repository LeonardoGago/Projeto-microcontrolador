# mira.py
import cv2
import mediapipe as mp
import math
import time
import serial
import sys # Importa sys para sair elegantemente

# --- Constantes e Variáveis Globais ---
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Escaneia o corpo e a mão
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
hands = mp_hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.8
)

# Variáveis de estado da mira e disparo
mira_x_prev = None
mira_y_prev = None
alpha = 0.15 # Constante de suavização da mira

tempo_inicio_fechada = None
disparar = False

# Conexão Serial com Arduino (inicializada aqui, mas com tratamento de erro)
arduino = None
try:
    # Verifique a porta COM correta para o seu Arduino
    arduino = serial.Serial('COM22', 9600, timeout=1)
    time.sleep(2) # Espera a conexão serial inicializar
    print("Conexão com Arduino estabelecida.")
except serial.SerialException as e:
    print(f"Erro ao conectar ao Arduino: {e}")
    print("Certifique-se de que o Arduino está conectado e a porta COM está correta.")
    print("A mira funcionará, mas sem controle do Arduino.")
    # Não sair, apenas define arduino como None
    # sys.exit() # Pode usar isso se o Arduino for estritamente obrigatório

# --- Funções Auxiliares ---
def distancia(p1, p2): # Distancia entre dois pontos
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def calcular_angulo(a, b, c):
    ab = [a.x - b.x, a.y - b.y] # Vetor ombro->Cotovelo
    cb = [c.x - b.x, c.y - b.y] # Vetor Cotovelo->Punho
    dot = ab[0] * cb[0] + ab[1] * cb[1] # Produto Escalar
    norm_ab = math.hypot(*ab) # Calcula a norma
    norm_cb = math.hypot(*cb)
    if norm_ab * norm_cb == 0: # Se um dos vetores é um ponto significa que o braço esta esticado (180 graus)
        return 180.0
    angle = math.acos(dot / (norm_ab * norm_cb)) # Angulo entre os dois vetores
    return math.degrees(angle)

def mao_direita_fechada(landmarks):
    punho = landmarks[0] # landmark do punho
    dedos_tips = [8, 12, 16, 20] # landmark das pontas dos dedos principais (indicador, médio, anelar, mínimo)
    dedos_fechados = 0
    for tip_id in dedos_tips: # Verifica pra cada dedo se...
        ponta = landmarks[tip_id]
        dist = distancia(punho, ponta)
        # O limiar 0.13 é um valor aproximado. Você pode precisar ajustar
        # este valor com base na sua câmera e na distância do usuário.
        if dist < 0.2:
            dedos_fechados += 1
    return dedos_fechados >= 4 # Considera mão fechada se 4 ou mais dedos estiverem próximos ao punho


# --- Função Principal de Renderização da Mira ---
# ATENÇÃO: Esta é a definição da função rodar_mira_jogo que você precisa no seu mira.py
def rodar_mira_jogo(frame_input, video_width, video_height): # Recebe o frame e as dimensões desejadas para o vídeo
    global mira_x_prev, mira_y_prev, tempo_inicio_fechada, disparar

    image = cv2.flip(frame_input.copy(), 1) # Copia o frame e usa o flip para simular um espelho
    image = cv2.resize(image, (video_width, video_height)) # Redimensiona para o tamanho do vídeo principal
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # Transforma em RGB

    pose_results = pose.process(image_rgb) # Processa a imagem para detectar o corpo
    hands_results = hands.process(image_rgb)

    h, w, _ = image.shape # Salva a altura (h) e a largura (w) da imagem redimensionada

    # Valores padrão para retorno, caso a pose não seja detectada
    angulo_x = 90
    angulo_y = 90
    disparar_status_text = "PRONTO"

    if pose_results.pose_landmarks: # Verifica se o corpo foi detectado
        lms = pose_results.pose_landmarks.landmark # Acessa a lista de pontos de referencia do corpo

        # Tenta obter os landmarks do braço esquerdo (corresponde ao direito na imagem espelhada)
        try:
            ombro = lms[mp_pose.PoseLandmark.LEFT_SHOULDER]
            cotovelo = lms[mp_pose.PoseLandmark.LEFT_ELBOW]
            punho = lms[mp_pose.PoseLandmark.LEFT_WRIST]

            # Angulo do cotovelo
            angulo = calcular_angulo(ombro, cotovelo, punho)

            # Converte as coordenadas normalizadas em pixels da imagem
            ombro_p = (int(ombro.x * w), int(ombro.y * h))
            cotovelo_p = (int(cotovelo.x * w), int(cotovelo.y * h))
            punho_p = (int(punho.x * w), int(punho.y * h))

            # Desenha as linhas do braço no frame do vídeo
            cv2.line(image, ombro_p, cotovelo_p, (255, 255, 0), 3)
            cv2.line(image, punho_p, cotovelo_p, (0, 255, 255), 3)
            cv2.circle(image, cotovelo_p, 6, (0, 0, 255), -1)

            # Vetor cotovelo → punho
            dx = punho.x - cotovelo.x
            dy = punho.y - cotovelo.y
            norm = math.hypot(dx, dy)
            if norm != 0:
                # Se for diferente de zero transforma no vetor unitário
                dx /= norm
                dy /= norm

            cx, cy = int(cotovelo.x * w), int(cotovelo.y * h) # Coordenadas em pixel do cotovelo
            t = 1000 # Fator de escala para a projeção da mira
            proj_x = int(cx + dx * t)
            proj_y = int(cy + dy * t)

            # Limita a mira aos limites da tela de vídeo
            mira_x = max(0, min(w - 1, proj_x))
            mira_y = max(0, min(h - 1, proj_y))

            # Suavização da mira
            if mira_x_prev is None: # Inicializando pela primeira vez
                mira_x_prev, mira_y_prev = mira_x, mira_y
            else:
                mira_x_prev = int((1 - alpha) * mira_x_prev + alpha * mira_x)
                mira_y_prev = int((1 - alpha) * mira_y_prev + alpha * mira_y)

            # Desenha a mira na tela do vídeo
            cv2.circle(image, (mira_x_prev, mira_y_prev), 20, (0, 0, 255), -1)
            cv2.line(image, cotovelo_p, (mira_x_prev, mira_y_prev), (0, 0, 255), 2)
            cv2.line(image, (0, h // 2), (w, h // 2), (100, 100, 100), 1) # Linha de referência horizontal

            # Mapeamento de coordenadas da mira para os ângulos do servo
            def mapear_para_servo(valor, valor_min, valor_max, angulo_min=0, angulo_max=180):
                return int(
                    angulo_min + (valor - valor_min) * (angulo_max - angulo_min) / (valor_max - valor_min)
                )

            angulo_x = mapear_para_servo(mira_x_prev, 0, w, 0, 180)
            angulo_y = mapear_para_servo(mira_y_prev, 0, h, 180, 0) # Y invertido: cima = 180, baixo = 0

            # Comunicação com o Arduino (se a conexão foi estabelecida)
            if arduino and arduino.is_open:
                try:
                    arduino.write(f"{angulo_x},{angulo_y}\n".encode()) # Envia as coordenadas X e Y pro arduino
                    resposta = arduino.readline().decode().strip() # Leia a resposta do Arduino se for necessário para depuração
                    print("Arduino respondeu:", resposta)
                except serial.SerialException as e:
                    print(f"Erro de escrita/leitura no Arduino: {e}")
                    # Pode adicionar lógica para tentar reconectar ou avisar o usuário

        except IndexError:
            # Captura erro se algum landmark essencial do braço não for detectado
            # Mantém a mira no centro e servos em 90 se o braço não for visto
            mira_x_prev, mira_y_prev = w // 2, h // 2
            angulo_x = 90
            angulo_y = 90
            # print("Ombro, cotovelo ou punho não detectados, mira no centro.")
        except AttributeError:
            # Caso algum objeto landmark esteja None por algum motivo
            mira_x_prev, mira_y_prev = w // 2, h // 2
            angulo_x = 90
            angulo_y = 90
            # print("Erro de atributo em landmark, mira no centro.")

    else: # Se nenhuma pose for detectada
        mira_x_prev, mira_y_prev = w // 2, h // 2 # Mira volta para o centro
        angulo_x = 90 # Servos ficam no meio
        angulo_y = 90

    # Verifica disparo com a mão direita fechada
    if hands_results.multi_hand_landmarks and hands_results.multi_handedness:
        for hand_landmarks, hand_handedness in zip(
            hands_results.multi_hand_landmarks, hands_results.multi_handedness
        ):
            if hand_handedness.classification[0].label == "Right": # Se for a mão direita
                if mao_direita_fechada(hand_landmarks.landmark): # Se a mão direita estiver fechada
                    if tempo_inicio_fechada is None: # Instante em que a mão foi fechada
                        tempo_inicio_fechada = time.time()
                    elif time.time() - tempo_inicio_fechada >= 2.0: # Disparo após 2 segundos de punho fechado
                        disparar = True
                else:
                    tempo_inicio_fechada = None # Se estiver aberta o tempo de inicio é vazio e não dispara
                    disparar = False
                break # Sai do loop assim que a mão direita é processada
    else: # Se nenhuma mão for detectada
        tempo_inicio_fechada = None
        disparar = False

    if disparar:
        disparar_status_text = "DISPARAR!"
        print("Disparar")
    else:
        disparar_status_text = "PRONTO"

    # Retorna o frame com a mira, e os dados para a UI lateral
    return image, angulo_x, angulo_y, disparar_status_text
