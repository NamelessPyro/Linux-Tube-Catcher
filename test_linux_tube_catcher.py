import unittest

from linux_tube_catcher import (
    build_ps3_ps_vita_480_video_args,
    build_ps3_ps_vita_video_args,
    build_mpeg4_simple_profile_video_args,
    build_xbox_360_video_args,
    build_video_transcode_args,
    format_duration,
    get_device_preset_target_quality,
    is_valid_media_url,
    parse_progress_percent,
    parse_max_downloads,
)


class LinuxTubeCatcherHelpersTest(unittest.TestCase):
    def test_valid_media_urls(self):
        self.assertTrue(is_valid_media_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(is_valid_media_url("http://vimeo.com/12345"))

    def test_invalid_media_urls(self):
        self.assertFalse(is_valid_media_url(""))
        self.assertFalse(is_valid_media_url("notaurl"))
        self.assertFalse(is_valid_media_url("ftp://example.com/video"))

    def test_format_duration(self):
        self.assertEqual(format_duration(None), "N/A")
        self.assertEqual(format_duration(59), "00:59")
        self.assertEqual(format_duration(61), "01:01")
        self.assertEqual(format_duration(3661), "01:01:01")

    def test_parse_max_downloads(self):
        self.assertEqual(parse_max_downloads("50"), 50)
        self.assertEqual(parse_max_downloads(" 12 "), 12)
        self.assertIsNone(parse_max_downloads("0"))
        self.assertIsNone(parse_max_downloads("-1"))
        self.assertIsNone(parse_max_downloads("abc"))

    def test_ps3_ps_vita_video_args(self):
        args = build_ps3_ps_vita_video_args()
        self.assertIn('-vf', args)
        self.assertIn('scale=-2:720', args)
        self.assertIn('-c:v', args)
        self.assertIn('libx264', args)
        self.assertIn('-pix_fmt', args)
        self.assertIn('yuv420p', args)
        self.assertIn('-c:a', args)
        self.assertIn('aac', args)

    def test_ps3_ps_vita_480_video_args(self):
        args = build_ps3_ps_vita_480_video_args()
        self.assertIn('scale=-2:480', args)
        self.assertIn('-profile:v', args)
        self.assertIn('baseline', args)
        self.assertIn('-level', args)
        self.assertIn('3.1', args)
        self.assertIn('-crf', args)
        self.assertIn('24', args)
        self.assertIn('-b:a', args)
        self.assertIn('128k', args)

    def test_mpeg4_simple_profile_video_args(self):
        args = build_mpeg4_simple_profile_video_args()
        self.assertIn('mpeg4', args)
        self.assertIn('scale=-2:720', args)
        self.assertIn('aac', args)

    def test_standard_video_transcode_args(self):
        args = build_video_transcode_args("Standard", "720p", "mp4")
        self.assertIn('-vf', args)
        self.assertIn('scale=-2:720', args)
        self.assertIn('libx264', args)
        self.assertIn('aac', args)

    def test_xbox_360_video_args(self):
        args = build_xbox_360_video_args()
        self.assertIn('libx264', args)
        self.assertIn('scale=-2:720', args)
        self.assertIn('main', args)
        self.assertIn('aac', args)

    def test_device_preset_target_quality(self):
        self.assertEqual(get_device_preset_target_quality("PS3 / PS Vita 480p (light)"), "480p")
        self.assertEqual(get_device_preset_target_quality("PS3 / PS Vita 720p"), "720p")

    def test_parse_progress_percent(self):
        self.assertEqual(parse_progress_percent("12.5%"), 12.5)
        self.assertEqual(parse_progress_percent("83.0"), 83.0)
        self.assertIsNone(parse_progress_percent("N/A"))


class VLCThemeAndUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        from PyQt6.QtWidgets import QApplication
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        cls.app = QApplication.instance() or QApplication([])

    def test_vlc_theme_palette(self):
        import vlc_theme
        self.assertGreaterEqual(len(vlc_theme.ACCENT_PALETTE), 9)
        hexes = [color for color, _ in vlc_theme.ACCENT_PALETTE]
        self.assertIn("#FF7A00", hexes)  # VLC signature orange
        self.assertIn("#2F6BEB", hexes)  # Sapphire blue
        self.assertIn("#2EA44F", hexes)  # Emerald green

    def test_stylesheet_generation(self):
        import vlc_theme
        dark_qss = vlc_theme.generate_stylesheet("#FF7A00", is_dark=True)
        self.assertIn("#FF7A00", dark_qss)
        self.assertIn("#121214", dark_qss)

        light_qss = vlc_theme.generate_stylesheet("#2F6BEB", is_dark=False)
        self.assertIn("#2F6BEB", light_qss)
        self.assertIn("#f4f4f7", light_qss)

    def test_svg_icon_rendering(self):
        import vlc_theme
        icon = vlc_theme.render_svg_icon("cone", "#FF7A00", 24)
        self.assertFalse(icon.isNull())
        pixmap = vlc_theme.render_svg_pixmap("download", "#ffffff", 20)
        self.assertFalse(pixmap.isNull())

    def test_window_initialization_and_navigation(self):
        from linux_tube_catcher import Willhiem, LinuxTubeCatcher
        self.assertIs(LinuxTubeCatcher, Willhiem)
        win = Willhiem()
        self.assertIsNotNone(win)
        self.assertEqual(win.windowTitle(), "Willhiem - VLC Community Design")
        self.assertEqual(win.page_stack.count(), 6)

        # Test navigation to each page
        for page_idx in range(6):
            win.navigate_to(page_idx)
            self.assertEqual(win.page_stack.currentIndex(), page_idx)

        # Test essential UI attributes
        self.assertIsNotNone(win.url_input)
        self.assertIsNotNone(win.path_input)
        self.assertIsNotNone(win.quality_combo)
        self.assertIsNotNone(win.video_format_combo)
        self.assertIsNotNone(win.audio_format_combo)
        self.assertIsNotNone(win.preset_combo)
        self.assertIsNotNone(win.download_btn)
        self.assertIsNotNone(win.convert_btn)
        self.assertIsNotNone(win.info_btn)
        self.assertIsNotNone(win.clear_btn)
        self.assertIsNotNone(win.progress)
        self.assertIsNotNone(win.log_text)

        # Test accent switching
        win.set_accent_color("#2EA44F")
        self.assertEqual(win.current_accent, "#2EA44F")
        win.set_theme_mode(False)
        self.assertFalse(win.is_dark)
        win.set_theme_mode(True)
        self.assertTrue(win.is_dark)


if __name__ == "__main__":
    unittest.main()
