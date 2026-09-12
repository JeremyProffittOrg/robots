# R2D2 artifact publication research

Verified 2026-09-12. Scope: read-only repository inspection and primary AWS documentation. No AWS commands, identity-state inspection, deployment, or email were performed.

## Verified repository facts

- Repository: `JeremyProffittOrg/robots`; default branch `main`; public repository. Verified with `gh api repos/JeremyProffittOrg/robots --jq '{full_name,default_branch,private}'`.
- Actions enabled; all actions allowed. Verified with `gh api repos/JeremyProffittOrg/robots/actions/permissions --jq '{enabled,allowed_actions}'`, returning `{"allowed_actions":"all","enabled":true}`.
- `gh api repos/JeremyProffittOrg/robots/actions/workflows --jq '.workflows | map({name,path,state})'` returned `[]`; `gh run list --repo JeremyProffittOrg/robots --limit 5 --json databaseId,name,conclusion,headSha` also returned `[]`.
- `C:/dev/robots/deploy.md` requires deployment through a push/merge to `main`, GitHub Actions OIDC, `aws-actions/configure-aws-credentials@v4`, region `us-east-1`, `contents: read`, and `id-token: write`. No local deployment or static keys.
- A local draft exists at `C:/dev/robots/.github/workflows/publish-dalek.yml`, with a private-bucket template at `C:/dev/robots/dalek/infra/deliverables.yaml`. Both are untracked according to `git status`; `git ls-files .github/workflows dalek/infra` returned no paths. They are unrelated operator work, not an existing deployed pipeline. Preserve them.
- The Dalek draft verifies a video manifest, uses OIDC, deploys CloudFormation, uploads exact MP4/PDF objects, downloads them, and compares SHA-256. Its bucket is `BucketOwnerEnforced`, AES256 encrypted, with all four public-access-block settings enabled. Do not make this bucket public or reuse its artifact prefix.
- Existing tracked R2D2 PDF: `r2d2/output/pdf/r2d2-design-and-assembly.pdf`. No R2D2 MP4 was found in the inspected output listing. The final animation must be generated and verified before publication.

`gh variable list --repo JeremyProffittOrg/robots` verified these non-secret settings:

- `AWS_DEPLOY_ROLE_ARN=arn:aws:iam::759775734231:role/gha-deploy`
- `DEPLOY_AWS_ACCOUNT=759775734231`
- `CLOUDFORMATION_S3_BUCKET=cloudformation-jeremy-ninja`
- `DOMAIN_NAME=robots.jeremy.ninja`
- `HOSTED_ZONE_ID=Z07996671GFOF4EO145M3`
- `ADMIN_USER=Jeremy`
- `CERTIFICATE_ARN=arn:aws:acm:us-east-1:759775734231:certificate/111763ad-8ade-47dd-a0d5-c707b954289e`
- `CERTIFICATE_ARN_US_EAST_2=arn:aws:acm:us-east-2:759775734231:certificate/867996e9-9d20-4693-9ce8-3b060842d271`

Only the role ARN and account are needed for the minimal path. Do not use the CloudFormation staging bucket for public deliverables. DNS and certificates are unnecessary for direct S3 HTTPS URLs. IAM permissions, effective account/organization public-access restrictions, and bucket-name availability were not inspected.

## Minimum proposed implementation

Add only `.github/workflows/publish-r2d2.yml` and `r2d2/infra/deliverables.yaml`, plus the final artifact and manifest files owned by this task. Follow the local Dalek draft's verification pattern without editing or staging that draft. Trigger on relevant R2D2 files and the new workflow/template under `main`; optionally allow manual workflow dispatch restricted to `refs/heads/main`. Use a separate concurrency group with cancellation disabled and a bounded timeout.

Proposed dedicated stack: `robots-r2d2-deliverables`. Proposed bucket: `robots-r2d2-deliverables-759775734231`. Its availability is not verified. Use CloudFormation `DeletionPolicy: Retain` and `UpdateReplacePolicy: Retain`. Set stack tags exactly as required by `deploy.md`: `Project=robots CostCenter=home-iot Environment=prod ManagedBy=sam DeployedVia=github-actions Owner=jeremy`. No alarms, dashboards, Lambda, logs, website endpoint, or scheduled automation is required. [CloudFormation S3 bucket reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-s3-bucket.html).

After OIDC login, inspect effective account public-access-block configuration from Actions with `aws s3control get-public-access-block --account-id "$DEPLOY_AWS_ACCOUNT"`. Handle only a specifically identified missing-configuration result as absent settings. Permission denial or a failed request is not evidence that public access is allowed. Do not change account/organization settings. AWS applies the most restrictive account, organization, and bucket restrictions. Public bucket policies require effective `BlockPublicPolicy` and `RestrictPublicBuckets` to permit the policy. [AWS Block Public Access documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).

If public object access is permitted, the dedicated bucket configuration should retain `BlockPublicAcls: true`, `IgnorePublicAcls: true`, and `BucketOwnerEnforced`, with bucket-level `BlockPublicPolicy: false` and `RestrictPublicBuckets: false`. Never send a public ACL. Bucket-owner-enforced ownership disables ACLs and uses policies for access. [AWS Object Ownership](https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html).

Use SSE-S3 (`SSEAlgorithm: AES256`) explicitly. It encrypts stored objects without requiring a customer KMS key for anonymous downloads. [AWS SSE-S3 documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingServerSideEncryption.html).

The only public allow statement should grant `Principal: '*'` the single action `s3:GetObject`, restricted to exactly these two proposed object ARNs:

```text
arn:aws:s3:::robots-r2d2-deliverables-759775734231/r2d2/r2d2-assembly-and-operation.mp4
arn:aws:s3:::robots-r2d2-deliverables-759775734231/r2d2/r2d2-design-and-assembly.pdf
```

No wildcard object allow, `ListBucket`, write grant, or public manifest is necessary. Add a deny for non-TLS access using `aws:SecureTransport: false` on the bucket and its objects. The wildcard in this deny is deliberate; it does not grant access. Manage the policy through `AWS::S3::BucketPolicy`. [CloudFormation policy reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-s3-bucketpolicy.html), [AWS policy condition examples](https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html).

Proposed stable URLs, not yet live or verified:

```text
https://robots-r2d2-deliverables-759775734231.s3.us-east-1.amazonaws.com/r2d2/r2d2-assembly-and-operation.mp4
https://robots-r2d2-deliverables-759775734231.s3.us-east-1.amazonaws.com/r2d2/r2d2-design-and-assembly.pdf
```

This uses the S3 REST HTTPS endpoint. The fixed keys remain stable when the final content is updated; report the committed revision and downloaded hashes with the delivery so the operator knows which files were checked. [S3 virtual-hosted URL syntax](https://docs.aws.amazon.com/AmazonS3/latest/userguide/VirtualHosting.html).

## Upload and acceptance checks

The Actions job must first verify the manifest's source hashes and the exact committed PDF/video bytes. Upload only the two named files, with `video/mp4` or `application/pdf`, `Content-Disposition: inline`, `Cache-Control: no-cache`, SHA-256 metadata, and an upload checksum. Do not run a directory sync or use `--delete`.

Download both objects through their anonymous HTTPS URLs and compare SHA-256 to the checked-out files. Check HTTP success, content types, and video byte-range handling (`Range: bytes=0-1023` should return 206 and 1024 bytes). S3 supports ranged GetObject requests. [GetObject API](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html).

Anonymous `GET /?list-type=2` must return 403. Inspect the deployed bucket policy to ensure only the two exact public object resources exist, and verify ownership controls and encryption with authenticated reads. Do not perform anonymous destructive/write probes. Print the final two URLs and hashes to the Actions summary only after both byte checks pass.

Watch the workflow to a terminal state with `gh run watch RUN_ID --repo JeremyProffittOrg/robots --exit-status`. Diagnose deterministic failures before a bounded retry. Completion means a successful run plus anonymous byte/hash checks, not merely an S3 upload exit code. The final email must include the verified MP4 link and PDF link/attachment from the same revision. This research does not determine the recipient or send the email.

## If direct public S3 access is blocked

Keep the bucket private. A CloudFront distribution with Origin Access Control can expose stable HTTPS download URLs while permitting only the distribution to read the two S3 keys. This adds resources but preserves account restrictions; implement through the same repository pipeline if selected. Do not substitute a website origin, public ACL, account-wide public-access change, or expiring link without reporting the changed delivery behavior. [AWS CloudFront OAC guidance](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html).

Presigned S3 URLs expire; when generated using temporary role credentials they cannot outlive those credentials. They therefore do not meet the stable-link requirement. [AWS presigned URL expiration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).
