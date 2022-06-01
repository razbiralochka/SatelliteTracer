from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from main import Ui_MainWindow
import sys
import pyqtgraphutils as pgutils
 
 
class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._img = None
        self.plot_settings()
        self.ui.pbPlot.clicked.connect(self.draw_path)
        self.ui.sldDrowV.valueChanged.connect(self.change_drowning_velocity)

        self.x = []
        self.y = []

        self.timer = None

        self.t = 0

        self.catch_oo = False
        self.l_oo = 0
        self.ts_oo = 0
        self.tk_oo = 0
        self.t_oo = 0

        self.catch_gs = False
        self.l_gs = 0
        self.ts_gs = 0
        self.tk_gs = 0
        self.t_gs = 0

        self.zones = []

    def plot_settings(self):
        '''
        Установка параметров для графика
        '''      
        bottom_plot = pg.AxisItem('bottom', pen=0.0, textPen=0.0)
        left_plot = pg.AxisItem('left', pen=0.0, textPen=0.0)
        top_plot = pg.AxisItem('top', pen=0.0, textPen=0.0)
        right_plot = pg.AxisItem('right', pen=0.0, textPen=0.0)

        self.ui.pwPlot.setBackground('w')
        self.ui.pwPlot.setAxisItems({'bottom':bottom_plot})
        self.ui.pwPlot.setAxisItems({'left':left_plot})
        self.ui.pwPlot.setAxisItems({'top':top_plot})
        self.ui.pwPlot.setAxisItems({'right':right_plot})
        self.ui.pwPlot.setLabel('left', 'Широта, град',)
        self.ui.pwPlot.setLabel('bottom', 'Долгота, град',)

        self.ui.pwPlot.setYRange(-90, 90, padding=0)
        self.ui.pwPlot.setXRange(-180, 180, padding=0)
        self.ui.pwPlot.setLimits(xMin=-180, xMax=180, yMin=-90, yMax=90)

        img = QtGui.QImage('map.png').mirrored(vertical=True)
        img = img.convertToFormat(QtGui.QImage.Format_ARGB32_Premultiplied)
        imgArray = pg.imageToArray(img, copy=True)

        self._img = pg.ImageItem(imgArray)
        self.set_img()
    
    def set_img(self):
        '''
        Установка карты на фон
        '''
        self.ui.pwPlot.addItem(self._img)
        self._img.setZValue(-100)
        self._img.setOpacity(0.85)
        self._img.setRect(pg.QtCore.QRectF(-180,-90,360,180))
        self.ui.pwPlot.showGrid(x=True, y=True, alpha=1)

    def change_drowning_velocity(self):
        '''
        Изменение скорости отрисовки
        '''
        self.timer.setInterval(self.ui.sldDrowV.value())


    def draw_path(self):
        '''
        Расчёт координат КА и отрисовка его местоположения на графике
        '''
        self.timer = QtCore.QTimer()
        self.ui.pwPlot.clear()
        self.set_img()
        self.x.clear()
        self.y.clear()
        self.zones.clear()

        self.catch_oo = False
        self.l_oo = 0
        self.ts_oo = 0
        self.tk_oo = 0
        self.t_oo = 0

        self.catch_gs = False
        self.l_gs = 0
        self.ts_gs = 0
        self.tk_gs = 0
        self.t_gs = 0


        mu = 3987e11
        Re = 6371*1000
        wz = 0.00007292115078

        i = np.deg2rad(float(self.ui.lnInclination.text()))
        Ha = float(self.ui.lnApofis.text())*1000
        Hp = float(self.ui.lnPerigos.text())*1000
        o0 = np.deg2rad(float(self.ui.lnOmega.text()))
        w0 = np.deg2rad(float(self.ui.lnArgPer.text()))

        lmoo = float(self.ui.lnLongitudeOO.text())
        fioo = float(self.ui.lnLatitudeOO.text())
        lmgs = float(self.ui.lnLongitudeGSRI.text())
        figs = float(self.ui.lnLatitudeGSRI.text())

        object_observation = pgutils.EllipseItem([lmoo-1, fioo-1], 1, color=(0, 0, 0))
        text_oo = pg.TextItem(text='Объект наблюдения', color=(0, 0, 0))
        
        ground_station = pgutils.EllipseItem([lmgs-1, figs-1], 1, color='r')
        text_gs = pg.TextItem(text='НППИ', color='r')

        self.ui.pwPlot.addItem(object_observation)
        self.ui.pwPlot.addItem(text_oo)
        text_oo.setPos(lmoo+1, fioo)

        self.ui.pwPlot.addItem(ground_station)
        self.ui.pwPlot.addItem(text_gs)
        text_gs.setPos(lmgs+1, figs)

        if (abs(np.rad2deg(i)) > 180) or (np.rad2deg(o0)>360) or (Hp>Ha):
            i = np.deg2rad(45)
            o0 = np.deg2rad(10)
            w0 = np.deg2rad(0)
            Hp = 500*1000
            Ha = 500*1000

        t0 = 0
        nvitkov = int(self.ui.sbNCoils.value())
        dt = self.ui.sbStep.value()

        e0 = [0 for i in range(5)]

        Rp = Re+Hp
        Ra = Re+Ha
        e = (Ra-Rp)/(Ra+Rp)
        a = (Rp+Ra)/2
        Ts = 2*np.pi*(a**3/mu)**.5
        p = a*(1-e**2)
        dOmega = np.deg2rad((-35.052/60)*(Re/p)**2*np.cos(i))
        dArgper = np.deg2rad((-17.523/60)*(Re/p)**2*(1-5*np.cos(i)**2))

        self.t = t0

        y = 15

        H = (Hp+Ha)/2
        alphazr = np.arccos(Re/(Re+H))

        lmgss = []
        figss = []

        fii = np.linspace(0, 2*np.pi, 60)
        for k in fii:
            lm_gss = alphazr*np.cos(k)+np.deg2rad(lmgs)
            if lm_gss>np.pi: lm_gss =lm_gss-2*np.pi
            if lm_gss<-np.pi: lm_gss =lm_gss+2*np.pi
            lmgss.append(np.rad2deg(lm_gss))

            fi_gss = alphazr*np.sin(k)+np.deg2rad(figs)
            if fi_gss>np.pi/2: fi_gss =fi_gss-np.pi
            if fi_gss<-np.pi/2: fi_gss =fi_gss+np.pi
            figss.append(np.rad2deg(fi_gss))

        def real_time_plotting():
            o = o0 + (self.t/Ts)*dOmega
            w = w0 + (self.t/Ts)*dArgper

            tzv = 1.00273791*self.t
            msr = tzv*(mu/a**3)**.5
            
            e0[0] = msr+e*np.sin(msr)+(e*e/2)*np.sin(2*msr)
            e0[1] = e**3/24*(9*np.sin(3*msr)-3*np.sin(msr))
            e0[2] = e**4/(24*8)*(64*np.sin(4*msr)-32*np.sin(2*msr))
            e0[3] = e**5/(120*16)*(625*np.sin(5*msr)+5*81*np.sin(3*msr)+10*np.sin(msr))
            e0[4] = e**6/(720*32)*(36*36*6*np.sin(6*msr)-6*256*4*np.sin(4*msr)+15*32*np.sin(2*msr))
            
            E = sum(e0)

            sint = (1-e**2)**.5*np.sin(E)/(1-e*np.cos(E))
            cost = (np.cos(E)-e)/(1-e*np.cos(E))

            teta = np.arctan((1-cost**2)**.5/cost)

            if sint>0 and cost<0:
                teta = teta + np.pi
            elif sint<0 and cost<0:
                teta = np.pi - teta
            elif sint<0 and cost>0:
                teta = 2*np.pi-teta

            r = p/(1+e*np.cos(teta))
            alpha = np.arcsin(r/Re*np.sin(np.deg2rad(y))) - np.deg2rad(y)
            u = w + teta

            sinfi = np.sin(i)*np.sin(u)

            fi = np.arcsin(sinfi)

            sinlm = (np.sin(o)*np.cos(u)+np.cos(o)*np.cos(i)*np.sin(u))/np.cos(fi)
            coslm = (np.cos(o)*np.cos(u)-np.sin(o)*np.cos(i)*np.sin(u))/np.cos(fi)

            if sinlm>0 and coslm>0:
                lm = np.arctan(sinlm/(1-sinlm**2)**.5)
            elif sinlm>0 and coslm<0:
                lm = np.pi+np.arctan((1-coslm**2)**.5/coslm)
            elif sinlm<0 and coslm<0:
                lm = np.pi-np.arctan(sinlm/(1-sinlm**2)**.5)
            elif sinlm<0 and coslm>0:
                lm = -np.arctan((1-coslm**2)**.5/coslm)

            #lm1 = lm-dOmega*self.t/Ts
            lm = lm-wz*self.t-dOmega*self.t/Ts

            if lm < -np.pi:
                lm = lm + 2*np.pi
            elif lm > np.pi:
                lm = lm - 2*np.pi

            self.x.append(np.rad2deg(lm))
            self.y.append(np.rad2deg(fi))
            
            self.ui.pwPlot.plot(x=self.x, pen=None, y=self.y, symbol='o', symbolPen=None, symbolSize=3, symbolBrush=.0, clear=True)
            gss = pg.PlotDataItem(x=lmgss, pen=None, y=figss, symbol='o', symbolPen=None, symbolSize=3, symbolBrush='r')
            self.ui.pwPlot.addItem(gss)
            
            if abs(np.arccos(np.sin(fi)*np.sin(np.deg2rad(fioo))+np.cos(fi)*np.cos(np.deg2rad(fioo))*np.cos(np.deg2rad(lmoo)-lm))) < alpha:
                self.zones.append(pgutils.EllipseItem([np.rad2deg(lm)-y, np.rad2deg(fi)-y], y, color=(0, 0, 0)))
                if self.catch_oo == False:
                    self.catch_oo = True
                    self.ts_oo = self.t
                    self.l_oo += 1
            else:
                if self.catch_oo == True:
                    self.catch_oo = False
                    self.tk_oo = self.t
                    self.t_oo += self.tk_oo-self.ts_oo
            
            if abs(np.arccos(np.sin(np.deg2rad(figs))*np.sin(fi)+np.cos(np.deg2rad(figs))*np.cos(fi)*np.cos(lm-np.deg2rad(lmgs)))) < alphazr:
                if self.catch_gs == False:
                    self.catch_gs = True
                    self.ts_gs = self.t
                    self.l_gs += 1
            else:
                if self.catch_gs == True:
                    self.catch_gs = False
                    self.tk_gs = self.t
                    self.t_gs += self.tk_gs-self.ts_gs



            self.set_img()
            self.ui.pwPlot.addItem(object_observation)
            self.ui.pwPlot.addItem(text_oo)
            self.ui.pwPlot.addItem(ground_station)
            self.ui.pwPlot.addItem(text_gs)
            if len(self.zones) != 0:
                for zone in self.zones:
                    self.ui.pwPlot.addItem(zone)
            
            self.t += dt
            if self.t > (Ts+100)*nvitkov:
                self.timer.stop()
                self.ui.ln_loo.setText(str(int(self.l_oo)))
                self.ui.ln_too.setText(str(round(self.t_oo/self.l_oo/60, 3)))
                self.ui.ln_lgs.setText(str(int(self.l_gs)))
                self.ui.ln_tgs.setText(str(round(self.t_gs/self.l_gs/60, 3)))

        self.timer.timeout.connect(real_time_plotting)
        self.timer.setInterval(self.ui.sldDrowV.value())
        self.timer.start()

app = QtWidgets.QApplication(sys.argv)
application = mywindow()
application.show()

sys.exit(app.exec())