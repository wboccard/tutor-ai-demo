import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair
from google.cloud import texttospeech, speech
from google.api_core.exceptions import InvalidArgument
import os

CHARACTERS = {
    'Miles': {
        'character_name': "Miles the Astronomer",
        'character_intro': "I am an astronomer, and I have been studying the solar system for many years. I am passionate about space exploration, and I love sharing my knowledge with others. I am excited to help you learn more about the solar system.",
        'context': """Your name is Miles. You are an astronomer who is knowledgeable about the solar system.
        Respond in short sentences. Shape your response as if talking to a 10-years-old.""",
        'examples': [
            InputOutputTextPair(
                    input_text="""How many moons does Mars have?""",
                    output_text="""Very good question. Mars has two moons, Phobos and Deimos. They are very small and irregularly shaped. Phobos is the larger of the two moons and is about 17 miles (27 kilometers) in diameter. Deimos is about 12 miles (19 kilometers) in diameter. Both moons are thought to be captured asteroids."""
                )
        ],
        'voice': "en-US-Standard-D",
    },
    'Cathy':{
        'character_name': "Cathy the Deep Sea Diver",
        'character_intro': "My name is Cathy, and I'm a deep sea diver. I love exploring the ocean and learning about all the amazing creatures that live there. I've been diving for over 10 years, and I've seen some pretty amazing things.",
        'context': """Your name is Cathy. You are an deep sea diver who is knowledgeable about the ocean.
        Respond in short sentences. Shape your response as if talking to a 10-years-old.""",
        'examples': [
            InputOutputTextPair(
                    input_text="""How deep is the ocean?""",
                    output_text="""Great question. The average depth of the ocean is about 3,688 meters. I've only ever gone down about 40 meters. An ocean that deep is sure to be full of adventures! Isn't that crazy?"""
                )
        ],
        'voice': "en-US-Standard-C",
    },
}

class Chatbot():

    def __init__(self, character: str):
        self.character = character
        self.speech_to_text_client = speech.SpeechClient()
        self.text_to_speech_client = texttospeech.TextToSpeechClient()
        vertexai.init(project="voltaic-range-392823", location="us-central1")
        self.chat_model = ChatModel.from_pretrained("chat-bison@001")
        self.chat = self.chat_model.start_chat(
            context=CHARACTERS[character]['context'],
            examples=CHARACTERS[character]['examples']
        )
        self.speech_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            # encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            language_code="en-US",
            enable_word_confidence=True,
            enable_word_time_offsets=True,
        )
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", 
            name=CHARACTERS[character]['voice']
        )

    def reset_character(self, character):
        self.character = character
        self.chat_model = ChatModel.from_pretrained("chat-bison@001")
        self.chat = self.chat_model.start_chat(
            context=CHARACTERS[character]['context'],
            examples=CHARACTERS[character]['examples']
        )
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", 
            name=CHARACTERS[character]['voice']
        )

    def get_speech_to_text(self, audio_content) -> str:

        audio = speech.RecognitionAudio(content=audio_content)

        # Detects speech in the audio file
        response = self.speech_to_text_client.recognize(config=self.speech_config, audio=audio)
        final_result = ""

        for result in response.results:
            final_result += (result.alternatives[0].transcript)
        
        return final_result

    # Text to Speech
    def text_to_speech(self, text):
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        synthesis_input = texttospeech.SynthesisInput(text=f"{text}")
        response = self.text_to_speech_client.synthesize_speech(
            input=synthesis_input, voice=self.voice, audio_config=audio_config
        )
        # with open(os.path.join("static","uploads","output.mp3"), "wb") as out:
        #     # Write the response to the output file.
        #     out.write(response.audio_content)
        #     print('Audio content written to file output.mp3')
        return response.audio_content

    def get_ai_response(self, input_file):
        parameters = {
            "temperature": 0.8,
            "max_output_tokens": 256,
            "top_p": 0.8,
            "top_k": 40
        }
        input_text = self.get_speech_to_text(input_file)
        print(input_text)
        try:
            response = self.chat.send_message(input_text, **parameters)
        except InvalidArgument:
            print(InvalidArgument)
            return None
        status = self.text_to_speech(response.text)
        return response.text
    
    def ask_chat(self, input_text):
        parameters = {
            "temperature": 0.8,
            "max_output_tokens": 256,
            "top_p": 0.8,
            "top_k": 40
        }
        try:
            response = self.chat.send_message(input_text, **parameters)
        except InvalidArgument:
            print(InvalidArgument)
            return None
        return response.text
