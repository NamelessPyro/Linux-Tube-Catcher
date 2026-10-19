"""
VLC Redesign Theme & Asset Engine for Willhiem
Implements the design language from the VLC Community Redesign:
- Deep matte dark mode palette & light mode support
- Accent color picker with 9 signature swatches
- Crisp vector SVG icons for sidebar, controls, and badges
- Modern card-based UI styling with rounded pill buttons and custom controls
"""

from typing import List, Tuple
from PyQt6.QtCore import Qt, QByteArray, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

DEFAULT_ACCENT = "#FF7A00"  # Signature VLC Orange

# The 9 accent color swatches from the VLC Community Redesign (Page 16 & 71)
ACCENT_PALETTE: List[Tuple[str, str]] = [
    ("#FF7A00", "VLC Orange"),
    ("#E04040", "Crimson"),
    ("#C29B38", "Amber"),
    ("#2EA44F", "Emerald"),
    ("#1B98B8", "Teal"),
    ("#2F6BEB", "Sapphire"),
    ("#7948C2", "Amethyst"),
    ("#B84085", "Magenta"),
    ("#707070", "Slate"),
]

# Crisp modern vector SVG icons
SVG_ICONS = {
    'cone': (
        '<svg viewBox="0 0 24 24" fill="none">'
        '<path d="M12 2L6 20h12L12 2z" fill="{color}"/>'
        '<path d="M9.3 11h5.4l-.8-2.5h-3.8L9.3 11z" fill="#FFFFFF"/>'
        '<path d="M7.7 16h8.6l-.7-2.2H8.4L7.7 16z" fill="#FFFFFF"/>'
        '<rect x="3" y="20" width="18" height="2.5" rx="1.2" fill="{color}"/>'
        '</svg>'
    ),
    'home': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<polyline points="9 22 9 12 15 12 15 22"/>'
        '</svg>'
    ),
    'download': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="7 10 12 15 17 10"/>'
        '<line x1="12" y1="15" x2="12" y2="3"/>'
        '</svg>'
    ),
    'convert': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="23 4 23 10 17 10"/>'
        '<polyline points="1 20 1 14 7 14"/>'
        '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>'
        '</svg>'
    ),
    'library': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2" y="2" width="20" height="20" rx="3"/>'
        '<line x1="7" y1="2" x2="7" y2="22"/>'
        '<line x1="17" y1="2" x2="17" y2="22"/>'
        '<line x1="2" y1="12" x2="22" y2="12"/>'
        '<line x1="2" y1="7" x2="7" y2="7"/>'
        '<line x1="2" y1="17" x2="7" y2="17"/>'
        '<line x1="17" y1="17" x2="22" y2="17"/>'
        '<line x1="17" y1="7" x2="22" y2="7"/>'
        '</svg>'
    ),
    'log': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="4 17 10 11 4 5"/>'
        '<line x1="12" y1="19" x2="20" y2="19"/>'
        '</svg>'
    ),
    'settings': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
        '</svg>'
    ),
    'folder': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
        '</svg>'
    ),
    'play': (
        '<svg viewBox="0 0 24 24" fill="{color}">'
        '<polygon points="6 4 20 12 6 20 6 4"/>'
        '</svg>'
    ),
    'refresh': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="23 4 23 10 17 10"/>'
        '<path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>'
        '</svg>'
    ),
    'check': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="20 6 9 17 4 12"/>'
        '</svg>'
    ),
    'copy': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>'
        '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'
        '</svg>'
    ),
    'trash': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="3 6 5 6 21 6"/>'
        '<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
        '</svg>'
    ),
    'info': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="12" y1="16" x2="12" y2="12"/>'
        '<line x1="12" y1="8" x2="12.01" y2="8"/>'
        '</svg>'
    ),
    'paste': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
        '<rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>'
        '</svg>'
    ),
    'clear': (
        '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="18" y1="6" x2="6" y2="18"/>'
        '<line x1="6" y1="6" x2="18" y2="18"/>'
        '</svg>'
    )
}


def render_svg_icon(name: str, color: str = "#ffffff", size: int = 20) -> QIcon:
    """Render an icon from SVG_ICONS into a QIcon."""
    svg_template = SVG_ICONS.get(name, SVG_ICONS['info'])
    svg_colored = svg_template.replace('{color}', color).replace('currentColor', color)
    renderer = QSvgRenderer(QByteArray(svg_colored.encode('utf-8')))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def render_svg_pixmap(name: str, color: str = "#ffffff", size: int = 24) -> QPixmap:
    """Render an icon from SVG_ICONS into a QPixmap."""
    svg_template = SVG_ICONS.get(name, SVG_ICONS['info'])
    svg_colored = svg_template.replace('{color}', color).replace('currentColor', color)
    renderer = QSvgRenderer(QByteArray(svg_colored.encode('utf-8')))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def adjust_color_brightness(hex_color: str, factor: float) -> str:
    """Lighten (factor > 1) or darken (factor < 1) a hex color."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    return f"#{hex_color}"


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba(r, g, b, alpha) string."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    return hex_color


def generate_stylesheet(accent: str = DEFAULT_ACCENT, is_dark: bool = True) -> str:
    """Generate the complete stylesheet adhering to the VLC Community Redesign."""
    accent_hover = adjust_color_brightness(accent, 1.15)
    accent_pressed = adjust_color_brightness(accent, 0.85)
    accent_subtle = hex_to_rgba(accent, 0.18)
    accent_border = hex_to_rgba(accent, 0.40)

    if is_dark:
        bg_main = "#121214"
        bg_sidebar = "#17171a"
        bg_topbar = "#161619"
        bg_bottombar = "#161619"
        bg_card = "#1a1a1e"
        bg_card_subtle = "#202025"
        bg_input = "#131316"
        border_subtle = "#26262c"
        border_input = "#2c2c34"
        text_primary = "#f4f4f6"
        text_secondary = "#a1a1aa"
        text_muted = "#71717a"
        btn_sec_bg = "#222227"
        btn_sec_hover = "#2a2a31"
        btn_sec_border = "#303038"
        table_alt_bg = "#16161a"
        table_hover = "#222228"
    else:
        bg_main = "#f4f4f7"
        bg_sidebar = "#eaebee"
        bg_topbar = "#ffffff"
        bg_bottombar = "#ffffff"
        bg_card = "#ffffff"
        bg_card_subtle = "#f0f1f4"
        bg_input = "#ffffff"
        border_subtle = "#d8d9de"
        border_input = "#c8c9ce"
        text_primary = "#18181b"
        text_secondary = "#52525b"
        text_muted = "#a1a1aa"
        btn_sec_bg = "#e8e9ed"
        btn_sec_hover = "#dcdee3"
        btn_sec_border = "#c4c5cc"
        table_alt_bg = "#f9f9fb"
        table_hover = "#eceef2"

    return f"""
    /* Core Application Window */
    QMainWindow, QWidget#centralWidget {{
        background-color: {bg_main};
        color: {text_primary};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Ubuntu", "Cantarell", "Noto Sans", sans-serif;
    }}

    /* Left Sidebar */
    QWidget#sidebarWidget {{
        background-color: {bg_sidebar};
        border-right: 1px solid {border_subtle};
    }}

    /* Top Navigation Bar */
    QFrame#topbarFrame {{
        background-color: {bg_topbar};
        border-bottom: 1px solid {border_subtle};
    }}

    /* Persistent Bottom Media / Status Bar */
    QFrame#bottombarFrame {{
        background-color: {bg_bottombar};
        border-top: 1px solid {border_subtle};
    }}

    /* Modern Card Containers */
    QFrame.vlcCard {{
        background-color: {bg_card};
        border: 1px solid {border_subtle};
        border-radius: 10px;
    }}

    QGroupBox {{
        background-color: {bg_card};
        border: 1px solid {border_subtle};
        border-radius: 10px;
        margin-top: 24px;
        font-weight: 600;
        font-size: 13px;
        color: {text_primary};
        padding: 16px 12px 12px 12px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 14px;
        padding: 0 6px;
        background-color: transparent;
        color: {text_primary};
    }}

    /* Typography */
    QLabel {{
        color: {text_primary};
        background: transparent;
    }}

    QLabel.vlcTitle {{
        font-size: 18px;
        font-weight: bold;
        color: {text_primary};
    }}

    QLabel.vlcSubtitle {{
        font-size: 12px;
        color: {text_secondary};
    }}

    QLabel.vlcMuted {{
        font-size: 11px;
        color: {text_muted};
    }}

    QLabel.vlcBadge {{
        background-color: {accent_subtle};
        color: {accent};
        font-size: 11px;
        font-weight: 600;
        border-radius: 10px;
        padding: 3px 10px;
        border: 1px solid {accent_border};
    }}

    /* Form Inputs */
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {bg_input};
        color: {text_primary};
        border: 1px solid {border_input};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        selection-background-color: {accent};
        selection-color: #ffffff;
    }}

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {accent};
    }}

    QLineEdit:disabled, QComboBox:disabled {{
        color: {text_muted};
        background-color: {bg_card_subtle};
        border: 1px solid {border_subtle};
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border-left: none;
        background: transparent;
    }}

    QComboBox QAbstractItemView {{
        background-color: {bg_card};
        color: {text_primary};
        border: 1px solid {border_subtle};
        border-radius: 6px;
        selection-background-color: {accent};
        selection-color: #ffffff;
        padding: 4px;
    }}

    /* Primary Action Buttons (Accent Filled) */
    QPushButton.vlcPrimaryBtn {{
        background-color: {accent};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 9px 20px;
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton.vlcPrimaryBtn:hover {{
        background-color: {accent_hover};
    }}

    QPushButton.vlcPrimaryBtn:pressed {{
        background-color: {accent_pressed};
    }}

    QPushButton.vlcPrimaryBtn:disabled {{
        background-color: {btn_sec_bg};
        color: {text_muted};
        border: 1px solid {border_subtle};
    }}

    /* Secondary / Outline Buttons */
    QPushButton.vlcSecondaryBtn, QPushButton {{
        background-color: {btn_sec_bg};
        color: {text_primary};
        border: 1px solid {btn_sec_border};
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        font-size: 12px;
    }}

    QPushButton.vlcSecondaryBtn:hover, QPushButton:hover {{
        background-color: {btn_sec_hover};
        border: 1px solid {text_muted};
    }}

    QPushButton.vlcSecondaryBtn:pressed, QPushButton:pressed {{
        background-color: {border_subtle};
    }}

    QPushButton:disabled {{
        color: {text_muted};
        border: 1px solid {border_subtle};
        background-color: {bg_card_subtle};
    }}

    /* Sidebar Navigation Item Buttons */
    QPushButton.vlcNavBtn {{
        text-align: left;
        background-color: transparent;
        color: {text_secondary};
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 500;
    }}

    QPushButton.vlcNavBtn:hover {{
        background-color: {btn_sec_hover};
        color: {text_primary};
    }}

    QPushButton.vlcNavBtn[active="true"] {{
        background-color: {accent_subtle};
        color: {accent};
        font-weight: 600;
    }}

    /* Checkboxes & Radio buttons */
    QCheckBox, QRadioButton {{
        color: {text_primary};
        spacing: 8px;
        font-size: 13px;
        background: transparent;
    }}

    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {border_input};
        background-color: {bg_input};
        border-radius: 4px;
    }}

    QRadioButton::indicator {{
        border-radius: 9px;
    }}

    QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
        border: 1px solid {accent};
    }}

    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {accent};
        border: 1px solid {accent};
    }}

    /* Smooth Progress Bar */
    QProgressBar {{
        background-color: {btn_sec_bg};
        border: 1px solid {border_subtle};
        border-radius: 7px;
        text-align: center;
        color: {text_primary};
        font-size: 11px;
        font-weight: 600;
        height: 14px;
    }}

    QProgressBar::chunk {{
        background-color: {accent};
        border-radius: 6px;
    }}

    /* Terminal Log Console */
    QTextEdit#vlcLogConsole {{
        background-color: {"#0d0d10" if is_dark else "#18181b"};
        color: #e4e4e7;
        font-family: "DejaVu Sans Mono", "Fira Code", "Ubuntu Mono", "Consolas", monospace;
        font-size: 12px;
        line-height: 1.4;
        border: 1px solid {border_subtle};
        border-radius: 8px;
        padding: 10px;
        selection-background-color: {accent};
        selection-color: #ffffff;
    }}

    /* Media Library Table */
    QTableWidget {{
        background-color: {bg_card};
        color: {text_primary};
        border: 1px solid {border_subtle};
        border-radius: 8px;
        gridline-color: {border_subtle};
        font-size: 12px;
        selection-background-color: {accent_subtle};
        selection-color: {text_primary};
    }}

    QTableWidget::item {{
        padding: 6px 10px;
    }}

    QTableWidget::item:hover {{
        background-color: {table_hover};
    }}

    QHeaderView::section {{
        background-color: {bg_card_subtle};
        color: {text_secondary};
        font-weight: 600;
        font-size: 12px;
        padding: 8px 10px;
        border: none;
        border-bottom: 1px solid {border_subtle};
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background-color: {border_input};
        border-radius: 5px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {accent};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar:horizontal {{
        background-color: transparent;
        height: 10px;
        margin: 0;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {border_input};
        border-radius: 5px;
        min-width: 20px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {accent};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    """
