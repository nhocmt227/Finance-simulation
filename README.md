# Trading simulation Project 

This is a trading simulation application that allows users to simulate simple trading logics using data from the [Alpha Vantage](https://www.alphavantage.co/). Whether you're testing your investment strategies or learning about market behavior, this tool provides a robust, interactive platform to explore the world of trading.

## Features 
- **Real-time Data Integration:** Pulls live market data from `Alpha Vantage API` to ensure your simulations are based on current market conditions.
- **Customizable Trading Strategies:** Allows users to implement and test various trading strategies with simple configuration.
- **User-Friendly Dashboard:** An intuitive web interface to monitor portfolio performance, view historical analysis, and analyze trading outcomes.
- **Simulated Transactions:** Execute virtual buy/sell orders to experience the dynamics of market trading without financial risk.
- **Secure Authentication:** User login and session management to safeguard your trading data and preferences.


## Tech Stack 
- **Backend:** Python 🐍 (Flask Framework)
- **Frontend:** EJS, HTML, CSS, JavaScript
- **Database:** SQLite
- **Build tools:** Python Doit

## Installation 
- Make sure your computer have Python, pip and SQLite
```bash
git clone https://github.com/nhocmt227/Finance-website.git
cd Finance-website
pip install -r requirements.txt
```
- On MacOS or Linux: `./setup/setup.sh`
- On PowerShell Window: `./setup/setup.bat`
- Run `dodo install`

## APIs
- [Alpha Vantage](https://www.alphavantage.co/)

## Usage
The usage commands can be seen on the `dodo.py` file.
- `doit start`: Start the application.
- `doit install`: Install the dependencies and run the app initialization.
- `doit test`: Run the unit tests locally.
- `doit cleanup`: Clean up the temporary files.
- `doit format`: Format the codebase.
- `doit lint`: Lint the codebase

<img src=frontend/static/images/demo_images/homepage.png alt="Alt text for the image">
<img src=frontend/static/images/demo_images/history.png alt="Alt text for the image">

## Things to note
- The `API_KEY` inside the repo is public, limited and for testing only.
- If you want to use your own `API_KEY`, open the `.env` file and replace the value of `API_KEY` with your personal `API_KEY`.

Happy trading!
