# Trading simulation Project

This is a trading simulation application that allows users to simulate simple trading logics using data from public APIs. Whether you're testing your investment strategies or learning about market behavior, this tool provides a robust, interactive platform to explore the world of trading.

[Finance Simulation Web](https://finance-simulation.onrender.com)

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
- **Build tools:** Python Doit, Docker
- **Deployment:** Render

## Running locally 
- Make sure your computer have Python, SQLite and Docker Desktop
- Docker Desktop installation: [Docker Desktop](https://apps.microsoft.com/detail/XP8CBJ40XLBWKX?hl=en-SG&gl=SG&ocid=pdpshare)
```bash
git clone https://github.com/nhocmt227/Finance-website.git
cd Finance-website
docker build -t stock-simulation-web .
docker run -p 9000:9000 stock-simulation-web
```
- You will see this on the terminal, click into this link to go to the web page:
```
Running on http://127.0.0.1:9000
```

## APIs
For development stage, we only use free tier API, so the API rates may be limited.
- [Alpha Vantage](https://www.alphavantage.co/): 25 calls/day
- [Twelve Data](https://twelvedata.com/account): 800 credits/day
- [Finnhub](https://finnhub.io/): 60 API calls/minute

## For developer:
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
