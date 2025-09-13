from typing import List

class DebateLogger:
    def __init__(self):
        self.entries: List[str] = []

    def log(self, message: str):
        self.entries.append(message)

    def get_transcript(self) -> List[str]:
        return self.entries

    def save_to_file(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            for entry in self.entries:
                f.write(entry + '\n')
