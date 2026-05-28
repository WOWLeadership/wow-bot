from flask import Flask, request
import requests
import os

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

RULES_LINK = "https://docs.google.com/document/d/1cPsrBR0YwIK6o0B2iBqPvg5F9aMoNKgDzAEAKZL81xs/edit?usp=sharing"
REPORT_LINK = "https://forms.gle/x76SEWDnY5mNQ4LR8"
ROLES_LINK = "https://master-role-document-2.tiiny.site/"
SCHEDULE_LINK = None


@app.route("/", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification token mismatch", 403


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]

                if "message" in event:
                    message = event["message"]

                    if "quick_reply" in message:
                        payload = message["quick_reply"]["payload"]
                        handle_payload(sender_id, payload)
                    else:
                        send_main_menu(sender_id)

                elif "postback" in event:
                    payload = event["postback"]["payload"]
                    handle_payload(sender_id, payload)

    return "ok", 200


def handle_payload(sender_id, payload):
    if payload == "RULES":
        send_text(sender_id, f"WOW Bot: You can review the official WOW Community Guidelines here:\n{RULES_LINK}")

    elif payload == "REPORT":
        send_text(
            sender_id,
            f"WOW Bot: Reports should be submitted within 24 hours of the incident when possible.\n\n"
            f"Use this form to submit a report:\n{REPORT_LINK}"
        )

    elif payload == "ROLES":
        send_text(sender_id, f"WOW Bot: You can review the current role document here:\n{ROLES_LINK}")

    elif payload == "SCHEDULE":
        if SCHEDULE_LINK:
            send_text(sender_id, f"WOW Bot: View the current game schedule here:\n{SCHEDULE_LINK}")
        else:
            send_text(sender_id, "WOW Bot: The schedule link is not available yet. Please check back later.")

    elif payload == "DEFINITIONS":
        send_text(sender_id, definitions_text())

    elif payload == "HOST_REQUEST":
        send_text(sender_id, host_request_text())

    else:
        send_main_menu(sender_id)


def send_main_menu(recipient_id):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "text": "WOW Bot: What can I help you with?",
            "quick_replies": [
                {"content_type": "text", "title": "Rules", "payload": "RULES"},
                {"content_type": "text", "title": "Report", "payload": "REPORT"},
                {"content_type": "text", "title": "Roles", "payload": "ROLES"},
                {"content_type": "text", "title": "Schedule", "payload": "SCHEDULE"},
                {"content_type": "text", "title": "Definitions", "payload": "DEFINITIONS"},
                {"content_type": "text", "title": "Host Request", "payload": "HOST_REQUEST"}
            ]
        }
    }

    requests.post(url, json=payload)


def send_text(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    requests.post(url, json=payload)


def definitions_text():
    return (
        "WOW Bot: Key Definitions\n\n"
        "Check: An investigative action used to learn information about a player.\n"
        "Claim: Stating the role you were assigned.\n"
        "CVS: Check, Vote, Save.\n"
        "Day: The public discussion and voting phase.\n"
        "Night: The phase where roles privately perform abilities.\n"
        "Vote: Publicly choosing a player for elimination.\n"
        "Save: Protecting a player from elimination.\n"
        "Throw: Intentionally harming your team or alignment’s chances of winning.\n"
        "Headshot: Immediate removal from active gameplay due to a rule or policy violation.\n"
        "Martyr: Sacrificing yourself or benefiting from elimination to help others.\n"
        "Turned: Becoming a different role or alignment during gameplay."
    )


def host_request_text():
    return (
        "WOW Bot: Host Request Intake\n\n"
        "Please send Leadership the following information:\n"
        "1. Your Facebook name\n"
        "2. Date and time you want to host\n"
        "3. Expected player count\n"
        "4. Game theme or game type\n"
        "5. Whether you need help balancing\n"
        "6. Any special rules, roles, or mechanics planned"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
