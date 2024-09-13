import cv2 as cv
import numpy as np

def region_of_interest(image):
    height = image.shape[0]
    width = image.shape[1]
    polygons = np.array([[(0, height), (width, height), (width, height // 2), (0, height // 2)]], dtype=np.int32)
    mask = np.zeros_like(image)
    cv.fillPoly(mask, polygons, (255, 255, 255))
    masked_image = cv.bitwise_and(image, mask)
    return masked_image

def split_image(image):
    width = image.shape[1]
    mid_x = width // 2
    left_split = image[:, :mid_x-1]
    right_split = image[:, mid_x+1:]
    return left_split, right_split

def detect_lines(image):
    ll = 110
    lr = 120
    gl = 5
    gr = 9
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 1)
    canny = cv.Canny(blurred, 50, 210)
    cropped_image = region_of_interest(canny)  # Apply ROI mask to the edge-detected image
    cropped_left, cropped_right = split_image(cropped_image)

    def filter_lines(lines):
        filtered_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx = x2 - x1
            dy = y2 - y1
            if dx != 0:
                angle = np.arctan2(dy, dx) * 180 / np.pi
                if not (-10 < angle < 10):
                    filtered_lines.append(line)
        return filtered_lines

    lines_left = cv.HoughLinesP(cropped_left, 1, np.pi / 180, 50, minLineLength=ll, maxLineGap=gl)
    lines_right = cv.HoughLinesP(cropped_right, 1, np.pi / 180, 50, minLineLength=lr, maxLineGap=gr)
    
    if lines_left is not None:
        lines_left = filter_lines(lines_left)
    if lines_right is not None:
        lines_right = filter_lines(lines_right)
        
    return lines_left, lines_right

def find_rectangles(lines):
    rectangles = []
    if lines is None:
        return rectangles

    # Extrair pontos das linhas
    points = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        points.append((x1, y1))
        points.append((x2, y2))
    
    points = np.array(points)
    if len(points) < 4:
        return rectangles

    # Encontrar os pontos extremos
    x_min, y_min = np.min(points, axis=0)
    x_max, y_max = np.max(points, axis=0)
    
    # Adicionar retângulo
    rectangles.append([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
    
    return rectangles

def draw_lines(image, lines, color=(0, 255, 0), thickness=2):
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv.line(image, (x1, y1), (x2, y2), color, thickness)

def combine_lines(lines_left, lines_right, angle_threshold=np.pi / 180 * 10):
    combined_lines = []
    
    if lines_left is not None and lines_right is not None:
        for line_left in lines_left:
            x1_l, y1_l, x2_l, y2_l = line_left[0]
            for line_right in lines_right:
                x1_r, y1_r, x2_r, y2_r = line_right[0]
                
                # Verifica se as linhas são aproximadamente paralelas
                dx_l = x2_l - x1_l
                dy_l = y2_l - y1_l
                dx_r = x2_r - x1_r
                dy_r = y2_r - y1_r
                
                angle_l = np.arctan2(dy_l, dx_l) * 180 / np.pi
                angle_r = np.arctan2(dy_r, dx_r) * 180 / np.pi
                
                if abs(angle_l - angle_r) < angle_threshold or abs(abs(angle_l - angle_r) - 180) < angle_threshold:
                    combined_lines.append(((x1_l, y1_l, x2_l, y2_l), (x1_r, y1_r, x2_r, y2_r)))
                    break
    
    return combined_lines
     

def draw_rectangles(image, rectangles, color=(255, 255, 0), thickness=2):
    for rectangle in rectangles:
        for i in range(len(rectangle)):
            pt1 = rectangle[i]
            pt2 = rectangle[(i + 1) % 4]
            cv.line(image, pt1, pt2, color, thickness)

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

        lines_left, lines_right = detect_lines(frame)

        # Criar cópias das imagens para desenhar linhas
        output = frame.copy()
        height, width = frame.shape[:2]
        mid_x = width // 2
        img_left = output[:, :mid_x]
        img_right = output[:, mid_x:]

# Encontrar e desenhar retângulos detectados
        rectangles_left = find_rectangles(lines_left)
        rectangles_right = find_rectangles(lines_right)
        
        
        
        # Desenhar retângulos combinados
        # Desenhar linhas detectadas nas imagens
        draw_lines(img_left, lines_left)
        draw_lines(img_right, lines_right)
        draw_rectangles(output, rectangles_left)
        draw_rectangles(output, rectangles_right)

        # Combinar linhas detectadas
        combined_lines = combine_lines(lines_left, lines_right)

        # Desenhar linhas combinadas nas imagens
        for line in combined_lines:
            (x1_l, y1_l, x2_l, y2_l), (x1_r, y1_r, x2_r, y2_r) = line
            cv.line(output, (x1_l, y1_l), (x2_l, y2_l), (0, 255, 255), 2)
            cv.line(output, (x1_r + mid_x, y1_r), (x2_r + mid_x, y2_r), (0, 255, 255), 2)

        
        # Mostrar imagem com retângulos
        cv.imshow('Rectangles Detected', output)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
