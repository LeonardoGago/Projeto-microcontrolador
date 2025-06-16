# jogo.py
import cv2
import numpy as np
import time
import interface
import mira
from interface import tempo_options

WIDTH, HEIGHT = 800, 600
cv2.namedWindow("MIRA NA CESTA")
cv2.setMouseCallback("MIRA NA CESTA", interface.mouse_callback)

cap = cv2.VideoCapture(0)
frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
estado = "menu"
start_time = None
pontuacao = 0

while True:
    if estado == "menu":
        cv2.resizeWindow("MIRA NA CESTA", WIDTH, HEIGHT)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        interface.draw_menu(frame)
        cv2.imshow("MIRA NA CESTA", frame)
        key = cv2.waitKey(10)

        if key == 27:
            break

        opcao = interface.get_selected_option()
        if opcao:
            if opcao == "Iniciar Jogo":
                estado = "jogo"
                start_time = time.time()
                pontuacao = 0
            elif opcao == "Dificuldade":
                estado = "dificuldade"
            elif opcao == "Tempo":
                estado = "tempo"
            elif opcao == "Sair":
                break
            interface.reset_selected_option()

    elif estado == "dificuldade":
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        interface.draw_dificuldade_menu(frame)
        cv2.imshow("MIRA NA CESTA", frame)
        key = cv2.waitKey(10)

        opcao = interface.get_selected_option()
        if opcao:
            if opcao in ["Facil", "Medio", "Dificil"]:
                interface.set_dificuldade(opcao)
                estado = "menu"
            elif opcao == "Voltar":
                estado = "menu"
            interface.reset_selected_option()

    elif estado == "tempo":
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        interface.draw_tempo_menu(frame)
        cv2.imshow("MIRA NA CESTA", frame)
        key = cv2.waitKey(10)

        opcao = interface.get_selected_option()
        if opcao:
            if opcao == "1 min":
                interface.set_tempo(60)
            elif opcao == "3 min":
                interface.set_tempo(180)
            elif opcao == "5 min":
                interface.set_tempo(300)
            elif opcao == "Infinito":
                interface.set_tempo(None)

            if opcao in tempo_options:
                estado = "menu"
            interface.reset_selected_option()

    elif estado == "jogo":
        ret, raw_frame = cap.read()
        if not ret:
            break

        frame = mira.rodar_mira_jogo(raw_frame)
        cv2.resizeWindow("MIRA NA CESTA", WIDTH, HEIGHT)

        tempo_total = interface.get_tempo()
        tempo_passado = int(time.time() - start_time) if start_time else 0
        tempo_restante = (
            tempo_total - tempo_passado if tempo_total is not None else None
        )

        if tempo_restante is not None and tempo_restante <= 0:
            estado = "resultado"
            continue

        dificuldade = interface.get_dificuldade()
        texto_restante = "--:--"
        if tempo_total is not None:
            minutos = tempo_restante // 60
            segundos = tempo_restante % 60
            texto_restante = f"{minutos:02}:{segundos:02}"

        # Exibe dificuldade, tempo e pontuação
        cv2.putText(
            frame,
            f"Dificuldade: {dificuldade}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            f"Tempo: {texto_restante}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            f"Pontos: {pontuacao}",
            (50, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        # Botão ENCERRAR (centralizado inferior)
        x, y, w, h = (WIDTH - 300) // 2, HEIGHT - 100, 300, 70
        mouse = interface.get_mouse_pos()
        color = (
            (255, 80, 80)
            if x < mouse[0] < x + w and y < mouse[1] < y + h
            else (180, 50, 50)
        )
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
        text_size = cv2.getTextSize("Encerrar", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(
            frame,
            "Encerrar",
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        interface.get_button_positions()["Encerrar"] = (x, y, w, h)

        opcao = interface.get_selected_option()
        if opcao == "Encerrar":
            estado = "resultado"
            interface.reset_selected_option()
            continue

        cv2.imshow("MIRA NA CESTA", frame)
        key = cv2.waitKey(10)
        if key == ord("q"):
            estado = "menu"

    elif estado == "resultado":
        cv2.resizeWindow("MIRA NA CESTA", WIDTH, HEIGHT)
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        mensagem = f"Pontuacao final: {pontuacao} ponto{'s' if pontuacao != 1 else ''}"
        cv2.putText(
            frame,
            mensagem,
            (WIDTH // 2 - 250, HEIGHT // 2 - 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3,
        )

        # Botões: Jogar de Novo e Voltar ao Menu
        botoes = ["Jogar de Novo", "Voltar ao Menu"]
        for i, label in enumerate(botoes):
            x, y, w, h = (WIDTH - 300) // 2, HEIGHT // 2 + i * 100, 300, 70
            interface.get_button_positions()[label] = (x, y, w, h)
            color = (
                (255, 165, 0)
                if x < interface.get_mouse_pos()[0] < x + w
                and y < interface.get_mouse_pos()[1] < y + h
                else (255, 130, 0)
            )
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            cv2.putText(
                frame,
                label,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )

        opcao = interface.get_selected_option()
        if opcao == "Jogar de Novo":
            start_time = time.time()
            pontuacao = 0
            estado = "jogo"
            interface.reset_selected_option()
        elif opcao == "Voltar ao Menu":
            estado = "menu"
            interface.reset_selected_option()

        cv2.imshow("MIRA NA CESTA", frame)
        cv2.waitKey(10)

cap.release()
cv2.destroyAllWindows()
