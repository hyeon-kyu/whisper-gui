# Whisper GUI (Lightning Whisper MLX 기반)

Lightning Whisper MLX 모델로 음성 파일을 전사하는 간단한 GUI 애플리케이션

---

## 기능

- 로컬에 있는 음성 파일을 선택해 lightning-whisper-mlx 모델로 텍스트 전사
- 모델 설정 및 배치 사이즈 지정 가능
- Tkinter 기반 간단한 GUI

---

## 실행 방법
- Python 설치 (3.12 권장 최신버전에서 lightning-whisper-mlx 설치가 안될 수 있음)
- `pip install -r requirements.txt`를 실행하여 의존성 파일 설치
- `python whisper_gui.py`

---

### 권장 설정

| 사용 환경                  | 모델 크기     | 배치 크기 (`batch_size`) |
|---------------------------|----------------|---------------------------|
| 💻 M1 / M2 / M3 기본형    | `small`        | 8~16                      |
| 💻 M1 Pro / M2 Pro 이상   | `medium`       | 16~24                     |
| 💻 M3 Pro / M4 Pro 이상   | `large-v3` | 24~32          |
| 🖥️ 메모리 48GB 이상 Pro / Max 칩셋 | `large-v3`     | 32 이상        
- 위 표는 참고사항이며, 본인의 사용 환경과 목적에 따라 선택 권장
(ex. 노이즈 환경에서 large-v2가 더 높은 정확도를 보임)
> ⚠️ 너무 큰 모델 또는 높은 `batch_size`를 사용하면 메모리 부족으로 앱이 강제 종료되거나 느려질 수 있습니다.

---

## 주의사항
- `lightning-whisper-mlx`는 내부적으로 Whisper 모델을 다운로드하거나 불러오며, 모델 초기 실행 시 시간이 걸릴 수 있습니다.
- `lightning-whisper-mlx`는 Apple Sillicon(M1/M2/M3/M4 등) 맥에서 최적화된 Whisper 모델 구현체입니다.

---

## 기술 스택
- Python
- Lightning Whisper Mlx
- Tkinter

---

## 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.