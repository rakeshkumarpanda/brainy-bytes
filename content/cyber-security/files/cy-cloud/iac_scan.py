# 2.2 Cloud security: shared responsibility, identity, settings and keys
# Example "iac_scan" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Scanning infrastructure as code before it is deployed (the idea behind Checkov, tfsec and KICS)
TERRAFORM = """
resource "aws_s3_bucket_public_access_block" "exports" {
  block_public_acls   = false
  block_public_policy = false
}
resource "aws_security_group_rule" "ssh" {
  type        = "ingress"
  from_port   = 22
  cidr_blocks = ["0.0.0.0/0"]
}
resource "aws_db_instance" "main" {
  storage_encrypted = false
  publicly_accessible = true
}
resource "aws_instance" "web" {
  metadata_options { http_tokens = "optional" }
}
"""

RULES = [
    ("block_public_acls   = false", "S3 public access block is off"),
    ('cidr_blocks = ["0.0.0.0/0"]', "a rule allows the whole internet"),
    ("storage_encrypted = false", "database storage not encrypted"),
    ("publicly_accessible = true", "database reachable from the internet"),
    ('http_tokens = "optional"', "IMDSv2 not required on the instance"),
]

for number, line in enumerate(TERRAFORM.strip().splitlines(), start=1):
    for pattern, message in RULES:
        if pattern in line:
            print(f"line {number:2}: {message}")
print("\nFix these in the pull request, before anything reaches the cloud. That is shifting cloud security left.")
