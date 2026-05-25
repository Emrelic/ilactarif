"""Botanik EOS içindeki gömülü Internet Explorer_Server'dan canlı HTML çek.

Mimari:
  - Botanik EOS bir WinForms uygulamasıdır (class: WindowsForms10.Window.8.app.*)
  - Top-level pencere başlığı: "MEDULA <ver> <KULLANICI> (A)" formatı
  - Uygulama içinde Win32 child olarak "Internet Explorer_Server" (Trident) gömülü
  - WM_HTML_GETOBJECT mesajı ile o pencereden IHTMLDocument2 alınır
  - document.url ve documentElement.outerHTML okunabilir

Bağımlılık: pywin32, comtypes
"""
from __future__ import annotations

import ctypes
import os
from ctypes.wintypes import HWND, LPARAM
from dataclasses import dataclass, field

import comtypes
import comtypes.client


_user32  = ctypes.windll.user32
_oleacc  = ctypes.windll.oleacc

# Microsoft tarafından yayınlı registered window message
_WM_HTML_GETOBJECT = _user32.RegisterWindowMessageW("WM_HTML_GETOBJECT")

# IHTMLDocument2 COM Interface IID
_IID_IHTMLDocument2 = comtypes.GUID("{332C4425-26CB-11D0-B483-00C04FD90119}")

_user32.SendMessageTimeoutW.restype  = ctypes.c_void_p
_oleacc.ObjectFromLresult.restype    = ctypes.HRESULT


# ---------------------------------------------------------------------------
# MSHTML typelib (ilk çağrıda Python'da otomatik wrapper üretilir, ~1 sn)
# ---------------------------------------------------------------------------
_MSHTML = None


def _get_mshtml():
    global _MSHTML
    if _MSHTML is None:
        windir = os.environ.get("WINDIR", r"C:\Windows")
        tlb = os.path.join(windir, "System32", "mshtml.tlb")
        _MSHTML = comtypes.client.GetModule(tlb)
    return _MSHTML


# ---------------------------------------------------------------------------
# Pencere keşfi
# ---------------------------------------------------------------------------
_EnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, HWND, LPARAM)


@dataclass
class MedulaWindow:
    hwnd:       int
    title:      str
    class_name: str
    pid:        int
    ie_servers: list = field(default_factory=list)   # list[int] child hwnd


def _get_pid(hwnd: int) -> int:
    pid = ctypes.c_ulong(0)
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def enum_top_windows() -> list[tuple[int, str, str, int]]:
    """Görünür top-level pencereleri (hwnd, title, class, pid) olarak listele."""
    items = []
    def cb(hwnd, lparam):
        if not _user32.IsWindowVisible(hwnd):
            return True
        buf = ctypes.create_unicode_buffer(512)
        _user32.GetWindowTextW(hwnd, buf, 512)
        if not buf.value:
            return True
        cls = ctypes.create_unicode_buffer(128)
        _user32.GetClassNameW(hwnd, cls, 128)
        items.append((hwnd, buf.value, cls.value, _get_pid(hwnd)))
        return True
    _user32.EnumWindows(_EnumProc(cb), 0)
    return items


def enum_child_windows(parent_hwnd: int) -> list[tuple[int, str]]:
    items = []
    def cb(hwnd, lparam):
        cls = ctypes.create_unicode_buffer(128)
        _user32.GetClassNameW(hwnd, cls, 128)
        items.append((hwnd, cls.value))
        return True
    _user32.EnumChildWindows(parent_hwnd, _EnumProc(cb), 0)
    return items


def find_medula_windows() -> list[MedulaWindow]:
    """Başlığında 'MEDULA' içeren top-level pencereleri ve içlerindeki IE_Server'ları bul."""
    result = []
    for hwnd, title, cls, pid in enum_top_windows():
        if "MEDULA" not in title.upper():
            continue
        ie_hwnds = [h for h, c in enum_child_windows(hwnd) if c == "Internet Explorer_Server"]
        result.append(MedulaWindow(
            hwnd=hwnd, title=title, class_name=cls, pid=pid, ie_servers=ie_hwnds,
        ))
    return result


def find_ie_servers_all() -> list[tuple[int, int]]:
    """Tüm görünür pencerelerin altında IE_Server child'larını tara (Botanik tespit edilemezse fallback).

    Döndürür: list[(parent_hwnd, ie_hwnd)]
    """
    out = []
    for hwnd, title, cls, pid in enum_top_windows():
        for ch, ccls in enum_child_windows(hwnd):
            if ccls == "Internet Explorer_Server":
                out.append((hwnd, ch))
    return out


# ---------------------------------------------------------------------------
# IE_Server hwnd'sinden IHTMLDocument2 al
# ---------------------------------------------------------------------------
def get_ie_document(ie_hwnd: int):
    """WM_HTML_GETOBJECT + ObjectFromLresult ile IHTMLDocument2 POINTER'ı döndür."""
    mshtml = _get_mshtml()

    SMTO_ABORTIFHUNG = 0x0002
    lres = ctypes.c_void_p(0)
    rc = _user32.SendMessageTimeoutW(
        HWND(ie_hwnd),
        ctypes.c_uint(_WM_HTML_GETOBJECT),
        0, 0,
        SMTO_ABORTIFHUNG,
        2000,
        ctypes.byref(lres),
    )
    if not rc or not lres.value:
        return None

    doc_ptr = ctypes.POINTER(mshtml.IHTMLDocument2)()
    try:
        _oleacc.ObjectFromLresult(
            lres,
            ctypes.byref(_IID_IHTMLDocument2),
            0,
            ctypes.byref(doc_ptr),
        )
    except OSError as e:
        return None
    return doc_ptr


# ---------------------------------------------------------------------------
# HTML + URL çek
# ---------------------------------------------------------------------------
def capture_one(ie_hwnd: int) -> dict:
    """Tek bir IE_Server'dan {url, title, html} veya hata bilgisi döndür."""
    doc = get_ie_document(ie_hwnd)
    if doc is None:
        return {"ie_hwnd": ie_hwnd, "error": "IHTMLDocument2 alınamadı"}
    try:
        url   = doc.url
        title = doc.title or ""
        # IHTMLDocument2'de body var; outerHTML için IHTMLElement gereklidir
        body = doc.body
        if body is None:
            return {"ie_hwnd": ie_hwnd, "url": url, "title": title,
                    "html": "", "error": "body None"}
        # body parent element → <html> kökü, tüm sayfa
        html_root = body
        try:
            html_root = body.parentElement or body
        except Exception:
            pass
        outer = html_root.outerHTML or ""
        return {"ie_hwnd": ie_hwnd, "url": url, "title": title, "html": outer}
    except Exception as e:
        return {"ie_hwnd": ie_hwnd, "error": f"{type(e).__name__}: {e}"}


def capture_window(mw: MedulaWindow) -> list[dict]:
    return [capture_one(h) for h in mw.ie_servers]
