"""Azure Speech Service-based pronunciation helper application.

This module provides a wxPython-based GUI for practicing word pronunciation using
Azure's Text-to-Speech service. It supports multiple voices, speaking styles,
and speech parameter adjustments like rate, pitch, and volume.
"""

import json
import os
from typing import Any
import html  # Add import for html escaping
import logging  # Import logging for debugging

import azure.cognitiveservices.speech as speechsdk
import wx

import config


class TooltipWindow(wx.PopupWindow):
    """Custom tooltip window with enhanced visibility and accessibility."""

    def __init__(self, parent, text):
        super().__init__(parent)
        panel = wx.Panel(self)
        label = wx.StaticText(panel, -1, text)

        panel.SetBackgroundColour(config.TOOLTIP_BACKGROUND_COLOR)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.ALL, 5)
        panel.SetSizer(sizer)

        panel.Fit()
        self.Fit()


class PronunciationHelper(wx.Frame):
    """Main application window for pronunciation practice.

    This class provides a GUI for practicing word pronunciation using Azure's
    Text-to-Speech service. It includes controls for voice selection, speaking style,
    speech rate, pitch, volume, and word emphasis.
    """

    def __init__(self):
        super().__init__(
            parent=None,
            title="Pronunciation Helper",
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )

        # Setup logger for this class instance
        self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
        if not self.logger.handlers:  # Avoid adding multiple handlers if class is instantiated multiple times
            self.logger.setLevel(logging.DEBUG)
            log_file_path = os.path.join(os.path.dirname(__file__), 'pronunciation_helper.log')
            handler = logging.FileHandler(log_file_path, mode='w')  # 'w' to overwrite, 'a' to append
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.info("PronunciationHelper initialized.")

        # Initialize tooltip
        self.tooltip = None

        # Configure speech service
        self.speech_config = speechsdk.SpeechConfig(
            subscription=config.SPEECH_KEY,
            region=config.SPEECH_REGION
        )
        self.logger.info("Speech service configured for region: %s", config.SPEECH_REGION)

        # Get available voices
        self.voices = self.get_available_voices()

        # Store speaking styles for voices
        self.speaking_styles = {}

        self.setup_ui()
        self.setup_accessibility()

        # Set minimum size
        self.SetMinSize(config.WINDOW_MIN_SIZE)
        self.Fit()

    def get_available_voices(self):
        """Get list of available English and Spanish voices from Azure."""
        self.logger.info("Attempting to fetch available voices.")
        try:
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            result = synthesizer.get_voices_async().get()
            if result.voices:
                self.logger.info("Successfully fetched %d voices from Azure.", len(result.voices))
                # Filter for English US and all Spanish voices, excluding multilingual voices
                filtered_voices = [
                    voice for voice in result.voices
                    if (voice.locale == 'en-US' or voice.locale.startswith('es-')) and
                       "Multilingual" not in voice.short_name
                ]
                self.logger.info("Filtered to %d voices (en-US and es-*).", len(filtered_voices))
                return {
                    f"{voice.short_name} ({voice.gender}, {voice.locale})": voice
                    for voice in filtered_voices
                }
            self.logger.warning("No voices found in the result from Azure Speech SDK.")
            return {}
        except (AttributeError, ConnectionError, Exception) as e:  # Added generic Exception
            self.logger.error("Failed to fetch voices: %s", str(e), exc_info=True)
            wx.MessageBox(
                f"Failed to fetch voices: {str(e)}",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
            return {}

    def setup_ui(self):
        """Setup the user interface with accessibility in mind."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Voice selection section
        voice_label = wx.StaticText(panel, label="Select Voice:")
        voice_choices = list(self.voices.keys())
        self.voice_combo = wx.Choice(panel, choices=voice_choices)
        if voice_choices:  # Check if there are any choices
            self.voice_combo.SetSelection(0)
            self.update_speaking_styles()  # This should only be called if a voice is selected
        else:
            self.voice_combo.Disable()  # Disable the combo box if no voices are available
        self.voice_combo.Bind(wx.EVT_CHOICE, self.on_voice_changed)

        # Speaking style selection
        style_box = wx.StaticBox(panel, label="Speaking Style")
        style_sizer = wx.StaticBoxSizer(style_box, wx.VERTICAL)
        self.style_combo = wx.Choice(panel, choices=['Default'])
        style_sizer.Add(self.style_combo, 0, wx.EXPAND | wx.ALL, 5)
        self.update_style_combo()

        # Speech rate control
        rate_box = wx.StaticBox(panel, label="Speech Rate")
        rate_sizer = wx.StaticBoxSizer(rate_box, wx.HORIZONTAL)
        self.rate_slider = wx.Slider(
            panel,
            value=config.DEFAULT_RATE,
            minValue=config.RATE_RANGE[0],
            maxValue=config.RATE_RANGE[1],
            style=wx.SL_HORIZONTAL
        )
        self.rate_label = wx.StaticText(panel, label="1.0x")
        rate_sizer.Add(self.rate_slider, 1, wx.EXPAND | wx.RIGHT, 5)
        rate_sizer.Add(self.rate_label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.rate_slider.Bind(wx.EVT_SLIDER, self.on_rate_changed)

        # Speech pitch control
        pitch_box = wx.StaticBox(panel, label="Speech Pitch")
        pitch_sizer = wx.StaticBoxSizer(pitch_box, wx.HORIZONTAL)
        self.pitch_slider = wx.Slider(
            panel,
            value=config.DEFAULT_PITCH,
            minValue=config.PITCH_RANGE[0],
            maxValue=config.PITCH_RANGE[1],
            style=wx.SL_HORIZONTAL
        )
        self.pitch_label = wx.StaticText(panel, label="0%")
        pitch_sizer.Add(self.pitch_slider, 1, wx.EXPAND | wx.RIGHT, 5)
        pitch_sizer.Add(self.pitch_label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.pitch_slider.Bind(wx.EVT_SLIDER, self.on_pitch_changed)

        # Volume control
        volume_box = wx.StaticBox(panel, label="Volume")
        volume_sizer = wx.StaticBoxSizer(volume_box, wx.HORIZONTAL)
        self.volume_slider = wx.Slider(
            panel,
            value=config.DEFAULT_VOLUME,
            minValue=config.VOLUME_RANGE[0],
            maxValue=config.VOLUME_RANGE[1],
            style=wx.SL_HORIZONTAL
        )
        self.volume_label = wx.StaticText(panel, label="100%")
        volume_sizer.Add(self.volume_slider, 1, wx.EXPAND | wx.RIGHT, 5)
        volume_sizer.Add(self.volume_label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.volume_slider.Bind(wx.EVT_SLIDER, self.on_volume_changed)

        # Emphasis control
        emphasis_box = wx.StaticBox(panel, label="Word Emphasis")
        emphasis_sizer = wx.StaticBoxSizer(emphasis_box, wx.VERTICAL)
        self.emphasis_combo = wx.Choice(panel, choices=config.DEFAULT_EMPHASIS_LEVELS)
        self.emphasis_combo.SetSelection(0)
        emphasis_sizer.Add(self.emphasis_combo, 0, wx.EXPAND | wx.ALL, 5)

        # Word entry sections
        mispronounced_label = wx.StaticText(panel, label="Mispronounced Word:")
        self.mispronounced_entry = wx.TextCtrl(panel)

        corrected_label = wx.StaticText(
            panel,
            label="Corrected Pronunciation (supports SSML):"
        )
        self.corrected_entry = wx.TextCtrl(panel)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.play_wrong_btn = wx.Button(panel, label="Play Mispronounced")
        self.play_correct_btn = wx.Button(panel, label="Play Corrected")
        self.save_btn = wx.Button(panel, label="Save to JSON")
        self.close_btn = wx.Button(panel, label="Close")

        button_sizer.Add(self.play_wrong_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(self.play_correct_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(self.save_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(self.close_btn, 0)

        # Bind button events
        self.play_wrong_btn.Bind(wx.EVT_BUTTON, self.on_play_mispronounced)
        self.play_correct_btn.Bind(wx.EVT_BUTTON, self.on_play_corrected)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)

        # Add all controls to main sizer with proper spacing
        main_sizer.Add(voice_label, 0, wx.ALL, 5)
        main_sizer.Add(self.voice_combo, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(style_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(rate_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(pitch_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(volume_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(emphasis_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(mispronounced_label, 0, wx.ALL, 5)
        main_sizer.Add(self.mispronounced_entry, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(corrected_label, 0, wx.ALL, 5)
        main_sizer.Add(self.corrected_entry, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        panel.SetSizer(main_sizer)

        # Set initial focus to voice combo
        self.voice_combo.SetFocus()

    def setup_accessibility(self):
        """Setup accessibility features including keyboard shortcuts and help text."""
        # Set accessible names and descriptions
        self.voice_combo.SetName("Voice selector")
        self.style_combo.SetName("Style selector")
        self.rate_slider.SetName("Rate control")
        self.pitch_slider.SetName("Pitch control")
        self.volume_slider.SetName("Volume control")
        self.emphasis_combo.SetName("Emphasis selector")
        self.mispronounced_entry.SetName("Mispronounced word entry")
        self.corrected_entry.SetName("Corrected pronunciation entry")

        # Set help text for screen readers
        self.voice_combo.SetHelpText("Select the voice for pronunciation")
        self.style_combo.SetHelpText("Select speaking style if available")
        self.rate_slider.SetHelpText("Adjust speech rate between 0.5x and 2.0x")
        self.pitch_slider.SetHelpText("Adjust speech pitch between -50% and +50%")
        self.volume_slider.SetHelpText("Adjust volume between 0% and 100%")
        self.emphasis_combo.SetHelpText("Set word emphasis level")

        # Bind keyboard shortcuts
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_ALT, ord('M'), self.play_wrong_btn.GetId()),
            (wx.ACCEL_ALT, ord('C'), self.play_correct_btn.GetId()),
            (wx.ACCEL_ALT, ord('S'), self.save_btn.GetId()),
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.close_btn.GetId())
        ])
        self.SetAcceleratorTable(accel_tbl)

        # Bind tooltip events
        self.bind_tooltip(
            self.voice_combo,
            "Select the voice for pronunciation (Tab to navigate)"
        )
        self.bind_tooltip(
            self.style_combo,
            "Select speaking style if available for the chosen voice"
        )
        self.bind_tooltip(
            self.rate_slider,
            "Use left/right arrows to adjust speech rate"
        )
        self.bind_tooltip(
            self.pitch_slider,
            "Use left/right arrows to adjust pitch"
        )
        self.bind_tooltip(
            self.volume_slider,
            "Use left/right arrows to adjust volume"
        )
        self.bind_tooltip(
            self.emphasis_combo,
            "Select emphasis level using up/down arrows"
        )
        self.bind_tooltip(self.play_wrong_btn, "Alt+M to play")
        self.bind_tooltip(self.play_correct_btn, "Alt+C to play")
        self.bind_tooltip(self.save_btn, "Alt+S to save")
        self.bind_tooltip(self.close_btn, "Esc to close")

    def bind_tooltip(self, widget, text):
        """Bind tooltip creation and destruction to a widget."""
        widget.Bind(
            wx.EVT_ENTER_WINDOW,
            lambda evt, text=text: self.on_show_tooltip(evt, text)
        )
        widget.Bind(wx.EVT_LEAVE_WINDOW, self.on_hide_tooltip)

    def on_show_tooltip(self, event, text):
        """Show tooltip when mouse enters widget."""
        if self.tooltip is not None:
            self.tooltip.Destroy()
        widget = event.GetEventObject()
        position = widget.ClientToScreen(wx.Point(0, 0))
        self.tooltip = TooltipWindow(self, text)
        self.tooltip.Position(
            position,
            config.TOOLTIP_OFFSET
        )
        self.tooltip.Show()

    def on_hide_tooltip(self, _: Any) -> None:
        """Hide tooltip when mouse leaves widget."""
        if self.tooltip is not None:
            self.tooltip.Destroy()
            self.tooltip = None

    def on_rate_changed(self, _: Any) -> None:
        """Update rate label when slider value changes."""
        rate = self.rate_slider.GetValue() / 100.0
        self.rate_label.SetLabel(f"{rate:.1f}x")

    def on_pitch_changed(self, _: Any) -> None:
        """Update pitch label when slider value changes."""
        pitch = self.pitch_slider.GetValue()
        self.pitch_label.SetLabel(f"{pitch:+d}%")

    def on_volume_changed(self, _: Any) -> None:
        """Update volume label when slider value changes."""
        volume = self.volume_slider.GetValue()
        self.volume_label.SetLabel(f"{volume}%")

    def update_speaking_styles(self):
        """Update available speaking styles based on selected voice."""
        selected_idx = self.voice_combo.GetSelection()
        if selected_idx != wx.NOT_FOUND:
            selected_voice = self.voice_combo.GetString(selected_idx)
            self.speaking_styles.clear()

            if selected_voice in self.voices:
                voice = self.voices[selected_voice]
                if hasattr(voice, 'style_list') and voice.style_list:
                    self.speaking_styles.update(
                        {style: style for style in voice.style_list}
                    )

    def update_style_combo(self):
        """Update the speaking style combobox based on selected voice."""
        styles = list(self.speaking_styles.keys())
        self.style_combo.Clear()
        if styles:
            self.style_combo.SetItems(['Default'] + styles)
            self.style_combo.SetSelection(0)
            self.style_combo.Enable()
        else:
            self.style_combo.SetItems(['Default'])
            self.style_combo.SetSelection(0)
            self.style_combo.Disable()

    def on_voice_changed(self, _: Any) -> None:
        """Handle voice selection change."""
        selected_voice_key = self.voice_combo.GetString(self.voice_combo.GetSelection())
        self.logger.info("Voice changed to: %s", selected_voice_key)
        self.update_speaking_styles()
        self.update_style_combo()

    def speak_text(self, text: str, is_ssml: bool = False, output_filename: str | None = None):
        """Speak the given text using Azure Speech Services or save to a file."""
        self.logger.info("speak_text called. Text (first 50 chars): '%s...', is_ssml: %s, output_filename: %s", text[:50], is_ssml, output_filename)
        try:
            selected_idx = self.voice_combo.GetSelection()
            if selected_idx == wx.NOT_FOUND:
                self.logger.error("No voice selected in combo box.")
                wx.MessageBox(
                    "Please select a voice first.",
                    "Voice Error",
                    wx.OK | wx.ICON_ERROR
                )
                return

            selected_voice_key = self.voice_combo.GetString(selected_idx)
            if not selected_voice_key or selected_voice_key not in self.voices:
                msg = "Please select a valid voice."
                self.logger.error("Invalid voice selected: '%s'. Message: %s", selected_voice_key, msg)
                wx.MessageBox(
                    msg,
                    "Voice Error",
                    wx.OK | wx.ICON_ERROR
                )
                return

            voice_info = self.voices[selected_voice_key]
            voice_name = voice_info.short_name
            voice_locale = voice_info.locale
            self.logger.info("Selected voice for synthesis: Name='%s', Locale='%s'", voice_name, voice_locale)

            if not is_ssml:
                rate = self.rate_slider.GetValue() / 100.0
                pitch = self.pitch_slider.GetValue()
                volume = self.volume_slider.GetValue()
                emphasis = self.emphasis_combo.GetString(
                    self.emphasis_combo.GetSelection()
                ).lower()
                style = self.style_combo.GetString(self.style_combo.GetSelection())
                style = '' if style == 'Default' else style

                ssml = (
                    f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
                    f'xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="{voice_locale}">'
                    f'<voice name="{voice_name}">'
                )

                if style and style in self.speaking_styles:
                    ssml += f'<mstts:express-as style="{style}">'

                ssml += (
                    f'<prosody rate="{rate:0.1f}" '
                    f'pitch="{pitch:+d}%" '
                    f'volume="{volume}%">'
                )

                escaped_text = html.escape(text)
                if emphasis != 'default':
                    ssml += f'<emphasis level="{emphasis}">{escaped_text}</emphasis>'
                else:
                    ssml += escaped_text

                ssml += '</prosody>'

                if style and style in self.speaking_styles:
                    ssml += '</mstts:express-as>'

                ssml += '</voice></speak>'
            else:
                ssml = text  # If is_ssml is true, text is already the full SSML
            self.logger.debug("Using SSML for synthesis: %s", ssml)

            # Configure audio output
            if output_filename:
                self.logger.info("Configuring audio output to file: %s", output_filename)
                audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
            else:
                self.logger.info("Configuring audio output to default speaker.")
                audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
            self.logger.info("Calling speech_synthesizer.speak_ssml_async(ssml).get()")
            result = synthesizer.speak_ssml_async(ssml).get()
            self.logger.info("Synthesis result object: %s", result)

            if result is None:
                msg = "Speech synthesis failed: No result object returned."
                self.logger.error(msg)
                wx.MessageBox(
                    msg,
                    "Synthesis Error",
                    wx.OK | wx.ICON_ERROR,
                )
                return

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                if output_filename:
                    self.logger.info("Speech synthesis completed. Audio data saved to %s", output_filename)
                    wx.MessageBox(f"Audio saved to {output_filename}", "Success", wx.OK | wx.ICON_INFORMATION)
                elif not result.audio_data or len(result.audio_data) == 0:
                    msg = "Speech synthesis completed, but no audio data was produced for playback. Please check your SSML, voice configuration, and network connection."
                    self.logger.warning(msg)
                    wx.MessageBox(
                        msg,
                        "Synthesis Warning",
                        wx.OK | wx.ICON_WARNING,
                    )
                else:
                    self.logger.info("Speech synthesis completed for speaker. Audio data length: %d", len(result.audio_data))
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                error_reason_str = cancellation_details.reason.name if hasattr(cancellation_details.reason, 'name') else str(cancellation_details.reason)
                error_code_str = cancellation_details.error_code.name if hasattr(cancellation_details.error_code, 'name') else str(cancellation_details.error_code)
                msg = (
                    f"Speech synthesis canceled.\n"
                    f"Reason: {error_reason_str}\n"
                    f"Error Code: {error_code_str}\n"
                    f"Details: {cancellation_details.error_details}"
                )
                self.logger.warning("Synthesis Canceled: Reason='%s', ErrorCode='%s', Details='%s'", error_reason_str, error_code_str, cancellation_details.error_details)
                wx.MessageBox(
                    msg,
                    "Synthesis Canceled",
                    wx.OK | wx.ICON_ERROR,
                )
            else:  # Other failure reasons
                error_reason_str = result.reason.name if hasattr(result.reason, 'name') else str(result.reason)
                msg = f"Speech synthesis failed with reason: {error_reason_str}"
                self.logger.error("%s - Full result: %s", msg, result)  # Log full result for other errors
                wx.MessageBox(
                    msg,
                    "Synthesis Error",
                    wx.OK | wx.ICON_ERROR,
                )

        except Exception as e:  # pylint: disable=broad-except
            msg = f"Speech synthesis error: {str(e)}"
            self.logger.error(msg, exc_info=True)
            wx.MessageBox(
                msg,
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    def on_play_mispronounced(self, event: Any) -> None:
        """Play the mispronounced word using the default speaker."""
        text = self.mispronounced_entry.GetValue().strip()
        self.logger.info("on_play_mispronounced called. Text: '%s'", text)
        if not text:
            msg = "Please enter a word to pronounce"
            self.logger.warning("Input required for mispronounced play: %s", msg)
            wx.MessageBox(
                msg,
                "Input Required",
                wx.OK | wx.ICON_WARNING
            )
            return

        button = event.GetEventObject()
        original_label = button.GetLabel()
        button.Disable()
        button.SetLabel("Processing...")
        wx.Yield()  # Ensure UI updates

        try:
            self.speak_text(text, is_ssml=False)
        finally:
            button.SetLabel(original_label)
            button.Enable()
            self.logger.info("on_play_mispronounced finished.")

    def on_play_corrected(self, event: Any) -> None:
        """Play the corrected pronunciation using the default speaker."""
        text = self.corrected_entry.GetValue().strip()
        self.logger.info("on_play_corrected called. Text (first 50 chars): '%s...'", text[:50])
        if not text:
            msg = "Please enter corrected pronunciation text (can be SSML)."
            self.logger.warning("Input required for corrected play: %s", msg)
            wx.MessageBox(
                msg,
                "Input Required",
                wx.OK | wx.ICON_WARNING
            )
            return

        button = event.GetEventObject()
        original_label = button.GetLabel()
        button.Disable()
        button.SetLabel("Processing...")
        wx.Yield()  # Ensure UI updates

        try:
            is_ssml = text.startswith('<speak>')
            self.speak_text(text, is_ssml=is_ssml)
        finally:
            button.SetLabel(original_label)
            button.Enable()
            self.logger.info("on_play_corrected finished.")

    def on_save(self, _: Any) -> None:
        """Save the word pair to a JSON file."""
        mispronounced = self.mispronounced_entry.GetValue().strip()
        corrected = self.corrected_entry.GetValue().strip()
        self.logger.info("on_save called. Mispronounced: '%s', Corrected (first 50 chars): '%s...'", mispronounced, corrected[:50])

        if not mispronounced or not corrected:
            msg = "Please enter both the mispronounced and corrected words"
            self.logger.warning("Input required for save: %s", msg)
            wx.MessageBox(
                msg,
                "Input Required",
                wx.OK | wx.ICON_WARNING
            )
            return

        data = {
            "mispronounced": mispronounced,
            "corrected": corrected
        }

        existing_data = []

        try:
            if os.path.exists(config.SAVE_FILENAME):
                with open(config.SAVE_FILENAME, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)

            if isinstance(existing_data, list):
                existing_data.append(data)
            else:
                existing_data = [data]

            with open(config.SAVE_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4)
            msg = "Word pair saved successfully"
            self.logger.info(msg)
            wx.MessageBox(
                msg,
                "Success",
                wx.OK | wx.ICON_INFORMATION
            )

        except json.JSONDecodeError as e:
            msg = f"Failed to read existing data: {str(e)}"
            self.logger.error(msg, exc_info=True)
            wx.MessageBox(
                msg,
                "Error",
                wx.OK | wx.ICON_ERROR
            )
        except IOError as e:
            msg = f"Failed to save data: {str(e)}"
            self.logger.error(msg, exc_info=True)
            wx.MessageBox(
                msg,
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    def on_close(self, _: Any) -> None:
        """Close the application."""
        self.logger.info("on_close called. Closing application.")
        self.Close()


def main():
    """Application entry point."""
    main_logger = logging.getLogger(__name__)
    if not main_logger.handlers:
        main_logger.setLevel(logging.DEBUG)
        log_file_path = os.path.join(os.path.dirname(__file__), 'pronunciation_helper.log')
        handler = logging.FileHandler(log_file_path, mode='a')  # Append to log file
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        main_logger.addHandler(handler)

    main_logger.info("Application starting.")
    app = wx.App()
    frame = PronunciationHelper()
    frame.Show()
    app.MainLoop()
    main_logger.info("Application closed.")


if __name__ == "__main__":
    main()
