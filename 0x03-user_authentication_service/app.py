#!/usr/bin/env python3
"""A basic Flask app for managing a digital library."""

from flask import Flask, jsonify, request, abort, redirect
from library_manager import LibraryManager

app = Flask(__name__)
LIB = LibraryManager()

@app.route("/", methods=["GET"], strict_slashes=False)
def home() -> str:
    """GET /
    Return:
        - The welcome message for the digital library.
    """
    return jsonify({"message": "Welcome to our Digital Library"})

@app.route("/books", methods=["POST"], strict_slashes=False)
def add_book() -> str:
    """POST /books
    Return:
        - The newly added book's information.
    """
    title, author, isbn = request.form.get("title"), request.form.get("author"), request.form.get("isbn")
    try:
        LIB.add_book(title, author, isbn)
        return jsonify({"title": title, "message": "book added successfully"}), 201
    except ValueError:
        return jsonify({"message": "book already in library"}), 400

@app.route("/members", methods=["POST"], strict_slashes=False)
def register_member() -> str:
    """POST /members
    Return:
        - The new member's registration information.
    """
    name, email = request.form.get("name"), request.form.get("email")
    try:
        member = LIB.register_member(name, email)
        return jsonify({"member_id": member.id, "message": "member registered"}), 201
    except ValueError:
        return jsonify({"message": "email already registered"}), 400

@app.route("/loans", methods=["POST"], strict_slashes=False)
def loan_book() -> str:
    """POST /loans
    Return:
        - The book loan confirmation.
    """
    member_id, isbn = request.form.get("member_id"), request.form.get("isbn")
    if LIB.loan_book(member_id, isbn):
        return jsonify({"message": "book loaned successfully"}), 200
    else:
        abort(400)

@app.route("/returns", methods=["POST"], strict_slashes=False)
def return_book() -> str:
    """POST /returns
    Return:
        - The book return confirmation and any applicable fine.
    """
    isbn = request.form.get("isbn")
    fine = LIB.return_book(isbn)
    if fine is not None:
        return jsonify({"message": "book returned", "fine": fine}), 200
    else:
        abort(400)

@app.route("/member/<member_id>", methods=["GET"], strict_slashes=False)
def get_member_loans(member_id: str) -> str:
    """GET /member/<member_id>
    Return:
        - The member's current loans.
    """
    loans = LIB.get_member_loans(member_id)
    if loans:
        return jsonify({"member_id": member_id, "loans": loans}), 200
    else:
        abort(404)

@app.route("/search", methods=["GET"], strict_slashes=False)
def search_books() -> str:
    """GET /search
    Return:
        - The search results for books.
    """
    keyword = request.args.get("q")
    results = LIB.search_books(keyword)
    return jsonify({"results": results}), 200

@app.route("/member/<member_id>", methods=["PUT"], strict_slashes=False)
def update_member_info(member_id: str) -> str:
    """PUT /member/<member_id>
    Return:
        - Confirmation of member information update.
    """
    update_data = request.form.to_dict()
    if LIB.update_member_info(member_id, **update_data):
        return jsonify({"message": "member information updated"}), 200
    else:
        abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
