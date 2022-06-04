from PyQt5 import QtGui
from PyQt5 import QtCore
import pyqtgraph as pg


class LineSegmentItem(pg.GraphicsObject):
    def __init__(self, p1, p2):
        pg.GraphicsObject.__init__(self)
        self.p1 = p1
        self.p2 = p2
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        p.drawLine(QtCore.QPoint(self.p1[0], self.p1[1]), QtCore.QPoint(self.p2[0], self.p2[1]))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class EllipseItem(pg.GraphicsObject):
    def __init__(self, center, radius1, radius2=None, color='w'):
        pg.GraphicsObject.__init__(self)
        self.center = center
        self.radius1 = radius1
        if radius2 == None:
            self.radius2 = radius1
        else:
            self.radius2 = radius2
        self.color = color
        self.generatePicture()

    def generatePicture(self):

        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen(self.color))
        p.drawEllipse(QtCore.QPoint(int(self.center[0]),int(self.center[1])), self.radius1 * 2, self.radius2 * 2)
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class RectangleItem(pg.GraphicsObject):
    def __init__(self, topLeft, size):
        pg.GraphicsObject.__init__(self)
        self.topLeft = topLeft
        self.size = size
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        tl = QtCore.QPointF(self.topLeft[0], self.topLeft[1])
        size = QtCore.QSizeF(self.size[0], self.size[1])
        p.drawRect(QtCore.QRectF(tl, size))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())
