"""Medula penceresini arka planda izleyen polling watcher.

Akış:
  1) Belirli aralıklarla (varsayılan 1.0 sn) Botanik EOS penceresinde
     IE_Server child'larından HTML çekilir.
  2) Sayfa tipi tespit edilir (medula_parser.detect_page_kind).
  3) "e_recete_detay" görüldüğünde reçete parse edilir.
  4) Aynı e-reçete numarası daha önce işlenmemişse callback tetiklenir.

Kullanım:
    watcher = MedulaWatcher(on_recete=handle)
    watcher.start()       # ayrı thread'de döngü başlar
    ...
    watcher.stop()

Callback imzası:
    handle(cap: PrescriptionCapture, html: str) -> None
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Optional

import comtypes

from .medula_capture import (
    MedulaWindow,
    capture_one,
    find_medula_windows,
)
from .medula_parser import PrescriptionCapture, parse_html

log = logging.getLogger("medula_watcher")

CallbackT = Callable[[PrescriptionCapture, str], None]


class MedulaWatcher:
    def __init__(
        self,
        on_recete: CallbackT,
        interval: float = 1.0,
        target_page_kinds: tuple[str, ...] = ("e_recete_detay",),
    ):
        self._cb = on_recete
        self._interval = interval
        self._targets = target_page_kinds
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._seen_recete_no: set[str] = set()
        self._last_url_per_ie: dict[int, str] = {}

    # ----------------------------------------------------------------- API
    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="medula-watcher")
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    def reset_seen(self) -> None:
        self._seen_recete_no.clear()

    # ----------------------------------------------------------------- loop
    def _loop(self) -> None:
        comtypes.CoInitialize()
        try:
            while not self._stop.is_set():
                try:
                    self._tick()
                except Exception as e:
                    log.warning("watcher tick error: %s", e, exc_info=False)
                # interval, ama dur sinyali gelirse erken çık
                self._stop.wait(self._interval)
        finally:
            try:
                comtypes.CoUninitialize()
            except Exception:
                pass

    def _tick(self) -> None:
        windows = find_medula_windows()
        if not windows:
            return
        for w in windows:
            for ie_hwnd in w.ie_servers:
                cap_info = capture_one(ie_hwnd)
                if "error" in cap_info:
                    continue
                url  = cap_info.get("url", "") or ""
                html = cap_info.get("html", "") or ""
                if not html:
                    continue

                # Hafif optimizasyon: URL+title değişmemişse parse atla.
                # NOT: Medula JSF ile aynı URL içinde içerik değişiyor; bu yüzden
                # URL eşliyse bile periyodik parse şart, ama biz yine de farklı
                # bir kontrol yapacağız (recete_no dedup ile).
                prescription = parse_html(html, document_url=url)
                if prescription.page_kind not in self._targets:
                    continue
                rno = prescription.recete_no.strip()
                if not rno:
                    # No yoksa hash al (basit)
                    rno = f"hash_{hash(html) & 0xFFFFFFFF:x}"
                if rno in self._seen_recete_no:
                    continue
                self._seen_recete_no.add(rno)
                log.info("Yeni e-reçete tespit edildi: %s (hasta=%s, ilaç=%d)",
                         rno, prescription.hasta_ad, len(prescription.drugs))
                try:
                    self._cb(prescription, html)
                except Exception as e:
                    log.error("callback error: %s", e, exc_info=True)
