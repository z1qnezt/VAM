from vosk import Model, KaldiRecognizer
from googlesearch import search
from pyowm import OWM
from termcolor import colored
from dotenv import load_dotenv
import speech_recognition
import googletrans
import pyttsx3
import wikipediaapi
import random
import webbrowser
import traceback
import json
import wave
import os
import vosk
import termcolor
import pyaudio

class Translation:

    def __init__(self):
        pass

    with open("translations.json", "r", encoding="UTF-8") as file:
        translations = json.load(file)

    def get(self, text: str):

        if text in self.translations:
            return self.translations[text][assistant.speech_language]
        else:
            print(colored("Not translated phrase: {}".format(text), "red"))
            return text


class OwnerPerson:

    name = ""
    home_city = ""
    native_language = ""
    target_language = ""


class VoiceAssistant:

    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():

    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            ttsEngine.setProperty("voice", voices[0].id)
        else:
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        ttsEngine.setProperty("voice", voices[1].id)


def record_and_recognize_audio(*args: tuple):

    with microphone:
        recognized_data = ""

        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            play_voice_assistant_speech(translator.get("Can you check if your microphone is on, please?"))
            traceback.print_exc()
            return

        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language=assistant.recognition_language).lower()

        except speech_recognition.UnknownValueError:
            pass
        
        except speech_recognition.RequestError:
            print(colored("Trying to use offline recognition...", "cyan"))
            recognized_data = use_offline_recognition()

        return recognized_data


def use_offline_recognition():

    recognized_data = ""
    try:
        if not os.path.exists("models/vosk-model-small-" + assistant.speech_language + "-0.4"):
            print(colored("Please download the model from:\n"
                          "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.",
                          "red"))
            exit(1)

        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-" + assistant.speech_language + "-0.4")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        traceback.print_exc()
        print(colored("Sorry, speech service is unavailable. Try again later", "red"))

    return recognized_data


def play_voice_assistant_speech(text_to_speech):

    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()


def play_greetings(*args: tuple):

    greetings = [
        translator.get("Hello, {}! How can I help you today?").format(person.name),
        translator.get("Good day to you {}! How can I help you today?").format(person.name)
    ]
    play_voice_assistant_speech(greetings[random.randint(0, len(greetings) - 1)])


def play_farewell_and_quit(*args: tuple):

    farewells = [
        translator.get("Goodbye, {}! Have a nice day!").format(person.name),
        translator.get("See you soon, {}!").format(person.name)
    ]
    play_voice_assistant_speech(farewells[random.randint(0, len(farewells) - 1)])
    ttsEngine.stop()
    quit()


def search_for_term_on_google(*args: tuple):

    if not args[0]: return
    search_term = " ".join(args[0])

    url = "https://google.com/search?q=" + search_term
    webbrowser.get().open(url)

    search_results = []
    try:
        for _ in search(search_term,  
                        tld="com",  
                        lang=assistant.speech_language, 
                        num=1, 
                        start=0,  
                        stop=1,  
                        pause=1.0, 
                        ):
            search_results.append(_)
            webbrowser.get().open(_)

    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return

    print(search_results)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on google").format(search_term))


def search_for_video_on_youtube(*args: tuple):

    if not args[0]: return
    search_term = " ".join(args[0])
    url = "https://www.youtube.com/results?search_query=" + search_term
    webbrowser.get().open(url)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on youtube").format(search_term))


def search_for_definition_on_wikipedia(*args: tuple):

    if not args[0]: return

    search_term = " ".join(args[0])

    wiki = wikipediaapi.Wikipedia(assistant.speech_language)

    wiki_page = wiki.page(search_term)
    try:
        if wiki_page.exists():
            play_voice_assistant_speech(translator.get("Here is what I found for {} on Wikipedia").format(search_term))
            webbrowser.get().open(wiki_page.fullurl)

            play_voice_assistant_speech(wiki_page.summary.split(".")[:2])
        else:
            play_voice_assistant_speech(translator.get(
                "Can't find {} on Wikipedia. But here is what I found on google").format(search_term))
            url = "https://google.com/search?q=" + search_term
            webbrowser.get().open(url)

    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return


def get_translation(*args: tuple):

    if not args[0]: return

    search_term = " ".join(args[0])
    google_translator = googletrans.Translator()
    translation_result = ""

    old_assistant_language = assistant.speech_language
    try:
        if assistant.speech_language != person.native_language:
            translation_result = google_translator.translate(search_term,  
                                                      src=person.target_language,  
                                                      dest=person.native_language)  

            play_voice_assistant_speech("The translation for {} in Russian is".format(search_term))

            assistant.speech_language = person.native_language
            setup_assistant_voice()

        else:
            translation_result = google_translator.translate(search_term,  
                                                      src=person.native_language, 
                                                      dest=person.target_language)  
            play_voice_assistant_speech("По-английски {} будет как".format(search_term))

            assistant.speech_language = person.target_language
            setup_assistant_voice()

        play_voice_assistant_speech(translation_result.text)

    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()

    finally:
        assistant.speech_language = old_assistant_language
        setup_assistant_voice()


def get_weather_forecast(*args: tuple):

    if args[0]:
        city_name = args[0][0]
    else:
        city_name = person.home_city

    try:
        weather_api_key = os.getenv("WEATHER_API_KEY")
        open_weather_map = OWM(weather_api_key)

        weather_manager = open_weather_map.weather_manager()
        observation = weather_manager.weather_at_place(city_name)
        weather = observation.weather

    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return

    status = weather.detailed_status
    temperature = weather.temperature('celsius')["temp"]
    wind_speed = weather.wind()["speed"]
    pressure = int(weather.pressure["press"] / 1.333)  # переведено из гПА в мм рт.ст.

    print(colored("Weather in " + city_name +
                  ":\n * Status: " + status +
                  "\n * Wind speed (m/sec): " + str(wind_speed) +
                  "\n * Temperature (Celsius): " + str(temperature) +
                  "\n * Pressure (mm Hg): " + str(pressure), "yellow"))

    play_voice_assistant_speech(translator.get("It is {0} in {1}").format(status, city_name))
    play_voice_assistant_speech(translator.get("The temperature is {} degrees Celsius").format(str(temperature)))
    play_voice_assistant_speech(translator.get("The wind speed is {} meters per second").format(str(wind_speed)))
    play_voice_assistant_speech(translator.get("The pressure is {} mm Hg").format(str(pressure)))


def change_language(*args: tuple):

    assistant.speech_language = "ru" if assistant.speech_language == "en" else "en"
    setup_assistant_voice()
    print(colored("Language switched to " + assistant.speech_language, "cyan"))


def run_person_through_social_nets_databases(*args: tuple):

    if not args[0]: return

    google_search_term = " ".join(args[0])
    vk_search_term = "_".join(args[0])
    fb_search_term = "-".join(args[0])

    url = "https://google.com/search?q=" + google_search_term + " site: vk.com"
    webbrowser.get().open(url)

    url = "https://google.com/search?q=" + google_search_term + " site: facebook.com"
    webbrowser.get().open(url)

    vk_url = "https://vk.com/people/" + vk_search_term
    webbrowser.get().open(vk_url)

    fb_url = "https://www.facebook.com/public/" + fb_search_term
    webbrowser.get().open(fb_url)

    play_voice_assistant_speech(translator.get("Here is what I found for {} on social nets").format(google_search_term))

def execute_command_with_name(command_name: str, *args: list):
    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else:
            pass 



commands = {
    ("hello", "hi", "morning", "привет"): play_greetings,
    ("bye", "goodbye", "quit", "exit", "stop", "пока"): play_farewell_and_quit,
    ("search", "google", "find", "найди"): search_for_term_on_google,
    ("video", "youtube", "watch", "видео"): search_for_video_on_youtube,
    ("wikipedia", "definition", "about", "определение", "википедия"): search_for_definition_on_wikipedia,
    ("translate", "interpretation", "translation", "перевод", "перевести", "переведи"): get_translation,
    ("language", "язык"): change_language,
    ("weather", "forecast", "погода", "прогноз"): get_weather_forecast,
    ("facebook", "person", "run", "пробей", "контакт"): run_person_through_social_nets_databases,
}

if __name__ == "__main__":

    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    ttsEngine = pyttsx3.init()

    person = OwnerPerson()
    person.name = "Mikhail"
    person.home_city = "Moscow"
    person.native_language = "en"
    person.target_language = "en"

    assistant = VoiceAssistant()
    assistant.name = "ФЕДЯ"
    assistant.sex = "female"
    assistant.speech_language = "en"

    setup_assistant_voice()

    translator = Translation()

    load_dotenv()

    while True:
        voice_input = record_and_recognize_audio()
        os.remove("microphone-results.wav")
        print(colored(voice_input, "blue"))

        voice_input = voice_input.split(" ")
        command = voice_input[0]
        command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
        execute_command_with_name(command, command_options)

