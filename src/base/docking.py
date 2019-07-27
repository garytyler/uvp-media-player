from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QKeySequence, QPainter, QStaticText, QTextOption
from PyQt5.QtWidgets import (
    QAction,
    QDockWidget,
    QLabel,
    QMenu,
    QProxyStyle,
    QSizePolicy,
    QSpacerItem,
    QStyle,
    QTabBar,
    QToolBar,
    QToolButton,
    QWidget,
)

from ..gui import icons


class ToolBar(QToolBar):

    Separator = 11
    Spacer = 12

    def __init__(self, title, parent=None, objects=[], collapsible=True, icon_size=36):
        super().__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        for i in objects:
            if isinstance(i, QMenu):
                self.add_menu(i)
            elif isinstance(i, QAction):
                self.addAction(i)
            elif isinstance(i, QWidget):
                self.addWidget(i)
            elif isinstance(i, int):
                if i == self.Separator:
                    self.addSeparator()
                elif i == self.Spacer:
                    self.add_spacer()

        self.set_title(title)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setMovable(True)
        self.setFloatable(True)
        self.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.set_ext_bttn_icon()

        if not collapsible:
            self.minimumSizeHint = lambda: self.sizeHint()

        self.topLevelChanged.connect(self.on_topLevelChanged)

    def add_spacer(self):
        w = QWidget(self)
        w.setMinimumWidth(5)
        self.addWidget(w)

    def set_ext_bttn_icon(self):
        ext_bttn = self.findChild(
            (QToolButton),
            name="qt_toolbar_ext_button",
            options=Qt.FindDirectChildrenOnly,
        )
        ext_bttn.setIcon(icons.toolbar_ext_bttn)

    def set_title(self, title):
        title = title.strip().lower().capitalize()
        self.toggleViewAction().setText(title)

    def add_menu(self, menu):
        action = menu.menuAction()
        self.addAction(action)
        button = self.widgetForAction(action)
        button.setPopupMode(QToolButton.InstantPopup)

    def on_topLevelChanged(self, topLevel):
        print(self.allowedAreas())
        # for area in self.allowedAreas():
        # print(area)  # self.


class CornerToolBar(ToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMaximumWidth(self.sizeHint().width())
        self.setMovable(False)
        self.setFloatable(False)
        self.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)


class DockableToolBarWidget(QDockWidget):
    def __init__(self, toolbar: ToolBar, titlebar=True, minimum=False):
        super().__init__(
            toolbar.toggleViewAction().text(),
            parent=toolbar.parent(),
            # flags=Qt.AlignRight,
        )
        self.setWidget(toolbar)

        self.setFeatures(QDockWidget.DockWidgetMovable)

        if titlebar:
            self.setFeatures(
                QDockWidget.DockWidgetVerticalTitleBar | QDockWidget.DockWidgetMovable
            )
            self.setup_title_bar(title=toolbar.toggleViewAction().text(), vertical=True)
        else:
            self.setFeatures(QDockWidget.NoDockWidgetFeatures)
            self.setTitleBarWidget(QWidget(None))

    def setup_title_bar(self, title, vertical=True):

        if self.features() & QDockWidget.DockWidgetVerticalTitleBar:
            self.title_bar = VerticalDockableWidgetTitleBar(title, self)
            self.setTitleBarWidget(self.title_bar)
        else:
            self.title_bar = HorizontalDockableWidgetTitleBar(title, self)
            self.setTitleBarWidget(self.title_bar)

    # @pyqtSlot(Qt.DockWidgetArea)
    # def on_dockLocationChanged(self, area):
    #     print("dockwidget on_dockLocationChanged", area)

    # @pyqtSlot(QDockWidget.DockWidgetFeatures)
    # def on_featuresChanged(self, features):
    #     print("dockwidget on_featuresChanged", features)

    # @pyqtSlot(bool)
    # def on_topLevelChanged(self, topLevel):
    #     print("dockwidget on_topLevelChanged", topLevel)


class CornerToolbarWidget(DockableToolBarWidget):
    def __init__(self, toolbar):
        super().__init__(self, toolbar, titlebar=False)
        print("Asdf")


class DockableWidget(QDockWidget):
    def __init__(self, title="", parent=None, titlebar=False):
        super().__init__(title, parent=parent)
        self._title = title
        self._parent = parent

        # self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # self.setFeatures(
        #     QDockWidget.DockWidgetVerticalTitleBar | QDockWidget.DockWidgetMovable
        # )
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.setTitleBarWidget(QWidget(None))

        # self.dockLocationChanged.connect(self.on_dockLocationChanged)
        # self.featuresChanged.connect(self.on_featuresChanged)
        # self.topLevelChanged.connect(self.on_topLevelChanged)

    def setup_title_bar(self):
        if self.features() & QDockWidget.DockWidgetVerticalTitleBar:
            self.title_bar = VerticalDockableWidgetTitleBar(self._title, self)
            self.setTitleBarWidget(self.title_bar)
        else:
            self.title_bar = HorizontalDockableWidgetTitleBar(self._title, self)
            self.setTitleBarWidget(self.title_bar)

    # @pyqtSlot(Qt.DockWidgetArea)
    # def on_dockLocationChanged(self, area):
    #     print("dockwidget on_dockLocationChanged", area)

    # @pyqtSlot(QDockWidget.DockWidgetFeatures)
    # def on_featuresChanged(self, features):
    #     print("dockwidget on_featuresChanged", features)

    # @pyqtSlot(bool)
    # def on_topLevelChanged(self, topLevel):
    #     print("dockwidget on_topLevelChanged", topLevel)


class DockableTabbedWidget(QDockWidget):
    def __init__(self, title="", parent=None, titlebar=False):
        super().__init__(title, parent=parent)
        self._title = title
        self._parent = parent

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # self.setFeatures(
        #     QDockWidget.DockWidgetVerticalTitleBar | QDockWidget.DockWidgetMovable
        # )
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.setTitleBarWidget(QWidget(None))

        # self.dockLocationChanged.connect(self.on_dockLocationChanged)
        # self.featuresChanged.connect(self.on_featuresChanged)
        # self.topLevelChanged.connect(self.on_topLevelChanged)

    def setup_title_bar(self):
        if self.features() & QDockWidget.DockWidgetVerticalTitleBar:
            self.title_bar = VerticalDockableWidgetTitleBar(self._title, self)
            self.setTitleBarWidget(self.title_bar)
        else:
            self.title_bar = HorizontalDockableWidgetTitleBar(self._title, self)
            self.setTitleBarWidget(self.title_bar)

    # @pyqtSlot(Qt.DockWidgetArea)
    # def on_dockLocationChanged(self, area):
    #     print("dockwidget on_dockLocationChanged", area)

    # @pyqtSlot(QDockWidget.DockWidgetFeatures)
    # def on_featuresChanged(self, features):
    #     print("dockwidget on_featuresChanged", features)

    # @pyqtSlot(bool)
    # def on_topLevelChanged(self, topLevel):
    #     print("dockwidget on_topLevelChanged", topLevel)


class HorizontalDockableWidgetTitleBar(QLabel):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setObjectName("horizontal-dock-title-bar")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._margin_height = 20
        self.adjustSize()

    def minimumSizeHint(self):
        return self.sizeHint()

    def sizeHint(self):
        size = super().sizeHint()
        return QSize(size.width(), self._margin_height)


class VerticalDockableWidgetTitleBar(QLabel):
    def __init__(self, text, parent):
        super().__init__(text, parent)
        self.setObjectName("vertical-dock-title-bar")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.text = text
        self._margin_height = 20
        self.text_rect = None

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setClipping(True)
        painter.rotate(-90)
        painter.translate(-self.height(), 0)
        flags = Qt.AlignCenter
        self.text_rect = painter.boundingRect(
            0, 0, self.height(), self.width(), flags, self.text
        )
        painter.drawText(self.text_rect, flags, self.text)
        painter.end()

    def minimumSizeHint(self):
        return self.sizeHint()

    def sizeHint(self):
        size = super().sizeHint()
        return QSize(size.height(), size.width())

    # def sizeHint(self):
    #     if self.text_rect:
    #         return QSize(self._margin_height, self.height())
    #     else:
    #         return QSize(self._margin_height, self.height())

    # def sizeHint(self):
    #     size = super().sizeHint()
    #     if self.text_rect:
    #         return QSize(self.text_rect.height(), size.height())
    #     else:
    #         return QSize(size.height(), size.height())


class ElidedTabTextProxyStyle(QProxyStyle):
    """Set tab text to elided on a QTabBar on tabbed QDockWidgets"""

    def __init__(self):
        QProxyStyle.__init__(self)

    def styleHint(self, hint, opt=0, widget=0, returnData=0):
        # curr_shape = QTabBar.TriangularEast
        if hint == QStyle.SH_TabBar_Alignment and isinstance(widget, QTabBar):
            widget.setElideMode(Qt.ElideRight)
        return super().styleHint(hint, opt, widget, returnData)


class TabsOnRightProxyStyle(QProxyStyle):
    """Moves tabs to right side of a QTabBar when installed to a QDockWidget, but a
    potentially buggy solution with side effects and low performance"""

    def __init__(self):
        QProxyStyle.__init__(self)

    def styleHint(self, hint, opt=0, widget=0, returnData=0):
        widgets = []
        curr_shape = QTabBar.TriangularEast
        if hint == QStyle.SH_TabBar_Alignment and isinstance(widget, QTabBar):
            if widget.shape() != curr_shape:
                if widget not in widgets:
                    widgets.append(widget)
                    return Qt.AlignRight
                else:
                    widgets.append(widget)
                    print("opt.shape", opt.shape)
                    print("opt.text", opt.text)
                    print("opt.icon", opt.icon)
                    print("opt.row", opt.row)
                    print("opt.position", opt.position)
                    print("opt.selectedPosition", opt.selectedPosition)
                    print("opt.cornerWidgets", opt.cornerWidgets)
                    print("opt.iconSize", opt.iconSize)
                    print("opt.documentMode", opt.documentMode)
                    print("opt.leftButtonSize", opt.leftButtonSize)
                    print("opt.rightButtonSize", opt.rightButtonSize)
                    print("opt.features", opt.features)
        return super().styleHint(hint, opt, widget, returnData)
