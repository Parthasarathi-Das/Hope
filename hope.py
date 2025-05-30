import yfinance as yf
import numpy as np
import pandas as pd
from bokeh.models import DatetimeTickFormatter
from bokeh.plotting import figure, output_file, save
from keras.api import Sequential
from keras.api.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import datetime 

def ticker_validate(ticker):
    try:
        data = yf.Ticker(ticker)
        info = data.info
        print(info)
        return True
    except Exception as e:
        print(e)
        return False

def prepare_data(scaled_data, base_days):
    x_data = []
    y_data = []

    for i in range(base_days, len(scaled_data)):
        x_data.append(scaled_data[i-base_days: i])
        y_data.append(scaled_data[i])
        train_factor = 0.7 #Optimum
    x_train, x_test = x_data[:int(train_factor*len(x_data))], x_data[int(train_factor*len(x_data)):]
    y_train, y_test = y_data[:int(train_factor*len(y_data))], y_data[int(train_factor*len(y_data)):]
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)
    return x_train, x_test, y_train, y_test

def predict_stock(ticker_name, days):
    end = datetime.datetime.now()
    start = datetime.datetime.now() - datetime.timedelta(days=5*365)
    stockdf = yf.download(ticker_name, start, end)
    stockdf = stockdf[["Close"]]
    #Scaling the data
    scaler = MinMaxScaler()
    scaled_stockdf = scaler.fit_transform(stockdf)
    base_days = 100
    x_train, x_test, y_train, y_test = prepare_data(scaled_stockdf, base_days)

    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=(base_days, 1)),
        LSTM(64, return_sequences=False),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(x_train, y_train, batch_size= 5, epochs=10, validation_data=(x_test,y_test))

    last_100 = scaled_stockdf[-100:].reshape(1,-1,1)
    future_predictions = []

    for i in range(days):
        next_day_pred = model.predict(last_100)
        future_predictions.append(scaler.inverse_transform(next_day_pred))
        last_100 = np.append(last_100[:,1:,:], next_day_pred.reshape(1,1,-1), axis = 1)

    start_date = datetime.date.today()
    dates = [(start_date + datetime.timedelta(days=i)).strftime("%d-%m-%Y") for i in range(days)]

    p = figure(title=f"{ticker_name} Stock Prediction for {days} days",
            height=500, width=1000,
            x_axis_label="Date", y_axis_label="Close",
            toolbar_location=None, sizing_mode="scale_both",
            x_axis_type="datetime")
    
    datetime_dates = [datetime.datetime.strptime(date, "%d-%m-%Y") for date in dates]
    p.line(datetime_dates, future_predictions, line_width=2)
    p.xaxis[0].formatter = DatetimeTickFormatter(
        days="%d-%m-%Y",
        months="%d-%m-%Y",
        years="%d-%m-%Y"
    )
    output_file("templates\\plot.html")
    save(p)
    start_date = datetime.date.today()
    dates = [(start_date + datetime.timedelta(days=i)).strftime("%d %B, %Y") for i in range(days)]
    print("Dates  ",len(dates))
    values = [array[0][0] for array in future_predictions]
    print("Values  ",len(values))
    prediction_df = pd.DataFrame({
        'Date': dates,
        'Predicted Close Price': values
    })
    return prediction_df