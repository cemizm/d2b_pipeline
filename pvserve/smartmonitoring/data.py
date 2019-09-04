
import pandas as pd
import math
from scipy import interpolate

class PrepareData:

    def cut_curves(self, curves):
        return curves[curves['E eff'] > 500]

    def calculate_scala(self, count, xmax):
        y = [0]
        x = [0]
        summ = 0
        for i in range(count-1):
            x.append(i+1)
            tmp = 0.5/(1+math.exp((0.5*i-count/4)))+0.1
            summ = summ + tmp
            y.append(summ)
        scala = []
        for v in y:
            scala.append(v / summ * xmax)
        return scala

    def get_x_y_data(self, dataset, suffix=None):
        xdata = []
        ydata = []
        for i in range(1, 251):
            if (dataset["U" + str(i) + str(suffix)] is not None and dataset["I" + str(i) + str(suffix)] is not None and not math.isnan(dataset["U" + str(i) + str(suffix)]) and not math.isnan(dataset["I" + str(i) + str(suffix)])):
                if dataset["U" + str(i) + str(suffix)] not in xdata:
                    xdata.append(dataset["U" + str(i) + str(suffix)])
                    ydata.append(dataset["I" + str(i) + str(suffix)])
        return xdata, ydata

    def get_interpolated_data(self, data_set, count, smoothing=True):
        xdata, ydata = self.get_x_y_data(data_set)
        scala = self.calculate_scala(count, xdata[-1])
        tck = None
        if smoothing:
            tck = interpolate.splrep(xdata, ydata)
        else:
            self.check_data(xdata, ydata)
            tck = interpolate.splrep(xdata, ydata, s=0)
        ynew = interpolate.splev(scala, tck, der=0)
        return scala, ynew

    def get_interpolated_data_arrays(self, xdata, ydata, count, smoothing=True):
        scala = self.calculate_scala(count, xdata[-1])
        tck = None
        if smoothing:
            tck = interpolate.splrep(xdata, ydata)
        else:
            self.check_data(xdata, ydata)
            tck = interpolate.splrep(xdata, ydata, s=0)
        ynew = interpolate.splev(scala, tck, der=0)
        return scala, ynew

    def check_data(self, xdata, ydata):
        while(xdata[0] < 0):
            xdata.pop(0)
            ydata.pop(0)
        if (xdata[0] != 0):
            xdata.insert(0, 0)
            ydata.insert(0, 0)
        else:
            if (ydata != 0):
                ydata[0] = 0