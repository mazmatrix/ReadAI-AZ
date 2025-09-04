from flask import Flask, request, jsonify
import logging
import IntegrationFunctions
import json

app = Flask(__name__)

# Set up logging. Creates a log file called app.log
logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger()

# Open the settings.json file and read the contents
with open('settings.json', "rb") as PFile:
    password_data = json.loads(PFile.read().decode('utf-8'))

# Set OneVizion credentials from settings.json
url_onevizion = password_data["urlOneVizion"]
login_onevizion = password_data["loginOneVizion"]
pass_onevizion = password_data["passOneVizion"]

# Initialize the integration functions
integration = IntegrationFunctions.BasicIntegration(
    urlOneVizion=url_onevizion, loginOneVizion=login_onevizion, passOneVizion=pass_onevizion
)


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)

        # Extract top-level fields
        session_id = data.get("session_id")
        trigger = data.get("trigger")
        title = data.get("title")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        participants = data.get("participants", [])
        owner = data.get("owner", {})
        summary = data.get("summary")
        action_items = [item.get("text") for item in data.get("action_items", [])]
        key_questions = [q.get("text") for q in data.get("key_questions", [])]
        topics = [t.get("text") for t in data.get("topics", [])]
        report_url = data.get("report_url")

        # Chapter summaries
        chapter_summaries = []
        for ch in data.get("chapter_summaries", []):
            chapter_summaries.append({
                "title": ch.get("title"),
                "description": ch.get("description"),
                "topics": [t.get("text") for t in ch.get("topics", [])]
            })

        # Transcript
        speakers = [s.get("name") for s in data.get("transcript", {}).get("speakers", [])]
        speaker_blocks = []
        for block in data.get("transcript", {}).get("speaker_blocks", []):
            speaker_blocks.append({
                "start_time": block.get("start_time"),
                "end_time": block.get("end_time"),
                "speaker": block.get("speaker", {}).get("name"),
                "words": block.get("words")
            })

        # Build dictionary
        parsed_payload = {
            "OSPD_SESSION_ID": session_id,
            "OSPD_MEETING_TITLE": title,
            "OSPD_MEETING_TIME": start_time,
            "OSPD_PARTICIPANTS": participants,
            "OSPD_MEETING_OWNER": owner,
            "OSPD_MEETING_SUMMARY": summary,
            "OSPD_ACTION_ITEMS": action_items,
            "OSPD_REPORT_URL": report_url,
            "OSPD_MEETING_TRANSCRIPT": {
                "speakers": speakers,
                "speaker_blocks": speaker_blocks
            }
        }

        parent_filter = {"XITOR_KEY": "Float Fiber"}

        try:
            new_trackor = integration.create_trackor("OSP_DOCUMENTS", parsed_payload, "Client", parent_filter)
            logger.info(f"Successfully created trackor  {new_trackor}")
        except Exception as e:
            logger.error(f"Failed to create trackor: {e}")

        # Return structured response
        return jsonify({
            "status": "success",
            "message": "Webhook parsed successfully!",
            "parsed_payload": parsed_payload
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
