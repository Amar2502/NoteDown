import sys

from PyQt6.QtCore import Qt, QTimer, QPoint, QVariantAnimation, QPropertyAnimation
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QToolTip, QDialog, QLineEdit, QTreeWidget, QTreeWidgetItem, QStyle, QFrame,
    QGraphicsDropShadowEffect
)

import core
from utils.folder import get_folders, get_file_names
from config import get_notes_dir

# ------------------ TOAST ------------------

# ── Icon glyphs per level (unicode, no emoji rendering issues on most OSes) ──
_ICONS = {
    "info":    "ℹ",
    "success": "✓",
    "error":   "✕",
    "warning": "⚠",
}

# ── Per-level color tokens ────────────────────────────────────────────────────
_STYLES = {
    "info": {
        "bg":           "rgba(13, 17, 23, 242)",
        "border":       "rgba(48, 54, 61, 255)",
        "accent":       "rgba(56, 139, 253, 255)",       # blue bar
        "icon_bg":      "rgba(31, 111, 235, 0.15)",
        "icon_color":   "#58a6ff",
        "text":         "#e6edf3",
        "sub":          "#8b949e",
    },
    "success": {
        "bg":           "rgba(13, 17, 23, 242)",
        "border":       "rgba(48, 54, 61, 255)",
        "accent":       "rgba(46, 160, 67, 255)",        # green bar
        "icon_bg":      "rgba(46, 160, 67, 0.15)",
        "icon_color":   "#3fb950",
        "text":         "#e6edf3",
        "sub":          "#8b949e",
    },
    "error": {
        "bg":           "rgba(13, 17, 23, 242)",
        "border":       "rgba(48, 54, 61, 255)",
        "accent":       "rgba(248, 81, 73, 255)",        # red bar
        "icon_bg":      "rgba(248, 81, 73, 0.15)",
        "icon_color":   "#f85149",
        "text":         "#e6edf3",
        "sub":          "#8b949e",
    },
    "warning": {
        "bg":           "rgba(13, 17, 23, 242)",
        "border":       "rgba(48, 54, 61, 255)",
        "accent":       "rgba(210, 153, 34, 255)",       # amber bar
        "icon_bg":      "rgba(210, 153, 34, 0.15)",
        "icon_color":   "#e3b341",
        "text":         "#e6edf3",
        "sub":          "#8b949e",
    },
}


class Toast(QLabel):
    def __init__(self):
        super().__init__(None)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # ── Inner label (actual content) ──────────────────────────────────────
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        self.hide()


class QuickHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(500, 360)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        card = QFrame(self)
        card.setObjectName("helpCard")
        card.setStyleSheet("""
            QFrame#helpCard {
                background: rgba(11, 14, 22, 235);
                border: 1px solid rgba(255, 255, 255, 22);
                border-radius: 16px;
            }
            QLabel#helpTitle {
                color: #e6edf3;
                font-size: 20px;
                font-weight: 800;
            }
            QLabel#helpText {
                color: #8b949e;
                font-size: 14px;
                line-height: 1.65;
            }
            QPushButton#helpClose {
                background: rgba(255,255,255,0.06);
                color: rgba(255,255,255,0.60);
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 700;
                padding: 9px 18px;
                min-width: 140px;
            }
            QPushButton#helpClose:hover {
                background: rgba(56, 139, 253, 0.35);
                color: white;
            }
        """)

        root = QVBoxLayout(card)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(10)
        dot = QLabel("•")
        dot.setStyleSheet("color:#388bfd;font-size:22px;padding-top:2px;")
        dot.setFixedWidth(18)
        title = QLabel("Quick Start")
        title.setObjectName("helpTitle")
        header.addWidget(dot, alignment=Qt.AlignmentFlag.AlignTop)
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        text = QLabel(
            "<span style='color:#e6edf3'><b>Where notes are saved</b></span><br>"
            "• Pick your <b style='color:#c9d1d9'>Obsidian Vault</b> root in setup (folder containing <b style='color:#c9d1d9'>.obsidian</b>)<br>"
            "• In session start, choose a <b style='color:#c9d1d9'>folder path</b> if you want notes inside a subfolder<br>"
            "• Leave folder empty to save notes at the <b style='color:#c9d1d9'>vault root</b><br><br>"
            "<span style='color:#e6edf3'><b>How to use</b></span><br>"
            "<b style='color:#c9d1d9'>1)</b> Click <b style='color:#c9d1d9'>Start / End Session</b><br>"
            "<b style='color:#c9d1d9'>2)</b> Copy text, then click <b style='color:#c9d1d9'>Text</b><br>"
            "<b style='color:#c9d1d9'>3)</b> Take screenshot, then click <b style='color:#c9d1d9'>Image</b><br>"
            "<b style='color:#c9d1d9'>4)</b> Click <b style='color:#c9d1d9'>Audio</b>, speak, click again to save<br>"
            "<b style='color:#c9d1d9'>5)</b> Click <b style='color:#c9d1d9'>Start / End Session</b> again to finish<br><br>"
            "<span style='color:#6e7681'>Tip:</span> Click <b style='color:#c9d1d9'>N↓</b> to open your vault quickly."
        )
        text.setObjectName("helpText")
        text.setWordWrap(True)
        root.addWidget(text)

        root.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()
        close_btn = QPushButton("Got it, let’s start")
        close_btn.setObjectName("helpClose")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)
        root.addLayout(footer)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)

    # ── Style ─────────────────────────────────────────────────────────────────

    def _apply_style(self, level):
        s = _STYLES.get(level, _STYLES["info"])
        icon = _ICONS.get(level, "ℹ")

        # Single-label approach: icon + text baked into rich text via HTML,
        # keeping the original single-QLabel structure intact.
        self._current_icon = icon
        self._current_s = s

        self.label.setStyleSheet(f"""
            QLabel {{
                background: {s['bg']};
                color: {s['text']};
                border: 1px solid {s['border']};
                border-left: 3px solid {s['accent']};
                border-radius: 12px;
                padding: 11px 18px 11px 14px;
                font-size: 13px;
                font-weight: 400;
                font-family: 'SF Pro Display', 'Segoe UI Variable', 'Inter', system-ui, sans-serif;
            }}
        """)

    # ── Show ──────────────────────────────────────────────────────────────────

    def show_message(self, text, level="info", duration=2200):
        self._apply_style(level)

        s = self._current_s
        icon = self._current_icon

        # Compose HTML: colored icon badge + message text side by side
        self.label.setText(
            f'<span style="color:{s["icon_color"]};font-weight:600;">{icon}</span>'
            f'&nbsp;&nbsp;'
            f'<span style="color:{s["text"]};">{text}</span>'
        )

        self.setMinimumWidth(300)
        self.setMaximumWidth(480)

        self.adjustSize()

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 80

        self.move(x, y)

        self.setWindowOpacity(0)
        self.show()

        # Fade in — ease out for snappy feel
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(180)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.start()

        QTimer.singleShot(duration, self.fade_out)

    # ── Fade out ──────────────────────────────────────────────────────────────

    def fade_out(self):
        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_anim.setDuration(220)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.finished.connect(self.hide)
        self.fade_out_anim.start()


# ------------------ SESSION DIALOG ------------------

SESSION_DIALOG_STYLE = """
/* ── Root dialog ─────────────────────────────────────────── */
QDialog {
    background-color: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 16px;
}

/* ── Section labels ──────────────────────────────────────── */
QLabel#sectionLabel {
    color: #8b949e;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── Selected path label ─────────────────────────────────── */
QLabel#pathLabel {
    color: #58a6ff;
    font-size: 10px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    padding: 4px 10px;
    background: rgba(88, 166, 255, 0.08);
    border: 1px solid rgba(88, 166, 255, 0.18);
    border-radius: 6px;
}

/* ── Warning / suggestion label ─────────────────────────── */
QLabel#warnLabel {
    font-size: 10px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #e3b341;
    padding-left: 2px;
}

/* ── Name input ──────────────────────────────────────────── */
QLineEdit#nameInput {
    background: #161b22;
    border: 1.5px solid #30363d;
    border-radius: 10px;
    padding: 10px 14px;
    color: #e6edf3;
    font-size: 13px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    selection-background-color: rgba(88, 166, 255, 0.35);
}
QLineEdit#nameInput:focus {
    border: 1.5px solid #388bfd;
    background: #1a2130;
}
QLineEdit#nameInput[invalid="true"] {
    border: 1.5px solid #f85149;
    background: rgba(248, 81, 73, 0.07);
}

/* ── Folder tree ─────────────────────────────────────────── */
QTreeWidget#folderTree {
    background: #161b22;
    border: 1.5px solid #30363d;
    border-radius: 12px;
    padding: 6px 4px;
    color: #c9d1d9;
    outline: none;
    font-size: 12px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
QTreeWidget#folderTree::item {
    padding: 5px 6px;
    border-radius: 7px;
    margin: 1px 2px;
}
QTreeWidget#folderTree::item:hover {
    background: rgba(88, 166, 255, 0.10);
    color: #e6edf3;
}
QTreeWidget#folderTree::item:selected {
    background: rgba(88, 166, 255, 0.22);
    color: #58a6ff;
    border: none;
}
QTreeWidget#folderTree::branch {
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 6px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ── Divider ─────────────────────────────────────────────── */
QFrame#divider {
    background: #21262d;
    max-height: 1px;
    border: none;
}

/* ── Cancel button ───────────────────────────────────────── */
QPushButton#cancelBtn {
    background: transparent;
    border: 1.5px solid #30363d;
    border-radius: 9px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 600;
    color: #8b949e;
    min-width: 80px;
}
QPushButton#cancelBtn:hover {
    background: #21262d;
    border-color: #8b949e;
    color: #c9d1d9;
}
QPushButton#cancelBtn:pressed {
    background: #161b22;
}

/* ── OK / Start button ───────────────────────────────────── */
QPushButton#okBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f6feb,
        stop:1 #388bfd
    );
    border: none;
    border-radius: 9px;
    padding: 8px 20px;
    font-size: 12px;
    font-weight: 700;
    color: #ffffff;
    min-width: 80px;
}
QPushButton#okBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #388bfd,
        stop:1 #58a6ff
    );
}
QPushButton#okBtn:pressed {
    background: #1158c7;
}
"""


class SessionNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Session")
        self.setModal(True)
        self.setFixedSize(460, 480)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet(SESSION_DIALOG_STYLE)
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Outer container (gives us the rounded border + shadow feel)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget(self)
        card.setObjectName("card")
        card.setStyleSheet("""
            QWidget#card {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 16px;
            }
        """)
        outer.addWidget(card)

        root = QVBoxLayout(card)
        root.setContentsMargins(20, 20, 20, 18)
        root.setSpacing(0)

        # ── Header row ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel("Start Session")
        title_lbl.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #e6edf3;
            letter-spacing: -0.3px;
        """)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6e7681;
                font-size: 18px;
                font-weight: 400;
                border-radius: 6px;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background: #21262d;
                color: #e6edf3;
            }
        """)
        close_btn.clicked.connect(self.reject)

        header.addWidget(title_lbl)
        header.addStretch()
        header.addWidget(close_btn)
        root.addLayout(header)
        root.addSpacing(18)

        # ── Session name section ──────────────────────────────────────────────
        name_lbl = QLabel("SESSION NAME")
        name_lbl.setObjectName("sectionLabel")
        root.addWidget(name_lbl)
        root.addSpacing(6)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("nameInput")
        self.name_input.setPlaceholderText("e.g. transformers-notes")
        self.name_input.textChanged.connect(self._update_suggestions)
        root.addWidget(self.name_input)
        root.addSpacing(5)

        self.suggestion_label = QLabel("")
        self.suggestion_label.setObjectName("warnLabel")
        self.suggestion_label.setFixedHeight(16)
        root.addWidget(self.suggestion_label)
        root.addSpacing(14)

        # ── Divider ────────────────────────────────────────────────────────────
        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(div)
        root.addSpacing(14)

        # ── Folder section ────────────────────────────────────────────────────
        folder_lbl = QLabel("SAVE IN FOLDER")
        folder_lbl.setObjectName("sectionLabel")
        root.addWidget(folder_lbl)
        root.addSpacing(6)

        self.folder_tree = QTreeWidget()
        self.folder_tree.setObjectName("folderTree")
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.setUniformRowHeights(True)
        self.folder_tree.setAnimated(True)
        self.folder_tree.setIndentation(16)
        self.folder_tree.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder_tree.setExpandsOnDoubleClick(True)
        self.folder_tree.setItemsExpandable(True)
        root.addWidget(self.folder_tree, stretch=1)
        root.addSpacing(8)

        self.selected_path_label = QLabel("/ root")
        self.selected_path_label.setObjectName("pathLabel")
        root.addWidget(self.selected_path_label)
        root.addSpacing(16)

        # ── Buttons ───────────────────────────────────────────────────────────
        div2 = QFrame()
        div2.setObjectName("divider")
        div2.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(div2)
        root.addSpacing(14)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setShortcut("Esc")
        cancel_btn.clicked.connect(self.reject)

        ok_btn = QPushButton("▶  Start")
        ok_btn.setObjectName("okBtn")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setDefault(True)
        ok_btn.setAutoDefault(True)
        ok_btn.clicked.connect(self.accept)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        root.addLayout(buttons)

        # ── Populate & wire ───────────────────────────────────────────────────
        self._populate_folder_tree(get_folders())
        self.folder_tree.itemSelectionChanged.connect(self._on_folder_selection_changed)
        self._update_suggestions("")

    # ── Core logic (UNCHANGED) ────────────────────────────────────────────────

    def _populate_folder_tree(self, folder_paths):
        self.folder_tree.clear()

        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)

        root_item = QTreeWidgetItem(["Root"])
        root_item.setData(0, Qt.ItemDataRole.UserRole, "")
        root_item.setIcon(0, folder_icon)
        root_item.setExpanded(True)
        self.folder_tree.addTopLevelItem(root_item)

        nodes_by_path = {"": root_item}

        from pathlib import Path

        for rel_path in sorted(folder_paths):
            parts = Path(rel_path).parts
            if not parts:
                continue

            parent_item = root_item

            for i, part in enumerate(parts):
                current_path = "/".join(parts[: i + 1])

                if current_path in nodes_by_path:
                    parent_item = nodes_by_path[current_path]
                    continue

                item = QTreeWidgetItem([part])
                item.setData(0, Qt.ItemDataRole.UserRole, current_path)
                item.setIcon(0, folder_icon)

                parent_item.addChild(item)
                nodes_by_path[current_path] = item

                parent_item = item

        self.folder_tree.setCurrentItem(root_item)
        self.folder_tree.expandItem(root_item)

    def _on_folder_selection_changed(self):
        folder = self._selected_folder()
        display = f"/ {folder.replace('/', '  /  ')}" if folder else "/ root"
        self.selected_path_label.setText(display)

    def _update_suggestions(self, text):
        text = text.strip().lower()

        if not text:
            self.suggestion_label.setText("")
            self.name_input.setProperty("invalid", False)
            self.name_input.style().unpolish(self.name_input)
            self.name_input.style().polish(self.name_input)
            return

        folder = self._selected_folder()
        notes_dir = get_notes_dir()
        base = notes_dir / folder if folder else notes_dir

        if not base.exists():
            self.suggestion_label.setText("")
            return

        files = [f.name for f in base.iterdir() if f.is_file()]
        input_name = text if text.endswith(".md") else f"{text}.md"

        for f in files:
            if f.lower() == input_name:
                self.name_input.setProperty("invalid", True)
                self.name_input.style().unpolish(self.name_input)
                self.name_input.style().polish(self.name_input)
                self.suggestion_label.setText(f"⚠  File already exists: {f}")
                return

        self.name_input.setProperty("invalid", False)
        self.name_input.style().unpolish(self.name_input)
        self.name_input.style().polish(self.name_input)

        base_name = input_name.replace(".md", "")
        similar = [f for f in files if f.lower().startswith(base_name)]

        if similar:
            self.suggestion_label.setText(f"⚑  Similar: {', '.join(similar[:2])}")
        else:
            self.suggestion_label.setText("")

    def _selected_folder(self) -> str:
        item = self.folder_tree.currentItem()
        if not item:
            return ""
        value = item.data(0, Qt.ItemDataRole.UserRole)
        return value if isinstance(value, str) else ""

    def get_data(self):
        name = self.name_input.text().strip()
        return name, self._selected_folder()


from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QApplication, QDialog
)
from PyQt6.QtCore import Qt, QPoint, QVariantAnimation, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QIcon, QColor, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient


# ── CircleButton ──────────────────────────────────────────────────────────────

class CircleButton(QPushButton):
    def __init__(self, icon_path, tooltip):
        super().__init__()

        self.base_alpha = 0.0

        self.setFixedSize(44, 44)
        self.setToolTip(tooltip)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.size() * 0.48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.update_style(self.base_alpha)

    def update_style(self, alpha):
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, {alpha});
                border-radius: 22px;
                border: 1px solid rgba(255, 255, 255, 0.07);
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.16);
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.06);
            }}
        """)

    def set_active(self, active: bool):
        """Highlight button when its feature is in an active/recording state."""
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(248, 81, 73, 0.22);
                    border-radius: 22px;
                    border: 1px solid rgba(248, 81, 73, 0.45);
                }
                QPushButton:hover {
                    background: rgba(248, 81, 73, 0.32);
                }
            """)
        else:
            self.update_style(self.base_alpha)

    def pulse(self):
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(550)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.anim.setStartValue(0.0)
        self.anim.setKeyValueAt(0.4, 0.22)
        self.anim.setEndValue(0.0)
        self.anim.valueChanged.connect(self.update_style)
        self.anim.start()


# ── FloatingPanel ─────────────────────────────────────────────────────────────

_PANEL_BG       = QColor(11, 14, 22, 215)
_PANEL_BORDER   = QColor(255, 255, 255, 22)
_DIVIDER_COLOR  = QColor(255, 255, 255, 12)


class FloatingPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(66, 295)

        self.drag_pos = QPoint()
        self.session_active = False
        self.audio_active   = False

        # ── Root layout ───────────────────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Close button ──────────────────────────────────────────────────────
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(18, 18)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.06);
                color: rgba(255,255,255,0.35);
                border: none;
                border-radius: 9px;
                font-size: 13px;
                font-weight: 300;
                padding-bottom: 1px;
            }
            QPushButton:hover {
                background: rgba(248, 81, 73, 0.75);
                color: white;
            }
        """)
        self.close_btn.clicked.connect(QApplication.quit)

        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(18, 18)
        self.help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_btn.setToolTip("Quick start guide")
        self.help_btn.setStyleSheet("""
            QPushButton {
                background: rgba(56, 139, 253, 0.18);
                color: rgba(198, 225, 255, 0.95);
                border: none;
                border-radius: 9px;
                font-size: 11px;
                font-weight: 700;
                padding-bottom: 1px;
            }
            QPushButton:hover {
                background: rgba(56, 139, 253, 0.42);
                color: white;
            }
        """)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.addStretch()
        top_bar.addWidget(self.help_btn)
        top_bar.addSpacing(6)
        top_bar.addWidget(self.close_btn)

        # ── Brand label ───────────────────────────────────────────────────────
        self.brand_label = QLabel("N↓")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_label.setStyleSheet("""
            QLabel {
                color: rgba(140, 170, 255, 200);
                font-size: 18px;
                font-weight: 800;
                letter-spacing: -0.5px;
            }
        """)

        # ── Action buttons ────────────────────────────────────────────────────
        self.session_btn = CircleButton("ui_utils/start.svg",  "Start / End Session")
        self.text_btn    = CircleButton("ui_utils/text.svg",   "Capture Text")
        self.image_btn   = CircleButton("ui_utils/image.svg",  "Capture Image")
        self.audio_btn   = CircleButton("ui_utils/audio.svg",  "Record Audio")

        for btn in (self.session_btn, self.text_btn, self.image_btn, self.audio_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # ── Assemble ──────────────────────────────────────────────────────────
        layout.addLayout(top_bar)
        layout.addSpacing(4)
        layout.addWidget(self.brand_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self.session_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(9)
        layout.addWidget(self.text_btn,    alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(9)
        layout.addWidget(self.image_btn,   alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(9)
        layout.addWidget(self.audio_btn,   alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        # ── Toast ─────────────────────────────────────────────────────────────
        self.toast = Toast()

        # ── Signals ───────────────────────────────────────────────────────────
        self.session_btn.clicked.connect(self.toggle_session)
        self.text_btn.clicked.connect(self.get_text)
        self.image_btn.clicked.connect(self.get_image)
        self.audio_btn.clicked.connect(self.toggle_audio)
        self.help_btn.clicked.connect(self.show_quick_help)

    # ── Paint: pill-shaped frosted panel ─────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = self.rect().adjusted(1, 1, -1, -1)

        # Background fill
        painter.setBrush(QBrush(_PANEL_BG))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(r, 20, 20)

        # Subtle top highlight — gives glass depth
        highlight = QLinearGradient(r.left(), r.top(), r.left(), r.top() + 40)
        highlight.setColorAt(0, QColor(255, 255, 255, 18))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight))
        painter.drawRoundedRect(r, 20, 20)

        # Border
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(_PANEL_BORDER, 1))
        painter.drawRoundedRect(r, 20, 20)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _show_action_error(self, error):
        self.toast.show_message(str(error), "error", 3200)

    def show_quick_help(self):
        dlg = QuickHelpDialog(self)
        # Place near the floating panel so it feels connected.
        dlg.move(self.x() - dlg.width() - 14, self.y())
        dlg.exec()

    def _ensure_session_active(self):
        if self.session_active:
            return True
        self.toast.show_message("Start a session first", "error", 2500)
        return False

    # ── Actions (logic UNCHANGED) ─────────────────────────────────────────────

    def toggle_session(self):
        try:
            if not self.session_active:
                dialog = SessionNameDialog(self)
                dialog.name_input.setFocus()

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    name, folder = dialog.get_data()
                    if not name:
                        return

                    core.start_session(name, folder)
                    self.session_active = True
                    self.session_btn.setIcon(QIcon("ui_utils/stop.svg"))
                    self.session_btn.set_active(True)
                    self.toast.show_message("Session started", "success")
            else:
                core.end_session()
                self.session_active = False
                self.audio_active   = False
                self.session_btn.setIcon(QIcon("ui_utils/start.svg"))
                self.session_btn.set_active(False)
                self.audio_btn.setIcon(QIcon("ui_utils/audio.svg"))
                self.audio_btn.set_active(False)
                self.toast.show_message("Session ended", "info")

        except Exception as e:
            self._show_action_error(e)

    def get_text(self):
        if not self._ensure_session_active():
            return
        try:
            core.handle_text()
            self.toast.show_message("Text saved", "success")
            self.text_btn.pulse()
        except Exception as e:
            self._show_action_error(e)

    def get_image(self):
        if not self._ensure_session_active():
            return
        try:
            core.handle_image()
            self.toast.show_message("Image saved", "success")
            self.image_btn.pulse()
        except Exception as e:
            self._show_action_error(e)

    def toggle_audio(self):
        if not self._ensure_session_active():
            return
        try:
            core.handle_audio()
            self.audio_active = not self.audio_active

            if self.audio_active:
                self.audio_btn.setIcon(QIcon("ui_utils/music.svg"))
                self.audio_btn.set_active(True)
                self.toast.show_message("Recording...", "info")
            else:
                self.audio_btn.setIcon(QIcon("ui_utils/audio.svg"))
                self.audio_btn.set_active(False)
                self.toast.show_message("Audio saved", "success")
                self.audio_btn.pulse()
        except Exception as e:
            self._show_action_error(e)

    # ── Drag (UNCHANGED) ──────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPosition().toPoint()
# ------------------ MAIN ------------------

def main():
    app = QApplication(sys.argv)
    QToolTip.setFont(QFont("Segoe UI", 9))

    ui = FloatingPanel()
    ui.move(200, 200)
    ui.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
