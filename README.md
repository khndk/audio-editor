## Audio Editor

### Description
This Python script provides a simple audio editing tool using the Shiny library. It allows users to load MP3/WAV files, cut segments of the audio, preview the edited audio, and download the edited audio in either MP3 or WAV format.

### Requirements
- Python (3.6 or above)
- Required Python packages: `os`, `pandas`, `pydub`, `numpy`, `shiny`, `faicons`, `IPython.display`

### How to Run
1. Ensure you have Python installed on your system.
2. Install the required Python packages if you haven't already by running:
`pip install pandas pydub numpy shiny faicons ipython`
3. Save the provided code snippet into a Python file, e.g., `audio_editor.py`.
4. Execute the script using the following command:
`python -m shiny run audio_editor.py`

### Usage
1. Choose an MP3/WAV file by clicking on "Choose MP3/WAV File" and select the desired file.
2. Specify the start and end times (in seconds) for the segment you want to cut from the audio.
3. Click on "Preview settings" to listen to the edited audio.
4. Once satisfied with the edits, click on "Apply settings" to finalize the changes.
5. You can download the edited audio in either MP3 or WAV format using the corresponding download buttons.

---
For any queries or issues, please contact the developer mentioned above.