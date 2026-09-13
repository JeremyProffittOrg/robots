"""Deliver the fable-r2d2 revision D package: one HTML email with the assembly manual attached and a
7-day presigned link to the video in the private S3 bucket, sent once over SESv2 (raw MIME, us-east-1).

Usage (from C:/dev/robots/fable-r2d2):
    python scripts/deliver.py --dry-run     # build the MIME message, print its size and any send blockers;
                                            # nothing is uploaded, sent or written
    python scripts/deliver.py               # refuse unless the package verifies as revision D, then upload,
                                            # presign, send once and write output/delivery-receipt.json

Objects go under fable-r2d2/revision-d/ so the revision C objects (fable-r2d2/<file>) are never
overwritten. Subject, outcome and evidence default to values read from docs/verification.json,
docs/pdf-check.json, output/video/video-manifest.json and scripts/parts.json; --subject, --outcome
and --evidence override them. Requires the local AWS identity (boto3 default credential chain) only
for a real send. No credentials are printed.
"""
import argparse
import datetime
import hashlib
import html as html_lib
import json
import subprocess
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_layout import REVISION, package_counts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REGION = "us-east-1"
BUCKET = "robots-deliverables-759775734231"
KEY_PREFIX = f"fable-r2d2/revision-{REVISION.lower()}/"
VIDEO = ROOT / "output/video/r2d2-assembly-and-operation.mp4"
PDF = ROOT / "output/pdf/r2d2-assembly-manual.pdf"
RECEIPT = ROOT / "output/delivery-receipt.json"
TEMPLATE = Path.home() / ".claude/templates/email-status.html"
SENDER = "robots@jeremy.ninja"
RECIPIENT = "proffitt.jeremy@gmail.com"
REPLY_TO = "proffitt.jeremy@gmail.com"
LINK_DAYS = 7
SESV2_LIMIT_BYTES = 40 * 1024 * 1024


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def read_json(path):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def s3_key(path):
    key = KEY_PREFIX + Path(path).name
    if not key.startswith(f"fable-r2d2/revision-{REVISION.lower()}/"):
        raise RuntimeError(f"refusing S3 key outside the revision {REVISION} prefix: {key}")
    return key


def send_blockers(root=ROOT):
    """Everything that stops a real revision D send; an empty list means the package may be sent."""
    root = Path(root)
    video, pdf = root / VIDEO.relative_to(ROOT), root / PDF.relative_to(ROOT)
    blockers = []
    verification = read_json(root / "docs/verification.json")
    if verification.get("all_pass") is not True or verification.get("revision") != REVISION:
        failed = [c["check"] for c in verification.get("checks", []) if not c.get("pass")]
        blockers.append(f"docs/verification.json: all_pass={verification.get('all_pass')}, "
                        f"revision={verification.get('revision')} (need {REVISION}); failed checks {failed}")
    manual = read_json(root / "docs/pdf-check.json")
    if manual.get("revision") != REVISION or manual.get("all_pass") is not True:
        blockers.append(f"docs/pdf-check.json: revision={manual.get('revision')}, all_pass={manual.get('all_pass')}")
    if not pdf.is_file():
        blockers.append(f"missing {pdf.relative_to(root)}")
    elif manual.get("sha256") != sha256(pdf):
        blockers.append("manual PDF does not match docs/pdf-check.json sha256")
    movie = read_json(root / "output/video/video-manifest.json")
    if movie.get("revision") != REVISION:
        blockers.append(f"output/video/video-manifest.json: revision={movie.get('revision')}")
    if not video.is_file():
        blockers.append(f"missing {video.relative_to(root)}")
    elif movie.get("video_sha256") != sha256(video):
        blockers.append("video MP4 does not match video-manifest.json video_sha256")
    return blockers


def receipt_revision(receipt, root=ROOT):
    """Revision a delivery receipt belongs to: its own field, or the frozen baseline that recorded it."""
    if receipt.get("revision"):
        return receipt["revision"]
    base = read_json(Path(root) / "docs/revision-c.json")
    if receipt.get("MessageId") and receipt["MessageId"] in base.get("summary", ""):
        return base.get("revision")
    return None


def default_texts(root=ROOT):
    """Subject, outcome and evidence built from the package manifests."""
    root = Path(root)
    counts = package_counts(root)
    verification = read_json(root / "docs/verification.json")
    manual = read_json(root / "docs/pdf-check.json")
    movie = read_json(root / "output/video/video-manifest.json")
    checks = verification.get("checks", [])
    passed = sum(1 for c in checks if c.get("pass"))
    pages, seconds = manual.get("pages"), movie.get("seconds")
    subject = (f"fable-r2d2 revision {REVISION} delivered - motorized interlocked stance change: "
               f"{counts['designs']} STL files, {pages}-page manual attached, {seconds} s video link, "
               f"{passed}/{len(checks)} package checks pass")
    outcome = (f"fable-r2d2 revision {REVISION} is packaged: {counts['designs']} STL files ({counts['pieces']} printed "
               f"pieces), a two-foot and a three-leg stance changed by an interlocked actuator with sensed shoulder "
               f"locks. The {pages}-page manual is attached and the {seconds} s video link is valid {LINK_DAYS} days. "
               f"docs/verification.json: {passed} of {len(checks)} checks pass, revision {verification.get('revision')}. "
               "Nothing has been printed, built or driven.")
    lines = [f"$ python scripts/verify.py"]
    lines += [f"{'PASS' if c.get('pass') else 'FAIL'} {c.get('check')}: {c.get('detail')}" for c in checks]
    if verification:
        lines.append(f"ALL PASS: revision {verification.get('revision')}" if verification.get("revision")
                     else "FAILURES PRESENT")
    return {"subject": subject, "outcome": outcome, "evidence": "\n".join(lines)}


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


def build_message(subject, outcome, evidence, next_text, in_flight, video_url, pdf_url):
    """The complete raw MIME message: HTML + text alternative, manual PDF attached."""
    sha = git("rev-parse", "HEAD")
    subject_line = git("log", "-1", "--format=%s")
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    esc = html_lib.escape
    links = (f'<p style="margin:0 0 12px;color:#0b0f19;background-color:#ffffff">Video (S3, private, link valid {LINK_DAYS} days): '
             f'<a href="{esc(video_url)}" style="color:#1d4ed8;background-color:#ffffff">{VIDEO.name}</a> '
             f'({VIDEO.stat().st_size / 1e6:.1f} MB, SHA-256 {sha256(VIDEO)[:16]}...)</p>'
             f'<p style="margin:0 0 12px;color:#0b0f19;background-color:#ffffff">Assembly manual PDF: attached, and also on S3: '
             f'<a href="{esc(pdf_url)}" style="color:#1d4ed8;background-color:#ffffff">{PDF.name}</a> '
             f'({PDF.stat().st_size / 1e6:.1f} MB, SHA-256 {sha256(PDF)[:16]}...)</p>')
    html = build_html({
        "OUTCOME_ONE_LINE": esc(outcome), "SHA": sha[:12], "COMMIT_SUBJECT": esc(subject_line),
        "ACTUAL_COMMAND_OUTPUT": esc(evidence), "ITEM": esc(in_flight), "NEXT": esc(next_text) + links,
        "REPO": "JeremyProffittOrg/robots (fable-r2d2)", "BRANCH": "main", "HEAD_SHA": sha[:12], "TIMESTAMP": timestamp,
    })
    message = MIMEMultipart("mixed")
    message["Subject"] = subject
    message["From"] = f"fable-r2d2 build <{SENDER}>"
    message["To"] = RECIPIENT
    message["Reply-To"] = REPLY_TO
    alternative = MIMEMultipart("alternative")
    text = (f"{outcome}\n\nVideo (S3, {LINK_DAYS}-day link): {video_url}\nPDF: attached and {pdf_url}\n\n"
            f"Evidence:\n{evidence}\n\nNext: {next_text}\n{sha[:12]} {subject_line}\n")
    alternative.attach(MIMEText(text, "plain", "utf-8"))
    alternative.attach(MIMEText(html, "html", "utf-8"))
    message.attach(alternative)
    attachment = MIMEApplication(PDF.read_bytes(), _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename=PDF.name)
    message.attach(attachment)
    return message.as_bytes(), html, sha, timestamp


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
    return s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=LINK_DAYS * 86400)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="build and measure the MIME message; upload and send nothing")
    parser.add_argument("--force", action="store_true", help="send again although a revision D receipt exists")
    parser.add_argument("--subject", help="override the manifest-derived subject")
    parser.add_argument("--outcome", help="override the manifest-derived one-line outcome")
    parser.add_argument("--evidence", help="path to a text file with verbatim command output (default: verification.json)")
    parser.add_argument("--next", default=("Physical build: print the fit coupons first, then the feet. Commission the "
                                           "stance change on the bench (docs/firmware.md section 11.4) before the first "
                                           "powered change."))
    parser.add_argument("--in-flight", default=f"Nothing; the revision {REVISION} package is complete.")
    parser.add_argument("--preview", type=Path, help="also write the HTML body to this path")
    args = parser.parse_args()

    missing = [str(p) for p in (VIDEO, PDF, TEMPLATE) if not p.is_file()]
    if missing:
        raise SystemExit("Cannot build the message; missing: " + ", ".join(missing))
    blockers = send_blockers()
    if not args.dry_run and blockers:
        raise SystemExit("REFUSED: the package is not a verified revision " + REVISION + ":\n  " + "\n  ".join(blockers))
    prior = read_json(RECEIPT)
    prior_revision = receipt_revision(prior)
    if prior.get("MessageId") and prior_revision == REVISION and not args.force and not args.dry_run:
        raise SystemExit(f"Already sent: revision {REVISION} MessageId {prior['MessageId']}; use --force to send again")

    texts = default_texts()
    subject = args.subject or texts["subject"]
    outcome = args.outcome or texts["outcome"]
    evidence = Path(args.evidence).read_text(encoding="utf-8") if args.evidence else texts["evidence"]
    video_key, pdf_key = s3_key(VIDEO), s3_key(PDF)

    if args.dry_run:
        video_url = f"(dry run: s3://{BUCKET}/{video_key} not uploaded)"
        pdf_url = f"(dry run: s3://{BUCKET}/{pdf_key} not uploaded)"
        bucket_state = "not contacted"
    else:
        import boto3
        s3 = boto3.client("s3", region_name=REGION)
        bucket_state = ensure_bucket(s3)
        video_url = upload_and_presign(s3, VIDEO, video_key)
        pdf_url = upload_and_presign(s3, PDF, pdf_key)

    raw, html, sha, timestamp = build_message(subject, outcome, evidence, args.next, args.in_flight, video_url, pdf_url)
    print(f"Subject: {subject}")
    print(f"S3 keys: s3://{BUCKET}/{video_key} and s3://{BUCKET}/{pdf_key} (bucket {bucket_state})")
    print(f"MIME size {len(raw)} bytes ({len(raw) / 1e6:.2f} MB of the {SESV2_LIMIT_BYTES / 1e6:.0f} MB SESv2 limit); "
          f"PDF sha256 {sha256(PDF)}; video sha256 {sha256(VIDEO)}")
    if args.preview:
        args.preview.write_text(html, encoding="utf-8")
        print(f"Preview HTML written to {args.preview}")
    # SESv2 accepts 40 MB; the older v1 send_raw_email caps at 10 MB, which a manual with figures exceeds.
    if len(raw) > SESV2_LIMIT_BYTES:
        raise SystemExit(f"Message is {len(raw)} bytes; SESv2 accepts at most {SESV2_LIMIT_BYTES}")
    if args.dry_run:
        if blockers:
            print("SEND BLOCKERS (a real send refuses until these clear):")
            for blocker in blockers:
                print(f"  {blocker}")
        else:
            print(f"SENDABLE: the package verifies as revision {REVISION}")
        print("DRY RUN: nothing uploaded, nothing sent")
        return

    import boto3
    ses = boto3.client("sesv2", region_name=REGION)
    response = ses.send_email(FromEmailAddress=SENDER, Destination={"ToAddresses": [RECIPIENT]},
                              Content={"Raw": {"Data": raw}})
    if prior.get("MessageId") and prior_revision != REVISION:
        archive = RECEIPT.with_name(f"delivery-receipt-revision-{(prior_revision or 'unknown').lower()}.json")
        if not archive.exists():
            archive.write_text(json.dumps(prior, indent=2) + "\n", encoding="utf-8")
    receipt = {"revision": REVISION, "MessageId": response["MessageId"], "sent_at_utc": timestamp, "to": RECIPIENT,
               "subject": subject, "mime_bytes": len(raw), "video_sha256": sha256(VIDEO), "pdf_sha256": sha256(PDF),
               "video_s3_key": video_key, "pdf_s3_key": pdf_key, "bucket": BUCKET, "link_valid_days": LINK_DAYS,
               "head_sha": sha}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"SENT MessageId {response['MessageId']}")


if __name__ == "__main__":
    main()
