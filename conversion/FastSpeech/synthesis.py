import torch
import torch.nn as nn
import matplotlib
matplotlib.use('agg')
import numpy as np
import os

from .fastspeech import FastSpeech
from .text import text_to_sequence
from .hparams import hp
from . import utils
from . import Audio
from . import waveglow

def get_FastSpeech(num):
    checkpoint_path = "checkpoint_" + str(num) + ".pth.tar"
    model = nn.DataParallel(FastSpeech()).to(device)
    model.load_state_dict(torch.load(os.path.join(
        hp.checkpoint_path, checkpoint_path))['model'])
    model.eval()

    return model

def synthesis(model, text, alpha=1.0):
    text = np.array(text_to_sequence(text, hp.text_cleaners))
    text = np.stack([text])

    src_pos = np.array([i+1 for i in range(text.shape[1])])
    src_pos = np.stack([src_pos])
    with torch.no_grad():
        sequence = torch.autograd.Variable(
            torch.from_numpy(text)).cuda().long()
        src_pos = torch.autograd.Variable(
            torch.from_numpy(src_pos)).cuda().long()

        mel, mel_postnet = model.module.forward(sequence, src_pos, alpha=alpha)

        return mel[0].cpu().transpose(0, 1), \
            mel_postnet[0].cpu().transpose(0, 1), \
            mel.transpose(1, 2), \
            mel_postnet.transpose(1, 2)


num = 600000
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("load model....")
g_model = get_FastSpeech(num)
wave_glow = utils.get_WaveGlow()
# tacotron2 = utils.get_Tacotron2()
print("load model finish!")

def tts(text, filename, alpha=1.0):
    # num = 600000
    # print("load model....")
    # model = get_FastSpeech(num)
    # wave_glow = utils.get_WaveGlow()
    # # tacotron2 = utils.get_Tacotron2()
    # print("load model finish!")
    # if not os.path.exists("results"):
    #     os.mkdir("results")

    texts = [text]
    for words in texts:
        mel, mel_postnet, mel_torch, mel_postnet_torch = synthesis(
            g_model, words, alpha=alpha)

        waveglow.inference.inference(mel_postnet_torch, wave_glow, filename)

        # mel_tac2, _, _, alignment = utils.load_data_from_tacotron2(words, tacotron2)
        # waveglow.inference.inference(torch.stack([torch.from_numpy(
        #     mel_tac2).cuda()]), wave_glow, filename)


if __name__ == "__main__":
    # Test
    num = 600000
    alpha = 1.0
    print("load model....")
    model = get_FastSpeech(num)
    wave_glow = utils.get_WaveGlow()
    tacotron2 = utils.get_Tacotron2()
    print("load model finish!")
    if not os.path.exists("results"):
        os.mkdir("results")

    texts = [
            "vipkid",
            "vip kid",
            "Let’s go out to the airport. The plane landed ten minutes ago.",
            "printing, in the only sense with which we are at present concerned, differs from most if not from all the arts and crafts represented in the exhibition",
            "in being comparatively modern.",
            "Scientists at the CERN laboratory say they have discovered a new particle.",
            "President Trump met with other leaders at the Group of 20 conference.",
            "and detailing police in civilian clothes to be scattered throughout the sizable crowd.",
            "VIPKid is a Chinese online education firm that offers an American elementary education experience to Chinese students aged 4-12",
            ]
    for words in texts:
        mel, mel_postnet, mel_torch, mel_postnet_torch = synthesis(
            model, words, alpha=alpha)

        Audio.tools.inv_mel_spec(mel_postnet, os.path.join(
            "results", words + "_" + str(num) + "_griffin_lim.wav"))

        waveglow.inference.inference(mel_postnet_torch, wave_glow, os.path.join(
            "results", words + "_" + str(num) + "_waveglow.wav"))

        mel_tac2, _, _, alignment = utils.load_data_from_tacotron2(words, tacotron2)
        waveglow.inference.inference(torch.stack([torch.from_numpy(
            mel_tac2).cuda()]), wave_glow, os.path.join("results", words + "_" + str(num) + "tacotron2.wav"))
        utils.plot_data([mel.numpy(), mel_postnet.numpy(), mel_tac2, alignment], words[:10])
        print("synthesis finish:", words)
