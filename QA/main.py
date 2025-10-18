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

        # Загрузка видео
        video_path = Path("videos/waiting.mp4").resolve()
        if video_path.exists():
            self.player.setSource(QUrl.fromLocalFile(str(video_path)))
        else:
            print(f"⚠️ Видео не найдено: {video_path}")

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
    
        self.player.playbackStateChanged.connect(self.on_playback_state_changed)
        self.player.setPosition(0)
        self.player.play()

    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.player.setPosition(0)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LLMVideoApp()
    window.show()
    embedder = Embedder()
    vectors = VectorDB()
    vectors.load('questions.bin', 'questions_dcts.bin')
    sys.exit(app.exec())