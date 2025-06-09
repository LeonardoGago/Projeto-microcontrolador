# Controle de Mira com Disparo por Detecção Corporal (MediaPipe + OpenCV)

Este projeto utiliza **MediaPipe** e **OpenCV** para controlar uma mira com base nos movimentos do braço direito do usuário, detectados em tempo real pela webcam. Além disso, detecta quando a mão direita está fechada para acionar um "DISPARAR" na tela — ideal para projetos com Arduino e controle de servo motores.

## 🧠 Funcionalidades

- Detecção do braço direito (ombro, cotovelo, punho) para formar a linha de mira.
- Cálculo da direção da mira em coordenadas relativas X e Y.
- Detecção da mão direita e verificação se está fechada.
- Exibição da mira e do sinal de disparo na tela.
- Base para futura comunicação serial com Arduino para controle físico de motores.

---

## 📁 Estrutura

```bash
├── teste.py         # Arquivo principal com o código do projeto
├── README.md        # Este documento
├── requirements.txt # (opcional) Bibliotecas necessárias
```

---

## 🔧 Instalação

1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

2. Crie um ambiente virtual (opcional):

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

3. Instale os pacotes:

```bash
pip install opencv-python mediapipe
```

---

## ▶️ Como Executar

Execute o arquivo com:

```bash
python teste.py
```

Certifique-se de que sua webcam esteja conectada e funcionando.

---

## 📌 Explicações das Funções e Blocos

### `distancia(p1, p2)`
Calcula a distância euclidiana entre dois pontos (landmarks) retornados pelo MediaPipe.

### `mao_direita_fechada(landmarks)`
Verifica se a mão direita está fechada. Faz isso ao medir a distância entre a ponta dos dedos (exceto o polegar) e o punho. Se todos estiverem próximos do punho, considera a mão como fechada.

---

## 🎯 Bloco principal (`while cap.isOpened()`)

### 1. Leitura e espelhamento da imagem
```python
frame = cv2.flip(frame, 1)
```
Espelha horizontalmente para que o movimento à direita na vida real corresponda à direita na tela.

### 2. Processamento de Pose e Mãos
```python
pose_results = pose.process(image_rgb)
hands_results = hands.process(image_rgb)
```

### 3. Detecção da Mira (usando braço esquerdo por causa do espelhamento)
```python
lms = pose_results.pose_landmarks.landmark
ombro = lms[mp_pose.PoseLandmark.LEFT_SHOULDER]
...
```
Esses pontos são convertidos para coordenadas de tela e desenham a mira em verde.

### 4. Detecção de Disparo
```python
if mao_direita_fechada(hand_landmarks.landmark):
    cv2.putText(image, "DISPARAR", ...)
```
Se a mão direita estiver fechada, exibe o texto "DISPARAR" em vermelho na tela.

---

## 🛠 Possíveis Extensões

- Comunicação serial com Arduino para controlar servo motores com base em `dx` e `dy`.
- Detecção de outros gestos (ex: "abrir mão" para recarregar).
- Adicionar sons ou HUD para simular interface de jogo.

---

## 📷 Requisitos

- Python 3.7 ou superior
- Webcam funcional
- MediaPipe
- OpenCV

---

## 🧑‍💻 Autor

Projeto criado por [Seu Nome], baseado em visão computacional interativa com Python.

---

## 📜 Licença

Este projeto está sob a licença MIT. Sinta-se livre para usar, modificar e compartilhar.