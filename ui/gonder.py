
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,QListWidgetItem, QApplication, QListView, QMessageBox,
                             QDesktopWidget, QSystemTrayIcon, QMenu, QAction,qApp, QTextEdit, QPushButton, QComboBox, QLabel)
from PyQt5.QtCore import Qt, QFileSystemWatcher, QSettings, QDateTime
from PyQt5.QtGui import QIcon
import os, yaml, sys, hashlib, shutil
from ui import listemadddesi, ayarlarui


class Gonderici(QDialog):
    
    MESAJ_DIZINI="./mesajlar/"
    def __init__(self,ebeveyn=None):
        super(Gonderici,self).__init__(ebeveyn)
        kutu = QVBoxLayout()
        self.ebeveyn = ebeveyn
        self.setLayout(kutu)
        kutu.setContentsMargins(5,5,5,5)

        self.mesaj_liste = QListWidget()
        self.mesaj_liste.setSelectionMode(QListView.ExtendedSelection)
        kutu.addWidget(self.mesaj_liste)

        self.tum_mesajlar_fonk()
        self.dosya_izleyici = QFileSystemWatcher()
        self.dosya_izleyici.addPath(self.MESAJ_DIZINI)
        self.dosya_izleyici.directoryChanged.connect(self.tum_mesajlar_fonk)

        kutu_h = QHBoxLayout()
        kutu_h.addWidget(QLabel("<b>Mesaj Tipi :</b>"))
        self.mesaj_tipi_text = QComboBox()
        self.mesaj_tipi_text.addItems(["------","bilgi","sistem","kritik",])
        kutu_h.addWidget(self.mesaj_tipi_text)
        kutu.addLayout(kutu_h)

        kutu_h = QHBoxLayout()
#        kutu_h.addWidget(QLabel("<b>Mesaj :</b>"))
        self.gonderilen_text = QTextEdit()
        self.gonderilen_text.setFixedHeight(100)
        kutu_h.addWidget(self.gonderilen_text)

        self.gonder_dugme = QPushButton("Gönder")
        self.gonder_dugme.setFixedHeight(100)
        self.gonder_dugme.clicked.connect(self.gonder_fonk)
        kutu_h.addWidget(self.gonder_dugme)
        kutu.addLayout(kutu_h)


    def gonder_fonk(self):
        tip = self.mesaj_tipi_text.currentText()
        mesaj = self.gonderilen_text.toPlainText()
        if tip == "------":
            QMessageBox.warning(self,"Uyarı","Lütfen bir mesaj tipi giriniz")
        elif mesaj == "":
            QMessageBox.warning(self,"Uyarı","Lütfen bir mesaj giriniz")
        else:
            gonderilecek = """mesaj_tipi : {}\nmesaj : {}\ntarih : {}""".format(tip,mesaj,QDateTime.currentDateTime().toString("yyyy-MM-dd_hh:mm:ss"))
            f = open("./gecici","w")
            f.write(gonderilecek)
            f.close()
            shutil.move("./gecici", self.MESAJ_DIZINI+self.dosyaHashle("./gecici"))
            QMessageBox.information(self,"Gönderildi","Mesajınız başarıyla gönderidi.")
            self.gonderilen_text.clear()
            self.tum_mesajlar_fonk()

    def ayarlar_fonk(self):
        ayarlar_pencere = ayarlarui.Ayarlar(self)
        ayarlar_pencere.show()

    def sistem_cekmecesi_tiklandi(self,value):
        if value == self.sistem_cekmecesi.DoubleClick:
            self.mesaj_oku_fonk()

    def mesaj_oku_fonk(self):
        self.sistem_cekmecesi.setIcon(QIcon("./icons/milis-bildirim.png"))
        self.show()

    def tum_mesajlar_fonk(self):
        self.mesaj_liste.clear()
        duzenli_mesajlar = self.ebeveyn.mesajlar_oku_sirala()
        mesajlar = duzenli_mesajlar.keys()
        sirali_mesajlar = list(mesajlar)
        sirali_mesajlar.sort()
        sirali_mesajlar = sirali_mesajlar[::-1]
        if len(sirali_mesajlar) != 0:
            for mesaj in sirali_mesajlar:
                mesaj_ = duzenli_mesajlar[mesaj]
                ozel_widget = listemadddesi.OzelListeMaddesi(self)
                ozel_widget.mesaj_id_ekle(mesaj_[2])
                ozel_widget.mesaj_tipi_ekle(mesaj_[0])
                ozel_widget.mesaj_ekle(mesaj_[1])
                ozel_widget.tarih_ekle(mesaj)
                ozel_widget.gonderen_ekle(mesaj_[3])
                ozel_widget.gonderen_onay_ekle(mesaj_[4])
                ozel_widget_item = QListWidgetItem(self.mesaj_liste)
                ozel_widget_item.setSizeHint(ozel_widget.sizeHint())
                self.mesaj_liste.setItemWidget(ozel_widget_item, ozel_widget)

    def dosyaHashle(self,dosya):
        BUF_SIZE = 65536  # 64k lik parca-chunklar ile 
        sha256 = hashlib.sha256()
        with open(dosya, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
        dosya_hash=sha256.hexdigest()
        return str(dosya_hash)
