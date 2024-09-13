import cv2 as cv
import numpy as np

def region_of_interest(image):
    """
    Cria uma máscara para a região de interesse na imagem, mantendo apenas a parte superior da imagem.
    """
    height, width = image.shape[:2]
    polygons = np.array([[(0, height), (width, height), (width, height // 2), (0, height // 2)]], dtype=np.int32)
    mask = np.zeros_like(image)
    cv.fillPoly(mask, polygons, (255, 255, 255))
    masked_image = cv.bitwise_and(image, mask)
    return masked_image

def split_image(image):
    """
    Divide a imagem verticalmente em duas partes: esquerda e direita.
    """
    width = image.shape[1]
    mid_x = width // 2
    return image[:, :mid_x], image[:, mid_x:]

def detect_lines(image):
    """
    Detecta linhas na imagem utilizando a Transformada de Hough.
    """
    min_line_length = 110  # Comprimento mínimo das linhas
    max_line_gap = 20     # Gap máximo entre segmentos de linha

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 1)
    canny = cv.Canny(blurred, 50, 210)

    cropped_left, cropped_right = split_image(canny)

    # Detecta as linhas em cada lado usando HoughLinesP
    lines_left = cv.HoughLinesP(cropped_left, 1, np.pi / 180, 50, minLineLength=min_line_length, maxLineGap=max_line_gap)
    lines_right = cv.HoughLinesP(cropped_right, 1, np.pi / 180, 50, minLineLength=min_line_length, maxLineGap=max_line_gap)

    # Filtra as linhas para manter apenas as que estão quase verticais
    lines_left_filtered = filter_lines(lines_left)
    lines_right_filtered = filter_lines(lines_right)


    return lines_left_filtered, lines_right_filtered

def filter_lines(lines):
    """
    Filtra linhas para manter apenas aquelas que estão quase verticais.
    """
    if lines is None:
        return []
    filtered_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx, dy = x2 - x1, y2 - y1
        if dx != 0:
            angle = np.arctan2(dy, dx) * 180 / np.pi
            if not (-10 < angle < 10):
                filtered_lines.append(line)
    return filtered_lines

def draw_lines(image, lines_left, lines_right):
    """
    Desenha as linhas detectadas na imagem, junto com uma linha horizontal entre duas linhas
    e uma linha vertical a partir do ponto médio dessa linha horizontal.
    """
    line_image = np.zeros_like(image)
    height, width = image.shape[:2]

    # Variáveis para armazenar os pontos para a linha horizontal
    pt1_left = pt1_right = None
    pt2_left = pt2_right = None

    # Desenhar as linhas do lado esquerdo (verde)
    if lines_left:
        for line in lines_left:
            x1, y1, x2, y2 = line[0]
            cv.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if pt1_left is None:  # Salvar o ponto superior da primeira linha
                if y1 > y2:
                    pt1_left = (x1, y1)
                else:
                    pt1_left = (x2, y2)
                if y1 < y2:
                    pt2_left = (x1, y1)
                else:
                    pt2_left = (x2, y2)

    # Desenhar as linhas do lado direito (azul)
    if lines_right:
        for line in lines_right:
            x1, y1, x2, y2 = line[0]
            x1 += width // 2
            x2 += width // 2
            cv.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            if pt1_right is None:  # Salvar o ponto superior da primeira linha
                if y1 > y2:
                    pt1_right = (x1, y1)
                else:
                    pt1_right = (x2, y2)
                if y1 < y2:
                    pt2_right = (x1, y1)
                else:
                    pt2_right = (x2, y2)

    # Desenhar a linha horizontal entre os dois pontos e a linha vertical no meio
    if pt1_left and pt1_right:
        # Desenhar linha horizontal entre os dois pontos
        cv.line(line_image, pt1_left, pt1_right, (0, 255, 255), 2)
        print(pt1_left, pt1_right )

        # Calcular o ponto médio da linha horizontal
        mid_x1 = (pt1_left[0] + pt1_right[0]) // 2
        mid_y1 = (pt1_left[1] + pt1_right[1]) // 2    

    if pt2_left and pt2_right:
        # Desenhar linha horizontal entre os dois pontos
        cv.line(line_image, pt2_left, pt2_right, (0, 255, 255), 2)
        #print(pt2_left, pt2_right )

        # Calcular o ponto médio da linha horizontal
        mid_x2 = (pt2_left[0] + pt2_right[0]) // 2
        mid_y2 = (pt2_left[1] + pt2_right[1]) // 2      

    # Desenhar a linha vertical vermelha e  a partir do ponto médio (controlando o tamanho)
    cv.line(line_image, (mid_x1, mid_y1), (mid_x1, mid_y2), (0, 0, 255), 2)
    cv.line(line_image, (mid_x2, mid_y1), (mid_x2, mid_y2), (240, 0, 255), 2)

    #Desenhar a linha da hipotenusa
    cv.line(line_image, (mid_x2, mid_y1), (mid_x1, mid_y2), (240, 99, 230), 2)

    # Combinar a imagem original com as linhas desenhadas
    combined_image = cv.addWeighted(image, 0.8, line_image, 1, 0)
    return combined_image


def main():
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Erro ao abrir a câmera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Não foi possível capturar o quadro.")
            break

        roi = region_of_interest(frame)
        lines_left, lines_right = detect_lines(roi)
        line_image = draw_lines(frame, lines_left, lines_right, )
        
        cv.imshow('Linhas Detectadas', line_image)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
