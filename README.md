# Trading simulation Project 🚀

This is a trading simulation application that allows users to simulate simple trading logics using data from the [Alpha Vantage](https://www.alphavantage.co/). Whether you're testing your investment strategies or learning about market behavior, this tool provides a robust, interactive platform to explore the world of trading.

## Features ✨
- **Real-time Data Integration:** Pulls live market data from `Alpha Vantage API` to ensure your simulations are based on current market conditions.
- **Customizable Trading Strategies:** Allows users to implement and test various trading strategies with simple configuration.
- **User-Friendly Dashboard:** An intuitive web interface to monitor portfolio performance, view historical analysis, and analyze trading outcomes.
- **Simulated Transactions:** Execute virtual buy/sell orders to experience the dynamics of market trading without financial risk.
- **Secure Authentication:** User login and session management to safeguard your trading data and preferences.


## Tech Stack 🔧
- **Backend:** Python 🐍 (Flask Framework)
- **Frontend:** EJS, HTML, CSS, JavaScript 💻
- **Database:** SQLite 🗄️

## Installation ⚙️
- Make sure your computer have Python, pip and SQLite
```bash
git clone https://github.com/nhocmt227/Finance-website.git
cd Finance-website
pip install -r requirements.txt
```
- On MacOS or Linux: `./setup.sh`
- On PowerShell Window: `./setup.bat`

## Video demo: https://www.youtube.com/watch?v=M0qMXj7qQoY

## Usage 🚀
- Run the app `flask run`, you will see the app running in your `localhost` port `5000`
- Visit `http://localhost:5000` in your browser.

<img src=static/images/demo_images/homepage.png alt="Alt text for the image">
<img src=static/images/demo_images/history.png alt="Alt text for the image">

## Things to note
- The `API_KEY` inside the repo is public, limited and for testing only.
- If you want to use your own `API_KEY`, open the `.env` file and replace the value of `API_KEY` with your personal `API_KEY`.

Happy trading!
