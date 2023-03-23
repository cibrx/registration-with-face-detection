from PyQt5 import QtWidgets
import mysql.connector
from PyQt5.QtWidgets import QMessageBox   #Mesagebox için
import sys
import cv2
from kisiEkle import Ui_Ogrenci_Kayit
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import time
import tkinter as tk
from tkinter import messagebox

class KisiEkle(QtWidgets.QMainWindow):
    def __init__(self):
        super(KisiEkle,self).__init__()
        self.ui=Ui_Ogrenci_Kayit()
        self.ui.setupUi(self)
        self.ui.txtVeliTel.setText(" ")
        self.ui.txtVeliTel.setText(" ")
        self.ui.btnKaydet.setEnabled(False)    
        self.ui.txtAd.setClearButtonEnabled(True)
        self.ui.txtSoyad.setClearButtonEnabled(True)
        self.ui.txtOgrNo.setClearButtonEnabled(True)
        self.ui.btnFotoCek.clicked.connect(self.btn_aktiflik)  
        self.ui.btnFotoCek.clicked.connect(self.fotoAl) 
        self.ui.btnKameraAc.clicked.connect(self.kameraAc)
        self.ui.btnKaydet.clicked.connect(self.Kaydet)
        self.ui.btnTenmizle.clicked.connect(self.Temizle)
        self.ui.radio_Erkek.setChecked(True)
        self.mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="yoklamadb")
        self.cursor1=self.mydb.cursor()
        self.cursor1.execute("""select * from siniflar where sinifAdi""")
        siniflar=self.cursor1.fetchall()
        for sinif in siniflar:
            self.ui.comboSinif.addItem(sinif[1])
            self.mydb.close()  
        
    def kameraAc(self):
        self.thread1=thread1()
        self.thread1.start()
        self.thread1.ImageUpdate.connect(self.ImageUpdateSlot)

    def btn_aktiflik(self):
        self.ui.btnKaydet.setEnabled(True)
        
    def Temizle(self):
        self.ui.txtAd.setText("")
        self.ui.txtSoyad.setText("")
        self.ui.txtOgrNo.setText("")
        self.ui.txtVeliMail.setText("")
        self.ui.txtVeliTel.setText("")
        self.ui.comboSinif.setCurrentText("Secilmedi")
        
    def fotoAl(self):
        time.sleep(0.5)
        os.mkdir(str(self.ui.txtOgrNo.text()))
        mevcutfoto=0
        cekilecekfoto=self.ui.spinbox_fotosayisi.value()
        while mevcutfoto<cekilecekfoto:
            self.thread1.start() #frame degişkeninin thread classina giderek yenilenmesini saglar
            Image=self.thread1.frame
            faces = self.thread1.face_cascade.detectMultiScale(Image, 1.3, 6)
            print(1)
            if faces!=():    
                for (x,y,w,h) in faces:
                    newImage=Image[y:y+h, x:x+w]
                    cv2.imwrite(self.ui.txtOgrNo.text()+"/"+str(mevcutfoto)+".jpg",newImage)  
                    self.ui.fotoList.addItem(str(mevcutfoto)+".jpg")
                    mevcutfoto+=1
        print("kayit bitti")    
            
    def Mesaj(self,baslik,mesaj):
        root = tk.Tk()
        root.withdraw() # hide the main window

        messagebox.showinfo(baslik, mesaj)
    
    def KisiKontrol(self,OgrNo):
        self.mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="yoklamadb")
        self.cursor1=self.mydb.cursor()
        self.cursor1.execute("""select * from ogrenciler2 where okulNo='%s'"""%(OgrNo))
        sonuclar=list()
        sonuclar=self.cursor1.fetchall()
        flag1=""

        if len(sonuclar)<1:
            flag1="0"
            self.mydb.close()
        else:
            flag1="1"
            self.mydb.close()
        
        return flag1
        
    
    def Kaydet(self):
        if self.ui.radio_Erkek.isChecked()==True and self.ui.radio_Kiz.isChecked()==False:
            self.cinsiyet="Erkek"
        else:
            self.cinsiyet="Kız"  
                     
        sonuc=self.KisiKontrol(self.ui.txtOgrNo.text())
        if sonuc=="0":
            self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="yoklamadb")
            self.cursor1=self.mydb.cursor()
            self.Addinsert="""INSERT INTO ogrenciler2(OkulNo,ad,soyad,cinsiyet,sinif,veliTelefon,veliMail) VALUES ('%s','%s','%s','%s','%s','%s','%s')"""%(str(self.ui.txtOgrNo.text()), self.ui.txtAd.text(),self.ui.txtSoyad.text(),self.cinsiyet,self.ui.comboSinif.currentText(),str(self.ui.txtVeliTel.text()),str(self.ui.txtVeliMail.text()))
            self.cursor1.execute(self.Addinsert)
            self.mydb.commit()
            self.mydb.close()
            self.Mesaj("Kaydetme İşlemi",self.ui.txtOgrNo.text()+" nolu "+self.ui.txtAd.text()+" "+self.ui.txtSoyad.text()+" isimli öğrenci başarılı bir şekilde kaydedilmiştir.")
        elif sonuc=="1":
            self.Mesaj("Tekrarlı Kayıt",self.ui.txtOgrNo.text()+" nolu öğrenci zaten kayıtlı..")
        else:
            self.Mesaj("Hata Meydana Geldi","Beklenmeyen bir hata meydana geldi.")


    def ImageUpdateSlot(self,Image):
        self.ui.lbKamera.setPixmap(QPixmap.fromImage(Image))

class thread1(QThread,QtWidgets.QMainWindow):
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        while self.ThreadActive:
            ret,self.frame=Capture.read()
            if ret:
                Image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                faces = self.face_cascade.detectMultiScale(Image, 1.3, 5)

                for (x,y,w,h) in faces:
                    cv2.rectangle(Image,(x,y),(x+w,y+h),(255,0,0),2)
                    
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(340,360, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
                
    def stop(self):
        self.ThreadActive=False
        self.quit()        

def Uygulama2():
    uygulama=QtWidgets.QApplication(sys.argv)
    win=KisiEkle()
    win.show()
    sys.exit(uygulama.exec_())

Uygulama2()