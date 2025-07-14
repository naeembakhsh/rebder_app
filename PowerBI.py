# import os
# import time
# from urllib.parse import urlencode
# from flask import Flask, redirect, request, session, url_for, jsonify
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# CLIENT_ID     = os.getenv("GHL_CLIENT_ID")
# CLIENT_SECRET = os.getenv("GHL_CLIENT_SECRET")
# REDIRECT_URI  = os.getenv("GHL_REDIRECT_URI")
# AUTH_BASE     = "https://marketplace.gohighlevel.com/oauth/chooselocation"
# TOKEN_URL     = "https://services.leadconnectorhq.com/oauth/token"
# API_BASE      = "https://services.leadconnectorhq.com"

# if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
#     raise RuntimeError("GHL_CLIENT_ID, GHL_CLIENT_SECRET, and GHL_REDIRECT_URI must be set in .env")

# app = Flask(__name__)
# app.secret_key = os.urandom(24)

# def build_auth_url():
#     params = {
#         "response_type": "code",
#         "client_id": CLIENT_ID,
#         "redirect_uri": REDIRECT_URI,
#         "scope": "locations.readonly campaigns.readonly users.readonly conversations.readonly contacts.readonly opportunities.readonly"
#     }
#     return f"{AUTH_BASE}?{urlencode(params)}"

# def store_tokens(tokens, location_id):
#     session["access_token"]  = tokens["access_token"]
#     session["refresh_token"] = tokens.get("refresh_token")
#     expires_in = tokens.get("expires_in", 3600)
#     session["token_expires_at"] = int(time.time()) + int(expires_in) - 30
#     session["location_id"]   = location_id if location_id else tokens.get("locationId")
#     session["company_id"]    = tokens.get("companyId")

# def token_expired():
#     return "token_expires_at" not in session or int(time.time()) >= session["token_expires_at"]

# def refresh_access_token():
#     data = {
#         "grant_type":    "refresh_token",
#         "refresh_token": session.get("refresh_token"),
#         "client_id":     CLIENT_ID,
#         "client_secret": CLIENT_SECRET
#     }
#     resp = requests.post(TOKEN_URL, data=data)
#     resp.raise_for_status()
#     tokens = resp.json()
#     store_tokens(tokens, session.get("location_id"))

# def get_access_token_from_request():
#     # 1. Try Authorization header (Bearer)
#     auth_header = request.headers.get("Authorization")
#     if auth_header and auth_header.startswith("Bearer "):
#         return auth_header.replace("Bearer ", "").strip()
#     # 2. Try access_token query param
#     if request.args.get("access_token"):
#         return request.args.get("access_token")
#     # 3. Fall back to session (browser user)
#     if "access_token" in session:
#         if token_expired():
#             refresh_access_token()
#         return session.get("access_token")
#     return None

# def get_location_id_from_request():
#     # 1. Try query param
#     if request.args.get("locationId"):
#         return request.args.get("locationId")
#     # 2. Try JSON body (for POST)
#     if request.is_json and request.get_json(silent=True):
#         body = request.get_json(silent=True)
#         if body and body.get("locationId"):
#             return body.get("locationId")
#     # 3. Fall back to session
#     return session.get("location_id")

# @app.route("/")
# def index():
#     return """
#     <h2>GoHighLevel OAuth Demo</h2>
#     <a href="/login">Connect your GHL account</a>
#     """

# @app.route("/login")
# def login():
#     return redirect(build_auth_url())

# @app.route("/callback", methods=["GET"])
# def callback():
#     error = request.args.get("error")
#     if error:
#         return jsonify({"error": f"Error during authorization: {error}"}), 400

#     code = request.args.get("code")
#     location_id = request.args.get("locationId")

#     if not code:
#         return jsonify({"error": "No code provided."}), 400

#     data = {
#         "grant_type":    "authorization_code",
#         "client_id":     CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "code":          code,
#         "redirect_uri":  REDIRECT_URI
#     }
#     try:
#         token_resp = requests.post(TOKEN_URL, data=data)
#         if not token_resp.ok:
#             return jsonify({
#                 "error": "Token exchange failed.",
#                 "detail": token_resp.text,
#                 "status_code": token_resp.status_code
#             }), token_resp.status_code
#         tokens = token_resp.json()
#         response_json = {
#             "access_token": tokens.get("access_token"),
#             "refresh_token": tokens.get("refresh_token"),
#             "expires_in": tokens.get("expires_in", 3600),
#             "token_type": tokens.get("token_type", "bearer"),
#             "location_id": location_id or tokens.get("locationId"),
#             "company_id": tokens.get("companyId")
#         }
#         return jsonify(response_json)
#     except Exception as e:
#         return jsonify({"error": "Internal server error.", "detail": str(e)}), 500

# @app.route("/refresh_token", methods=["POST"])
# def refresh_token():
#     req = request.get_json(force=True)
#     refresh_token = req.get("refresh_token")
#     location_id = req.get("location_id")  # Optional; for your client convenience

#     if not refresh_token:
#         return jsonify({"error": "No refresh_token provided."}), 400

#     data = {
#         "grant_type":    "refresh_token",
#         "refresh_token": refresh_token,
#         "client_id":     CLIENT_ID,
#         "client_secret": CLIENT_SECRET
#     }
#     try:
#         token_resp = requests.post(TOKEN_URL, data=data)
#         if not token_resp.ok:
#             return jsonify({
#                 "error": "Token refresh failed.",
#                 "detail": token_resp.text,
#                 "status_code": token_resp.status_code
#             }), token_resp.status_code
#         tokens = token_resp.json()
#         response_json = {
#             "access_token": tokens.get("access_token"),
#             "refresh_token": tokens.get("refresh_token"),
#             "expires_in": tokens.get("expires_in", 3600),
#             "token_type": tokens.get("token_type", "bearer"),
#             "location_id": location_id or tokens.get("locationId"),
#             "company_id": tokens.get("companyId")
#         }
#         return jsonify(response_json)
#     except Exception as e:
#         return jsonify({"error": "Internal server error.", "detail": str(e)}), 500

# def safe_get_json(resp):
#     try:
#         return resp.json()
#     except Exception:
#         return {"error": f"Non-JSON response: {resp.text}", "status": resp.status_code}

# @app.route("/get_campaigns", methods=["GET"])
# def get_campaigns():
#     access_token = get_access_token_from_request()
#     if not access_token:
#         return jsonify({"error": "No valid access token."}), 401

#     params = request.args.to_dict(flat=True)
#     if "locationId" not in params:
#         location_id = get_location_id_from_request()
#         if not location_id:
#             return jsonify({"error": "No locationId found in session, query, or body."}), 400
#         params["locationId"] = location_id

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Version": "2021-07-28"
#     }

#     resp = requests.get(f"{API_BASE}/campaigns", headers=headers, params=params)
#     if resp.status_code != 200:
#         return jsonify({
#             "error": "Error fetching campaigns",
#             "detail": resp.text,
#             "status_code": resp.status_code
#         }), resp.status_code

#     try:
#         data = resp.json()
#     except Exception:
#         return jsonify({"error": "Could not parse campaigns response", "raw_response": resp.text}), 500

#     return jsonify(data)

# @app.route("/get_conversations_with_details", methods=["GET"])
# def get_conversations_with_details():
#     access_token = get_access_token_from_request()
#     if not access_token:
#         return jsonify({"error": "No valid access token."}), 401

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Version": "2021-04-15"
#     }

#     params = request.args.to_dict(flat=True)
#     if "locationId" not in params:
#         location_id = get_location_id_from_request()
#         if not location_id:
#             return jsonify({"error": "No locationId found in session, query, or body."}), 400
#         params["locationId"] = location_id

#     # 1. Search for conversations (returns summary info)
#     search_resp = requests.get(f"{API_BASE}/conversations/search", headers=headers, params=params)
#     if search_resp.status_code != 200:
#         return jsonify({
#             "error": "Error searching conversations",
#             "detail": search_resp.text,
#             "status_code": search_resp.status_code
#         }), search_resp.status_code

#     try:
#         search_data = search_resp.json()
#     except Exception:
#         return jsonify({"error": "Could not parse conversations search response", "raw_response": search_resp.text}), 500

#     conversations = search_data.get("conversations", [])

#     # 2. For each conversation, fetch the full details using /conversations/{conversationId}
#     detailed_conversations = []
#     for conv in conversations:
#         conversation_id = conv.get("id")
#         if not conversation_id:
#             continue  # skip if id is missing
#         detail_resp = requests.get(f"{API_BASE}/conversations/{conversation_id}", headers=headers)
#         if detail_resp.status_code == 200:
#             try:
#                 detailed_conversations.append(detail_resp.json())
#             except Exception:
#                 detailed_conversations.append({"id": conversation_id, "error": "Could not parse detail", "raw_response": detail_resp.text})
#         else:
#             detailed_conversations.append({"id": conversation_id, "error": "Error fetching conversation", "status_code": detail_resp.status_code, "raw_response": detail_resp.text})

#     return jsonify({
#         "conversations_summary": conversations,
#         "conversations_detailed": detailed_conversations
#     })

# @app.route("/get_opportunities", methods=["GET"])
# def get_opportunities():
#     access_token = get_access_token_from_request()
#     if not access_token:
#         return jsonify({"error": "No valid access token."}), 401

#     params = request.args.to_dict(flat=True)
#     if "location_id" not in params and "locationId" not in params:
#         location_id = get_location_id_from_request()
#         if not location_id:
#             return jsonify({"error": "No location_id/locationId found in session, query, or body."}), 400
#         params["location_id"] = location_id

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Version": "2021-07-28"
#     }

#     resp = requests.get(f"{API_BASE}/opportunities/search", headers=headers, params=params)
#     if resp.status_code != 200:
#         return jsonify({
#             "error": "Error fetching opportunities",
#             "detail": resp.text,
#             "status_code": resp.status_code
#         }), resp.status_code

#     try:
#         data = resp.json()
#     except Exception:
#         return jsonify({"error": "Could not parse opportunities response", "raw_response": resp.text}), 500

#     return jsonify(data)

# @app.route("/get_pipelines", methods=["GET"])
# def get_pipelines():
#     access_token = get_access_token_from_request()
#     if not access_token:
#         return jsonify({"error": "No valid access token."}), 401

#     params = request.args.to_dict(flat=True)
#     if "locationId" not in params:
#         location_id = get_location_id_from_request()
#         if not location_id:
#             return jsonify({"error": "No locationId found in session, query, or body."}), 400
#         params["locationId"] = location_id

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Version": "2021-07-28"
#     }

#     resp = requests.get(f"{API_BASE}/opportunities/pipelines", headers=headers, params=params)
#     if resp.status_code != 200:
#         return jsonify({
#             "error": "Error fetching pipelines",
#             "detail": resp.text,
#             "status_code": resp.status_code
#         }), resp.status_code

#     try:
#         data = resp.json()
#     except Exception:
#         return jsonify({"error": "Could not parse pipelines response", "raw_response": resp.text}), 500

#     return jsonify(data)

# @app.route("/get_users", methods=["GET"])
# def get_users():
#     access_token = get_access_token_from_request()
#     if not access_token:
#         return jsonify({"error": "No valid access token."}), 401

#     params = request.args.to_dict(flat=True)
#     # companyId is required!
#     if "companyId" not in params:
#         company_id = session.get("company_id")
#         if not company_id:
#             return jsonify({"error": "No companyId found in session or request."}), 400
#         params["companyId"] = company_id

#     # location_id is optional, but set if available
#     if "location_id" not in params and "locationId" not in params:
#         location_id = get_location_id_from_request()
#         if location_id:
#             params["locationId"] = location_id

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Version": "2021-07-28"
#     }

#     resp = requests.get(f"{API_BASE}/users/search", headers=headers, params=params)
#     if resp.status_code != 200:
#         return jsonify({
#             "error": "Error fetching users",
#             "detail": resp.text,
#             "status_code": resp.status_code
#         }), resp.status_code

#     try:
#         data = resp.json()
#     except Exception:
#         return jsonify({"error": "Could not parse users response", "raw_response": resp.text}), 500

#     return jsonify(data)

# @app.route("/search_contacts", methods=["POST"])
# def search_contacts():
#     access_token = get_access_token_from_request()
#     if not access_token:
#         return jsonify({"error": "No valid access token."}), 401

#     body = request.get_json(force=True) or {}

#     if not body.get("locationId"):
#         location_id = get_location_id_from_request()
#         if not location_id:
#             return jsonify({"error": "No locationId found in request, query, or session."}), 400
#         body["locationId"] = location_id

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Version": "2021-07-28",
#         "Content-Type": "application/json"
#     }

#     resp = requests.post(f"{API_BASE}/contacts/search", headers=headers, json=body)
#     if resp.status_code != 200:
#         return jsonify({
#             "error": "Error searching contacts",
#             "detail": resp.text,
#             "status_code": resp.status_code
#         }), resp.status_code

#     try:
#         data = resp.json()
#     except Exception:
#         return jsonify({"error": "Could not parse contacts response", "raw_response": resp.text}), 500

#     return jsonify(data)

# @app.route("/profile")
# def profile():
#     access_token = get_access_token_from_request()
#     location_id  = get_location_id_from_request()
#     if not access_token or not location_id:
#         return redirect(url_for("index"))

#     headers = {"Authorization": f"Bearer {access_token}"}

#     # 1) Get this location's details
#     loc_resp = requests.get(f"{API_BASE}/locations/{location_id}", headers=headers)
#     locs = safe_get_json(loc_resp)

#     # 2) List Campaigns for this location
#     camps_resp = requests.get(f"{API_BASE}/campaigns", headers=headers, params={"locationId": location_id})
#     camps = safe_get_json(camps_resp)

#     # 3) List Contacts for this location
#     contacts_resp = requests.get(f"{API_BASE}/contacts", headers=headers, params={"locationId": location_id, "limit": 10})
#     contacts = safe_get_json(contacts_resp)

#     return jsonify({
#         "location": locs,
#         "campaigns": camps,
#         "contacts": contacts
#     })

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

