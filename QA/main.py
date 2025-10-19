from db_access import VectorDB
from embedder import Embedder

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QGraphicsView, QGraphicsScene
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem 
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtCore import QSizeF
from PyQt6.QtCore import QTimer, QEvent


def generate_response(prompt: str) -> str:
    result = vectors.search(embedder.embed(prompt), k=1)
    if result[0][0] > 0.85:
        ans = result[2][0]["answer"]
    else:
        ans = 'Я не знаю ответа на этот вопрос' 
    return ans

class LLMVideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM + Видео (PyQt6, без QVideoWidget)")
        self.resize(850, 700)
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        self.move(x, 0)

        # === Видео через QGraphicsView ===
        self.scene = QGraphicsScene()
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        self.video_view = QGraphicsView(self.scene)
        self.video_view.setFixedSize(600, 800)
        self.video_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.video_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.video_view.setStyleSheet("background-color: #1e1e1e;")

        # Установка размера видео (опционально)
        self.video_item.setSize(QSizeF(self.video_view.size()))

        # === Медиаплеер ===
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_item)        

        # === GUI ===
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        self.response_box.setPlaceholderText("Ответ от LLM...")

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Введите запрос...")
        self.input_line.returnPressed.connect(self.on_submit)

        self.submit_btn = QPushButton("Отправить")
        self.submit_btn.clicked.connect(self.on_submit)

        layout = QVBoxLayout()
        layout.addWidget(self.video_view)
        layout.addWidget(self.response_box, stretch=1)
        layout.addWidget(self.input_line)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)
    
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

        self.exit_animation_playing = False
        self.exit_requested = False
        self.current_state = None

        self.play_video("QA/videos/hello.mp4", "hello")

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print(self.current_state)
            if self.current_state == "hello":
                self.play_video("QA/videos/idle.mp4", "idle")
            elif self.current_state == "ask":
                self.play_video("QA/videos/idle.mp4", "idle")
            else:
                self.play_video("QA/videos/idle.mp4", "idle")

    def play_video(self, filename: str, state: str):
        path = Path(filename).resolve()
        if not path.exists():
            print(f"⚠️ Файл не найден: {path}")
            return
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        print(path, state)
        self.current_state = state
        self.player.play()

    def on_submit(self):
        text = self.input_line.text().strip()
        if not text:
            return
        try:
            response = generate_response(text)
        except Exception as e:
            response = f"Ошибка: {e}"

        self.response_box.setText(response)

        self.input_line.clear()

        self.play_video("QA/videos/ask.mp4", "ask")
    
    def closeEvent(self, event):
        if not self.exit_requested:
            # Первый раз: запускаем анимацию выхода
            event.ignore()  # ← отменяем закрытие
            self.start_exit_animation()
        else:
            # Второй раз (после анимации): разрешаем закрытие
            event.accept()

    def start_exit_animation(self):
        if self.exit_animation_playing:
            return
        self.exit_animation_playing = True
        self.exit_requested = True

        # Загружаем и проигрываем анимацию выхода
        self.player.setSource(QUrl.fromLocalFile(str(Path("QA/videos/bye.mp4").resolve())))
        self.player.play()

        # Через N секунд — закрыть приложение
        # (подбери время под длительность exit.mp4)
        QTimer.singleShot(4000, self.final_close)  # 3 секунды

    def final_close(self):
        # Принудительно закрываем (игнорируя closeEvent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LLMVideoApp()
    window.show()
    embedder = Embedder()
    vectors = VectorDB()
    vectors.load(str(Path('QA/questions.bin').resolve()),  str(Path('QA/questions_dcts.bin').resolve()))
    sys.exit(app.exec())