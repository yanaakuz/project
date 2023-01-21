# импортирование нужных библиотек
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# переменная для фиксирования ключевых позиций (верх-низ)
moment_pose = ""

# счетчик самих отжиманий
count = 0

# изображение с камеры
cap = cv2.VideoCapture(0)
with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # список с координатами точек тела
        coords = []

        # хранение изображения и определение на нем позы
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # рисование ключевых точек позы
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                )

            # цикл для фиксирования координат
            for id, temp in enumerate(results.pose_landmarks.landmark):
                h, w, t = image.shape

                # умножаем координаты на размеры картинки
                x = int(temp.x * w)
                y = int(temp.y * h)
                coords.append([id, x, y])

        if len(coords) != 0:
            if (coords[14][2] and coords[13][2] <= coords[12][2] and coords[11][2]): # координата "y" каждого плеча ниже каждого локтя
                moment_pose = "вниз"
            if (coords[12][2] and coords[11][2] <= coords[14][2] and coords[13][2]) and moment_pose == "вниз": # координата "y" каждого плеча выше каждого локтя, при это предыдущее положение было снизу => произошло отжимание
                moment_pose = "вверх"
                count += 1


        # шрифт для надписи счетчика
        font = cv2.FONT_HERSHEY_SIMPLEX

        # вставка текста на видео
        cv2.putText(image,
                    str(count),
                    (50, 50),
                    font, 1,
                    (0, 0, 0),
                    2,
                    cv2.LINE_4)

        # вывод видео
        cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()