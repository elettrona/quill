from quill.ui.editor_surface import PLAIN, RICH, surface_kind


class _PlainCtrl:
    pass


class _MethodSurface:
    def surface_kind(self) -> str:
        return RICH


class _AttrSurface:
    surface_kind = "rich"


def test_plain_control_defaults_to_plain() -> None:
    assert surface_kind(_PlainCtrl()) == PLAIN


def test_method_surface_reports_kind() -> None:
    assert surface_kind(_MethodSurface()) == RICH


def test_attribute_surface_reports_kind() -> None:
    assert surface_kind(_AttrSurface()) == RICH


def test_none_is_plain() -> None:
    assert surface_kind(None) == PLAIN
