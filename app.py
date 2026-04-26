from flask import Flask, render_template, request, jsonify, Response
from sms import SendSms
import threading
import queue
import json
import time

app = Flask(__name__)

log_queue = queue.Queue()
stop_event = threading.Event()
active_thread = None
stats = {"sent": 0, "failed": 0, "running": False, "target": ""}

servisler_sms = []
for attribute in dir(SendSms):
    attribute_value = getattr(SendSms, attribute)
    if callable(attribute_value) and not attribute.startswith('__'):
        servisler_sms.append(attribute)


def push_log(message, status="info"):
    log_queue.put(json.dumps({"message": message, "status": status, "time": time.strftime("%H:%M:%S")}))


def run_normal(phone_numbers, mail, count, interval):
    global stats
    stats["running"] = True
    stats["sent"] = 0
    stats["failed"] = 0

    try:
        if count is None:
            push_log("Starting continuous send mode. Click Stop to end.", "info")
            while not stop_event.is_set():
                for tel_no in phone_numbers:
                    if stop_event.is_set():
                        break
                    sms = SendSms(tel_no, mail)
                    for attr in servisler_sms:
                        if stop_event.is_set():
                            break
                        method = getattr(sms, attr)
                        if callable(method):
                            try:
                                method()
                                stats["sent"] += 1
                                push_log(f"[SUCCESS] {tel_no} --> {attr}", "success")
                            except Exception as e:
                                stats["failed"] += 1
                                push_log(f"[FAILED] {tel_no} --> {attr}", "error")
                            time.sleep(interval)
        else:
            for tel_no in phone_numbers:
                if stop_event.is_set():
                    break
                push_log(f"Starting for number: {tel_no}", "info")
                sms = SendSms(tel_no, mail)
                sent_for_number = 0
                while sent_for_number < count and not stop_event.is_set():
                    for attr in servisler_sms:
                        if sent_for_number >= count or stop_event.is_set():
                            break
                        method = getattr(sms, attr)
                        if callable(method):
                            try:
                                method()
                                stats["sent"] += 1
                                sent_for_number += 1
                                push_log(f"[SUCCESS] {tel_no} --> {attr} ({sent_for_number}/{count})", "success")
                            except Exception as e:
                                stats["failed"] += 1
                                push_log(f"[FAILED] {tel_no} --> {attr}", "error")
                            time.sleep(interval)
                push_log(f"Finished for {tel_no}: {sent_for_number} SMS sent.", "info")
    finally:
        stats["running"] = False
        push_log("Operation completed.", "info")


def run_turbo(phone, mail):
    global stats
    stats["running"] = True
    stats["sent"] = 0
    stats["failed"] = 0
    push_log("Turbo mode activated — sending at maximum speed.", "info")

    try:
        sms_obj = SendSms(phone, mail)
        while not stop_event.is_set():
            threads = []
            for attr in servisler_sms:
                if stop_event.is_set():
                    break
                def worker(a=attr):
                    try:
                        getattr(sms_obj, a)()
                        stats["sent"] += 1
                        push_log(f"[SUCCESS] {phone} --> {a}", "success")
                    except:
                        stats["failed"] += 1
                        push_log(f"[FAILED] {phone} --> {a}", "error")
                t = threading.Thread(target=worker, daemon=True)
                threads.append(t)
                t.start()
            for t in threads:
                t.join(timeout=0.5)
    finally:
        stats["running"] = False
        push_log("Turbo operation stopped.", "info")


@app.route("/")
def index():
    return render_template("index.html", service_count=len(servisler_sms), services=servisler_sms)


@app.route("/start", methods=["POST"])
def start():
    global active_thread, stop_event, stats

    if stats["running"]:
        return jsonify({"error": "Already running. Stop the current operation first."}), 400

    data = request.json
    mode = data.get("mode", "normal")
    phone_raw = data.get("phone", "").replace(" ", "")
    mail = data.get("mail", "").strip()
    interval = float(data.get("interval", 1))
    count_raw = data.get("count", "")

    phone_numbers = [p.strip() for p in phone_raw.split(",") if p.strip()]
    invalid = [p for p in phone_numbers if len(p) != 10 or not p.isdigit()]
    if invalid:
        return jsonify({"error": f"Invalid phone number(s): {', '.join(invalid)}. Must be 10 digits without +90."}), 400
    if not phone_numbers:
        return jsonify({"error": "Please enter at least one phone number."}), 400
    if mail and ("@" not in mail or "." not in mail.split("@")[-1]):
        return jsonify({"error": "Invalid email address."}), 400

    count = None
    if count_raw:
        try:
            count = int(count_raw)
            if count <= 0:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Count must be a positive integer."}), 400

    stop_event = threading.Event()
    stats["target"] = phone_raw

    while not log_queue.empty():
        try:
            log_queue.get_nowait()
        except:
            break

    if mode == "turbo":
        if len(phone_numbers) != 1:
            return jsonify({"error": "Turbo mode supports only one phone number."}), 400
        active_thread = threading.Thread(target=run_turbo, args=(phone_numbers[0], mail), daemon=True)
    else:
        active_thread = threading.Thread(target=run_normal, args=(phone_numbers, mail, count, interval), daemon=True)

    active_thread.start()
    return jsonify({"success": True, "message": f"Started in {mode} mode."})


@app.route("/stop", methods=["POST"])
def stop():
    global stop_event
    stop_event.set()
    return jsonify({"success": True, "message": "Stop signal sent."})


@app.route("/stats")
def get_stats():
    return jsonify(stats)


@app.route("/logs")
def logs():
    def stream():
        while True:
            try:
                msg = log_queue.get(timeout=20)
                yield f"data: {msg}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'message': '', 'status': 'ping'})}\n\n"
    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
