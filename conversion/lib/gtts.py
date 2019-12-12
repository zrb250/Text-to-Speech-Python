# -*- coding: utf-8 -*-
import re, requests, warnings
from .gtts_token import Token

class gTTS:
    """ gTTS (Google Text to Speech): an interface to Google's Text to Speech API """

    # Google TTS API supports two read speeds
    # (speed <= 0.3: slow; speed > 0.3: normal; default: 1)
    class Speed:
        SLOW = 0.3
        NORMAL = 1

    GOOGLE_TTS_URL = 'https://translate.google.com/translate_tts'
    MAX_CHARS = 100 # Max characters the Google TTS API takes at a time
    TTS_ENGINE = {
        'fastspeech': 'fastspeech + waveglow',
        'tacotron2': 'tacotron2 + waveglow',
    }
    SPEECH_SPEED = {
         's':'slow (0.5*normal)',
         'n': 'normal (1.0*normal)',
         'f': 'fast (1.5*normal)',
    }
    LANGUAGES = {
        'en' : 'English',
    }

    def __init__(self, text, lang = 'en', slow = False, debug = False):
        self.debug = debug
        if lang.lower() not in self.LANGUAGES:
            raise Exception('Language not supported: %s' % lang)
        else:
            self.lang = lang.lower()

        if not text:
            raise Exception('No text to speak')
        else:
            self.text = text

        # Read speed
        if slow:
            self.speed = self.Speed().SLOW
        else:
            self.speed = self.Speed().NORMAL


        # Split text in parts
        if self._len(text) <= self.MAX_CHARS:
            text_parts = [text]
        else:
            text_parts = self._tokenize(text, self.MAX_CHARS)           

        # Clean
        def strip(x): return x.replace('\n', '').strip()
        text_parts = [strip(x) for x in text_parts]
        text_parts = [x for x in text_parts if len(x) > 0]
        self.text_parts = text_parts
        
        # Google Translate token
        self.token = Token()

    def save(self, savefile):
        """ Do the Web request and save to `savefile` """
        with open(savefile, 'wb') as f:
            self.write_to_fp(f)

    def write_to_fp(self, fp):
        return;

    def _len(self, text):
        """ Get char len of `text`, after decoding if Python 2 """
        try:
            # Python 2
            return len(unicode(text))
        except NameError:
            # Python 3
            return len(text)

    def _tokenize(self, text, max_size):
        """ Tokenizer on basic punctuation """
        
        punc = "¡!()[]¿?.,،;:—。、：？！\n"
        punc_list = [re.escape(c) for c in punc]
        pattern = '|'.join(punc_list)
        parts = re.split(pattern, text)

        min_parts = []
        for p in parts:
            min_parts += self._minimize(p, " ", max_size)
        return min_parts

    def _minimize(self, thestring, delim, max_size):
        """ Recursive function that splits `thestring` in chunks
        of maximum `max_size` chars delimited by `delim`. Returns list. """ 
        
        if self._len(thestring) > max_size:
            idx = thestring.rfind(delim, 0, max_size)
            return [thestring[:idx]] + self._minimize(thestring[idx:], delim, max_size)
        else:
            return [thestring]

if __name__ == "__main__":
        pass