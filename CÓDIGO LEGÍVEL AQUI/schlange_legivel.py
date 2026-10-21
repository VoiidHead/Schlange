import os
import sys
from random import randint

import pygame

# ---------------------------------------------------------------------------
# Inicialização do pygame
# ---------------------------------------------------------------------------
pygame.init()

# Tenta inicializar o mixer de áudio; se falhar, o jogo continua sem som.
try:
    pygame.mixer.init()
    som_ativado = True
except pygame.error:
    som_ativado = False


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def caminho_recurso(caminho_relativo):
    """
    Resolve caminhos de arquivos para funcionar tanto em execução normal
    quanto em versão empacotada.
    """
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.abspath(".")
    return os.path.join(base, caminho_relativo)


# Pasta de armazenamento do recorde
pasta_salvamento = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Schlange")
os.makedirs(pasta_salvamento, exist_ok=True)
arquivo_recorde = os.path.join(pasta_salvamento, "besto.txt")


def salvar_recorde(valor):
    with open(arquivo_recorde, "w", encoding="utf-8") as arquivo:
        arquivo.write(str(valor))


def carregar_recorde():
    try:
        with open(arquivo_recorde, "r", encoding="utf-8") as arquivo:
            return int(arquivo.read())
    except (FileNotFoundError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# Configurações do jogo
# ---------------------------------------------------------------------------
class TelaJogo:
    largura = 640
    altura = 480


class Cobra:
    largura = 25
    altura = 25
    x = (TelaJogo.largura / 2) - (largura / 2)
    y = (TelaJogo.altura / 2) - (altura / 2)
    velocidade = 5
    direcao = "parado"
    tamanho = 1


class Maca:
    raio = 20
    x = randint(raio, TelaJogo.largura - raio)
    y = randint(raio, TelaJogo.altura - raio)


# ---------------------------------------------------------------------------
# Lógica de colisão
# ---------------------------------------------------------------------------
def colisao_circulo_retangulo(retangulo, centro_x, centro_y, raio):
    """
    Verifica se um círculo colidiu com um retângulo.
    """
    ponto_x = max(retangulo.left, min(centro_x, retangulo.right))
    ponto_y = max(retangulo.top, min(centro_y, retangulo.bottom))

    dx = centro_x - ponto_x
    dy = centro_y - ponto_y

    return (dx ** 2) + (dy ** 2) <= (raio ** 2)


def desenhar_corpo(corpo_cobra, pausado):
    """
    Desenha o corpo da cobra.
    Quando pausado, o corpo fica mais escuro.
    """
    cor = (255, 212, 59) if not pausado else (205, 162, 9)

    for posicao in corpo_cobra[:-1]:
        pygame.draw.rect(
            tela_jogo,
            cor,
            (posicao[0], posicao[1], Cobra.largura, Cobra.altura),
        )


# ---------------------------------------------------------------------------
# Reinício do jogo
# ---------------------------------------------------------------------------
def reiniciar_jogo():
    global pontos, tempo_animacao, estado_jogo, pausado, novo_recorde

    Cobra.x = (TelaJogo.largura / 2) - (Cobra.largura / 2)
    Cobra.y = (TelaJogo.altura / 2) - (Cobra.altura / 2)
    Cobra.tamanho = 1
    Cobra.direcao = "parado"

    corpo_cobra.clear()

    pontos = 0
    novo_recorde = False
    tempo_animacao = 0
    pausado = False

    Maca.x = randint(Maca.raio, TelaJogo.largura - Maca.raio)
    Maca.y = randint(Maca.raio, TelaJogo.altura - Maca.raio)

    estado_jogo = "jogando"


# ---------------------------------------------------------------------------
# Possíveis estados da variável principal:
# - "jogando": o jogo está em execução
# - "animacao": a cobra colidiu e a animação de morte está em andamento
# - "game_over": a tela de fim de jogo está ativa
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Variáveis globais do jogo
# ---------------------------------------------------------------------------
pontos = 0
recorde = carregar_recorde()
corpo_cobra = []
novo_recorde = False
ultima_direcao = "direita"

# Fontes
fonte = pygame.font.SysFont("Tahoma", 24)
texto_fechar = fonte.render("esc para fechar o jogo", True, (255, 255, 255))
texto_game_over = fonte.render("ESTÁ MORTO!", True, (255, 255, 255))
texto_novo_recorde = fonte.render("NOVO RECORDE!!", True, (255, 255, 255))

estado_jogo = "jogando"
pausado = False
tempo_animacao = 0

# Janela principal
tela_jogo = pygame.display.set_mode((TelaJogo.largura, TelaJogo.altura))
pygame.display.set_caption("Schlange")

# Ícone do jogo
icone = pygame.transform.smoothscale(
    pygame.image.load(caminho_recurso("icon/icon.png")),
    (32, 32),
)
pygame.display.set_icon(icone)

relogio = pygame.time.Clock()

# Sons
if som_ativado:
    som_comer = pygame.mixer.Sound(caminho_recurso("sfx/hungrySchlange.wav"))
    som_dano = pygame.mixer.Sound(caminho_recurso("sfx/slicedSchlange.wav"))
    som_morte = pygame.mixer.Sound(caminho_recurso("sfx/SchlangeIsDead.wav"))


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------
while True:
    relogio.tick(60)

    # Captura eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.WINDOWMINIMIZED:
            pausado = True

        if evento.type == pygame.KEYDOWN:
            if estado_jogo == "jogando":
                if not pausado:
                    if evento.key == pygame.K_ESCAPE:
                        pausado = True

                    elif evento.key in [pygame.K_w, pygame.K_UP]:
                        if Cobra.direcao != "baixo":
                            Cobra.direcao = "cima"

                    elif evento.key in [pygame.K_a, pygame.K_LEFT]:
                        if Cobra.direcao != "direita":
                            Cobra.direcao = "esquerda"

                    elif evento.key in [pygame.K_s, pygame.K_DOWN]:
                        if Cobra.direcao != "cima":
                            Cobra.direcao = "baixo"

                    elif evento.key in [pygame.K_d, pygame.K_RIGHT]:
                        if Cobra.direcao != "esquerda":
                            Cobra.direcao = "direita"

                else:
                    if evento.key == pygame.K_ESCAPE:
                        if pontos > recorde:
                            recorde = pontos
                            salvar_recorde(recorde)
                        pygame.quit()
                        sys.exit()

                    elif evento.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                        Cobra.direcao = ultima_direcao
                        pausado = False

            elif estado_jogo == "animacao":
                if evento.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                    if som_ativado:
                        som_morte.play()
                    estado_jogo = "game_over"

                if evento.key == pygame.K_ESCAPE:
                    if pontos > recorde:
                        recorde = pontos
                        salvar_recorde(recorde)
                    pygame.quit()
                    sys.exit()

            elif estado_jogo == "game_over":
                if evento.key in [pygame.K_r, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                    reiniciar_jogo()

                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # -----------------------------------------------------------------------
    # Verificação do estado do jogo
    # -----------------------------------------------------------------------
    match estado_jogo:
        case "jogando":
            if not pausado:
                tela_jogo.fill((0, 190, 0))
                texto_pontuacao = fonte.render(f"Pontuação: {pontos}", True, (255, 255, 255), (0, 0, 0))

                # Movimento da cobra
                if Cobra.direcao == "cima":
                    Cobra.y -= Cobra.velocidade
                elif Cobra.direcao == "esquerda":
                    Cobra.x -= Cobra.velocidade
                elif Cobra.direcao == "baixo":
                    Cobra.y += Cobra.velocidade
                elif Cobra.direcao == "direita":
                    Cobra.x += Cobra.velocidade

                # Teleporte da borda para o lado oposto
                if Cobra.x >= TelaJogo.largura:
                    Cobra.x = 0
                elif Cobra.x < 0:
                    Cobra.x = TelaJogo.largura

                if Cobra.y >= TelaJogo.altura:
                    Cobra.y = 0
                elif Cobra.y < 0:
                    Cobra.y = TelaJogo.altura

                # Guarda a posição atual da cabeça no corpo
                corpo_cobra.append([Cobra.x, Cobra.y])

                # Limita o tamanho do corpo
                if len(corpo_cobra) > Cobra.tamanho * 6:
                    del corpo_cobra[0]

                # Desenha o corpo
                if Cobra.direcao != "parado":
                    desenhar_corpo(corpo_cobra, False)

                # Cabeça da cobra
                retangulo_cobra = pygame.draw.rect(
                    tela_jogo,
                    (48, 105, 152),
                    (Cobra.x, Cobra.y, Cobra.largura, Cobra.altura),
                )

                # Maçã
                pygame.draw.circle(tela_jogo, (255, 0, 0), (Maca.x, Maca.y), Maca.raio)

                # Colisão com a maçã
                if colisao_circulo_retangulo(retangulo_cobra, Maca.x, Maca.y, Maca.raio):
                    Maca.x = randint(Maca.raio, TelaJogo.largura - Maca.raio)
                    Maca.y = randint(Maca.raio, TelaJogo.altura - Maca.raio)

                    while colisao_circulo_retangulo(retangulo_cobra, Maca.x, Maca.y, Maca.raio):
                        Maca.x = randint(Maca.raio, TelaJogo.largura - Maca.raio)
                        Maca.y = randint(Maca.raio, TelaJogo.altura - Maca.raio)

                    if som_ativado:
                        som_comer.play()

                    Cobra.tamanho += 1
                    pontos += 1

                # Verifica colisão com o próprio corpo
                if corpo_cobra.count([Cobra.x, Cobra.y]) > 1 and Cobra.direcao != "parado":
                    Cobra.direcao = "parado"
                    estado_jogo = "animacao"

                tela_jogo.blit(texto_pontuacao, (20, TelaJogo.altura - 462))
                pygame.display.flip()

            else:
                # Tela de pausa
                tela_jogo.fill((0, 140, 0))
                texto_pontuacao_pausada = fonte.render(f"Pontuação: {pontos}", True, (175, 175, 175), (0, 0, 0))
                texto_pausa = fonte.render("pause", True, (255, 255, 255))
                posicao_pausa = texto_pausa.get_rect(center=(TelaJogo.largura / 2, TelaJogo.altura / 2))

                # Guarda a última direção válida
                if Cobra.direcao == "cima":
                    ultima_direcao = "cima"
                elif Cobra.direcao == "esquerda":
                    ultima_direcao = "esquerda"
                elif Cobra.direcao == "baixo":
                    ultima_direcao = "baixo"
                elif Cobra.direcao == "direita":
                    ultima_direcao = "direita"

                Cobra.direcao = "parado"

                desenhar_corpo(corpo_cobra, True)
                pygame.draw.rect(
                    tela_jogo,
                    (48, 105, 152),
                    (Cobra.x, Cobra.y, Cobra.largura, Cobra.altura),
                )
                pygame.draw.circle(tela_jogo, (175, 0, 0), (Maca.x, Maca.y), Maca.raio)

                tela_jogo.blit(texto_pontuacao_pausada, (20, TelaJogo.altura - 462))
                tela_jogo.blit(texto_pausa, posicao_pausa)
                tela_jogo.blit(texto_fechar, (1, TelaJogo.altura - 30))
                pygame.display.flip()

        case "animacao":
            # Animação de colisão
            tela_jogo.fill((0, 190, 0))
            tempo_animacao += 1

            if tempo_animacao == 30:
                tempo_animacao = 0

                if len(corpo_cobra) > 1:
                    for _ in range(min(6, len(corpo_cobra))):
                        del corpo_cobra[0]

                    if som_ativado:
                        som_dano.play()
                else:
                    if som_ativado:
                        som_morte.play()
                    estado_jogo = "game_over"

            desenhar_corpo(corpo_cobra, False)
            pygame.draw.rect(
                tela_jogo,
                (48, 105, 152),
                (Cobra.x, Cobra.y, Cobra.largura, Cobra.altura),
            )
            pygame.draw.circle(tela_jogo, (255, 0, 0), (Maca.x, Maca.y), Maca.raio)

            pygame.display.flip()

        case "game_over":
            # Tela de game over
            tela_jogo.fill((0, 0, 0))

            if pontos > recorde and not novo_recorde:
                recorde = pontos
                salvar_recorde(recorde)
                novo_recorde = True

            texto_pontuacao = fonte.render(f"Pontuação: {pontos}", True, (255, 255, 255))
            texto_recorde = fonte.render(f"Recorde: {recorde}", True, (255, 255, 255))

            posicao_pontuacao = texto_pontuacao.get_rect(center=(TelaJogo.largura / 2, TelaJogo.altura / 2))
            posicao_game_over = texto_game_over.get_rect(midbottom=(posicao_pontuacao.centerx, posicao_pontuacao.top - 10))
            posicao_recorde = texto_recorde.get_rect(midtop=(posicao_pontuacao.centerx, posicao_pontuacao.bottom + 10))
            posicao_novo_recorde = texto_novo_recorde.get_rect(midtop=(posicao_pontuacao.centerx, posicao_pontuacao.bottom + 10))

            tela_jogo.blit(texto_game_over, posicao_game_over)
            tela_jogo.blit(texto_pontuacao, posicao_pontuacao)
            tela_jogo.blit(texto_fechar, (1, TelaJogo.altura - 30))

            if novo_recorde:
                tela_jogo.blit(texto_novo_recorde, posicao_novo_recorde)
            else:
                tela_jogo.blit(texto_recorde, posicao_recorde)

            pygame.display.flip()
