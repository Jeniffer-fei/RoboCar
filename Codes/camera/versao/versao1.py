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
    ll, lr = 110, 120  # Comprimento mínimo das linhas
    gl, gr = 5, 9      # Gap máximo entre segmentos de linha

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 1)
    canny = cv.Canny(blurred, 50, 210)

    cropped_left, cropped_right = split_image(canny)

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

    def combine_lines(lines1, lines2):
        """
        Combina linhas detectadas de dois lados com base na proximidade.
        """
        combined_lines = []
        if lines1 is not None and lines2 is not None:
            for line1 in lines1:
                x1, y1, x2, y2 = line1[0]
                for line2 in lines2:
                    x3, y3, x4, y4 = line2[0]
                    # Calcula a distância entre os pontos iniciais das linhas
                    distance = np.sqrt((x3 - x1)**2 + (y3 - y1)**2)
                    if distance < 50:  # Limiar para fusão
                        combined_lines.append((line1, line2))
        return combined_lines

    lines_left = cv.HoughLinesP(cropped_left, 1, np.pi / 180, 50, minLineLength=ll, maxLineGap=gl)
    lines_right = cv.HoughLinesP(cropped_right, 1, np.pi / 180, 50, minLineLength=lr, maxLineGap=gr)

    lines_left = filter_lines(lines_left)
    lines_right = filter_lines(lines_right)

    combined_lines = combine_lines(lines_left, lines_right)
    
    return lines_left, lines_right, combined_lines

def draw_lines(image, lines_left, lines_right, combined_lines):
    """
    Desenha as linhas detectadas na imagem.
    """
    line_image = np.zeros_like(image)
    height, width = image.shape[:2]

    if lines_left:
        for line in lines_left:
            x1, y1, x2, y2 = line[0]
            cv.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    if lines_right:
        for line in lines_right:
            x1, y1, x2, y2 = line[0]
            x1 += width // 2
            x2 += width // 2
            cv.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if combined_lines:
        for line1, line2 in combined_lines:
            x1, y1, x2, y2 = line1[0]
            x3, y3, x4, y4 = line2[0]
            # Desenha as linhas combinadas
            cv.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv.line(line_image, (x3 + width // 2, y3), (x4 + width // 2, y4), (255, 0, 0), 2)

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
        lines_left, lines_right, combined_lines = detect_lines(roi)
        line_image = draw_lines(frame, lines_left, lines_right, combined_lines)
        
        cv.imshow('Linhas Detectadas', line_image)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
