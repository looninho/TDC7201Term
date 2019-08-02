# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 22:52:31 2018

@author: Loon
"""

import sys

from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox,
                             QLabel, QSpinBox, QLineEdit,
                             QPushButton, QGridLayout, QMessageBox,
                             QDesktopWidget)
from PyQt5.QtGui import QIcon

from PyQt5.QtSerialPort import QSerialPortInfo
import serialtransaction as st

import os, pickle, time, random


class Dialog(QWidget):  
    #codeFound = pyqtSignal()
    words=''
    lastwords=''
    canSend = False
    requestToSend=''
    m_waitTimeout=100
    m_attemp=0
    stockf021=b''
    
    def __init__(self):
        super().__init__()
        self.m_transaction = 0
        self.stop = True
        self.m_serialt = st.SerialTransaction()
        self.initUI()
        #self.longdelay = 0.8
        self.shortdelay=0.05
    
    def initUI(self):
        
        self.m_serialPortLabel = QLabel("Serial port:")
        self.m_serialPortComboBox = QComboBox()
        self.m_serialBaudsLabel = QLabel("Bauds:")
        self.m_serialBaudsComboBox = QComboBox()
        self.m_waitResponseLabel = QLabel("Wait response, msec:")
        self.m_waitResponseSpinBox = QSpinBox()
        self.m_longDelayLabel = QLabel("transaction delay, msec:")
        self.m_longDelaySpinBox = QSpinBox()
        
        self.m_runButton = QPushButton("Send request")
        self.m_requestLabel = QLabel("Request (hex without 0x):")
        self.m_requestLineEdit = QLineEdit("09")
        self.m_trafficLabel = QLabel("No traffic.")
        self.m_statusLabel = QLabel("Status: Not running.")
        
        available_ports = QSerialPortInfo.availablePorts()
        for port in available_ports:
            self.m_serialPortComboBox.addItem(port.portName())
        
        available_bauds = QSerialPortInfo.standardBaudRates()
        for bauds in available_bauds:
            self.m_serialBaudsComboBox.addItem(str(bauds))
        self.m_serialBaudsComboBox.itemText(9)

        self.m_waitResponseSpinBox.setRange(0,10000)
        self.m_waitResponseSpinBox.setValue(1500)
        
        self.m_longDelaySpinBox.setRange(0,10000)
        self.m_longDelaySpinBox.setValue(100)
        self.longdelay = 0.1
                       
        mainLayout = QGridLayout()
                
        mainLayout.addWidget(self.m_serialPortLabel,0,0)
        mainLayout.addWidget(self.m_serialPortComboBox,0,1)
        mainLayout.addWidget(self.m_serialBaudsLabel,0,2)
        mainLayout.addWidget(self.m_serialBaudsComboBox,0,3)
        
        mainLayout.addWidget(self.m_waitResponseLabel,1,0)
        mainLayout.addWidget(self.m_waitResponseSpinBox,1,1)
        
        mainLayout.addWidget(self.m_longDelayLabel,2,0)
        mainLayout.addWidget(self.m_longDelaySpinBox,2,1)
                
        #mainLayout.addWidget(self.m_stopButton,1,2,2,1)
        mainLayout.addWidget(self.m_requestLabel,3,0)
        mainLayout.addWidget(self.m_requestLineEdit,3,1)
        
        mainLayout.addWidget(self.m_runButton,4,1)
        
        mainLayout.addWidget(self.m_trafficLabel,5,0,1,4)
        
        mainLayout.addWidget(self.m_statusLabel,6,0,1,5)
        
        self.setLayout(mainLayout)
        
        self.setWindowTitle("TDC7201 Terminal")
        self.setWindowIcon(QIcon('pinion-icon.png'))
        self.m_serialPortComboBox.setFocus()
        
        #connection
        self.m_runButton.clicked.connect(self.transactionUI)
        self.m_serialt.responseSignal.connect(self.showResponse)
        self.m_serialt.errorSignal.connect(self.processError)
        self.m_serialt.timeoutSignal.connect(self.processTimeout)
        self.m_longDelaySpinBox.valueChanged.connect(self.updLongDelay)
        self.m_waitResponseSpinBox.valueChanged.connect(self.updwaitTimeout)
        
        self.center()
        
        self.show()
    
    def transaction(self):
        #self.setControlsEnabled(False)
        self.m_statusLabel.setText("Status: Running, connected to port {}.".format(self.m_serialPortComboBox.currentText()))
        response=self.m_serialt.transaction(self.m_serialPortComboBox.currentText(),\
                                  self.m_waitTimeout,\
                                  self.requestToSend)
        
         #wait_until(self.readyToSend,self.longdelay,self.shortdelay)
        return response
    
    def transactionUI(self):
        #self.setControlsEnabled(False)
        self.m_statusLabel.setText("Status: Running, connected to port {} with bauds {}.".format(self.m_serialPortComboBox.currentText(), self.m_serialBaudsComboBox.currentText()))
        #wait_until(self.readyToSend,self.longdelay,self.shortdelay)
        response = self.m_serialt.transaction(self.m_serialPortComboBox.currentText(),\
                                  int(self.m_serialBaudsComboBox.currentText()),\
                                  self.m_waitTimeout,\
                                  self.m_requestLineEdit.text())
        #wait_until(self.readyToSend,self.longdelay,self.shortdelay)
        self.m_waitTimeout = self.m_waitResponseSpinBox.value()
        return response
    
    def showResponse(self, ba):
        print("receive at {}".format(QTime.currentTime().toString()))
        #self.setControlsEnabled(True)
        self.m_transaction += 1
        self.m_trafficLabel.setText("response ({} bytes):{}".format(ba.size(),ba))
        #ok = False
        #print(ba.toInt(ok))
        #print(ba)
        #self.canSend=True
        return
    
    def readyToSend(self):
        return self.canSend
    
    def processError(self, s):
        self.setControlsEnabled(True)
        self.m_statusLabel.setText("Status: Not running, {}.".format(s))
        self.m_trafficLabel.setText("No traffic.")
        return
    
    def processTimeout(self, s):
        self.setControlsEnabled(True)
        self.m_statusLabel.setText("Status: Running, {}.".format(s))
        self.m_trafficLabel.setText("No traffic.")
        return
    
    def updLongDelay(self,val):
        #self.longdelay = self.m_longDelaySpinBox.value()/1000
        self.londelay = val/1000
        print("Long delay = {} s".format(self.londelay))
        return
    
    def updwaitTimeout(self,val):
        #self.longdelay = self.m_longDelaySpinBox.value()/1000
        self.m_waitTimeout = val
        print("Long delay = {} s".format(self.m_waitTimeout))
        return
    
    def setControlsEnabled(self, enable):
        self.m_runButton.setEnabled(enable)
        self.m_serialPortComboBox.setEnabled(enable)
        self.m_waitResponseSpinBox.setEnabled(enable)
        self.m_requestLineEdit.setEnabled(enable)
        return
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def closeEvent(self,event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes | 
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore() 

def wait_until(somepredicate, timeout, period=0.01, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if somepredicate(*args, **kwargs): return True
        time.sleep(period)
    return False

# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    w = Dialog()
    #w.show()
    
    sys.exit(app.exec_())
