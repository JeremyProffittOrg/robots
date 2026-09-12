# Video and PDF delivery

The `Publish Dalek design artifacts` GitHub Actions workflow publishes the committed ROUND-9 MP4 and PDF to the private `robots-dalek-deliverables-759775734231` S3 bucket in `us-east-1`. The object prefix is `dalek/<full Git commit SHA>/`. Each uploaded file has its media type, inline filename and SHA256 metadata. The workflow downloads both objects and compares their complete SHA256 hashes before reporting success.

Publication uses the repository's `AWS_DEPLOY_ROLE_ARN` through GitHub OIDC. The CloudFormation template creates one encrypted bucket with public access blocked. There are no public bucket grants, servers, scheduled jobs or stored workflow keys. Run the workflow on `main` or push updated final artifacts to `main`.

The final operator email contains the PDF attachment and a signed S3 GET link to the MP4. The local configured SES identity sends the email only after final checks and successful publication. Signed URLs stay out of Git and workflow logs. The email states the exact link expiry. The file remains in S3 after link expiry; a new signed link can be issued without republishing it.

AWS permits an IAM-user signed URL for up to seven days. A URL signed by temporary role credentials expires when that role session expires, even if a longer interval was requested. This is why the short-lived deployment role does not create the emailed link. The local signing and send commands use the existing configured identity without exposing credential values. [AWS S3 signed URL documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).
