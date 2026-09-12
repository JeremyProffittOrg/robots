"""Upload the assembly video to a private S3 bucket, presign a 7-day link, and email the
operator an HTML status message with the assembly-manual PDF attached (SES, us-east-1).

Usage (from C:/dev/robots/fable-r2d2):
    python scripts/deliver.py --dry-run          # build the MIME message, print size, no send
    python scripts/deliver.py                    # upload, presign, send once, print MessageId

Requires the local AWS identity (boto3 default credential chain). Sends exactly once: the
script refuses to run if output/delivery-receipt.json already records a MessageId unless
--force is given. No credentials are printed.
"""
import argparse
import datetime
import hashlib
import json
import subprocess
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parents[1]
REGION = "us-east-1"
BUCKET = "robots-deliverables-759775734231"
KEY_PREFIX = "fable-r2d2/"
VIDEO = ROOT / "output/video/r2d2-assembly-and-operation.mp4"
PDF = ROOT / "output/pdf/r2d2-assembly-manual.pdf"
RECEIPT = ROOT / "output/delivery-receipt.json"
TEMPLATE = Path.home() / ".claude/templates/email-status.html"
SENDER = "robots@jeremy.ninja"
RECIPIENT = "proffitt.jeremy@gmail.com"
REPLY_TO = "proffitt.jeremy@gmail.com"
LINK_DAYS = 7


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def ensure_bucket(s3):
    try:
        s3.head_bucket(Bucket=BUCKET)
        return "existing"
    except s3.exceptions.ClientError:
        s3.create_bucket(Bucket=BUCKET)
        s3.put_public_access_block(Bucket=BUCKET, PublicAccessBlockConfiguration={
            "BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True})
        s3.put_bucket_encryption(Bucket=BUCKET, ServerSideEncryptionConfiguration={
            "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]})
        return "created"


def upload_and_presign(s3, path, key):
    s3.upload_file(str(path), BUCKET, key, ExtraArgs={"ContentType": "video/mp4" if path.suffix == ".mp4" else "application/pdf"})
    url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=LINK_DAYS * 86400)
    return url


def build_html(context):
    html = TEMPLATE.read_text(encoding="utf-8")
    # Remove the correction block unless a correction is supplied.
    if not context.get("CORRECTION"):
        start = html.index("<!-- Include ONLY when a claim")
        end = html.index("</div>", html.index("{{WHAT_I_SAID_THEN_WHAT_IS_TRUE_AND_HOW_IT_WAS_CAUGHT}}")) + len("</div>")
        html = html[:start] + html[end:]
    else:
        html = html.replace("{{WHAT_I_SAID_THEN_WHAT_IS_TRUE_AND_HOW_IT_WAS_CAUGHT}}", context["CORRECTION"])
    for key, value in context.items():
        html = html.replace("{{" + key + "}}", value)
    return html


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--outcome", required=True, help="one-line outcome for the top block")
    parser.add_argument("--evidence", required=True, help="path to a text file with verbatim command output")
    parser.add_argument("--next", default="Physical build: print the fit coupons first, then the feet.")
    parser.add_argument("--in-flight", default="Nothing; the package is complete.")
    args = parser.parse_args()
    for path in (VIDEO, PDF, TEMPLATE):
        if not path.is_file():
            raise SystemExit(f"Missing: {path}")
    if RECEIPT.exists() and not args.force and not args.dry_run:
        prior = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if prior.get("MessageId"):
            raise SystemExit(f"Already sent: MessageId {prior['MessageId']}; use --force to send again")
    sha = git("rev-parse", "HEAD")
    subject_line = git("log", "-1", "--format=%s")
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    video_url = "(dry run: no upload)"
    pdf_url = "(dry run: no upload)"
    bucket_state = "dry-run"
    if not args.dry_run:
        s3 = boto3.client("s3", region_name=REGION)
        bucket_state = ensure_bucket(s3)
        video_url = upload_and_presign(s3, VIDEO, KEY_PREFIX + VIDEO.name)
        pdf_url = upload_and_presign(s3, PDF, KEY_PREFIX + PDF.name)
    evidence = Path(args.evidence).read_text(encoding="utf-8")
    links = (f'<p style="margin:0 0 12px;color:#0b0f19;background-color:#ffffff">Video (S3, private, link valid {LINK_DAYS} days): '
             f'<a href="{video_url}" style="color:#1d4ed8;background-color:#ffffff">{VIDEO.name}</a> '
             f'({VIDEO.stat().st_size / 1e6:.1f} MB, SHA-256 {sha256(VIDEO)[:16]}...)</p>'
             f'<p style="margin:0 0 12px;color:#0b0f19;background-color:#ffffff">Assembly manual PDF: attached, and also on S3: '
             f'<a href="{pdf_url}" style="color:#1d4ed8;background-color:#ffffff">{PDF.name}</a> '
             f'({PDF.stat().st_size / 1e6:.1f} MB, SHA-256 {sha256(PDF)[:16]}...)</p>')
    html = build_html({
        "OUTCOME_ONE_LINE": args.outcome, "SHA": sha[:12], "COMMIT_SUBJECT": subject_line,
        "ACTUAL_COMMAND_OUTPUT": evidence.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"),
        "ITEM": args.in_flight, "NEXT": args.next + links,
        "REPO": "JeremyProffittOrg/robots (fable-r2d2)", "BRANCH": "main", "HEAD_SHA": sha[:12], "TIMESTAMP": timestamp,
    })
    message = MIMEMultipart("mixed")
    message["Subject"] = args.subject
    message["From"] = f"fable-r2d2 build <{SENDER}>"
    message["To"] = RECIPIENT
    message["Reply-To"] = REPLY_TO
    alternative = MIMEMultipart("alternative")
    text = (f"{args.outcome}\n\nVideo (S3, {LINK_DAYS}-day link): {video_url}\nPDF: attached and {pdf_url}\n\n"
            f"Evidence:\n{evidence}\n\nNext: {args.next}\n{sha[:12]} {subject_line}\n")
    alternative.attach(MIMEText(text, "plain", "utf-8"))
    alternative.attach(MIMEText(html, "html", "utf-8"))
    message.attach(alternative)
    attachment = MIMEApplication(PDF.read_bytes(), _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename=PDF.name)
    message.attach(attachment)
    raw = message.as_bytes()
    print(f"MIME size {len(raw)} bytes; bucket {bucket_state}; PDF sha256 {sha256(PDF)}; video sha256 {sha256(VIDEO)}")
    if len(raw) > 40 * 1024 * 1024:
        raise SystemExit("Message exceeds the SES 40 MB limit")
    if args.dry_run:
        (ROOT / "output/delivery-preview.html").write_text(html, encoding="utf-8")
        print("DRY RUN: wrote output/delivery-preview.html; nothing sent")
        return
    ses = boto3.client("ses", region_name=REGION)
    response = ses.send_raw_email(Source=SENDER, Destinations=[RECIPIENT], RawMessage={"Data": raw})
    receipt = {"MessageId": response["MessageId"], "sent_at_utc": timestamp, "to": RECIPIENT, "subject": args.subject,
               "mime_bytes": len(raw), "video_sha256": sha256(VIDEO), "pdf_sha256": sha256(PDF),
               "video_s3_key": KEY_PREFIX + VIDEO.name, "pdf_s3_key": KEY_PREFIX + PDF.name, "bucket": BUCKET,
               "link_valid_days": LINK_DAYS, "head_sha": sha}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"SENT MessageId {response['MessageId']}")


if __name__ == "__main__":
    main()
