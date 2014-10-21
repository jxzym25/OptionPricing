#Android Studio is a full-featured IDE
import sys
from PySide.QtGui import *
from PySide.QtCore import *
from bs4 import BeautifulSoup
import urllib2
import numpy as np
from scipy.stats import norm
from scipy.integrate import quad
import urllib
import os
import csv
import cmath as cm
import matplotlib
import scipy
from scipy.sparse.linalg import dsolve
from datetime import *

matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.axis = self.figure.add_subplot(111)

        self.layoutVertical = QVBoxLayout(self)
        self.layoutVertical.addWidget(self.canvas)

class GUI(QWidget):
    def __init__(self):
        super(GUI, self).__init__()      
        self.initUI()

    def initUI(self):
        self.errorMessageDialog = QErrorMessage(self)
        self.errorMessageDialog.setWindowTitle('ERROR')

        self.retrieving = False
        self.retrieved = False

        frameStyle = QFrame.Sunken | QFrame.Panel

        self.setToolTip('This is a tool for <b>Option Pricing</b>')

        #--------------------------------------
        #Define Different Input Widget and Grid

        groupBoxBackgroundInformation = QGroupBox('Background Information')
        groupBoxRetrievedData = QGroupBox('Retrieved Data')
        groupBoxInput = QGroupBox('Input Parameters')
        groupBoxOutput = QGroupBox('Output Results')

        gridBackgroundInformation = QGridLayout()
        gridRetrievedData = QGridLayout()
        gridInput = QGridLayout()
        gridOutput = QGridLayout()

        groupBoxBackgroundInformation.setLayout(gridBackgroundInformation)
        groupBoxRetrievedData.setLayout(gridRetrievedData)
        groupBoxInput.setLayout(gridInput)
        groupBoxOutput.setLayout(gridOutput)

        #Define Different Widget For Different Models
        widgetInput_BlackScholes = QWidget()
        widgetInput_Heston = QWidget()
        widgetInput_Merton = QWidget()
        widgetInput_TrendFollowing = QWidget()
        gridInput_BlackScholes = QGridLayout()
        gridInput_Heston = QGridLayout()
        gridInput_Merton = QGridLayout()
        gridInput_TrendFollowing = QGridLayout()
        widgetInput_BlackScholes.setLayout(gridInput_BlackScholes)
        widgetInput_Heston.setLayout(gridInput_Heston)
        widgetInput_Merton.setLayout(gridInput_Merton)
        widgetInput_TrendFollowing.setLayout(gridInput_TrendFollowing)


        stackedInput = QStackedWidget()
        stackedInput.addWidget(widgetInput_BlackScholes)
        stackedInput.addWidget(widgetInput_Heston)
        stackedInput.addWidget(widgetInput_Merton)
        stackedInput.addWidget(widgetInput_TrendFollowing)
        stackedInput.setStyleSheet("QStackedWidget { border: 2px gray; margin: 0px; }")


        #--------------------------------
        #Initialize all the labels and input boxes
 
        #Initialize Data Retrieved Part
        tickerLabel = QLabel(self)
        tickerLabel.setText('A Valid Tiker')
        self.tickerInput = QLineEdit(self)

        self.retrieveButton = QPushButton('Retrieve', self)
        self.retrieveButton.setToolTip('Retrieve data from <b>Yahoo Finance</b>')
        self.retrieveButton.resize(self.retrieveButton.sizeHint())
        self.retrieveButton.pressed.connect(self.retrieve)

        stockPriceLabel = QLabel(self)
        stockPriceLabel.setText('Current Stock Price')
        self.stockPriceOutput = QLabel(self)
        self.stockPriceOutput.setFrameStyle(frameStyle)

        dividendRateLabel = QLabel(self)
        dividendRateLabel.setText('Current Dividend Rate')
        self.dividendRateOutput = QLabel(self)
        self.dividendRateOutput.setFrameStyle(frameStyle)

        historicalVolatilityLabel = QLabel(self)
        historicalVolatilityLabel.setText('Historical Volatility (Yearly)')
        self.historicalVolatilityOutput = QLabel(self)
        self.historicalVolatilityOutput.setFrameStyle(frameStyle)

        interestRateLabel = QLabel(self)
        interestRateLabel.setText('Interest Rate')
        self.interestRateOutput = QLabel(self)
        self.interestRateOutput.setFrameStyle(frameStyle)
        self.interestRate = getInterestRate()
        self.interestRateOutput.setText(str(self.interestRate*100)+"%")

        self.matplotlibWidget = MatplotlibWidget(self)
        self.matplotlibWidget.canvas.draw()

        #Initialize Input Parameters Part

        modelLabel = QLabel(self)
        modelLabel.setText('Option Pricing Model')
        self.model = QComboBox(self)
        self.model.addItem('Black Scholes')
        self.model.addItem('Heston')
        self.model.addItem('Merton Jump-Diffusion')
        self.model.addItem('Optimal Trend Following')
        self.model.activated.connect(lambda: stackedInput.setCurrentIndex(self.model.currentIndex()))

        ##WE HAVE DIFFERENT MODELS
        ##1. Input for Black Scholes Model
        strikePriceLabel_BlackScholes = QLabel(self)
        strikePriceLabel_BlackScholes.setText('Strike Price')
        self.strikePriceInput_BlackScholes = QLineEdit(self)

        timeToMaturityLabel_BlackScholes = QLabel(self)
        timeToMaturityLabel_BlackScholes.setText('Time To Maturity')
        self.timeToMaturityInput_BlackScholes = QLineEdit(self)

        volatilityLabel_BlackScholes = QLabel(self)
        volatilityLabel_BlackScholes.setText('Volatility')
        self.volatilityInput_BlackScholes = QLineEdit(self)

        ##2. Input for Heston Model
        strikePriceLabel_Heston = QLabel(self)
        strikePriceLabel_Heston.setText('Strike Price')
        self.strikePriceInput_Heston = QLineEdit(self)

        timeToMaturityLabel_Heston = QLabel(self)
        timeToMaturityLabel_Heston.setText('Time To Maturity')
        self.timeToMaturityInput_Heston = QLineEdit(self)

        meanInversionLabel_Heston = QLabel(self)
        meanInversionLabel_Heston.setText('Mean Inversion')
        self.meanInversionInput_Heston = QLineEdit(self)

        longRunVarianceLabel_Heston = QLabel(self)
        longRunVarianceLabel_Heston.setText('Long-run Variance')
        self.longRunVarianceInput_Heston = QLineEdit(self)

        currentVarianceLabel_Heston = QLabel(self)
        currentVarianceLabel_Heston.setText('Current Variance')
        self.currentVarianceInput_Heston = QLineEdit(self)

        correlationLabel_Heston = QLabel(self)
        correlationLabel_Heston.setText('Correlation of Z1(t) and Z2(t)')
        self.correlationInput_Heston = QLineEdit(self)

        volatilityOfVolatilityLabel_Heston = QLabel(self)
        volatilityOfVolatilityLabel_Heston.setText('Volatility Of Volatility')
        self.volatilityOfVolatilityInput_Heston = QLineEdit(self)

        ##3. Input for Merton Jump-Diffusion Model
        strikePriceLabel_Merton = QLabel(self)
        strikePriceLabel_Merton.setText('Strike Price')
        self.strikePriceInput_Merton = QLineEdit(self)

        timeToMaturityLabel_Merton = QLabel(self)
        timeToMaturityLabel_Merton.setText('Time To Maturity')
        self.timeToMaturityInput_Merton = QLineEdit(self)

        volatilityLabel_Merton = QLabel(self)
        volatilityLabel_Merton.setText('Volatility')
        self.volatilityInput_Merton = QLineEdit(self)

        expectedNumberOfJumpsLabel_Merton = QLabel(self)
        expectedNumberOfJumpsLabel_Merton.setText('Expeceted Number Of Jumps (Per Year)')
        self.expectedNumberOfJumpsInput_Merton = QLineEdit(self)

        proportionOfTotalVolatilityLabel_Merton = QLabel(self)
        proportionOfTotalVolatilityLabel_Merton.setText('Proportion Of Total Volatility')
        self.proportionOfTotalVolatilityInput_Merton = QLineEdit(self)

        ##4. Input for Optimal Trend Following Model
        expectedLengthOfBullMarketLabel_TrendFollowing = QLabel(self)
        expectedLengthOfBullMarketLabel_TrendFollowing.setText('Expected Length Of Bull Market')
        #expectedLengthOfBullMarketLabel_TrendFollowing.setToolTip('Switching Intensity From Bull to Bear')
        self.expectedLengthOfBullMarketInput_TrendFollowing = QLineEdit(self)

        expectedLengthOfBearMarketLabel_TrendFollowing = QLabel(self)
        expectedLengthOfBearMarketLabel_TrendFollowing.setText('Expected Length Of Bear Market')
        #expectedLengthOfBearMarketLabel_TrendFollowing.setToolTip('Switching Intensity From Bear to Bear')
        self.expectedLengthOfBearMarketInput_TrendFollowing = QLineEdit(self)

        expectedReturnRateBullLabel_TrendFollowing = QLabel(self)
        expectedReturnRateBullLabel_TrendFollowing.setText('Expected Return Rate in Bull Market')
        expectedReturnRateBullLabel_TrendFollowing.setToolTip('Positive!')
        self.expectedReturnRateBullInput_TrendFollowing = QLineEdit(self)

        expectedReturnRateBearLabel_TrendFollowing = QLabel(self)
        expectedReturnRateBearLabel_TrendFollowing.setText('Expected Return Rate in Bear Market')
        expectedReturnRateBearLabel_TrendFollowing.setToolTip('Negative!')
        self.expectedReturnRateBearInput_TrendFollowing = QLineEdit(self)
        
        volatilityLabel_TrendFollowing = QLabel(self)
        volatilityLabel_TrendFollowing.setText('Volatility')
        self.volatilityInput_TrendFollowing = QLineEdit(self)

        ratioOfSlippageBuyLabel_TrendFollowing = QLabel(self)
        ratioOfSlippageBuyLabel_TrendFollowing.setText('Ratio of Slippage per Transaction with Buy Order')
        ratioOfSlippageBuyLabel_TrendFollowing.setToolTip('[0, 1]')
        self.ratioOfSlippageBuyInput_TrendFollowing = QLineEdit(self)

        ratioOfSlippageSellLabel_TrendFollowing = QLabel(self)
        ratioOfSlippageSellLabel_TrendFollowing.setText('Ratio of Slippage per Transaction with Sell Order')
        ratioOfSlippageSellLabel_TrendFollowing.setToolTip('[0, 1]')
        self.ratioOfSlippageSellInput_TrendFollowing = QLineEdit(self)

        interestedTimeIntervalLabel = QLabel(self)
        interestedTimeIntervalLabel.setText('Interested Time Interval (years)')
        self.interestedTimeIntervalInput_TrendFollowing = QLineEdit(self)
        ##Other

        computeButton = QPushButton('Compute', self)
        computeButton.setToolTip('Compute Option Price')
        computeButton.resize(computeButton.sizeHint())
        computeButton.clicked.connect(self.compute)

        resetDefaultButton = QPushButton('Reset to Defaults', self)
        resetDefaultButton.setToolTip('Reset to Default Values')
        resetDefaultButton.resize(resetDefaultButton.sizeHint())
        resetDefaultButton.clicked.connect(self.setDefault)

        #Initialize Output Results Part

        callOptionPriceLabel = QLabel(self)
        callOptionPriceLabel.setText('Call Option Price')
        self.callOptionPriceOutput = QLabel(self)
        self.callOptionPriceOutput.setFrameStyle(frameStyle)

        putOptionPriceLabel = QLabel(self)
        putOptionPriceLabel.setText('Put Option Price')
        self.putOptionPriceOutput = QLabel(self)
        self.putOptionPriceOutput.setFrameStyle(frameStyle)


        #----------------------
        #Widget setup

        #Set Column Width
        gridBackgroundInformation.setColumnStretch(0, 250)
        gridBackgroundInformation.setColumnStretch(1, 250)
        gridRetrievedData.setColumnStretch(0, 250)
        gridRetrievedData.setColumnStretch(1, 250)
        gridInput.setColumnStretch(0, 250)
        gridInput.setColumnStretch(1, 250)
        gridOutput.setColumnStretch(0, 250)
        gridOutput.setColumnStretch(1, 250)
        gridInput_BlackScholes.setColumnStretch(0, 250)
        gridInput_BlackScholes.setColumnStretch(1, 250)
        gridInput_Heston.setColumnStretch(0, 250)
        gridInput_Heston.setColumnStretch(1, 250)
        gridInput_Merton.setColumnStretch(0, 250)
        gridInput_Merton.setColumnStretch(1, 250)
        gridInput_TrendFollowing.setColumnStretch(0, 250)
        gridInput_TrendFollowing.setColumnStretch(1, 250)


        #Background Information
        gridBackgroundInformation.addWidget(interestRateLabel, 0, 0)
        gridBackgroundInformation.addWidget(self.interestRateOutput, 0, 1)

        gridBackgroundInformation.addWidget(tickerLabel, 1, 0)
        gridBackgroundInformation.addWidget(self.tickerInput, 1, 1)

        gridBackgroundInformation.addWidget(self.retrieveButton, 2, 1)

        #Retrieved Data
        gridRetrievedData.addWidget(stockPriceLabel, 0, 0)
        gridRetrievedData.addWidget(self.stockPriceOutput, 0, 1)

        gridRetrievedData.addWidget(dividendRateLabel, 1, 0)
        gridRetrievedData.addWidget(self.dividendRateOutput, 1, 1)

        gridRetrievedData.addWidget(historicalVolatilityLabel, 2, 0)
        gridRetrievedData.addWidget(self.historicalVolatilityOutput, 2, 1)

        #Input Result

        #1. Black Scholes Model
        gridInput_BlackScholes.addWidget(strikePriceLabel_BlackScholes, 0, 0)
        gridInput_BlackScholes.addWidget(self.strikePriceInput_BlackScholes, 0, 1)

        gridInput_BlackScholes.addWidget(timeToMaturityLabel_BlackScholes, 1, 0)
        gridInput_BlackScholes.addWidget(self.timeToMaturityInput_BlackScholes, 1, 1)

        gridInput_BlackScholes.addWidget(volatilityLabel_BlackScholes, 2, 0)
        gridInput_BlackScholes.addWidget(self.volatilityInput_BlackScholes, 2, 1)

        #2. Heston Model
        gridInput_Heston.addWidget(strikePriceLabel_Heston, 0, 0)
        gridInput_Heston.addWidget(self.strikePriceInput_Heston, 0, 1)

        gridInput_Heston.addWidget(timeToMaturityLabel_Heston, 1, 0)
        gridInput_Heston.addWidget(self.timeToMaturityInput_Heston, 1, 1)

        gridInput_Heston.addWidget(meanInversionLabel_Heston, 2, 0)
        gridInput_Heston.addWidget(self.meanInversionInput_Heston, 2, 1)

        gridInput_Heston.addWidget(longRunVarianceLabel_Heston, 3, 0)
        gridInput_Heston.addWidget(self.longRunVarianceInput_Heston, 3, 1)

        gridInput_Heston.addWidget(currentVarianceLabel_Heston, 4, 0)
        gridInput_Heston.addWidget(self.currentVarianceInput_Heston, 4, 1)

        gridInput_Heston.addWidget(correlationLabel_Heston, 5, 0)
        gridInput_Heston.addWidget(self.correlationInput_Heston, 5, 1)

        gridInput_Heston.addWidget(volatilityOfVolatilityLabel_Heston, 6, 0)
        gridInput_Heston.addWidget(self.volatilityOfVolatilityInput_Heston, 6, 1)

        #3. Merton Jump-Diffusion Model
        gridInput_Merton.addWidget(strikePriceLabel_Merton, 0, 0)
        gridInput_Merton.addWidget(self.strikePriceInput_Merton, 0, 1)

        gridInput_Merton.addWidget(timeToMaturityLabel_Merton, 1, 0)
        gridInput_Merton.addWidget(self.timeToMaturityInput_Merton, 1, 1)

        gridInput_Merton.addWidget(volatilityLabel_Merton, 2, 0)
        gridInput_Merton.addWidget(self.volatilityInput_Merton, 2, 1)

        gridInput_Merton.addWidget(expectedNumberOfJumpsLabel_Merton, 3, 0)
        gridInput_Merton.addWidget(self.expectedNumberOfJumpsInput_Merton, 3, 1)

        gridInput_Merton.addWidget(proportionOfTotalVolatilityLabel_Merton, 4, 0)
        gridInput_Merton.addWidget(self.proportionOfTotalVolatilityInput_Merton, 4, 1)

        #4. Optimal Trend Following Model
        gridInput_TrendFollowing.addWidget(expectedLengthOfBullMarketLabel_TrendFollowing, 0, 0)
        gridInput_TrendFollowing.addWidget(self.expectedLengthOfBullMarketInput_TrendFollowing, 0, 1)

        gridInput_TrendFollowing.addWidget(expectedLengthOfBearMarketLabel_TrendFollowing, 1, 0)
        gridInput_TrendFollowing.addWidget(self.expectedLengthOfBearMarketInput_TrendFollowing, 1, 1)
        
        gridInput_TrendFollowing.addWidget(expectedReturnRateBullLabel_TrendFollowing, 2, 0)
        gridInput_TrendFollowing.addWidget(self.expectedReturnRateBullInput_TrendFollowing, 2, 1)

        gridInput_TrendFollowing.addWidget(expectedReturnRateBearLabel_TrendFollowing, 3, 0)
        gridInput_TrendFollowing.addWidget(self.expectedReturnRateBearInput_TrendFollowing, 3, 1)

        gridInput_TrendFollowing.addWidget(volatilityLabel_TrendFollowing, 4, 0)
        gridInput_TrendFollowing.addWidget(self.volatilityInput_TrendFollowing, 4, 1)

        gridInput_TrendFollowing.addWidget(ratioOfSlippageBuyLabel_TrendFollowing, 5, 0)
        gridInput_TrendFollowing.addWidget(self.ratioOfSlippageBuyInput_TrendFollowing, 5, 1)

        gridInput_TrendFollowing.addWidget(ratioOfSlippageSellLabel_TrendFollowing, 6, 0)
        gridInput_TrendFollowing.addWidget(self.ratioOfSlippageSellInput_TrendFollowing, 6, 1)

        gridInput_TrendFollowing.addWidget(interestedTimeIntervalLabel, 7, 0)
        gridInput_TrendFollowing.addWidget(self.interestedTimeIntervalInput_TrendFollowing, 7, 1)

        #Final combination
        gridInput.addWidget(modelLabel, 0, 0)
        gridInput.addWidget(self.model, 0, 1)

        gridInput.addWidget(stackedInput, 1, 0, 1, 2)
        gridInput.addWidget(resetDefaultButton, 2, 0)
        gridInput.addWidget(computeButton, 2, 1)

        #Output Result
        gridOutput.addWidget(callOptionPriceLabel, 0, 0)
        gridOutput.addWidget(self.callOptionPriceOutput, 0, 1)

        gridOutput.addWidget(putOptionPriceLabel, 1, 0)
        gridOutput.addWidget(self.putOptionPriceOutput, 1, 1)

        leftVBox = QVBoxLayout()
        rightVBox = QVBoxLayout()
        leftVBox.addWidget(groupBoxBackgroundInformation)
        leftVBox.addWidget(groupBoxRetrievedData)
        leftVBox.addWidget(self.matplotlibWidget)
        leftVBox.addStretch(1)
        rightVBox.addWidget(groupBoxInput)
        rightVBox.addWidget(groupBoxOutput)
        rightVBox.addStretch(1)

        mainHBox = QHBoxLayout()
        mainHBox.addLayout(leftVBox)
        mainHBox.addLayout(rightVBox)
        mainHBox.setStretch(0,500)
        mainHBox.setStretch(1,500)
        self.setLayout(mainHBox)

        self.setGeometry(300, 300, 1000, 450)
        self.setWindowTitle('Option Pricing')
        self.show()

    def setDefault(self):
        if (self.retrieved):
            #1. Black Scholes
            self.strikePriceInput_BlackScholes.setText(str(self.stockPrice))
            self.timeToMaturityInput_BlackScholes.setText('1.00')
            self.volatilityInput_BlackScholes.setText(str(self.historicalVolatility))

            #2. Heston
            self.strikePriceInput_Heston.setText(str(self.stockPrice))
            self.timeToMaturityInput_Heston.setText('1.00')
            self.meanInversionInput_Heston.setText('0.02')
            self.longRunVarianceInput_Heston.setText('1.00')
            self.currentVarianceInput_Heston.setText(str(self.historicalVolatility))
            self.correlationInput_Heston.setText('0.00')
            self.volatilityOfVolatilityInput_Heston.setText('1.00')

            #3. Merton Jump Diffusion
            self.strikePriceInput_Merton.setText(str(self.stockPrice))
            self.timeToMaturityInput_Merton.setText('1.00')
            self.volatilityInput_Merton.setText(str(self.historicalVolatility))
            self.expectedNumberOfJumpsInput_Merton.setText('1')
            self.proportionOfTotalVolatilityInput_Merton.setText('0.00')

            #4. Optimal Trend Following
            self.expectedLengthOfBullMarketInput_TrendFollowing.setText(str(1.0/0.36))
            self.expectedLengthOfBearMarketInput_TrendFollowing.setText(str(1.0/2.53))
            self.expectedReturnRateBullInput_TrendFollowing.setText('0.18')
            self.expectedReturnRateBearInput_TrendFollowing.setText('-0.77')
            self.ratioOfSlippageBuyInput_TrendFollowing.setText('0.001')
            self.ratioOfSlippageSellInput_TrendFollowing.setText('0.001')
            self.volatilityInput_TrendFollowing.setText(str(self.historicalVolatility))
            self.interestedTimeIntervalInput_TrendFollowing.setText('10')

        else:
            self.errorMessageDialog.showMessage('<b>Please Retrieve Data First!!!</b>')

    def retrieve(self):
        if (self.retrieving == False):
            self.retrieving = True
            ticker = self.tickerInput.text()
            if (ticker != ''):
                url = "https://finance.yahoo.com/q?s="+ticker
                [self.stockPrice, self.dividendRate] = getStockPrice(url)
                if (self.stockPrice > -1e-6):
                    self.stockPriceOutput.setText(str(self.stockPrice))
                    self.dividendRateOutput.setText(str(self.dividendRate*100)+"%")

                    url = "http://www.google.com/finance/historical?q=" + ticker + "&output=csv"
                    url = generateURL(ticker, 20)
                    [self.historicalPrice, self.timeStamp] = getHistoricalPrice(url)

                    historicalReturn = []
                    for i in range(len(self.historicalPrice) - 1):
                        historicalReturn.append(np.log(self.historicalPrice[i+1]/self.historicalPrice[i]))
                    #print len(self.historicalPrice)

                    #Change volatility from daily to yearly
                    self.historicalVolatility = np.std(historicalReturn) * np.sqrt(250)

                    self.historicalVolatilityOutput.setText(str(self.historicalVolatility))
                else:
                    self.errorMessageDialog.showMessage('<b>Invalid ticker!!!</b>')
            else:
                self.errorMessageDialog.showMessage('<b>Invalid ticker!!!</b>')
            self.retrieving = False
            self.retrieved = True
            self.matplotlibWidget.axis.cla()
            list_of_dates = [datetime.strptime(x, "%Y-%m-%d") for x in self.timeStamp]
            self.dates = matplotlib.dates.date2num(list_of_dates)
            self.matplotlibWidget.axis.plot_date(self.dates, self.historicalPrice, '-')
            self.matplotlibWidget.canvas.draw()

        self.setDefault()

    def compute(self):
        if (self.retrieved):
            currentModel = self.model.currentText()
            if (currentModel == 'Black Scholes'):
                strikePrice = float(self.strikePriceInput_BlackScholes.text())
                timeToMaturity = float(self.timeToMaturityInput_BlackScholes.text())
                volatility = float(self.volatilityInput_BlackScholes.text())
                [callOptionPrice, putOptionPrice] = BlackScholes(self.stockPrice, strikePrice,
                        timeToMaturity, volatility, self.interestRate, self.dividendRate)
            elif currentModel == 'Heston':
                strikePrice = float(self.strikePriceInput_Heston.text())
                timeToMaturity = float(self.timeToMaturityInput_Heston.text())
                meanInversion = float(self.meanInversionInput_Heston.text())
                longRunVariance = float(self.longRunVarianceInput_Heston.text())
                currentVariance = float(self.currentVarianceInput_Heston.text())
                correlation = float(self.correlationInput_Heston.text())
                volatilityOfVolatility = float(self.volatilityOfVolatilityInput_Heston.text())

                [callOptionPrice, putOptionPrice] = HestonQuad_q(meanInversion, longRunVariance,
                        volatilityOfVolatility, correlation, currentVariance, self.interestRate,
                        timeToMaturity, self.stockPrice, strikePrice, self.dividendRate)
            elif currentModel == 'Merton Jump-Diffusion':
                strikePrice = float(self.strikePriceInput_Merton.text())
                timeToMaturity = float(self.timeToMaturityInput_Merton.text())
                volatility = float(self.volatilityInput_Merton.text())
                expectedNumberOfJumps = int(self.expectedNumberOfJumpsInput_Merton.text())
                proportionOfTotalVolatility = float(self.proportionOfTotalVolatilityInput_Merton.text())

                if expectedNumberOfJumps > 0:
                    [callOptionPrice, putOptionPrice] = MertonJumpDiffusion(self.stockPrice, strikePrice,
                            timeToMaturity, volatility, self.interestRate, self.dividendRate,
                            expectedNumberOfJumps, proportionOfTotalVolatility)
                else:
                    self.errorMessageDialog.showMessage('<b>Please Enter a Positive Expected Number Of Jumps</b>')

            elif currentModel == 'Optimal Trend Following':
                volatility = float(self.volatilityInput_TrendFollowing.text())
                expectedLengthOfBullMarket = float(self.expectedLengthOfBullMarketInput_TrendFollowing.text())
                expectedLengthOfBearMarket = float(self.expectedLengthOfBearMarketInput_TrendFollowing.text())
                switchingIntensityFromBullToBear = 1.0/expectedLengthOfBullMarket
                switchingIntensityFromBearToBull = 1.0/expectedLengthOfBearMarket
                expectedReturnRateBull = float(self.expectedReturnRateBullInput_TrendFollowing.text())
                expectedReturnRateBear = float(self.expectedReturnRateBearInput_TrendFollowing.text())
                ratioOfSlippageBuy = float(self.ratioOfSlippageBuyInput_TrendFollowing.text())
                ratioOfSlippageSell = float(self.ratioOfSlippageSellInput_TrendFollowing.text())
                interestedTimeInterval = int(self.interestedTimeIntervalInput_TrendFollowing.text())

                if ratioOfSlippageBuy > 1 or ratioOfSlippageBuy < 0:
                    self.errorMessageDialog.showMessage('<b>Please Enter a Valid Slippage Ratio with a Buy Order</b>')
                elif ratioOfSlippageSell > 1 or ratioOfSlippageSell < 0:
                    self.errorMessageDialog.showMessage('<b>Please Enter a Valid Slippage Ratio with a Sell Order</b>')
                elif expectedReturnRateBull < 0:
                    self.errorMessageDialog.showMessage('<b>Please Enter a Positive Expected Return Rate in Bull Market</b>')
                elif expectedReturnRateBear > 0:
                    self.errorMessageDialog.showMessage('<b>Please Enter a Negative Expected Return Rate in Bear Market</b>')
                else:
                    ticker = self.tickerInput.text()
                    url = generateURL(ticker, interestedTimeInterval)
                    historicalPrice, timeStamp = getHistoricalPrice(url)
                    # print url
                    # print len(historicalPrice)
                    list_of_dates = [datetime.strptime(x, "%Y-%m-%d") for x in timeStamp]
                    dates = matplotlib.dates.date2num(list_of_dates)

                    #def OptimalTrendFollowing(mu1, mu2, rho, Kb, Ks, sigma, lamda1, lamda2, s, timeStamp, T):
                    [buylist, selllist, valueOfPortfolio] = OptimalTrendFollowing(expectedReturnRateBull, expectedReturnRateBear, 
                            self.interestRate, ratioOfSlippageBuy, ratioOfSlippageSell, volatility, switchingIntensityFromBullToBear,
                            switchingIntensityFromBearToBull, historicalPrice, timeStamp)
                    buytime = [dates[i] for i in buylist]
                    selltime = [dates[i] for i in selllist]
                    #print buytime
                    #print selltime
                    buyprice = [historicalPrice[i] for i in buylist]
                    sellprice = [historicalPrice[i] for i in selllist]

                    fig = plt.figure(figsize=(20, 20))
                    ax = fig.add_subplot(111)
                    maxPrice = max(historicalPrice)
                    seg = maxPrice/15.0
                    ax.plot_date(dates, historicalPrice,'-',color = 'c',label = "Historical Price")
                    ax.plot_date(dates, valueOfPortfolio, '-', color ='m',label = "Portfolio Value")
                    ax.vlines(buytime, buyprice, [x+seg for x in buyprice] , color = 'r', linestyles = 'dashed', label = 'Buy')
                    ax.vlines(selltime, [x-seg for x in sellprice], sellprice, color = 'g', linestyles = 'dashed', label = 'Sell')
                    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m-%d"))
                    plt.legend(bbox_to_anchor=(0.85, 0.95), loc=2, borderaxespad=0.)
                    plt.show()

                    callOptionPrice = "N/A"
                    putOptionPrice = "N/A"

            self.callOptionPriceOutput.setText(str(callOptionPrice))
            self.putOptionPriceOutput.setText(str(putOptionPrice))
        else:
            self.errorMessageDialog.showMessage('<b>Please Retrieve Data First!!!</b>')

def generateURL(ticker, T):
        TD = date.today()
        return "http://real-chart.finance.yahoo.com/table.csv?s=" + ticker + "&a=" + str(TD.month-1) + "&b=" + str(TD.day) + "&c=" + str(TD.year-T) + "&d=" + str(TD.month-1) + "&e=" + str(TD.day) + "&f=" + str(TD.year) + "&ignore=.csv"

def getStockPrice(url):
    response = urllib2.urlopen(url)
    if (response.geturl()!=url):
        return [-1,-1]
    content = response.read()
    soup = BeautifulSoup(content).find("span", {"class" : "time_rtq_ticker"})
    stockPrice = float(soup.string.replace(",",""))
    soup = BeautifulSoup(content).find_all("tr", {"class" : "end"})
    dividendRate = 0.0

    if (len(soup) == 1):
        soup = soup[0]
        dividendRateString = soup.td.string
        if (dividendRateString != "N/A (N/A) "):
            temp = dividendRateString.split(" ")
            temp = temp[1].split("(")
            temp = temp[1].split("%")
            dividendRate = float(temp[0])/100

    return [stockPrice, dividendRate]

def getHistoricalPrice(url):
    urllib.urlretrieve (url, "data.csv")
    csvfile = file('data.csv','rb')
    reader = csv.reader(csvfile)

    counter = 0
    closePrice = []
    timeStamp = []
    for line in reader:
        counter = counter + 1
        if (counter > 1):
            closePrice.append(float(line[4]))
            timeStamp.append(line[0])
    closePrice = closePrice[::-1]
    timeStamp = timeStamp[::-1]
    csvfile.close()
    os.remove("data.csv")
    return [closePrice, timeStamp]

def getInterestRate():
    url = "https://ycharts.com/indicators/10_year_treasury_rate"
    response = urllib2.urlopen(url)
    content = response.read()
    soup = BeautifulSoup(content).find("div", {"id" : "pgNameVal"})
    temp = soup.string.split("%")
    return float(temp[0])/100

def BlackScholes(S, X, T, sigma, r, q):
    d1 = (np.log(S/X)+(r-q+0.5*sigma*sigma)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)

    call = S*np.exp(-q*T)*norm.cdf(d1)-X*np.exp(-r*T)*norm.cdf(d2)
    put = X*np.exp(-r*T)*norm.cdf(-d2)-S*np.exp(-q*T)*norm.cdf(-d1)
    return [call, put]

def HestonQuad_q(kappa,theta,sigma,rho,v0,r,T,s0,K,q):
    if T==0:
      call = max(s0-K,0)
    else:
        call = s0*np.exp(-q*T)*HestonP(kappa,theta,sigma,rho,v0,r,T,s0,K,1,q) - K*np.exp(-r*T)*HestonP(kappa,theta,sigma,rho,v0,r,T,s0,K,2,q)
    put = call - s0*np.exp(-q*T) + K*np.exp(-r*T)
    return [call, put]

def HestonP(kappa, theta, sigma, rho, v0, r, T, s0, K, Type, q):
    r = r-q
    ans, err = quad(HestonPIntegrand,0,100,args=(kappa,theta,sigma,rho,v0,r,T,s0,K,Type,q))
    return 0.5 + 1/np.pi*ans

def HestonPIntegrand(phi, kappa ,theta, sigma, rho, v0, r, T, s0, K, Type, q):
    r = r-q
    result = cm.exp(-1j*phi*cm.log(K)).real*Hestf(phi,kappa,theta,sigma,rho,v0,r,T,s0,Type,q)/(1j*phi)
    return result.real

def Hestf(phi, kappa, theta, sigma, rho, v0, r, T, s0, Type, q):
    r = r-q
    if (Type == 1):
        u = 0.5
        b = kappa - rho*sigma
    else:
        u = -0.5
        b = kappa

    a = kappa*theta
    x = cm.log(s0)
    d = cm.sqrt((rho*sigma*phi*1j-b)**2-sigma**2*(2*u*phi*1j-phi**2))
    g = (b-rho*sigma*phi*1j + d)/(b-rho*sigma*phi*1j - d)
    C = r*phi*1j*T + a/sigma**2*((b- rho*sigma*phi*1j + d)*T - 2*cm.log((1-g*cm.exp(d*T))/(1-g)))
    D = (b-rho*sigma*phi*1j + d)/sigma**2*((1-cm.exp(d*T))/(1-g*cm.exp(d*T)))
    return cm.exp(C + D*v0 + 1j*phi*x)

def MertonJumpDiffusion(S, X, T, sigma, r, q, lamda, gamma):
    factor = 1.0
    power = 1.0
    call = 0.0
    put = 0.0
    for i in range(0, 100):
        coefficient = power/factor*np.exp(-lamda*T)
        #print coefficient

        delta2 = gamma * sigma**2 / lamda
        sigma_i = np.sqrt(sigma**2 - lamda*delta2 + delta2*(i/T))

        [europeanCall, europeanPut] = BlackScholes(S, X, T, sigma_i, r, q)
        call = call + coefficient * europeanCall
        put = put + coefficient * europeanPut
        factor = factor * (i+1)
        power = power * lamda * T

    return [call, put]

def OptimalTrendFollowing(mu1, mu2, rho, Kb, Ks, sigma, lambda1, lambda2, s, timeStamp):
    [pb, ps] = solveHJB(mu1, mu2, sigma, lambda1, lambda2, Kb, Ks, rho, 2)
    # print "pb=", pb
    # print "ps=", ps
    p0 = (ps+pb)/2
    #p0 = (rho-mu2+sigma**2/2)/(mu1-mu2)
    N = len(s)
    p = np.zeros(N)
    p[0] = p0
    hs = np.zeros(N)
    hs[0] = int(1)
    nbuy = 0
    nsell = 0

    #Assume we are holding one stock at t=0
    M = 0.0
    bstock = 1.0/(1+Kb)
    dt = 1.0/250        # a different dt from the one in solveHJB
    for j in range(1,N):
        f = -(lambda1+lambda2)*p[j-1]+lambda2-(mu1-mu2)*p[j-1]*(1-p[j-1])*((mu1-mu2)*p[j-1]+mu2-sigma**2/2)/(sigma**2)
        p[j]= min(max(p[j-1]+f*dt+(mu1-mu2)*p[j-1]*(1-p[j-1])*np.log(s[j]/s[j-1])/(sigma**2),0),1)
    #print p
    buytime = []
    selltime = []

    # print s

    # hs = 1 -> Holding Stock
    # hs = 0 -> Holding Cash

    buylist = []
    selllist = []
    valueOfPortfolio = []
    valueOfPortfolio.append(M)
    for j in range(1,N):
        # print hs[j-1]
        # print bstock
        if hs[j-1] == 0:
            M = M*np.exp(rho*dt)
        if hs[j-1] == 1 and p[j]<=ps:
            nsell = nsell+1
            M = s[j]*(1-Ks)*bstock
            # print "Sell: " + str(M)
            # print "     Today: " + str(s[j])
            # print "     Yesterday: " + str(s[j-1])
            bstock = 0
            hs[j] = 0
            selltime.append(timeStamp[j])
            selllist.append(j)
        elif hs[j-1] == 0 and p[j]>=pb:
            nbuy = nbuy+1
            bstock = M*1.0/s[j]/(1+Kb)
            M = 0
            # print "Buy: " + str(bstock)
            hs[j] = 1
            buytime.append(timeStamp[j])
            buylist.append(j)
        else:
            hs[j] = hs[j-1]
            # print "Keep: " + str(M + bstock*s[j])

        valueOfPortfolio.append(M + bstock*s[j])

    # print valueOfPortfolio
    # print hs
    # print buytime
    # print selltime
    if hs[N-1] is 1:
        nsell = nsell+1
        M = s[N-1]*(1-Ks)*bstock
        hs[N-1] = 0

    ntrade = nbuy + nsell
    return [buylist, selllist, valueOfPortfolio]

def solveHJB(mu1, mu2, sigma, lambda1, lambda2, Kb, Ks, rho, T):
    Ny = 1000
    Nt = 200

    beta = 1e7
    tol = 1e-8

    psell = []
    pbuy = []

    h = 1.0/Ny
    dt = T*1.0/Nt
    y = np.array([h*i for i in range(Ny+1)])
    v = np.array([np.log(1-Ks) for i in range(Ny+1)])
    vnew = [1 for i in range(Ny+1)]

    c2 = 0.5*np.array([((mu1-mu2)*x*(1-x)/sigma)**2 for x in y])/h/h
    c1 = (-(lambda1+lambda2)*y+lambda2)/h
    c0 = 0
    f0= (mu1-mu2)*y+(mu2-rho-sigma**2/2)
    left = -c2+c1*(c1<0)
    middle = 1/dt+2*c2+np.abs(c1)-c0;
    right = -c2-c1*(c1>0)

    for t in range(int(T/dt)):
        counter = 0
        vn = v

        while True:
            counter = counter+1

            Indi1 = beta*(v-(np.log(1+Kb))>0);
            Indi2 = beta*((np.log(1-Ks))-v>0);
            b = vn/dt+(np.log(1+Kb))*Indi1+(np.log(1-Ks))*Indi2+f0;
            A = scipy.sparse.spdiags(np.array([right, middle+Indi1+Indi2, left]),[-1,0,1],Ny+1,Ny+1).T
            b[0] = A[0,0]*np.log(1-Ks)
            A[0,1] = 0
            b[Ny] = A[Ny,Ny]*np.log(1+Kb)
            A[Ny,Ny-1]=0
            vnew = dsolve.spsolve(A,b,use_umfpack=False)
            if (np.linalg.norm(vnew-v)*1.0/np.linalg.norm(v))<tol:
                break
            v = vnew

        uu = vnew
        temp = np.where(uu-(np.log(1+Kb))>=0)[0]
        pbuy.append(y[temp[0]])
        temp = np.where(uu-(np.log(1-Ks))<=0)[0]
        psell.append(y[temp[len(temp)-1]])

    return [pbuy[Nt-1], psell[Nt-1]]

def main():
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()