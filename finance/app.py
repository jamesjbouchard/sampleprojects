# Credit for help: Stack Exchange, DDB, (Flask, Python, HTML, Jinja online documentation)

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    folio = db.execute(
        """
        SELECT symbol,
               SUM(value) as total_value,
               SUM(quantity) as total_shares,
               printf("$%.2f", SUM(value)) as formatted_total_value
        FROM userdata
        WHERE id = :id
        GROUP BY symbol
    """,
        id=session["user_id"],
    )

    cash_str = db.execute(
        "SELECT printf('$%.2f', cash) as formatted_cash FROM users WHERE id = :id",
        id=session["user_id"],
    )[0]["formatted_cash"]

    # Remove the dollar sign and convert cash to a float
    cash = float(cash_str.replace("$", ""))

    # Calculate the total value of holdings
    total_holdings = sum(row["total_value"] for row in folio)

    # Format the total value of holdings
    formatted_total_holdings = "${:.2f}".format(total_holdings)

    # Calculate the combined balance by adding cash and total_holdings
    formatted_total_balance = "${:.2f}".format(total_holdings + cash)

    return render_template(
        "index.html",
        folio=folio,
        formatcash=cash_str,
        formatted_total_holdings=formatted_total_holdings,
        formatted_total_balance=formatted_total_balance,
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()

        # Check if the symbol is empty
        if not symbol:
            return apology("You must enter a ticker")

        quote = lookup(symbol)

        # Check if the quote is None (symbol not found)
        if quote is None:
            return apology("This ticker doesn't exist in our database")

        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("Shares must be a number")

        if not shares:
            return apology("Must enter a number of shares")

        cash = db.execute(
            "SELECT cash FROM users WHERE id = :id", id=session["user_id"]
        )[0]["cash"]
        value = shares * quote["price"]

        if shares < 0:
            return apology("Enter a valid number of shares to buy")
        elif quote["price"] * shares > cash:
            return apology("You don't have enough liquidity")
        else:
            db.execute(
                "INSERT INTO userdata (id, symbol, quantity, value, buysell, date) VALUES (:id, :symbol, :quantity, :value, 'buy', datetime('now'))",
                id=session["user_id"],
                symbol=symbol,
                quantity=shares,
                value=value,
            )
            db.execute(
                "UPDATE users SET cash = cash - :cost WHERE id = :id",
                cost=value,
                id=session["user_id"],
            )
            flash("The buy was successful")
            return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute(
        """
        SELECT trx_id, symbol, quantity,
               printf("$%.2f", value) as formatted_value,
               buysell, date
        FROM userdata
        WHERE id = :id
    """,
        id=session["user_id"],
    )
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)

        if not quote:
            return apology("This ticker does not exist in our database")
        return render_template("quoted.html", quote=quote)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Check if the request method is POST
    if request.method == "POST":
        # Check to see if both fields are entered correctly else return apology
        if not request.form.get("username"):
            return apology("Must provide a username", 400)
        elif not request.form.get("password"):
            return apology("Must provide a password", 400)
        elif not request.form.get("confirmation"):
            return apology("Must enter password twice to verify", 400)

        # Check to see if the passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match, please try again", 400)

        # Check if the user is already in the database
        check = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(check) != 0:
            return apology("Username already in use, pick another")

        # Insert the new user into the database
        db.execute(
            "INSERT INTO users(username, hash) VALUES(?,?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )

        # Check if username was added
        check = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # log the user in
        session["user_id"] = check[0]["id"]

        # redirect to the portfolio page
        return redirect("/")

    # If it's not a POST request, render the registration form
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Fetch the user's stock portfolio
    user_stocks = db.execute(
        "SELECT symbol, SUM(quantity) as total_quantity FROM userdata WHERE id = :id GROUP BY symbol HAVING total_quantity > 0",
        id=session["user_id"],
    )

    if request.method == "POST":
        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("Shares must be a number")

        if not shares:
            return apology("Must enter the number of shares")

        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        cash = db.execute(
            "SELECT cash FROM users WHERE id = :id", id=session["user_id"]
        )[0]["cash"]

        # Check if the selected stock exists in the user's portfolio
        selected_stock = next(
            (stock for stock in user_stocks if stock["symbol"] == symbol), None
        )

        if shares < 0:
            return apology("Enter a valid number of shares to sell")
        elif not quote:
            return apology("This ticker doesn't exist in our database")
        elif not symbol:
            return apology("You must enter a ticker")
        elif not selected_stock:
            return apology("You don't own this stock")
        elif selected_stock["total_quantity"] < shares:
            return apology("You don't have enough shares to sell")

        value = shares * quote["price"]
        db.execute(
            "INSERT INTO userdata (id, symbol, quantity, value, buysell, date) VALUES (:id, :symbol, :quantity, :value, 'sell', datetime('now'))",
            id=session["user_id"],
            symbol=symbol,
            quantity=-shares,
            value=-value,
        )
        db.execute(
            "UPDATE users SET cash = cash + :profit WHERE id = :id",
            profit=value,
            id=session["user_id"],
        )
        flash("The sale was successful")
        return redirect("/")
    else:
        return render_template("sell.html", user_stocks=user_stocks)
