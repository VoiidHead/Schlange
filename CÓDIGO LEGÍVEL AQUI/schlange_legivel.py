import pygame
from random import randint
import os
import sys

pygame.init()


# Encontra o caminho correto dos arquivos, inclusive quando o jogo
# estiver sendo executado como um executável criado pelo PyInstaller.
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Cria uma pasta para salvar os dados do jogo dentro do AppData.
pasta_save = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Schlange")
os.makedirs(pasta_save, exist_ok=True)

arquivo_recorde = os.path.join(pasta_save, "besto.txt")


# Salva o recorde no arquivo.
def salvar_recorde(recorde):
    with open(arquivo_recorde, "w") as arquivo:
        arquivo.write(str(recorde))


# Carrega o recorde salvo.
# Se o arquivo não existir ou estiver inválido, retorna 0.
def carregar_recorde():
    try:
        with open(arquivo_recorde, "r") as arquivo:
            return int(arquivo.read())
    except (FileNotFoundError, ValueError):
        return 0


# Classe que guarda as dimensões da janela.
class Janela:
    largura = 640
    altura = 480


# Classe que guarda as informações da cobra.
class Cobra:
    largura = 25
    altura = 25

    x = (Janela.largura / 2) - (largura / 2)
    y = (Janela.altura / 2) - (altura / 2)

    velocidade = 5

    # A cobra começa parada.
    direcao = None

    tamanho = 1


# Classe que guarda as informações da maçã.
class Maca:
    raio = 20
    x = randint(raio, Janela.largura - raio)
    y = randint(raio, Janela.altura - raio)


# Verifica se um retângulo e um círculo estão colidindo.
def colisao_circulo(retangulo, centro_x, centro_y, raio):
    ponto_x = max(retangulo.left, min(centro_x, retangulo.right))
    ponto_y = max(retangulo.top, min(centro_y, retangulo.bottom))

    distancia_x = centro_x - ponto_x
    distancia_y = centro_y - ponto_y

    return distancia_x**2 + distancia_y**2 <= raio**2


# Desenha o corpo da cobra.
# Quando o jogo está pausado, o corpo fica com uma cor diferente.
def desenhar_corpo(corpo, pausado):
    if not pausado:
        for posicao in corpo[:-1]:
            pygame.draw.rect(monitor, (255, 212, 59), (posicao[0], posicao[1], Cobra.largura, Cobra.altura))
    else:
        for posicao in corpo[:-1]:
            pygame.draw.rect(monitor, (205, 162, 9), (posicao[0], posicao[1], Cobra.largura, Cobra.altura))


# Reinicia todos os valores necessários para começar uma nova partida.
def reiniciar_jogo():
    global pontuacao, contador_morte, estado_jogo, pausado, novo_recorde

    Cobra.x = (Janela.largura / 2) - (Cobra.largura / 2)
    Cobra.y = (Janela.altura / 2) - (Cobra.altura / 2)

    Cobra.tamanho = 1
    Cobra.direcao = None

    corpo.clear()

    pontuacao = 0
    novo_recorde = False
    contador_morte = 0
    pausado = False

    Maca.x = randint(Maca.raio, Janela.largura - Maca.raio)
    Maca.y = randint(Maca.raio, Janela.altura - Maca.raio)

    estado_jogo = 0


# Valores iniciais do jogo.
pontuacao = 0
recorde = carregar_recorde()
corpo = []

novo_recorde = False

# Guarda a última direção antes de pausar.
# Ela só é atualizada quando o jogo é pausado.
ultima_direcao = None


# Fontes e textos usados pelo jogo.
fonte_tahoma = pygame.font.SysFont("Tahoma", 24)

texto_esc = fonte_tahoma.render("esc para fechar o jogo", True, (255, 255, 255))
texto_game_over = fonte_tahoma.render("ESTÁ MORTO!", True, (255, 255, 255))
texto_novo_recorde = fonte_tahoma.render("NOVO RECORDE!!", True, (255, 255, 255))


# Estados possíveis do jogo:
# 0   = jogo normal
# 0.5 = animação da morte
# 1   = tela de game over
estado_jogo = 0

pausado = False
contador_morte = 0


# Criação da janela.
monitor = pygame.display.set_mode((Janela.largura, Janela.altura))
pygame.display.set_caption("Schlange")

pygame.display.set_icon(pygame.transform.smoothscale(pygame.image.load(resource_path("icon/icon.png")), (32, 32)))


# Relógio usado para limitar o jogo a 60 FPS.
relogio = pygame.time.Clock()


# Efeitos sonoros.
som_comer = pygame.mixer.Sound(resource_path("sfx/hungrySchlange.wav"))
som_dano = pygame.mixer.Sound(resource_path("sfx/slicedSchlange.wav"))
som_morte = pygame.mixer.Sound(resource_path("sfx/SchlangeIsDead.wav"))


# Loop principal do jogo.
while True:

    # Mantém o jogo em 60 FPS.
    relogio.tick(60)


    # Processa os eventos do teclado, fechamento da janela etc.
    for evento in pygame.event.get():

        # Fechar a janela.
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if evento.type == pygame.KEYDOWN:

            # =========================================================
            # JOGO NORMAL
            # =========================================================
            if estado_jogo == 0:

                # Se o jogo não estiver pausado, podemos movimentar a cobra.
                if not pausado:

                    # ESC pausa o jogo.
                    if evento.key == pygame.K_ESCAPE:
                        pausado = True


                    # W ou seta para cima.
                    # A cobra não pode voltar diretamente para baixo.
                    elif evento.key in [pygame.K_w, pygame.K_UP]:
                        if Cobra.direcao != "baixo":
                            Cobra.direcao = "cima"


                    # A ou seta para esquerda.
                    # A cobra não pode voltar diretamente para direita.
                    elif evento.key in [pygame.K_a, pygame.K_LEFT]:
                        if Cobra.direcao != "direita":
                            Cobra.direcao = "esquerda"


                    # S ou seta para baixo.
                    # A cobra não pode voltar diretamente para cima.
                    elif evento.key in [pygame.K_s, pygame.K_DOWN]:
                        if Cobra.direcao != "cima":
                            Cobra.direcao = "baixo"


                    # D ou seta para direita.
                    # A cobra não pode voltar diretamente para esquerda.
                    elif evento.key in [pygame.K_d, pygame.K_RIGHT]:
                        if Cobra.direcao != "esquerda":
                            Cobra.direcao = "direita"


                # Se o jogo estiver pausado.
                else:

                    # ESC fecha o jogo.
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()


                    # Espaço ou Enter continua o jogo.
                    elif evento.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                        Cobra.direcao = ultima_direcao
                        pausado = False


            # =========================================================
            # ANIMAÇÃO DA MORTE
            # =========================================================
            elif estado_jogo == 0.5:

                # Quando o jogador aperta uma tecla, o som de morte
                # é reproduzido e a tela de game over aparece.
                if evento.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                    som_morte.play()
                    estado_jogo = 1


            # =========================================================
            # GAME OVER
            # =========================================================
            elif estado_jogo == 1:

                # R, Espaço ou Enter reinicia o jogo.
                if evento.key in [pygame.K_r, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                    reiniciar_jogo()


                # ESC fecha o jogo.
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


    # =============================================================
    # ESTADOS DO JOGO
    # =============================================================

    match estado_jogo:

        # =========================================================
        # JOGO NORMAL
        # =========================================================
        case 0:

            # Tudo dentro deste bloco só acontece enquanto o jogo
            # não estiver pausado.
            if not pausado:

                # Fundo verde.
                monitor.fill((0, 190, 0))


                # Texto da pontuação.
                texto_pontuacao = fonte_tahoma.render(f"Pontuação: {pontuacao}", True, (255, 255, 255), (0, 0, 0))


                # -------------------------------------------------
                # MOVIMENTO DA COBRA
                # -------------------------------------------------

                match Cobra.direcao:

                    case "cima":
                        Cobra.y -= Cobra.velocidade

                    case "esquerda":
                        Cobra.x -= Cobra.velocidade

                    case "baixo":
                        Cobra.y += Cobra.velocidade

                    case "direita":
                        Cobra.x += Cobra.velocidade


                # -------------------------------------------------
                # TELETRANSPORTE PELAS BORDAS
                # -------------------------------------------------

                # Se a cobra sair pela direita, aparece pela esquerda.
                if Cobra.x >= Janela.largura:
                    Cobra.x = 0

                # Se sair pela esquerda, aparece pela direita.
                elif Cobra.x < 0:
                    Cobra.x = Janela.largura


                # Se sair por baixo, aparece em cima.
                if Cobra.y >= Janela.altura:
                    Cobra.y = 0

                # Se sair por cima, aparece embaixo.
                elif Cobra.y < 0:
                    Cobra.y = Janela.altura


                # Adiciona a posição atual da cabeça ao corpo.
                corpo.append([Cobra.x, Cobra.y])


                # O corpo precisa ter uma quantidade limitada de posições.
                # Quanto maior a cobra, mais posições são mantidas.
                if len(corpo) > Cobra.tamanho * 6:
                    del corpo[0]


                # Só desenha a cobra quando ela já tiver uma direção.
                if Cobra.direcao is not None:
                    desenhar_corpo(corpo, False)


                # Desenha a cabeça da cobra.
                cabeca_cobra = pygame.draw.rect(monitor, (48, 105, 152), (Cobra.x, Cobra.y, Cobra.largura, Cobra.altura))


                # Desenha a maçã.
                pygame.draw.circle(monitor, (255, 0, 0), (Maca.x, Maca.y), Maca.raio)


                # -------------------------------------------------
                # COMER A MAÇÃ
                # -------------------------------------------------

                if colisao_circulo(cabeca_cobra, Maca.x, Maca.y, Maca.raio):

                    # Escolhe uma nova posição para a maçã.
                    Maca.x = randint(Maca.raio, Janela.largura - Maca.raio)
                    Maca.y = randint(Maca.raio, Janela.altura - Maca.raio)


                    # Garante que a nova maçã não apareça dentro da cobra.
                    while colisao_circulo(cabeca_cobra, Maca.x, Maca.y, Maca.raio):
                        Maca.x = randint(Maca.raio, Janela.largura - Maca.raio)
                        Maca.y = randint(Maca.raio, Janela.altura - Maca.raio)


                    # Toca o som de comer.
                    som_comer.play()

                    # Aumenta o tamanho da cobra e a pontuação.
                    Cobra.tamanho += 1
                    pontuacao += 1


                # -------------------------------------------------
                # COLISÃO COM O PRÓPRIO CORPO
                # -------------------------------------------------

                # Se a posição atual da cabeça aparecer mais de uma vez
                # no corpo, a cobra bateu nela mesma.
                if corpo.count([Cobra.x, Cobra.y]) > 1 and Cobra.direcao is not None:

                    # Para a cobra.
                    Cobra.direcao = None

                    # Vai para a animação da morte.
                    estado_jogo = 0.5


                # Desenha a pontuação na tela.
                monitor.blit(texto_pontuacao, (20, Janela.altura - 462))

                # Atualiza a tela.
                pygame.display.flip()


            # =====================================================
            # JOGO PAUSADO
            # =====================================================
            else:

                # Fundo verde mais escuro.
                monitor.fill((0, 140, 0))


                # Pontuação fica acinzentada durante a pausa.
                texto_pontuacao = fonte_tahoma.render(f"Pontuação: {pontuacao}", True, (175, 175, 175), (0, 0, 0))


                # Texto "pause".
                texto_pausa = fonte_tahoma.render("pause", True, (255, 255, 255))
                posicao_pausa = texto_pausa.get_rect(center=(Janela.largura / 2, Janela.altura / 2))


                # Guarda a direção que a cobra estava seguindo antes
                # de ser pausada.
                if Cobra.direcao == "cima":
                    ultima_direcao = "cima"

                elif Cobra.direcao == "esquerda":
                    ultima_direcao = "esquerda"

                elif Cobra.direcao == "baixo":
                    ultima_direcao = "baixo"

                elif Cobra.direcao == "direita":
                    ultima_direcao = "direita"


                # A cobra fica parada enquanto o jogo está pausado.
                Cobra.direcao = None


                # Desenha o corpo com a cor da pausa.
                desenhar_corpo(corpo, True)


                # Desenha a cabeça.
                pygame.draw.rect(monitor, (48, 105, 152), (Cobra.x, Cobra.y, Cobra.largura, Cobra.altura))


                # Desenha a maçã com uma cor mais escura.
                pygame.draw.circle(monitor, (175, 0, 0), (Maca.x, Maca.y), Maca.raio)


                # Desenha a pontuação e as instruções.
                monitor.blit(texto_pontuacao, (20, Janela.altura - 462))
                monitor.blit(texto_pausa, posicao_pausa)
                monitor.blit(texto_esc, (1, Janela.altura - 30))


                # Atualiza a tela.
                pygame.display.flip()


        # =========================================================
        # ANIMAÇÃO DA MORTE
        # =========================================================
        case 0.5:

            # Fundo verde.
            monitor.fill((0, 190, 0))


            # Aumenta o contador a cada frame.
            contador_morte += 1


            # A cada 30 frames, remove uma parte do corpo.
            if contador_morte == 30:

                contador_morte = 0


                # Se ainda houver mais de uma parte do corpo,
                # remove até seis partes.
                if len(corpo) > 1:

                    for _ in range(min(6, len(corpo))):
                        del corpo[0]

                    # Toca o som de dano.
                    som_dano.play()


                # Quando o corpo acaba, vai para o game over.
                else:
                    som_morte.play()
                    estado_jogo = 1


            # Desenha o corpo e a cabeça durante a animação.
            desenhar_corpo(corpo, False)

            pygame.draw.rect(monitor, (48, 105, 152), (Cobra.x, Cobra.y, Cobra.largura, Cobra.altura))

            pygame.draw.circle(monitor, (255, 0, 0), (Maca.x, Maca.y), Maca.raio)


            # Atualiza a tela.
            pygame.display.flip()


        # =========================================================
        # GAME OVER
        # =========================================================
        case 1:

            # Fundo preto.
            monitor.fill((0, 0, 0))


            # Verifica se o jogador conseguiu um novo recorde.
            if pontuacao > recorde and not novo_recorde:

                recorde = pontuacao
                salvar_recorde(recorde)

                novo_recorde = True


            # Cria os textos da tela de game over.
            texto_pontuacao = fonte_tahoma.render(f"Pontuação: {pontuacao}", True, (255, 255, 255))

            texto_recorde = fonte_tahoma.render(f"Recorde: {recorde}", True, (255, 255, 255))


            # Calcula as posições dos textos.
            posicao_pontuacao = texto_pontuacao.get_rect(center=(Janela.largura / 2, Janela.altura / 2))

            posicao_game_over = texto_game_over.get_rect(midbottom=(posicao_pontuacao.centerx, posicao_pontuacao.top - 10))

            posicao_recorde = texto_recorde.get_rect(midtop=(posicao_pontuacao.centerx, posicao_pontuacao.bottom + 10))

            posicao_novo_recorde = texto_novo_recorde.get_rect(midtop=(posicao_pontuacao.centerx, posicao_pontuacao.bottom + 10))


            # Desenha "ESTÁ MORTO!" e a pontuação.
            monitor.blit(texto_game_over, posicao_game_over)
            monitor.blit(texto_pontuacao, posicao_pontuacao)

            # Mostra a instrução para fechar o jogo.
            monitor.blit(texto_esc, (1, Janela.altura - 30))


            # Se bateu o recorde, mostra a mensagem de novo recorde.
            # Caso contrário, mostra o recorde normalmente.
            if novo_recorde:
                monitor.blit(texto_novo_recorde, posicao_novo_recorde)
            else:
                monitor.blit(texto_recorde, posicao_recorde)


            # Atualiza a tela.
            pygame.display.flip()
