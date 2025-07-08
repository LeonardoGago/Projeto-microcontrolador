# jogo.py
import cv2
import numpy as np
import time
import interface
import mira     
import sys # Importa sys para lidar com saída

# --- Configurações de Dimensões ---
TOTAL_HEIGHT = interface.HEIGHT # Usa a altura da interface (600) como altura total
WIDTH_VIDEO = 640               
WIDTH_UI = 250                  # Largura da tela lateral para informações
TOTAL_WIDTH = WIDTH_VIDEO + WIDTH_UI

# --- Inicialização da Janela OpenCV ---
cv2.namedWindow("MIRA NA CESTA")
cv2.setMouseCallback("MIRA NA CESTA", interface.mouse_callback)

# --- Captura de Vídeo ---
cap = cv2.VideoCapture(0) # Inicia a captura de vídeo (0 para webcam padrão)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera. Verifique se ela está conectada e não está em uso.")
    sys.exit() # Sai do programa se a câmera não abrir

# --- Variáveis de Estado do Jogo ---
estado = "menu" # Estados: "menu", "dificuldade", "tempo", "jogo", "resultado"
start_time = None # Tempo de início do jogo
pontuacao = 0     # Pontuação atual
game_time_limit = None # Limite de tempo do jogo (em segundos, ou None para infinito)

while True:
    # --- Gerenciamento de Estados do Jogo ---
    if estado == "menu":
        # Ajusta a janela para as dimensões do menu
        cv2.resizeWindow("MIRA NA CESTA", interface.WIDTH, interface.HEIGHT)
        frame_display = np.zeros((interface.HEIGHT, interface.WIDTH, 3), dtype=np.uint8)
        interface.draw_menu(frame_display)
        cv2.imshow("MIRA NA CESTA", frame_display)
        key = cv2.waitKey(10) # Pequeno atraso para processar eventos do mouse/teclado

        if key == 27: # ESC para sair
            break

        opcao = interface.get_selected_option()
        if opcao:
            if opcao == "Iniciar Jogo":
                estado = "jogo"
                start_time = time.time() # Inicia o temporizador do jogo
                pontuacao = 0 # Zera a pontuação ao iniciar um novo jogo
                game_time_limit = interface.get_tempo() # Pega o tempo configurado no menu
            elif opcao == "Dificuldade":
                estado = "dificuldade"
            elif opcao == "Tempo":
                estado = "tempo"
            elif opcao == "Sair":
                break # Sai do loop principal
            interface.reset_selected_option() # Limpa a opção selecionada

    elif estado == "dificuldade":
        cv2.resizeWindow("MIRA NA CESTA", interface.WIDTH, interface.HEIGHT)
        frame_display = np.zeros((interface.HEIGHT, interface.WIDTH, 3), dtype=np.uint8)
        interface.draw_dificuldade_menu(frame_display)
        cv2.imshow("MIRA NA CESTA", frame_display)
        cv2.waitKey(10)

        opcao = interface.get_selected_option()
        if opcao:
            if opcao in ["Facil", "Medio", "Dificil"]:
                interface.set_dificuldade(opcao)
            estado = "menu" # Sempre volta ao menu principal após seleção ou "Voltar"
            interface.reset_selected_option()

    elif estado == "tempo":
        cv2.resizeWindow("MIRA NA CESTA", interface.WIDTH, interface.HEIGHT)
        frame_display = np.zeros((interface.HEIGHT, interface.WIDTH, 3), dtype=np.uint8)
        interface.draw_tempo_menu(frame_display)
        cv2.imshow("MIRA NA CESTA", frame_display)
        cv2.waitKey(10)

        opcao = interface.get_selected_option()
        if opcao:
            # Atualiza o tempo global na interface.py
            if opcao == "1 min":
                interface.set_tempo(60)
            elif opcao == "3 min":
                interface.set_tempo(180)
            elif opcao == "5 min":
                interface.set_tempo(300)
            elif opcao == "Infinito":
                interface.set_tempo(None) # Usa None para tempo infinito

            estado = "menu" # Sempre volta ao menu principal
            interface.reset_selected_option()

    elif estado == "jogo":
        # Redimensiona a janela para acomodar o vídeo e a UI lateral
        cv2.resizeWindow("MIRA NA CESTA", TOTAL_WIDTH, TOTAL_HEIGHT)

        ret, raw_frame = cap.read()
        if not ret:
            print("Erro: Falha ao ler frame da câmera durante o jogo.")
            break

        # Chama a função do mira.py que processa o frame e retorna os dados da UI
        # Agora passamos a TOTAL_HEIGHT para a função rodar_mira_jogo,
        # garantindo que a altura do vídeo retornado seja a mesma da UI.
        processed_video_frame, angulo_x_servo, angulo_y_servo, disparar_status = \
            mira.rodar_mira_jogo(raw_frame, WIDTH_VIDEO, TOTAL_HEIGHT)
        
        # Atualiza pontuação se o Arduino informou "acertou"
        pontuacao += mira.consumir_pontos()

        # --- Lógica de Tempo de Jogo ---
        time_remaining_str = "Infinito"
        if game_time_limit is not None:
            elapsed_time = time.time() - start_time
            time_remaining = max(0, game_time_limit - int(elapsed_time))
            minutes = time_remaining // 60
            seconds = time_remaining % 60
            time_remaining_str = f"{minutes:02d}:{seconds:02d}"
            if time_remaining == 0:
                print("Tempo de jogo esgotado!")
                estado = "resultado" # Passa para a tela de resultado
                continue # Pula o resto do loop para ir para a tela de resultado

        # --- Criação da Tela Lateral (HUD) ---
        # A ui_frame já será criada com TOTAL_HEIGHT
        ui_frame = np.zeros((TOTAL_HEIGHT, WIDTH_UI, 3), dtype=np.uint8)
        ui_frame[:] = interface.BACKGROUND_COLOR # Fundo escuro para a UI

        # --- Desenho das Informações na UI Lateral ---
        y_offset = 50
        text_color_ui = (255, 255, 255) # Cor padrão do texto (branco)

        # Título da UI
        cv2.putText(ui_frame, "STATUS DO JOGO", (WIDTH_UI // 2 - cv2.getTextSize("STATUS DO JOGO", interface.FONT, 0.6, 2)[0][0] // 2, 30),
                    interface.FONT, 0.6, (0, 200, 255), 2)
        y_offset += 30 # Ajusta para o próximo item

        # Pontuação
        cv2.putText(ui_frame, "PONTUACAO:", (20, y_offset + 30), interface.FONT, 0.7, text_color_ui, 2)
        cv2.putText(ui_frame, f"{pontuacao}", (20, y_offset + 60), interface.FONT, 0.9, (0, 255, 255), 2) # Ciano
        y_offset += 80

        # Tempo Restante
        cv2.putText(ui_frame, "TEMPO:", (20, y_offset + 30), interface.FONT, 0.7, text_color_ui, 2)
        cv2.putText(ui_frame, time_remaining_str, (20, y_offset + 60), interface.FONT, 0.9, (0, 255, 255), 2) # Ciano
        y_offset += 80

        # --- Status de Disparo (CORRIGIDO/VERIFICADO AQUI) ---
        status_color = (0, 255, 0) if disparar_status == "PRONTO" else (0, 0, 255) # Verde para PRONTO, Vermelho para DISPARAR!
        cv2.putText(ui_frame, "STATUS:", (20, y_offset + 30), interface.FONT, 0.7, text_color_ui, 2)
        cv2.putText(ui_frame, disparar_status, (20, y_offset + 60), interface.FONT, 0.9, status_color, 2)
        y_offset += 80
        # ----------------------------------------------------

        # Dificuldade Atual
        cv2.putText(ui_frame, "DIFICULDADE:", (20, y_offset + 30), interface.FONT, 0.7, text_color_ui, 2)
        cv2.putText(ui_frame, interface.get_dificuldade(), (20, y_offset + 60), interface.FONT, 0.9, (0, 255, 255), 2) # Ciano
        y_offset += 80

        # Ângulos do Servo
        cv2.putText(ui_frame, "SERVO X:", (20, y_offset + 30), interface.FONT, 0.7, text_color_ui, 2)
        cv2.putText(ui_frame, f"{angulo_x_servo}", (20, y_offset + 60), interface.FONT, 0.9, (255, 0, 255), 2) # Magenta
        y_offset += 70

        cv2.putText(ui_frame, "SERVO Y:", (20, y_offset + 30), interface.FONT, 0.7, text_color_ui, 2)
        cv2.putText(ui_frame, f"{angulo_y_servo}", (20, y_offset + 60), interface.FONT, 0.9, (255, 0, 255), 2) # Magenta
        y_offset += 70

        # --- Botão ENCERRAR na UI Lateral ---
        # Posiciona o botão de encerrar na parte inferior da UI lateral
        btn_w, btn_h = 200, 50
        btn_x = (WIDTH_UI - btn_w) // 2
        btn_y = TOTAL_HEIGHT - btn_h - 20 # 20 pixels de margem inferior

        # Atualiza as posições de botão para a mouse_callback,
        # mas mapeando para as coordenadas da janela total!
        # Isso é crucial para que o clique funcione corretamente na janela combinada.
        button_info = (btn_x + WIDTH_VIDEO, btn_y, btn_w, btn_h) # X ajustado
        interface.get_button_positions()["Encerrar_Jogo"] = button_info

        # Desenha o botão
        mouse_x_total, mouse_y_total = interface.get_mouse_pos()
        # Verifica se o mouse está sobre o botão na janela combinada
        btn_color = interface.HOVER_COLOR if interface.is_mouse_over(button_info) else interface.BUTTON_COLOR
        cv2.rectangle(ui_frame, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), btn_color, -1)

        # Centraliza o texto "Encerrar" dentro do botão
        text_size = cv2.getTextSize("Encerrar", interface.FONT, 0.8, 2)[0]
        text_x = btn_x + (btn_w - text_size[0]) // 2
        text_y = btn_y + (btn_h + text_size[1]) // 2
        cv2.putText(ui_frame, "Encerrar", (text_x, text_y), interface.FONT, 0.8, interface.TEXT_COLOR, 2)


        # --- Combina as duas imagens lado a lado para exibição ---
        combined_frame = np.hstack((processed_video_frame, ui_frame))
        cv2.imshow("MIRA NA CESTA", combined_frame)

        # Lógica de clique no botão "Encerrar"
        opcao_clicada = interface.get_selected_option()
        if opcao_clicada == "Encerrar_Jogo": # Use o nome que você definiu para o botão
            estado = "resultado"
            interface.reset_selected_option()
            continue # Pula o resto do loop para ir para a tela de resultado

        key = cv2.waitKey(10)
        if key == ord("q"): # "q" para voltar ao menu ou sair, dependendo da sua preferência
            estado = "menu" # Ou "break" para sair do programa

        # Lógica de pontuação (exemplo - você adicionaria a detecção de acerto real aqui)
        # O estado de disparo vem de mira.disparar.
        # Você deve ter uma lógica para detectar se o disparo "acertou" algo.
        if mira.disparar:
             # Exemplo de como você aumentaria a pontuação
             # Isso deve ser ligado à sua lógica de detecção de alvo
             # (que não está no código fornecido)
             # Por exemplo:
             # if is_target_hit(mira.mira_x_prev, mira.mira_y_prev, target_coords):
             #     pontuacao += 1
             #     print("ALVO ATINGIDO!")
             pass # placeholder para sua lógica de pontuação

    elif estado == "resultado":
        cv2.resizeWindow("MIRA NA CESTA", interface.WIDTH, interface.HEIGHT)
        frame_display = np.zeros((interface.HEIGHT, interface.WIDTH, 3), dtype=np.uint8)

        mensagem = f"Pontuacao final: {pontuacao} ponto{'s' if pontuacao != 1 else ''}"
        cv2.putText(
            frame_display,
            mensagem,
            (interface.WIDTH // 2 - cv2.getTextSize(mensagem, interface.FONT, 1.2, 3)[0][0] // 2, interface.HEIGHT // 2 - 100),
            interface.FONT,
            1.2,
            (0, 255, 0),
            3,
        )

        # Botões: Jogar de Novo e Voltar ao Menu
        botoes = ["Jogar de Novo", "Voltar ao Menu"]
        for i, label in enumerate(botoes):
            x, y, w, h = (interface.WIDTH - 300) // 2, interface.HEIGHT // 2 + i * 100, 300, 70
            # Note que para a tela de resultado, os botões estão no 'frame_display' normal do menu,
            # então não precisa ajustar o X para WIDTH_VIDEO.
            interface.get_button_positions()[label] = (x, y, w, h)
            color = (
                (255, 165, 0) # Laranja claro para hover
                if interface.is_mouse_over((x, y, w, h))
                else (255, 130, 0) # Laranja escuro normal
            )
            cv2.rectangle(frame_display, (x, y), (x + w, y + h), color, -1)
            text_size = cv2.getTextSize(label, interface.FONT, 1, 2)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            cv2.putText(
                frame_display,
                label,
                (text_x, text_y),
                interface.FONT,
                1,
                (255, 255, 255),
                2,
            )

        opcao_resultado = interface.get_selected_option()
        if opcao_resultado == "Jogar de Novo":
            start_time = time.time()
            pontuacao = 0
            estado = "jogo"
            interface.reset_selected_option()
        elif opcao_resultado == "Voltar ao Menu":
            estado = "menu"
            interface.reset_selected_option()

        cv2.imshow("MIRA NA CESTA", frame_display)
        cv2.waitKey(10) # Pequeno atraso

# --- Limpeza Final ---
cap.release()
cv2.destroyAllWindows()
if mira.arduino and mira.arduino.is_open: # Garante que o Arduino está conectado antes de tentar fechar
    mira.arduino.close()
    print("Conexão com Arduino fechada.")
