"""
setup.py — NoteDown first-run configuration
Logic: 100% unchanged. UI: completely redesigned.
"""

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Optional, Tuple

from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QBrush, QLinearGradient

try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PyQt6.QtMultimediaWidgets import QVideoWidget
    HAS_MULTIMEDIA = True
except Exception:
    HAS_MULTIMEDIA = False
    QMediaPlayer = None
    QAudioOutput = None
    QVideoWidget = None


# ── All unchanged helpers (no edits) ─────────────────────────────────────────

def _bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

def _ui_utils_dir() -> Path:
    return _bundle_root() / "ui_utils"

def _config_dir() -> Path:
    appdata = os.environ.get("APPDATA") or str(Path.home())
    return Path(appdata) / "NoteDown"

def _config_path() -> Path:
    return _config_dir() / "config.json"

def load_paths() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    cfg_path = _config_path()
    if not cfg_path.exists():
        return None, None, None
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        vault_path      = data.get("vault_path")
        assets_path     = data.get("assets_path")
        screenshot_path = data.get("screenshot_path")
        if not vault_path or not assets_path or not screenshot_path:
            return None, None, None
        return str(vault_path), str(assets_path), str(screenshot_path)
    except Exception:
        return None, None, None

def load_count() -> int:
    cfg_path = _config_path()
    if not cfg_path.exists():
        return 0
    try:
        data  = json.loads(cfg_path.read_text(encoding="utf-8"))
        value = data.get("count", 0)
        return int(value) if isinstance(value, (int, float, str)) else 0
    except Exception:
        return 0

def save_count(value: int) -> None:
    cfg_path = _config_path()
    cfg_dir  = _config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    payload  = {"count": int(value)}
    if cfg_path.exists():
        try:
            payload.update(json.loads(cfg_path.read_text(encoding="utf-8")))
        except Exception:
            pass
    cfg_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def save_paths(vault_path: str, assets_path: str, screenshot_path: str) -> None:
    cfg_dir        = _config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path       = _config_path()
    existing_count = load_count()
    payload = {
        "vault_path":      str(vault_path),
        "assets_path":     str(assets_path),
        "screenshot_path": str(screenshot_path),
        "count":           existing_count,
    }
    cfg_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def _apply_config_globals(vault_path: str, assets_path: str, screenshot_path: str) -> None:
    # Backwards-compat no-op:
    # Paths are read from `%APPDATA%/NoteDown/config.json` via `config.py`.
    return

def _ensure_assets_folder(vault_path: Path, assets_path: Path) -> Path:
    if not assets_path.exists():
        assets_path.mkdir(parents=True, exist_ok=True)
    return assets_path

def _show_and_exit_error(message: str) -> None:
    QMessageBox.critical(None, "Setup Required", message)
    QApplication.instance().quit()
    raise SystemExit(1)


# ── Design tokens ─────────────────────────────────────────────────────────────

_STYLE = """
/* ── Base ──────────────────────────────────────────────────────────────── */
QDialog, QWidget {
    background: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI Variable', 'SF Pro Text', 'Helvetica Neue', sans-serif;
}

/* ── Section step rows ──────────────────────────────────────────────────── */
QWidget#stepCard {
    background: #111720;
    border: 1px solid #1e2636;
    border-radius: 14px;
}

/* ── Step number badge ──────────────────────────────────────────────────── */
QLabel#stepBadge {
    background: rgba(56, 139, 253, 0.14);
    color: #58a6ff;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    qproperty-alignment: AlignCenter;
}
QLabel#stepBadgeDone {
    background: rgba(46, 160, 67, 0.18);
    color: #3fb950;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    qproperty-alignment: AlignCenter;
}

/* ── Step title ─────────────────────────────────────────────────────────── */
QLabel#stepTitle {
    font-size: 12px;
    font-weight: 600;
    color: #c9d1d9;
}

/* ── Path input ─────────────────────────────────────────────────────────── */
QLineEdit#pathEdit {
    background: #0d1117;
    border: 1.5px solid #21262d;
    border-radius: 10px;
    padding: 6px 12px;
    min-height: 34px;
    color: #8b949e;
    font-size: 11px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    selection-background-color: rgba(88, 166, 255, 0.3);
}
QLineEdit#pathEdit[populated="true"] {
    color: #58a6ff;
    border-color: rgba(56, 139, 253, 0.35);
    background: rgba(56, 139, 253, 0.05);
}

/* ── Browse button ──────────────────────────────────────────────────────── */
QPushButton#browseBtn {
    background: transparent;
    border: 1.5px solid #21262d;
    border-radius: 9px;
    padding: 6px 14px;
    min-height: 34px;
    font-size: 11px;
    font-weight: 600;
    color: #8b949e;
    min-width: 90px;
}
QPushButton#browseBtn:hover {
    border-color: #388bfd;
    color: #58a6ff;
    background: rgba(56, 139, 253, 0.07);
}
QPushButton#browseBtn:pressed {
    background: rgba(56, 139, 253, 0.12);
}

/* ── Cancel button ──────────────────────────────────────────────────────── */
QPushButton#cancelBtn {
    background: transparent;
    border: 1.5px solid #30363d;
    border-radius: 10px;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: 600;
    color: #6e7681;
    min-width: 90px;
}
QPushButton#cancelBtn:hover {
    border-color: #8b949e;
    color: #c9d1d9;
    background: rgba(255,255,255,0.04);
}

/* ── CTA (Start) button ─────────────────────────────────────────────────── */
QPushButton#ctaBtn {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #1f6feb, stop:1 #388bfd);
    border: none;
    border-radius: 10px;
    padding: 9px 24px;
    font-size: 12px;
    font-weight: 700;
    color: white;
    min-width: 140px;
}
QPushButton#ctaBtn:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #388bfd, stop:1 #58a6ff);
}
QPushButton#ctaBtn:pressed {
    background: #1158c7;
}
QPushButton#ctaBtn:disabled {
    background: #21262d;
    color: #6e7681;
}

/* ── Right panel (help) ─────────────────────────────────────────────────── */
QWidget#helpPanel {
    background: #0f141d;
    border: 1px solid #1e2636;
    border-radius: 16px;
}

/* ── Steps guide list ───────────────────────────────────────────────────── */
QLabel#guideStep {
    color: #8b949e;
    font-size: 11px;
    line-height: 1.6;
    padding: 4px 0;
}

/* ── Tip bar ────────────────────────────────────────────────────────────── */
QLabel#tipBar {
    background: rgba(227,179,65,0.08);
    color: #e3b341;
    border-left: 3px solid rgba(227,179,65,0.5);
    border-radius: 0 8px 8px 0;
    padding: 8px 12px;
    font-size: 11px;
    line-height: 1.5;
}

/* ── Section divider ────────────────────────────────────────────────────── */
QFrame#divider {
    background: #1e2636;
    max-height: 1px;
    border: none;
}

/* ── Video placeholder ──────────────────────────────────────────────────── */
QLabel#videoPlaceholder {
    background: #0d1117;
    border: 1px dashed #21262d;
    border-radius: 12px;
    color: #484f58;
    font-size: 11px;
    qproperty-alignment: AlignCenter;
}

QSplitter::handle {
    background: #1e2636;
    width: 1px;
}
"""


# ── Reusable step-row widget ──────────────────────────────────────────────────

class _StepRow(QWidget):
    """
    One folder-picker row:  [badge]  [title + hint]
                                     [path edit]  [browse btn]
    """

    def __init__(self, number: str, title: str, hint: str, btn_label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("stepCard")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(8)

        # ── Header row ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(10)

        self.badge = QLabel(number)
        self.badge.setObjectName("stepBadge")
        self.badge.setFixedSize(20, 20)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_col = QVBoxLayout()
        label_col.setSpacing(1)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("stepTitle")

        hint_lbl = QLabel(hint)
        hint_lbl.setStyleSheet("font-size:10px;color:#6e7681;")

        label_col.addWidget(title_lbl)
        label_col.addWidget(hint_lbl)

        header.addWidget(self.badge)
        header.addLayout(label_col)
        header.addStretch()
        outer.addLayout(header)

        # ── Input row ─────────────────────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(8)
        input_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.edit = QLineEdit()
        self.edit.setObjectName("pathEdit")
        self.edit.setReadOnly(True)
        self.edit.setPlaceholderText("No folder selected…")

        self.btn = QPushButton(btn_label)
        self.btn.setObjectName("browseBtn")
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)

        input_row.addWidget(self.edit, stretch=1)
        input_row.addWidget(self.btn)
        outer.addLayout(input_row)

    def set_path(self, path: str):
        self.edit.setText(path)
        self.edit.setProperty("populated", True)
        self.edit.setToolTip(path)
        self.edit.style().unpolish(self.edit)
        self.edit.style().polish(self.edit)
        # Flip badge to ✓
        self.badge.setText("✓")
        self.badge.setObjectName("stepBadgeDone")
        self.badge.style().unpolish(self.badge)
        self.badge.style().polish(self.badge)


# ── SetupDialog ───────────────────────────────────────────────────────────────

class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("NoteDown — Setup")
        # Larger default size so the 2-column layout never feels cramped.
        self.setFixedSize(1100, 650)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._vault_path:      Optional[Path] = None
        self._assets_path:     Optional[Path] = None
        self._screenshot_path: Optional[Path] = None

        self.setStyleSheet(_STYLE)
        self._build_ui()

        # Center on screen
        try:
            screen = QApplication.primaryScreen().availableGeometry()
            self.move(
                screen.x() + (screen.width()  - self.width())  // 2,
                screen.y() + (screen.height() - self.height()) // 2,
            )
        except Exception:
            pass

        # Pre-fill
        vault, assets, screenshot = load_paths()
        if vault and assets and screenshot:
            v, a, s = Path(vault), Path(assets), Path(screenshot)
            if v.exists() and a.exists() and s.exists():
                self._set_vault(v)
                self._set_assets(a)
                self._set_screenshot(s)
                self.cta_btn.setEnabled(True)
                return

        self.cta_btn.setEnabled(False)

    # ── Paint: card with rounded corners ─────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor("#0d1117")))
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        p.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 18, 18)

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ════════════════════════════════════════════════════════════════════
        # LEFT PANE — configuration
        # ════════════════════════════════════════════════════════════════════
        left = QWidget()
        left.setFixedWidth(470)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(28, 28, 24, 24)
        lv.setSpacing(0)

        # Header
        logo_row = QHBoxLayout()
        logo_lbl = QLabel("N↓")
        logo_lbl.setStyleSheet("""
            font-size:22px; font-weight:800;
            color:rgba(140,170,255,230); letter-spacing:-1px;
        """)
        logo_row.addWidget(logo_lbl)
        logo_row.addStretch()

        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton{background:rgba(255,255,255,.06);border:none;
                border-radius:12px;color:rgba(255,255,255,.35);font-size:16px;
                font-weight:300;padding-bottom:1px;}
            QPushButton:hover{background:rgba(248,81,73,.7);color:white;}
        """)
        close_btn.clicked.connect(self.on_cancel)
        logo_row.addWidget(close_btn)
        lv.addLayout(logo_row)
        lv.addSpacing(20)

        # Title
        title = QLabel("Set up NoteDown")
        title.setStyleSheet(
            "font-size:20px;font-weight:800;color:#e6edf3;letter-spacing:-0.5px;"
        )
        sub = QLabel(
            "Point NoteDown to your Obsidian vault and the\n"
            "folders where attachments & screenshots live."
        )
        sub.setStyleSheet("font-size:12px;color:#6e7681;line-height:1.5;")
        lv.addWidget(title)
        lv.addSpacing(4)
        lv.addWidget(sub)
        lv.addSpacing(22)

        # ── Step rows ─────────────────────────────────────────────────────────
        self._vault_row = _StepRow(
            "1", "Obsidian Vault",
            "The folder that contains .obsidian/",
            "Browse",
        )
        self._vault_row.btn.clicked.connect(self.pick_vault)

        self._assets_row = _StepRow(
            "2", "Assets Folder",
            "Where images & audio will be saved",
            "Browse",
        )
        self._assets_row.btn.clicked.connect(self.pick_assets)

        self._screenshot_row = _StepRow(
            "3", "Screenshot Folder",
            "Where NoteDown looks for screenshots",
            "Browse",
        )
        self._screenshot_row.btn.clicked.connect(self.pick_screenshot)

        for row in (self._vault_row, self._assets_row, self._screenshot_row):
            lv.addWidget(row)
            lv.addSpacing(8)

        # Expose the individual QLineEdit + QPushButton refs the old code used
        self.vault_edit      = self._vault_row.edit
        self.assets_edit     = self._assets_row.edit
        self.screenshot_edit = self._screenshot_row.edit
        self.vault_btn       = self._vault_row.btn
        self.assets_btn      = self._assets_row.btn
        self.screenshot_btn  = self._screenshot_row.btn

        # Tip
        self.tip_label = QLabel(
            "💡  No Assets folder yet? NoteDown will create one inside your vault."
        )
        self.tip_label.setObjectName("tipBar")
        self.tip_label.setWordWrap(True)
        lv.addWidget(self.tip_label)

        lv.addStretch()

        # Footer buttons
        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.on_cancel)

        self.cta_btn = QPushButton("▶  Start NoteDown")
        self.cta_btn.setObjectName("ctaBtn")
        self.cta_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cta_btn.clicked.connect(self.on_start)

        footer.addWidget(self.cancel_btn)
        footer.addWidget(self.cta_btn)
        lv.addLayout(footer)

        # ════════════════════════════════════════════════════════════════════
        # VERTICAL DIVIDER
        # ════════════════════════════════════════════════════════════════════
        vdiv = QFrame()
        vdiv.setFrameShape(QFrame.Shape.VLine)
        vdiv.setStyleSheet("background:#1e2636;max-width:1px;border:none;")

        # ════════════════════════════════════════════════════════════════════
        # RIGHT PANE — help
        # ════════════════════════════════════════════════════════════════════
        right = QWidget()
        right.setObjectName("helpPanel")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(24, 28, 24, 24)
        rv.setSpacing(14)

        # Help header
        help_title = QLabel("Quick Guide")
        help_title.setStyleSheet(
            "font-size:14px;font-weight:700;color:#e6edf3;letter-spacing:-0.2px;"
        )
        rv.addWidget(help_title)

        # Video slot
        self._video_slot = QWidget()
        self._video_slot.setMinimumHeight(240)
        vsl = QVBoxLayout(self._video_slot)
        vsl.setContentsMargins(0,0,0,0)

        if HAS_MULTIMEDIA:
            self.video_widget = QVideoWidget()
            self.video_widget.setMinimumHeight(240)
            self.video_widget.setStyleSheet("border-radius:10px;background:#0d1117;")
            vsl.addWidget(self.video_widget)

            self.player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.audio_output.setVolume(1.0)
            self.player.setAudioOutput(self.audio_output)
            self.player.setVideoOutput(self.video_widget)

            self._video_fallback_label = QLabel("")
            self._video_fallback_label.setObjectName("videoPlaceholder")
            self._video_fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._video_fallback_label.setWordWrap(True)
            self._video_fallback_label.setMinimumHeight(240)
            self._video_fallback_label.setVisible(False)
            vsl.addWidget(self._video_fallback_label)

            QTimer.singleShot(50, self._try_load_help_video)
        else:
            ph = QLabel("Video help isn't available on this system.")
            ph.setObjectName("videoPlaceholder")
            ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ph.setWordWrap(True)
            ph.setMinimumHeight(240)
            vsl.addWidget(ph)

        rv.addWidget(self._video_slot, stretch=1)

        # Divider
        hdiv = QFrame()
        hdiv.setObjectName("divider")
        hdiv.setFrameShape(QFrame.Shape.HLine)
        rv.addWidget(hdiv)

        # Guide steps
        guide_steps = [
            ("Vault",      "Pick the root folder that contains <code>.obsidian/</code>"),
            ("Assets",     "Pick your attachments folder — or let NoteDown create it"),
            ("Screenshot", "Pick where NoteDown scans for screenshots"),
        ]
        for label, desc in guide_steps:
            row = QHBoxLayout()
            row.setSpacing(10)
            dot = QLabel("•")
            dot.setStyleSheet("color:#388bfd;font-size:16px;padding-top:1px;")
            dot.setFixedWidth(14)
            txt = QLabel(f"<b style='color:#c9d1d9'>{label}</b> &mdash; {desc}")
            txt.setObjectName("guideStep")
            txt.setWordWrap(True)
            row.addWidget(dot, alignment=Qt.AlignmentFlag.AlignTop)
            row.addWidget(txt, stretch=1)
            rv.addLayout(row)

        # Bottom note
        bottom_note = QLabel(
            "Setup runs once. To reconfigure, delete "
            "<code style='color:#58a6ff'>%APPDATA%/NoteDown/config.json</code>."
        )
        bottom_note.setWordWrap(True)
        bottom_note.setStyleSheet("font-size:10px;color:#484f58;")
        rv.addWidget(bottom_note)

        root.addWidget(left)
        root.addWidget(vdiv)
        root.addWidget(right, stretch=1)

    # ── All core logic methods below are 100% unchanged ───────────────────────

    def _try_load_help_video(self) -> None:
        try:
            candidates  = ["setup.mp4", "setup_help.mp4", "paths.mp4", "where_to_point.mp4"]
            ui_utils    = _ui_utils_dir()
            video_path  = None
            for name in candidates:
                p = ui_utils / name
                if p.exists():
                    video_path = p
                    break

            if not video_path:
                self.video_widget.hide()
                if hasattr(self, "_video_fallback_label") and self._video_fallback_label:
                    self._video_fallback_label.setText(
                        "No help video found.\n\n"
                        "Add a file to `ui_utils/` named one of:\n"
                        "`setup.mp4`, `setup_help.mp4`, `paths.mp4`, `where_to_point.mp4`."
                    )
                    self._video_fallback_label.show()
                return

            if hasattr(self, "_video_fallback_label") and self._video_fallback_label:
                self._video_fallback_label.hide()
            self.video_widget.show()

            self.player.setSource(QUrl.fromLocalFile(str(video_path)))
            self.player.setLoops(-1)
            self.player.play()
        except Exception:
            if hasattr(self, "video_widget") and self.video_widget:
                self.video_widget.hide()
            if hasattr(self, "_video_fallback_label") and self._video_fallback_label:
                self._video_fallback_label.setText("Help video failed to load. Setup still works.")
                self._video_fallback_label.setVisible(True)

    def on_cancel(self) -> None:
        _show_and_exit_error("Setup was cancelled. Please run NoteDown again to configure it.")

    def pick_vault(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Select your Obsidian Vault folder (the folder containing `.obsidian/`)",
            str(Path.home()),
        )
        if not path:
            _show_and_exit_error("Vault selection cancelled. Setup cannot continue.")
            return
        v = Path(path)
        self._set_vault(v)
        default_assets = v / "Assets"
        self._set_assets(default_assets)

    def pick_assets(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Select the folder where NoteDown should save attachments (images/audio)",
            str(Path.home()),
        )
        if not path:
            _show_and_exit_error("Assets selection cancelled. Setup cannot continue.")
            return
        self._set_assets(Path(path))

    def pick_screenshot(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Select the folder where NoteDown should look for screenshots",
            str(Path.home()),
        )
        if not path:
            _show_and_exit_error("Screenshot selection cancelled. Setup cannot continue.")
            return
        self._set_screenshot(Path(path))

    def _set_vault(self, v: Path) -> None:
        self._vault_path = v
        self._vault_row.set_path(str(v))
        if not (v / ".obsidian").exists():
            self.vault_edit.setToolTip(
                "This vault doesn't contain `.obsidian/` — check you picked the right folder."
            )
        self._refresh_cta_state()

    def _set_assets(self, a: Path) -> None:
        self._assets_path = a
        self._assets_row.set_path(str(a))
        self._refresh_cta_state()

    def _set_screenshot(self, s: Path) -> None:
        self._screenshot_path = s
        self._screenshot_row.set_path(str(s))
        self._refresh_cta_state()

    def _refresh_cta_state(self) -> None:
        self.cta_btn.setEnabled(
            bool(self._vault_path and self._assets_path and self._screenshot_path)
        )

    def on_start(self) -> None:
        if not self._vault_path:
            QMessageBox.warning(self, "Missing Vault", "Please select your Obsidian Vault folder.")
            return
        if not self._assets_path:
            QMessageBox.warning(self, "Missing Assets Folder", "Please select your assets/attachments folder.")
            return
        if not self._screenshot_path:
            QMessageBox.warning(self, "Missing Screenshot Folder", "Please select your screenshot folder.")
            return

        vault      = self._vault_path
        assets     = self._assets_path
        screenshot = self._screenshot_path

        if not vault.exists():
            QMessageBox.critical(self, "Invalid Vault", "The selected Vault folder does not exist.")
            return
        if not screenshot.exists():
            QMessageBox.critical(self, "Invalid Screenshot Folder", "The selected Screenshot folder does not exist.")
            return

        try:
            assets = _ensure_assets_folder(vault, assets)
        except Exception as e:
            QMessageBox.critical(self, "Could not create Assets folder",
                                 f"Failed to create assets folder:\n{e}")
            return

        save_paths(str(vault), str(assets), str(screenshot))
        self._stop_help_video()
        self.accept()

    def _stop_help_video(self) -> None:
        try:
            if hasattr(self, "player") and self.player:
                self.player.stop()
        except Exception:
            pass

    def closeEvent(self, event) -> None:
        self._stop_help_video()
        return super().closeEvent(event)


# ── Entry point (100% unchanged) ─────────────────────────────────────────────

def _set_working_directory_for_ui_icons() -> None:
    try:
        os.chdir(str(_bundle_root()))
    except Exception:
        pass


def _launch_main_ui(app: QApplication) -> None:
    _set_working_directory_for_ui_icons()
    from ui import FloatingPanel
    panel = FloatingPanel()
    app._notedown_panel = panel
    panel.show()
    try:
        screen = QApplication.primaryScreen().availableGeometry()
        panel.move(
            screen.x() + (screen.width()  - panel.width())  // 2,
            screen.y() + (screen.height() - panel.height()) // 2,
        )
    except Exception:
        pass
    panel.raise_()
    panel.activateWindow()
    app.processEvents()


def _show_first_time_howto(parent=None) -> None:
    video_path = _ui_utils_dir() / "userguide.mp4"
    if not video_path.exists():
        QMessageBox.information(
            parent,
            "Welcome to NoteDown",
            "Quick guide video not found.\n\n"
            "Please add this file:\n"
            f"{video_path}",
        )
        return

    if not HAS_MULTIMEDIA:
        QMessageBox.information(
            parent,
            "Welcome to NoteDown",
            "Video playback is not available on this system.\n\n"
            f"Please watch this file manually:\n{video_path}",
        )
        return

    dlg = QDialog(parent)
    dlg.setWindowTitle("How to Use NoteDown")
    dlg.setModal(True)
    dlg.setFixedSize(940, 620)
    dlg.setStyleSheet(_STYLE)

    root = QVBoxLayout(dlg)
    root.setContentsMargins(18, 16, 18, 14)
    root.setSpacing(10)

    title = QLabel("How to Use NoteDown")
    title.setStyleSheet("font-size:18px;font-weight:800;color:#e6edf3;")
    sub = QLabel("Watch this short guide before you continue.")
    sub.setStyleSheet("font-size:12px;color:#8b949e;")
    root.addWidget(title)
    root.addWidget(sub)

    video = QVideoWidget()
    video.setMinimumHeight(500)
    video.setStyleSheet("background:#0d1117;border:1px solid #21262d;border-radius:12px;")
    root.addWidget(video, stretch=1)

    footer = QHBoxLayout()
    footer.addStretch()
    ok_btn = QPushButton("Continue")
    ok_btn.setObjectName("ctaBtn")
    ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    ok_btn.clicked.connect(dlg.accept)
    footer.addWidget(ok_btn)
    root.addLayout(footer)

    player = QMediaPlayer(dlg)
    audio_output = QAudioOutput(dlg)
    audio_output.setVolume(1.0)
    player.setAudioOutput(audio_output)
    player.setVideoOutput(video)
    player.setSource(QUrl.fromLocalFile(str(video_path)))
    player.setLoops(-1)
    player.play()

    def _stop_player(_):
        try:
            player.stop()
        except Exception:
            pass

    dlg.finished.connect(_stop_player)
    dlg.exec()


def main() -> None:
    try:
        print("[NoteDown] Starting setup...")
        app = QApplication(sys.argv)
        # Prevent Qt from quitting when transient setup/guide dialogs close.
        # The floating panel is shown immediately afterward.
        app.setQuitOnLastWindowClosed(False)

        vault, assets, screenshot = load_paths()
        if vault and assets and screenshot:
            print(f"[NoteDown] Loaded config vault={vault} assets={assets}")
            v, a, s = Path(vault), Path(assets), Path(screenshot)
            if v.exists():
                try:
                    if not a.exists():
                        a.mkdir(parents=True, exist_ok=True)
                    if not s.exists():
                        raise FileNotFoundError(f"Screenshot folder not found: {s}")
                    _apply_config_globals(vault, str(a), str(s))

                    print("[NoteDown] Launching main UI...")
                    _launch_main_ui(app)
                    sys.exit(app.exec())
                except Exception:
                    print("[NoteDown] Config path invalid; opening setup.")
                    traceback.print_exc()

        print("[NoteDown] Showing setup dialog...")
        dlg = SetupDialog()
        dlg.show()

        res = dlg.exec()
        if res != QDialog.DialogCode.Accepted:
            sys.exit(0)

        save_count(1)

        print("[NoteDown] Setup complete; launching main UI...")
        _launch_main_ui(app)
        sys.exit(app.exec())
    except Exception:
        msg = traceback.format_exc()
        print("[NoteDown] Fatal error:\n" + msg)
        try:
            QMessageBox.critical(None, "NoteDown Error", msg)
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()