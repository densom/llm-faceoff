from typing import List, Dict, Any
from datetime import datetime
from llm_faceoff.llms.adapter_interface import LLMAdapterInterface
from llm_faceoff.config import ConfigManager
from llm_faceoff.debate.logger import DebateLogger
from llm_faceoff.debate.output_formatter import MarkdownFormatter, JSONFormatter, HTMLFormatter

class DebateOrchestrator:
    def __init__(self, llm_adapters: List[LLMAdapterInterface], config: ConfigManager):
        self.llm_adapters = llm_adapters
        self.config = config
        self.logger = DebateLogger()
        self.current_turn = 0

        # Session metadata
        self.session_id = "session-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        self.participants: List[Dict[str, Any]] = []
        self.status = "initialized"
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.started_at = None
        self.completed_at = None
        self.messages: List[Dict[str, Any]] = []
        self.statistics: Dict[str, Any] = {}

        # Initialize participants from adapters
        for idx, adapter in enumerate(llm_adapters):
            participant = {
                'id': f'p{idx+1}',
                'name': adapter.name,
                'provider': adapter.name.split()[0] if adapter.name else 'Unknown',
                'model': '',  # Model info can be added if available
                'role': 'proposition' if idx == 0 else 'opposition' if idx == 1 else 'moderator'
            }
            self.participants.append(participant)

    def start_debate(self, topic: str):
        self.status = "active"
        self.started_at = datetime.utcnow().isoformat() + "Z"
        self.logger.log(f"Debate started on topic: {topic}")

        rounds = self.config.get('rounds', 1) or 1

        # Opening statements
        for idx, adapter in enumerate(self.llm_adapters):
            response = adapter.generate_response(topic, '')
            self.logger.log(f"{adapter.name} (Opening): {response}")
            self._add_message(idx, response, "Opening Statement")

        # Rebuttal rounds
        for round_number in range(1, rounds):
            for idx, adapter in enumerate(self.llm_adapters):
                context = self.logger.get_transcript()
                context_str = '\n'.join(context)
                response = adapter.generate_response(topic, context_str)
                self.logger.log(f"{adapter.name} (Rebuttal Round {round_number}): {response}")
                self._add_message(idx, response, f"Rebuttal Round {round_number}")

        # Closing statements
        for idx, adapter in enumerate(self.llm_adapters):
            context = self.logger.get_transcript()
            context_str = '\n'.join(context)
            response = adapter.generate_response(topic, context_str)
            self.logger.log(f"{adapter.name} (Closing): {response}")
            self._add_message(idx, response, "Closing Statement")

        self.logger.log("Debate ended.")
        self.status = "completed"
        self.completed_at = datetime.utcnow().isoformat() + "Z"

        # Compute statistics
        self._compute_statistics()

    def _add_message(self, participant_idx: int, content: str, msg_type: str):
        participant = self.participants[participant_idx]
        self.current_turn += 1
        message = {
            'id': f'm{self.current_turn}',
            'participant_id': participant['id'],
            'content': content,
            'type': msg_type,
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'metadata': {}
        }
        self.messages.append(message)

    def _compute_statistics(self):
        total_messages = len(self.messages)
        total_participants = len(self.participants)
        if total_messages == 0:
            self.statistics = {
                'total_messages': 0,
                'total_participants': total_participants,
                'duration_minutes': 0,
                'avg_message_length': 0,
                'participant_stats': {}
            }
            return

        # Duration in minutes
        start_time = datetime.fromisoformat(self.started_at.replace('Z', '+00:00')) if self.started_at else None
        end_time = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00')) if self.completed_at else None
        duration = (end_time - start_time).total_seconds() / 60 if start_time and end_time else 0

        total_chars = 0
        participant_stats = {p['id']: {'message_count': 0, 'total_characters': 0} for p in self.participants}

        for msg in self.messages:
            length = len(msg['content'])
            total_chars += length
            pid = msg['participant_id']
            participant_stats[pid]['message_count'] += 1
            participant_stats[pid]['total_characters'] += length

        for pid, stats in participant_stats.items():
            count = stats['message_count']
            stats['avg_characters'] = stats['total_characters'] // count if count > 0 else 0

        avg_message_length = total_chars // total_messages if total_messages > 0 else 0

        self.statistics = {
            'total_messages': total_messages,
            'total_participants': total_participants,
            'duration_minutes': int(duration),
            'avg_message_length': avg_message_length,
            'participant_stats': participant_stats
        }

    def get_transcript(self) -> List[str]:
        return self.logger.get_transcript()

    def get_formatted_output(self, format_type: str) -> str:
        # Prepare session data dictionary for output
        config_obj = getattr(self, 'config', {})
        config_dict = getattr(config_obj, 'config', config_obj)

        session_data = {
            'session_id': getattr(self, 'session_id', 'unknown'),
            'config': config_dict,
            'participants': getattr(self, 'participants', []),
            'status': getattr(self, 'status', 'unknown'),
            'created_at': getattr(self, 'created_at', None),
            'started_at': getattr(self, 'started_at', None),
            'completed_at': getattr(self, 'completed_at', None),
            'current_turn': getattr(self, 'current_turn', 0),
            'messages': getattr(self, 'messages', []),
            'statistics': getattr(self, 'statistics', {}),
        }

        if format_type.lower() == 'markdown':
            formatter = MarkdownFormatter(session_data)
            return formatter.to_markdown()
        elif format_type.lower() == 'json':
            formatter = JSONFormatter(session_data)
            return formatter.to_json()
        elif format_type.lower() == 'html':
            formatter = HTMLFormatter(session_data)
            return formatter.to_html()
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
