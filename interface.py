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
button_positions = {}
_selected_option = None
_mouse_pos = (0, 0)

# Configurações padrão
dificuldade = "Facil"
tempo = 60  # segundos (1 min)


def draw_menu(frame):
    global button_positions
    button_positions.clear()
    frame[:] = BACKGROUND_COLOR
    title = "MIRA NA CESTA"
    cv2.putText(frame, title, (WIDTH // 2 - 200, 80), FONT, 1.5, (0, 255, 0), 3)

    for idx, text in enumerate(menu_options):
        x, y, w, h = 250, 150 + idx * 100, 300, 70
        button_positions[text] = (x, y, w, h)
        color = HOVER_COLOR if is_mouse_over((x, y, w, h)) else BUTTON_COLOR
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)

        display_text = text
        if text == "Tempo":
            tempo_val = get_tempo()
            display_text += (
                f": {'Infinito' if tempo_val is None else f'{tempo_val//60} min'}"
            )
        elif text == "Dificuldade":
            display_text += f": {get_dificuldade()}"

        text_size = cv2.getTextSize(display_text, FONT, 0.9, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(frame, display_text, (text_x, text_y), FONT, 0.9, TEXT_COLOR, 2)


def draw_dificuldade_menu(frame):
    global button_positions
    button_positions.clear()
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


def is_mouse_over(rect):
    x, y, w, h = rect
    return x < _mouse_pos[0] < x + w and y < _mouse_pos[1] < y + h


def mouse_callback(event, x, y, flags, param):
    global _selected_option, _mouse_pos
    _mouse_pos = (x, y)
    if event == cv2.EVENT_LBUTTONDOWN:
        for text, (bx, by, bw, bh) in button_positions.items():
            if bx < x < bx + bw and by < y < by + bh:
                _selected_option = text
    elif event == cv2.EVENT_MOUSEMOVE:
        _mouse_pos = (x, y)


def get_selected_option():
    return _selected_option


def reset_selected_option():
    global _selected_option
    _selected_option = None


def get_mouse_pos():
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
