# interface.py
import cv2
import numpy as np

# Dimensões da tela
WIDTH, HEIGHT = 800, 600

# Cores e fonte
BUTTON_COLOR = (50, 150, 255)
HOVER_COLOR = (255, 100, 100)
TEXT_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (30, 30, 30)
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Menus principais
menu_options = ["Iniciar Jogo", "Dificuldade", "Tempo", "Sair"]
dificuldade_options = ["Facil", "Medio", "Dificil", "Voltar"]
tempo_options = ["1 min", "3 min", "5 min", "Infinito", "Voltar"]

# Estados
button_positions = {} #Dicionario que armazena tamanho e posição dos botões 
_selected_option = None #Armazena o último botão clicado
_mouse_pos = (0, 0) #Armazena a posição do mouse na tela 

# Configurações padrão
dificuldade = "Facil"
tempo = 60  # segundos (1 min)


def draw_menu(frame):
    global button_positions
    button_positions.clear() #Limpa o dicionario cada vez que a tela inical é desenhada
    frame[:] = BACKGROUND_COLOR #Pinta o frame com a cord de fundo definida
    title = "MIRA NA CESTA"
    cv2.putText(frame, title, (WIDTH // 2 - 200, 80), FONT, 1.5, (0, 255, 0), 3) #Desenha o titulo na parte superior do frame

    for idx, text in enumerate(menu_options): #Loop para desenhar os botões
        x, y, w, h = 250, 150 + idx * 100, 300, 70 #Coordenadas com espassamento em y, largura, altura
        button_positions[text] = (x, y, w, h)
        color = HOVER_COLOR if is_mouse_over((x, y, w, h)) else BUTTON_COLOR #Aplica uma cor no houver
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1) #Desenha o retangulo

        display_text = text
        if text == "Tempo": #Adiciona o tempo ao lado do botão tempo
            tempo_val = get_tempo()
            display_text += (
                f": {'Infinito' if tempo_val is None else f'{tempo_val//60} min'}"
            )
        elif text == "Dificuldade": #Adiciona a dificuldade ao lado de dificuldade
            display_text += f": {get_dificuldade()}"

        text_size = cv2.getTextSize(display_text, FONT, 0.9, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(frame, display_text, (text_x, text_y), FONT, 0.9, TEXT_COLOR, 2)


def draw_dificuldade_menu(frame):
    global button_positions
    button_positions.clear() #Limpa todos os botões anteriores toda vez que a página é recarregada
    frame[:] = BACKGROUND_COLOR
    cv2.putText(
        frame,
        "Escolha a Dificuldade",
        (WIDTH // 2 - 220, 80),
        FONT,
        1.3,
        (0, 255, 0),
        3,
    )

    for idx, text in enumerate(dificuldade_options):
        x, y, w, h = 250, 150 + idx * 80, 300, 70
        button_positions[text] = (x, y, w, h)
        color = HOVER_COLOR if is_mouse_over((x, y, w, h)) else BUTTON_COLOR
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
        text_size = cv2.getTextSize(text, FONT, 1, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y), FONT, 1, TEXT_COLOR, 2)


def draw_tempo_menu(frame):
    global button_positions
    button_positions.clear()
    frame[:] = BACKGROUND_COLOR
    cv2.putText(
        frame,
        "Escolha o Tempo de Jogo",
        (WIDTH // 2 - 260, 80),
        FONT,
        1.3,
        (0, 255, 0),
        3,
    )

    for idx, text in enumerate(tempo_options):
        x, y, w, h = 250, 150 + idx * 70, 300, 70
        button_positions[text] = (x, y, w, h)
        color = HOVER_COLOR if is_mouse_over((x, y, w, h)) else BUTTON_COLOR
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
        text_size = cv2.getTextSize(text, FONT, 1, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y), FONT, 1, TEXT_COLOR, 2)


def is_mouse_over(rect): #Verifica constantemente a posição do mouse na tela
    x, y, w, h = rect
    return x < _mouse_pos[0] < x + w and y < _mouse_pos[1] < y + h


def mouse_callback(event, x, y, flags, param):
    global _selected_option, _mouse_pos
    _mouse_pos = (x, y) # Sempre atualiza a posição do mouse
    if event == cv2.EVENT_LBUTTONDOWN: # Verifica se o botão esquerdo do mouse foi clicado
        for text, (bx, by, bw, bh) in button_positions.items(): # Itera sobre todos os botões registrados
            if bx < x < bx + bw and by < y < by + bh: # Verifica se o clique ocorreu DENTRO de um botão
                _selected_option = text # Se sim, armazena o texto do botão como a opção selecionada
    elif event == cv2.EVENT_MOUSEMOVE: # Se o mouse apenas moveu
        _mouse_pos = (x, y) # Atualiza a posição do mouse (redundante com a primeira linha, mas garante)


def get_selected_option(): #Pega o ultimo botao selecionado
    return _selected_option


def reset_selected_option(): #Reseta o ultimo botao selecionado
    global _selected_option
    _selected_option = None


def get_mouse_pos(): #Pega a posição do mouse
    return _mouse_pos


def set_dificuldade(value):
    global dificuldade
    dificuldade = value


def get_dificuldade():
    return dificuldade


def set_tempo(value):
    global tempo
    tempo = value


def get_tempo():
    return tempo


def get_button_positions():
    return button_positions
