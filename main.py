from PyQt5.uic import loadUiType

from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QAction, QFileDialog, QInputDialog
from PyQt5.QtWidgets import QTableWidgetItem as itemSet

import sys
import re,math
import matplotlib as mpl
import numpy as np

from scipy.signal import find_peaks, peak_widths, peak_prominences
from lmfit.models import GaussianModel, LinearModel

import sqlite3
from sqlite3 import Error
 
Ui_MainWindow, QMainWindow, = loadUiType('window.ui')
Ui_Dialog, QDialog, = loadUiType('AsBrDialog.ui')

class Main(QMainWindow, Ui_MainWindow):
     def __init__(self, ):
        super().__init__()
        self.setupUi(self)
        self.actionOpen.triggered.connect(self.openFileDialog) 
        self.actionQuit.triggered.connect(QtCore.QCoreApplication.instance().quit) 
        self.actionAnalyze.triggered.connect(self.Analyze)  
        self.actionCon.triggered.connect(self.showDialog)
        self.actionAsBr.triggered.connect(self.AsBr)
        self.actionAsPb.triggered.connect(self.AsBrDialog)
        self.fig_dict = {}
        self.mplfigs.itemClicked.connect(self.changefig)
        global x,y
        x={}
        y={}
          
     def openFileDialog(self,):    
        fname, _filter = QtWidgets.QFileDialog.getOpenFileName(self, 
                             'Open File',"","Text Files (*.txt)")
        f = open(fname,'r')      
        with f:
             global name, AsKbNet, b1_local, b1_data, a1_local, a1_data, NGa
             pattern = r"([\b\w\-.()\s]+).txt"
             match = re.search(pattern,fname)
             if match :
                  name=match.group()
             data=np.loadtxt(fname,skiprows=21)
             xo=data[:,0]
             yo=data[:,1]
             x[name]=xo[np.where(1<xo)]
             y[name]=yo[np.where(1<xo)]
             self.plot()
             self.addfig(name, self.fig)
             self.tableWidget.clear()
             self.tableWidget.setRowCount(0)
             AsKbNet=0
             NGa=0
             b1_local=[]
             b1_data=[]
             a1_local=[]
             a1_data=[]
             
     def plot(self,):         
        self.rmmpl()
        self.fig=Figure()
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        self.ax1.set(facecolor='#FFFFCC',ylabel='Counts')
        self.ax2.set(facecolor='#FFFFCC',xlabel='E(keV)',ylabel='Counts')
        self.ax1.plot(x[name],y[name]) 
        self.addmpl(self.fig)
        self.sukien()
        
     def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, 
                self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self.toolbar)

     def rmmpl(self,):
             self.mplvl.removeWidget(self.canvas)
             self.canvas.close()
             self.mplvl.removeWidget(self.toolbar)
             self.toolbar.close()


     def addfig(self, name, fig):         
        self.fig_dict[name] = fig
        self.mplfigs.addItem(name)  

     def changefig(self, item):
        text = item.text()
        global name, AsKbNet, b1_local, b1_data, a1_local, a1_data, NGa
        name=text
        self.plot()   
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        AsKbNet=0
        NGa=0
        b1_local=[]
        b1_data=[]
        a1_local=[]
        a1_data=[]
        
     def sukien(self,):             
          mpl.widgets.AxesWidget(self.ax1)
          self.span = SpanSelector(self.ax1, self.onselect, 'horizontal', useblit=True,
                    rectprops=dict(alpha=0.5, facecolor='red'), button=1)
          self.fig.canvas.mpl_connect('button_press_event', self.onclick)
             
     def onclick(self,event,):
          if event.button==3:
               global a1_local
               a1_local=[]
               if a1_data==[]:
                    self.Analyze()
               else:
                    self.table_def()
                    self.ax2.cla()
                    self.ax2.set(facecolor='#FFFFCC',xlabel='E(keV)',ylabel='Counts')
                    self.canvas.draw()
                    for i in range(len(a1_data)):
                         self.tableWidget.setRowCount(i+2)
                         self.tableWidget.setItem(i+1, 0, itemSet(str(i+1)))
                         self.tableWidget.setItem(i+1, 1,itemSet(str(a1_data[i][0])))
                         self.tableWidget.setItem(i+1, 2,itemSet(str(a1_data[i][1])))
                         self.tableWidget.setItem(i+1, 3,itemSet(str(a1_data[i][2])))
                         self.tableWidget.setItem(i+1, 4,itemSet(str(a1_data[i][3])))
                         self.tableWidget.setItem(i+1, 5,itemSet(str(a1_data[i][4])))
                         self.tableWidget.setItem(i+1, 6,itemSet(str(a1_data[i][5])))
               if NGa !=0:
                    self.concentration()
                    
     def table_def(self,):
           self.tableWidget.setRowCount(1)
           self.tableWidget.setColumnCount(7)
           self.tableWidget.setItem(0, 0,itemSet('No.'))
           self.tableWidget.setItem(0, 1,itemSet('Element'))
           self.tableWidget.setItem(0, 2,itemSet('Line'))
           self.tableWidget.setItem(0, 3, itemSet('Energy/keV'))
           self.tableWidget.setItem(0, 4, itemSet('Net'))
           self.tableWidget.setItem(0, 5, itemSet('Backgr.'))
           self.tableWidget.setItem(0, 6, itemSet('Sigma'))
           self.sukien()
          
     def onselect(self, xmin, xmax): 
          self.ax2.cla()
          global a1_data, a1_local, b1, NGa, x_local, y_local, dtphong, dtthuc, sigma, b1_local, thisx, thisy, dinh
          if a1_data==[]:
                self.Analyze()
          indmin, indmax = np.searchsorted(x[name], (xmin, xmax))
          indmax = min(len(x[name]) - 1, indmax)
          x_local= x[name][indmin:indmax]
          y_local= y[name][indmin:indmax]
          peaks,_ = find_peaks(y_local,width=5,threshold=2)
          results_half = peak_widths(y_local,peaks, rel_height=0.5)
          left=results_half[2]*(max(x_local)-min(x_local))/len(x_local)+1
          right=results_half[3]*(max(x_local)-min(x_local))/len(x_local)+1
          gauss_mod = GaussianModel(prefix='gauss_')
          linear_mod = LinearModel(prefix='linear_')
          b1=[]
          b1_local=[]
          a1_local=[]
          self.ax2.plot(x_local, y_local)
          self.rmmpl()
          self.addmpl(self.fig)  
          for i in range(len(peaks)):
               FWHM=round(right[i]-left[i],3)
               phi=(FWHM)*2.355
               xmin=x_local[peaks[i]]-phi/2
               xmax=x_local[peaks[i]]+phi/2
               indmin, indmax = np.searchsorted(x_local, (xmin, xmax))
               indmax = min(len(x_local) - 1, indmax)
               thisx = x_local[indmin:indmax]
               thisy = y_local[indmin:indmax]
               pars = gauss_mod.guess(thisy, x=thisx)
               pars += linear_mod.make_params(intercept=thisy.min(), slope=0)
               mod = gauss_mod + linear_mod
               out = mod.fit(thisy, pars, x=thisx)
               comps = out.eval_components(x=thisx)
               dttong=int(sum(out.best_fit))
               dtphong=int(sum(comps['linear_']))
               dtthuc=int(dttong-dtphong)
               dinh=peaks[i]
               self.data_b1line((x_local[peaks[i]]-0.05)*1000,(x_local[peaks[i]]+0.05)*1000)
          for i in range(len(peaks)):
               FWHM=round(right[i]-left[i],3)
               phi=(FWHM)*2.355
               xmin=x_local[peaks[i]]-phi/2
               xmax=x_local[peaks[i]]+phi/2
               indmin, indmax = np.searchsorted(x_local, (xmin, xmax))
               indmax = min(len(x_local) - 1, indmax)
               thisx = x_local[indmin:indmax]
               thisy = y_local[indmin:indmax]
               pars = gauss_mod.guess(thisy, x=thisx)
               pars += linear_mod.make_params(intercept=thisy.min(), slope=0)
               mod = gauss_mod + linear_mod
               out = mod.fit(thisy, pars, x=thisx)
               comps = out.eval_components(x=thisx)
               dttong=int(sum(out.best_fit))
               dtphong=int(sum(comps['linear_']))
               dtthuc=int(dttong-dtphong)
               if dtthuc>3*dtphong:
                    if dtthuc+2*dtphong >0:
                         sigma=int(math.sqrt(dtthuc+2*dtphong))
                         self.data_a1line_local((x_local[peaks[i]]-0.05)*1000,(x_local[peaks[i]]+0.05)*1000)
                         if a1match_local==1:
                              self.ax2.vlines(thisx,ymin=0, ymax=thisy,color='r')
                              self.ax2.plot(x_local[peaks[i]], y_local[peaks[i]], "x",color='y')
          if a1_local==[]:
               self.tableWidget.clear()
               self.tableWidget.setRowCount(0)
          else:
               self.table_def()
               for i in range(len(b1_local)):
                    self.ax2.vlines(b1_local[i][5],ymin=0, ymax=b1_local[i][6],color='r')
                    self.ax2.plot(x_local[b1_local[i][7]], y_local[b1_local[i][7]], "x",color='y')
               self.ax2.set(facecolor='#FFFFCC',xlabel='E(keV)',ylabel='Counts')
               self.canvas.draw()
               for i in range(len(a1_local)):
                    self.tableWidget.setRowCount(i+2)
                    self.tableWidget.setItem(i+1, 0, itemSet(str(i+1)))
                    self.tableWidget.setItem(i+1, 1,itemSet(str(a1_local[i][0])))
                    self.tableWidget.setItem(i+1, 2,itemSet(str(a1_local[i][1])))
                    self.tableWidget.setItem(i+1, 3,itemSet(str(a1_local[i][2])))
                    self.tableWidget.setItem(i+1, 4,itemSet(str(a1_local[i][3])))
                    self.tableWidget.setItem(i+1, 5,itemSet(str(a1_local[i][4])))
                    self.tableWidget.setItem(i+1, 6,itemSet(str(a1_local[i][5])))
               if NGa!=0:
                    self.concentration()          
          self.sukien()
          
     def Analyze(self,):
          self.ax2.cla()
          peaks,_ = find_peaks(y[name],width=5,threshold=2)
          self.table_def()
          results_half = peak_widths(y[name],peaks, rel_height=0.5)
          left=results_half[2]*(max(x[name])-min(x[name]))/len(x[name])+1
          right=results_half[3]*(max(x[name])-min(x[name]))/len(x[name])+1
          gauss_mod = GaussianModel(prefix='gauss_')
          linear_mod = LinearModel(prefix='linear_')
          global b1,a1_data, b1_data,a1_local, b1_local, NGa ,AsKbNet, dtphong,dtthuc,sigma,thisx, thisy, dinh
          b1=[]
          b1_data=[]
          a1_data=[]
          b1_local=[]
          a1_local=[]
          NGa=0
          AsKbNet=0
          for i in range(len(peaks)):
               FWHM=round(right[i]-left[i],3)
               phi=(FWHM)*2.355
               xmin=x[name][peaks[i]]-phi/2
               xmax=x[name][peaks[i]]+phi/2
               indmin, indmax = np.searchsorted(x[name], (xmin, xmax))
               indmax = min(len(x[name]) - 1, indmax)
               thisx = x[name][indmin:indmax]
               thisy = y[name][indmin:indmax]
               pars = gauss_mod.guess(thisy, x=thisx)
               pars += linear_mod.make_params(intercept=thisy.min(), slope=0)
               mod = gauss_mod + linear_mod
               out = mod.fit(thisy, pars, x=thisx)
               comps = out.eval_components(x=thisx)
               dttong=int(sum(out.best_fit))
               dtphong=int(sum(comps['linear_']))
               dtthuc=int(dttong-dtphong)
               dinh=peaks[i]
               self.data_b1line((x[name][peaks[i]]-0.05)*1000,(x[name][peaks[i]]+0.05)*1000)
          for i in range(len(peaks)):
               FWHM=round(right[i]-left[i],3)
               phi=(FWHM)*2.355
               xmin=x[name][peaks[i]]-phi/2
               xmax=x[name][peaks[i]]+phi/2
               indmin, indmax = np.searchsorted(x[name], (xmin, xmax))
               indmax = min(len(x[name]) - 1, indmax)
               thisx = x[name][indmin:indmax]
               thisy = y[name][indmin:indmax]
               pars = gauss_mod.guess(thisy, x=thisx)
               pars += linear_mod.make_params(intercept=thisy.min(), slope=0)
               mod = gauss_mod + linear_mod
               out = mod.fit(thisy, pars, x=thisx)
               comps = out.eval_components(x=thisx)
               dttong=int(sum(out.best_fit))
               dtphong=int(sum(comps['linear_']))
               dtthuc=int(dttong-dtphong)
               if dtthuc>3*dtphong:
                    if dtthuc+2*dtphong >0:
                         sigma=int(math.sqrt(dtthuc+2*dtphong))
                         self.data_a1line((x[name][peaks[i]]-0.05)*1000,(x[name][peaks[i]]+0.05)*1000)
                         if a1match_data==1:
                              self.ax1.vlines(thisx,ymin=0, ymax=thisy,color='r')
                              self.ax1.plot(x[name][peaks[i]], y[name][peaks[i]], "x",color='y')
          for i in range(len(b1_data)):
               self.ax1.vlines(b1_data[i][5],ymin=0, ymax=b1_data[i][6],color='r')
               self.ax1.plot(x[name][b1_data[i][7]], y[name][b1_data[i][7]], "x",color='y')
          self.ax2.set(facecolor='#FFFFCC',xlabel='E(keV)',ylabel='Counts')
          self.canvas.draw()
          for i in range(len(a1_data)):
               self.tableWidget.setRowCount(i+2)
               self.tableWidget.setItem(i+1, 0, itemSet(str(i+1)))
               self.tableWidget.setItem(i+1, 1,itemSet(str(a1_data[i][0])))
               self.tableWidget.setItem(i+1, 2,itemSet(str(a1_data[i][1])))
               self.tableWidget.setItem(i+1, 3,itemSet(str(a1_data[i][2])))
               self.tableWidget.setItem(i+1, 4,itemSet(str(a1_data[i][3])))
               self.tableWidget.setItem(i+1, 5,itemSet(str(a1_data[i][4])))
               self.tableWidget.setItem(i+1, 6,itemSet(str(a1_data[i][5])))

     def create_connection(self,db_file):
          try:
               conn = sqlite3.connect(db_file)
               return conn
          except Error as e:
               print(e)
          return None

     def select_b1line(self, conn, E1, E2):
          global b1
          cur = conn.cursor()
          cur.execute("SELECT * FROM xray_transitions WHERE emission_energy>? AND emission_energy<?", (E1,E2,))
          rows = cur.fetchall()
          for row in rows:
               crit=r'b1'
               match=re.search(crit,row[3])            
               if match:  
                    pattern=r'[K,L]'
                    line=re.search(pattern,row[3])
                    if b1==[]:
                         b1=[[row[1],line.group(),row[6],dtthuc,dtphong,thisx,thisy,dinh]]
                    else:
                         b1=np.append(b1,[[row[1],line.group(),row[6],dtthuc,dtphong,thisx,thisy,dinh]],axis=0)
                         
     def data_b1line(self,E1,E2):
          database = "./XrayDB-master/xraydb.sqlite"
          conn = self.create_connection(database)
          with conn:
               self.select_b1line(conn,E1,E2)           
               
     def select_a1line(self, conn, E1, E2):
          global a1_data, a1match_data, b1_data
          a1match_data=0
          cur = conn.cursor()
          cur.execute("SELECT * FROM xray_transitions WHERE emission_energy>? AND emission_energy<?", (E1,E2,))
          rows = cur.fetchall()
          for row in rows:
               crit=r'a1'
               match=re.search(crit,row[3])            
               if match: 
                    pattern=r'[K,L]'
                    line=re.search(pattern,row[3])
                    for i in range(len(b1)):
                         if row[1]==b1[i][0] and line.group()==b1[i][1] and row[1]!='Ga':
                              a1match_data=1
                              if a1_data==[]:
                                   a1_data=[[row[1],row[3],round(row[6]/1000,3),dtthuc,dtphong,sigma]]
                              else:
                                   a1_data=np.append(a1_data,[[row[1],row[3],round(row[6]/1000,3),dtthuc,dtphong,sigma]],axis=0)
                              if b1_data==[]:
                                   b1_data=[b1[i]]
                              else:
                                   b1_data=np.append(b1_data,[b1[i]],axis=0)
                              self.ax1.plot([row[6]/1000, row[6]/1000],[0 ,max(y[name]/2)],color='b')
                              self.ax1.plot([float(b1[i][2])/1000, float(b1[i][2])/1000],[0 ,max(y[name]/2)],color='b')
                              self.ax1.text(row[6]/1000,max(y[name]/2),row[1]+b1[i][1]+"a",bbox={})
                              self.ax1.text(float(b1[i][2])/1000,max(y[name]/2),row[1]+b1[i][1]+"b",bbox={})
                    if row[1]=='Ga':
                         a1match_data=1
                         if a1_data==[]:
                              a1_data=[[row[1],row[3],round(row[6]/1000,3), dtthuc,dtphong,sigma]]
                         else:
                              a1_data=np.append(a1_data,[[row[1],row[3],round(row[6]/1000,3),dtthuc,dtphong,sigma]],axis=0)
                         self.ax1.plot([9250.6/1000, 9250.6/1000],[0 ,max(y[name]/2)],color='b')
                         self.ax1.plot([10267.0/1000, 10267.0/1000],[0 ,max(y[name]/2)],color='b')
                         self.ax1.text(9250.6/1000,max(y[name]/2),"GaKa",bbox={})
                         self.ax1.text(10267.0/1000,max(y[name]/2),"GaKb",bbox={})

     def select_a1line_local(self, conn, E1, E2):
          global a1_local, a1match_local, b1_local
          a1match_local=0
          cur = conn.cursor()
          cur.execute("SELECT * FROM xray_transitions WHERE emission_energy>? AND emission_energy<?", (E1,E2,))
          rows = cur.fetchall()
          for row in rows:
               crit=r'a1'
               match=re.search(crit,row[3])            
               if match: 
                    pattern=r'[K,L]'
                    line=re.search(pattern,row[3])
                    for i in range(len(b1)):
                         if row[1]==b1[i][0] and line.group()==b1[i][1] and row[1]!='Ga':
                              a1match_local=1
                              if  a1_local==[]:
                                   a1_local=[[row[1],row[3],round(row[6]/1000,3),dtthuc,dtphong,sigma]]
                              else:
                                   a1_local=np.append(a1_local,[[row[1],row[3],round(row[6]/1000,3),dtthuc,dtphong,sigma]],axis=0)
                              if  b1_local==[]:
                                   b1_local=[b1[i]]
                              else:
                                   b1_local=np.append(b1_local,[b1[i]],axis=0)
                              self.ax2.plot([row[6]/1000, row[6]/1000],[0 ,max(y_local/2)],color='b')
                              self.ax2.plot([float(b1[i][2])/1000, float(b1[i][2])/1000],[0 ,max(y_local/2)],color='b')
                              self.ax2.text(row[6]/1000,max(y_local/2),row[1]+b1[i][1]+"a",bbox={})
                              self.ax2.text(float(b1[i][2])/1000,max(y_local/2),row[1]+b1[i][1]+"b",bbox={})
                    if row[1]=='Ga':
                         a1match_local=1
                         if  a1_local==[]:
                              a1_local=[[row[1],row[3],round(row[6]/1000,3),dtthuc,dtphong,sigma]]
                         else:
                              a1_local=np.append(a1_local,[[row[1],row[3],round(row[6]/1000,3),dtthuc,dtphong,sigma]],axis=0)
                         self.ax2.plot([9250.6/1000, 9250.6/1000],[0 ,max(y_local/2)],color='b')
                         self.ax2.plot([10267.0/1000, 10267.0/1000],[0 ,max(y_local/2)],color='b')
                         self.ax2.text(9250.6/1000,max(y_local/2),"GaKa",bbox={})
                         self.ax2.text(10267.0/1000,max(y_local/2),"GaKb",bbox={})
                         
     def data_a1line(self,E1,E2):
          database = "./XrayDB-master/xraydb.sqlite"
          conn = self.create_connection(database)
          with conn:
               self.select_a1line(conn,E1,E2)          
               
     def data_a1line_local(self,E1,E2):
          database = "./XrayDB-master/xraydb.sqlite"
          conn = self.create_connection(database)
          with conn:
               self.select_a1line_local(conn,E1,E2)       

     def showDialog(self,):
          global kq,donvi
          kq, result =  QInputDialog.getDouble(self,'Input Dialog','Nhap nong do Ga:',0,0,999999999999,3) 
          dv=('g/l','mg/l','µg/l','ng/l')
          donvi, ok = QInputDialog.getItem(self,'Input Dialog','donvi',dv,0, False)
          if result == True and ok and donvi:
               self.concentration()
     
     def concentration(self,):
          global NGa
          if a1_data==[]:
               self.Analyze()
          Cis=kq
          Ga=r'Ga'
          for i in range(len(a1_data)):
               match=re.search(Ga,a1_data[i][0])
               if match:
                     NGa=float(a1_data[i][3])
                     dGa=float(a1_data[i][5])
          if NGa !=0 :
               self.tableWidget.setColumnCount(9)
               self.tableWidget.setItem(0, 7, itemSet('Conc./('+donvi+')'))
               self.tableWidget.setItem(0, 8, itemSet('SigmaC/('+donvi+')'))
               hsc=np.genfromtxt("C:\\Users\\MinhNo\\Desktop\\khoá luận\\hesochuan.txt",dtype='str')
               for i in range (len(a1_data)):
                    for j in range(len(hsc)):
                         if  a1_data[i][0]==hsc[j][1]:
                              nongdo=round((Cis*float(a1_data[i][3]))/(NGa*float(hsc[j][2])),3)
                              SigmaC=round((dGa/NGa+float(a1_data[i][5])/float(a1_data[i][3]))*nongdo,3)
                              self.tableWidget.setItem(i+1, 7,itemSet(str(nongdo)))
                              self.tableWidget.setItem(i+1, 8,itemSet(str(SigmaC)))
               if a1_local != []:
                    for i in range (len(a1_local)):
                         for j in range(len(hsc)):
                              if  a1_local[i][0]==hsc[j][1]:
                                   nongdo=round((Cis*float(a1_local[i][3]))/(NGa*float(hsc[j][2])),3)
                                   SigmaC=round((dGa/NGa+float(a1_local[i][5])/float(a1_local[i][3]))*nongdo,3)
                                   self.tableWidget.setItem(i+1, 7,itemSet(str(nongdo)))
                                   self.tableWidget.setItem(i+1, 8,itemSet(str(SigmaC)))
                                   
     def AsBrDialog(self,):
          global Dialog
          Dialog=QtWidgets.QDialog()
          ui=Ui_Dialog()
          ui.setupUi(Dialog)
          ui.YesClick.clicked.connect(self.AsBrPb)
          ui.NoClick.clicked.connect(self.AsPb)
          Dialog.show()
          Dialog.exec_()
          
     def AsBrPb(self,):
          Dialog.close()
          self.AsBr()
          self.AsPb()   
          
     def AsBr(self,):
          global a1_local, AsKbNet, a1_Br
          if a1_data==[]:
               self.Analyze()
          self.ax2.cla()
          xo=x[name][np.where((11.3<x[name])&(x[name]<12.4))]
          yo=y[name][np.where((11.3<x[name])&(x[name]<12.4))]
          lin_mod = LinearModel(prefix='lin_')
          EAsKb=11.72
          EBr=11.92
          gauss1 = GaussianModel(prefix='g1_')
          pars = gauss1.guess(yo, x=xo)
          pars.update(gauss1.make_params())
          pars['g1_center'].set(EAsKb, min=EAsKb-0.02, max=EAsKb+0.02)
          pars['g1_sigma'].set(0.1, min=0.05)
          pars['g1_amplitude'].set(300, min=10)
          gauss2 = GaussianModel(prefix='g2_')
          pars.update(gauss2.make_params())
          pars['g2_center'].set(EBr, min=EBr-0.02, max=EBr+0.02)
          pars['g2_sigma'].set(0.1, min=0.05)
          pars['g2_amplitude'].set(300, min=10)
          pars.update(lin_mod.make_params())
          pars['lin_intercept'].set(0.1)
          pars['lin_slope'].set(0.1)
          mod = gauss1 + gauss2  + lin_mod
          out = mod.fit(yo, pars, x=xo)
          plot_components = True
          self.ax2.plot(xo, yo, 'g')
          self.ax2.plot(xo, out.best_fit, 'r-')
          self.ax2.plot([EAsKb, EAsKb],[0 ,max(yo)*1.1],color='b')
          self.ax2.plot([EBr, EBr],[0 ,max(yo)*1.1],color='b')
          self.ax2.text(EAsKb,max(yo)*1.1,"AsKb",bbox={})
          self.ax2.text(EBr,max(yo)*1.1,"BrKa",bbox={})
          if plot_components:
              comps = out.eval_components(x=xo)
              self.ax2.plot(xo, comps['g1_'], 'm--')
              self.ax2.plot(xo, comps['g2_'], 'c--')
              self.ax2.plot(xo, comps['lin_'], 'k--')
              self.ax2.set(facecolor='#FFFFCC',xlabel='E(keV)',ylabel='Counts')
              self.canvas.draw()
#          dttong=int(sum(out.best_fit))
          dtbg=int(sum(comps['lin_']))
          AsKbNet=int(sum(comps['g1_']))
          BrKaNet=int(sum(comps['g2_']))
          sigmaBr=int(math.sqrt(BrKaNet+2*dtbg))
          a1_local=[['Br','Ka1',EBr,BrKaNet,dtbg, sigmaBr]]
          a1_Br=a1_local
          self.tableWidget.setRowCount(2)
          self.tableWidget.setItem(1, 0, itemSet(str(1)))
          self.tableWidget.setItem(1, 1,itemSet(str(a1_local[0][0])))
          self.tableWidget.setItem(1, 2,itemSet(str(a1_local[0][1])))
          self.tableWidget.setItem(1, 3,itemSet(str(a1_local[0][2])))
          self.tableWidget.setItem(1, 4,itemSet(str(a1_local[0][3])))
          self.tableWidget.setItem(1, 5,itemSet(str(a1_local[0][4])))
          self.tableWidget.setItem(1, 6,itemSet(str(a1_local[0][5])))
          if NGa != 0:
               self.concentration()
                    
     def AsPb(self,):
          global AsKbNet,a1_local,b1_local
          Dialog.close()
          self.onselect(9,13)
          As=r'As'
          Pb=r'Pb'
          EBr=11.92
          tlPb=1.40
          tlAs=8.3
          if AsKbNet!=0:
               a1_local=np.append(a1_local,a1_Br,axis=0)
               self.ax2.plot([EBr, EBr],[0 ,max(y_local/2)],color='b')
               self.ax2.text(EBr,max(y_local/2),"BrKa",bbox={})
          for i in range(len(b1_local)):
               if AsKbNet == 0:
                    match=re.search(As,b1_local[i][0])
                    if match:
                        AsKbNet = int(b1_local[i][3])  
               match=re.search(Pb,b1_local[i][0])
               if match:
                    PbLbNet = int(b1_local[i][3])
          for i in range(len(a1_local)):
               match=re.search(As,a1_local[i][0])
               if match:
                    AsPbNet=int(a1_local[i][3])
          AsKaNet=AsKbNet*tlAs
          PbLaNet=PbLbNet*tlPb
          tong= AsKaNet+PbLaNet
          NAs=AsKaNet*AsPbNet/tong
          NPb=PbLaNet*AsPbNet/tong
          for i in range(len(a1_local)):
               match=re.search(As,a1_local[i][0])
               if match:
                    a1_local[i,3]=int(NAs)
                    a1_local[i,5]=int(math.sqrt(NAs+2* int(a1_local[i,4])))
                    match=re.search(As,a1_local[i][0])
               match=re.search(Pb,a1_local[i][0])
               if match:
                    a1_local[i,3]=int(NPb)
                    a1_local[i,5]=int(math.sqrt(NPb+2* int(a1_local[i,4])))
          for i in range(len(a1_local)):
               self.tableWidget.setRowCount(i+2)
               self.tableWidget.setItem(i+1, 0, itemSet(str(i+1)))
               self.tableWidget.setItem(i+1, 1,itemSet(str(a1_local[i][0])))
               self.tableWidget.setItem(i+1, 2,itemSet(str(a1_local[i][1])))
               self.tableWidget.setItem(i+1, 3,itemSet(str(a1_local[i][2])))
               self.tableWidget.setItem(i+1, 4,itemSet(str(a1_local[i][3])))
               self.tableWidget.setItem(i+1, 5,itemSet(str(a1_local[i][4])))
               self.tableWidget.setItem(i+1, 6,itemSet(str(a1_local[i][5])))
          if NGa!=0:
               self.concentration()          

if __name__ == '__main__':     
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    fig=Figure()
    main.addmpl(fig)
    main.show()
    app.exec_()
