from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

from .lib.gtts import gTTS
from .FastSpeech.synthesis import tts

def index(request):
	conversion_text = ''
	conversion_lang = 'en'
	conversion_engine = 'fastspeech'
	conversion_speed = 'n'

	language_list = gTTS.LANGUAGES.items()
	tts_engine_list = gTTS.TTS_ENGINE.items()
	conversion_speed_list = gTTS.SPEECH_SPEED.items()

	content = {
		'conversion_text': conversion_text,
		'language_list' : language_list,
		'selected_lang' : conversion_lang,
		'tts_engine_list':tts_engine_list,
		'selected_engine':conversion_engine,
		'conversion_speed_list':conversion_speed_list,
		'selected_speed':conversion_speed,
	}

	template = loader.get_template('index.html')
	return HttpResponse(template.render(content, request))

def translate(request):
	if request.method != "POST":
		return redirect('/')

	conversion_text = request.POST.get('conversion_text', '')
	conversion_lang = request.POST.get('conversion_lang', 'en')
	conversion_engine = request.POST.get('conversion_engine', 'fastspeech')
	conversion_speed = request.POST.get('conversion_speed', 'n')


	language_list_master = gTTS.LANGUAGES
	language_list = language_list_master.items()
	selected_lang = (language_list_master[conversion_lang] if conversion_lang in language_list_master else "")

	tts_engine_list = gTTS.TTS_ENGINE
	conversion_speed_list = gTTS.SPEECH_SPEED

	selected_engine = (tts_engine_list[conversion_engine] if conversion_engine in tts_engine_list else "")
	selected_speed = (conversion_speed_list[conversion_speed] if conversion_speed in conversion_speed_list else "")

	audio_save_path = 'static/files/synthesis_result.wav'
	conversion_status = False

	if conversion_text!="":
		tts(conversion_text, audio_save_path, conversion_engine, conversion_speed)
		conversion_status = True

	content = {
		'conversion_text': conversion_text,
		'saved_path' : audio_save_path,
		'conversion_status' : conversion_status,
		'language_list' : language_list,
		'selected_lang' : selected_lang,
		'selected_engine':selected_engine,
		'selected_speed':selected_speed,
	}
	template = loader.get_template('translate.html')
	return HttpResponse(template.render(content, request))