import os
import pandas as pd
import pydub
import numpy as np
from typing import Any

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo

from faicons import icon_svg

from IPython.display import HTML, Audio
audio_style = "<style>audio { margin-left: 35px; width: 90%; margin-right: 35px;}</style>"

def load_audio_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension == ".wav":
        audio_raw = pydub.AudioSegment.from_wav(file_path)
    elif(file_extension == ".mp3"):
        audio_raw = pydub.AudioSegment.from_mp3(file_path)
    audio_ = np.array(audio_raw.get_array_of_samples())
    if audio_raw.channels == 2:
        audio_ = audio_.reshape((-1, 2))
    return audio_, audio_raw.frame_rate

def edit_audio(audio, sr, first_cut, last_cut):
    if audio is not None:
        channels = 2 if (audio.ndim == 2 and audio.shape[1] == 2) else 1
        if channels == 2:
            return(np.concatenate((audio[:sr*first_cut,:], audio[sr*last_cut:,]), axis=0))
        else:
            return(np.concatenate((audio[:sr*first_cut], audio[sr*last_cut:]), axis=0))


def make_downloader(id: str, label: str, title: str, desc: str, extra: Any = None):
    return ui.column(
        6,
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div(
                {"class": "card-body"},
                ui.p(desc, class_="card-text text-muted"),
                ui.HTML("<center>"),
                extra,
                ui.download_button(id, label, class_="btn-primary"),
                ui.HTML("</center>"),
            ),
        ),
    )

app_ui = ui.page_fluid(
    ui.panel_title("Audio Editor V0.0.2"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file("file1", "Choose MP3/WAV File", accept=[".mp3", ".wav"], multiple=False),
            ui.row(ui.column(
                    5,
                    ui.input_numeric("cut_start_min", "Cut start (min)", 0)
                ),
                ui.column(
                    1,
                    ui.HTML("<center style='margin-top:37px'><b>:</b></center>")
                ),
                ui.column(
                5,
                ui.input_numeric("cut_start_s", "Cut start (s)", 1)
                )
            ),
            ui.row(ui.column(
                    5,
                    ui.input_numeric("cut_end_min", "Cut end (min)", 0)
                ),
                ui.column(
                    1,
                    ui.HTML("<center style='margin-top:37px'><b>:</b></center>")
                ),
                ui.column(
                5,
                ui.input_numeric("cut_end_s", "Cut end (s)", 2)
                )
            ),
            ui.row(
                make_downloader(
                    "mp3downloader",
                    label="Download MP3",
                    title="Download audio (MP3)",
                    desc="Downloads edited audio as MP3",
                ),
                make_downloader(
                    "wavdownloader",
                    label="Download WAV",
                    title="Download audio (WAV)",
                    desc="Downloads edited audio as WAV",
                )
            ),
        ),
        #ui.panel_conditional("input.file1",
            ui.HTML(audio_style),
            ui.output_ui("play_audio"),
            ui.input_action_button("preview_button", "Preview settings", icon=icon_svg("scissors")),
            ui.output_ui("play_audio_edited"),
            ui.input_action_button("apply_button", "Apply settings", icon=icon_svg("floppy-disk"))
        #)
    ),
    ui.tags.footer(
        ui.hr(),
        ui.HTML("<center>"),
        ui.div(
            ui.HTML('Developed by <a href="mailto:dominik.kuehn@extern.h-da.de">Dominik Kuehn</a>'),
        ),
        ui.HTML("</center>"),
        ui.hr()
    )

)


def server(input: Inputs, output: Outputs, session: Session):
    audio = reactive.Value(None)
    edited_audio = reactive.Value(None)
    file_name = reactive.Value(None)
    sr = reactive.Value(44100)
    
    @reactive.calc
    def parsed_file():
        file: list[FileInfo] | None = input.file1()
        if file is None:
            return None, None, None
        audio_, sr_ = load_audio_file(file[0]["datapath"])
        file_name_ = os.path.splitext(os.path.basename(file[0]["name"]))[0]
        print(f'Loading {file_name_} file')
        print("Loading audio file - end")
        return audio_, sr_, file_name_

    @render.ui
    def play_audio():
        if audio() is None:
            id = ui.notification_show("Loading audio file\n This may take a while...", duration=None)
            parsed_audio, parsed_sr, file_name_temp = parsed_file()
            file_name.set(file_name_temp)
            audio.set(parsed_audio)
            sr.set(parsed_sr)
            ui.notification_remove(id)
        if audio() is not None:
            channels = 2 if (audio().ndim == 2 and audio().shape[1] == 2) else 1
            if channels == 2:
                output = Audio(data = audio().T, rate=sr())
            else:
                output = Audio(data = audio(), rate=sr())

        else:
            output = None
        return output
    
    @reactive.effect
    @reactive.event(input.preview_button)
    def audio_edited():
        if audio() is not None:
            id = ui.notification_show("Preparing edited audio output...", duration=None)
            edited_audio.set(edit_audio(audio = audio(), sr=sr(), first_cut=input.cut_start_min()*60+input.cut_start_s(), last_cut=input.cut_end_min()*60+input.cut_end_s()+1))
            ui.notification_remove(id)

    @reactive.effect
    @reactive.event(input.apply_button)
    def _():
        if edited_audio() is not None:
            id = ui.notification_show("Appling settings...", duration=None, type="message")
            audio.set(edited_audio())
            ui.notification_remove(id)
            ui.notification_show("Settings applied!", type="message")

    @render.ui
    def play_audio_edited():
        if edited_audio() is not None:
            channels = 2 if (edited_audio().ndim == 2 and edited_audio().shape[1] == 2) else 1
            print(f"channels: {channels}")
            if channels == 2:
                return Audio(data = edited_audio().T, rate=sr())
            else:
                return Audio(data = edited_audio(), rate=sr())

    
    @render.download()
    def mp3downloader():
        path = os.path.join(os.path.dirname(__file__), file_name()+".mp3")
        export_audio_file(file_name_=path, sr_=sr(), audio_=audio(), format_="mp3")
        return path
    @render.download()
    def wavdownloader():
        path = os.path.join(os.path.dirname(__file__), file_name()+".wav")
        print(f"save in this dir: {path}")
        export_audio_file(file_name_=path, sr_=sr(), audio_=audio(), format_="wav")
        return path
app = App(app_ui, server)

def export_audio_file(file_name_, sr_, audio_, format_):
    channels = 2 if (audio_.ndim == 2 and audio_.shape[1] == 2) else 1
    y = np.int16(audio_)
    print("save file...")
    print(pydub.AudioSegment(y.tobytes(), frame_rate=sr_, sample_width=2, channels=channels).export(file_name_, format=format_))