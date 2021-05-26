import image_mixer
from PyQt5 import QtWidgets , QtCore, QtGui
import matplotlib.image as mpimg
import sys
from numpy.fft import fft2, ifft2 , fftshift
import numpy as np
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QImage
import matplotlib.pyplot as plt
import logging
# from skimage import color
# from skimage import io


# Create and configure logger
logging.basicConfig(level=logging.DEBUG, filename="app.log", format='%(lineno)s - %(levelname)s - %(message)s', filemode='w')

logger = logging.getLogger()

class Image():
    def __init__(self , img_array):
        self.img_array = img_array   
        self.img_shape =  self.img_array.shape
        # print(self.img)
        # print(type(self.img))
        self.ft_img = fft2(self.img_array)
        self.shifted_fft = fftshift(self.ft_img)

        self.mag = np.abs(self.ft_img)
        self.mag_comp = 20 * np.log(np.abs(self.shifted_fft)) 

        self.phase = np.angle(self.ft_img)
        self.phase_comp = np.angle(self.shifted_fft)

        self.real = np.real(self.ft_img)
        self.real_comp = np.real(self.shifted_fft)
        self.real_comp[self.real_comp <= 0] = 10 ** -10
        self.real_comp = 20 *np.log(self.real_comp)

        self.imag = np.imag(self.ft_img)
        self.imag_comp = np.imag(self.shifted_fft)
        self.imag_comp[self.imag_comp <= 0] = 10 ** -10
        self.imag_comp = 20 *np.log(self.imag_comp)

        self.unimag = np.ones(self.mag.shape)
        self.uniphase = np.zeros(self.phase.shape)

        self.display_comp = [self.mag_comp ,self.phase_comp ,self.real_comp ,self.imag_comp ]
        # self.components = { "mag" : self.mag ,"phase" : self.phase ,"real" : self.real ,"imag": self.imag ,"unimag": self.unimag,"uniphase": self.uniphase }
        self.components =[self.mag ,self.phase ,self.real , self.imag , self.unimag, self.uniphase ]
        
        

class MainWindow(QtWidgets.QMainWindow , image_mixer.Ui_MainWindow):
    # resized = QtCore.pyqtSignal()
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        logger.info("the application has started")
        self.img = 2 * [0]
        self.combobox =  [self.comboBox , self.comboBox_2]
        self.widgets = [self.img1_view , self.img2_view,self.img1_comp, self.img2_comp ,self.output1 , self.output2]
        self.ratio = [0,0]
        self.sliders = [self.horizontalSlider, self.horizontalSlider_2]  
        self.combobox_output = [self.comboBox_3, self.comboBox_4, self.comboBox_5, self.comboBox_6, self.comboBox_7]
        self.comboBox_7.setCurrentIndex(1)
        
        for i in range(2):  
            self.mixing_sliders(i)  
        for i in range(5):
            self.mixing_combobox(i)
        
        for i in range(2):
            self.combobox_action(i)
        self.pushButton.clicked.connect(self.reset)
        # self.radio_buttons = [self.radio_img1 , self.radio_img2]
        # self.current_img = 0
        self.actionOpen.triggered.connect(self.open_image)
        self.widget_configuration()
        self.default()



    def combobox_action(self , i):
        self.combobox[i].activated.connect(lambda:self.comp_img(i))

    
        
    def widget_configuration(self):

        for widget in self.widgets:
            widget.ui.histogram.hide()
            widget.ui.roiBtn.hide()
            widget.ui.menuBtn.hide()
            widget.ui.roiPlot.hide()
            widget.getView().setAspectLocked(False)
            widget.view.setAspectLocked(False)

    def open_image(self):
        self.file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File',"", "Image Files (*.png *jpeg *.jpg)")
        self.img_array = plt.imread(self.file_path)
        R, G, B = self.img_array[:,:,0], self.img_array[:,:,1], self.img_array[:,:,2]
        self.img_array = (0.2989 * R + 0.5870 * G + 0.1140 * B).T
        # self.img_array = io.imread(self.file_path)
        # self.img_array = color.rgb2gray(self.img_array).T
        if self.img[0] == 0 :
            i = 0
            self.combobox[0].setEnabled(True)
            self.pushButton.setEnabled(True)
            self.img[0] = Image(self.img_array)
        elif self.img[1] == 0:
            i = 1
            self.img[1] = Image(self.img_array)
            if ( (np.size(self.img[0].img_array) !=  np.size(self.img[1].img_array))) :
                self.pop_up()
                self.img[i] = 0
                self.img_array = 0
                logger.warning("The image size is not suitable")
            else:
                self.en_dis_able(True)
                self.mixing()
                logger.info("tools are enabled")
        
        
        try:        
            # self.pixmap[i] = self.convert2pixelmap(self.img_array)
            # self.label[i].setPixmap(self.pixmap[i])
            self.comp_img(i)
            self.display(self.img_array , self.widgets[i] , self.img[0].img_shape)
            
        except:
            return None
    def display(self , data , widget , img_shape):
        widget.setImage(data)
        widget.view.setLimits(xMin=0, xMax=img_shape[0], yMin= 0 , yMax= img_shape[1])
        widget.view.setRange(xRange=[0, img_shape[0]], yRange=[0, img_shape[1]], padding=0)
        

    def en_dis_able(self , x):
        self.comboBox_2.setEnabled(x)
        self.comboBox_3.setEnabled(x)
        self.comboBox_4.setEnabled(x)
        self.comboBox_5.setEnabled(x)
        self.comboBox_6.setEnabled(x)
        self.comboBox_7.setEnabled(x)
        self.horizontalSlider.setEnabled(x)
        self.horizontalSlider_2.setEnabled(x)
        self.pushButton.setEnabled(x)
    def reset(self):
        for i in range(6):
            self.widgets[i].clear()
        self.en_dis_able(False)
        for i in range(2):
            self.combobox[i].setEnabled(False)
            self.img[i] = 0
        self.widget_configuration()
        self.default()
        logger.info("the application has been reseted")

    def comp_img(self , i):
        if self.img[i] != 0:
            self.display(self.img[i].display_comp[self.combobox[i].currentIndex()] , self.widgets[i + 2] , self.img[0].img_shape)


    def pop_up(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText('Warning!')
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setInformativeText('Image sizes must be the same, please upload another image')
        x = msg.exec_()

        
       
    
    # connecting the Sliders
    
    
    def mixing_sliders(self, i):
        self.sliders[i].valueChanged.connect(lambda: self.mixing())
    def mixing_combobox(self , i):
        self.combobox_output[i].activated.connect(lambda: self.mixing())

    
    def mixing(self):
        if self.comboBox_5.currentText() == 'Mag' :
            self.available_items([False,True,False,False,False,True])
        elif self.comboBox_5.currentText() == 'Phase' :
            self.available_items([True,False,False,False,True,False])
        elif self.comboBox_5.currentText() == 'Real' :
            self.available_items([False,False,False,True,False,False])
        elif self.comboBox_5.currentText() == 'Imag' :
            self.available_items([False,False,True,False,False,False])
        elif self.comboBox_5.currentText() == 'uniMag' :
            self.available_items([False,True,False,False,False,True])
        elif self.comboBox_5.currentText() == 'uniPhase' :
            self.available_items([True,False,False,False,True,False])

        self.image1 = self.img[self.comboBox_4.currentIndex()]
        self.image2 = self.img[self.comboBox_6.currentIndex()]

        
        self.label_10.setText(str(self.sliders[0].value()) + "%")
        self.label_11.setText(str(self.sliders[1].value()) + "%")
        for i in range(2):
            self.ratio[i] = (self.sliders[i].value()/100)
   
            # Constructing complex number (real + imaginary)
        condition1 = (self.comboBox_5.currentText() == self.comboBox_7.currentText())
        condition2 = (self.comboBox_5.currentText() in ['Phase' , 'uniPhase'] and self.comboBox_7.currentText() in ['Phase' , 'uniPhase']) or (self.comboBox_5.currentText() in ['Mag' , 'uniMag'] and self.comboBox_7.currentText() in ['Mag' , 'uniMag'])
        condition3 = (self.comboBox_5.currentText() in ['Real' ,'Imag' ] and self.comboBox_7.currentText() in ['Phase' ,'Mag','uniPhase','uniMag' ])
        condition4 = (self.comboBox_7.currentText() in ['Real' ,'Imag' ] and self.comboBox_5.currentText() in ['Phase' ,'Mag','uniPhase','uniMag' ])
        if  condition1 or condition3 or condition2 or condition4:
            pass
        else:
            comp1 = np.add(self.image1.components[self.comboBox_5.currentIndex()] * self.ratio[0] , self.image2.components[self.comboBox_5.currentIndex()] * (1 - self.ratio[0]))
            logger.info(f"comp1 is {self.comboBox_5.currentText()}")
            comp2 = np.add(self.image2.components[self.comboBox_7.currentIndex()] * self.ratio[1] , self.image1.components[self.comboBox_7.currentIndex()] * (1 - self.ratio[1]))
            logger.info(f"comp1 is {self.comboBox_7.currentText()}")


            if self.comboBox_5.currentText() == "Real":
                #new_imag = (1j*new_imag)
                complex_number = np.add(comp1, comp2 * 1j)
                logger.info("components are added")
            elif self.comboBox_5.currentText() == "Imag":
                #new_imag = (1j*new_imag)
                complex_number = np.add(comp1 * 1j, comp2)
                logger.info("components are added")
                
            # Constructing complex number (Magnitude + phase)
            elif self.comboBox_5.currentText() in ["Mag" ,"uniMag"] :
                #new_phase = np.exp(1j * new_phase)
                complex_number = np.multiply(comp1, np.exp(1j * comp2))
                logger.info("components are multiplied")

            elif self.comboBox_5.currentText() in ["Phase" ,"uniPhase"] :
                #new_phase = np.exp(1j * new_phase)
                complex_number = np.multiply(comp2, np.exp(1j * comp1))
                logger.info("components are multiplied")
                
            
            
            try:
                output = np.real(ifft2(complex_number))
                self.display(output , self.widgets[4 + self.comboBox_3.currentIndex()] , self.img[0].img_shape)
            except:
                return None

    def available_items(self, boolian_list):
        for i in range(len(boolian_list)):
            self.comboBox_7.model().item(i).setEnabled(boolian_list[i])
    def default(self):
        default_image = plt.imread("default/default-image.jpg")
        R, G, B = default_image[:,:,0], default_image[:,:,1], default_image[:,:,2]
        default_image = (0.2989 * R + 0.5870 * G + 0.1140 * B).T
        for i in range(6):
            self.display(default_image , self.widgets[i] , default_image.shape)




def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()