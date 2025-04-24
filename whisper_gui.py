import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar
from tkinter.scrolledtext import ScrolledText
from lightning_whisper_mlx import LightningWhisperMLX

class WhisperApp:
    def __init__(self, root):
        self.root = root
        root.title('Lightning Whisper MLX GUI')
        
        self.whisper = None
        
        # 파일 선택
        tk.Label(root, text='음성 파일:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.file_var = tk.StringVar()
        tk.Entry(root, textvariable=self.file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text='찾아보기', command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        
        # 모델 선택
        tk.Label(root, text='모델:').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.model_var = tk.StringVar(value='medium')
        models = ['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3']
        tk.OptionMenu(root, self.model_var, *models).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # 배치 크기 설정
        tk.Label(root, text='배치 크기:').grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.batch_var = StringVar(value='16')
        batch_frame = tk.Frame(root)
        batch_frame.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        batch_entry = tk.Entry(batch_frame, textvariable=self.batch_var, width=5)
        batch_entry.pack(side=tk.LEFT)
        
        # 언어 선택
        tk.Label(root, text='언어:').grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.lang_var = tk.StringVar(value='auto')
        langs = ['auto', 'en', 'ko', 'ja', 'es']
        tk.OptionMenu(root, self.lang_var, *langs).grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Transcribe 버튼
        self.transcribe_button = tk.Button(root, text='Transcribe', command=self.start_transcription)
        self.transcribe_button.grid(row=4, column=1, pady=10)
        
        # 결과 출력
        tk.Label(root, text='결과:').grid(row=5, column=0, padx=5, pady=5, sticky='nw')
        result_frame = tk.Frame(root)
        result_frame.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky='nw')
        
        output_frame = tk.Frame(result_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_box = ScrolledText(output_frame, width=80, height=20, state='disabled')
        self.output_box.pack(fill=tk.BOTH, expand=True)
        
        copy_btn = tk.Button(output_frame, text="복사", command=self.copy_to_clipboard)
        copy_btn.pack(pady=5)
        
        # 모델 상태
        self.status_var = tk.StringVar(value='모델 상태: 로드되지 않음')
        tk.Label(root, textvariable=self.status_var).grid(row=6, column=1, padx=5, pady=5, sticky='w')

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Audio Files', '*.mp3 *.wav *.m4a'), ('All Files', '*.*')]
        )
        if file_path:
            self.file_var.set(file_path)

    def get_batch_size(self):
        """배치 크기를 가져오고 유효성을 검사합니다."""
        try:
            batch_size = int(self.batch_var.get())
            if batch_size < 1 or batch_size > 64:
                messagebox.showwarning('경고', '배치 크기는 1~64 사이여야 합니다.')
                return 16
            return batch_size
        except ValueError:
            messagebox.showwarning('경고', '배치 크기는 정수여야 합니다.')
            self.batch_var.set('16')
            return 16

    def load_model(self):
        model_name = self.model_var.get()
        batch_size = self.get_batch_size()
        
        try:
            self.update_status(f"모델 로딩 중: {model_name}, 배치 크기: {batch_size}...")
            self.whisper = LightningWhisperMLX(
                model=model_name,
                batch_size=batch_size,
                quant=None,
            )
            self.update_status(f"모델 상태: {model_name} 로드됨, 배치 크기: {batch_size}")
            return True
        except Exception as e:
            self.update_status(f"모델 로드 실패: {e}")
            messagebox.showerror('오류', f'모델 로드 실패: {e}')
            return False

    def start_transcription(self):
        file_path = self.file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror('오류', '유효한 파일을 선택하세요.')
            return
        
        self.transcribe_button.config(state=tk.DISABLED)    
        threading.Thread(target=self.transcribe_file, args=(file_path,), daemon=True).start()

    def transcribe_file(self, file_path):
        self.update_output('모델을 확인하는 중...\n')
        
        # 모델 재로드
        try:
            batch_size = self.get_batch_size()
            current_model = self.model_var.get()
            
            if self.whisper is None:
                if not self.load_model():
                    return
            else:
                need_reload = False
                
                current_settings = (current_model, batch_size)
                
                if not hasattr(self, 'current_settings'):
                    need_reload = True
                elif self.current_settings != current_settings:
                    need_reload = True
                
                if need_reload and not self.load_model():
                    return
                
                self.current_settings = current_settings
        except ValueError:
            self.update_output('배치 크기가 유효하지 않습니다.')
            return
        except Exception as e:
            self.update_output(f'모델 속성 접근 오류로 모델을 다시 로드합니다: {e}')
            if not self.load_model():
                return
        
        self.update_output('Transcribing...\n')
        try:
            language = self.lang_var.get()
            if language == 'auto':
                language = None
            
            res = self.whisper.transcribe(audio_path=file_path, language=language)
            text = res.get('text', '')
            self.update_output(text)
        except Exception as e:
            self.update_output(f'Error: {e}')
        finally:
            self.root.after(0, lambda: self.transcribe_button.config(state=tk.NORMAL))

    def update_output(self, content):
        self.output_box.config(state='normal')
        self.output_box.delete('1.0', tk.END)
        self.output_box.insert(tk.END, content)
        self.output_box.config(state='disabled')

    def update_status(self, status):
        self.status_var.set(status)

    # 클립보드 복사   
    def copy_to_clipboard(self):
        try:
            self.output_box.config(state='normal')
            content = self.output_box.get('1.0', tk.END).strip()
            self.output_box.config(state='disabled')
            
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            
            temp_status = self.status_var.get()
            self.update_status("텍스트가 클립보드에 복사되었습니다.")
            
            self.root.after(3000, lambda: self.status_var.set(temp_status))
        except Exception as e:
            messagebox.showerror('오류', f'클립보드에 복사하는 중 오류 발생: {e}')

if __name__ == '__main__':
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
